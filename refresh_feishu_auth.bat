@echo off
setlocal
cd /d "%~dp0"
set "PIE_PY="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PIE_PY set "PIE_PY=%%P"
if not defined PIE_PY if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PIE_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not defined PIE_PY (
  echo Python is required to refresh Feishu authorization.
  pause
  exit /b 1
)
echo Close the legacy ticket assistant before continuing.
echo A browser window will open for Feishu authorization.
"%PIE_PY%" -B feishu_auth.py
pause
