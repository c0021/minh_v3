# MinhOS Bridge Windows Service Setup Guide

## 🚀 Quick Installation

**Run as Administrator:**
```cmd
cd C:\Users\colin\Sync\minh_v4\windows\bridge_installation
install_service.bat
```

## 📋 What This Sets Up

### ✅ Windows Service Features
- **Service Name**: MinhOSBridge
- **Auto-Start**: Starts automatically when Windows boots
- **Auto-Restart**: Automatically restarts if the bridge crashes
- **Request Limit**: Removed (no more 100-request shutdowns)
- **Logging**: All activity logged to `logs\bridge_service.log`

### ✅ Service Management Scripts
- **`install_service.bat`** - Install the Windows Service (run as Administrator)
- **`uninstall_service.bat`** - Remove the Windows Service
- **`service_status.bat`** - Check status and manage the service
- **`bridge_service.py`** - Service wrapper that handles auto-restarts

## 📖 Installation Steps

### 1. Prerequisites
- Windows 10/11
- Python 3.8+ installed
- MinhOS Bridge files in the current directory
- Administrator privileges

### 2. Install Service
```cmd
# Open Command Prompt as Administrator
cd C:\Users\colin\Sync\minh_v4\windows\bridge_installation
install_service.bat
```

The installer will:
- ✅ Check for existing virtual environment
- ✅ Create the Windows Service with auto-restart policies
- ✅ Configure the service to start automatically
- ✅ Offer to start the service immediately

### 3. Verify Installation
```cmd
# Check service status
service_status.bat

# Or use Windows commands
sc query MinhOSBridge
```

## 🔧 Service Management

### Start/Stop/Restart Service
```cmd
# Start
sc start MinhOSBridge

# Stop  
sc stop MinhOSBridge

# Restart
sc stop MinhOSBridge && sc start MinhOSBridge
```

### Check Service Status
```cmd
# Quick status
sc query MinhOSBridge

# Detailed management interface
service_status.bat
```

### View Service Logs
```cmd
# View recent logs
type logs\bridge_service.log

# View last 20 lines
powershell "Get-Content logs\bridge_service.log -Tail 20"
```

## 🛠️ Advanced Configuration

### Service Properties
- **Startup Type**: Automatic
- **Log On As**: Local System
- **Recovery Actions**: 
  - First failure: Restart service after 5 seconds
  - Second failure: Restart service after 10 seconds  
  - Subsequent failures: Restart service after 30 seconds

### Auto-Restart Logic
The service wrapper (`bridge_service.py`) provides additional restart intelligence:
- **Rate Limiting**: Max 10 restarts per hour
- **Graceful Shutdown**: Handles Ctrl+C and service stop requests
- **Error Recovery**: Different wait times for normal vs error shutdowns
- **Comprehensive Logging**: All bridge output captured in service log

## 🔍 Troubleshooting

### Service Won't Install
- **Cause**: Not running as Administrator
- **Solution**: Right-click Command Prompt → "Run as administrator"

### Service Won't Start
- **Check**: Virtual environment exists at `venv\Scripts\python.exe`
- **Check**: Bridge script exists at `bridge.py`  
- **Check**: Windows Event Log (Application) for service errors

### Bridge Still Stops After 17 Minutes
- **Cause**: Request limit was not fully removed
- **Solution**: The limit has been removed from `bridge.py`. Restart the service.

### High CPU Usage
- **Cause**: Rapid restart loops
- **Check**: Service logs for error patterns
- **Solution**: Service wrapper limits restarts to prevent loops

### Log File Growing Too Large
- **Location**: `logs\bridge_service.log`
- **Management**: Log rotation can be added if needed
- **Temporary**: Delete the log file (service will recreate it)

## 📊 Monitoring

### Windows Services Manager
1. Press `Win+R` → type `services.msc`
2. Find "MinhOS Sierra Chart Bridge"
3. Right-click for Start/Stop/Restart options

### Task Manager
1. Open Task Manager → Services tab
2. Find "MinhOSBridge" service
3. Right-click for management options

### Command Line Monitoring
```cmd
# Continuous status monitoring
for /l %i in () do (sc query MinhOSBridge && timeout 10)

# Real-time log viewing
powershell "Get-Content logs\bridge_service.log -Wait"
```

## 🔄 Uninstallation

To completely remove the service:
```cmd
# Run as Administrator
uninstall_service.bat
```

This will:
- Stop the running service
- Remove the service from Windows
- Keep log files (delete manually if desired)

## 🎯 Production Benefits

### Reliability
- **24/7 Operation**: Starts with Windows, runs continuously
- **Fault Tolerance**: Automatic restart on crashes or request limits  
- **Resource Management**: Prevents runaway restart loops

### Monitoring
- **Complete Logging**: All bridge activity captured
- **Service Integration**: Visible in Windows Service Manager
- **Event Log Integration**: Service start/stop events in Windows Event Log

### Maintenance
- **Zero Touch**: No manual intervention required
- **Remote Management**: Can be managed via Remote Desktop or PowerShell
- **Update Friendly**: Service can be stopped, files updated, service restarted

---

## ✅ Installation Complete

Your MinhOS Bridge is now installed as a Windows Service and will:
- Start automatically when Windows boots
- Restart automatically if it crashes or hits limits
- Log all activity for monitoring and debugging
- Provide 24/7 market data access to your MinhOS trading system

The bridge will be available at: **http://localhost:8765**