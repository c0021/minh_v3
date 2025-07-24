# MinhOS v3 - Linux-Native Trading Platform

> **🚀 Revolutionary Architecture**: Trade from anywhere with your Linux laptop while your Windows PC handles Sierra Chart via Tailscale!

MinhOS v3 is a complete rewrite of the MinhOS trading system, designed for Linux environments with sophisticated AI-powered trading intelligence. It connects to Sierra Chart running on Windows via a secure Tailscale mesh network.

## ✨ Key Features

### 🏗️ **Modern Architecture**
- **Linux-Native**: 100% Linux compatible, no Windows dependencies
- **Tailscale Integration**: Secure remote connection to Windows trading PC
- **Microservices**: Modular service-based architecture
- **Async/Await**: Modern Python async programming throughout
- **Type Safety**: Comprehensive type hints and validation

### 🤖 **AI-Powered Trading**
- **Market Intelligence**: Advanced pattern recognition and analysis
- **Risk Management**: Sophisticated risk controls and circuit breakers
- **Decision Support**: Human-in-the-loop trading decisions
- **Machine Learning**: Continuous learning from market outcomes

### 📊 **Real-Time Data**
- **WebSocket Streaming**: Sub-second market data updates
- **Multi-Symbol Support**: Handle multiple trading instruments
- **Historical Storage**: Efficient time-series data management
- **Event-Driven**: Real-time event processing and notifications

### 🛡️ **Enterprise-Grade**
- **Health Monitoring**: Comprehensive system health checks
- **Performance Metrics**: Built-in performance monitoring
- **Graceful Shutdown**: Proper service lifecycle management
- **Error Recovery**: Robust error handling and recovery

## 🏛️ Architecture Overview

```
┌─── Windows PC (Home) ──────────────┐    Tailscale    ┌─── Linux Laptop (Anywhere) ─────────────┐
│                                    │       Mesh      │                                        │
│  Sierra Chart                      │     Network     │  MinhOS v3 Platform                    │
│  └── Real-time market data         │   🔒 Secure     │  ├── AI Trading Intelligence            │
│                                    │   🌐 Remote     │  ├── Real-time Analytics               │
│  Windows Bridge (bridge.py)       │                │  ├── Risk Management                   │
│  ├── FastAPI server :8765          │◄───────────────►│  ├── Pattern Recognition              │
│  ├── WebSocket streaming           │                │  ├── Web Dashboard                     │
│  └── Trade execution proxy        │                │  └── Machine Learning Models           │
│                                    │                │                                        │
│  Always-on, stable connection     │                │  Develop & trade from anywhere         │
└────────────────────────────────────┘                └────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Linux System**: Ubuntu 20.04+, Pop!_OS, or similar
- **Python 3.9+**: With pip and venv
- **Docker** (optional): For supporting services
- **Tailscale Account**: For secure networking

### 1. Install MinhOS v3

```bash
# Clone the repository
git clone https://github.com/minhos/minhos_v3.git
cd minhos_v3

# Set up development environment
make dev

# Or manual installation
pip install -r requirements.txt
docker-compose up -d redis postgres
```

### 2. Set up Windows Bridge

On your Windows trading PC:

```powershell
# Copy bridge files to Windows PC
# Run the installation script
.\bridge_windows\install.ps1

# Start the bridge
cd C:\MinhOSBridge
.\start_bridge.ps1
```

### 3. Configure Tailscale

```bash
# Install Tailscale on both systems
curl -fsSL https://tailscale.com/install.sh | sh

# Connect both devices to your Tailscale network
sudo tailscale up

# Set your Windows PC hostname (example: trading-pc)
# Update SIERRA_HOST in .env if different
export SIERRA_HOST=trading-pc
```

### 4. Test Connection

```bash
# Test bridge connectivity
make bridge-test

# Start MinhOS v3
make run

# Open dashboard
firefox http://localhost:8000
```

## 📁 Project Structure

```
minhos_v3/
├── bridge_windows/           # Windows bridge (minimal)
│   ├── bridge.py            # FastAPI bridge server
│   ├── requirements.txt     # Bridge dependencies
│   └── install.ps1          # Windows installation script
│
├── minhos/                  # Main Linux application
│   ├── core/                # Core utilities
│   │   ├── config.py        # Tailscale-aware configuration
│   │   ├── base_service.py  # Service base class
│   │   └── sierra_client.py # Bridge client
│   │
│   ├── services/            # Core services
│   │   ├── market_data.py   # Real-time data streaming
│   │   ├── web_api.py       # REST API endpoints
│   │   ├── state_manager.py # State persistence
│   │   ├── ai_brain_service.py      # AI analysis
│   │   ├── trading_engine.py        # Trading logic
│   │   ├── pattern_analyzer.py      # Pattern recognition
│   │   └── risk_manager.py          # Risk management
│   │
│   ├── dashboard/           # Web interface
│   ├── analysis/            # Trading analysis tools
│   └── utils/              # Utilities
│
├── tests/                   # Comprehensive test suite
├── scripts/                 # Management scripts
├── data/                    # Local data storage
├── logs/                    # Application logs
├── Makefile                 # Development commands
├── docker-compose.yml       # Supporting services
└── requirements.txt         # Python dependencies
```

## 🛠️ Development

### Common Commands

```bash
# Development workflow
make install          # Install dependencies
make dev             # Start development environment  
make run             # Run MinhOS v3
make test            # Run test suite
make lint            # Code linting
make format          # Code formatting

# Monitoring
make logs            # View logs
make status          # System status
make bridge-test     # Test bridge connection

# Maintenance
make clean           # Clean temporary files
```

### Configuration

Create `.env` file from `.env.example`:

```bash
cp .env.example .env

# Edit configuration
SIERRA_HOST=trading-pc    # Your Windows PC Tailscale hostname
SIERRA_PORT=8765         # Bridge port
MINHOS_ENV=dev          # Environment
```

### Testing

```bash
# Run all tests
make test

# Run specific test categories
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/bridge/ -m bridge  # Bridge connection tests (requires bridge)

# Skip slow tests
pytest -m "not slow"
```

## 📊 Services Overview

### Core Services

| Service | Purpose | Port | Dependencies |
|---------|---------|------|--------------|
| **Market Data** | Real-time data streaming | WS:9001 | Sierra Bridge |
| **Web API** | REST endpoints | HTTP:8000 | State Manager |
| **State Manager** | Data persistence | - | SQLite/Redis |
| **Trading Engine** | Trade execution logic | - | Market Data, Risk |
| **AI Brain** | Market analysis | - | Market Data, Patterns |
| **Risk Manager** | Risk controls | - | Trading Engine |

### Bridge Communication

The Windows bridge provides these endpoints:
- `GET /health` - Health status
- `GET /api/market_data` - Current market snapshot
- `WS /ws/market_stream` - Real-time data stream
- `POST /api/trade/execute` - Execute trades
- `GET /api/trade/status/{id}` - Trade status

## 🧠 AI Features

### Market Intelligence
- **Pattern Recognition**: Identify market patterns and trends
- **Regime Detection**: Automatically detect market conditions
- **Signal Generation**: AI-powered trading signals
- **Confidence Scoring**: Signal reliability assessment

### Risk Management
- **Position Monitoring**: Real-time position tracking
- **Drawdown Protection**: Maximum loss prevention
- **Volatility Adjustments**: Dynamic position sizing
- **Circuit Breakers**: Automatic emergency stops

### Machine Learning
- **Online Learning**: Continuous model updates
- **Feature Engineering**: Advanced market indicators
- **Performance Tracking**: Track prediction accuracy
- **Model Selection**: Automatic best model selection

## 🔧 Configuration Options

### Environment Variables

```bash
# Core Configuration
MINHOS_ENV=dev                    # Environment: dev/prod/test
SIERRA_HOST=trading-pc            # Windows PC hostname
SIERRA_PORT=8765                  # Bridge port

# Database
DATABASE_URL=sqlite:///./data/minhos.db
REDIS_URL=redis://localhost:6379/0

# Trading
MAX_POSITION_SIZE=100000.0        # Maximum position size
MAX_DAILY_LOSS=5000.0            # Daily loss limit
ENABLE_PAPER_TRADING=true        # Paper trading mode

# API
API_PORT=8000                    # REST API port
WS_PORT=9001                     # WebSocket port
```

### Advanced Configuration

See `minhos/core/config.py` for comprehensive configuration options including:
- Database connection pooling
- Redis clustering
- Performance tuning
- Monitoring settings
- Security options

## 📈 Monitoring & Observability

### Built-in Monitoring
- **Health Checks**: Service health monitoring
- **Performance Metrics**: Request rates, latency, errors
- **System Metrics**: CPU, memory, disk usage
- **Trading Metrics**: P&L, positions, risk metrics

### Optional Monitoring Stack
```bash
# Start monitoring services
docker-compose --profile monitoring up -d

# Access dashboards
firefox http://localhost:3000    # Grafana (admin/admin)
firefox http://localhost:9090    # Prometheus
```

## 🔒 Security

### Network Security
- **Tailscale Encryption**: All traffic encrypted end-to-end
- **No Port Forwarding**: No open ports on public internet
- **Access Control**: Tailscale device authentication

### Application Security  
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: API rate limiting and throttling
- **Error Handling**: Secure error messages
- **Audit Logging**: Complete audit trail

## 🚢 Deployment

### Development (Local)
```bash
make dev           # Start with Docker services
make run           # Run MinhOS v3
```

### Production (Linux Server)
```bash
# Install for production
make install-prod

# Set up systemd service
make deploy-systemd

# Start service
sudo systemctl start minhos
sudo systemctl enable minhos
```

### Docker Deployment
```bash
# Build container
docker build -t minhos:v3 .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing Strategy

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing  
- **Bridge Tests**: Windows bridge connectivity
- **Performance Tests**: Load and performance testing

### Test Coverage
```bash
make test                    # Run all tests with coverage
firefox htmlcov/index.html  # View coverage report
```

## 📚 Documentation

### API Documentation
- REST API: `http://localhost:8000/docs` (FastAPI auto-docs)
- WebSocket API: See `docs/websocket_api.md`

### Development Guides
- [Service Development](docs/service_development.md)
- [Adding New Indicators](docs/indicators.md)
- [Custom Trading Strategies](docs/strategies.md)
- [Bridge Protocol](docs/bridge_protocol.md)

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Follow code style and add tests
4. **Run tests**: `make test`
5. **Submit PR**: Include description and tests

### Code Standards
- **Formatting**: Black + isort (`make format`)
- **Linting**: Ruff (`make lint`) 
- **Type Hints**: mypy (`make type-check`)
- **Testing**: pytest with good coverage
- **Documentation**: Docstrings and comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Bridge Connection Failed**
```bash
# Check Tailscale connection
tailscale status

# Test bridge manually  
curl http://trading-pc:8765/health

# Check bridge logs on Windows
```

**Service Won't Start**
```bash
# Check logs
make logs

# Verify dependencies
docker-compose ps

# Reset database
make db-reset
```

**Performance Issues**
```bash
# Check system resources
make status

# Monitor performance
make profile
```

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/minhos/minhos_v3/issues)
- **Discussions**: [GitHub Discussions](https://github.com/minhos/minhos_v3/discussions)
- **Wiki**: [Project Wiki](https://github.com/minhos/minhos_v3/wiki)

---

## 🎯 Roadmap

### v3.1 (Next Release)
- [ ] **Natural Language Chat Interface** - Conversational trading assistant powered by Kimi K2 API
- [ ] Advanced charting interface
- [ ] Multiple broker integration
- [ ] Mobile dashboard
- [ ] Cloud deployment options

### v3.2 (Future)
- [ ] Multi-asset portfolio management
- [ ] Advanced options strategies  
- [ ] Social trading features
- [ ] API marketplace

---

**Made with ❤️ for traders who demand excellence**

*MinhOS v3 - Trade smarter, not harder*