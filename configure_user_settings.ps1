# User-Level Development Configuration
# Run this script as regular user (no admin required)

Write-Host "=== User-Level Development Configuration ===" -ForegroundColor Green
Write-Host "Configuring user-specific settings for optimal development..." -ForegroundColor Yellow
Write-Host ""

# 1. Confirm PowerShell Execution Policy
Write-Host "1. Checking PowerShell Execution Policy..." -ForegroundColor Cyan
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "Current policy: $currentPolicy" -ForegroundColor Yellow

if ($currentPolicy -ne "Unrestricted") {
    try {
        Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser -Force
        Write-Host "✓ PowerShell execution policy set to Unrestricted" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to set execution policy: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "✓ PowerShell execution policy already Unrestricted" -ForegroundColor Green
}

# 2. Configure Git (if installed) for development
Write-Host "`n2. Configuring Git settings..." -ForegroundColor Cyan
try {
    $gitPath = Get-Command git -ErrorAction SilentlyContinue
    if ($gitPath) {
        # Configure Git for better Windows/WSL compatibility
        git config --global core.autocrlf false
        git config --global core.filemode false
        git config --global core.longpaths true
        Write-Host "✓ Git configured for Windows development" -ForegroundColor Green
    } else {
        Write-Host "! Git not found - skipping Git configuration" -ForegroundColor Yellow
    }
} catch {
    Write-Host "! Git configuration skipped: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3. Create development environment variables
Write-Host "`n3. Setting development environment variables..." -ForegroundColor Cyan
try {
    [Environment]::SetEnvironmentVariable("NODE_ENV", "development", "User")
    [Environment]::SetEnvironmentVariable("PYTHONUNBUFFERED", "1", "User")
    [Environment]::SetEnvironmentVariable("FORCE_COLOR", "1", "User")
    Write-Host "✓ Development environment variables set" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to set environment variables: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Configure npm for optimal performance
Write-Host "`n4. Optimizing npm configuration..." -ForegroundColor Cyan
try {
    npm config set fund false
    npm config set audit false
    npm config set progress false
    npm config set loglevel warn
    Write-Host "✓ npm optimized for development" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to configure npm: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Create useful development aliases
Write-Host "`n5. Creating PowerShell development aliases..." -ForegroundColor Cyan
try {
    $profilePath = $PROFILE.CurrentUserAllHosts
    $aliasContent = @"

# Development Aliases
Set-Alias -Name ll -Value Get-ChildItem
Set-Alias -Name grep -Value Select-String
function cddev { Set-Location "C:\Users\colin\Sync\minh_v4" }
function bridge { Set-Location "C:\Users\colin\Sync\minh_v4\windows\bridge_installation" }
function logs { Get-Content -Tail 50 -Wait }

# Quick development commands
function dev-status {
    Write-Host "=== Development Environment Status ===" -ForegroundColor Green
    Write-Host "Node.js: " -NoNewline; node --version
    Write-Host "npm: " -NoNewline; npm --version
    Write-Host "Claude CLI: " -NoNewline; claude --version
    Write-Host "PowerShell Policy: " -NoNewline; Get-ExecutionPolicy
    Write-Host "Current Directory: " -NoNewline; Get-Location
}

function bridge-status {
    Write-Host "=== Bridge Status ===" -ForegroundColor Green
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8765/health" -TimeoutSec 5
        Write-Host "Bridge Health: " -NoNewline -ForegroundColor Green
        Write-Host "✓ Running" -ForegroundColor Green
    } catch {
        Write-Host "Bridge Health: " -NoNewline -ForegroundColor Red
        Write-Host "✗ Not responding" -ForegroundColor Red
    }
}

"@

    if (!(Test-Path (Split-Path $profilePath))) {
        New-Item -ItemType Directory -Path (Split-Path $profilePath) -Force | Out-Null
    }
    
    Add-Content -Path $profilePath -Value $aliasContent
    Write-Host "✓ PowerShell development aliases added to profile" -ForegroundColor Green
    Write-Host "  Use 'cddev' to go to project directory" -ForegroundColor Gray
    Write-Host "  Use 'bridge' to go to bridge directory" -ForegroundColor Gray
    Write-Host "  Use 'dev-status' to check development environment" -ForegroundColor Gray
    Write-Host "  Use 'bridge-status' to check bridge health" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed to create PowerShell aliases: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Test Claude CLI access
Write-Host "`n6. Testing Claude CLI access..." -ForegroundColor Cyan
try {
    $claudeVersion = claude --version
    Write-Host "✓ Claude CLI working: $claudeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Claude CLI test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== User Configuration Complete ===" -ForegroundColor Green
Write-Host "Your development environment is now optimized!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run the admin script: configure_unrestricted_access.ps1 (as Administrator)"
Write-Host "2. Restart your computer for all changes to take effect"
Write-Host "3. Restart PowerShell to load new aliases and settings"
Write-Host ""
Write-Host "Press any key to continue..."
pause
