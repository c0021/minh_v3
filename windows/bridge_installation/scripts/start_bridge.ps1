# MinhOS Sierra Chart Bridge Startup Script (PowerShell)
# Enhanced bridge with historical data access
# 
# This PowerShell script provides advanced startup capabilities with better
# error handling, logging, and system integration for Windows environments.

param(
    [switch]$Install,
    [switch]$Service,
    [switch]$Debug,
    [switch]$Help
)

# Script information
$BridgeVersion = "3.1.0"
$ScriptName = "MinhOS Sierra Chart Bridge"

# Colors for output
$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
}

function Write-Header {
    param([string]$Message)
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host $Message -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Colors.Success
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Colors.Error
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info
}

function Show-Help {
    Write-Header "$ScriptName v$BridgeVersion - Help"
    
    Write-Host "USAGE:" -ForegroundColor $Colors.Header
    Write-Host "  .\start_bridge.ps1 [OPTIONS]" -ForegroundColor $Colors.Info
    Write-Host ""
    
    Write-Host "OPTIONS:" -ForegroundColor $Colors.Header
    Write-Host "  -Install    Install Python dependencies and setup environment" -ForegroundColor $Colors.Info
    Write-Host "  -Service    Install as Windows service (requires admin)" -ForegroundColor $Colors.Info
    Write-Host "  -Debug      Run with debug logging enabled" -ForegroundColor $Colors.Info
    Write-Host "  -Help       Show this help message" -ForegroundColor $Colors.Info
    Write-Host ""
    
    Write-Host "EXAMPLES:" -ForegroundColor $Colors.Header
    Write-Host "  .\start_bridge.ps1                  # Start bridge normally" -ForegroundColor $Colors.Info
    Write-Host "  .\start_bridge.ps1 -Install         # Install dependencies first" -ForegroundColor $Colors.Info
    Write-Host "  .\start_bridge.ps1 -Debug           # Start with debug logging" -ForegroundColor $Colors.Info
    Write-Host "  .\start_bridge.ps1 -Service         # Install as Windows service" -ForegroundColor $Colors.Info
    Write-Host ""
    
    Write-Host "ENDPOINTS:" -ForegroundColor $Colors.Header
    Write-Host "  Health Check:   http://localhost:8765/health" -ForegroundColor $Colors.Info
    Write-Host "  Status:         http://localhost:8765/status" -ForegroundColor $Colors.Info
    Write-Host "  Market Data:    http://localhost:8765/api/market_data" -ForegroundColor $Colors.Info
    Write-Host "  File Access:    http://localhost:8765/api/file/list" -ForegroundColor $Colors.Info
    Write-Host "  WebSocket:      ws://localhost:8765/ws/market_data" -ForegroundColor $Colors.Info
    
    exit 0
}

function Test-PythonInstallation {
    Write-Info "Checking Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
            return $true
        }
    }
    catch {
        # Python not found
    }
    
    Write-Error "Python is not installed or not in PATH"
    Write-Warning "Please install Python 3.8+ from https://python.org/downloads/"
    Write-Warning "Ensure 'Add Python to PATH' is checked during installation"
    return $false
}

function Test-RequiredFiles {
    Write-Info "Checking required files..."
    
    $requiredFiles = @("bridge.py", "file_access_api.py", "requirements.txt")
    $allFilesExist = $true
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "Found: $file"
        } else {
            Write-Error "Missing: $file"
            $allFilesExist = $false
        }
    }
    
    return $allFilesExist
}

function Setup-VirtualEnvironment {
    Write-Info "Setting up Python virtual environment..."
    
    if (-not (Test-Path "venv")) {
        Write-Info "Creating virtual environment..."
        python -m venv venv
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            return $false
        }
        
        Write-Success "Virtual environment created"
    } else {
        Write-Success "Virtual environment already exists"
    }
    
    return $true
}

function Install-Dependencies {
    Write-Info "Installing Python dependencies..."
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to activate virtual environment"
        return $false
    }
    
    # Check if dependencies are already installed
    $fastApiInstalled = pip show fastapi 2>$null
    
    if (-not $fastApiInstalled -or $Install) {
        Write-Info "Installing/updating dependencies from requirements.txt..."
        
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install dependencies"
            Write-Warning "Please check your internet connection and try again"
            return $false
        }
        
        Write-Success "Dependencies installed successfully"
    } else {
        Write-Success "Dependencies already installed"
    }
    
    return $true
}

function Start-BridgeService {
    param([bool]$DebugMode = $false)
    
    Write-Header "Starting $ScriptName v$BridgeVersion"
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:PYTHONUNBUFFERED = "1"
    $env:PYTHONDONTWRITEBYTECODE = "1"
    
    if ($DebugMode) {
        $env:LOG_LEVEL = "DEBUG"
        Write-Info "Debug logging enabled"
    }
    
    # Show service information
    Write-Info "Bridge Directory: $(Get-Location)"
    Write-Info "Date/Time: $(Get-Date)"
    Write-Info "Virtual Environment: $env:VIRTUAL_ENV"
    Write-Host ""
    
    Write-Info "Available Endpoints:"
    Write-Host "  Health Check:   http://localhost:8765/health" -ForegroundColor $Colors.Success
    Write-Host "  Status:         http://localhost:8765/status" -ForegroundColor $Colors.Success
    Write-Host "  Market Data:    http://localhost:8765/api/market_data" -ForegroundColor $Colors.Success
    Write-Host "  File Access:    http://localhost:8765/api/file/list" -ForegroundColor $Colors.Success
    Write-Host "  WebSocket:      ws://localhost:8765/ws/market_data" -ForegroundColor $Colors.Success
    Write-Host ""
    
    Write-Info "Press Ctrl+C to stop the bridge service"
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host ""
    
    # Start the bridge
    try {
        python bridge.py
        $exitCode = $LASTEXITCODE
        
        Write-Host ""
        Write-Header "Bridge Service Stopped"
        
        if ($exitCode -eq 0) {
            Write-Success "Bridge stopped normally"
        } else {
            Write-Error "Bridge stopped with error code: $exitCode"
            Show-TroubleshootingInfo
        }
        
    } catch {
        Write-Error "Failed to start bridge: $($_.Exception.Message)"
        Show-TroubleshootingInfo
    }
}

function Show-TroubleshootingInfo {
    Write-Host ""
    Write-Warning "Troubleshooting Tips:"
    Write-Host "  • Check if Sierra Chart is running" -ForegroundColor $Colors.Info
    Write-Host "  • Verify Tailscale connectivity" -ForegroundColor $Colors.Info
    Write-Host "  • Ensure port 8765 is not in use: netstat -an | findstr :8765" -ForegroundColor $Colors.Info
    Write-Host "  • Check bridge.log for detailed error information" -ForegroundColor $Colors.Info
    Write-Host "  • Restart bridge with -Debug flag for more information" -ForegroundColor $Colors.Info
    
    if (Test-Path "bridge.log") {
        Write-Host ""
        Write-Info "Last 10 lines of bridge.log:"
        Write-Host "-" * 40 -ForegroundColor $Colors.Info
        Get-Content "bridge.log" -Tail 10 | ForEach-Object {
            Write-Host $_ -ForegroundColor $Colors.Info
        }
        Write-Host "-" * 40 -ForegroundColor $Colors.Info
    }
}

function Install-WindowsService {
    Write-Header "Installing $ScriptName as Windows Service"
    
    # Check if running as administrator
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Error "Installing as Windows service requires administrator privileges"
        Write-Warning "Please run PowerShell as Administrator and try again"
        return
    }
    
    Write-Info "Windows service installation would require additional tools like NSSM"
    Write-Info "For now, you can add the bridge to Windows startup folder:"
    Write-Host ""
    Write-Host "Startup folder location:" -ForegroundColor $Colors.Info
    Write-Host "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" -ForegroundColor $Colors.Success
    Write-Host ""
    Write-Info "Create a shortcut to start_bridge.bat in the startup folder"
}

# Main execution
if ($Help) {
    Show-Help
}

# Change to script directory
Set-Location $PSScriptRoot

Write-Header "$ScriptName v$BridgeVersion"
Write-Info "Enhanced with Historical Data Access"
Write-Host ""

# Validate environment
if (-not (Test-PythonInstallation)) {
    exit 1
}

if (-not (Test-RequiredFiles)) {
    Write-Error "Required files are missing. Please ensure all bridge files are present."
    exit 1
}

# Setup virtual environment
if (-not (Setup-VirtualEnvironment)) {
    exit 1
}

# Install dependencies
if (-not (Install-Dependencies)) {
    exit 1
}

# Handle special modes
if ($Service) {
    Install-WindowsService
    exit 0
}

# Start the bridge service
try {
    while ($true) {
        Start-BridgeService -DebugMode $Debug
        
        Write-Host ""
        Write-Host "Options:" -ForegroundColor $Colors.Header
        Write-Host "  R - Restart bridge service" -ForegroundColor $Colors.Info
        Write-Host "  L - View bridge log" -ForegroundColor $Colors.Info
        Write-Host "  Q - Quit" -ForegroundColor $Colors.Info
        Write-Host ""
        
        $choice = Read-Host "Enter your choice (R/L/Q)"
        
        switch ($choice.ToUpper()) {
            "R" { 
                Write-Info "Restarting bridge service..."
                continue 
            }
            "L" { 
                if (Test-Path "bridge.log") {
                    Write-Header "Bridge Log File (Last 30 lines)"
                    Get-Content "bridge.log" -Tail 30 | ForEach-Object {
                        Write-Host $_ -ForegroundColor $Colors.Info
                    }
                    Write-Host ""
                    Read-Host "Press Enter to continue"
                } else {
                    Write-Warning "Log file not found"
                }
            }
            "Q" { 
                Write-Success "Thank you for using $ScriptName!"
                exit 0 
            }
            default { 
                Write-Warning "Invalid choice. Please enter R, L, or Q."
            }
        }
    }
} catch {
    Write-Error "Script error: $($_.Exception.Message)"
    exit 1
}