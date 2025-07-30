@echo off
REM Sierra Chart Data Structure Investigation
REM Run this on Windows to discover Sierra Chart data organization

echo ========================================
echo Sierra Chart Data Structure Investigation
echo ========================================
echo Date/Time: %date% %time%
echo.

echo 1. SEARCHING FOR SIERRA CHART INSTALLATIONS...
echo ========================================

REM Check common Sierra Chart installation paths
set FOUND_INSTALLATIONS=

if exist "C:\SierraChart" (
    echo [FOUND] C:\SierraChart\
    set FOUND_INSTALLATIONS=1
    dir "C:\SierraChart" /b
    echo.
)

if exist "C:\Program Files\Sierra Chart" (
    echo [FOUND] C:\Program Files\Sierra Chart\
    set FOUND_INSTALLATIONS=1
    dir "C:\Program Files\Sierra Chart" /b
    echo.
)

if exist "C:\Program Files (x86)\Sierra Chart" (
    echo [FOUND] C:\Program Files (x86)\Sierra Chart\
    set FOUND_INSTALLATIONS=1
    dir "C:\Program Files (x86)\Sierra Chart" /b
    echo.
)

if exist "D:\SierraChart" (
    echo [FOUND] D:\SierraChart\
    set FOUND_INSTALLATIONS=1
    dir "D:\SierraChart" /b
    echo.
)

REM Check user data directories
if exist "%APPDATA%\SierraChart" (
    echo [FOUND] %APPDATA%\SierraChart\
    set FOUND_INSTALLATIONS=1
    dir "%APPDATA%\SierraChart" /b
    echo.
)

if exist "%LOCALAPPDATA%\SierraChart" (
    echo [FOUND] %LOCALAPPDATA%\SierraChart\
    set FOUND_INSTALLATIONS=1
    dir "%LOCALAPPDATA%\SierraChart" /b
    echo.
)

if not defined FOUND_INSTALLATIONS (
    echo [ERROR] No Sierra Chart installations found in standard locations
    echo.
    echo Searching entire C: drive for SierraChart folders...
    dir C:\ /s /b /ad | findstr /i sierrachart
    echo.
)

echo 2. INVESTIGATING DATA DIRECTORIES...
echo ========================================

REM Function to investigate a data directory
call :InvestigateDataDir "C:\SierraChart\Data"
call :InvestigateDataDir "C:\Program Files\Sierra Chart\Data"
call :InvestigateDataDir "C:\Program Files (x86)\Sierra Chart\Data"
call :InvestigateDataDir "D:\SierraChart\Data"
call :InvestigateDataDir "%APPDATA%\SierraChart\Data"
call :InvestigateDataDir "%LOCALAPPDATA%\SierraChart\Data"

echo 3. SEARCHING FOR HISTORICAL DATA FILES...
echo ========================================

echo Searching for .dly files (Daily data):
for %%d in ("C:\SierraChart\Data" "C:\Program Files\Sierra Chart\Data" "C:\Program Files (x86)\Sierra Chart\Data" "D:\SierraChart\Data") do (
    if exist %%d (
        echo.
        echo Checking %%d for .dly files:
        dir %%d\*.dly /s 2>nul | find /v "File Not Found" | find /v "0 File(s)"
    )
)

echo.
echo Searching for .scid files (Intraday/Tick data):
for %%d in ("C:\SierraChart\Data" "C:\Program Files\Sierra Chart\Data" "C:\Program Files (x86)\Sierra Chart\Data" "D:\SierraChart\Data") do (
    if exist %%d (
        echo.
        echo Checking %%d for .scid files:
        dir %%d\*.scid /s 2>nul | find /v "File Not Found" | find /v "0 File(s)"
    )
)

echo.
echo 4. SAMPLE FILES ANALYSIS...
echo ========================================

REM Find and analyze sample files
for %%d in ("C:\SierraChart\Data" "C:\Program Files\Sierra Chart\Data" "C:\Program Files (x86)\Sierra Chart\Data" "D:\SierraChart\Data") do (
    if exist %%d (
        echo.
        echo Sample files in %%d:
        echo --- .dly files (first 10) ---
        dir %%d\*.dly /o:d 2>nul | head -n 10 2>nul || (dir %%d\*.dly /o:d 2>nul | findstr /n ".*" | findstr "^[1-9]:")
        
        echo --- .scid files (first 10) ---
        dir %%d\*.scid /o:d 2>nul | head -n 10 2>nul || (dir %%d\*.scid /o:d 2>nul | findstr /n ".*" | findstr "^[1-9]:")
        
        echo --- Subdirectories ---
        dir %%d /ad /b 2>nul
    )
)

echo.
echo 5. TRADING SYMBOL ANALYSIS...
echo ========================================

echo Looking for common futures symbols (NQ, ES, YM, RTY):
for %%s in (NQ ES YM RTY CL GC SI) do (
    echo.
    echo Symbol: %%s
    for %%d in ("C:\SierraChart\Data" "C:\Program Files\Sierra Chart\Data" "C:\Program Files (x86)\Sierra Chart\Data" "D:\SierraChart\Data") do (
        if exist %%d (
            echo   In %%d:
            dir %%d\%%s*.* /b 2>nul | findstr /i "\.dly \.scid" || echo     No %%s files found
        )
    )
)

echo.
echo 6. FILE SIZE AND DATE ANALYSIS...
echo ========================================

for %%d in ("C:\SierraChart\Data" "C:\Program Files\Sierra Chart\Data" "C:\Program Files (x86)\Sierra Chart\Data" "D:\SierraChart\Data") do (
    if exist %%d (
        echo.
        echo Recent files in %%d (by date):
        dir %%d\*.dly %%d\*.scid /o:-d /t:w 2>nul | head -n 15 2>nul || (
            echo Daily files:
            dir %%d\*.dly /o:-d /t:w 2>nul | findstr /n ".*" | findstr "^[1-5]:"
            echo SCID files:
            dir %%d\*.scid /o:-d /t:w 2>nul | findstr /n ".*" | findstr "^[1-5]:"
        )
    )
)

echo.
echo ========================================
echo Investigation Complete
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Review the file paths and naming patterns above
echo 2. Update your MinhOS bridge file_access_api.py with correct paths
echo 3. Test file access with the discovered file names
echo.
echo This information will help configure your bridge API correctly.
echo.

pause
goto :eof

:InvestigateDataDir
set DIR_PATH=%~1
if exist %DIR_PATH% (
    echo.
    echo [FOUND] Data directory: %DIR_PATH%
    echo Directory contents:
    dir %DIR_PATH% /b
    echo.
    echo File counts:
    dir %DIR_PATH%\*.dly 2>nul | find /c ".dly" && echo .dly files found || echo No .dly files
    dir %DIR_PATH%\*.scid 2>nul | find /c ".scid" && echo .scid files found || echo No .scid files
    echo.
) else (
    echo [NOT FOUND] %DIR_PATH%
)
goto :eof