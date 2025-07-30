# Day 4: Market Data Service Consolidation Plan

## Current State Analysis

### Files to Consolidate:
1. **market_data.py** (609 lines) - MarketDataService class, WebSocket streaming, HTTP API
2. **market_data_migrated.py** (363 lines) - MarketDataService with unified data store
3. **sierra_client.py** (721 lines) - SierraClient class, bridge communication
4. **sierra_historical_data.py** (490 lines) - SierraHistoricalDataService, historical data access
5. **multi_chart_collector.py** (475 lines) - MultiChartCollector, multi-timeframe data

### Key Classes to Merge:
- `MarketDataService` (2 versions - original and migrated)
- `SierraClient` - Real-time data from Sierra Chart bridge
- `SierraHistoricalDataService` - Historical data access
- `MultiChartCollector` - Multi-timeframe collection

## Consolidation Strategy

### New Consolidated Structure:
```python
class MarketDataService:
    """
    Consolidated market data service including:
    - Real-time streaming from Sierra Chart bridge
    - Historical data access
    - Multi-timeframe data collection
    - WebSocket distribution
    - HTTP API endpoints
    - Unified data store management
    """
    
    def __init__(self):
        # Real-time components (from sierra_client)
        self.sierra_client = SierraClientConnector()
        
        # Historical components (from sierra_historical_data)
        self.historical_service = HistoricalDataManager()
        
        # Multi-chart components (from multi_chart_collector)
        self.multi_chart_collector = MultiTimeframeCollector()
        
        # Streaming components (from market_data)
        self.websocket_server = WebSocketStreamer()
        self.http_api = HTTPAPIHandler()
        
        # Unified data store (from market_data_migrated)
        self.market_data_adapter = get_market_data_adapter()
        
    # Real-time data methods
    async def connect_to_sierra_bridge(self)
    async def fetch_realtime_data(self)
    async def process_incoming_data(self)
    
    # Historical data methods
    async def get_historical_data(self, symbol, start_date, end_date)
    async def load_historical_files(self)
    async def search_historical_records(self)
    
    # Multi-timeframe methods
    async def collect_multi_timeframe_data(self)
    async def aggregate_timeframes(self)
    async def sync_timeframe_data(self)
    
    # Streaming methods
    async def start_websocket_server(self)
    async def broadcast_market_data(self)
    async def handle_client_subscriptions(self)
    
    # HTTP API methods
    async def start_http_server(self)
    async def handle_market_data_requests(self)
    async def serve_historical_data(self)
```

## Implementation Steps

### 1. Create New Consolidated File
Create `/minhos/services/market_data_service.py`

### 2. Merge Core Components
1. **Import and Initialize** - Combine all imports
2. **Data Models** - Merge MarketData, SierraChartRecord, MultiChartData
3. **Configuration** - Centralize all settings
4. **Connection Management** - Unified connection handling

### 3. Merge Functionality Blocks
1. **Sierra Bridge Connection** (from sierra_client.py)
2. **Historical Data Access** (from sierra_historical_data.py)  
3. **Multi-timeframe Collection** (from multi_chart_collector.py)
4. **WebSocket Streaming** (from market_data.py/market_data_migrated.py)
5. **HTTP API** (from market_data.py/market_data_migrated.py)

### 4. Update Service Registry
Update `/minhos/services/__init__.py` to:
- Export consolidated `MarketDataService`
- Remove separate sierra_client, sierra_historical exports
- Update service registry

### 5. Update Dependencies
Update files that import these services:
- Dashboard APIs
- AI Brain Service  
- Trading Engine
- State Manager

## File Size Estimation
**Total lines to consolidate**: 2,658 lines
**Expected consolidated file**: ~1,800 lines (removing duplicates)
**Reduction**: ~30% smaller due to eliminated duplication

## Key Challenges

1. **Avoiding Duplication**: Two MarketDataService classes exist
2. **Method Conflicts**: Similar method names across files
3. **Configuration Merge**: Different config approaches
4. **Dependency Updates**: Multiple files import these services

## Success Criteria

- [ ] Single `market_data_service.py` file
- [ ] All real-time data functionality preserved
- [ ] All historical data access working
- [ ] All multi-timeframe collection functional
- [ ] WebSocket streaming operational
- [ ] HTTP API endpoints working
- [ ] All dependent services updated
- [ ] No functionality lost

## Testing Checklist

- [ ] Real-time data flows from Sierra Chart
- [ ] Historical data queries work
- [ ] Multi-timeframe aggregation functions
- [ ] WebSocket clients receive data
- [ ] HTTP API responds correctly
- [ ] Dashboard displays market data
- [ ] AI Brain receives data for analysis
- [ ] Trading engine gets market feeds