# Phase 1: Architecture Consolidation Plan (Days 1-9)

## 🎯 Goal: Transform 15+ tangled services into 4 clean services + 2 interfaces

---

## 📅 Day 1-2: Configuration Centralization

### Day 1: Create config_manager.py
**File**: `/core/config_manager.py`

#### Tasks:
1. **Audit Configuration Sources** (2 hours)
   - [ ] Find all ports across codebase
   - [ ] Find all IPs/hostnames  
   - [ ] Find all timeouts/intervals
   - [ ] Find all trading parameters
   - [ ] Document in `config_audit.md`

2. **Create Centralized Config** (3 hours)
   ```python
   # Structure:
   CONFIG = {
       "network": {
           "bridge_host": "172.21.128.1",
           "bridge_port": 8765,
           "dashboard_port": 8888,
           "api_port": 8000,
           # ... all network config
       },
       "trading": {
           "autonomous_threshold": 0.75,
           "max_position_size": 5,
           # ... all trading params
       },
       "timing": {
           "service_status_update": 10000,
           "ai_transparency_update": 2000,
           # ... all intervals
       }
   }
   ```

3. **Create Config Access Methods** (1 hour)
   - `get_config(path)` - dot notation access
   - `update_config(path, value)` - runtime updates
   - `load_from_env()` - environment overrides

### Day 2: Migrate Services to config_manager
**Goal**: Remove ALL hardcoded values

#### Migration Order:
1. [ ] `sierra_client.py` - Remove hardcoded IPs/ports
2. [ ] `web_api.py` - Use config for endpoints
3. [ ] `dashboard/main.py` - Config for UI settings
4. [ ] `ai_brain_service.py` - Config for thresholds
5. [ ] All other services

#### Validation:
- [ ] No hardcoded ports remain (grep for `:8765`, `:8000`, etc)
- [ ] No hardcoded IPs remain (grep for IP patterns)
- [ ] All services start successfully
- [ ] Configuration changes work without restarts

---

## 📅 Day 3-5: Service Consolidation

### Day 3: Create ai_brain_service.py (Consolidated)
**Merge these into ONE file**:
- Current `ai_brain_service.py`
- `pattern_analyzer.py` 
- AI-related logic from dashboard
- Decision quality integration

**Structure**:
```python
class AIBrainService:
    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.pattern_detector = PatternDetector()
        self.signal_generator = SignalGenerator()
        self.decision_tracker = DecisionTracker()
    
    # All AI methods in one place
    async def analyze_market(self, data): ...
    async def detect_patterns(self, data): ...
    async def generate_signals(self, analysis): ...
    async def track_decision(self, decision): ...
```

### Day 4: Create market_data_service.py (Consolidated)
**Merge these into ONE file**:
- `market_data.py`
- `market_data_adapter.py`
- `market_data_store.py`
- `sierra_client.py` (data fetching parts)
- `sierra_historical_data.py`
- `multi_chart_collector.py`

**Structure**:
```python
class MarketDataService:
    def __init__(self):
        self.sierra_client = SierraClient()
        self.data_store = DataStore()
        self.historical = HistoricalData()
        
    # All market data methods
    async def get_realtime_data(self): ...
    async def get_historical_data(self): ...
    async def subscribe_symbol(self): ...
```

### Day 5: Create trading_service.py + risk_service.py
**trading_service.py** merges:
- `trading_engine.py`
- `live_trading_integration.py`
- Trading logic from other files

**risk_service.py** merges:
- `risk_manager.py`
- Risk validation from scattered files
- Position sizing logic

---

## 📅 Day 6-7: API Consolidation

### Day 6: Create api_server.py
**Merge ALL endpoints from**:
- `web_api.py` 
- `dashboard/api.py`
- `dashboard/api_trading.py`
- `dashboard/api_enhanced.py`
- WebSocket endpoints

**Single FastAPI app**:
```python
app = FastAPI()

# Market Data Endpoints
@app.get("/api/market/latest")
@app.get("/api/market/historical")
@app.websocket("/ws/market")

# Trading Endpoints  
@app.post("/api/trading/execute")
@app.get("/api/trading/positions")

# AI Endpoints
@app.get("/api/ai/analysis")
@app.get("/api/ai/signals")

# ... all 50+ endpoints in ONE file
```

### Day 7: Create dashboard_server.py
**Consolidate dashboard logic**:
- Merge scattered dashboard Python files
- Single entry point for UI
- Clean separation from API

---

## 📅 Day 8-9: Validation & Migration

### Day 8: Integration Testing
- [ ] Run full test suite
- [ ] Verify all endpoints work
- [ ] Check dashboard functionality
- [ ] Test real-time data flow
- [ ] Verify trading capabilities

### Day 9: Final Migration
- [ ] Create migration scripts
- [ ] Document breaking changes
- [ ] Update deployment configs
- [ ] Final validation
- [ ] Go live with new architecture

---

## 📊 Success Metrics

### Quantitative:
- File count: 60+ → 8 files
- Code duplication: -80%
- Configuration sources: 60+ → 1
- API endpoints: Scattered → 1 file

### Qualitative:
- [ ] Any developer can find any feature in <30 seconds
- [ ] Configuration changes don't require code changes
- [ ] Services have clear, single responsibilities
- [ ] No tangled dependencies

---

## 🚨 Risk Mitigation

1. **Parallel Development**: Keep old code running while building new
2. **Feature Flags**: Toggle between old/new implementations
3. **Incremental Testing**: Test each service as consolidated
4. **Rollback Plan**: Git branches for instant reversion

---

## 📝 Daily Checklist Template

Copy this for each day:

```markdown
## Day X Progress (Date: YYYY-MM-DD)

### Completed:
- [ ] Task 1
- [ ] Task 2

### Blockers:
- None / Description

### Tomorrow:
- Plan for next day

### Notes:
- Important observations
```