@echo off
REM MinhOS Bridge - Windows Service Uninstallation Script

echo ========================================
echo MinhOS Bridge Service Uninstallation
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

echo Checking for existing service...
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Service "%SERVICE_NAME%" is not installed.
    pause
    exit /b 0
)

echo Stopping service...
sc stop "%SERVICE_NAME%"
timeout /t 5 /nobreak >nul

echo Deleting service...
sc delete "%SERVICE_NAME%"

if %errorLevel% EQU 0 (
    echo Service "%SERVICE_NAME%" has been successfully removed.
) else (
    echo Failed to remove service. Check Windows Event Log for details.
)

echo.
echo Uninstallation complete!
pause