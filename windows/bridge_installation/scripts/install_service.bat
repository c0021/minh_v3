@echo off
REM MinhOS Bridge - Windows Service Installation Script
REM This script installs the MinhOS bridge as a Windows Service

echo ========================================
echo MinhOS Bridge Service Installation
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
set SERVICE_DISPLAY_NAME=MinhOS Sierra Chart Bridge
set SERVICE_DESCRIPTION=MinhOS Bridge for Sierra Chart market data integration with auto-restart capabilities
set BRIDGE_DIR=%~dp0
set PYTHON_EXE=%BRIDGE_DIR%venv\Scripts\python.exe
set SERVICE_SCRIPT=%BRIDGE_DIR%bridge_service.py

echo Current directory: %BRIDGE_DIR%
echo Python executable: %PYTHON_EXE%
echo Service script: %SERVICE_SCRIPT%
echo.

REM Check if Python virtual environment exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python virtual environment not found at %PYTHON_EXE%
    echo Please run start_bridge.bat first to create the virtual environment
    pause
    exit /b 1
)

REM Check if service script exists
if not exist "%SERVICE_SCRIPT%" (
    echo ERROR: Service script not found at %SERVICE_SCRIPT%
    pause
    exit /b 1
)

REM Stop existing service if running
echo Checking for existing service...
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% EQU 0 (
    echo Stopping existing service...
    sc stop "%SERVICE_NAME%"
    timeout /t 5 /nobreak >nul
    echo Deleting existing service...
    sc delete "%SERVICE_NAME%"
    timeout /t 2 /nobreak >nul
)

REM Create the Windows Service
echo Creating Windows Service...
sc create "%SERVICE_NAME%" ^
    binPath= "\"%PYTHON_EXE%\" \"%SERVICE_SCRIPT%\"" ^
    DisplayName= "%SERVICE_DISPLAY_NAME%" ^
    start= auto ^
    obj= LocalSystem

if %errorLevel% NEQ 0 (
    echo ERROR: Failed to create service
    pause
    exit /b 1
)

REM Configure service description
sc description "%SERVICE_NAME%" "%SERVICE_DESCRIPTION%"

REM Configure service recovery options (auto-restart on failure)
echo Configuring auto-restart policy...
sc failure "%SERVICE_NAME%" reset= 86400 actions= restart/5000/restart/10000/restart/30000

REM Create logs directory
if not exist "%BRIDGE_DIR%logs" (
    mkdir "%BRIDGE_DIR%logs"
)

echo.
echo ========================================
echo Service Installation Complete!
echo ========================================
echo.
echo Service Name: %SERVICE_NAME%
echo Display Name: %SERVICE_DISPLAY_NAME%
echo Status: Installed (not started)
echo.
echo To start the service:
echo   sc start %SERVICE_NAME%
echo   OR use Services.msc GUI
echo.
echo To check service status:
echo   sc query %SERVICE_NAME%
echo.
echo Service logs will be written to:
echo   %BRIDGE_DIR%logs\bridge_service.log
echo.
echo The service will automatically:
echo - Start when Windows boots
echo - Restart if the bridge crashes
echo - Handle the 100-request limit by auto-restarting
echo.

choice /c YN /n /m "Start the service now? (Y/N): "
if errorlevel 2 goto :END
if errorlevel 1 goto :START_SERVICE

:START_SERVICE
echo Starting MinhOS Bridge Service...
sc start "%SERVICE_NAME%"
if %errorLevel% EQU 0 (
    echo Service started successfully!
    echo.
    echo You can monitor the service in:
    echo - Services.msc (Windows Services Manager)
    echo - Task Manager ^> Services tab
    echo - Log file: %BRIDGE_DIR%logs\bridge_service.log
) else (
    echo Failed to start service. Check the Windows Event Log for details.
)

:END
echo.
echo Installation complete!
pause