#!/usr/bin/env python3
"""
MinhOS v3 Live Trading Integration Service
=========================================

Integrates all MinhOS services with live Sierra Chart trading via the Windows bridge.

This service orchestrates the complete live trading system:
- Connects MinhOS AI brain to live market data
- Integrates trading engine with live execution
- Coordinates risk management with live positions
- Manages multi-chart data flow
- Handles decision-based live trading

Key Components Integration:
- Sierra Client → Live market data from Windows bridge
- Multi-Chart Collector → Cross-asset and timeframe analysis  
- AI Brain → Live analysis of real market data
- Trading Engine → Live trade execution via bridge
- Risk Manager → Real-time position and risk monitoring
- State Manager → Live P&L and position tracking

Author: MinhOS v3 System
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from minhos.core.base_service import BaseService
from minhos.core.config import config
from minhos.services.sierra_client import SierraClient, TradeCommand
from minhos.services.multi_chart_collector import MultiChartCollector
from minhos.services.state_manager import StateManager
from minhos.services.risk_manager import RiskManager
from minhos.services.trading_engine import TradingEngine, TradingDecision
from minhos.services.ai_brain_service import AIBrainService

logger = logging.getLogger(__name__)

@dataclass
class LiveTradingStatus:
    """Live trading system status"""
    timestamp: str
    sierra_connected: bool
    charts_active: int
    ai_brain_active: bool
    risk_manager_active: bool
    trading_enabled: bool
    positions_count: int
    daily_pnl: float
    pending_decisions: int
    last_trade_time: Optional[str] = None

class LiveTradingIntegration(BaseService):
    """Orchestrates all MinhOS services for live trading"""
    
    def __init__(self):
        super().__init__("live_trading_integration", 9005)
        self.config = config
        
        # Service instances
        self.sierra_client: Optional[SierraClient] = None
        self.multi_chart_collector: Optional[MultiChartCollector] = None
        self.state_manager: Optional[StateManager] = None
        self.risk_manager: Optional[RiskManager] = None
        self.trading_engine: Optional[TradingEngine] = None
        self.ai_brain: Optional[AIBrainService] = None
        
        # Integration settings
        self.live_trading_enabled = os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true'
        self.auto_trading_enabled = os.getenv('ENABLE_AUTO_TRADING', 'false').lower() == 'true'
        
        # Status tracking
        self.running = False
        self.last_status: Optional[LiveTradingStatus] = None
        self.system_health_checks = {}
        
        # Subscribers
        self.status_subscribers = set()
        
        logger.info(f"Live Trading Integration initialized - Live: {self.live_trading_enabled}")
    
    async def start(self):
        """Start the live trading integration system"""
        await super().start()
        logger.info("Starting MinhOS v3 Live Trading Integration...")
        
        try:
            # 1. Initialize core services first
            await self._initialize_core_services()
            
            # 2. Initialize Sierra Chart connection
            await self._initialize_sierra_connection()
            
            # 3. Initialize data collection
            await self._initialize_data_collection()
            
            # 4. Initialize AI and trading services
            await self._initialize_trading_services()
            
            # 5. Start integration loops
            await self._start_integration_loops()
            
            logger.info("🚀 MinhOS v3 Live Trading System ONLINE!")
            
        except Exception as e:
            logger.critical(f"Failed to start live trading system: {e}")
            raise
    
    async def _initialize_core_services(self):
        """Initialize core MinhOS services"""
        logger.info("Initializing core services...")
        
        # State manager (foundation service)
        self.state_manager = StateManager()
        await self.state_manager.start()
        
        # Risk manager
        self.risk_manager = RiskManager()
        await self.risk_manager.start()
        
        logger.info("✅ Core services initialized")
    
    async def _initialize_sierra_connection(self):
        """Initialize connection to Sierra Chart via Windows bridge"""
        logger.info("Initializing Sierra Chart connection...")
        
        # Create Sierra Client
        self.sierra_client = SierraClient()
        await self.sierra_client.start()
        
        # Wait for connection to establish
        max_wait = 30  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            status = self.sierra_client.get_status()
            if status['connection_state'] == 'connected':
                logger.info("✅ Sierra Chart bridge connected")
                break
            
            await asyncio.sleep(2)
            wait_time += 2
        else:
            raise Exception("Failed to connect to Sierra Chart bridge within timeout")
    
    async def _initialize_data_collection(self):
        """Initialize multi-chart data collection"""
        logger.info("Initializing multi-chart data collection...")
        
        # Create multi-chart collector
        self.multi_chart_collector = MultiChartCollector(self.sierra_client)
        await self.multi_chart_collector.start()
        
        # Wait for initial data
        await asyncio.sleep(5)
        
        logger.info("✅ Multi-chart data collection active")
    
    async def _initialize_trading_services(self):
        """Initialize AI and trading services"""
        logger.info("Initializing AI and trading services...")
        
        # AI Brain service
        self.ai_brain = AIBrainService()
        await self.ai_brain.start()
        
        # Trading engine
        self.trading_engine = TradingEngine()
        await self.trading_engine.start()
        
        logger.info("✅ AI and trading services initialized")
    
    async def _start_integration_loops(self):
        """Start main integration loops"""
        logger.info("Starting integration loops...")
        
        # Data flow integration
        asyncio.create_task(self._data_integration_loop())
        
        # Trading integration
        asyncio.create_task(self._trading_integration_loop())
        
        # Status monitoring
        asyncio.create_task(self._status_monitoring_loop())
        
        # Health checks
        asyncio.create_task(self._health_check_loop())
        
        logger.info("✅ Integration loops started")
    
    async def _data_integration_loop(self):
        """Integrate live market data with MinhOS AI analysis"""
        while self.running:
            try:
                # Get multi-chart analysis
                if self.multi_chart_collector:
                    analysis = self.multi_chart_collector.get_current_analysis()
                    
                    if analysis and analysis.nq_1min:
                        # Feed live data to AI brain for analysis
                        market_data = {
                            'timestamp': analysis.timestamp,
                            'symbol': analysis.nq_1min.symbol,
                            'price': analysis.nq_1min.price,
                            'volume': analysis.nq_1min.volume,
                            'bid': analysis.nq_1min.bid,
                            'ask': analysis.nq_1min.ask,
                            'vix_level': analysis.vix_level,
                            'market_regime': analysis.market_regime,
                            'timeframe_alignment': analysis.timeframe_alignment
                        }
                        
                        # Send to AI brain for analysis
                        if self.ai_brain:
                            await self.ai_brain.process_market_data(market_data)
                
                await asyncio.sleep(5.0)  # Analyze every 5 seconds
                
            except Exception as e:
                logger.error(f"Data integration error: {e}")
                await asyncio.sleep(10.0)
    
    async def _trading_integration_loop(self):
        """Integrate AI decisions with live trade execution"""
        while self.running:
            try:
                if not (self.trading_engine and self.sierra_client):
                    await asyncio.sleep(5.0)
                    continue
                
                # Check for new trading decisions
                decisions = self.trading_engine.get_pending_decisions()
                
                for decision in decisions:
                    if decision.auto_execute and self.auto_trading_enabled:
                        # Execute automatically
                        await self._execute_live_decision(decision)
                    elif decision.priority == "CRITICAL":
                        # Log critical decisions for manual review
                        logger.warning(f"CRITICAL DECISION: {decision.action} - {decision.reasoning}")
                
                await asyncio.sleep(2.0)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Trading integration error: {e}")
                await asyncio.sleep(10.0)
    
    async def _execute_live_decision(self, decision: TradingDecision):
        """Execute a trading decision via live Sierra Chart connection"""
        if not self.live_trading_enabled:
            logger.info(f"PAPER TRADE: {decision.action} - Live trading disabled")
            return
        
        try:
            # Create trade command
            trade_command = TradeCommand(
                command_id=f"minhos_{decision.decision_id}",
                action=decision.action,
                symbol="NQU25-CME",  # Primary symbol
                quantity=decision.quantity,
                order_type="MARKET"
            )
            
            # Execute via Sierra Client
            result = await self.sierra_client.execute_trade(trade_command)
            
            if result and result.status == "FILLED":
                logger.info(f"✅ LIVE TRADE EXECUTED: {decision.action} {decision.quantity} @ ${result.fill_price}")
                
                # Update decision status
                await self.trading_engine.update_decision_status(
                    decision.decision_id, 
                    "EXECUTED", 
                    f"Filled @ ${result.fill_price}"
                )
                
                # Update state manager with live position
                if self.state_manager:
                    await self.state_manager.update_position(
                        symbol=trade_command.symbol,
                        quantity=decision.quantity if decision.action == "BUY" else -decision.quantity,
                        price=result.fill_price
                    )
            
            else:
                logger.error(f"❌ TRADE REJECTED: {result.message if result else 'No response'}")
                
                # Update decision status
                await self.trading_engine.update_decision_status(
                    decision.decision_id,
                    "REJECTED",
                    result.message if result else "Unknown error"
                )
        
        except Exception as e:
            logger.error(f"Live trade execution error: {e}")
    
    async def _status_monitoring_loop(self):
        """Monitor and update system status"""
        while self.running:
            try:
                # Collect status from all services
                status = await self._collect_system_status()
                self.last_status = status
                
                # Broadcast to subscribers
                await self._broadcast_status(status)
                
                await asyncio.sleep(10.0)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Status monitoring error: {e}")
                await asyncio.sleep(30.0)
    
    async def _collect_system_status(self) -> LiveTradingStatus:
        """Collect comprehensive system status"""
        timestamp = datetime.now().isoformat()
        
        # Sierra connection status
        sierra_connected = False
        charts_active = 0
        if self.sierra_client:
            sierra_status = self.sierra_client.get_status()
            sierra_connected = sierra_status['connection_state'] == 'connected'
        
        if self.multi_chart_collector:
            charts_status = self.multi_chart_collector.get_status()
            charts_active = charts_status['charts_active']
        
        # AI brain status
        ai_brain_active = self.ai_brain is not None and self.ai_brain.running
        
        # Risk manager status
        risk_manager_active = self.risk_manager is not None and self.risk_manager.running
        
        # Trading status
        trading_enabled = self.live_trading_enabled
        
        # Position data
        positions_count = 0
        daily_pnl = 0.0
        if self.state_manager:
            positions = await self.state_manager.get_all_positions()
            positions_count = len([p for p in positions if p.quantity != 0])
            daily_pnl = sum(p.unrealized_pnl for p in positions)
        
        # Pending decisions
        pending_decisions = 0
        if self.trading_engine:
            decisions = self.trading_engine.get_pending_decisions()
            pending_decisions = len(decisions)
        
        return LiveTradingStatus(
            timestamp=timestamp,
            sierra_connected=sierra_connected,
            charts_active=charts_active,
            ai_brain_active=ai_brain_active,
            risk_manager_active=risk_manager_active,
            trading_enabled=trading_enabled,
            positions_count=positions_count,
            daily_pnl=daily_pnl,
            pending_decisions=pending_decisions
        )
    
    async def _health_check_loop(self):
        """Perform periodic health checks"""
        while self.running:
            try:
                # Check each service health
                health_checks = {}
                
                if self.sierra_client:
                    health_checks['sierra_client'] = self.sierra_client.get_status()
                
                if self.multi_chart_collector:
                    health_checks['multi_chart_collector'] = self.multi_chart_collector.get_status()
                
                if self.ai_brain:
                    health_checks['ai_brain'] = {'running': self.ai_brain.running}
                
                if self.risk_manager:
                    health_checks['risk_manager'] = {'running': self.risk_manager.running}
                
                if self.trading_engine:
                    health_checks['trading_engine'] = {'running': self.trading_engine.running}
                
                self.system_health_checks = health_checks
                
                # Log health summary
                healthy_services = sum(1 for check in health_checks.values() if check.get('running', True))
                total_services = len(health_checks)
                
                if healthy_services == total_services:
                    logger.debug(f"System health: ALL SYSTEMS OPERATIONAL ({healthy_services}/{total_services})")
                else:
                    logger.warning(f"System health: {healthy_services}/{total_services} services healthy")
                
                await asyncio.sleep(60.0)  # Health check every minute
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60.0)
    
    async def _broadcast_status(self, status: LiveTradingStatus):
        """Broadcast status to subscribers"""
        if not self.status_subscribers:
            return
        
        message = {
            'type': 'live_trading_status',
            'data': status.__dict__
        }
        
        # Broadcast to subscribers
        disconnected = []
        for websocket in self.status_subscribers.copy():
            try:
                await websocket.send(json.dumps(message, default=str))
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected subscribers
        for websocket in disconnected:
            self.status_subscribers.discard(websocket)
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections for system monitoring"""
        self.status_subscribers.add(websocket)
        logger.info(f"New status subscriber: {websocket.remote_address}")
        
        try:
            # Send current status
            if self.last_status:
                await self._broadcast_status(self.last_status)
            
            # Handle incoming messages
            async for message in websocket:
                try:
                    request = json.loads(message)
                    await self._handle_status_request(websocket, request)
                except Exception as e:
                    logger.error(f"WebSocket message error: {e}")
        
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            self.status_subscribers.discard(websocket)
            logger.info("Status subscriber disconnected")
    
    async def _handle_status_request(self, websocket, request: Dict):
        """Handle status requests from subscribers"""
        req_type = request.get('type')
        
        if req_type == 'get_system_status':
            if self.last_status:
                await websocket.send(json.dumps({
                    'type': 'system_status',
                    'data': self.last_status.__dict__
                }, default=str))
        
        elif req_type == 'get_health_checks':
            await websocket.send(json.dumps({
                'type': 'health_checks',
                'data': self.system_health_checks
            }, default=str))
        
        elif req_type == 'emergency_stop':
            logger.critical("EMERGENCY STOP requested via WebSocket")
            if self.risk_manager:
                await self.risk_manager.emergency_stop("Manual emergency stop")
    
    async def stop(self):
        """Stop the live trading integration system"""
        logger.info("Stopping MinhOS v3 Live Trading Integration...")
        
        # Stop all services in reverse order
        services = [
            self.ai_brain,
            self.trading_engine,
            self.multi_chart_collector,
            self.sierra_client,
            self.risk_manager,
            self.state_manager
        ]
        
        for service in services:
            if service:
                try:
                    await service.stop()
                except Exception as e:
                    logger.error(f"Error stopping service: {e}")
        
        await super().stop()
        logger.info("Live Trading Integration stopped")
    
    def get_status(self) -> Dict:
        """Get current integration system status"""
        return {
            'service': 'live_trading_integration',
            'live_trading_enabled': self.live_trading_enabled,
            'auto_trading_enabled': self.auto_trading_enabled,
            'services_initialized': {
                'sierra_client': self.sierra_client is not None,
                'multi_chart_collector': self.multi_chart_collector is not None,
                'ai_brain': self.ai_brain is not None,
                'risk_manager': self.risk_manager is not None,
                'trading_engine': self.trading_engine is not None,
                'state_manager': self.state_manager is not None
            },
            'status_subscribers': len(self.status_subscribers),
            'last_status_time': self.last_status.timestamp if self.last_status else None
        }
    
    # Abstract method implementations required by BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        await self._initialize_core_services()
        await self._initialize_sierra_connection()
        await self._initialize_data_collection()
        await self._initialize_trading_services()
        
    async def _start_service(self):
        """Start service-specific functionality"""
        logger.info("Starting live trading integration loops...")
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self._data_integration_loop())
        asyncio.create_task(self._trading_integration_loop())
        asyncio.create_task(self._status_monitoring_loop())
        asyncio.create_task(self._health_check_loop())
        
    async def _stop_service(self):
        """Stop service-specific functionality"""
        logger.info("Stopping live trading integration...")
        self.running = False
        
    async def _cleanup(self):
        """Cleanup service resources"""
        # Stop all services in reverse order
        services = [
            self.ai_brain,
            self.trading_engine,
            self.multi_chart_collector,
            self.sierra_client,
            self.risk_manager,
            self.state_manager
        ]
        
        for service in services:
            if service:
                try:
                    if hasattr(service, 'stop'):
                        await service.stop()
                except Exception as e:
                    logger.error(f"Error stopping service during cleanup: {e}")

# Service factory
async def create_live_trading_integration() -> LiveTradingIntegration:
    """Create and initialize Live Trading Integration"""
    integration = LiveTradingIntegration()
    await integration.start()
    return integration

if __name__ == "__main__":
    # Standalone mode for testing
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        integration = await create_live_trading_integration()
        
        try:
            # Keep system running
            while True:
                status = integration.get_status()
                logger.info(f"Integration Status: {status}")
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down live trading integration...")
        finally:
            await integration.stop()
    
    asyncio.run(main())