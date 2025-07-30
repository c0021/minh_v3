# MinhOS v3 - Complete Features & Functionality Documentation

**Version**: 3.0.0  
**Last Updated**: July 26, 2025  
**System Status**: Production Ready with Dashboard Rollover Alerts  

---

## 🚀 System Overview

MinhOS v3 is an advanced AI-powered trading system that provides real-time market analysis, automated trading capabilities, and comprehensive risk management. The system integrates with Sierra Chart for live market data and trade execution while maintaining strict "no fake data" policies.

**Core Philosophy**: Making the best decisions possible with available information and resources - 100% real market data, zero simulation or mock data.

---

## 🏗️ Core Architecture & Services

### Central Command Interface
- **File**: `minh.py`
- **Purpose**: Single entry point CLI for managing the complete MinhOS v3 trading system
- **Commands**:
  - `start` - Start MinhOS v3 trading system (with optional `--monitor` flag)
  - `stop` - Stop all MinhOS services gracefully  
  - `status` - Show comprehensive system status and health
  - `test` - Run integration tests for all components
  - `config` - Manage configuration settings (show/set operations)
  - `logs` - View system logs (with optional `--follow` flag)

### Core Services

#### 1. AI Brain Service (`ai_brain_service.py`)
**Advanced AI analysis and trading signal generation**
- **Signal Types**: BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
- **Analysis Types**: Technical, Momentum, Volatility, Volume, Pattern
- **Features**:
  - Real-time market analysis with 1000-point data buffer
  - Trading signals with confidence scoring (0.0-1.0)
  - Multi-timeframe analysis (trend, momentum, volatility)
  - Pattern recognition and support/resistance identification
  - Historical fallback system (7-day lookback)
  - Automatic gap-filling for continuous data integrity

#### 2. Trading Engine (`trading_engine.py`)  
**Intelligent trading execution with human oversight**
- **Decision Priorities**: Critical, High, Medium, Low, Informational
- **Market Regimes**: Trending Up/Down, Ranging, Volatile, Quiet
- **Execution Strategies**: Market, Limit, Stop Market, Adaptive
- **Features**:
  - Autonomous trading at 75%+ confidence without human approval
  - Decision quality framework with SQLite persistence
  - Market regime detection and adaptive strategies
  - Position management with intelligent sizing
  - Human override capabilities for all decisions

#### 3. Risk Manager (`risk_manager.py`)
**Comprehensive risk management and validation**
- **Risk Levels**: Low, Medium, High, Critical, Emergency
- **Features**:
  - Pre-trade validation for all orders
  - Real-time position monitoring
  - Daily loss limits and drawdown protection
  - Volatility-adjusted position sizing
  - Order rate limiting (anti-spam protection)
  - Risk violation alerts with recommendations

#### 4. Sierra Client (`sierra_client.py`)
**Live trading integration with Sierra Chart**
- **Connection**: WebSocket + HTTP API bridge to Windows Sierra Chart
- **Features**:
  - Real-time market data streaming (NQ, ES, VIX)
  - Live trade execution via bridge API
  - Multi-symbol data collection and distribution
  - Robust reconnection logic with fallback IPs
  - Trade result tracking and status reporting

#### 5. State Manager (`state_manager.py`)
**Centralized system state and persistence**
- **States**: Online/Offline system states, Manual/Semi/Full trading modes
- **Features**:
  - SQLite-based persistent storage
  - Position tracking and portfolio management
  - Configuration management
  - System health monitoring
  - Trading session logging

---

## 🖥️ Dashboard & User Interface

### Web Dashboard (`dashboard/main.py`)
**FastAPI-based real-time monitoring interface**

#### 4-Section Layout:
1. **AI Transparency (Blue)** - Real-time AI reasoning display
2. **Decision Quality (Orange)** - Process evaluation with 6-category scoring
3. **Chat Interface (Green)** - Natural language trading commands
4. **Traditional Metrics** - Market data, positions, performance

#### Dashboard Features:
- **Real-time Updates**: WebSocket-based live data streaming
- **Rollover Alerts**: Purple-themed widget showing contract expiration countdown
- **Color-coded Status**: Critical (red), Warning (yellow), Info (blue), Normal (green)
- **API Endpoints**: 50+ REST endpoints for system control
- **Enhanced Grid Layout**: 3-column responsive design

### Chat Interface (`chat_service.py`)
**Natural language interaction with trading system**
- **WebSocket Endpoint**: `/ws/chat` for real-time bidirectional communication
- **NLP Processing**: API-agnostic (Kimi K2, OpenAI, Local LLM support)
- **Features**:
  - Intent parsing and command translation
  - Natural language → structured trading commands
  - Conversation history and context management
  - Service integration bridge to AI Brain and Sierra Client
  - Smart command suggestions based on market state

---

## 🔄 Symbol Management Revolution

### Centralized Symbol Manager (`symbol_manager.py`)
**Eliminates quarterly contract rollover maintenance**

#### Key Features:
- **Automatic Rollover Logic**: NQU25 → NQZ25 → NQH26 based on expiration dates
- **Single Source of Truth**: Centralized configuration for all services
- **Contract Specifications**: Tick size, contract size, expiration schedules
- **Environment Awareness**: Production vs development symbol sets

#### Configuration (`symbols.json`):
```json
{
  "contracts": {
    "NQ": {
      "base_symbol": "NQ",
      "exchange": "CME", 
      "expiration_months": ["H", "M", "U", "Z"],
      "days_before_rollover": 10
    }
  },
  "environments": {
    "production": {
      "enabled_symbols": ["NQ", "ES", "VIX"],
      "max_concurrent_subscriptions": 3
    }
  }
}
```

#### Migration Framework (`symbol_integration.py`):
- Drop-in replacement functions for existing services
- Backwards compatibility during transition
- Service migration tracking
- Unified socket subscription management

---

## 📊 Data Integration & Market Data

### Historical Data Service (`sierra_historical_data.py`)
**20x more historical context for AI analysis**
- **Data Sources**: Sierra Chart .dly (CSV) and .scid (binary) files  
- **Features**:
  - Automatic gap detection and backfilling
  - Tailscale-aware remote file access
  - Historical preprocessing for AI consumption
  - Multi-timeframe data support (1min, 30min, daily)

### Market Data Adapter (`market_data_adapter.py`)
**Unified data pipeline across all services**
- **Real-time Processing**: Live Sierra Chart → MinhOS services
- **Data Validation**: NO FAKE DATA policy enforcement
- **Distribution**: WebSocket relay to all connected services
- **Caching**: Intelligent data buffering and replay

---

## 🤖 AI Trading Capabilities

### Mathematical & Statistical Analysis
- **Multi-timeframe Analysis**: 1-minute to daily charts
- **Technical Indicators**: 14+ standard indicators (RSI, MACD, Bollinger Bands)
- **Pattern Recognition**: Candlestick patterns, support/resistance levels
- **Volume Analysis**: Volume-weighted decisions and momentum tracking
- **Volatility Modeling**: Dynamic position sizing based on market volatility

### Decision Quality Framework
**6-Category Process Evaluation System**
1. **Information Quality** - Data completeness and reliability
2. **Alternative Options** - Range of choices considered  
3. **Decision Process** - Methodology and reasoning quality
4. **Risk Assessment** - Threat identification and mitigation
5. **Timing** - Market timing and execution quality
6. **Learning Integration** - Feedback incorporation and improvement

### Autonomous Trading Features
- **Confidence Thresholds**: 75%+ for autonomous execution
- **Risk-Adjusted Sizing**: Dynamic position sizing based on confidence and volatility
- **Stop Loss Management**: Automatic stop placement and adjustment
- **Human Override**: Manual intervention available at any time

---

## 🛡️ Risk Management & Safety

### Pre-Trade Validation
- **Position Limits**: Maximum position size enforcement
- **Daily Loss Limits**: Automatic trading halt on loss thresholds
- **Drawdown Protection**: Maximum portfolio drawdown monitoring
- **Order Rate Limiting**: Anti-spam protection (max orders per minute)

### Real-time Monitoring
- **Risk Level Alerts**: 5-tier risk level system (Low to Emergency)
- **Violation Tracking**: All risk breaches logged with recommendations
- **Circuit Breakers**: Automatic system halt on critical violations
- **Recovery Procedures**: Automated and manual recovery protocols

---

## 🌐 External Integrations

### Sierra Chart Bridge
**Windows Bridge for Live Trading**
- **Location**: `windows/bridge_installation/`
- **Features**:
  - HTTP API server on port 8765
  - File access API for historical data
  - Real-time market data streaming
  - Trade execution command processing
  - Health monitoring and status reporting

### ACSIL Studies (`windows/acsil_studies/`)
**Sierra Chart custom studies for enhanced data collection**
- **MinhOS_TickDataExporter_v3.cpp**: Latest tick data export study
- **Trade Execution Integration**: Direct Sierra Chart trade submission
- **Custom Indicators**: MinhOS-specific technical indicators

---

## 📈 Performance & Monitoring

### System Status Monitoring
- **Health Checks**: Automated service health validation
- **Performance Metrics**: Latency, throughput, success rates
- **Resource Monitoring**: Memory, CPU, storage usage
- **Alert System**: Proactive issue detection and notification

### Trading Performance
- **P&L Tracking**: Real-time profit/loss calculation
- **Win Rate Analysis**: Success rate by strategy and timeframe
- **Risk-Adjusted Returns**: Sharpe ratio and maximum drawdown
- **Decision Quality Metrics**: Process improvement tracking

---

## 🔧 Configuration & Customization

### Environment Configuration
- **Production**: 3-symbol focus (NQ, ES, VIX) for optimal performance
- **Development**: Extended symbol set for testing
- **Testing**: Minimal setup for validation

### Customizable Parameters
- **AI Analysis**: Trend periods, confidence thresholds, signal sensitivity
- **Risk Management**: Position limits, loss thresholds, volatility multipliers  
- **Trading Engine**: Execution strategies, timing parameters, human override levels
- **Dashboard**: Update frequencies, alert thresholds, display preferences

---

## 🚀 Production Deployment Features

### Startup & Shutdown
- **Graceful Startup**: Service dependency resolution and health validation
- **Clean Shutdown**: Proper service termination and state persistence
- **Recovery**: Automatic restart and state restoration capabilities
- **Monitoring**: Real-time system health and performance tracking

### Operational Tools
- **Status Commands**: Comprehensive system diagnostics
- **Log Management**: Centralized logging with rotation and archival
- **Configuration Management**: Runtime configuration updates
- **Testing Suite**: Comprehensive integration testing framework

---

## 📋 Current Capabilities Summary

### ✅ Fully Operational Features
- **Real Trading**: Live market execution with Sierra Chart integration
- **AI Analysis**: Mathematical/statistical market analysis with historical context
- **Dashboard**: 4-section web interface with real-time updates and rollover alerts
- **Symbol Management**: Automatic quarterly contract rollover with zero maintenance
- **Risk Management**: Comprehensive pre-trade validation and position monitoring
- **Chat Interface**: Natural language trading commands with NLP processing
- **Historical Data**: Complete Sierra Chart archive integration for backtesting

### 🎯 Key Achievements
- **Zero Fake Data**: 100% real market data, no simulation or mock data
- **Resource Optimized**: Designed for retail trader budget constraints ($150/month)
- **Process-Focused**: Decision quality prioritized over pure outcomes
- **AI Transparent**: Complete real-time AI reasoning display
- **Centralized Management**: Single source of truth for all symbol configuration

---

**System Status**: Production ready with all core trading, analysis, and monitoring capabilities operational. Dashboard rollover alerts provide visual confirmation of the revolutionary centralized symbol management system.