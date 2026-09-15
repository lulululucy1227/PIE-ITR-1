@echo off
setlocal
cd /d "%~dp0error-code-pilot"

if not exist "scripts\launch-local.mjs" (
  echo PIE Troubleshooter files were not found.
  echo Keep this file in the PIE-ITR-ErrorCode folder and try again.
  pause
  exit /b 1
)

set "NODE_EXE="
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" set "NODE_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not defined NODE_EXE if exist "%ProgramFiles%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if not defined NODE_EXE for /f "delims=" %%N in ('where node 2^>nul') do if not defined NODE_EXE set "NODE_EXE=%%N"

if not defined NODE_EXE (
  echo Node.js is not available on this computer.
  echo Open Codex once, then double-click this file again.
  pause
  exit /b 1
)

"%NODE_EXE%" scripts\launch-local.mjs
if errorlevel 1 pause
