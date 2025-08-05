@echo off
REM MinhOS Bridge - Service Status and Management Script

echo ========================================
echo MinhOS Bridge Service Status
echo ========================================
echo.

set SERVICE_NAME=MinhOSBridge
set LOG_FILE=%~dp0logs\bridge_service.log

REM Check service status
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Service "%SERVICE_NAME%" is not installed.
    echo Run install_service.bat to install it.
    goto :END
)

echo Service Information:
sc query "%SERVICE_NAME%"
echo.

echo Service Configuration:
sc qc "%SERVICE_NAME%"
echo.

REM Show recent log entries if log file exists
if exist "%LOG_FILE%" (
    echo ========================================
    echo Recent Log Entries (last 20 lines):
    echo ========================================
    powershell "Get-Content '%LOG_FILE%' -Tail 20"
    echo.
) else (
    echo No log file found at %LOG_FILE%
    echo.
)

echo ========================================
echo Service Management Options:
echo ========================================
echo 1. Start Service
echo 2. Stop Service
echo 3. Restart Service
echo 4. View Full Log
echo 5. Exit
echo.

choice /c 12345 /n /m "Select option (1-5): "
if errorlevel 5 goto :END
if errorlevel 4 goto :VIEW_LOG
if errorlevel 3 goto :RESTART_SERVICE
if errorlevel 2 goto :STOP_SERVICE
if errorlevel 1 goto :START_SERVICE

:START_SERVICE
echo Starting service...
sc start "%SERVICE_NAME%"
goto :END

:STOP_SERVICE
echo Stopping service...
sc stop "%SERVICE_NAME%"
goto :END

:RESTART_SERVICE
echo Restarting service...
sc stop "%SERVICE_NAME%"
timeout /t 5 /nobreak >nul
sc start "%SERVICE_NAME%"
goto :END

:VIEW_LOG
if exist "%LOG_FILE%" (
    echo ========================================
    echo Full Log File Contents:
    echo ========================================
    type "%LOG_FILE%"
) else (
    echo No log file found.
)
goto :END

:END
echo.
pause