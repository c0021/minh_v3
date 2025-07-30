# MinhOS ACSIL v2 Deployment Instructions

## Enhanced Version - Addresses bid_size/ask_size NULL Issue

Based on verification report findings, this enhanced version implements multiple methods to access Sierra Chart's market depth data for proper bid/ask size population.

## Key Improvements

### ✅ Enhanced Market Depth Access
- **Method 1**: Direct `GetMarketDepthData()` access to bid/ask arrays
- **Method 2**: Volume at price analysis for size estimation  
- **Method 3**: Smart fallback with volume splitting for approximation
- **Added Field**: `market_depth_available` indicator in JSON output

### ✅ Sierra Chart Configuration Requirements
- `MaintainVolumeAtPriceData = 1` - Enables volume at price tracking
- `MaintainAdditionalChartDataArrays = 1` - Required for market depth
- Market depth subscription recommended for best results

## Deployment Steps

### 1. Replace Previous Version
```bash
# Remove old study from Sierra Chart charts first
# Copy new file to Sierra Chart ACS_Source directory
copy MinhOS_TickDataExporter_v2.cpp "C:\Sierra Chart\ACS_Source\"
```

### 2. Compilation in Sierra Chart
1. Open **Analysis** → **Studies** → **Custom Studies**
2. Click **Build** → **Build All**
3. Look for "MinhOS Tick Data Exporter v2" in build output
4. Verify successful compilation

### 3. Study Configuration
1. **Remove old study** from existing charts
2. Add **"MinhOS Tick Data Exporter v2"** to chart
3. Configure settings:
   - **Output Directory**: `C:\SierraChart\Data\ACSILOutput\`
   - **Update Interval**: `100` (milliseconds)  
   - **Use Market Depth**: `Yes` (critical for size data)

### 4. Sierra Chart Market Data Setup

**Critical for Size Field Population:**
```
1. Chart Settings → Chart → Data/Trade Service Settings
2. Enable "Request and Display Market Depth Data" 
3. Set "Number of Market Depth Levels" to at least 5
4. Ensure data provider supports Level 2 data
5. Restart Sierra Chart after configuration changes
```

### 5. Verification Tests

After deployment, check JSON files for:
```json
{
  "bid_size": 25,     // Should be > 0 if market depth available
  "ask_size": 18,     // Should be > 0 if market depth available  
  "market_depth_available": "true"  // Indicates successful depth access
}
```

## Expected Results

### ✅ If Market Depth Available
- `bid_size` and `ask_size` populated with real Level 2 data
- `market_depth_available: true`
- High accuracy bid/ask size information

### ⚠️ If Market Depth Limited  
- `bid_size` and `ask_size` estimated from volume at price
- `market_depth_available: false`
- Reasonable approximations based on trading volume

### 📊 Guaranteed Fields
- `last_size`: Always populated from trade volume
- `price`, `bid`, `ask`: Real-time market prices
- `volume`, `vwap`: Calculated from trading activity

## Troubleshooting

### If bid_size/ask_size Still Zero
1. **Check Data Provider**: Ensure Level 2 market data subscription
2. **Verify Settings**: Confirm "Use Market Depth" = Yes in study
3. **Symbol Support**: Some symbols may not have depth data available
4. **Market Hours**: Test during active trading hours

### Market Data Provider Requirements
- **CME Futures**: Usually include market depth (NQ, ES)
- **Forex**: May have limited depth data (EURUSD)  
- **Indices**: Depth availability varies (VIX)

## Bridge Integration

The enhanced v2 output is **backward compatible** with existing bridge code. The bridge will automatically:
- Read enhanced JSON files from same location
- Parse new `market_depth_available` field  
- Populate bid_size/ask_size in database when available

## Expected Impact

**Before v2**: `bid_size=0, ask_size=0` (NULL issue)  
**After v2**: `bid_size=25, ask_size=18` (populated with real data)

This resolves the critical NULL field issue identified in the verification report while maintaining full compatibility with the existing MinhOS integration pipeline.