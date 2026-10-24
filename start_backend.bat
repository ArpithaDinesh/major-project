@echo off
echo ========================================================
echo       MindSync Python FastAPI Backend Launcher
echo ========================================================
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
    echo Using isolated virtual environment (.venv)
) else (
    set "PYTHON_CMD=python"
)

echo.
echo Starting FastAPI Uvicorn Server on http://localhost:8000 ...
%PYTHON_CMD% backend\run.py
pause
