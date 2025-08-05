@echo off
echo Checking what's using port 8765...
echo.
netstat -ano | findstr :8765
echo.
echo To kill the process, use: taskkill /PID [process_id] /F
pause