# MinhOS v3 Sierra Chart Streaming Fix Implementation Guide

## Problem Summary

Your 1Hz polling from Linux to Windows Sierra Chart Bridge API appears to hang due to TCP Nagle's Algorithm interacting with Delayed ACK, creating cumulative 200-500ms delays.

## Solution Components

### 1. Optimized Sierra Client (PRIMARY SOLUTION)

Located at: `src/services/sierra_client_optimized.py`

**Key Features:**
- Disables Nagle's Algorithm via TCP_NODELAY socket option
- Implements connection pooling for TCP connection reuse
- Includes retry logic with exponential backoff
- Maintains persistent HTTP sessions
- Provides detailed performance logging

**Integration with existing code:**

```python
# In your main application
from src.services.sierra_client_optimized import OptimizedSierraClient

# Replace your current polling implementation
client = OptimizedSierraClient(
    bridge_url="http://marypc:8765",
    db_connection=your_db_instance
)

# Start streaming (blocks - run in thread if needed)
client.stream_market_data()
```

### 2. System TCP Optimizations

**Windows (Sierra Chart PC):**
1. Run as Administrator: `scripts\tcp_optimize_windows.bat`
2. Restart the Bridge API service
3. Reboot Windows for full effect

**Linux (MinhOS PC):**
1. Run: `sudo ./scripts/tcp_optimize_linux.sh`
2. Changes apply immediately (no reboot needed)

### 3. Verify the Fix

Run the diagnostic script:
```bash
python scripts/diagnose_streaming.py
```

**Expected Results:**
- Single request: <100ms
- With connection pooling: <50ms average
- 1Hz streaming: Stable with <100ms per request
- Performance improvement: 5-10x with pooling

### 4. Alternative: Server-Sent Events (Optional)

If TCP optimizations aren't sufficient, use SSE implementation:
- Client: `src/services/sierra_client_sse.py`
- Requires adding SSE endpoint to your Windows Bridge API
- Provides push-based updates instead of polling

## Integration Steps

### Step 1: Apply TCP Optimizations

**On Windows PC (marypc):**
```batch
cd C:\path\to\minh_v3\scripts
tcp_optimize_windows.bat
```

**On Linux PC:**
```bash
cd /home/colindo/Sync/minh_v3
sudo ./scripts/tcp_optimize_linux.sh
```

### Step 2: Update Your Service

Replace your current Sierra Client implementation:

```python
# OLD (problematic)
while True:
    response = requests.get("http://marypc:8765/api/market_data")
    process_data(response.json())
    time.sleep(1)

# NEW (optimized)
from src.services.sierra_client_optimized import OptimizedSierraClient

client = OptimizedSierraClient(db_connection=db)
client.stream_market_data()  # Handles everything internally
```

### Step 3: Update Your Service Manager

If using systemd:

```ini
[Unit]
Description=MinhOS Sierra Client Service
After=network.target

[Service]
Type=simple
User=minh
WorkingDirectory=/home/colindo/Sync/minh_v3
ExecStart=/usr/bin/python3 /home/colindo/Sync/minh_v3/src/services/sierra_client_optimized.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 4: Monitor Performance

Check logs for performance metrics:
```bash
journalctl -u minh-sierra-client -f
```

Expected log output:
```
2025-01-23 10:00:00 - OptimizedSierraClient - INFO - Starting optimized market data streaming...
2025-01-23 10:00:01 - OptimizedSierraClient - INFO - Market data: MES @ $5012.25 (bid: $5012.00, ask: $5012.50)
2025-01-23 10:01:00 - OptimizedSierraClient - INFO - Performance: 60 requests, 1.00 req/s, uptime: 60s
```

## Troubleshooting

### Issue: Still seeing high latency

1. Verify TCP settings applied:
   ```bash
   python scripts/diagnose_streaming.py
   ```

2. Check firewall isn't interfering:
   ```bash
   # Temporarily disable firewall for testing
   sudo ufw disable  # Linux
   netsh advfirewall set allprofiles state off  # Windows (Admin)
   ```

3. Ensure Bridge API isn't the bottleneck:
   - Check Windows Task Manager for high CPU
   - Monitor Sierra Chart performance

### Issue: Connection drops frequently

1. Increase keep-alive settings in OptimizedSierraClient
2. Check network stability: `ping -t cthinkpad`
3. Consider using SSE implementation for more reliable streaming

### Issue: Database not updating

1. Verify `db_connection` is passed correctly
2. Check database write permissions
3. Monitor logs for processing errors

## Performance Expectations

**Before Fix:**
- Initial requests work fine
- Subsequent requests hang/delay
- Dashboard shows "WAITING"
- Only 1 database record despite polling

**After Fix:**
- Consistent <100ms response times
- Stable 1Hz data flow
- Dashboard updates in real-time
- Database receives updates every second

## Next Steps

1. Apply the fix following the steps above
2. Run diagnostic to verify improvement
3. Monitor for 24 hours to ensure stability
4. Consider SSE implementation for even better performance

## Support

If issues persist after implementing this fix:
1. Collect diagnostic output
2. Check Sierra Chart Bridge API logs
3. Verify network path between machines
4. Consider professional TCP tuning consultation

The root cause (Nagle's Algorithm + Delayed ACK) is well-understood and this solution directly addresses it. You should see immediate improvement.