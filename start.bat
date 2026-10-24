@echo off
title MindSync - AI Personal Knowledge Vault
echo ========================================================
echo       MindSync Full-Stack Launcher (Frontend + Backend)
echo ========================================================
echo.
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    start "MindSync Backend (FastAPI)" cmd /c ".venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000"
) else (
    start "MindSync Backend (FastAPI)" cmd /c "python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000"
)

echo [2/3] Waiting for services to initialize...
timeout /t 2 /nobreak >nul

echo [3/3] Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo Starting Vite Frontend on http://localhost:5173 ...
echo (Keep this window open while using MindSync)
echo.
call "C:\Program Files\nodejs\npm.cmd" run dev
pause
