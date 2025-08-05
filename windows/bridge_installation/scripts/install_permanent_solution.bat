@echo off
REM MinhOS Bridge - Permanent Solution Installation
REM This creates a Windows Service that runs your working start_bridge.bat

echo ========================================
echo MinhOS Bridge Permanent Solution Setup
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

echo Installing permanent solution...
echo Current directory: %BRIDGE_DIR%
echo.

REM Stop and delete any existing service
echo Removing any existing service...
sc stop "%SERVICE_NAME%" >nul 2>&1
sc delete "%SERVICE_NAME%" >nul 2>&1

REM Create the Windows Service using service wrapper
echo Creating Windows Service...
sc create "%SERVICE_NAME%" binPath= "py \"%BRIDGE_DIR%service_wrapper.py\"" DisplayName= "MinhOS Sierra Chart Bridge" start= auto obj= LocalSystem

if %errorLevel% NEQ 0 (
    echo ERROR: Failed to create service
    pause
    exit /b 1
)

REM Configure service description
sc description "%SERVICE_NAME%" "MinhOS Bridge - Permanent Solution with Auto-Restart"

REM Configure auto-restart policy
echo Configuring auto-restart policy...
sc failure "%SERVICE_NAME%" reset= 86400 actions= restart/5000/restart/10000/restart/30000

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
echo PERMANENT SOLUTION INSTALLED!
echo ========================================
echo.
echo Your MinhOS Bridge will now:
echo  ✅ Start automatically when Windows boots
echo  ✅ Run 24/7 in the background
echo  ✅ Auto-restart on any failure
echo  ✅ Use your tested start_bridge.bat script
echo.
echo The bridge is available at: http://localhost:8765
echo.
echo To manage the service:
echo  - Start: sc start %SERVICE_NAME%
echo  - Stop:  sc stop %SERVICE_NAME%
echo  - Status: sc query %SERVICE_NAME%
echo.
pause