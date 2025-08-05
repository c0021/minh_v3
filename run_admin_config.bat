@echo off
echo === Windows 10 Unrestricted Development Access Setup ===
echo This script will configure your system for unrestricted development access.
echo.

:: Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Running as Administrator
) else (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo 1. Disabling UAC (User Account Control)...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 0 /f
if %errorLevel% == 0 (
    echo ✓ UAC disabled (requires restart to take effect)
) else (
    echo ✗ Failed to disable UAC
)

echo.
echo 2. Adding Windows Defender exclusions...
powershell -Command "Add-MpPreference -ExclusionPath 'C:\Users\colin\Sync\minh_v4'" 2>nul
if %errorLevel% == 0 (echo ✓ Added exclusion: C:\Users\colin\Sync\minh_v4) else (echo ! Failed to add exclusion: minh_v4)

powershell -Command "Add-MpPreference -ExclusionPath 'C:\Users\colin\AppData\Roaming\npm'" 2>nul
if %errorLevel% == 0 (echo ✓ Added exclusion: npm folder) else (echo ! Failed to add exclusion: npm)

powershell -Command "Add-MpPreference -ExclusionPath 'C:\Program Files\nodejs'" 2>nul
if %errorLevel% == 0 (echo ✓ Added exclusion: Node.js) else (echo ! Failed to add exclusion: nodejs)

echo.
echo 3. Disabling SmartScreen...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" /v SmartScreenEnabled /t REG_SZ /d "Off" /f
if %errorLevel% == 0 (
    echo ✓ SmartScreen disabled
) else (
    echo ✗ Failed to disable SmartScreen
)

echo.
echo 4. Enabling Developer Mode...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" /v AllowDevelopmentWithoutDevLicense /t REG_DWORD /d 1 /f
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" /v AllowAllTrustedApps /t REG_DWORD /d 1 /f
if %errorLevel% == 0 (
    echo ✓ Developer Mode enabled
) else (
    echo ✗ Failed to enable Developer Mode
)

echo.
echo 5. Adding Windows Firewall exceptions...
netsh advfirewall firewall add rule name="Node.js" dir=in action=allow program="C:\Program Files\nodejs\node.exe" 2>nul
netsh advfirewall firewall add rule name="Node.js" dir=out action=allow program="C:\Program Files\nodejs\node.exe" 2>nul
echo ✓ Added firewall rules for Node.js

echo.
echo 6. Setting network profile to Private...
powershell -Command "Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private" 2>nul
if %errorLevel% == 0 (
    echo ✓ Network profile set to Private
) else (
    echo ! Network profile setting may have failed
)

echo.
echo === Configuration Complete ===
echo.
echo IMPORTANT: You must RESTART your computer for all changes to take effect!
echo.
echo Changes made:
echo • UAC disabled (no more admin prompts)
echo • Windows Defender exclusions added for dev folders
echo • SmartScreen disabled
echo • Developer Mode enabled
echo • Firewall exceptions added for Node.js
echo • Network set to Private (enables local discovery)
echo.
echo Press any key to continue...
pause
