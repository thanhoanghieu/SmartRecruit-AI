@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ======================================
echo HE THONG QUAN LY TUYEN DUNG AI
echo ======================================
if not exist "app\main.py" (
    echo LOI: Khong tim thay app\main.py
    pause
    exit /b 1
)
if not exist "run.py" (
    echo LOI: Khong tim thay run.py
    pause
    exit /b 1
)
python -c "import uvicorn, fastapi, sqlalchemy, pydantic_settings, jinja2" >nul 2>&1
python run.py
if errorlevel 1 (
    echo LOI: May chu khoi dong that bai.
    pause
    exit /b 1
)
echo Dang khoi dong may chu...
python run.py
pause