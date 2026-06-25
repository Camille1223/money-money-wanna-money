#!/usr/bin/env node
/**
 * ensure_token.mjs — make sure auth.json has a valid Graph access token before
 * sync_sharepoint.py starts polling. Reuses SAP MCP's auth machinery (silent
 * refresh -> browser auth fallback) so the dashboard never gets stuck with
 * stale tokens after a double-click.
 *
 * Called from AR_Dashboard.bat before launching the Python sync.
 * Exits 0 on success, non-zero on failure (in which case the dashboard will
 * still try to launch and show its stale-banner — better than crashing).
 *
 * Relies on the SAP MCP monorepo at C:\Users\I588206\sap-mcp-combo being
 * present and built. That is where the auth flows (silent refresh + browser
 * fallback for Teams OAuth) actually live; we just borrow them.
 */
import { pathToFileURL } from 'node:url';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const SAP_AUTH_DIST = resolve(
  'C:/Users/I588206/sap-mcp-combo/packages/shared/sap-auth/dist/index.js',
);
if (!existsSync(SAP_AUTH_DIST)) {
  console.error('[ensure_token] sap-auth dist not found at', SAP_AUTH_DIST);
  console.error('[ensure_token] cannot ensure token automatically — sync will run with whatever is cached');
  process.exit(3);
}

const { createAuthClient } = await import(pathToFileURL(SAP_AUTH_DIST).href);

const GRAPH = 'https://graph.microsoft.com';

const client = createAuthClient({
  domain: 'teams.microsoft.com',
  method: 'oauth',
  entryUrl: 'https://teams.microsoft.com/',
  tokenAudience: 'https://ic3.teams.office.com',
  additionalAudiences: [
    'https://api.spaces.skype.com',
    'https://chatsvcagg.teams.microsoft.com',
    GRAPH,
  ],
});

try {
  const headers = await client.getHeaders({ audience: GRAPH });
  if (!headers || !headers.Authorization) {
    console.error('[ensure_token] no Authorization header returned');
    process.exit(2);
  }
  console.log('[ensure_token] Graph token ready');
  process.exit(0);
} catch (e) {
  console.error('[ensure_token] FAIL:', e && e.message ? e.message : e);
  process.exit(1);
}
