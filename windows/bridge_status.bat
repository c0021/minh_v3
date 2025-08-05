@echo off
echo ========================================
echo MinhOS Bridge Status Checker
echo ========================================
echo.
echo Checking bridge status...
echo.
cd /d "%~dp0bridge_installation"
call scripts\check_status.bat
echo.
pause
