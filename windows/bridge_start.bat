@echo off
echo ========================================
echo MinhOS Windows Bridge Starter
echo ========================================
echo.
echo Starting bridge from: %~dp0bridge_installation\
echo.
cd /d "%~dp0bridge_installation"
call scripts\start_bridge.bat
echo.
echo Bridge startup complete.
pause
