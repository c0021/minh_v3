@echo off
cd /d "C:\Users\cong7\Sync\minh_v3\windows\bridge_installation"
echo Starting MinhOS Bridge...
echo.
echo Bridge will be available at:
echo   - http://localhost:8765/health
echo   - http://cThinkpad:8765/health
echo.
echo Press Ctrl+C to stop the bridge
echo.
venv\Scripts\python.exe bridge.py
pause 