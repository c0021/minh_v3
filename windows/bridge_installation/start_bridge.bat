@echo off
REM MinhOS Sierra Chart Bridge Startup Script
REM Enhanced bridge with historical data access
REM 
REM This script starts the MinhOS bridge service with proper environment setup
REM and error handling for production deployment.

echo ========================================
echo MinhOS Sierra Chart Bridge v3.1.0
echo Enhanced with Historical Data Access
echo ========================================
echo.

REM Get current directory
set BRIDGE_DIR=%~dp0
cd /d "%BRIDGE_DIR%"

echo Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's added to PATH
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
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

REM Log startup information
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
echo Press Ctrl+C to stop the bridge service
echo ========================================
echo.

REM Start the bridge with enhanced error handling
:START_BRIDGE
python bridge.py
set EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo Bridge service stopped (Exit code: %EXIT_CODE%)
echo ========================================

if %EXIT_CODE%==0 (
    echo Bridge stopped normally
) else (
    echo Bridge stopped with error code: %EXIT_CODE%
    echo.
    echo Common solutions:
    echo - Check if Sierra Chart is running
    echo - Verify Tailscale connectivity
    echo - Ensure port 8765 is not in use
    echo - Check bridge.log for detailed error information
)

echo.
echo Options:
echo   R - Restart bridge service
echo   L - View last 20 lines of log file
echo   Q - Quit
echo.

choice /c RLQ /n /m "Enter your choice (R/L/Q): "
if errorlevel 3 goto :END
if errorlevel 2 goto :VIEW_LOG
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