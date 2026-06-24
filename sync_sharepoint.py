"""
AR Dashboard - SharePoint auto-sync backend (multi-user).

Reads a SharePoint share link from config.json (written by the dashboard's
settings panel), resolves it via Microsoft Graph, and downloads the file as
current.xlsx. Also exposes a small HTTP API so the dashboard can:

  POST /api/config { "sharepoint_url": "https://..." }   - save link
  POST /api/sync                                         - sync now
  GET  /api/status                                       - last sync state
  GET  /api/config                                       - current link

Auth comes from ~/.sap-mcp/auth.json (managed by sap-auth MCP).

Run with: python sync_sharepoint.py
Stops with Ctrl+C.
"""
import base64
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AUTH_PATH = Path(os.path.expanduser('~')) / '.sap-mcp' / 'auth.json'
HERE = Path(__file__).resolve().parent
OUT_PATH = HERE / 'current.xlsx'
META_PATH = HERE / 'current.meta.json'
CONFIG_PATH = HERE / 'config.json'

API_PORT = 8766
POLL_SECONDS = 60  # every minute — near-real-time

LOG = lambda msg: print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}', flush=True)

# Shared state for the API
STATE_LOCK = threading.Lock()
STATE = {
    'lastSyncAt': None,
    'lastSyncOk': None,
    'lastError': None,
    'lastFile': None,
    'lastModified': None,
    'syncing': False,
}


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        LOG(f'config.json unreadable: {e}')
        return {}


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding='utf-8')


def _refresh_graph_token(prov_name, prov):
    """Use the provider's stored MSAL refresh token to mint a fresh Graph access
    token. Writes the new access token AND rotated refresh token back into
    auth.json so the next call also succeeds. Returns the new access token or
    None on failure.

    This is what keeps the dashboard alive without nagging the user to "run a
    Teams/Outlook MCP tool" every few hours — the refresh token lives ~90 days
    and gets rotated on every use.
    """
    rt_obj = prov.get('refreshToken')
    if not isinstance(rt_obj, dict):
        return None
    rt = rt_obj.get('secret')
    client_id = rt_obj.get('clientId')
    if not rt or not client_id:
        return None
    body = urllib.parse.urlencode({
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': rt,
        'scope': 'https://graph.microsoft.com/.default offline_access',
    }).encode()
    req = urllib.request.Request(
        'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        data=body,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': f'https://{prov_name}',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        LOG(f'refresh_token exchange for {prov_name} failed: {e}')
        return None
    new_access = result.get('access_token')
    if not new_access:
        return None
    expires_in = int(result.get('expires_in', 3600))
    new_exp = int(time.time()) + expires_in
    # Persist new tokens back into auth.json (atomically — write to tmp then replace)
    try:
        with open(AUTH_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        target = data.get('providers', {}).get(prov_name, {})
        # Update the Graph token in the tokens array
        updated = False
        for t in target.get('tokens', []):
            if t.get('audience') == 'https://graph.microsoft.com':
                t['token'] = new_access
                t['expiresAt'] = new_exp
                updated = True
                break
        if not updated:
            target.setdefault('tokens', []).append({
                'token': new_access,
                'audience': 'https://graph.microsoft.com',
                'expiresAt': new_exp,
                'scopes': ['https://graph.microsoft.com/.default'],
            })
        # Rotate refresh token (Azure issues a new one on every refresh)
        if 'refresh_token' in result:
            rt_obj['secret'] = result['refresh_token']
            target['refreshToken'] = rt_obj
        tmp = AUTH_PATH.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(data, indent=2), encoding='utf-8')
        tmp.replace(AUTH_PATH)
        LOG(f'Refreshed Graph token via {prov_name} ({expires_in}s, persisted)')
    except Exception as e:
        # Even if persistence fails, we can still return the access token for
        # this call — the next sync will just refresh again.
        LOG(f'refresh ok but persisting to auth.json failed: {e}')
    return new_access


def get_graph_token():
    """Read the most recent valid Graph token from auth.json. If all are
    expired, attempt to refresh using a stored MSAL refresh token before
    giving up."""
    if not AUTH_PATH.exists():
        LOG(f'auth.json not found at {AUTH_PATH} - run any Teams/Outlook MCP tool to sign in.')
        return None
    with open(AUTH_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    providers = data.get('providers', {})
    for prov_name in ('teams.cloud.microsoft', 'teams.microsoft.com'):
        prov = providers.get(prov_name)
        if not prov:
            continue
        for t in prov.get('tokens', []):
            if t.get('audience') == 'https://graph.microsoft.com':
                exp = t.get('expiresAt', 0)
                remaining = exp - int(time.time())
                if remaining < 60:
                    LOG(f'Graph token in {prov_name} expired {-remaining}s ago, trying next...')
                    continue
                LOG(f'Using Graph token from {prov_name} ({remaining}s remaining)')
                return t['token']
    # All cached tokens stale — try refresh_token grant on each provider
    for prov_name in ('teams.microsoft.com', 'teams.cloud.microsoft'):
        prov = providers.get(prov_name)
        if not prov:
            continue
        tok = _refresh_graph_token(prov_name, prov)
        if tok:
            return tok
    LOG('No valid Graph token and refresh failed - run any Teams/Outlook MCP tool to re-sign in.')
    return None


def graph_get(url, token):
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def encode_share_id(share_url):
    """Graph's encoding for /shares/{share-id}: u! + base64url(url) without padding."""
    b = base64.urlsafe_b64encode(share_url.encode('utf-8')).decode('ascii').rstrip('=')
    return 'u!' + b


def resolve_share(token, share_url):
    """Resolve any SharePoint sharing link or direct doc link to a driveItem."""
    sid = encode_share_id(share_url)
    url = f'https://graph.microsoft.com/v1.0/shares/{sid}/driveItem'
    status, body, _ = graph_get(url, token)
    if status != 200:
        return None, f'shares lookup failed ({status}): {body[:300]!r}'
    try:
        return json.loads(body), None
    except Exception as e:
        return None, f'shares lookup parse error: {e}'


def fetch_driveitem_fresh(token, item):
    """Re-fetch the driveItem to get a fresh @microsoft.graph.downloadUrl."""
    parent = item.get('parentReference') or {}
    drive_id = parent.get('driveId')
    item_id = item.get('id')
    if not drive_id or not item_id:
        return item, None
    url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}'
    status, body, _ = graph_get(url, token)
    if status != 200:
        return item, f'driveItem refresh failed ({status})'
    try:
        return json.loads(body), None
    except Exception as e:
        return item, f'driveItem refresh parse error: {e}'


def download_file(item):
    dl = item.get('@microsoft.graph.downloadUrl')
    if not dl:
        return False, 'no downloadUrl on item'
    name = item.get('name', 'file.xlsx')
    LOG(f'Downloading {name} ({item.get("size", 0)} bytes)...')
    try:
        with urllib.request.urlopen(dl, timeout=180) as resp:
            data = resp.read()
    except Exception as e:
        return False, f'download error: {e}'
    tmp = OUT_PATH.with_suffix('.xlsx.tmp')
    tmp.write_bytes(data)
    tmp.replace(OUT_PATH)
    META_PATH.write_text(json.dumps({
        'name': name,
        'lastModifiedDateTime': item.get('lastModifiedDateTime'),
        'syncedAt': datetime.now().isoformat(timespec='seconds'),
        'size': len(data),
        'webUrl': item.get('webUrl'),
    }, indent=2), encoding='utf-8')
    LOG(f'Saved -> {OUT_PATH}')
    return True, None


def sync_once():
    with STATE_LOCK:
        STATE['syncing'] = True
        STATE['lastError'] = None
    try:
        cfg = load_config()
        url = (cfg.get('sharepoint_url') or '').strip()
        if not url:
            msg = 'No SharePoint link configured. Open the dashboard, click ⚙, paste your file link.'
            LOG(msg)
            with STATE_LOCK:
                STATE['lastError'] = msg
                STATE['lastSyncOk'] = False
            return False
        token = get_graph_token()
        if not token:
            with STATE_LOCK:
                STATE['lastError'] = 'no Graph token'
                STATE['lastSyncOk'] = False
            return False
        item, err = resolve_share(token, url)
        if err:
            LOG(err)
            with STATE_LOCK:
                STATE['lastError'] = err
                STATE['lastSyncOk'] = False
            return False
        # The /shares lookup sometimes omits @microsoft.graph.downloadUrl.
        if not item.get('@microsoft.graph.downloadUrl'):
            item, refresh_err = fetch_driveitem_fresh(token, item)
            if refresh_err:
                LOG(refresh_err)
        # Skip if already up to date
        last_mod = item.get('lastModifiedDateTime')
        if META_PATH.exists() and OUT_PATH.exists():
            try:
                existing = json.loads(META_PATH.read_text(encoding='utf-8'))
                if existing.get('lastModifiedDateTime') == last_mod:
                    LOG(f'Up to date: {item.get("name")} ({last_mod})')
                    with STATE_LOCK:
                        STATE['lastSyncAt'] = datetime.now().isoformat(timespec='seconds')
                        STATE['lastSyncOk'] = True
                        STATE['lastFile'] = item.get('name')
                        STATE['lastModified'] = last_mod
                    return True
            except Exception:
                pass
        ok, err = download_file(item)
        with STATE_LOCK:
            STATE['lastSyncAt'] = datetime.now().isoformat(timespec='seconds')
            STATE['lastSyncOk'] = ok
            STATE['lastError'] = err
            STATE['lastFile'] = item.get('name')
            STATE['lastModified'] = last_mod
        return ok
    except Exception as e:
        LOG(f'sync_once error: {e}')
        with STATE_LOCK:
            STATE['lastError'] = str(e)
            STATE['lastSyncOk'] = False
        return False
    finally:
        with STATE_LOCK:
            STATE['syncing'] = False


# ============== HTTP API ==============

class APIHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/status':
            with STATE_LOCK:
                payload = dict(STATE)
            payload['hasConfig'] = bool((load_config().get('sharepoint_url') or '').strip())
            return self._json(200, payload)
        if self.path == '/api/config':
            cfg = load_config()
            return self._json(200, {'sharepoint_url': cfg.get('sharepoint_url', '')})
        return self._json(404, {'error': 'not found'})

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length) if length else b''
        try:
            data = json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            return self._json(400, {'error': 'invalid json'})

        if self.path == '/api/config':
            url = (data.get('sharepoint_url') or '').strip()
            if not url:
                return self._json(400, {'error': 'sharepoint_url required'})
            cfg = load_config()
            cfg['sharepoint_url'] = url
            save_config(cfg)
            LOG(f'Config updated, link saved.')
            # Kick off a sync in the background
            threading.Thread(target=sync_once, daemon=True).start()
            return self._json(200, {'ok': True, 'sharepoint_url': url})

        if self.path == '/api/sync':
            with STATE_LOCK:
                if STATE['syncing']:
                    return self._json(202, {'ok': True, 'queued': False, 'note': 'already syncing'})
            threading.Thread(target=sync_once, daemon=True).start()
            return self._json(202, {'ok': True, 'queued': True})

        return self._json(404, {'error': 'not found'})

    def log_message(self, format, *args):
        # Quieter access log
        return


def serve_api():
    server = ThreadingHTTPServer(('127.0.0.1', API_PORT), APIHandler)
    LOG(f'API listening on http://127.0.0.1:{API_PORT}')
    server.serve_forever()


def main():
    LOG(f'AR Dashboard sync starting. Polling every {POLL_SECONDS}s (~real-time).')
    LOG(f'Output: {OUT_PATH}')
    LOG(f'Config: {CONFIG_PATH}')

    api_thread = threading.Thread(target=serve_api, daemon=True)
    api_thread.start()

    while True:
        try:
            sync_once()
        except Exception as e:
            LOG(f'Sync loop error: {e}')
        try:
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            LOG('Stopped.')
            return


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        ok = sync_once()
        sys.exit(0 if ok else 1)
    main()
