@echo off
setlocal
cd /d "%~dp0"
start "PIE ITR Local API" /b python -B local_api.py
cd frontend
start "PIE ITR V2" /b pnpm dev --host 127.0.0.1 --port 5173
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:5173/
