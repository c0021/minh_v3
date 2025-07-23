# Market Data Migration Guide

## Overview

The MinhOS v3 market data architecture has been refactored to use a single source of truth for all market data. This eliminates data inconsistencies and reduces memory usage.

## New Architecture

### Before (Multiple Storage Locations)
```
Sierra Chart → MarketDataService → In-memory Dict
                                 ↘ WebSocket Clients
                                 
             → StateManager → In-memory Dict + SQLite (/tmp/minhos/state.db)
             
             → PatternAnalyzer → In-memory Deque
             
             → MultiChartCollector → In-memory Deque
```

### After (Single Source of Truth)
```
Sierra Chart → MarketDataService → Unified Market Data Store → SQLite (/data/market_data.db)
                                                              ↘ In-memory Cache
                                                              ↘ All Services Subscribe
```

## Key Components

### 1. Market Data Store (`minhos/core/market_data_store.py`)
- Single source of truth for all market data
- SQLite persistence in `/home/colindo/Sync/minh_v3/data/market_data.db`
- In-memory cache for recent data (configurable size)
- Automatic cleanup of old data
- Thread-safe operations
- Real-time pub/sub for updates

### 2. Market Data Adapter (`minhos/core/market_data_adapter.py`)
- Compatibility layer for existing services
- Both sync and async APIs
- Backward-compatible methods
- Easy migration path

## Migration Steps

### Step 1: Update Service Imports
```python
# Old
from typing import Dict
self.latest_data: Dict[str, MarketData] = {}

# New
from minhos.core.market_data_adapter import get_market_data_adapter
self.market_data_adapter = get_market_data_adapter()
```

### Step 2: Replace Data Storage
```python
# Old
self.latest_data[symbol] = market_data

# New
await self.market_data_adapter.async_add_data(market_data)
```

### Step 3: Replace Data Access
```python
# Old
data = self.latest_data.get(symbol)

# New
data = self.market_data_adapter.get_market_data(symbol)
```

### Step 4: Subscribe to Updates
```python
# In your service's start method
async def start(self):
    await self.market_data_adapter.start()
    await self.market_data_adapter.subscribe(self._on_market_data_update)

# Callback for updates
async def _on_market_data_update(self, data: MarketData):
    # Handle new data
    pass
```

## Services to Migrate

1. **MarketDataService** (`market_data.py`) - ✅ Example created
2. **StateManager** (`state_manager.py`) - Pending
3. **PatternAnalyzer** (`pattern_analyzer.py`) - Pending  
4. **MultiChartCollector** (`multi_chart_collector.py`) - Pending

## Benefits

1. **Single Source of Truth**: No more data inconsistencies
2. **Reduced Memory Usage**: ~75% reduction (from 4+ copies to 1)
3. **Persistent Storage**: Market data survives restarts
4. **Better Performance**: Optimized SQLite with indexes
5. **Historical Data**: Built-in support for time-range queries
6. **Real-time Updates**: Pub/sub for all services
7. **Automatic Cleanup**: Configurable retention policies

## Configuration

The market data store uses these settings:
- Database: `/home/colindo/Sync/minh_v3/data/market_data.db`
- Memory cache: 1000 records per symbol
- Retention: 30 days
- Cleanup interval: 1 hour
- WAL mode: Enabled for concurrent access

## Example Usage

See `/home/colindo/Sync/minh_v3/examples/unified_market_data_usage.py` for a complete example.

## Troubleshooting

1. **Import Errors**: Ensure the `minhos.core` package is in your Python path
2. **Database Locked**: WAL mode should prevent this, but check for stale processes
3. **Memory Usage**: Adjust `max_memory_records` if needed
4. **Performance**: Create additional indexes for specific query patterns