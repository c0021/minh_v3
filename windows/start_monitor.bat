@echo off
echo ========================================
echo MinhOS Bridge Monitor
echo ========================================
echo.
echo Starting bridge monitoring...
echo This will watch for bridge shutdowns and capture diagnostic info.
echo Press Ctrl+C to stop monitoring.
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install required monitoring dependencies
echo Checking monitoring dependencies...
python -m pip install psutil requests --quiet

REM Start the monitor
echo.
echo ========================================
echo Monitor starting...
echo ========================================
python monitor_bridge.py

pause
