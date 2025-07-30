# MinhOS Sierra Chart Trade Execution Integration

## Complete Trading Integration: Data + Execution

This enhanced ACSIL v2 study provides **bi-directional integration** between MinhOS and Sierra Chart:

### ✅ **Data Flow**: Sierra Chart → ACSIL → Bridge → MinhOS
- Real-time market data with populated bid_size/ask_size fields
- Enhanced market depth access for accurate pricing

### ✅ **Trade Flow**: MinhOS → Bridge → ACSIL → Sierra Chart  
- Live trade execution through Sierra Chart's order management
- Real-time order status and confirmations
- Support for MARKET and LIMIT orders

## File-Based Communication Protocol

### **Command Files** (MinhOS → Sierra Chart)
**Location**: `C:\SierraChart\Data\ACSILOutput\trade_commands.json`

**Format**:
```json
{
  "order_id": "minhos_1721847234_1234",
  "symbol": "NQU25-CME", 
  "side": "BUY",
  "quantity": 1,
  "price": 23000.0,
  "type": "LIMIT"
}
```

### **Response Files** (Sierra Chart → MinhOS)
**Location**: `C:\SierraChart\Data\ACSILOutput\trade_response_[order_id].json`

**Format**:
```json
{
  "order_id": "minhos_1721847234_1234",
  "status": "PROCESSING",
  "message": "Order submitted successfully. Order ID: 12345",
  "timestamp": 1721847234,
  "source": "sierra_chart_acsil"
}
```

## Deployment Steps

### 1. **Deploy Enhanced ACSIL Study**
```bash
# Copy enhanced study to Sierra Chart
copy MinhOS_TickDataExporter_v2.cpp "C:\Sierra Chart\ACS_Source\"

# Compile in Sierra Chart
Analysis → Studies → Custom Studies → Build → Build All
```

### 2. **Configure Study Settings**
```
Study: "MinhOS Tick Data Exporter v2"
- Output Directory: C:\SierraChart\Data\ACSILOutput\
- Update Interval: 100 (milliseconds)
- Use Market Depth: Yes
- Enable Trade Execution: Yes  ← NEW SETTING
```

### 3. **Sierra Chart Trading Setup**
```
1. Trade → Trade Service Settings
2. Enable "Allow Automated Trading Systems"
3. Set "Trade Mode" to "Live" (not simulation)
4. Configure position limits and risk controls
5. Ensure broker connection is active
```

### 4. **Restart Bridge with Trading Support**
The bridge has been enhanced with:
- `send_trade_command()` - Writes command files for ACSIL
- `check_trade_responses()` - Monitors response files
- Enhanced `/api/trade/execute` endpoint

## API Usage Examples

### **Execute Trade via MinhOS**
```python
import requests

trade_request = {
    "command_id": "test_123",
    "symbol": "NQU25-CME",
    "action": "BUY", 
    "quantity": 1,
    "price": 23000.0,
    "order_type": "LIMIT"
}

response = requests.post("http://cthinkpad:8765/api/trade/execute", json=trade_request)
print(response.json())
# {"status": "SUBMITTED", "order_id": "test_123", "message": "Trade command sent to Sierra Chart ACSIL"}
```

### **Check Trade Status**
```python
status = requests.get("http://cthinkpad:8765/api/trade/status/test_123")
print(status.json())
# {"command_id": "test_123", "status": "FILLED", "message": "Order completed"}
```

## Trading Flow Sequence

1. **MinhOS Decision**: AI system decides to execute trade
2. **API Call**: POST to `/api/trade/execute` with trade parameters  
3. **Command File**: Bridge writes `trade_commands.json`
4. **ACSIL Processing**: Study reads command file (every 100ms)
5. **Sierra Chart Execution**: Order submitted to broker via Sierra Chart
6. **Response File**: ACSIL writes `trade_response_[id].json`
7. **Status Update**: Bridge monitors and updates trade status
8. **MinhOS Confirmation**: Trade result available via status API

## Safety Features

### **ACSIL Study Safety**
- Command file deleted after processing (single execution)
- Order validation before submission
- Error handling with detailed response messages
- Time-in-force set to DAY (orders expire at market close)

### **Bridge Safety**  
- Trade command logging for audit trail
- Response file cleanup to prevent accumulation
- Error handling for file access issues
- Request validation before sending to ACSIL

### **Sierra Chart Safety**
- Automated trading must be explicitly enabled
- Position limits enforced by Sierra Chart
- Broker risk controls remain active
- Real-time order status updates

## Testing Protocol

### **1. Paper Trading Test**
```
1. Set Sierra Chart to "Simulation Mode"
2. Execute test trades via MinhOS API
3. Verify command/response file creation
4. Confirm order appears in Sierra Chart Trade Activity Log
```

### **2. Live Trading Verification**
```
1. Switch Sierra Chart to "Live Mode" 
2. Start with small position sizes
3. Monitor both MinhOS logs and Sierra Chart order status
4. Verify trade confirmations match between systems
```

## Expected Performance

### **Latency**
- **Command Processing**: ~100ms (ACSIL update interval)
- **Order Submission**: Depends on broker connection
- **Response Time**: ~200ms total MinhOS → Sierra Chart

### **Reliability**
- File-based communication eliminates network issues
- Atomic file operations prevent corruption
- Automatic cleanup prevents file accumulation

## Troubleshooting

### **No Trade Execution**
1. Check "Enable Trade Execution" = Yes in study settings
2. Verify "Allow Automated Trading Systems" enabled in Sierra Chart
3. Confirm broker connection active
4. Check Sierra Chart Message Log for order rejections

### **Command Files Not Processing**
1. Verify ACSIL study is running on chart
2. Check file permissions on ACSILOutput directory
3. Monitor Sierra Chart Study Debug Output for errors

### **API Returns "REJECTED"**
1. Check bridge logs for file write errors
2. Verify trade request format matches expected JSON
3. Confirm all required fields are provided

This integration provides **production-ready trade execution** while maintaining MinhOS's core principle of **REAL TRADING ONLY** - no simulation, only authentic market execution via Sierra Chart's professional trading platform.