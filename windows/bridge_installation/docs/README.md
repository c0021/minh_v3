# MinhOS Sierra Chart Bridge v3.1.0

Enhanced Windows bridge providing real-time market data streaming and historical data access for MinhOS trading system.

## 🎯 Features

### Real-Time Trading
- **Market Data Streaming**: Live price feeds from Sierra Chart
- **Trade Execution**: Order placement and management
- **WebSocket API**: Real-time data broadcasting
- **Position Management**: Current position tracking

### Historical Data Access
- **Sierra Chart Integration**: Direct access to .dly (CSV) and .scid (binary) files
- **Secure File API**: Path validation and read-only access
- **Multiple Formats**: Support for daily, tick, and depth data
- **Gap Detection**: Automatic historical data backfilling

### Security & Reliability
- **Tailscale Networking**: Private network access only
- **Path Validation**: Restricted to Sierra Chart data directories
- **Error Handling**: Comprehensive logging and recovery
- **Health Monitoring**: Status endpoints and diagnostics

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11** with administrative access
- **Python 3.8+** installed with PATH configured
- **Sierra Chart** installed and running
- **Tailscale** for network connectivity

### Installation

1. **Start Bridge Service** (Recommended - Batch Script)
   ```cmd
   start_bridge.bat
   ```

2. **Advanced Startup** (PowerShell with more options)
   ```powershell
   .\start_bridge.ps1
   ```

3. **Install Dependencies Only**
   ```powershell
   .\start_bridge.ps1 -Install
   ```

## 📁 File Structure

```
bridge_installation/
├── bridge.py              # Main bridge application
├── file_access_api.py      # Historical data access API
├── requirements.txt        # Python dependencies
├── start_bridge.bat       # Windows batch startup script
├── start_bridge.ps1       # PowerShell startup script (advanced)
├── README.md              # This documentation
├── bridge.log             # Runtime log file (created on startup)
└── venv/                  # Python virtual environment (created on first run)
```

## 🌐 API Endpoints

### Health & Status
- **GET** `/health` - Health check
- **GET** `/status` - Detailed service status

### Market Data
- **GET** `/api/market_data` - Latest market data for all symbols
- **GET** `/api/market_data?symbol=NQ` - Data for specific symbol
- **WebSocket** `/ws/market_data` - Real-time data stream

### Trading
- **POST** `/api/trade/execute` - Execute trade order
- **GET** `/api/trade/status/{command_id}` - Get trade status
- **GET** `/api/positions` - Current positions

### Historical Data (File Access)
- **GET** `/api/file/list?path=C:\SierraChart\Data` - List files in directory
- **GET** `/api/file/read?path=C:\SierraChart\Data\NQ.dly` - Read text file (CSV)
- **GET** `/api/file/read_binary?path=C:\SierraChart\Data\NQ.scid` - Read binary file
- **GET** `/api/file/info?path=C:\SierraChart\Data\NQ.dly` - Get file metadata

## 🔧 Configuration

### Sierra Chart Settings
The bridge expects Sierra Chart to be installed at one of these locations:
- `C:\SierraChart\Data`
- `C:\Sierra Chart\Data`
- `D:\SierraChart\Data`
- `D:\Sierra Chart\Data`

### Network Configuration
- **Bridge Port**: 8765 (configurable in bridge.py)
- **Sierra Chart DTC Port**: 11099 (default)
- **Network**: Tailscale private network only

### Supported File Types
- **Daily Data**: `.dly` files (CSV format)
- **Tick Data**: `.scid` files (binary format)
- **Market Depth**: `.depth` files
- **Text Files**: `.txt`, `.csv` files

## 🛠️ Advanced Usage

### PowerShell Options
```powershell
# Install dependencies and setup environment
.\start_bridge.ps1 -Install

# Run with debug logging
.\start_bridge.ps1 -Debug

# Install as Windows service (requires admin)
.\start_bridge.ps1 -Service

# Show help and available options
.\start_bridge.ps1 -Help
```

### Environment Variables
- `PYTHONUNBUFFERED=1` - Real-time log output
- `PYTHONDONTWRITEBYTECODE=1` - Prevent .pyc files
- `LOG_LEVEL=DEBUG` - Enable debug logging

## 🐛 Troubleshooting

### Common Issues

1. **"Python not found"**
   - Install Python 3.8+ from https://python.org/downloads/
   - Ensure "Add Python to PATH" is checked during installation

2. **"Failed to install dependencies"**
   - Check internet connection
   - Try: `pip install -r requirements.txt` manually

3. **"Connection failed"**
   - Verify Sierra Chart is running
   - Check Tailscale connectivity: `tailscale status`
   - Test port availability: `netstat -an | findstr :8765`

4. **"File access denied"**
   - Verify Sierra Chart data directory exists
   - Check file permissions
   - Ensure bridge has read access to data files

### Diagnostic Commands
```cmd
# Check Python installation
python --version

# Test Tailscale connectivity
ping your-linux-machine

# Check if port is in use
netstat -an | findstr :8765

# View bridge logs
type bridge.log
```

## 📊 Monitoring

### Health Check
```bash
# From Linux MinhOS system
curl http://trading-pc:8765/health
```

### Status Information
```bash
# Detailed status including file API
curl http://trading-pc:8765/status
```

### Log Files
- **bridge.log** - Main application log
- **Console Output** - Real-time status information

## 🔐 Security

### Network Security
- **Tailscale Only**: No public internet exposure
- **Private Network**: Access restricted to Tailscale mesh
- **No Authentication**: Relying on network-level security

### File System Security
- **Read-Only Access**: No write or delete operations
- **Path Validation**: Restricted to Sierra Chart directories only
- **Extension Filtering**: Only allowed file types accessible
- **Input Sanitization**: All paths validated and normalized

## 🚀 Integration with MinhOS

### Linux Configuration
Update your MinhOS configuration:
```python
# In /home/colindo/Sync/minh_v3/minhos/core/config.py
SIERRA_HOST = "trading-pc"  # Your Windows machine Tailscale name
```

### Historical Data Service
The bridge integrates with MinhOS historical data service:
```python
# Access historical data from Linux
historical_service = get_sierra_historical_service()
data = await historical_service.get_historical_data("NQ", start_date, end_date)
```

## 📞 Support

### Log Analysis
1. Check `bridge.log` for detailed error information
2. Run with `-Debug` flag for verbose output
3. Monitor Windows Event Viewer for system-level issues

### Performance Tuning
- Adjust `update_interval` in bridge.py for data frequency
- Monitor memory usage with Task Manager
- Consider Windows service installation for automatic startup

---

## 🎉 Ready for Production

This bridge is designed for production deployment with:
- ✅ Comprehensive error handling and recovery
- ✅ Security-focused file access controls
- ✅ Production-ready logging and monitoring
- ✅ Integration with existing MinhOS architecture
- ✅ Support for both batch and PowerShell startup methods

The bridge transforms MinhOS from real-time-only to a comprehensive historical analysis platform with access to years of Sierra Chart tick data for enhanced AI decision making.