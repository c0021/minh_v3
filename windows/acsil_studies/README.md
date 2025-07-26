# MinhOS ACSIL Tick Data Exporter

This ACSIL study exports real-time market data with bid/ask sizes from Sierra Chart to JSON files for MinhOS consumption.

## Features

- ✅ Real-time tick data export (OHLC, Volume)
- ✅ Market depth data (bid/ask prices and sizes)  
- ✅ Last trade size from time & sales
- ✅ VWAP calculation
- ✅ JSON format for easy Python consumption
- ✅ Atomic file writes to prevent corruption
- ✅ Rate-limited updates (configurable interval)

## Installation

### 1. Development Environment Setup

On the Windows machine running Sierra Chart:

```bash
# Install Visual Studio 2019 or 2022 with C++ support
# Ensure "MSVC v143 - VS 2022 C++ x64/x86 build tools" is installed
# Add "Windows 10/11 SDK" component
```

### 2. Copy Files to Sierra Chart

```bash
# Copy source files to Sierra Chart ACS_Source directory
copy MinhOS_TickDataExporter.cpp "C:\Sierra Chart\ACS_Source\"
copy MinhOS_TickDataExporter.h "C:\Sierra Chart\ACS_Source\"
```

### 3. Compilation

In Sierra Chart:
1. Open **Analysis** → **Studies** → **Custom Studies**
2. Click **Build** → **Build All**
3. Look for "MinhOS Tick Data Exporter" in the build output
4. Check for compilation errors in the build log

### 4. Add Study to Chart

1. Right-click on a chart → **Studies** → **Add Custom Study**
2. Select **"MinhOS Tick Data Exporter"**
3. Configure settings:
   - **Output Directory**: `C:\SierraChart\Data\ACSILOutput\`
   - **Update Interval**: `100` (milliseconds)
   - **Export All Charts**: `Yes`
4. Click **OK**

### 5. Verify Output

Check for JSON files in: `C:\SierraChart\Data\ACSILOutput\`

Expected files:
- `NQU25_CME.json`
- `EURUSD.json`  
- `XAUUSD.json`
- etc.

## JSON Output Format

```json
{
  "symbol": "NQU25-CME",
  "timestamp": 1721836800,
  "price": 18125.50,
  "open": 18120.00,
  "high": 18130.25,
  "low": 18118.75,
  "volume": 1250,
  "bid": 18125.25,
  "ask": 18125.75,
  "bid_size": 15,
  "ask_size": 22,
  "last_size": 5,
  "vwap": 18124.83,
  "trades": 1,
  "source": "sierra_chart_acsil"
}
```

## Python Bridge Integration

The MinhOS Python bridge automatically reads these JSON files and serves the data via:
- REST API: `GET http://cthinkpad:8765/api/market_data`
- WebSocket: `ws://cthinkpad:8765/ws/market_data`

Files are checked every 100ms and must be less than 10 seconds old to be considered valid.

## Troubleshooting

### Study Not Building
- Verify Visual Studio C++ tools are installed
- Check Sierra Chart ACS_Source directory permissions
- Look for compilation errors in Sierra Chart build log

### No JSON Files Created
- Verify output directory exists and is writable
- Check Sierra Chart chart has the study applied
- Ensure market data is flowing (market hours)

### Python Bridge Not Reading Data
- Verify JSON file format matches expected structure
- Check file timestamps (must be recent)
- Look for parsing errors in bridge logs

### Missing Size Data
- Ensure Sierra Chart has market depth enabled
- Check data provider supports Level II data
- Verify Time & Sales data is available

## Performance Notes

- Default 100ms update interval balances latency with CPU usage
- JSON files are written atomically to prevent corruption
- File age checking prevents stale data consumption
- Study handles multiple symbols efficiently

## Next Steps

1. **Deploy to Windows machine** running Sierra Chart
2. **Compile and test** with live market data
3. **Monitor JSON output** during market hours
4. **Verify Python bridge integration** receives size data
5. **Confirm NULL field resolution** in MinhOS database

This implementation provides the missing market microstructure data (bid_size, ask_size, last_size) that was causing NULL values in the MinhOS database.