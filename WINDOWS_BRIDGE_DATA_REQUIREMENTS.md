# Windows Bridge Data Requirements for MinhOS v4

## Overview
This document lists ALL data fields and endpoints that MinhOS requires from the Windows Sierra Chart bridge for full functionality, including ML services, trading, and dashboard operations.

---

## 🔴 CRITICAL REQUIRED DATA FIELDS

### 1. Real-Time Market Data (Per Symbol)
**Endpoint**: `/api/data/{symbol}` or WebSocket stream  
**Required Fields**:
```json
{
  "symbol": "NQU25-CME",        // REQUIRED: Exact symbol identifier
  "last_price": 23265.25,       // REQUIRED: Current market price
  "bid": 23265.00,              // REQUIRED: Best bid price
  "ask": 23265.50,              // REQUIRED: Best ask price
  "volume": 1500,               // REQUIRED: Current volume (MUST be > 0 during market hours)
  "timestamp": "2025-08-04T11:03:45.123456", // REQUIRED: ISO format timestamp (MUST be current)
  "high": 23300.00,             // REQUIRED: Session high
  "low": 23200.00,              // REQUIRED: Session low
  "open": 23250.00              // REQUIRED: Session open
}
```

### 2. Supported Symbols List
**Endpoint**: `/api/symbols`  
**Required Response**:
```json
{
  "symbols": [
    "NQU25-CME",    // Nasdaq futures
    "ESU25-CME",    // S&P 500 futures
    "VIX_CGI"       // Volatility index
  ],
  "timestamp": "2025-08-04T11:03:45.123456"
}
```

### 3. Bridge Health Check
**Endpoint**: `/health`  
**Required Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T11:03:45.123456",
  "service": "minhos_sierra_bridge",
  "version": "3.1.0"
}
```

---

## 📊 MARKET DATA REQUIREMENTS

### WebSocket Streaming Data
**Endpoint**: `ws://MaryPC:8765/ws/{symbol}`  
**Required Message Format**:
```json
{
  "type": "market_data",
  "symbol": "NQU25-CME",
  "data": {
    "price": 23265.25,
    "bid": 23265.00,
    "ask": 23265.50,
    "volume": 1500,
    "timestamp": "2025-08-04T11:03:45.123456"
  }
}
```

### Historical Data (OHLCV)
**Endpoint**: `/api/historical/{symbol}`  
**Query Parameters**: `?start_date=2025-08-01&end_date=2025-08-04&timeframe=1min`  
**Required Response**:
```json
{
  "symbol": "NQU25-CME",
  "timeframe": "1min",
  "data": [
    {
      "timestamp": "2025-08-04T09:30:00",
      "open": 23250.00,
      "high": 23255.00,
      "low": 23248.00,
      "close": 23252.00,
      "volume": 125
    }
    // ... more candles
  ]
}
```

---

## 🤖 ML SERVICE DATA REQUIREMENTS

### 1. Feature Data for LSTM Models
**Required fields in each market data update**:
- `price` (current price)
- `volume` (MUST be > 0 for ML to activate)
- `bid_ask_spread` (calculated from bid/ask)
- `price_change` (from previous tick)
- `volume_change` (from previous tick)
- `volatility` (calculated from recent price movements)
- `momentum` (price direction indicator)
- `timestamp` (MUST be within last 5 minutes)

### 2. Ensemble Model Requirements
**Additional fields needed**:
- `rsi` (Relative Strength Index)
- `macd` (Moving Average Convergence Divergence)
- `bollinger_bands` (upper, middle, lower)
- `volume_weighted_average_price` (VWAP)
- `order_flow_imbalance` (bid volume vs ask volume)

### 3. Kelly Criterion Position Sizing
**Required fields**:
- `win_rate` (historical win percentage)
- `average_win` (average profit on winning trades)
- `average_loss` (average loss on losing trades)
- `current_capital` (account balance)
- `max_position_size` (risk limits)

---

## 📈 TRADING EXECUTION REQUIREMENTS

### Order Placement
**Endpoint**: `/api/order/place`  
**Required Request**:
```json
{
  "symbol": "NQU25-CME",
  "side": "BUY",
  "quantity": 1,
  "order_type": "MARKET",
  "price": null,  // For limit orders
  "stop_price": null  // For stop orders
}
```

### Order Status
**Endpoint**: `/api/order/status/{order_id}`  
**Required Response**:
```json
{
  "order_id": "12345",
  "status": "FILLED",
  "filled_quantity": 1,
  "average_price": 23265.25,
  "timestamp": "2025-08-04T11:03:45.123456"
}
```

### Position Information
**Endpoint**: `/api/positions`  
**Required Response**:
```json
{
  "positions": [
    {
      "symbol": "NQU25-CME",
      "quantity": 1,
      "side": "LONG",
      "entry_price": 23250.00,
      "current_price": 23265.25,
      "unrealized_pnl": 15.25,
      "realized_pnl": 0
    }
  ]
}
```

---

## 🔍 DATA QUALITY REQUIREMENTS

### Timestamp Requirements
- **Format**: ISO 8601 (`YYYY-MM-DDTHH:MM:SS.ffffff`)
- **Timezone**: UTC or with timezone offset
- **Freshness**: Must be within 5 minutes of current time during market hours
- **Consistency**: All timestamps must use the same format

### Volume Requirements
- **Non-zero during market hours**: Volume MUST be > 0 between 9:30 AM - 4:00 PM ET
- **Cumulative**: Volume should accumulate throughout the session
- **Reset**: Volume should reset at session start

### Price Data Requirements
- **Decimal precision**: At least 2 decimal places (e.g., 23265.25)
- **Bid ≤ Last ≤ Ask**: Bid must be less than or equal to ask
- **Continuous updates**: Prices should update at least every second during active trading
- **No stale data**: Prices must reflect current market, not cached values

---

## ⚠️ COMMON ISSUES TO CHECK

### 1. Stale Data Detection
MinhOS will mark data as "stale" if:
- Timestamp is > 5 minutes old
- Volume is 0 during market hours
- Prices don't change for > 60 seconds during active trading

### 2. ML Service Activation
ML models won't generate predictions if:
- Volume = 0 (models think market is closed)
- Timestamp is stale (> 5 minutes old)
- Missing required fields (null or undefined values)
- Data quality issues (e.g., bid > ask)

### 3. WebSocket Connection
Ensure WebSocket provides:
- Heartbeat/ping messages every 30 seconds
- Automatic reconnection on disconnect
- Message acknowledgment system
- Error messages for debugging

---

## 📝 VALIDATION CHECKLIST

Use this checklist to verify the Windows bridge is sending all required data:

- [ ] `/health` endpoint returns "healthy" status
- [ ] `/api/symbols` returns all 3 symbols (NQU25-CME, ESU25-CME, VIX_CGI)
- [ ] `/api/data/NQU25-CME` returns all required fields
- [ ] Timestamp in data is current (within last 5 minutes)
- [ ] Volume > 0 during market hours (9:30 AM - 4:00 PM ET)
- [ ] WebSocket connections established for all symbols
- [ ] WebSocket messages arriving at least once per second
- [ ] Bid ≤ Last Price ≤ Ask
- [ ] High ≥ Current Price ≥ Low
- [ ] Historical data endpoint returns OHLCV candles
- [ ] Order placement endpoint accepts orders
- [ ] Position information endpoint returns current positions

---

## 🔗 TEST COMMANDS

Run these commands from MinhOS to test bridge connectivity:

```bash
# Test health
curl -s "http://MaryPC:8765/health"

# Test symbols
curl -s "http://MaryPC:8765/api/symbols"

# Test market data
curl -s "http://MaryPC:8765/api/data/NQU25-CME"

# Test WebSocket (requires wscat or similar)
wscat -c "ws://MaryPC:8765/ws/NQU25-CME"
```

---

## 📞 SUPPORT

If any of these data requirements are not being met, the Windows bridge needs to be updated to provide the missing fields. The most critical requirements for ML functionality are:

1. **Current timestamps** (within 5 minutes)
2. **Non-zero volume** during market hours
3. **All price fields** (bid, ask, last, high, low, open)
4. **WebSocket streaming** for real-time updates

Without these, MinhOS ML services will show as "inactive" or generate 0 predictions.