@echo off
echo ========================================
echo Opening MinhOS Bridge Dashboard
echo ========================================
echo.
echo Opening dashboard in your default browser...
start "" "%~dp0bridge_dashboard.html"
echo.
echo Dashboard opened!
echo Note: The dashboard will connect to http://localhost:8765
echo Make sure the bridge is running for live data.
pause
