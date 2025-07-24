# MinhOS v3 Windows Bridge Installation Script
# Run this script on your Windows trading PC

Write-Host "MinhOS v3 Windows Bridge Setup" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = py --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    Write-Host "Download from: https://python.org/downloads" -ForegroundColor Yellow
    exit 1
}

# Create bridge directory
$bridgeDir = "C:\MinhOSBridge"
Write-Host "Creating bridge directory: $bridgeDir" -ForegroundColor Yellow

if (-not (Test-Path $bridgeDir)) {
    New-Item -ItemType Directory -Path $bridgeDir
}

# Copy files to bridge directory
Copy-Item "bridge.py" "$bridgeDir\bridge.py" -Force
Copy-Item "requirements.txt" "$bridgeDir\requirements.txt" -Force

# Change to bridge directory
Set-Location $bridgeDir

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
py -m venv venv

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\activate.ps1"
pip install -r requirements.txt

Write-Host "" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "Bridge installed at: $bridgeDir" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Green
Write-Host "To start the bridge:" -ForegroundColor Yellow
Write-Host "1. cd $bridgeDir" -ForegroundColor White
Write-Host "2. venv\Scripts\activate.ps1" -ForegroundColor White
Write-Host "3. py bridge.py" -ForegroundColor White
Write-Host "" -ForegroundColor Green
Write-Host "Or run the start script: start_bridge.ps1" -ForegroundColor Yellow

# Create start script
$startScript = @'
# MinhOS v3 Bridge Startup Script
cd C:\MinhOSBridge
venv\Scripts\activate.ps1
py bridge.py
'@

$startScript | Out-File -FilePath "start_bridge.ps1" -Encoding UTF8
Write-Host "Created start_bridge.ps1 for easy startup" -ForegroundColor Green

Write-Host "" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Ensure Sierra Chart is running" -ForegroundColor White
Write-Host "2. Start the bridge with start_bridge.ps1" -ForegroundColor White
Write-Host "3. Access via Tailscale from your Linux laptop" -ForegroundColor White
Write-Host "   - Health: http://trading-pc:8765/health" -ForegroundColor White
Write-Host "   - Market: http://trading-pc:8765/api/market_data" -ForegroundColor White