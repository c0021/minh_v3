#!/usr/bin/env python3
"""
MinhOS Enhanced AI Context Generator
===================================
Intelligent context generation for AI assistance with deep system understanding.
Automatically detects problems and provides relevant context for effective troubleshooting.

Version: 2.0.0 - Complete rewrite with system intelligence
"""

import os
import sys
import json
import yaml
import glob
import sqlite3
import traceback
import subprocess
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("context_generator")

class ProblemType(Enum):
    """Types of problems that can be auto-detected"""
    STARTUP_FAILURE = "startup_failure"
    SERVICE_DOWN = "service_down"
    DATA_STALE = "data_stale"
    CONNECTIVITY = "connectivity"
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"
    UNKNOWN = "unknown"

@dataclass
class SystemIssue:
    """Represents a detected system issue"""
    problem_type: ProblemType
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    affected_services: List[str]
    suggested_context: List[str]
    diagnostics: Dict[str, Any]

class MinhOSEnhancedContextGenerator:
    """
    Enhanced AI Context Generator with intelligent problem detection
    and comprehensive system understanding
    """
    
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.context_parts = []
        self.detected_issues = []
        self.system_state = {}
        
        # MinhOS v3 port configuration
        self.standard_ports = {
            "sierra_bridge": 8765,
            "minhos_dashboard": 8888,
            "live_integration": 9005,
            "sierra_client": 9003,
            "multi_chart_collector": 9004,
            "ai_brain_service": 9006,
            "trading_engine": 9007,
            "state_manager": 9008,
            "risk_manager": 9009
        }
        
        # Critical file paths
        self.critical_files = {
            "config": self.root_path / "config.yaml",
            "truth": self.root_path / "SYSTEM_TRUTH.json",
            "main_entry": self.root_path / "minh.py",
            "service_orchestrator": self.root_path / "services" / "service_orchestrator.py",
            "backend_study": self.root_path / "services" / "backend_study_enhanced.py",
            "dashboard": self.root_path / "dashboard" / "main.py"
        }
        
        # Database paths
        self.db_paths = {
            "latest_data": self.root_path / "database" / "latest_market_data.json",
            "sqlite_db": self.root_path / "data" / "minhos_state.db",
            "history": self.root_path / "database" / "market_data_history.json"
        }
        
        # Log paths
        self.log_paths = {
            "diagnostic": self.root_path / "diagnostic_log.txt",
            "error": self.root_path / "logs" / "error.log",
            "system": self.root_path / "logs" / "system.log"
        }
        
        # Perform initial system analysis
        self._analyze_system_state()
        
    def _analyze_system_state(self):
        """Analyze current system state and detect problems"""
        logger.info("Analyzing system state...")
        
        # Check service health
        self._check_service_health()
        
        # Check data freshness
        self._check_data_freshness()
        
        # Check configuration integrity
        self._check_configuration()
        
        # Check system resources
        self._check_system_resources()
        
        # Check recent errors
        self._check_recent_errors()
        
        logger.info(f"System analysis complete. Found {len(self.detected_issues)} issues")
    
    def _check_service_health(self):
        """Check health of all critical services"""
        logger.info("Checking service health...")
        
        # Get detailed service health status
        detailed_health = self.verify_service_health()
        
        down_services = []
        unresponsive_services = []
        
        for service_name, health_info in detailed_health.items():
            if not health_info["port_listening"]:
                down_services.append(service_name)
            elif health_info["port_listening"] and not health_info["service_responding"]:
                unresponsive_services.append(service_name)
        
        # Store detailed health info for later use
        self.system_state["detailed_health"] = detailed_health
        
        if down_services:
            issue = SystemIssue(
                problem_type=ProblemType.SERVICE_DOWN,
                severity="HIGH",
                description=f"Services not running: {', '.join(down_services)}",
                affected_services=down_services,
                suggested_context=["service_architecture", "startup_sequence", "port_config"],
                diagnostics={"down_services": down_services, "expected_ports": self.standard_ports}
            )
            self.detected_issues.append(issue)
        
        if unresponsive_services:
            issue = SystemIssue(
                problem_type=ProblemType.CONNECTIVITY,
                severity="MEDIUM",
                description=f"Services listening but not responding: {', '.join(unresponsive_services)}",
                affected_services=unresponsive_services,
                suggested_context=["service_health", "connectivity", "error_analysis"],
                diagnostics={"unresponsive_services": unresponsive_services, "health_details": detailed_health}
            )
            self.detected_issues.append(issue)
    
    def _check_data_freshness(self):
        """Check if market data is stale"""
        logger.info("Checking data freshness...")
        
        latest_data_file = self.db_paths["latest_data"]
        if latest_data_file.exists():
            try:
                with open(latest_data_file, 'r') as f:
                    data = json.load(f)
                
                if 'received_at' in data:
                    received_time = datetime.fromisoformat(data['received_at'].replace('Z', '+00:00'))
                    if received_time.tzinfo:
                        received_time = received_time.replace(tzinfo=None)
                    
                    age_seconds = (datetime.now() - received_time).total_seconds()
                    
                    if age_seconds > 60:  # Data older than 1 minute
                        issue = SystemIssue(
                            problem_type=ProblemType.DATA_STALE,
                            severity="MEDIUM",
                            description=f"Market data is {int(age_seconds)}s old",
                            affected_services=["backend_study", "market_data_watcher"],
                            suggested_context=["data_flow", "sierra_chart_integration"],
                            diagnostics={"data_age_seconds": age_seconds, "last_update": data['received_at']}
                        )
                        self.detected_issues.append(issue)
            except Exception as e:
                logger.error(f"Error checking data freshness: {e}")
    
    def _check_configuration(self):
        """Check configuration integrity"""
        logger.info("Checking configuration...")
        
        config_file = self.critical_files["config"]
        if not config_file.exists():
            issue = SystemIssue(
                problem_type=ProblemType.CONFIGURATION,
                severity="HIGH",
                description="Configuration file missing",
                affected_services=["all"],
                suggested_context=["configuration", "system_setup"],
                diagnostics={"missing_file": str(config_file)}
            )
            self.detected_issues.append(issue)
            return
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check port configuration
            if 'ports' in config:
                port_mismatches = []
                for service, expected_port in self.standard_ports.items():
                    if service in config['ports']:
                        actual_port = config['ports'][service]
                        if actual_port != expected_port:
                            port_mismatches.append(f"{service}: {actual_port} (expected {expected_port})")
                
                if port_mismatches:
                    issue = SystemIssue(
                        problem_type=ProblemType.CONFIGURATION,
                        severity="MEDIUM",
                        description=f"Port configuration mismatches: {', '.join(port_mismatches)}",
                        affected_services=list(self.standard_ports.keys()),
                        suggested_context=["configuration", "port_management"],
                        diagnostics={"port_mismatches": port_mismatches}
                    )
                    self.detected_issues.append(issue)
                    
        except Exception as e:
            issue = SystemIssue(
                problem_type=ProblemType.CONFIGURATION,
                severity="HIGH",
                description=f"Configuration file invalid: {e}",
                affected_services=["all"],
                suggested_context=["configuration", "yaml_validation"],
                diagnostics={"error": str(e)}
            )
            self.detected_issues.append(issue)
    
    def _check_system_resources(self):
        """Check system resource usage"""
        logger.info("Checking system resources...")
        
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, skipping system resource checks")
            return
        
        try:
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                issue = SystemIssue(
                    problem_type=ProblemType.PERFORMANCE,
                    severity="MEDIUM",
                    description=f"High memory usage: {memory.percent}%",
                    affected_services=["all"],
                    suggested_context=["performance", "system_resources"],
                    diagnostics={"memory_percent": memory.percent, "available_gb": memory.available / (1024**3)}
                )
                self.detected_issues.append(issue)
            
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                issue = SystemIssue(
                    problem_type=ProblemType.PERFORMANCE,
                    severity="HIGH",
                    description=f"Low disk space: {disk.percent}% used",
                    affected_services=["all"],
                    suggested_context=["performance", "disk_cleanup"],
                    diagnostics={"disk_percent": disk.percent, "free_gb": disk.free / (1024**3)}
                )
                self.detected_issues.append(issue)
                
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
    
    def _check_recent_errors(self):
        """Check for recent errors in logs"""
        logger.info("Checking recent errors...")
        
        # Check diagnostic log
        diagnostic_log = self.log_paths["diagnostic"]
        if diagnostic_log.exists():
            try:
                with open(diagnostic_log, 'r') as f:
                    lines = f.readlines()
                
                # Look for recent errors (last 100 lines)
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                error_patterns = ["ERROR", "FAILED", "EXCEPTION", "CRITICAL", "FATAL"]
                
                recent_errors = []
                for line in recent_lines:
                    if any(pattern in line.upper() for pattern in error_patterns):
                        recent_errors.append(line.strip())
                
                if recent_errors:
                    issue = SystemIssue(
                        problem_type=ProblemType.UNKNOWN,
                        severity="MEDIUM",
                        description=f"Recent errors found in diagnostic log ({len(recent_errors)} errors)",
                        affected_services=["unknown"],
                        suggested_context=["error_analysis", "diagnostic_logs"],
                        diagnostics={"recent_errors": recent_errors[-10:]}  # Last 10 errors
                    )
                    self.detected_issues.append(issue)
                    
            except Exception as e:
                logger.error(f"Error checking diagnostic log: {e}")
    
    def _is_port_listening(self, port: int) -> bool:
        """Check if a port is listening"""
        if not PSUTIL_AVAILABLE:
            return False
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
        except:
            pass
        return False
    
    def verify_service_health(self):
        """Cross-check port listening vs actual service response"""
        health_status = {}
        
        # Service health check endpoints
        service_endpoints = {
            "backend_study": ("http://localhost:8765/health", "http://localhost:8765/market-data"),
            "http_server": ("http://localhost:8000/api/health", "http://localhost:8000/health"),
            "websocket": ("http://localhost:9002/health", None),  # WebSocket health check endpoint
            "dashboard": ("http://localhost:8888/health", "http://localhost:8888/api/status")
        }
        
        for service, port in self.standard_ports.items():
            listening = self._is_port_listening(port)
            responding = False
            response_time = None
            status_code = None
            error_message = None
            
            health_status[service] = {
                "port": port,
                "port_listening": listening,
                "service_responding": False,
                "response_time_ms": None,
                "status_code": None,
                "error": None
            }
            
            if listening and REQUESTS_AVAILABLE:
                # Try actual health endpoints
                endpoints = service_endpoints.get(service, (f"http://localhost:{port}/health", None))
                
                for endpoint in endpoints:
                    if endpoint is None:
                        continue
                        
                    try:
                        import time
                        start = time.time()
                        resp = requests.get(endpoint, timeout=2)
                        response_time = (time.time() - start) * 1000  # Convert to milliseconds
                        
                        if resp.status_code == 200:
                            responding = True
                            status_code = resp.status_code
                            break
                        elif resp.status_code in [404, 405]:
                            # Service is up but endpoint doesn't exist, try other endpoint
                            continue
                        else:
                            status_code = resp.status_code
                            error_message = f"HTTP {resp.status_code}"
                            
                    except requests.exceptions.ConnectionError:
                        error_message = "ConnectionError"
                    except requests.exceptions.Timeout:
                        error_message = "Timeout"
                    except Exception as e:
                        error_message = f"{type(e).__name__}: {str(e)[:50]}"
                
                # Update health status
                health_status[service].update({
                    "service_responding": responding,
                    "response_time_ms": response_time,
                    "status_code": status_code,
                    "error": error_message
                })
            
            elif listening and not REQUESTS_AVAILABLE:
                # Fallback to socket check if requests not available
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    if result == 0:
                        health_status[service]["service_responding"] = True
                        health_status[service]["error"] = "Socket check passed (requests not available)"
                    else:
                        health_status[service]["error"] = "Socket connection failed"
                except Exception as e:
                    health_status[service]["error"] = f"Socket check failed: {str(e)[:50]}"
                    
        return health_status
    
    def get_trading_context(self):
        """Get comprehensive trading system context"""
        context = {
            "active_strategies": self._get_active_strategies(),
            "current_positions": self._get_positions(),
            "risk_parameters": self._get_risk_config(),
            "recent_trades": self._get_recent_trades(),
            "signal_history": self._get_signal_history(),
            "pnl_summary": self._get_pnl_summary(),
            "market_data_status": self._get_market_data_status()
        }
        return context
    
    def _get_active_strategies(self):
        """Query meta_intelligence_trading.py for active strategies"""
        strategies = []
        try:
            # Check if the meta intelligence trading file exists
            meta_intelligence_file = self.root_path / "core" / "ai" / "meta_intelligence_trading.py"
            if meta_intelligence_file.exists():
                with open(meta_intelligence_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract strategy-related patterns
                import re
                # Look for class definitions that might be strategies
                strategy_classes = re.findall(r'class\s+(\w*Strategy\w*)', content)
                strategy_functions = re.findall(r'def\s+(\w*strategy\w*)', content)
                
                for strategy in strategy_classes:
                    strategies.append({"name": strategy, "type": "class", "status": "defined"})
                for strategy in strategy_functions:
                    strategies.append({"name": strategy, "type": "function", "status": "defined"})
                    
        except Exception as e:
            strategies.append({"error": f"Failed to read meta intelligence: {str(e)}"})
        
        return strategies
    
    def _get_positions(self):
        """Get current trading positions from state"""
        positions = []
        try:
            # Check SQLite database for positions
            sqlite_db = self.db_paths["sqlite_db"]
            if sqlite_db.exists():
                import sqlite3
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Check if positions table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='positions'")
                if cursor.fetchone():
                    cursor.execute("SELECT * FROM positions ORDER BY timestamp DESC LIMIT 10")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute("PRAGMA table_info(positions)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    for row in rows:
                        position = dict(zip(columns, row))
                        positions.append(position)
                        
                conn.close()
                
        except Exception as e:
            positions.append({"error": f"Failed to read positions: {str(e)}"})
        
        return positions
    
    def _get_risk_config(self):
        """Get risk management parameters"""
        risk_config = {}
        try:
            # Check risk defaults
            risk_defaults_file = self.root_path / "config" / "risk_defaults.json"
            if risk_defaults_file.exists():
                with open(risk_defaults_file, 'r') as f:
                    risk_config = json.load(f)
            
            # Check main config for risk settings
            config_file = self.critical_files["config"]
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'risk' in config:
                        risk_config.update(config['risk'])
                        
        except Exception as e:
            risk_config["error"] = f"Failed to read risk config: {str(e)}"
            
        return risk_config
    
    def _get_recent_trades(self):
        """Get recent trading activity"""
        trades = []
        try:
            # Check SQLite database for trades
            sqlite_db = self.db_paths["sqlite_db"]
            if sqlite_db.exists():
                import sqlite3
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Check if trades table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
                if cursor.fetchone():
                    cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 20")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute("PRAGMA table_info(trades)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    for row in rows:
                        trade = dict(zip(columns, row))
                        trades.append(trade)
                        
                conn.close()
                
        except Exception as e:
            trades.append({"error": f"Failed to read trades: {str(e)}"})
        
        return trades
    
    def _get_signal_history(self):
        """Get recent trading signals"""
        signals = []
        try:
            # Check SQLite database for signals
            sqlite_db = self.db_paths["sqlite_db"]
            if sqlite_db.exists():
                import sqlite3
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Check if signals table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
                if cursor.fetchone():
                    cursor.execute("SELECT * FROM signals ORDER BY timestamp DESC LIMIT 50")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute("PRAGMA table_info(signals)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    for row in rows:
                        signal = dict(zip(columns, row))
                        signals.append(signal)
                        
                conn.close()
                
        except Exception as e:
            signals.append({"error": f"Failed to read signals: {str(e)}"})
        
        return signals
    
    def _get_pnl_summary(self):
        """Get profit and loss summary"""
        pnl = {}
        try:
            # Check SQLite database for PnL data
            sqlite_db = self.db_paths["sqlite_db"]
            if sqlite_db.exists():
                import sqlite3
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Check if pnl table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pnl'")
                if cursor.fetchone():
                    cursor.execute("SELECT * FROM pnl ORDER BY timestamp DESC LIMIT 1")
                    row = cursor.fetchone()
                    
                    if row:
                        # Get column names
                        cursor.execute("PRAGMA table_info(pnl)")
                        columns = [column[1] for column in cursor.fetchall()]
                        pnl = dict(zip(columns, row))
                        
                conn.close()
                
        except Exception as e:
            pnl["error"] = f"Failed to read PnL: {str(e)}"
        
        return pnl
    
    def _get_market_data_status(self):
        """Get current market data status"""
        status = {}
        try:
            # Check latest market data
            latest_data_file = self.db_paths["latest_data"]
            if latest_data_file.exists():
                with open(latest_data_file, 'r') as f:
                    data = json.load(f)
                    
                status["last_update"] = data.get('received_at', 'Unknown')
                status["symbol"] = data.get('symbol', 'Unknown')
                status["last_price"] = data.get('close', 'Unknown')
                status["volume"] = data.get('volume', 'Unknown')
                
                # Calculate data age
                if 'received_at' in data:
                    try:
                        received_time = datetime.fromisoformat(data['received_at'].replace('Z', '+00:00'))
                        if received_time.tzinfo:
                            received_time = received_time.replace(tzinfo=None)
                        age_seconds = (datetime.now() - received_time).total_seconds()
                        status["data_age_seconds"] = age_seconds
                        status["data_fresh"] = age_seconds < 60
                    except:
                        status["data_age_seconds"] = "Unknown"
                        status["data_fresh"] = False
                        
        except Exception as e:
            status["error"] = f"Failed to read market data: {str(e)}"
        
        return status
    
    def auto_detect_problem_type(self) -> ProblemType:
        """Automatically detect the most likely problem type"""
        if not self.detected_issues:
            return ProblemType.UNKNOWN
        
        # Prioritize by severity and type
        high_severity_issues = [i for i in self.detected_issues if i.severity == "HIGH"]
        if high_severity_issues:
            return high_severity_issues[0].problem_type
        
        medium_severity_issues = [i for i in self.detected_issues if i.severity == "MEDIUM"]
        if medium_severity_issues:
            return medium_severity_issues[0].problem_type
        
        return self.detected_issues[0].problem_type
    
    def get_system_overview(self) -> str:
        """Generate comprehensive system overview"""
        overview = []
        overview.append("# MinhOS System Architecture Overview")
        overview.append("")
        
        # System status
        overview.append("## System Status")
        if self.detected_issues:
            overview.append(f"⚠️  **{len(self.detected_issues)} issues detected**")
            for issue in self.detected_issues[:3]:  # Show top 3 issues
                overview.append(f"- {issue.severity}: {issue.description}")
        else:
            overview.append("✅ No issues detected")
        
        overview.append("")
        
        # Service architecture
        overview.append("## Service Architecture")
        overview.append("""
MinhOS v2 Trading System Components:

### Core Services (Startup Order):
1. **Backend Study** (port 8765) - Sierra Chart Integration
   - Primary data ingestion from Sierra Chart files
   - HTTP API for market data
   - Data validation and enhancement
   - Dependencies: None (foundation service)

2. **Market Data Watcher** (background) - File System Monitor
   - Monitors Sierra Chart file changes
   - Resilient data ingestion
   - Dependencies: Backend Study

3. **WebSocket Server** (port 9001) - Real-time Data Hub
   - Real-time data distribution
   - Chat and notification system
   - Health check endpoint (port 9002)
   - Dependencies: Backend Study

4. **HTTP Server** (port 8000) - API Layer
   - REST API endpoints
   - Trading logic and commands
   - Dependencies: Backend Study

5. **Dashboard** (port 8888) - User Interface
   - Web-based trading interface
   - Real-time market data display
   - AI analysis interface
   - Dependencies: WebSocket, HTTP Server

### Intelligence Layer:
- **AI Brain Service** - Pattern analysis and signal generation
- **Trading Copilot** - Trading decision assistance
- **Pattern Learner** - Market pattern recognition
- **Risk Manager** - Risk assessment and controls
- **Autonomous Guardian** - System monitoring and healing

### Data Flow:
```
Sierra Chart Files → Backend Study → State Manager → WebSocket → Dashboard
                           ↓              ↓           ↓
                      Database       Event Bus    Real-time UI
```

### Configuration Management:
- **config.yaml** - Main system configuration
- **SYSTEM_TRUTH.json** - Runtime system state
- **src/minh/core/config_manager.py** - Configuration validation
- **core/minhos_fundamental_truths.py** - System truth enforcement
        """)
        
        return "\\n".join(overview)
    
    def get_data_flow_diagram(self) -> str:
        """Generate ASCII data flow diagram"""
        return """
## Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sierra Chart  │    │  Market Data     │    │  Backend Study  │
│   Files         │───▶│  Watcher         │───▶│  (Port 8765)    │
│ (C:/SierraChart │    │  (File Monitor)  │    │  Enhancement    │
│  /Data/*.json)  │    │                  │    │  & Validation   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   WebSocket      │    │  State Manager  │
│   (Port 8888)   │◀───│   Server         │◀───│  (SQLite DB)    │
│   Real-time UI  │    │   (Port 9001)    │    │  Event Bus      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Server   │    │   AI Brain       │    │  Risk Manager   │
│   (Port 8000)   │◀───│   Service        │◀───│  Trading Logic  │
│   API Layer     │    │   Intelligence   │    │  Safety         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Data Formats:

**Market Data JSON:**
```json
{
  "symbol": "NQ",
  "close": 21850.0,
  "bid": 21849.5,
  "ask": 21850.5,
  "volume": 12345,
  "timestamp": "2025-01-17T10:30:00Z",
  "data_source": "sierra_chart",
  "received_at": "2025-01-17T10:30:00.150Z"
}
```

**WebSocket Message:**
```json
{
  "type": "market_data",
  "data": {...},
  "timestamp": "2025-01-17T10:30:00Z",
  "sequence": 1234
}
```
        """
    
    def get_service_dependencies(self) -> str:
        """Generate service dependency graph"""
        return """
## Service Dependencies

```
Backend Study (8765) ── Foundation Service
├── Market Data Watcher ── File System Monitor
├── HTTP Server (8000) ── API Layer
├── WebSocket Server (9001) ── Real-time Hub
└── Dashboard (8888) ── User Interface
    └── Browser Auto-Launch

Intelligence Layer:
├── AI Brain Service ── Pattern Analysis
├── Trading Copilot ── Decision Support
├── Pattern Learner ── Market Learning
├── Risk Manager ── Safety Controls
└── Autonomous Guardian ── System Health
```

### Startup Sequence:
1. **Backend Study** must start first (foundation)
2. **Market Data Watcher** starts in background
3. **WebSocket Server** starts after Backend Study
4. **HTTP Server** starts after Backend Study
5. **Dashboard** starts after WebSocket + HTTP
6. **Browser** auto-launches after Dashboard health check

### Failure Impact:
- **Backend Study Down**: Entire system offline
- **WebSocket Down**: No real-time updates
- **HTTP Server Down**: No API access
- **Dashboard Down**: No user interface
- **Data Watcher Down**: No file-based data ingestion
        """
    
    def get_configuration_analysis(self) -> str:
        """Analyze and document configuration"""
        analysis = []
        analysis.append("## Configuration Analysis")
        analysis.append("")
        
        # Check config file
        config_file = self.critical_files["config"]
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                analysis.append("### Current Configuration:")
                analysis.append("```yaml")
                analysis.append(yaml.dump(config, default_flow_style=False))
                analysis.append("```")
                
                # Port analysis
                analysis.append("### Port Configuration Analysis:")
                if 'ports' in config:
                    for service, expected_port in self.standard_ports.items():
                        actual_port = config['ports'].get(service, 'NOT SET')
                        if actual_port == expected_port:
                            analysis.append(f"✅ {service}: {actual_port}")
                        else:
                            analysis.append(f"❌ {service}: {actual_port} (expected {expected_port})")
                
                # Sierra Chart paths
                analysis.append("### Sierra Chart Integration:")
                if 'sierra_chart' in config:
                    for key, path in config['sierra_chart'].items():
                        analysis.append(f"- {key}: {path}")
                
            except Exception as e:
                analysis.append(f"❌ Configuration file error: {e}")
        else:
            analysis.append("❌ Configuration file not found")
        
        analysis.append("")
        analysis.append("### Configuration Files:")
        analysis.append("- **config.yaml** - Main system configuration")
        analysis.append("- **src/config.py** - Sierra Chart file paths")
        analysis.append("- **src/minh/core/config_manager.py** - Configuration management")
        analysis.append("- **core/minhos_fundamental_truths.py** - Truth enforcement")
        
        return "\\n".join(analysis)
    
    def get_diagnostic_info(self) -> str:
        """Get comprehensive diagnostic information"""
        diagnostics = []
        diagnostics.append("## System Diagnostics")
        diagnostics.append("")
        
        # System information
        diagnostics.append("### System Information:")
        diagnostics.append(f"- Python Version: {sys.version}")
        diagnostics.append(f"- Working Directory: {os.getcwd()}")
        diagnostics.append(f"- System Time: {datetime.now()}")
        
        # Process information
        diagnostics.append("")
        diagnostics.append("### Process Information:")
        if PSUTIL_AVAILABLE:
            try:
                # Check for MinhOS processes
                minhos_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info['cmdline']
                        if cmdline and any('minh' in str(cmd).lower() for cmd in cmdline):
                            minhos_processes.append(f"PID {proc.info['pid']}: {' '.join(cmdline)}")
                    except:
                        pass
                
                if minhos_processes:
                    diagnostics.append("**MinhOS Processes:**")
                    for proc in minhos_processes:
                        diagnostics.append(f"- {proc}")
                else:
                    diagnostics.append("- No MinhOS processes detected")
            except Exception as e:
                diagnostics.append(f"- Error checking processes: {e}")
        else:
            diagnostics.append("- Process checking not available (psutil not installed)")
        
        # Port status with detailed health info
        diagnostics.append("")
        diagnostics.append("### Service Health Status:")
        if "detailed_health" in self.system_state:
            for service, health_info in self.system_state["detailed_health"].items():
                port = health_info["port"]
                listening = health_info["port_listening"]
                responding = health_info["service_responding"]
                response_time = health_info["response_time_ms"]
                error = health_info["error"]
                
                # Create status string
                if listening and responding:
                    status = f"✅ HEALTHY"
                    if response_time:
                        status += f" ({response_time:.1f}ms)"
                elif listening and not responding:
                    status = f"⚠️ LISTENING BUT NOT RESPONDING"
                    if error:
                        status += f" ({error})"
                else:
                    status = "❌ NOT LISTENING"
                
                diagnostics.append(f"- {service} (port {port}): {status}")
        else:
            # Fallback to basic port checking
            for service, port in self.standard_ports.items():
                listening = self._is_port_listening(port)
                status = "✅ LISTENING" if listening else "❌ NOT LISTENING"
                diagnostics.append(f"- {service} (port {port}): {status}")
        
        # File system check
        diagnostics.append("")
        diagnostics.append("### Critical Files:")
        for name, path in self.critical_files.items():
            exists = path.exists()
            status = "✅ EXISTS" if exists else "❌ MISSING"
            diagnostics.append(f"- {name}: {status} ({path})")
        
        # Database check
        diagnostics.append("")
        diagnostics.append("### Database Status:")
        for name, path in self.db_paths.items():
            exists = path.exists()
            size = ""
            if exists:
                try:
                    size = f" ({path.stat().st_size} bytes)"
                except:
                    pass
            status = "✅ EXISTS" if exists else "❌ MISSING"
            diagnostics.append(f"- {name}: {status}{size}")
        
        return "\\n".join(diagnostics)
    
    def get_recent_errors(self, max_errors: int = 20) -> str:
        """Get recent error information"""
        errors = []
        errors.append("## Recent Errors and Issues")
        errors.append("")
        
        # Check diagnostic log
        diagnostic_log = self.log_paths["diagnostic"]
        if diagnostic_log.exists():
            try:
                with open(diagnostic_log, 'r') as f:
                    lines = f.readlines()
                
                # Find recent errors
                error_patterns = ["ERROR", "FAILED", "EXCEPTION", "CRITICAL", "FATAL"]
                recent_errors = []
                
                for line in reversed(lines):  # Start from most recent
                    if any(pattern in line.upper() for pattern in error_patterns):
                        recent_errors.append(line.strip())
                        if len(recent_errors) >= max_errors:
                            break
                
                if recent_errors:
                    errors.append("### Recent Errors from Diagnostic Log:")
                    errors.append("```")
                    for error in reversed(recent_errors):  # Show chronologically
                        errors.append(error)
                    errors.append("```")
                else:
                    errors.append("✅ No recent errors found in diagnostic log")
                    
            except Exception as e:
                errors.append(f"❌ Error reading diagnostic log: {e}")
        else:
            errors.append("❌ Diagnostic log not found")
        
        # Show detected issues
        if self.detected_issues:
            errors.append("")
            errors.append("### Auto-Detected Issues:")
            for issue in self.detected_issues:
                errors.append(f"**{issue.severity}**: {issue.description}")
                errors.append(f"- Affected services: {', '.join(issue.affected_services)}")
                errors.append(f"- Problem type: {issue.problem_type.value}")
                if issue.diagnostics:
                    errors.append(f"- Diagnostics: {json.dumps(issue.diagnostics, indent=2)}")
                errors.append("")
        
        return "\\n".join(errors)
    
    def get_performance_metrics(self) -> str:
        """Get system performance metrics"""
        metrics = []
        metrics.append("## Performance Metrics")
        metrics.append("")
        
        # Get comprehensive performance data
        perf_data = self._collect_performance_metrics()
        
        if perf_data.get("system"):
            sys_metrics = perf_data["system"]
            metrics.append("### System Resources:")
            metrics.append(f"- **CPU Usage**: {sys_metrics.get('cpu_percent', 'N/A')}%")
            metrics.append(f"- **Memory Usage**: {sys_metrics.get('memory_percent', 'N/A')}% ({sys_metrics.get('memory_used_gb', 'N/A')}GB / {sys_metrics.get('memory_total_gb', 'N/A')}GB)")
            metrics.append(f"- **Disk Usage**: {sys_metrics.get('disk_percent', 'N/A')}% ({sys_metrics.get('disk_used_gb', 'N/A')}GB / {sys_metrics.get('disk_total_gb', 'N/A')}GB)")
            
            if sys_metrics.get('network_io'):
                net_io = sys_metrics['network_io']
                metrics.append(f"- **Network I/O**: {net_io.get('bytes_sent', 0)} sent, {net_io.get('bytes_recv', 0)} received")
            
            if sys_metrics.get('disk_io'):
                disk_io = sys_metrics['disk_io']
                metrics.append(f"- **Disk I/O**: {disk_io.get('read_bytes', 0)} read, {disk_io.get('write_bytes', 0)} written")
        
        # Per-service metrics
        if perf_data.get("services"):
            metrics.append("")
            metrics.append("### Per-Service Performance:")
            for service, service_metrics in perf_data["services"].items():
                metrics.append(f"**{service}:**")
                metrics.append(f"- CPU: {service_metrics.get('cpu_percent', 'N/A')}%")
                metrics.append(f"- Memory: {service_metrics.get('memory_mb', 'N/A')}MB")
                metrics.append(f"- Threads: {service_metrics.get('threads', 'N/A')}")
                metrics.append(f"- Open Files: {service_metrics.get('open_files', 'N/A')}")
                metrics.append("")
        
        # Trading-specific metrics
        if perf_data.get("trading"):
            trading_metrics = perf_data["trading"]
            metrics.append("### Trading Performance:")
            metrics.append(f"- **Data Latency**: {trading_metrics.get('data_latency_ms', 'N/A')}ms")
            metrics.append(f"- **Order Execution**: {trading_metrics.get('order_execution_ms', 'N/A')}ms")
            metrics.append(f"- **Signal Processing**: {trading_metrics.get('signal_processing_ms', 'N/A')}ms")
        
        # Network status
        if PSUTIL_AVAILABLE:
            try:
                connections = psutil.net_connections()
                listening_ports = [conn.laddr.port for conn in connections if conn.status == 'LISTEN']
                minhos_ports = [port for port in listening_ports if port in self.standard_ports.values()]
                
                metrics.append("")
                metrics.append("### Network Status:")
                metrics.append(f"- **Total Listening Ports**: {len(listening_ports)}")
                metrics.append(f"- **MinhOS Ports Active**: {len(minhos_ports)}/{len(self.standard_ports)}")
                
            except Exception as e:
                metrics.append(f"❌ Error getting network status: {e}")
        
        # Data freshness
        latest_data_file = self.db_paths["latest_data"]
        if latest_data_file.exists():
            try:
                with open(latest_data_file, 'r') as f:
                    data = json.load(f)
                
                if 'received_at' in data:
                    received_time = datetime.fromisoformat(data['received_at'].replace('Z', '+00:00'))
                    if received_time.tzinfo:
                        received_time = received_time.replace(tzinfo=None)
                    
                    age_seconds = (datetime.now() - received_time).total_seconds()
                    
                    metrics.append("")
                    metrics.append("### Data Freshness:")
                    metrics.append(f"- **Last Market Data**: {int(age_seconds)}s ago")
                    metrics.append(f"- **Data Status**: {'✅ Fresh' if age_seconds < 60 else '❌ Stale'}")
                    
            except Exception as e:
                metrics.append(f"❌ Error checking data freshness: {e}")
        
        return "\\n".join(metrics)
    
    def _collect_performance_metrics(self):
        """Collect system performance metrics"""
        metrics = {}
        
        # Per-service metrics
        services = {}
        if PSUTIL_AVAILABLE:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info['cmdline']
                        if cmdline:
                            cmdline_str = ' '.join(cmdline)
                            # Check if this is a MinhOS process
                            for service_name in self.standard_ports.keys():
                                if service_name in cmdline_str.lower() or any(service_name in str(cmd).lower() for cmd in cmdline):
                                    process = psutil.Process(proc.info['pid'])
                                    services[service_name] = {
                                        "pid": proc.info['pid'],
                                        "cpu_percent": process.cpu_percent(),
                                        "memory_mb": process.memory_info().rss / 1024 / 1024,
                                        "threads": process.num_threads(),
                                        "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0
                                    }
                                    break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except Exception as e:
                logger.error(f"Error collecting per-service metrics: {e}")
        
        metrics["services"] = services
        
        # System-wide metrics
        system_metrics = {}
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_metrics = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": memory.percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "memory_total_gb": memory.total / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_used_gb": disk.used / (1024**3),
                    "disk_total_gb": disk.total / (1024**3)
                }
                
                # Network and disk I/O
                try:
                    system_metrics["disk_io"] = psutil.disk_io_counters()._asdict()
                    system_metrics["network_io"] = psutil.net_io_counters()._asdict()
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
        
        metrics["system"] = system_metrics
        
        # Trading-specific metrics
        trading_metrics = {
            "data_latency_ms": self._measure_data_latency(),
            "order_execution_ms": self._get_order_execution_time(),
            "signal_processing_ms": self._get_signal_processing_time()
        }
        
        metrics["trading"] = trading_metrics
        
        return metrics
    
    def _measure_data_latency(self):
        """Measure data latency from Sierra Chart to system"""
        try:
            # Check the age of the latest market data
            latest_data_file = self.db_paths["latest_data"]
            if latest_data_file.exists():
                with open(latest_data_file, 'r') as f:
                    data = json.load(f)
                    
                if 'received_at' in data:
                    received_time = datetime.fromisoformat(data['received_at'].replace('Z', '+00:00'))
                    if received_time.tzinfo:
                        received_time = received_time.replace(tzinfo=None)
                    
                    age_seconds = (datetime.now() - received_time).total_seconds()
                    return age_seconds * 1000  # Convert to milliseconds
        except:
            pass
        
        return None
    
    def _get_order_execution_time(self):
        """Get average order execution time"""
        try:
            # Check recent trades for execution time data
            sqlite_db = self.db_paths["sqlite_db"]
            if sqlite_db.exists():
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Check if trades table has execution time data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
                if cursor.fetchone():
                    cursor.execute("SELECT execution_time_ms FROM trades WHERE execution_time_ms IS NOT NULL ORDER BY timestamp DESC LIMIT 10")
                    rows = cursor.fetchall()
                    
                    if rows:
                        avg_execution_time = sum(row[0] for row in rows) / len(rows)
                        conn.close()
                        return avg_execution_time
                        
                conn.close()
        except:
            pass
        
        return None
    
    def _get_signal_processing_time(self):
        """Get average signal processing time"""
        try:
            # Check recent signals for processing time data
            sqlite_db = self.db_paths["sqlite_db"]
            if sqlite_db.exists():
                conn = sqlite3.connect(sqlite_db)
                cursor = conn.cursor()
                
                # Check if signals table has processing time data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
                if cursor.fetchone():
                    cursor.execute("SELECT processing_time_ms FROM signals WHERE processing_time_ms IS NOT NULL ORDER BY timestamp DESC LIMIT 20")
                    rows = cursor.fetchall()
                    
                    if rows:
                        avg_processing_time = sum(row[0] for row in rows) / len(rows)
                        conn.close()
                        return avg_processing_time
                        
                conn.close()
        except:
            pass
        
        return None
    
    def get_error_analysis(self, hours: int = 24):
        """Analyze errors across all services with correlation"""
        errors = {
            "by_service": self._collect_service_errors(hours),
            "by_severity": self._group_errors_by_severity(),
            "patterns": self._identify_error_patterns(),
            "correlations": self._find_error_correlations(),
            "root_causes": self._suggest_root_causes()
        }
        return errors
    
    def _collect_service_errors(self, hours: int):
        """Collect errors from all services within specified hours"""
        service_errors = {}
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Check diagnostic log
        diagnostic_log = self.log_paths["diagnostic"]
        if diagnostic_log.exists():
            try:
                with open(diagnostic_log, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if any(pattern in line.upper() for pattern in ['ERROR', 'EXCEPTION', 'FAILED', 'CRITICAL']):
                        # Try to extract service name from line
                        service_name = "unknown"
                        for service in self.standard_ports.keys():
                            if service in line.lower():
                                service_name = service
                                break
                        
                        if service_name not in service_errors:
                            service_errors[service_name] = []
                        service_errors[service_name].append(line.strip())
                        
            except Exception as e:
                logger.error(f"Error reading diagnostic log: {e}")
        
        # Check individual service logs
        logs_dir = self.root_path / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                try:
                    service_name = log_file.stem
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        if any(pattern in line.upper() for pattern in ['ERROR', 'EXCEPTION', 'FAILED', 'CRITICAL']):
                            if service_name not in service_errors:
                                service_errors[service_name] = []
                            service_errors[service_name].append(line.strip())
                            
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
        
        return service_errors
    
    def _group_errors_by_severity(self):
        """Group errors by severity level"""
        severity_groups = {
            "CRITICAL": [],
            "ERROR": [],
            "WARNING": [],
            "INFO": []
        }
        
        # Analyze recent errors from detected issues
        for issue in self.detected_issues:
            if issue.severity == "HIGH":
                severity_groups["CRITICAL"].append(issue.description)
            elif issue.severity == "MEDIUM":
                severity_groups["ERROR"].append(issue.description)
            else:
                severity_groups["WARNING"].append(issue.description)
        
        return severity_groups
    
    def _identify_error_patterns(self):
        """Look for recurring error patterns"""
        patterns = {
            "recurring_errors": [],
            "time_based_patterns": [],
            "cascade_failures": []
        }
        
        # Check for recurring error messages
        error_counts = {}
        for issue in self.detected_issues:
            error_key = issue.description.lower()
            # Normalize error message for pattern matching
            normalized = ' '.join(error_key.split()[:5])  # First 5 words
            
            if normalized in error_counts:
                error_counts[normalized] += 1
            else:
                error_counts[normalized] = 1
        
        # Find patterns that occur more than once
        for error_pattern, count in error_counts.items():
            if count > 1:
                patterns["recurring_errors"].append({
                    "pattern": error_pattern,
                    "count": count
                })
        
        # Check for cascade failures (multiple services failing around the same time)
        if len(self.detected_issues) > 1:
            service_failures = []
            for issue in self.detected_issues:
                if issue.problem_type in [ProblemType.SERVICE_DOWN, ProblemType.CONNECTIVITY]:
                    service_failures.extend(issue.affected_services)
            
            if len(service_failures) > 1:
                patterns["cascade_failures"].append({
                    "affected_services": service_failures,
                    "description": "Multiple services failing simultaneously"
                })
        
        return patterns
    
    def _find_error_correlations(self):
        """Find correlations between different types of errors"""
        correlations = []
        
        # Check if data staleness correlates with service issues
        data_issues = [i for i in self.detected_issues if i.problem_type == ProblemType.DATA_STALE]
        service_issues = [i for i in self.detected_issues if i.problem_type == ProblemType.SERVICE_DOWN]
        
        if data_issues and service_issues:
            correlations.append({
                "type": "data_service_correlation",
                "description": "Data staleness may be caused by service failures",
                "data_issues": len(data_issues),
                "service_issues": len(service_issues)
            })
        
        # Check if configuration issues correlate with service problems
        config_issues = [i for i in self.detected_issues if i.problem_type == ProblemType.CONFIGURATION]
        if config_issues and service_issues:
            correlations.append({
                "type": "config_service_correlation",
                "description": "Configuration problems may be causing service failures",
                "config_issues": len(config_issues),
                "service_issues": len(service_issues)
            })
        
        return correlations
    
    def _suggest_root_causes(self):
        """Suggest potential root causes based on error analysis"""
        root_causes = []
        
        # Analyze issue patterns
        high_severity_issues = [i for i in self.detected_issues if i.severity == "HIGH"]
        
        if high_severity_issues:
            for issue in high_severity_issues:
                if issue.problem_type == ProblemType.SERVICE_DOWN:
                    root_causes.append({
                        "cause": "Service startup failure",
                        "description": f"Services {', '.join(issue.affected_services)} are not running",
                        "suggested_actions": [
                            "Check service logs for startup errors",
                            "Verify port availability",
                            "Check configuration files",
                            "Restart services in correct order"
                        ]
                    })
                elif issue.problem_type == ProblemType.CONFIGURATION:
                    root_causes.append({
                        "cause": "Configuration error",
                        "description": issue.description,
                        "suggested_actions": [
                            "Validate configuration files",
                            "Check port assignments",
                            "Verify file paths",
                            "Review recent configuration changes"
                        ]
                    })
        
        # Check for resource issues
        performance_issues = [i for i in self.detected_issues if i.problem_type == ProblemType.PERFORMANCE]
        if performance_issues:
            root_causes.append({
                "cause": "Resource constraints",
                "description": "System resources may be limiting performance",
                "suggested_actions": [
                    "Monitor CPU and memory usage",
                    "Check disk space",
                    "Review process resource consumption",
                    "Consider scaling or optimization"
                ]
            })
        
        return root_causes
    
    def get_business_logic_summary(self):
        """Extract and summarize trading logic"""
        summary = {
            "trading_strategies": self._extract_strategy_logic(),
            "risk_rules": self._extract_risk_rules(),
            "signal_generation": self._extract_signal_logic(),
            "execution_logic": self._extract_execution_logic(),
            "data_processing": self._extract_data_pipeline()
        }
        return summary
    
    def _extract_strategy_logic(self):
        """Extract trading strategy logic from code"""
        strategies = []
        
        # Check meta intelligence trading file
        meta_file = self.root_path / "core" / "ai" / "meta_intelligence_trading.py"
        if meta_file.exists():
            strategies.append(self._analyze_file_for_logic(meta_file, "trading_strategy"))
        
        # Check trading copilot
        copilot_file = self.root_path / "services" / "trading_copilot.py"
        if copilot_file.exists():
            strategies.append(self._analyze_file_for_logic(copilot_file, "trading_copilot"))
        
        return strategies
    
    def _extract_risk_rules(self):
        """Extract risk management rules"""
        risk_rules = []
        
        # Check risk manager
        risk_file = self.root_path / "services" / "risk_manager.py"
        if risk_file.exists():
            risk_rules.append(self._analyze_file_for_logic(risk_file, "risk_management"))
        
        return risk_rules
    
    def _extract_signal_logic(self):
        """Extract signal generation logic"""
        signals = []
        
        # Check AI brain service
        ai_brain_file = self.root_path / "services" / "ai_brain_service.py"
        if ai_brain_file.exists():
            signals.append(self._analyze_file_for_logic(ai_brain_file, "signal_generation"))
        
        return signals
    
    def _extract_execution_logic(self):
        """Extract execution logic"""
        execution = []
        
        # Check HTTP server for execution endpoints
        http_server_file = self.root_path / "services" / "http_server.py"
        if http_server_file.exists():
            execution.append(self._analyze_file_for_logic(http_server_file, "execution"))
        
        return execution
    
    def _extract_data_pipeline(self):
        """Extract data processing pipeline"""
        pipeline = []
        
        # Check backend study
        backend_file = self.root_path / "services" / "backend_study_enhanced.py"
        if backend_file.exists():
            pipeline.append(self._analyze_file_for_logic(backend_file, "data_processing"))
        
        # Check market data watcher
        watcher_file = self.root_path / "services" / "market_data_watcher.py"
        if watcher_file.exists():
            pipeline.append(self._analyze_file_for_logic(watcher_file, "data_monitoring"))
        
        return pipeline
    
    def _analyze_file_for_logic(self, file_path: Path, logic_type: str):
        """Analyze a file for specific business logic"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # Extract key functions and classes
            functions = re.findall(r'def\s+(\w+)', content)
            classes = re.findall(r'class\s+(\w+)', content)
            
            # Look for specific patterns based on logic type
            patterns = []
            if logic_type == "trading_strategy":
                patterns = re.findall(r'strategy|signal|buy|sell|trade', content, re.IGNORECASE)
            elif logic_type == "risk_management":
                patterns = re.findall(r'risk|limit|stop|position|exposure', content, re.IGNORECASE)
            elif logic_type == "signal_generation":
                patterns = re.findall(r'signal|indicator|pattern|analysis', content, re.IGNORECASE)
            elif logic_type == "execution":
                patterns = re.findall(r'execute|order|trade|position', content, re.IGNORECASE)
            elif logic_type == "data_processing":
                patterns = re.findall(r'process|parse|validate|transform', content, re.IGNORECASE)
            
            return {
                "file": str(file_path.relative_to(self.root_path)),
                "logic_type": logic_type,
                "functions": functions[:10],  # First 10 functions
                "classes": classes,
                "pattern_matches": len(patterns),
                "key_patterns": list(set(patterns))[:10]  # First 10 unique patterns
            }
            
        except Exception as e:
            return {
                "file": str(file_path.relative_to(self.root_path)),
                "logic_type": logic_type,
                "error": str(e)
            }
    
    def generate_smart_context(self, focus_area: str = "auto", problem_description: str = None) -> str:
        """
        Generate intelligent context based on detected issues or specified focus area
        
        Args:
            focus_area: Area to focus on or 'auto' for automatic detection
            problem_description: Optional description of the specific problem
        
        Returns:
            Comprehensive context string
        """
        context = []
        
        # Header
        context.append("# MinhOS Enhanced AI Context")
        context.append(f"Generated: {datetime.now().isoformat()}")
        context.append("")
        
        # Problem description
        if problem_description:
            context.append("## Problem Description")
            context.append(problem_description)
            context.append("")
        
        # Auto-detect focus area if requested
        if focus_area == "auto":
            detected_type = self.auto_detect_problem_type()
            focus_area = detected_type.value
            context.append(f"## Auto-Detected Focus Area: {focus_area}")
            context.append("")
        
        # Always include system overview
        context.append(self.get_system_overview())
        context.append("")
        
        # Focus-specific context
        if focus_area in ["startup_failure", "startup", "service_down"]:
            context.append("## Startup and Service Management")
            context.append(self.get_service_dependencies())
            context.append("")
            context.append("### Critical Startup Files:")
            self._add_file_content(context, "minh.py", "Main entry point")
            self._add_file_content(context, "src/minh/command_parser.py", "Command parsing and execution")
            self._add_file_content(context, "services/service_orchestrator.py", "Service management", max_lines=100)
            
        elif focus_area in ["data_stale", "data_flow", "connectivity"]:
            context.append("## Data Flow and Connectivity")
            context.append(self.get_data_flow_diagram())
            context.append("")
            context.append("### Data Processing Files:")
            self._add_file_content(context, "services/backend_study_enhanced.py", "Market data ingestion", max_lines=100)
            self._add_file_content(context, "services/market_data_watcher.py", "File system monitoring", max_lines=50)
            self._add_file_content(context, "services/state_manager.py", "State management", max_lines=50)
            
        elif focus_area in ["configuration", "config"]:
            context.append(self.get_configuration_analysis())
            context.append("")
            context.append("### Configuration Files:")
            self._add_file_content(context, "config.yaml", "Main configuration")
            self._add_file_content(context, "src/config.py", "Sierra Chart paths")
            self._add_file_content(context, "src/minh/core/config_manager.py", "Configuration management", max_lines=100)
            
        elif focus_area in ["performance", "resources"]:
            context.append(self.get_performance_metrics())
            context.append("")
            
            # Add error analysis for performance issues
            try:
                error_analysis = self.get_error_analysis()
                context.append("### Error Analysis:")
                
                # Show root causes related to performance
                if error_analysis['root_causes']:
                    context.append("**Potential Root Causes:**")
                    for cause in error_analysis['root_causes']:
                        context.append(f"- {cause['cause']}: {cause['description']}")
                
                # Show error patterns
                if error_analysis['patterns']['recurring_errors']:
                    context.append("**Recurring Error Patterns:**")
                    for pattern in error_analysis['patterns']['recurring_errors']:
                        context.append(f"- {pattern['pattern']} (occurred {pattern['count']} times)")
                
                context.append("")
                
            except Exception as e:
                context.append(f"❌ Error getting performance analysis: {e}")
                context.append("")
            
            context.append("### Performance-Related Files:")
            self._add_file_content(context, "services/autonomous_guardian.py", "System monitoring", max_lines=50)
            self._add_file_content(context, "services/unified_monitor.py", "Performance monitoring", max_lines=50)
            
        elif focus_area in ["trading", "ai_analysis"]:
            context.append("## Trading and AI Analysis")
            
            # Add trading context
            try:
                trading_context = self.get_trading_context()
                context.append("### Current Trading State:")
                context.append(f"**Active Strategies**: {len(trading_context['active_strategies'])}")
                context.append(f"**Current Positions**: {len(trading_context['current_positions'])}")
                context.append(f"**Recent Trades**: {len(trading_context['recent_trades'])}")
                context.append(f"**Recent Signals**: {len(trading_context['signal_history'])}")
                
                # Market data status
                market_status = trading_context['market_data_status']
                if market_status:
                    data_fresh = market_status.get('data_fresh', False)
                    context.append(f"**Market Data**: {'✅ Fresh' if data_fresh else '❌ Stale'}")
                    if 'last_price' in market_status:
                        context.append(f"**Last Price**: {market_status['last_price']}")
                
                context.append("")
                
                # Add business logic summary
                business_logic = self.get_business_logic_summary()
                context.append("### Business Logic Summary:")
                for logic_type, logic_data in business_logic.items():
                    if logic_data:
                        context.append(f"**{logic_type.replace('_', ' ').title()}**: {len(logic_data)} components")
                
                context.append("")
                
            except Exception as e:
                context.append(f"❌ Error getting trading context: {e}")
                context.append("")
            
            context.append("### Trading Intelligence Files:")
            self._add_file_content(context, "services/ai_brain_service.py", "AI analysis engine")
            self._add_file_content(context, "services/trading_copilot.py", "Trading decisions", max_lines=100)
            self._add_file_content(context, "services/risk_manager.py", "Risk management", max_lines=50)
            self._add_file_content(context, "core/ai/meta_intelligence_trading.py", "Meta intelligence trading", max_lines=100)
            
        elif focus_area == "dashboard":
            context.append("## Dashboard and User Interface")
            context.append("### Dashboard Files:")
            self._add_file_content(context, "dashboard/main.py", "Dashboard entry point")
            self._add_file_content(context, "dashboard/server.py", "Dashboard server")
            self._add_file_content(context, "dashboard/data_manager.py", "Data management")
            
        # Always include diagnostic information
        context.append("")
        context.append(self.get_diagnostic_info())
        context.append("")
        context.append(self.get_recent_errors())
        
        # Include fundamental truths
        context.append("")
        context.append("## MinhOS Fundamental Truths")
        context.append("These are the core principles that govern MinhOS operation:")
        self._add_file_content(context, "core/minhos_fundamental_truths.py", "System truth enforcement", max_lines=100)
        
        return "\\n".join(context)
    
    def _add_file_content(self, context: List[str], file_path: str, description: str, max_lines: int = 200):
        """Add file content to context"""
        full_path = self.root_path / file_path
        
        if full_path.exists():
            context.append(f"### {file_path}")
            context.append(f"*{description}*")
            context.append("```python")
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\\n')
                    
                    if len(lines) > max_lines:
                        context.append('\\n'.join(lines[:max_lines]))
                        context.append(f"\\n... ({len(lines) - max_lines} more lines)")
                    else:
                        context.append(content)
                        
            except Exception as e:
                context.append(f"Error reading file: {e}")
                
            context.append("```")
            context.append("")
        else:
            context.append(f"### {file_path} - FILE NOT FOUND")
            context.append("")
    
    def save_context(self, filename: str = "AI_CONTEXT.md", focus_area: str = "auto", 
                    problem_description: str = None, dry_run: bool = False) -> str:
        """
        Save enhanced context to file
        
        Args:
            filename: Output filename
            focus_area: Focus area for context generation
            problem_description: Optional problem description
            dry_run: If True, don't save file, just return content
        
        Returns:
            Generated context content
        """
        context = self.generate_smart_context(focus_area, problem_description)
        
        if not dry_run:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(context)
                
                print(f"✅ Enhanced AI context saved to {filename}")
                print(f"📊 Context Statistics:")
                print(f"   - Size: {len(context):,} characters")
                print(f"   - Lines: {context.count('\\n'):,}")
                print(f"   - Focus Area: {focus_area}")
                print(f"   - Issues Detected: {len(self.detected_issues)}")
                
                if self.detected_issues:
                    print(f"\\n🔍 Detected Issues:")
                    for issue in self.detected_issues[:3]:  # Show top 3
                        print(f"   - {issue.severity}: {issue.description}")
                
                print(f"\\n📋 Usage Instructions:")
                print(f"   1. Copy the contents of {filename}")
                print(f"   2. Paste into your AI assistant with your question")
                print(f"   3. The context is optimized for your specific situation")
                
            except Exception as e:
                print(f"❌ Error saving context: {e}")
                return context
        
        return context
    
    def list_available_focus_areas(self) -> Dict[str, str]:
        """List all available focus areas with descriptions"""
        return {
            "auto": "Automatically detect the best focus area based on system analysis",
            "startup": "System startup issues and service management",
            "service_down": "Service health and connectivity problems",
            "data_stale": "Market data freshness and data flow issues",
            "connectivity": "Network connectivity and Sierra Chart integration",
            "configuration": "Configuration file issues and validation",
            "performance": "System performance and resource usage",
            "trading": "Trading logic and execution issues",
            "ai_analysis": "AI brain and pattern analysis problems",
            "dashboard": "Dashboard and user interface issues",
            "full_diagnostic": "Complete system diagnostic with all available information"
        }
    
    def get_usage_examples(self) -> str:
        """Get usage examples for the enhanced context generator"""
        return """
# MinhOS Enhanced Context Generator Usage Examples

## Basic Usage:
```bash
# Auto-detect problem and generate context
python "user tool/context_for_ai.py"

# Generate context for specific area
python "user tool/context_for_ai.py" startup
python "user tool/context_for_ai.py" data_flow
python "user tool/context_for_ai.py" configuration

# Include problem description
python "user tool/context_for_ai.py" --problem "Dashboard won't load"
```

## Advanced Usage:
```bash
# Dry run (preview without saving)
python "user tool/context_for_ai.py" --dry-run

# Full diagnostic mode
python "user tool/context_for_ai.py" full_diagnostic

# Custom output file
python "user tool/context_for_ai.py" --output custom_context.md
```

## Available Focus Areas:
- **auto**: Automatically detect the best focus area
- **startup**: System startup and service management
- **data_flow**: Market data processing and connectivity
- **configuration**: Configuration files and validation
- **performance**: System performance and resources
- **trading**: Trading logic and AI analysis
- **dashboard**: User interface and web dashboard
- **full_diagnostic**: Complete system analysis

## Common Scenarios:

### System Won't Start:
```bash
python "user tool/context_for_ai.py" startup --problem "System fails to start"
```

### No Market Data:
```bash
python "user tool/context_for_ai.py" data_flow --problem "No market data updating"
```

### Dashboard Issues:
```bash
python "user tool/context_for_ai.py" dashboard --problem "Dashboard shows errors"
```

### Configuration Problems:
```bash
python "user tool/context_for_ai.py" configuration --problem "Port conflicts"
```

The enhanced context generator will automatically detect system issues and provide relevant context for AI assistance.
        """


def main():
    """Enhanced main function with intelligent context generation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced AI Context Generator for MinhOS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python "user tool/context_for_ai.py"                    # Auto-detect and generate
  python "user tool/context_for_ai.py" startup           # Focus on startup issues
  python "user tool/context_for_ai.py" --dry-run         # Preview without saving
  python "user tool/context_for_ai.py" --problem "..."   # Include problem description
        """
    )
    
    # Enhanced argument parsing
    parser.add_argument('focus', nargs='?', default='auto',
                      help='Focus area (auto, startup, data_flow, configuration, performance, trading, dashboard, full_diagnostic)')
    parser.add_argument('--problem', '-p', type=str,
                      help='Describe the specific problem you are experiencing')
    parser.add_argument('--output', '-o', type=str, default='AI_CONTEXT.md',
                      help='Output filename (default: AI_CONTEXT.md)')
    parser.add_argument('--dry-run', action='store_true',
                      help='Preview context without saving to file')
    parser.add_argument('--list-areas', action='store_true',
                      help='List available focus areas')
    parser.add_argument('--examples', action='store_true',
                      help='Show usage examples')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_areas:
        generator = MinhOSEnhancedContextGenerator()
        areas = generator.list_available_focus_areas()
        print("Available Focus Areas:")
        print("=" * 50)
        for area, description in areas.items():
            print(f"  {area:<20} - {description}")
        return
    
    if args.examples:
        generator = MinhOSEnhancedContextGenerator()
        print(generator.get_usage_examples())
        return
    
    # Generate context
    print("=" * 80)
    print("🧠 MinhOS Enhanced AI Context Generator v2.0")
    print("=" * 80)
    print(f"📍 Focus Area: {args.focus}")
    print(f"🔍 Analyzing system state...")
    
    try:
        generator = MinhOSEnhancedContextGenerator()
        
        # Show detected issues
        if generator.detected_issues:
            print(f"⚠️  Detected {len(generator.detected_issues)} system issues:")
            for issue in generator.detected_issues[:3]:  # Show top 3
                print(f"   - {issue.severity}: {issue.description}")
        else:
            print("✅ No system issues detected")
        
        print(f"📝 Generating context...")
        
        # Generate and save context
        context = generator.save_context(
            filename=args.output,
            focus_area=args.focus,
            problem_description=args.problem,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            print("\\n" + "="*60)
            print("DRY RUN - Preview of generated context:")
            print("="*60)
            print(context[:2000] + "..." if len(context) > 2000 else context)
            print("="*60)
            print(f"Full context would be {len(context):,} characters")
        
    except Exception as e:
        print(f"❌ Error generating context: {e}")
        print("\\nStack trace:")
        traceback.print_exc()
        sys.exit(1)
    
    print("\\n" + "="*80)
    print("✅ Context generation complete!")
    print("="*80)


if __name__ == "__main__":
    main()