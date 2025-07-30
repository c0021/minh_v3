# MinhOS Sierra Chart Bridge - Windows Installation Guide

## 🎯 Quick Installation (5 Minutes)

**This package is completely self-contained and ready for deployment on any Windows machine.**

### Prerequisites
- Windows 10/11
- Python 3.8+ installed ([Download here](https://python.org/downloads/))
- Sierra Chart installed (for data access)

### Installation Steps

1. **Copy this entire folder** to your Windows machine
2. **Open Command Prompt** as Administrator 
3. **Navigate to the folder**:
   ```cmd
   cd path\to\bridge_installation
   ```
4. **Run the installer**:
   ```cmd
   start_bridge.bat
   ```

**That's it!** The script will automatically:
- ✅ Create Python virtual environment
- ✅ Install all dependencies 
- ✅ Handle port conflicts
- ✅ Start the bridge service

## 📁 What's Included

```
bridge_installation/
├── bridge.py                    # Main bridge application
├── file_access_api.py          # Sierra Chart data access
├── bridge_symbols.json         # Symbol configuration
├── requirements.txt            # Python dependencies
├── start_bridge.bat           # Windows installer/starter
└── start_bridge.ps1           # PowerShell alternative
```

## 🚀 After Installation

**Bridge will be running on:**
- Health Check: `http://localhost:8765/health`
- Market Data: `http://localhost:8765/api/market_data`
- WebSocket: `ws://localhost:8765/ws/live_data/{symbol}`

**Test the installation:**
```cmd
curl http://localhost:8765/health
```

## 🔧 Configuration

### Tailscale Network Access
The bridge automatically binds to all network interfaces (`0.0.0.0:8765`) for Tailscale access.

### Sierra Chart Integration
Place your Sierra Chart data files in: `C:\SierraChart\Data\`

The bridge will automatically monitor:
- `NQU25-CME.dly` (daily data)
- `NQU25-CME.scid` (real-time data)
- Other configured symbols

## 🛠️ Troubleshooting

### Port 8765 Already in Use
The installer automatically detects and kills conflicting processes. If prompted:
- Press `K` to kill existing processes
- Press `C` to continue anyway

### Python Not Found
Download and install Python from: https://python.org/downloads/
Ensure "Add Python to PATH" is checked during installation.

### Dependencies Failed to Install
Check internet connection and run:
```cmd
pip install -r requirements.txt
```

### Bridge Keeps Shutting Down
This indicates resource exhaustion. Solutions:
1. **Restart Windows** (clears file handles)
2. **Close unnecessary programs** (free memory)
3. **Check Windows Task Manager** for memory usage

## 📊 Performance Monitoring

Monitor bridge performance via:
- **Task Manager**: Check CPU/Memory usage
- **Resource Monitor**: Check file handles
- **Bridge Logs**: Check `bridge.log` for errors

## 🔄 Managing the Service

**Start Bridge:**
```cmd
start_bridge.bat
```

**Stop Bridge:**
Press `Ctrl+C` in the command window

**Restart Bridge:**
When bridge stops, choose `R` to restart

**View Logs:**
When bridge stops, choose `L` to view last 20 log lines

## 🌐 Network Configuration

**Default Binding:** `0.0.0.0:8765` (all interfaces)
**Tailscale Access:** Automatically enabled
**Firewall:** Windows may prompt to allow Python network access - click "Allow"

## 📝 Production Deployment Notes

- Bridge runs in foreground - keep command window open
- For 24/7 operation, consider running as Windows Service
- Monitor memory usage if running for extended periods
- Bridge automatically handles Sierra Chart disconnections and reconnects

## 🆘 Support

If installation fails:
1. Check `bridge.log` for detailed error messages
2. Verify Python 3.8+ is installed and in PATH
3. Ensure administrator privileges for port 8765
4. Check Windows Defender/antivirus isn't blocking Python

---

**✅ Installation Complete:** Your MinhOS Sierra Chart Bridge is ready for production use!