@echo off
setlocal
cd /d "%~dp0"
rem Replace a previous PIE Local API instance on its fixed loopback port.
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8787"') do taskkill /f /pid %%P >nul 2>nul
set "PIE_PY="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PIE_PY set "PIE_PY=%%P"
if not defined PIE_PY if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PIE_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not defined PIE_PY (
  echo Python is required to start PIE ITR Local API. Install Python, then run this file again.
  pause
  exit /b 1
)
start "PIE ITR Local API" /b "%PIE_PY%" -B local_api.py
cd frontend
set "PIE_NODE="
for /f "delims=" %%N in ('where node 2^>nul') do if not defined PIE_NODE set "PIE_NODE=%%N"
if not defined PIE_NODE if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" set "PIE_NODE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not defined PIE_NODE (
  echo Node.js is required to start PIE ITR V2. Install Node.js LTS, then run this file again.
  pause
  exit /b 1
)
if exist "node_modules\.bin\vite.cmd" (
  start "PIE ITR V2" /b "%PIE_NODE%" "node_modules\vite\bin\vite.js" --host 127.0.0.1 --port 5173
) else (
  where pnpm >nul 2>nul || (
    echo Frontend dependencies are missing. Run: corepack enable ^&^& corepack pnpm install
    pause
    exit /b 1
  )
  start "PIE ITR V2" /b pnpm dev --host 127.0.0.1 --port 5173
)
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:5173/
