@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   Smart Classroom - First-time Setup
echo ========================================
echo.

if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/3] Virtual environment already exists, skip.
)

echo.
echo [2/3] Installing Python dependencies...
venv\Scripts\pip install fastapi uvicorn ultralytics opencv-python websockets "numpy<2" -i https://mirrors.aliyun.com/pypi/simple/

echo.
echo [3/3] Installing Node.js dependencies and building frontend...
cd frontend-vue
call npm install
call npm run build
cd ..

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo Next step: Run start.bat or:
echo   venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
echo.
echo Then open: http://127.0.0.1:8000
echo.
pause
