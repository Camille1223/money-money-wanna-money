@echo off
REM ============================================================
REM AR Dashboard launcher — auto-update edition
REM   - git pull on every launch so any push to main is live next click
REM   - Reaps any leftover instances on ports 8765/8766 first
REM   - Logs both static server + sync to .log files
REM   - Triggers an immediate sync on startup (no 10-min wait)
REM ============================================================

cd /d "%~dp0"

set STATIC_PORT=8765
set SYNC_PORT=8766

REM ----- Pull latest code from GitHub --------------------------
REM Silent if no git / no network — dashboard still launches with whatever
REM code is on disk. Local edits to tracked files would block pull, so we
REM stash anything dirty first (rare for end users, just a safety net).
where git >nul 2>&1
if %ERRORLEVEL%==0 if exist .git (
  echo [AR Dashboard] Checking for updates from GitHub...
  git stash push -u -m "auto-launcher" >nul 2>&1
  git pull --ff-only origin main 2>&1 | findstr /V /C:"Already up to date" /C:"Already up-to-date"
  git stash pop >nul 2>&1
)

echo [AR Dashboard] Reaping any leftover instances on %STATIC_PORT% / %SYNC_PORT% ...

REM Kill anything listening on either port (idempotent — silent if nothing to kill)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%STATIC_PORT% " ^| findstr LISTENING') do (
  taskkill /F /PID %%P >nul 2>&1
)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%SYNC_PORT% " ^| findstr LISTENING') do (
  taskkill /F /PID %%P >nul 2>&1
)

REM Brief pause so the kernel actually releases the sockets
ping 127.0.0.1 -n 2 >nul

REM ----- Sync backend (port 8766) ------------------------------
if exist sync_sharepoint.py (
  echo [AR Dashboard] Starting SharePoint sync backend ^(port %SYNC_PORT%^)...
  start "AR Sync" cmd /c "set PYTHONIOENCODING=utf-8 && python -u sync_sharepoint.py > sync.log 2>&1"
)

REM ----- Open browser after a short delay -----------------------
start "" cmd /c "ping 127.0.0.1 -n 3 >nul && start http://localhost:%STATIC_PORT%/index.html"

REM ----- Trigger an immediate sync once the backend is up -------
start "" cmd /c "ping 127.0.0.1 -n 5 >nul && curl -s -X POST http://127.0.0.1:%SYNC_PORT%/api/sync >nul 2>&1"

echo.
echo [AR Dashboard] Static server: http://localhost:%STATIC_PORT%/
echo [AR Dashboard] Close this window to stop the dashboard.
echo.

python -u -m http.server %STATIC_PORT% > server.log 2>&1
