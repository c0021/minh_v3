# PowerShell script to set up Sierra Chart Bridge on new Windows machine
# Run as Administrator

param(
    [string]$InstallPath = "C:\MinhOS_Bridge",
    [switch]$SkipTCPOptimization = $false,
    [switch]$AutoStart = $false
)

Write-Host "MinhOS Sierra Chart Bridge Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script must be run as Administrator. Exiting..." -ForegroundColor Red
    exit 1
}

# Create installation directory
Write-Host "Creating installation directory: $InstallPath" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null

# Copy current directory files to installation path
Write-Host "Copying Bridge files..." -ForegroundColor Yellow
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item -Path "$ScriptPath\*" -Destination $InstallPath -Recurse -Force

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8 or later." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Set-Location $InstallPath
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Apply TCP optimizations
if (-not $SkipTCPOptimization) {
    Write-Host "" 
    Write-Host "Applying TCP optimizations..." -ForegroundColor Yellow
    & "$InstallPath\tcp_optimize_windows.bat"
    Write-Host "TCP optimizations applied!" -ForegroundColor Green
} else {
    Write-Host "Skipping TCP optimizations (use -SkipTCPOptimization:`$false to apply)" -ForegroundColor Yellow
}

# Create firewall rule
Write-Host ""
Write-Host "Creating Windows Firewall rule..." -ForegroundColor Yellow
$ruleName = "MinhOS Bridge API"
Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8765 `
    -Action Allow `
    -Program "$InstallPath\bridge.py" | Out-Null
Write-Host "Firewall rule created for port 8765" -ForegroundColor Green

# Create start script
Write-Host ""
Write-Host "Creating start script..." -ForegroundColor Yellow
$startScript = @"
@echo off
cd /d "$InstallPath"
echo Starting MinhOS Bridge API...
echo.
echo Bridge URL: http://%COMPUTERNAME%:8765
echo.
python bridge.py
pause
"@
$startScript | Out-File -FilePath "$InstallPath\start_bridge.bat" -Encoding ASCII
Write-Host "Start script created: start_bridge.bat" -ForegroundColor Green

# Create Windows Task for auto-start (optional)
if ($AutoStart) {
    Write-Host ""
    Write-Host "Creating Windows Task for auto-start..." -ForegroundColor Yellow
    
    $action = New-ScheduledTaskAction -Execute "python.exe" -Argument "bridge.py" -WorkingDirectory $InstallPath
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName "MinhOS Bridge API" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "MinhOS Sierra Chart Bridge API Service" `
        -RunLevel Highest | Out-Null
        
    Write-Host "Auto-start task created" -ForegroundColor Green
}

# Get system information
Write-Host ""
Write-Host "System Information:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
$computerName = $env:COMPUTERNAME
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"}

Write-Host "Computer Name: $computerName" -ForegroundColor White
Write-Host "IP Addresses:" -ForegroundColor White
foreach ($ip in $ipAddresses) {
    Write-Host "  - $($ip.IPAddress) ($($ip.InterfaceAlias))" -ForegroundColor Gray
}

# Display connection information
Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Bridge API Information:" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host "Installation Path: $InstallPath" -ForegroundColor White
Write-Host "Bridge URL: http://${computerName}:8765" -ForegroundColor White
Write-Host ""
Write-Host "To start the Bridge API:" -ForegroundColor Yellow
Write-Host "  1. Open Sierra Chart and load your charts"
Write-Host "  2. Run: $InstallPath\start_bridge.bat"
Write-Host ""
Write-Host "To configure MinhOS to use this bridge:" -ForegroundColor Yellow
Write-Host "  On your Linux machine, run:"
Write-Host "  ./scripts/switch_bridge_host.sh $computerName" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use the IP address:"
foreach ($ip in $ipAddresses | Select-Object -First 1) {
    Write-Host "  ./scripts/switch_bridge_host.sh $($ip.IPAddress)" -ForegroundColor Cyan
}

# Test Python script for Bridge API
$testScript = @"
import time
import sys
sys.path.insert(0, r'$InstallPath')

print("\nTesting Bridge API setup...")
try:
    import bridge
    print("✓ Bridge module loaded successfully")
except Exception as e:
    print(f"✗ Failed to load bridge module: {e}")
    sys.exit(1)

print("\nSetup verification complete!")
print("You can now start the Bridge API.")
"@

$testScript | Out-File -FilePath "$InstallPath\test_setup.py" -Encoding UTF8
Write-Host ""
Write-Host "Running setup verification..." -ForegroundColor Yellow
python "$InstallPath\test_setup.py"

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")