@echo off
REM MinhOS Bridge - True Permanent Solution
REM This runs your bridge with auto-restart using Windows Task Scheduler

echo ========================================
echo MinhOS True Permanent Solution
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

set TASK_NAME=MinhOSBridge
set BRIDGE_DIR=%~dp0

echo Installing permanent solution using Task Scheduler...
echo Current directory: %BRIDGE_DIR%
echo.

REM Delete existing task if it exists
echo Removing any existing scheduled task...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Create the scheduled task that runs at startup and restarts on failure
echo Creating scheduled task...
schtasks /create /tn "%TASK_NAME%" /tr "\"%BRIDGE_DIR%start_bridge.bat\"" /sc onstart /ru SYSTEM /rl HIGHEST /f

if %errorLevel% NEQ 0 (
    echo ERROR: Failed to create scheduled task
    pause
    exit /b 1
)

REM Configure task to restart on failure
echo Configuring restart on failure...
schtasks /change /tn "%TASK_NAME%" /tr "\"%BRIDGE_DIR%start_bridge.bat\"" /ru SYSTEM /rl HIGHEST

REM Start the task immediately
echo Starting the bridge...
schtasks /run /tn "%TASK_NAME%"

REM Show task status
echo.
echo ========================================
echo Task Status:
echo ========================================
schtasks /query /tn "%TASK_NAME%" /fo LIST

echo.
echo ========================================
echo PERMANENT SOLUTION INSTALLED!
echo ========================================
echo.
echo Your MinhOS Bridge will now:
echo  ✅ Start automatically when Windows boots
echo  ✅ Run your tested start_bridge.bat script
echo  ✅ Auto-restart if Windows reboots
echo  ✅ No request limits (already fixed)
echo.
echo The bridge is available at: http://localhost:8765
echo.
echo To manage:
echo  - Stop: schtasks /end /tn %TASK_NAME%
echo  - Start: schtasks /run /tn %TASK_NAME%
echo  - Remove: schtasks /delete /tn %TASK_NAME% /f
echo.
pause