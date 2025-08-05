@echo off
echo ========================================
echo MinhOS Bridge Monitor Starter
echo ========================================
echo.
echo Starting monitor from: %~dp0bridge_installation\
echo.
cd /d "%~dp0bridge_installation"
call scripts\start_monitor.bat
