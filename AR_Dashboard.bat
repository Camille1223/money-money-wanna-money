@echo off
REM === AR Dashboard Launcher ===
REM Starts a local Python web server in the dashboard folder and opens the browser.
REM Closing the black console window will stop the server.

cd /d "%~dp0"

REM Pick an unlikely-to-be-used port
set PORT=8765

REM Open the dashboard in the default browser after a short delay
start "" cmd /c "ping 127.0.0.1 -n 2 >nul && start http://localhost:%PORT%/index.html"

REM Run the auto-sync backend if auth is available; otherwise just serve files.
if exist sync_sharepoint.py (
  echo [AR Dashboard] Starting SharePoint auto-sync backend...
  start "AR Sync" /min cmd /c "set PYTHONIOENCODING=utf-8 && python sync_sharepoint.py"
)

echo [AR Dashboard] Serving on http://localhost:%PORT%/
echo Close this window to stop the server.
python -m http.server %PORT%
