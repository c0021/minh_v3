@echo off
echo === Sierra Chart Status Check ===
echo.

echo Checking if Sierra Chart is running...
tasklist /FI "IMAGENAME eq SierraChart.exe" 2>NUL | find /I /N "SierraChart.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Sierra Chart is running
) else (
    echo [ERROR] Sierra Chart is NOT running!
    echo Please start Sierra Chart before running the bridge.
)
echo.

echo Checking Sierra Chart data directories...
if exist "C:\SierraChart\Data" (
    echo [OK] Found C:\SierraChart\Data
    dir "C:\SierraChart\Data\*.scid" 2>NUL | find "File(s)" >NUL
    if "%ERRORLEVEL%"=="0" (
        echo [OK] SCID data files found
    ) else (
        echo [WARN] No SCID files found in data directory
    )
) else if exist "C:\Sierra Chart\Data" (
    echo [OK] Found C:\Sierra Chart\Data
    dir "C:\Sierra Chart\Data\*.scid" 2>NUL | find "File(s)" >NUL
    if "%ERRORLEVEL%"=="0" (
        echo [OK] SCID data files found
    ) else (
        echo [WARN] No SCID files found in data directory
    )
) else (
    echo [ERROR] Sierra Chart data directory not found!
)
echo.

echo Checking network connectivity...
ping -n 1 100.123.37.79 >NUL 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [OK] Can reach MinhOS server via Tailscale
) else (
    echo [ERROR] Cannot reach MinhOS server - check Tailscale connection
)
echo.

echo Checking if bridge is already running...
netstat -an | find ":8765" | find "LISTENING" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Bridge port 8765 is listening
    curl -s http://localhost:8765/health >NUL 2>&1
    if "%ERRORLEVEL%"=="0" (
        echo [OK] Bridge is responding to health checks
    ) else (
        echo [WARN] Bridge port is open but not responding
    )
) else (
    echo [INFO] Bridge is not currently running on port 8765
)
echo.

pause