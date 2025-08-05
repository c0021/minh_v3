@echo off
echo ========================================
echo 📧 MinhOS Bridge Email Alert Setup
echo ========================================
echo.
echo This will configure email notifications for bridge shutdowns.
echo You'll be able to receive alerts even when away from your computer.
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Starting email alert configuration...
echo.

REM Run the email setup
python email_alerts.py

echo.
echo ========================================
echo Email Alert Setup Complete!
echo ========================================
echo.
echo Your bridge monitoring will now send email alerts for:
echo - Bridge shutdowns (immediate notification)
echo - Bridge recovery (when bridge comes back online)
echo - Critical system events
echo.
echo The monitoring system will continue running in the background
echo and send you emails whenever issues occur.
echo.
pause
