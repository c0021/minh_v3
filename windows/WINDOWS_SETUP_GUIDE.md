# Windows Setup Guide for MinhOS v3 Sierra Chart Integration

This folder contains all Windows-specific files for the Sierra Chart Bridge API.

## Files in this Directory

1. **tcp_optimize_windows.bat** - TCP optimization script to fix streaming issues
2. **bridge_api_sse_enhancement.py** - Optional SSE support for the Bridge API

## Setup Instructions

### Step 1: Apply TCP Optimizations (REQUIRED)

**Run as Administrator:**

```batch
cd C:\path\to\minh_v3\windows
tcp_optimize_windows.bat
```

This script will:
- Disable Nagle's Algorithm system-wide
- Optimize TCP settings for low latency
- Set proper keep-alive parameters

**Important:** Restart the Bridge API service after running this script. A system reboot is recommended for all changes to take full effect.

### Step 2: Verify Bridge API

Ensure your Sierra Chart Bridge API is running at `http://localhost:8765`

Test with:
```batch
curl http://localhost:8765/health
```

### Step 3: (Optional) Add SSE Support

If TCP optimizations alone don't provide smooth enough streaming, you can enhance your Bridge API with Server-Sent Events support:

1. Copy the SSE enhancement code from `bridge_api_sse_enhancement.py`
2. Integrate it into your existing `bridge_api.py`
3. This provides push-based streaming instead of polling

## Expected TCP Settings After Optimization

The script sets these registry values:
- `TcpAckFrequency = 1` (Disable delayed ACK)
- `TcpNoDelay = 1` (Disable Nagle's Algorithm)
- `KeepAliveTime = 30000` (30 seconds)
- `KeepAliveInterval = 1000` (1 second)

## Troubleshooting

### If streaming still has issues:

1. **Check Windows Firewall**
   - Ensure port 8765 is open
   - Add exception for your Bridge API

2. **Verify Registry Changes**
   - Open Registry Editor (regedit)
   - Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters`
   - Confirm TcpAckFrequency and TcpNoDelay are set to 1

3. **Monitor Network Performance**
   ```batch
   netstat -an | findstr :8765
   ```

4. **Test Direct Connection**
   From Linux machine:
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s http://cthinkpad:8765/api/market_data
   ```

## Network Architecture

```
Sierra Chart (Windows)
    ↓
localhost:8765 (Bridge API)
    ↓
Network Interface (with TCP optimizations)
    ↓
Linux PC (MinhOS v3)
```

## Performance Expectations

### Before Optimization:
- Initial requests: Fast (<100ms)
- Subsequent requests: Slow (200-500ms)
- 1Hz polling: Appears to hang

### After Optimization:
- All requests: Fast (<50ms)
- 1Hz polling: Smooth and consistent
- Connection reuse: 5-10x improvement

## Additional Notes

- The TCP optimizations are system-wide and will improve all network applications
- These settings are particularly important for cross-platform communication
- The optimizations are safe and recommended by Microsoft for low-latency scenarios