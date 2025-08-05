@echo off
REM MinhOS Sierra Chart Bridge Startup Script - ENHANCED VERSION
REM This version includes auto-restart logic for request limits and other failures

echo ========================================
echo MinhOS Sierra Chart Bridge v3.1.0
echo Enhanced with Auto-Restart Capability
echo ========================================
echo.

REM Get current directory
set BRIDGE_DIR=%~dp0
cd /d "%BRIDGE_DIR%"

echo Current directory: %CD%
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's added to PATH
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

echo Python version:
py --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo Dependencies already installed
)
echo.

REM Check if required files exist
if not exist "bridge.py" (
    echo ERROR: bridge.py not found
    echo Please ensure all bridge files are present
    pause
    exit /b 1
)

if not exist "file_access_api.py" (
    echo ERROR: file_access_api.py not found
    echo Please ensure all bridge files are present
    pause
    exit /b 1
)

REM Set environment variables for better performance
set PYTHONUNBUFFERED=1
set PYTHONDONTWRITEBYTECODE=1

REM Initialize restart tracking
set RESTART_COUNT=0
set MAX_RESTARTS_PER_HOUR=10

echo ========================================
echo Starting MinhOS Bridge Service
echo ========================================
echo Date/Time: %date% %time%
echo Bridge Directory: %CD%
echo Python Path: %VIRTUAL_ENV%
echo.
echo Available Endpoints:
echo   Health Check: http://localhost:8765/health
echo   Status: http://localhost:8765/status
echo   Market Data: http://localhost:8765/api/market_data
echo   File Access: http://localhost:8765/api/file/list
echo   WebSocket: ws://localhost:8765/ws/market_data
echo.
echo AUTO-RESTART ENABLED: Bridge will automatically restart on failures
echo Press Ctrl+C to stop the bridge service
echo ========================================
echo.

REM Check if port 8765 is already in use
echo Checking if port 8765 is available...
netstat -ano | findstr :8765 >nul 2>&1
if not errorlevel 1 (
    echo.
    echo WARNING: Port 8765 is already in use!
    echo.
    echo Processes using port 8765:
    netstat -ano | findstr :8765
    echo.
    echo Killing processes using port 8765...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8765') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    echo Port 8765 should now be available
    echo.
)

REM Start the bridge with auto-restart logic
:START_BRIDGE
set /a RESTART_COUNT+=1
echo.
echo [%date% %time%] Starting bridge (attempt #%RESTART_COUNT%)...

py bridge.py
set EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo Bridge service stopped (Exit code: %EXIT_CODE%)
echo ========================================

if %EXIT_CODE%==0 (
    echo Bridge stopped normally
    set WAIT_TIME=5
) else (
    echo Bridge stopped with error code: %EXIT_CODE%
    set WAIT_TIME=10
    echo.
    echo Common solutions:
    echo - Check if Sierra Chart is running
    echo - Verify Tailscale connectivity
    echo - Check bridge.log for detailed error information
)

REM Check restart limits
if %RESTART_COUNT% GEQ %MAX_RESTARTS_PER_HOUR% (
    echo.
    echo WARNING: Maximum restarts (%MAX_RESTARTS_PER_HOUR%) reached.
    echo Waiting 60 seconds before allowing more restarts...
    timeout /t 60 /nobreak >nul
    set RESTART_COUNT=0
)

echo.
echo Options:
echo   A - Auto-restart in %WAIT_TIME% seconds (default)
echo   R - Restart now
echo   L - View last 20 lines of log file
echo   Q - Quit
echo.

choice /c ARLQ /t %WAIT_TIME% /d A /n /m "Choice (A/R/L/Q) - auto-restart in %WAIT_TIME%s: "
if errorlevel 4 goto :END
if errorlevel 3 goto :VIEW_LOG
if errorlevel 2 goto :START_BRIDGE
if errorlevel 1 goto :START_BRIDGE

:VIEW_LOG
echo.
echo ========================================
echo Last 20 lines of bridge.log:
echo ========================================
if exist "bridge.log" (
    powershell "Get-Content bridge.log -Tail 20"
) else (
    echo Log file not found
)
echo ========================================
echo.
pause
goto :START_BRIDGE

:END
echo.
echo Thank you for using MinhOS Bridge Service!
pause