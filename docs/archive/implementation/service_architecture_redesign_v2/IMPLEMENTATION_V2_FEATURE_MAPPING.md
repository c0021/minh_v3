# MinhOS v3 Implementation v2 - Complete Feature Migration Mapping

## 🎯 EXECUTIVE SUMMARY

This document provides the **exact mapping** of every current MinhOS feature to its new location in Implementation v2. Every line of functionality is accounted for to ensure **zero feature loss**.

---

## 📍 CURRENT STATE → NEW LOCATION MAPPING

### **SERVICE-BY-SERVICE MIGRATION MAP**

#### **1. SERVICE ORCHESTRATOR**
**Current Location**: `/minhos/services/orchestrator.py`
**New Location**: `/core/services/service_orchestrator.py`

**Features Being Moved:**
- `start_all_services()` → `/core/services/lifecycle_manager.py::start_services()`
- `monitor_health()` → `/core/services/health_monitor.py::monitor_all_services()`
- `handle_service_failure()` → `/core/services/health_monitor.py::handle_failure()`
- Service startup order logic → `/core/services/dependency_resolver.py::resolve_startup_order()`

**Dependencies Moving To:**
- Service registry → `/core/services/service_registry.py`
- Health monitoring → `/core/services/health_monitor.py`

---

#### **2. AI BRAIN SERVICE**
**Current Location**: `/minhos/services/ai_brain_service.py`
**New Location**: `/services/ai_brain/ai_brain_service.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
analyze_market_data()                    → /services/ai_brain/analysis/technical_analyzer.py::analyze()
generate_trading_signal()               → /services/ai_brain/signals/signal_generator.py::generate()
calculate_confidence()                   → /services/ai_brain/signals/confidence_scorer.py::calculate()
historical_context_loading()            → /services/ai_brain/analysis/pattern_recognizer.py::load_context()
real_time_reasoning_display()           → /services/ai_brain/transparency/reasoning_explainer.py::explain()
multi_timeframe_analysis()              → /services/ai_brain/analysis/technical_analyzer.py::multi_timeframe()
decision_quality_context_generation()   → /services/ai_brain/transparency/decision_logger.py::log_context()
```

**API Endpoints Moving To:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/ai/current-analysis                 → /interfaces/rest/endpoints/ai_endpoints.py::get_current_analysis()
/api/ai/reasoning-breakdown              → /interfaces/rest/endpoints/ai_endpoints.py::get_reasoning_breakdown()
/api/ai/risk-assessment                  → /interfaces/rest/endpoints/ai_endpoints.py::get_risk_assessment()
/api/ai/signals                          → /interfaces/rest/endpoints/ai_endpoints.py::get_signals()
/api/ai/market-analysis                  → /interfaces/rest/endpoints/ai_endpoints.py::get_market_analysis()
/api/ai/execution-history                → /interfaces/rest/endpoints/ai_endpoints.py::get_execution_history()
/api/ai/pattern-analysis                 → /interfaces/rest/endpoints/ai_endpoints.py::get_pattern_analysis()
```

**Dashboard Features Moving To:**
```
CURRENT DASHBOARD SECTION                → NEW COMPONENT
AI Transparency Dashboard (Blue)         → /dashboard/templates/components/ai_transparency.html
Current AI Analysis Widget               → /dashboard/static/js/components/ai_transparency.js::updateCurrentAnalysis()
Technical Indicators Display             → /dashboard/static/js/components/ai_transparency.js::updateTechnicalIndicators()
Technical Analysis Breakdown             → /dashboard/static/js/components/ai_transparency.js::updateBreakdown()
Risk Assessment Display                  → /dashboard/static/js/components/ai_transparency.js::updateRiskAssessment()
Real-time reasoning updates              → /dashboard/static/js/components/ai_transparency.js::updateReasoning()
```

---

#### **3. STATE MANAGER**
**Current Location**: `/minhos/services/state_manager.py`
**New Location**: `/services/system_state/state_service.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
get_position()                           → /services/system_state/tracking/position_tracker.py::get_current_position()
update_pnl()                            → /services/system_state/tracking/pnl_calculator.py::update()
save_system_config()                     → /core/config/config_manager.py::save_config()
get_risk_parameters()                    → /core/config/config_manager.py::get_risk_config()
SQLite database management               → /data/database/connections/sqlite_manager.py
Unified market data store integration    → /data/database/repositories/market_data_repo.py
Persistent state across restarts         → /services/system_state/persistence/state_persister.py
```

**Database Files Moving To:**
```
CURRENT DATABASE                         → NEW LOCATION
/data/state.db                          → /data/database/sqlite/state.db (managed by sqlite_manager.py)
/data/decision_quality.db               → /data/database/sqlite/decision_quality.db
/data/market_data.db                    → /data/database/sqlite/market_data.db
/data/risk.db                           → /data/database/sqlite/risk.db
```

---

#### **4. RISK MANAGER**
**Current Location**: `/minhos/services/risk_manager.py`
**New Location**: `/services/risk/risk_service.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
validate_trade_request()                → /services/risk/validation/pre_trade_validator.py::validate()
check_circuit_breakers()                → /services/risk/limits/circuit_breaker.py::check_breakers()
monitor_positions()                      → /services/risk/monitoring/real_time_monitor.py::monitor()
calculate_position_size()               → /services/risk/sizing/kelly_calculator.py::calculate_size()
Multiple validation layers               → /services/risk/validation/ (multiple validators)
Drawdown protection                      → /services/risk/limits/drawdown_protector.py
Portfolio impact assessment             → /services/risk/validation/exposure_validator.py::assess_impact()
```

**API Endpoints Moving To:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/risk/status                        → /interfaces/rest/endpoints/risk_endpoints.py::get_status()
/api/risk/parameters                    → /interfaces/rest/endpoints/risk_endpoints.py::update_parameters()
```

---

#### **5. SIERRA CLIENT**
**Current Location**: `/minhos/services/sierra_client.py`
**New Location**: `/services/market_data/providers/sierra_provider.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
connect_to_bridge()                      → /services/market_data/providers/sierra_provider.py::connect()
stream_market_data()                     → /services/market_data/streaming/stream_manager.py::start_stream()
execute_trade()                          → /services/trading/execution/order_manager.py::execute_via_sierra()
get_health_status()                      → /services/market_data/providers/sierra_provider.py::get_health()
TCP optimizations (TCP_NODELAY)          → /services/market_data/streaming/tcp_optimizer.py
Automatic reconnection logic             → /services/market_data/streaming/reconnection_handler.py
Bridge health monitoring                 → /services/market_data/providers/sierra_provider.py::monitor_bridge()
Multi-symbol data streaming              → /services/market_data/streaming/stream_manager.py::handle_multi_symbol()
```

**Hardcoded Values Being Centralized:**
```
CURRENT HARDCODED VALUE                  → NEW CONFIGURATION LOCATION
host = "cthinkpad"                      → /configuration/master/production.yaml::network.sierra_bridge.host
port = 8765                             → /configuration/master/production.yaml::network.sierra_bridge.port
timeout = 5000                          → /configuration/master/production.yaml::network.sierra_bridge.timeout
symbol = "NQU25"                        → Retrieved from /core/symbols/symbol_manager.py::get_current_symbol()
```

---

#### **6. TRADING ENGINE**
**Current Location**: `/minhos/services/trading_engine.py`
**New Location**: `/services/trading/trading_service.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
process_ai_signal()                      → /services/trading/execution/execution_engine.py::process_signal()
detect_market_regime()                   → /services/trading/analysis/market_regime_detector.py::detect()
autonomous_execution()                   → /services/trading/modes/full_auto_mode.py::execute_autonomous()
calculate_execution_timing()             → /services/trading/execution/execution_engine.py::calculate_timing()
Autonomous AI execution (75%+ threshold) → /services/trading/modes/full_auto_mode.py::CONFIDENCE_THRESHOLD
Market regime detection                  → /services/trading/analysis/market_regime_detector.py
Decision quality integration             → /services/trading/quality/decision_integrator.py
Execution discipline measurement         → /services/trading/quality/execution_evaluator.py
```

**API Endpoints Moving To:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/trading/mode                       → /interfaces/rest/endpoints/trading_endpoints.py::set_mode()
/api/trading/emergency-stop             → /interfaces/rest/endpoints/trading_endpoints.py::emergency_stop()
/api/trading/positions                  → /interfaces/rest/endpoints/trading_endpoints.py::get_positions()
/api/trading/orders                     → /interfaces/rest/endpoints/trading_endpoints.py::get_orders()
/api/trading/history                    → /interfaces/rest/endpoints/trading_endpoints.py::get_history()
/api/trading/performance                → /interfaces/rest/endpoints/trading_endpoints.py::get_performance()
/api/trading/config                     → /interfaces/rest/endpoints/trading_endpoints.py::get_config()
```

**Dashboard Features Moving To:**
```
CURRENT DASHBOARD FEATURE                → NEW COMPONENT
Trading Control Panel                   → /dashboard/templates/components/trading_control.html
Trading mode buttons                    → /dashboard/static/js/components/trading_control.js::setTradingMode()
Emergency stop button                   → /dashboard/static/js/components/trading_control.js::emergencyStop()
Trading Configuration Panel             → /dashboard/templates/components/trading_config.html
Autonomous trading toggle                → /dashboard/static/js/components/trading_control.js::updateTradingConfig()
```

---

#### **7. DECISION QUALITY FRAMEWORK**
**Current Location**: `/minhos/core/decision_quality.py`
**New Location**: `/services/decision_quality/decision_quality_service.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
evaluate_decision() (6 categories)      → /services/decision_quality/evaluation/category_evaluator.py::evaluate()
get_quality_summary()                   → /services/decision_quality/reporting/dashboard_reporter.py::get_summary()
export_quality_history()               → /services/decision_quality/reporting/export_manager.py::export()
Information Analysis category           → /services/decision_quality/evaluation/information_analyzer.py
Risk Assessment category                → /services/decision_quality/evaluation/risk_assessor.py
Execution Discipline category           → /services/decision_quality/evaluation/execution_evaluator.py
Pattern Recognition category            → /services/decision_quality/evaluation/pattern_scorer.py
Market Context category                 → /services/decision_quality/evaluation/context_evaluator.py
Timing Quality category                 → /services/decision_quality/evaluation/timing_assessor.py
SQLite persistence                      → /data/database/repositories/decision_repo.py
Process improvement recommendations     → /services/decision_quality/improvement/recommendation_engine.py
Quality trend tracking                  → /services/decision_quality/tracking/trend_analyzer.py
```

**API Endpoints Moving To:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/decision-quality/current           → /interfaces/rest/endpoints/quality_endpoints.py::get_current()
/api/decision-quality/detailed/{id}     → /interfaces/rest/endpoints/quality_endpoints.py::get_detailed()
/api/decision-quality/summary           → /interfaces/rest/endpoints/quality_endpoints.py::get_summary()
```

**Dashboard Features Moving To:**
```
CURRENT DASHBOARD SECTION                → NEW COMPONENT
Decision Quality Dashboard (Orange)     → /dashboard/templates/components/decision_quality.html
Overall Quality Score display           → /dashboard/static/js/components/decision_quality.js::updateOverallScore()
6-category evaluation display           → /dashboard/static/js/components/decision_quality.js::updateCategories()
Recent Decision Scores list             → /dashboard/static/js/components/decision_quality.js::updateRecentDecisions()
Process Improvement Recommendations     → /dashboard/static/js/components/decision_quality.js::updateRecommendations()
Quality Category bars and scoring       → /dashboard/static/js/components/decision_quality.js::updateCategoryScore()
```

---

#### **8. SIERRA HISTORICAL DATA**
**Current Location**: `/minhos/services/sierra_historical_data.py`
**New Location**: `/services/market_data/providers/historical_provider.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
read_scid_files()                       → /services/market_data/providers/historical_provider.py::read_scid()
read_dly_files()                        → /services/market_data/providers/historical_provider.py::read_dly()
detect_gaps()                           → /services/market_data/processors/gap_detector.py::detect()
backfill_data()                         → /services/market_data/processors/gap_detector.py::backfill()
20x more historical data access         → /services/market_data/providers/historical_provider.py::get_extended_history()
Multiple data format support            → /services/market_data/processors/format_converter.py
Sierra Chart data directory access      → /services/market_data/providers/historical_provider.py::access_sierra_data()
```

---

#### **9. MULTI-CHART COLLECTOR**
**Current Location**: `/minhos/services/multi_chart_collector.py`
**New Location**: `/services/market_data/collectors/multi_asset_collector.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
_collect_all_data()                     → /services/market_data/collectors/multi_asset_collector.py::collect_all()
_perform_analysis()                     → /services/market_data/analysis/cross_asset_analyzer.py::analyze()
_determine_market_regime()              → /services/market_data/analysis/market_regime_detector.py::determine()
Multi-symbol data collection            → /services/market_data/collectors/multi_asset_collector.py::collect_symbols()
Cross-asset correlation analysis        → /services/market_data/analysis/cross_asset_analyzer.py::calculate_correlations()
Real-time broadcasting to subscribers   → /services/market_data/streaming/broadcast_manager.py::broadcast()
```

**Configured Assets Preserved:**
```
CURRENT ASSETS                           → NEW CONFIGURATION
NQ (1min, 30min, daily)                → /configuration/master/production.yaml::symbols.active_contracts[NQ]
ES (1min)                               → /configuration/master/production.yaml::symbols.active_contracts[ES]
VIX (1min)                              → /configuration/master/production.yaml::symbols.active_contracts[VIX]
```

---

#### **10. WEB API SERVICE**
**Current Location**: `/minhos/services/web_api.py`
**New Location**: `/interfaces/rest/api_server.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
_handle_market_data()                   → /interfaces/rest/endpoints/market_endpoints.py::handle_market_data()
_handle_health()                        → /interfaces/rest/endpoints/system_endpoints.py::handle_health()
_handle_debug_*()                       → /interfaces/rest/endpoints/system_endpoints.py::handle_debug_*()
CORS support                            → /interfaces/rest/middleware/cors_middleware.py
Rate limiting (100 req/min)             → /interfaces/rest/middleware/rate_limiter.py
Comprehensive debug endpoints           → /interfaces/rest/endpoints/system_endpoints.py::debug_*()
Real-time system statistics             → /interfaces/rest/endpoints/system_endpoints.py::get_stats()
```

**All API Endpoints Moving To:**
```
CURRENT ENDPOINT                         → NEW HANDLER FILE
/health                                 → /interfaces/rest/endpoints/system_endpoints.py
/api/health                             → /interfaces/rest/endpoints/system_endpoints.py
/api/status                             → /interfaces/rest/endpoints/system_endpoints.py
/api/market_data                        → /interfaces/rest/endpoints/market_endpoints.py
/api/market/latest                      → /interfaces/rest/endpoints/market_endpoints.py
/api/latest-data                        → /interfaces/rest/endpoints/market_endpoints.py
/api/symbols                            → /interfaces/rest/endpoints/market_endpoints.py
/market_data                            → /interfaces/rest/endpoints/market_endpoints.py
/api/services                           → /interfaces/rest/endpoints/system_endpoints.py
/api/stats                              → /interfaces/rest/endpoints/system_endpoints.py
/api/performance                        → /interfaces/rest/endpoints/system_endpoints.py
/api/debug/data-age                     → /interfaces/rest/endpoints/system_endpoints.py
/api/debug/last-update                  → /interfaces/rest/endpoints/system_endpoints.py
/api/debug/file-stats                   → /interfaces/rest/endpoints/system_endpoints.py
/api/debug/connections                  → /interfaces/rest/endpoints/system_endpoints.py
/api/config                             → /interfaces/rest/endpoints/config_endpoints.py
```

---

#### **11. DASHBOARD API SERVICE**
**Current Location**: `/minhos/dashboard/api.py`
**New Location**: `/interfaces/rest/endpoints/` (split by category)

**Features Being Moved:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/status                             → /interfaces/rest/endpoints/system_endpoints.py::get_system_status()
/api/trading/mode                       → /interfaces/rest/endpoints/trading_endpoints.py::set_trading_mode()
/api/trading/emergency-stop             → /interfaces/rest/endpoints/trading_endpoints.py::emergency_stop()
/api/health                             → /interfaces/rest/endpoints/system_endpoints.py::get_health()
/api/market/data/{symbol}               → /interfaces/rest/endpoints/market_endpoints.py::get_market_data()
/api/market/symbols                     → /interfaces/rest/endpoints/market_endpoints.py::get_symbols()
/api/ai/current-analysis                → /interfaces/rest/endpoints/ai_endpoints.py::get_current_analysis()
/api/ai/reasoning-breakdown             → /interfaces/rest/endpoints/ai_endpoints.py::get_reasoning_breakdown()
/api/ai/execution-history               → /interfaces/rest/endpoints/ai_endpoints.py::get_execution_history()
/api/ai/pattern-analysis                → /interfaces/rest/endpoints/ai_endpoints.py::get_pattern_analysis()
/api/ai/risk-assessment                 → /interfaces/rest/endpoints/ai_endpoints.py::get_risk_assessment()
/api/ai/signals                         → /interfaces/rest/endpoints/ai_endpoints.py::get_signals()
/api/ai/market-analysis                 → /interfaces/rest/endpoints/ai_endpoints.py::get_market_analysis()
/api/decision-quality/current           → /interfaces/rest/endpoints/quality_endpoints.py::get_current_quality()
/api/decision-quality/detailed/{id}     → /interfaces/rest/endpoints/quality_endpoints.py::get_detailed_quality()
/api/decision-quality/summary           → /interfaces/rest/endpoints/quality_endpoints.py::get_quality_summary()
/api/trading/positions                  → /interfaces/rest/endpoints/trading_endpoints.py::get_positions()
/api/trading/position                   → /interfaces/rest/endpoints/trading_endpoints.py::manage_position()
/api/trading/orders                     → /interfaces/rest/endpoints/trading_endpoints.py::get_orders()
/api/patterns/detected                  → /interfaces/rest/endpoints/pattern_endpoints.py::get_detected_patterns()
/api/risk/status                        → /interfaces/rest/endpoints/risk_endpoints.py::get_risk_status()
/api/risk/parameters                    → /interfaces/rest/endpoints/risk_endpoints.py::update_risk_parameters()
/api/config/{section}                   → /interfaces/rest/endpoints/config_endpoints.py::get_config_section()
/api/config/update                      → /interfaces/rest/endpoints/config_endpoints.py::update_config()
/api/sierra/status                      → /interfaces/rest/endpoints/sierra_endpoints.py::get_sierra_status()
/api/sierra/command                     → /interfaces/rest/endpoints/sierra_endpoints.py::send_sierra_command()
/api/chat/status                        → /interfaces/rest/endpoints/chat_endpoints.py::get_chat_status()
/api/chat/conversation/{client_id}      → /interfaces/rest/endpoints/chat_endpoints.py::get_conversation()
/api/chat/test                          → /interfaces/rest/endpoints/chat_endpoints.py::test_chat()
/api/symbols/rollover-status            → /interfaces/rest/endpoints/symbol_endpoints.py::get_rollover_status()
```

---

#### **12. DASHBOARD TRADING API**
**Current Location**: `/minhos/dashboard/api_trading.py`
**New Location**: `/interfaces/rest/endpoints/trading_endpoints.py`

**Features Being Moved:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/trading/config                     → /interfaces/rest/endpoints/trading_endpoints.py::get_trading_config()
/api/trading/config                     → /interfaces/rest/endpoints/trading_endpoints.py::update_trading_config()
/api/trading/history                    → /interfaces/rest/endpoints/trading_endpoints.py::get_trade_history()
/api/trading/performance                → /interfaces/rest/endpoints/trading_endpoints.py::get_performance()
/api/trading/positions                  → /interfaces/rest/endpoints/trading_endpoints.py::get_positions()
/api/trading/emergency-stop             → /interfaces/rest/endpoints/trading_endpoints.py::emergency_stop()
```

---

#### **13. WEBSOCKET CHAT**
**Current Location**: `/minhos/dashboard/websocket_chat.py`
**New Location**: `/interfaces/websockets/chat_ws.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
WebSocket /ws/chat                      → /interfaces/websockets/chat_ws.py::chat_websocket()
WebSocket /ws/chat/{client_id}          → /interfaces/websockets/chat_ws.py::chat_websocket_with_id()
chat_message processing                 → /interfaces/websockets/chat_ws.py::handle_chat_message()
ping/pong handling                      → /interfaces/websockets/chat_ws.py::handle_ping()
get_history message type                → /interfaces/websockets/chat_ws.py::handle_get_history()
Natural language command processing    → /services/chat/command_processor.py::process_command()
Kimi K2 integration                     → /services/chat/providers/kimi_provider.py
```

---

#### **14. LIVE TRADING INTEGRATION**
**Current Location**: `/minhos/services/live_trading_integration.py`
**New Location**: `/services/orchestration/trading_orchestrator.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
coordinate_live_trading()               → /services/orchestration/trading_orchestrator.py::coordinate()
integrate_ai_with_market_data()         → /services/orchestration/ai_data_integrator.py::integrate()
manage_multi_chart_flow()               → /services/orchestration/data_flow_manager.py::manage_flow()
Multi-service orchestration             → /services/orchestration/service_coordinator.py
Decision-based live trading coordination → /services/orchestration/decision_coordinator.py
```

---

#### **15. PATTERN ANALYZER**
**Current Location**: `/minhos/services/pattern_analyzer.py`
**New Location**: `/services/analysis/pattern_service.py`

**Features Being Moved:**
```
CURRENT FEATURE                          → NEW LOCATION
Pattern detection algorithms            → /services/analysis/pattern_service.py::detect_patterns()
Pattern recognition engine              → /services/analysis/engines/pattern_engine.py
Historical pattern matching             → /services/analysis/matching/historical_matcher.py
Pattern confidence scoring              → /services/analysis/scoring/pattern_scorer.py
```

**API Endpoints Moving To:**
```
CURRENT ENDPOINT                         → NEW HANDLER
/api/patterns/detected                  → /interfaces/rest/endpoints/pattern_endpoints.py::get_detected()
```

---

### **DASHBOARD COMPONENTS MAPPING**

#### **Current Dashboard Template**
**Current Location**: `/minhos/dashboard/templates/index.html` (1,739 lines)
**New Location**: Split into organized components

**Dashboard Sections Mapping:**
```
CURRENT SECTION                          → NEW COMPONENT
Lines 596-617: System Status Bar        → /dashboard/templates/components/system_status.html
Lines 666-784: AI Transparency (Blue)   → /dashboard/templates/components/ai_transparency.html
Lines 786-881: Decision Quality (Orange) → /dashboard/templates/components/decision_quality.html
Lines 883-913: Chat Interface (Green)   → /dashboard/templates/components/chat_interface.html
Lines 655-662: Rollover Alerts (Purple) → /dashboard/templates/components/rollover_alerts.html
Lines 622-636: Trading Control Panel    → /dashboard/templates/components/trading_control.html
Lines 638-653: Market Data Panel        → /dashboard/templates/components/market_data.html
Lines 915-958: Critical Systems Monitor → /dashboard/templates/components/critical_systems.html
Lines 960-996: Trading Config Panel     → /dashboard/templates/components/trading_config.html
```

**JavaScript Functions Mapping:**
```
CURRENT FUNCTION                         → NEW LOCATION
Lines 1011-1049: connectWebSocket()     → /dashboard/static/js/utils/websocket_manager.js::connect()
Lines 1051-1055: handleWebSocketMessage() → /dashboard/static/js/utils/websocket_manager.js::handleMessage()
Lines 1057-1106: updateDashboard()      → /dashboard/static/js/dashboard.js::updateDashboard()
Lines 1108-1143: updateRolloverAlerts() → /dashboard/static/js/components/rollover_alerts.js::update()
Lines 1145-1241: updateAITransparency() → /dashboard/static/js/components/ai_transparency.js::update()
Lines 1243-1254: updateConnectionStatus() → /dashboard/static/js/utils/websocket_manager.js::updateStatus()
Lines 1273-1292: setTradingMode()        → /dashboard/static/js/components/trading_control.js::setMode()
Lines 1294-1313: emergencyStop()        → /dashboard/static/js/components/trading_control.js::emergencyStop()
Lines 1315-1384: loadCriticalStatus()   → /dashboard/static/js/components/critical_systems.js::loadStatus()
Lines 1386-1393: updateStatusBadge()    → /dashboard/static/js/utils/status_utils.js::updateBadge()
Lines 1395-1428: loadServiceStatus()    → /dashboard/static/js/components/system_monitor.js::loadStatus()
Lines 1435-1552: updateDecisionQuality() → /dashboard/static/js/components/decision_quality.js::update()
Lines 1554-1657: Chat Interface Functions → /dashboard/static/js/components/chat_interface.js
Lines 1664-1735: Trading Dashboard Functions → /dashboard/static/js/components/trading_control.js
```

---

### **CONFIGURATION VALUES MAPPING**

#### **Hardcoded Values Being Centralized**

**Network Configuration:**
```
CURRENT HARDCODED                        → NEW CONFIGURATION LOCATION
"cthinkpad" (Sierra bridge host)        → /configuration/master/production.yaml::network.sierra_bridge.host
8765 (Sierra bridge port)               → /configuration/master/production.yaml::network.sierra_bridge.port
8080 (Web API port)                     → /configuration/master/production.yaml::network.web_api.port
5000 (Dashboard port)                   → /configuration/master/production.yaml::network.dashboard.port
5000 (WebSocket timeout)                → /configuration/master/production.yaml::network.sierra_bridge.timeout
```

**Symbol Configuration:**
```
CURRENT HARDCODED                        → NEW CONFIGURATION LOCATION
"NQU25" (hardcoded ~60 files)          → Retrieved from /core/symbols/symbol_manager.py::get_current_symbol()
"ESU25"                                 → Retrieved from /core/symbols/symbol_manager.py::get_current_symbol()
"EURUSD"                               → /configuration/master/production.yaml::symbols.forex.EURUSD
"XAUUSD"                               → /configuration/master/production.yaml::symbols.forex.XAUUSD
"VIX_CGI"                              → /configuration/master/production.yaml::symbols.indices.VIX
```

**Trading Configuration:**
```
CURRENT HARDCODED                        → NEW CONFIGURATION LOCATION
autonomous_threshold = 0.75             → /configuration/master/production.yaml::trading.autonomous_threshold
trading_modes = ["manual", "semi", "auto"] → /configuration/master/production.yaml::trading.modes
max_position_size = 5                   → /configuration/master/production.yaml::risk.max_position_size
circuit_breaker_threshold = 0.05        → /configuration/master/production.yaml::risk.circuit_breaker_threshold
```

**Update Intervals:**
```
CURRENT HARDCODED                        → NEW CONFIGURATION LOCATION
setInterval(loadServiceStatus, 10000)   → /configuration/master/production.yaml::dashboard.update_intervals.service_status
setInterval(loadCriticalStatus, 5000)   → /configuration/master/production.yaml::dashboard.update_intervals.critical_status
setInterval(updateAITransparency, 2000) → /configuration/master/production.yaml::dashboard.update_intervals.ai_transparency
setInterval(updateDecisionQuality, 3000) → /configuration/master/production.yaml::dashboard.update_intervals.decision_quality
```

---

### **DATABASE AND DATA MAPPING**

#### **Database Files:**
```
CURRENT DATABASE                         → NEW LOCATION
/data/decision_quality.db               → /data/database/sqlite/decision_quality.db
/data/state.db                          → /data/database/sqlite/state.db
/data/market_data.db                    → /data/database/sqlite/market_data.db
/data/risk.db                           → /data/database/sqlite/risk.db
```

#### **Data Access:**
```
CURRENT DATA ACCESS                      → NEW DATA ACCESS LAYER
Direct SQLite calls                     → /data/database/repositories/decision_repo.py
State manager database calls           → /data/database/repositories/state_repo.py
Market data storage                     → /data/database/repositories/market_data_repo.py
Risk parameter storage                  → /data/database/repositories/risk_repo.py
```

---

## 🔍 **VALIDATION CHECKLIST BY FEATURE**

### **All 50+ API Endpoints Must Work Identically:**
- [ ] `/api/status` returns same system status data
- [ ] `/api/health` returns same health check data
- [ ] `/api/trading/mode` accepts same mode parameters
- [ ] `/api/trading/emergency-stop` triggers same emergency stop
- [ ] `/api/market/data/{symbol}` returns same market data format
- [ ] `/api/market/symbols` returns same symbol list
- [ ] `/api/ai/current-analysis` returns same AI analysis data
- [ ] `/api/ai/reasoning-breakdown` returns same reasoning data
- [ ] `/api/ai/risk-assessment` returns same risk data
- [ ] `/api/decision-quality/current` returns same quality metrics
- [ ] `/api/decision-quality/summary` returns same quality summary
- [ ] `/api/trading/positions` returns same position data
- [ ] `/api/trading/orders` returns same order data
- [ ] `/api/risk/status` returns same risk status
- [ ] `/api/symbols/rollover-status` returns same rollover data
- [ ] All other 35+ endpoints return identical data

### **All Dashboard Sections Must Look and Function Identically:**
- [ ] System Status Bar shows same health/mode/positions/P&L
- [ ] AI Transparency (Blue) shows same real-time reasoning
- [ ] Decision Quality (Orange) shows same 6-category evaluation
- [ ] Chat Interface (Green) processes same natural language commands
- [ ] Rollover Alerts (Purple) shows same countdown timers
- [ ] Trading Control Panel has same mode buttons and emergency stop
- [ ] Market Data Panel shows same live prices
- [ ] Critical Systems Monitor shows same service health
- [ ] Trading Config Panel has same autonomous toggle

### **All Real-Time Features Must Continue Working:**
- [ ] WebSocket connections auto-reconnect
- [ ] Dashboard updates at same intervals (10s, 5s, 2s, 3s)
- [ ] AI reasoning updates in real-time
- [ ] Market data streams continuously
- [ ] System health monitors continuously
- [ ] Chat interface responds to messages
- [ ] Rollover countdown updates every minute

### **All Data Must Be Preserved:**
- [ ] decision_quality.db accessible and unchanged
- [ ] state.db accessible and unchanged
- [ ] market_data.db accessible and unchanged
- [ ] risk.db accessible and unchanged
- [ ] All historical trading data preserved
- [ ] All decision quality history preserved
- [ ] All system configuration preserved

---

## 📋 **IMPLEMENTATION EXECUTION PLAN**

### **Phase 1: Create New Structure (Day 1)**
1. Create all new directories according to mapping
2. Move configuration files to centralized locations
3. Test that configuration centralization works
4. **Validation**: Current system still works with centralized config

### **Phase 2: Migrate Core Services (Days 2-3)**
1. Move each service according to mapping above
2. Update imports and dependencies
3. Test each service individually
4. **Validation**: Each service works in new location

### **Phase 3: Migrate API Endpoints (Days 4-5)**
1. Move all 50+ endpoints to organized modules
2. Update routing and imports
3. Test all endpoints return identical data
4. **Validation**: All API tests pass

### **Phase 4: Migrate Dashboard (Days 6-7)**
1. Split dashboard template into components
2. Organize JavaScript into modules
3. Test all dashboard sections work identically
4. **Validation**: Dashboard looks and functions exactly the same

### **Phase 5: Final Integration (Days 8-9)**
1. Test complete system end-to-end
2. Validate all features preserved
3. Performance testing
4. **Validation**: System ready for production

---

## ✅ **ZERO-LOSS GUARANTEE**

This mapping ensures that **every single feature, endpoint, dashboard section, configuration value, and piece of functionality** has a clearly defined new home. Nothing is lost, everything is organized better.

**Before Implementation**: Scattered chaos with NQU25 hardcoded in ~60 files
**After Implementation**: Clean architecture with centralized configuration

**Same Features, Better Organization, Zero Loss, Quarterly Rollover Problem Solved.**