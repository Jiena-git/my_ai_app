@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ========================================
echo   Smart Classroom Monitor v3.0
echo   Vue3 + ECharts + FastAPI
echo ========================================
echo.
echo Starting server...
echo.
echo   Backend API : http://127.0.0.1:8000/api/*
echo   Frontend    : http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.
venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
