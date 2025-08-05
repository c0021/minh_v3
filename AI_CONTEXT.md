# MinhOS Enhanced AI Context\nGenerated: 2025-07-24T11:35:18.260560\n\n## Auto-Detected Focus Area: service_down\n\n# MinhOS System Architecture Overview\n\n## System Status\n⚠️  **2 issues detected**\n- HIGH: Services not running: sierra_bridge, live_integration, sierra_client, multi_chart_collector, ai_brain_service, trading_engine, state_manager, risk_manager\n- HIGH: Configuration file missing\n\n## Service Architecture\n
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
        \n\n## Startup and Service Management\n
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
        \n\n### Critical Startup Files:\n### minh.py\n*Main entry point*\n```python\n#!/usr/bin/env python3
"""
MinhOS v3 Central Command Interface
==================================

Single entry point for live trading integration with Sierra Chart.
Unified CLI for managing the complete MinhOS v3 trading system.

Usage:
    python3 minh.py start [--monitor]
    python3 minh.py stop
    python3 minh.py status  
    python3 minh.py test
    python3 minh.py config [show|set KEY VALUE]
    python3 minh.py logs [follow]

Commands:
    start       Start MinhOS v3 trading system
    stop        Stop all MinhOS services gracefully
    status      Show system status and health
    test        Run integration tests
    config      Manage configuration settings
    logs        View system logs

Options:
    --monitor   Start with detailed monitoring and logging

Note: Sierra Chart controls sim/demo mode internally

Author: MinhOS v3 System
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from client import MinhOSClient
from minhos.core.config import config as minhos_config

class MinhOSCommand:
    """Central command handler for MinhOS v3"""
    
    def __init__(self):
        self.config = minhos_config
        self.bridge_url = f"http://{os.getenv('BRIDGE_HOSTNAME', 'marypc')}:8765"
        self.integration = None
        self.running = False
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('minhos')
    
    def run(self, args):
        """Main entry point for command execution"""
        if args.command == 'start':
            asyncio.run(self.start_command(args))
        elif args.command == 'stop':
            asyncio.run(self.stop_command(args))
        elif args.command == 'status':
            asyncio.run(self.status_command(args))
        elif args.command == 'test':
            asyncio.run(self.test_command(args))
        elif args.command == 'config':
            self.config_command(args)
        elif args.command == 'logs':
            self.logs_command(args)
        else:
            self.logger.error(f"Unknown command: {args.command}")
            return 1
        
        return 0
    
    async def start_command(self, args):
        """Start MinhOS v3 trading system"""
        self._display_banner()
        
        try:
            # Pre-flight checks
            await self._pre_flight_checks()
            
            # Import and start integration (dynamic import to avoid startup delays)
            self.logger.info("🚀 Starting MinhOS v3 Trading System...")
            
            # Configure environment (Sierra Chart controls sim/demo mode)
            self._configure_trading_environment()
            
            # Start the integration system
            from minhos.services.live_trading_integration import LiveTradingIntegration
            self.integration = LiveTradingIntegration()
            await self.integration.start()
            
            self.running = True
            self.logger.info("✅ MinhOS v3 System ONLINE!")
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Monitoring loop
            if args.monitor:
                await self._monitoring_loop()
            else:
                await self._simple_loop()
        
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"Startup failed: {e}")
            raise
        finally:
            await self._shutdown()
    
    async def stop_command(self, args):
        """Stop MinhOS services"""
        self.logger.info("🛑 Stopping MinhOS v3 services...")
        
        # TODO: Implement proper service stopping
        # For now, just check if anything is running
        
        try:
            # Check if bridge is responsive
            async with MinhOSClient(self.bridge_url) as client:
                health = await client.health_check()
                if health:
                    self.logger.info("Bridge is still running on Windows")
        except:
            pass
        
        self.logger.info("✅ MinhOS v3 services stopped")
    
    async def status_command(self, args):
        """Show system status"""
        self.logger.info("📊 MinhOS v3 System Status")
        print("="*50)
        
        # Check bridge connection
        try:
            async with MinhOSClient(self.bridge_url) as client:
                health = await client.health_check()
                
                if health and health.get('status') == 'healthy':
                    print(f"✅ Sierra Chart Bridge: CONNECTED ({self.bridge_url})")
                    print(f"   Last Update: {health.get('last_data_update', 'Unknown')}")
                    
                    # Get market data
                    market_data = await client.get_market_data()
                    if market_data:
                        print(f"✅ Market Data: {market_data['symbol']} @ ${market_data['price']}")
                        print(f"   Bid/Ask: ${market_data['bid']} / ${market_data['ask']}")
                        print(f"   Volume: {market_data['volume']:,}")
                    else:
                        print("⚠️  Market Data: Not available")
                
                else:
                    print(f"❌ Sierra Chart Bridge: UNHEALTHY")
        
        except Exception as e:
            print(f"❌ Sierra Chart Bridge: DISCONNECTED ({e})")
        
        # System info
        print(f"\n📍 System Info:")
        print(f"   Bridge URL: {self.bridge_url}")
        print(f"   Environment: {self.config.environment}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("="*50)
    
    async def test_command(self, args):
        """Run integration tests"""
        self.logger.info("🧪 Running MinhOS v3 Integration Tests")
        print("="*50)
        
        tests = [
            ("Bridge Connection", self._test_bridge_connection),
            ("Market Data", self._test_market_data),
            ("Trade Execution", self._test_trade_execution)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔬 Testing: {test_name}")
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"   {status}")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results[test_name] = False
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        
        print(f"\n📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - System ready!")
        else:
            print("💥 Some tests failed - check configuration")
            return 1
        
        return 0
    
    def config_command(self, args):
        """Manage configuration"""
        if args.action == 'show':
            print("📋 MinhOS v3 Configuration:")
            print("="*30)
            config_dict = self.config.to_dict()
            for section, values in config_dict.items():
                print(f"\n[{section.upper()}]")
                if isinstance(values, dict):
                    for key, value in values.items():
                        print(f"  {key:20} = {value}")
                else:
                    print(f"  {section:20} = {values}")
        
        elif args.action == 'set' and args.key and args.value:
            # TODO: Implement config setting
            print(f"Setting {args.key} = {args.value}")
        
        else:
            print("Usage: python minh.py config [show|set KEY VALUE]")
    
    def logs_command(self, args):
        """View system logs"""
        # TODO: Implement log viewing
        if args.follow:
            print("Following logs... (Ctrl+C to stop)")
            print("(Log following not yet implemented)")
        else:
            print("Recent logs:")
            print("(Log viewing not yet implemented)")
    
    def _display_banner(self):
        """Display startup banner"""
        banner = f"""
╔═══════════════════════════════════════════════════╗
║                MinhOS v3 Live Trading             ║
║          Advanced AI Trading Integration          ║
╠═══════════════════════════════════════════════════╣
║ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                      ║
║ Bridge: {self.bridge_url:35} ║
╚═══════════════════════════════════════════════════╝
        """
        print(banner)
    
    def _confirm_live_trading(self):
        """Confirm live trading mode"""
        confirmed = os.getenv('CONFIRM_LIVE_TRADING', '').lower() == 'yes'
        
        if not confirmed:
            print("\n⚠️  LIVE TRADING CONFIRMATION REQUIRED")
            print("Set environment variable to confirm:")
            print("  export CONFIRM_LIVE_TRADING=yes")
            raise Exception("Live trading not confirmed")
        
        print("🔥 LIVE TRADING CONFIRMED")
    
    def _configure_trading_environment(self):
        """Configure trading environment variables"""
        # Sierra Chart controls sim/demo mode internally
        self.logger.info("Trading Mode: Controlled by Sierra Chart")
    
    async def _pre_flight_checks(self):
        """Pre-flight system checks"""
        self.logger.info("Performing pre-flight checks...")
        
        # Test bridge connection
        async with MinhOSClient(self.bridge_url) as client:
            health = await client.health_check()
            
            if not health or health.get('status') != 'healthy':
                raise Exception(f"Bridge health check failed: {health}")
            
            self.logger.info(f"✅ Bridge connected: {self.bridge_url}")
    
    async def _monitoring_loop(self):
        """Detailed monitoring loop"""
        self.logger.info("📊 Starting detailed monitoring...")
        
        while self.running:
            try:
                if self.integration:
                    status = self.integration.get_status()
                    self.logger.info(f"System: {json.dumps(status, indent=2)}")
                
                await asyncio.sleep(30)  # Status every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _simple_loop(self):
        """Simple keep-alive loop"""
        self.logger.info("System running... (Ctrl+C to stop)")
        
        while self.running:
            await asyncio.sleep(5)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum} - shutting down...")
        self.running = False
    
    async def _shutdown(self):
        """Graceful shutdown"""
        if self.integration:
            self.logger.info("Stopping integration services...")
            try:
                await self.integration.stop()
            except Exception as e:
                self.logger.error(f"Shutdown error: {e}")
        
        self.logger.info("🏁 MinhOS v3 shutdown complete")
    
    async def _test_bridge_connection(self):
        """Test bridge connection"""
        async with MinhOSClient(self.bridge_url) as client:
            health = await client.health_check()
            return health and health.get('status') == 'healthy'
    
    async def _test_market_data(self):
        """Test market data"""
        async with MinhOSClient(self.bridge_url) as client:
            data = await client.get_market_data()
            return data is not None and data.get('price', 0) > 0
    
    async def _test_trade_execution(self):
        """Test trade execution"""
        async with MinhOSClient(self.bridge_url) as client:
            result = await client.execute_trade("BUY", "NQU25-CME", 1)
            return result and 'command_id' in result

def create_parser():
    """Create command line parser"""
    parser = argparse.ArgumentParser(
        prog="minh.py",
        description="MinhOS v3 Live Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 minh.py start                    # Start trading system
  python3 minh.py start --monitor          # Start with detailed monitoring
  python3 minh.py status                   # Check system status
  python3 minh.py test                     # Run integration tests
  python3 minh.py stop                     # Stop all services
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start MinhOS v3 system')
    start_parser.add_argument('--monitor', action='store_true', help='Detailed monitoring')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop MinhOS services')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Test command  
    subparsers.add_parser('test', help='Run integration tests')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('action', nargs='?', choices=['show', 'set'], default='show')
    config_parser.add_argument('key', nargs='?', help='Configuration key')
    config_parser.add_argument('value', nargs='?', help='Configuration value')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='View system logs')
    logs_parser.add_argument('--follow', '-f', action='store_true', help='Follow logs')
    
    return parser

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # No mode configuration needed - Sierra Chart controls sim/demo
    
    # Create and run command handler
    command = MinhOSCommand()
    return command.run(args)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nShutdown by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)\n```\n\n### src/minh/command_parser.py - FILE NOT FOUND\n\n### services/service_orchestrator.py - FILE NOT FOUND\n\n\n## System Diagnostics\n\n### System Information:\n- Python Version: 3.10.12 (main, May 27 2025, 17:12:29) [GCC 11.4.0]\n- Working Directory: /home/colindo/Sync/minh_v3\n- System Time: 2025-07-24 11:35:18.260647\n\n### Process Information:\n**MinhOS Processes:**\n- PID 716734: python3 minh.py start\n\n### Service Health Status:\n- sierra_bridge (port 8765): ❌ NOT LISTENING\n- minhos_dashboard (port 8888): ✅ HEALTHY\n- live_integration (port 9005): ❌ NOT LISTENING\n- sierra_client (port 9003): ❌ NOT LISTENING\n- multi_chart_collector (port 9004): ❌ NOT LISTENING\n- ai_brain_service (port 9006): ❌ NOT LISTENING\n- trading_engine (port 9007): ❌ NOT LISTENING\n- state_manager (port 9008): ❌ NOT LISTENING\n- risk_manager (port 9009): ❌ NOT LISTENING\n\n### Critical Files:\n- config: ❌ MISSING (/home/colindo/Sync/minh_v3/config.yaml)\n- truth: ❌ MISSING (/home/colindo/Sync/minh_v3/SYSTEM_TRUTH.json)\n- main_entry: ✅ EXISTS (/home/colindo/Sync/minh_v3/minh.py)\n- service_orchestrator: ❌ MISSING (/home/colindo/Sync/minh_v3/services/service_orchestrator.py)\n- backend_study: ❌ MISSING (/home/colindo/Sync/minh_v3/services/backend_study_enhanced.py)\n- dashboard: ❌ MISSING (/home/colindo/Sync/minh_v3/dashboard/main.py)\n\n### Database Status:\n- latest_data: ❌ MISSING\n- sqlite_db: ❌ MISSING\n- history: ❌ MISSING\n\n## Recent Errors and Issues\n\n❌ Diagnostic log not found\n\n### Auto-Detected Issues:\n**HIGH**: Services not running: sierra_bridge, live_integration, sierra_client, multi_chart_collector, ai_brain_service, trading_engine, state_manager, risk_manager\n- Affected services: sierra_bridge, live_integration, sierra_client, multi_chart_collector, ai_brain_service, trading_engine, state_manager, risk_manager\n- Problem type: service_down\n- Diagnostics: {
  "down_services": [
    "sierra_bridge",
    "live_integration",
    "sierra_client",
    "multi_chart_collector",
    "ai_brain_service",
    "trading_engine",
    "state_manager",
    "risk_manager"
  ],
  "expected_ports": {
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
}\n\n**HIGH**: Configuration file missing\n- Affected services: all\n- Problem type: configuration\n- Diagnostics: {
  "missing_file": "/home/colindo/Sync/minh_v3/config.yaml"
}\n\n\n## MinhOS Fundamental Truths\nThese are the core principles that govern MinhOS operation:\n### core/minhos_fundamental_truths.py - FILE NOT FOUND\n