# MinhOS v3 Critical Components

## Overview
This document describes the newly created critical components that enable MinhOS v3 to achieve feature parity with v2.

## Components Created

### 1. Main Entry Point (`minhos/main.py`)
- Central orchestrator for the entire system
- Manages application lifecycle
- Handles graceful shutdown via signal handlers
- Provides system status reporting
- Integrates with the service orchestrator

**Key Features:**
- Async-first design
- Comprehensive logging
- Configuration management
- Status monitoring

### 2. Service Orchestrator (`minhos/services/orchestrator.py`)
- Manages all service lifecycles
- Handles service dependencies
- Provides health monitoring
- Automatic service recovery with backoff
- Service restart capabilities

**Key Features:**
- Dependency-based startup ordering
- Health check monitoring
- Automatic recovery for failed services
- Manual service restart API
- Comprehensive service status reporting

### 3. Web Dashboard (`minhos/dashboard/main.py`)
- FastAPI-based web interface
- Real-time WebSocket updates
- System monitoring and control
- Integration with all services

**Key Features:**
- Real-time status updates via WebSocket
- Service health monitoring
- Trading control interface
- Performance metrics visualization
- Responsive web design

### 4. Dashboard API (`minhos/dashboard/api.py`)
- Comprehensive REST API endpoints
- System control and monitoring
- Trading operations
- Configuration management

**Endpoints:**
- `/api/status` - System status
- `/api/trading/mode` - Trading mode control
- `/api/trading/emergency-stop` - Emergency stop
- `/api/market/data/{symbol}` - Market data
- `/api/trading/positions` - Position management
- `/api/ai/signals` - AI trading signals
- `/api/risk/status` - Risk management status
- `/api/config/{section}` - Configuration access

### 5. Dashboard Frontend (`minhos/dashboard/templates/index.html`)
- Modern, responsive web interface
- Real-time data visualization
- System control panel
- WebSocket integration

**Features:**
- Live system status display
- Trading mode controls
- Emergency stop button
- Service health monitoring
- Real-time log viewer
- Market data display

### 6. Enhanced Market Data Service
The existing `market_data.py` already includes comprehensive WebSocket capabilities:
- WebSocket server on port 9001
- HTTP API on port 9002
- Real-time data streaming
- Client subscription management
- Chat functionality
- Performance metrics

## Architecture Integration

### Service Dependencies
```
state_manager (foundation)
    ↓
sierra_client
    ↓
market_data
    ↓
pattern_analyzer + risk_manager
    ↓
ai_brain
    ↓
trading_engine
    ↓
web_api
    ↓
dashboard
```

### Communication Flow
1. Sierra Chart → Sierra Client (via Tailscale bridge)
2. Sierra Client → Market Data Service
3. Market Data Service → WebSocket clients
4. Services → State Manager (shared state)
5. Dashboard → Web API → All services

## Running MinhOS v3

### Prerequisites
- Python 3.9+
- Linux environment
- Tailscale connection to Windows/Sierra Chart
- Required Python packages (see requirements.txt)

### Startup
```bash
# From the MinhOS v3 directory
chmod +x start.sh
./start.sh
```

### Access Points
- Dashboard: http://localhost:8888
- API: http://localhost:8888/api
- WebSocket: ws://localhost:9001
- Market Data API: http://localhost:9002

## Key Improvements over v2

1. **Clean Architecture**: Separation of concerns with modular services
2. **Linux-Native**: No Windows dependencies in core system
3. **Modern Stack**: FastAPI, WebSockets, async/await throughout
4. **Better Error Handling**: Comprehensive error handling and recovery
5. **Real-time Updates**: WebSocket-based real-time data streaming
6. **Service Health**: Automatic health monitoring and recovery
7. **Unified API**: Single REST API for all operations

## Configuration

Create a `config.yaml` file in the root directory:

```yaml
environment: production
debug: false

services:
  sierra_bridge:
    host: 100.64.0.2
    port: 5555
  
  market_data:
    ws_port: 9001
    http_port: 9002
  
  web_api:
    port: 8000
  
  dashboard:
    port: 8888

trading:
  mode: manual
  risk_limit: 10000
  max_positions: 5
```

## Testing

### Health Check
```bash
# Check dashboard health
curl http://localhost:8888/health

# Check API health
curl http://localhost:8888/api/health

# Check system status
curl http://localhost:8888/api/status
```

### WebSocket Test
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:9001');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({type: 'ping'}));
};

ws.onmessage = (event) => {
    console.log('Received:', JSON.parse(event.data));
};
```

## Troubleshooting

### Service Won't Start
- Check logs in `logs/minhos.log`
- Verify all dependencies are installed
- Ensure ports are not in use
- Check Sierra Chart bridge connectivity

### Dashboard Not Loading
- Verify dashboard service is running
- Check browser console for errors
- Ensure WebSocket connection is established
- Check API endpoints are responding

### No Market Data
- Verify Sierra Chart is running
- Check Tailscale connection
- Verify bridge service on Windows
- Check market_data service logs

## Next Steps

1. Implement authentication for dashboard
2. Add data persistence for historical analysis
3. Enhance AI trading strategies
4. Add more chart visualizations
5. Implement backtesting interface
6. Add performance analytics dashboard