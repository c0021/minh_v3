# Windows 10 Unrestricted Development Access Configuration
# Run this script as Administrator

Write-Host "=== Windows 10 Unrestricted Development Access Setup ===" -ForegroundColor Green
Write-Host "This script will configure your system for unrestricted development access." -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green

# 1. Disable UAC (User Account Control)
Write-Host "`n1. Disabling UAC (User Account Control)..." -ForegroundColor Cyan
try {
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 0
    Write-Host "✓ UAC disabled (requires restart to take effect)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to disable UAC: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Add Windows Defender Exclusions
Write-Host "`n2. Adding Windows Defender exclusions..." -ForegroundColor Cyan
$exclusions = @(
    "C:\Users\colin\Sync\minh_v4",
    "C:\Users\colin\AppData\Roaming\npm",
    "C:\Program Files\nodejs",
    "C:\Users\colin\AppData\Local\npm-cache"
)

foreach ($path in $exclusions) {
    try {
        Add-MpPreference -ExclusionPath $path -ErrorAction Stop
        Write-Host "✓ Added exclusion: $path" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to add exclusion $path : $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 3. Disable SmartScreen
Write-Host "`n3. Disabling SmartScreen..." -ForegroundColor Cyan
try {
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" -Name "SmartScreenEnabled" -Value "Off"
    Write-Host "✓ SmartScreen disabled" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to disable SmartScreen: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Configure Windows Firewall exceptions
Write-Host "`n4. Adding Windows Firewall exceptions..." -ForegroundColor Cyan
$firewallRules = @(
    @{Name="Node.js"; Program="C:\Program Files\nodejs\node.exe"},
    @{Name="Python"; Program="C:\Python*\python.exe"},
    @{Name="Bridge Application"; Program="C:\Users\colin\Sync\minh_v4\windows\bridge_installation\bridge.py"}
)

foreach ($rule in $firewallRules) {
    try {
        New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Program $rule.Program -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName $rule.Name -Direction Outbound -Program $rule.Program -Action Allow -ErrorAction SilentlyContinue
        Write-Host "✓ Added firewall rule: $($rule.Name)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to add firewall rule $($rule.Name): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 5. Set network profile to Private
Write-Host "`n5. Setting network profile to Private..." -ForegroundColor Cyan
try {
    Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private
    Write-Host "✓ Network profile set to Private" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to set network profile: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 6. Disable Windows Update automatic restart
Write-Host "`n6. Configuring Windows Update settings..." -ForegroundColor Cyan
try {
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" -Name "UxOption" -Value 1
    Write-Host "✓ Windows Update configured for manual restart" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to configure Windows Update: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 7. Enable Developer Mode (requires registry change)
Write-Host "`n7. Enabling Developer Mode..." -ForegroundColor Cyan
try {
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -Value 1
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowAllTrustedApps" -Value 1
    Write-Host "✓ Developer Mode enabled" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to enable Developer Mode: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=== Configuration Complete ===" -ForegroundColor Green
Write-Host "IMPORTANT: You must RESTART your computer for all changes to take effect!" -ForegroundColor Red
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Yellow
Write-Host "• UAC disabled (no more admin prompts)" 
Write-Host "• Windows Defender exclusions added for dev folders"
Write-Host "• SmartScreen disabled"
Write-Host "• Firewall exceptions added for Node.js, Python, Bridge"
Write-Host "• Network set to Private (enables local discovery)"
Write-Host "• Windows Update configured for manual restart"
Write-Host "• Developer Mode enabled"
Write-Host ""
Write-Host "Press any key to continue..."
pause
