@echo off
echo ========================================
echo MinhOS Bridge Status Check
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run status check
python check_bridge_status.py

echo.
echo ========================================
echo Opening Status Dashboard...
echo ========================================
echo.

REM Open the status dashboard in default browser
start bridge_status_dashboard.html

echo Dashboard opened in your browser.
echo You can now see real-time bridge status!
echo.
pause
