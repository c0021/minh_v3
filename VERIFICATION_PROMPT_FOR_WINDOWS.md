# ACSIL Integration Verification Prompt for Claude Code Windows

Please perform a comprehensive verification of the ACSIL tick data integration and provide a detailed status report.

## Verification Tasks

### 1. ACSIL File Output Verification
Check if ACSIL study is creating JSON files correctly:
```
- Directory: C:\SierraChart\Data\ACSILOutput
- Expected files: NQU25_CME.json, ESU25_CME.json, VIX_CGI.json
- Verify files are being updated in real-time (check timestamps)
- Read and display sample content from each file
- Confirm data includes: price, bid_size, ask_size, last_size, volume, timestamp
```

### 2. Bridge Service Status
Verify the Python bridge is running and configured correctly:
```
- Check if bridge process is running (should be python bridge.py)
- Verify bridge can access the ACSIL directory
- Check bridge logs for any ACSIL-related errors
- Confirm bridge is using correct symbol list: ["NQU25-CME", "ESU25-CME", "VIX_CGI"]
```

### 3. API Endpoint Testing
Test the bridge API responses:
```
- GET http://localhost:8765/health (should return healthy status)
- GET http://localhost:8765/api/market_data (should return real-time data)
- Verify API returns data with populated bid_size, ask_size, last_size fields
- Check if source field shows "sierra_chart_acsil"
```

### 4. Data Flow Verification
Confirm data is flowing from ACSIL → Bridge → MinhOS:
```
- Compare ACSIL file timestamps with API response timestamps
- Verify API data matches ACSIL file content
- Check for any data processing delays or errors
- Confirm all 3 symbols are being processed
```

### 5. Size Field Population Check
Critical verification - confirm NULL field resolution:
```
- Verify last_size field contains non-zero values from real trades
- Check if bid_size and ask_size are populated (may be 0 if no market depth)
- Confirm these are real values from Sierra Chart, not placeholders
```

## Required Report Format

Please provide a structured report with:

### STATUS SUMMARY
- ✅/❌ ACSIL Study Running
- ✅/❌ JSON Files Being Created  
- ✅/❌ Bridge Reading ACSIL Files
- ✅/❌ API Serving Real-time Data
- ✅/❌ Size Fields Populated

### DETAILED FINDINGS
- File locations and timestamps
- Sample JSON data from each symbol
- API response examples
- Any errors or issues found
- Bridge log excerpts (last 20 lines)

### DATA QUALITY ASSESSMENT
- Are bid_size, ask_size, last_size fields populated with real values?
- Is the timestamp precision adequate?
- Is data updating in real-time during market hours?
- Any data inconsistencies or gaps?

### RECOMMENDATIONS
- Any configuration changes needed
- Issues requiring immediate attention  
- Confirmation if NULL field issue is resolved

## Expected Outcome
The verification should confirm that:
1. ACSIL study exports real-time market data to JSON files
2. Bridge reads files via direct file system access 
3. API serves live data with populated size fields
4. The NULL bid_size, ask_size, last_size issue is resolved

Please run this verification during market hours if possible for live data testing, or use the most recent available data if markets are closed.

---
**Target**: Confirm successful integration of Sierra Chart ACSIL → Python Bridge → MinhOS data pipeline with populated market microstructure fields.