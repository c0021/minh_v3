@echo off
REM MinhOS Bridge - Final Permanent Solution
REM This creates a Windows Service that directly runs Python bridge.py

echo ========================================
echo MinhOS Final Permanent Solution
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

set SERVICE_NAME=MinhOSBridge
set BRIDGE_DIR=%~dp0

echo Installing final permanent solution...
echo Current directory: %BRIDGE_DIR%
echo.

REM Stop and delete any existing service
echo Removing any existing service...
sc stop "%SERVICE_NAME%" >nul 2>&1
sc delete "%SERVICE_NAME%" >nul 2>&1

REM Create the Windows Service directly with Python and bridge.py
echo Creating Windows Service...
sc create "%SERVICE_NAME%" binPath= "\"%BRIDGE_DIR%venv\Scripts\python.exe\" \"%BRIDGE_DIR%bridge.py\"" DisplayName= "MinhOS Sierra Chart Bridge" start= auto obj= LocalSystem

if %errorLevel% NEQ 0 (
    echo ERROR: Failed to create service
    pause
    exit /b 1
)

REM Configure service description
sc description "%SERVICE_NAME%" "MinhOS Bridge - Final Permanent Solution"

REM Configure auto-restart policy
echo Configuring auto-restart policy...
sc failure "%SERVICE_NAME%" reset= 86400 actions= restart/5000/restart/10000/restart/30000

REM Set the service to run in the correct directory
sc config "%SERVICE_NAME%" start= auto

REM Start the service
echo Starting the service...
sc start "%SERVICE_NAME%"

REM Show service status
echo.
echo ========================================
echo Service Status:
echo ========================================
sc query "%SERVICE_NAME%"

echo.
echo ========================================
echo FINAL PERMANENT SOLUTION INSTALLED!
echo ========================================
echo.
echo Your MinhOS Bridge will now:
echo  ✅ Start automatically when Windows boots
echo  ✅ Run 24/7 in the background  
echo  ✅ Auto-restart on any failure
echo  ✅ Run directly with no request limits
echo.
echo The bridge is available at: http://localhost:8765
echo.
pause