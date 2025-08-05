@echo off
echo ========================================
echo MinhOS Bridge Service Status
echo ========================================
echo.
echo Checking Windows service status...
echo.
cd /d "%~dp0bridge_installation"
call scripts\service_status.bat
echo.
pause
