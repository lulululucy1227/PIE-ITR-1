@echo off
setlocal
cd /d "%~dp0"
if exist "runtime\node.exe" (
  "runtime\node.exe" scripts\launch-local.mjs
) else (
  where node >nul 2>nul
  if not errorlevel 1 (
    node scripts\launch-local.mjs
  ) else (
    echo This package is incomplete: runtime\node.exe is missing.
  )
)
if errorlevel 1 pause
