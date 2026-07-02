@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   Deploy Fine-tuned Model
echo ========================================
echo.

set SRC=runs\detect\runs\train\classroom_finetune\weights\best.pt
set DST=weights\yolov8s.pt

if not exist "%SRC%" (
    echo [ERROR] Trained model not found: %SRC%
    echo Training may not be complete yet.
    pause
    exit /b 1
)

echo Backing up original model...
copy /Y "%DST%" weights\yolov8s_backup.pt

echo Deploying fine-tuned model...
copy /Y "%SRC%" "%DST%"

echo.
echo Done! Restart the server to use the new model.
echo Run: start.bat
pause
