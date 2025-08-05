#!/usr/bin/env python3
"""
MinhOS v4 Trading Service (Consolidated)
========================================
Unified trading service combining core trading engine and live trading integration.
Provides complete trading functionality from analysis to execution.

Consolidates:
- trading_engine.py (Core trading logic and decision-making)
- live_trading_integration.py (Service orchestration and live execution)

Key Features:
- AI-driven trading signals and execution
- Advanced risk management and decision support
- Real-time market data integration
- Live Sierra Chart trading via Windows bridge
- Human oversight and autonomous capabilities
"""

import asyncio
import json
import logging
import statistics
import os
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Tuple, Callable
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# Core MinhOS imports
from minhos.core.base_service import BaseService, ServiceStatus
from minhos.core.config import config

# Service imports
from .sierra_client import SierraClient, TradeCommand, get_sierra_client
from .multi_chart_collector import MultiChartCollector
from .state_manager import StateManager, get_state_manager, Position, TradingState, SystemState
from .risk_manager import RiskManager, get_risk_manager
from .ai_brain_service import AIBrainService, get_ai_brain_service, TradingSignal, SignalType
from .sierra_historical_data import SierraHistoricalDataService
from ..models.market import MarketData
# from ..dashboard.main import DashboardServer  # Now consolidated into dashboard_server.py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_service")

# Enums and Data Classes
class DecisionPriority(Enum):
    """Priority levels for trading decisions"""
    CRITICAL = "critical"      # Need decision immediately
    HIGH = "high"              # Need decision within minutes
    MEDIUM = "medium"          # Need decision within hour
    LOW = "low"                # Consider when convenient
    INFORMATIONAL = "info"     # FYI only, no action needed

class MarketRegime(Enum):
    """Market regime classifications"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    QUIET = "quiet"
    UNKNOWN = "unknown"

class ExecutionStrategy(Enum):
    """Trade execution strategies"""
    MARKET = "market"           # Execute immediately at market
    LIMIT = "limit"             # Wait for better price
    STOP_MARKET = "stop_market" # Stop loss market order
    ADAPTIVE = "adaptive"       # Intelligent execution

@dataclass
class TradingDecision:
    """Represents a decision that needs human input or automated handling"""
    id: str
    title: str
    description: str
    priority: DecisionPriority
    options: List[str]
    context: Dict[str, Any]
    auto_action: Optional[str] = None
    created_at: datetime = None
    resolved: bool = False
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.id:
            self.id = f"decision_{int(self.created_at.timestamp())}"

@dataclass
class TradeOrder:
    """Represents a trade order"""
    symbol: str
    side: str  # BUY, SELL, CLOSE
    quantity: int
    order_type: ExecutionStrategy
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    reason: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class LiveTradingStatus:
    """Live trading system status"""
    is_connected: bool
    services_running: Dict[str, bool]
    positions: List[Dict[str, Any]]
    daily_pnl: float
    total_pnl: float
    last_update: datetime
    errors: List[str]

class TradingService(BaseService):
    """
    Unified Trading Service - Core trading engine + Live integration
    
    Provides complete trading functionality:
    - Real-time market analysis and signal generation
    - AI-driven trading decisions with human oversight
    - Risk management and position sizing
    - Live execution via Sierra Chart bridge
    - Service orchestration and monitoring
    """
    
    def __init__(self):
        super().__init__("TradingService")
        
        # Core components
        self.sierra_client = None
        self.multi_chart_collector = None
        self.state_manager = None
        self.risk_manager = None
        self.ai_brain = None
        self.historical_data = None
        self.dashboard = None
        
        # Trading engine state
        self.current_market_data = None
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_history = deque(maxlen=100)
        self.market_insights = {}
        self.pattern_signals = []
        self.active_decisions = {}
        self.pending_orders = deque(maxlen=100)
        self.performance_metrics = {}
        self.last_analysis = None
        
        # Live integration state
        self.status = LiveTradingStatus(
            is_connected=False,
            services_running={},
            positions=[],
            daily_pnl=0.0,
            total_pnl=0.0,
            last_update=datetime.now(),
            errors=[]
        )
        
        # Configuration
        self.autonomous_threshold = config.get("trading.autonomous_threshold", 0.75)
        self.max_position_size = config.get("trading.max_position_size", 5)
        self.analysis_interval = config.get("timing.market_analysis", 5000) / 1000
        self.decision_check_interval = config.get("timing.decision_check", 30000) / 1000
        
        # Task tracking
        self._analysis_task = None
        self._decision_task = None
        self._order_task = None
        self._performance_task = None
        self._integration_task = None
        self._status_task = None
        self._health_task = None
        
        # Running services registry
        self._running_services = {}

    async def start(self):
        """Start the unified trading service"""
        logger.info("Starting MinhOS v4 Trading Service...")
        
        try:
            # Use BaseService start method which calls our abstract methods
            await super().start()
            logger.info("Trading Service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Trading Service: {e}")
            await self.stop()
            raise

    async def _initialize_core_services(self):
        """Initialize core MinhOS services"""
        logger.info("Initializing core services...")
        
        # Get service instances
        self.state_manager = get_state_manager()
        self.risk_manager = get_risk_manager()
        self.ai_brain = get_ai_brain_service()
        
        # Start services if not already running
        services = [
            ("StateManager", self.state_manager),
            ("RiskManager", self.risk_manager),
            ("AIBrainService", self.ai_brain)
        ]
        
        for name, service in services:
            if hasattr(service, 'start') and not getattr(service, '_running', False):
                await service.start()
                self._running_services[name] = service
                logger.info(f"Started {name}")
            self.status.services_running[name] = True

    async def _initialize_sierra_connection(self):
        """Initialize Sierra Chart connection"""
        logger.info("Initializing Sierra Chart connection...")
        
        self.sierra_client = get_sierra_client()
        if hasattr(self.sierra_client, 'start'):
            await self.sierra_client.start()
            self._running_services["SierraClient"] = self.sierra_client
        
        self.status.services_running["SierraClient"] = True
        logger.info("Sierra Chart connection established")

    async def _initialize_data_collection(self):
        """Initialize data collection services"""
        logger.info("Initializing data collection...")
        
        # Multi-chart collector for cross-asset analysis
        self.multi_chart_collector = MultiChartCollector()
        if hasattr(self.multi_chart_collector, 'start'):
            await self.multi_chart_collector.start()
            self._running_services["MultiChartCollector"] = self.multi_chart_collector
        
        # Historical data service
        self.historical_data = SierraHistoricalDataService()
        if hasattr(self.historical_data, 'start'):
            await self.historical_data.start()
            self._running_services["HistoricalData"] = self.historical_data
        
        self.status.services_running["DataCollection"] = True
        logger.info("Data collection services initialized")

    async def _initialize_trading_services(self):
        """Initialize trading-specific services"""
        logger.info("Initializing trading services...")
        
        # Subscribe to market data updates
        if hasattr(self.sierra_client, 'subscribe_to_updates'):
            await self.sierra_client.subscribe_to_updates(self._on_market_data)
        
        # Initialize performance tracking
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'daily_pnl': 0.0,
            'max_drawdown': 0.0,
            'last_reset': datetime.now().date()
        }
        
        logger.info("Trading services initialized")

    async def _start_dashboard(self):
        """Start dashboard server (now handled separately)"""
        logger.info("Dashboard server handled by separate dashboard_server.py...")
        
        try:
            # Dashboard is now a separate service
            # No longer managed directly by trading service
            self.status.services_running["Dashboard"] = True
            logger.info("Dashboard server reference updated")
        except Exception as e:
            logger.error(f"Dashboard reference error: {e}")
            self.status.services_running["Dashboard"] = False

    async def _run_dashboard(self):
        """Run dashboard server (now handled separately)"""
        try:
            # Dashboard is now handled by separate dashboard_server.py
            logger.info("Dashboard server is now a separate service")
        except Exception as e:
            logger.error(f"Dashboard reference error: {e}")

    async def _start_processing_loops(self):
        """Start all trading engine processing loops"""
        logger.info("Starting processing loops...")
        
        # Core trading loops
        self._analysis_task = asyncio.create_task(self._market_analysis_loop())
        self._decision_task = asyncio.create_task(self._decision_management_loop())
        self._order_task = asyncio.create_task(self._order_management_loop())
        self._performance_task = asyncio.create_task(self._performance_tracking_loop())
        
        logger.info("Processing loops started")

    async def _start_integration_loops(self):
        """Start live integration monitoring loops"""
        logger.info("Starting integration loops...")
        
        # Live integration loops
        self._integration_task = asyncio.create_task(self._data_integration_loop())
        self._status_task = asyncio.create_task(self._status_monitoring_loop())
        self._health_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Integration loops started")

    # Market Data and Analysis Methods
    async def _on_market_data(self, market_data: MarketData):
        """Handle incoming market data"""
        self.current_market_data = market_data
        self.last_analysis = datetime.now()
        
        # Update status
        self.status.last_update = datetime.now()

    async def _market_analysis_loop(self):
        """Main market analysis loop"""
        while self._running:
            try:
                if self.current_market_data:
                    # Detect market regime
                    new_regime = await self._detect_market_regime()
                    if new_regime != self.current_regime:
                        await self._on_regime_change(new_regime)
                    
                    # Update market insights
                    await self._update_market_insights()
                    
                    # Evaluate trading opportunities
                    await self._evaluate_trading_opportunities()
                
                await asyncio.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Market analysis error: {e}")
                await asyncio.sleep(self.analysis_interval)

    async def _detect_market_regime(self) -> MarketRegime:
        """Detect current market regime"""
        if not self.current_market_data:
            return MarketRegime.UNKNOWN
        
        # Simple regime detection based on price action
        # This could be enhanced with more sophisticated analysis
        try:
            price = self.current_market_data.price
            volume = self.current_market_data.volume
            
            # Get recent price history for trend analysis
            if len(self.regime_history) < 10:
                return MarketRegime.UNKNOWN
            
            # Simple moving average trend detection
            recent_prices = [data.price for data in list(self.regime_history)[-10:]]
            if len(recent_prices) >= 5:
                early_avg = statistics.mean(recent_prices[:5])
                late_avg = statistics.mean(recent_prices[-5:])
                
                price_change_pct = (late_avg - early_avg) / early_avg * 100
                
                if price_change_pct > 0.1:
                    return MarketRegime.TRENDING_UP
                elif price_change_pct < -0.1:
                    return MarketRegime.TRENDING_DOWN
                else:
                    return MarketRegime.RANGING
            
            return MarketRegime.UNKNOWN
            
        except Exception as e:
            logger.error(f"Regime detection error: {e}")
            return MarketRegime.UNKNOWN

    async def _on_regime_change(self, new_regime: MarketRegime):
        """Handle market regime change"""
        old_regime = self.current_regime
        self.current_regime = new_regime
        
        logger.info(f"Market regime changed: {old_regime.value} -> {new_regime.value}")
        
        # Create decision for regime change if significant
        if old_regime != MarketRegime.UNKNOWN:
            await self._create_decision(
                title=f"Market Regime Change",
                description=f"Market regime changed from {old_regime.value} to {new_regime.value}",
                priority=DecisionPriority.MEDIUM,
                options=["Adjust strategy", "Maintain current approach", "Reduce exposure"],
                context={"old_regime": old_regime.value, "new_regime": new_regime.value}
            )

    async def _update_market_insights(self):
        """Update market insights and patterns"""
        if not self.current_market_data:
            return
        
        # Store market data for analysis
        self.regime_history.append(self.current_market_data)
        
        # Update insights
        self.market_insights.update({
            'current_price': self.current_market_data.price,
            'current_volume': self.current_market_data.volume,
            'regime': self.current_regime.value,
            'last_update': datetime.now().isoformat()
        })

    async def _evaluate_trading_opportunities(self):
        """Evaluate current trading opportunities"""
        try:
            # Get AI signal
            if self.ai_brain and self.current_market_data:
                signal = await self.ai_brain.analyze_market_data(self.current_market_data)
                if signal:
                    await self._process_ai_signal(signal)
            
            # Check for pattern opportunities
            await self._check_pattern_opportunities()
            
            # Check for risk adjustments
            await self._check_risk_adjustments()
            
        except Exception as e:
            logger.error(f"Opportunity evaluation error: {e}")

    async def _process_ai_signal(self, signal: TradingSignal):
        """Process AI trading signal"""
        try:
            current_price = self.current_market_data.price if self.current_market_data else 0.0
            
            # Log AI reasoning
            await self._log_ai_reasoning(signal, current_price)
            
            # Check confidence threshold
            if signal.confidence >= self.autonomous_threshold:
                # Create trade order
                order = await self._create_trade_order_from_signal(signal, current_price)
                if order:
                    # Validate with risk manager
                    if await self._validate_trade_with_risk_manager(order, signal):
                        # Execute autonomous trade
                        success = await self._execute_autonomous_trade(order, signal)
                        if success:
                            await self._log_trade_execution(signal, order, "autonomous")
                        else:
                            await self._log_trade_failure(signal, order, "execution_failed")
                    else:
                        await self._log_trade_rejection(signal, order, "risk_validation_failed")
            else:
                # Below threshold - log and potentially create decision
                await self._log_signal_below_threshold(signal, current_price)
                
                if signal.confidence >= 0.5:  # Still significant
                    await self._create_decision(
                        title=f"Trading Signal: {signal.signal_type.value}",
                        description=f"AI suggests {signal.signal_type.value} with {signal.confidence:.1%} confidence",
                        priority=DecisionPriority.HIGH,
                        options=["Execute trade", "Wait for better signal", "Adjust parameters"],
                        context={"signal": asdict(signal), "current_price": current_price}
                    )
            
        except Exception as e:
            await self._log_processing_error(signal, str(e))

    async def _create_trade_order_from_signal(self, signal: TradingSignal, current_price: float) -> Optional[TradeOrder]:
        """Create trade order from AI signal"""
        try:
            # Determine side
            side = "BUY" if signal.signal_type == SignalType.BUY else "SELL"
            
            # Calculate position size
            quantity = await self._calculate_position_size(signal, current_price)
            
            # Determine execution strategy based on signal urgency and market conditions
            if signal.confidence >= 0.9:
                order_type = ExecutionStrategy.MARKET
            elif self.current_regime in [MarketRegime.VOLATILE]:
                order_type = ExecutionStrategy.ADAPTIVE
            else:
                order_type = ExecutionStrategy.LIMIT
            
            return TradeOrder(
                symbol=signal.symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=signal.target_price,
                stop_price=signal.stop_loss,
                reason=f"AI signal: {signal.confidence:.1%} confidence"
            )
            
        except Exception as e:
            logger.error(f"Order creation error: {e}")
            return None

    async def _calculate_position_size(self, signal: TradingSignal, current_price: float) -> int:
        """Calculate appropriate position size"""
        try:
            # Get current account info
            if self.state_manager:
                state = await self.state_manager.get_trading_state()
                available_capital = getattr(state, 'available_capital', 100000)  # Default
            else:
                available_capital = 100000
            
            # Risk-based sizing (max 2% per trade)
            max_risk = available_capital * 0.02
            
            # Calculate risk per share
            if signal.stop_loss and current_price:
                risk_per_share = abs(current_price - signal.stop_loss)
                if risk_per_share > 0:
                    max_shares = int(max_risk / risk_per_share)
                    return min(max_shares, self.max_position_size)
            
            # Default conservative sizing
            return min(1, self.max_position_size)
            
        except Exception as e:
            logger.error(f"Position sizing error: {e}")
            return 1

    async def _validate_trade_with_risk_manager(self, order: TradeOrder, signal: TradingSignal) -> bool:
        """Validate trade with risk manager"""
        try:
            if self.risk_manager:
                # Check position limits
                if hasattr(self.risk_manager, 'validate_trade'):
                    return await self.risk_manager.validate_trade(order, signal)
                else:
                    # Basic validation
                    return order.quantity <= self.max_position_size
            return True
            
        except Exception as e:
            logger.error(f"Risk validation error: {e}")
            return False

    async def _execute_autonomous_trade(self, order: TradeOrder, signal: TradingSignal) -> bool:
        """Execute autonomous trade"""
        try:
            if self.sierra_client:
                # Convert to Sierra Chart trade command
                trade_command = TradeCommand(
                    symbol=order.symbol,
                    action=order.side,
                    quantity=order.quantity,
                    order_type=order.order_type.value,
                    price=order.price
                )
                
                # Execute trade
                result = await self.sierra_client.execute_trade(trade_command)
                return result.get('success', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False

    # Logging methods
    async def _log_ai_reasoning(self, signal: TradingSignal, current_price: float):
        """Log AI reasoning"""
        logger.info(f"AI Signal: {signal.signal_type.value} | Confidence: {signal.confidence:.1%} | Target: ${signal.target_price} | Current: ${current_price}")

    async def _log_trade_execution(self, signal: TradingSignal, order: TradeOrder, execution_type: str):
        """Log successful trade execution"""
        logger.info(f"Trade executed ({execution_type}): {order.side} {order.quantity} {order.symbol} | Reason: {order.reason}")

    async def _log_trade_failure(self, signal: TradingSignal, order: TradeOrder, reason: str):
        """Log trade execution failure"""
        logger.warning(f"Trade failed: {order.side} {order.quantity} {order.symbol} | Reason: {reason}")

    async def _log_trade_rejection(self, signal: TradingSignal, order: TradeOrder, reason: str):
        """Log trade rejection"""
        logger.info(f"Trade rejected: {order.side} {order.quantity} {order.symbol} | Reason: {reason}")

    async def _log_signal_below_threshold(self, signal: TradingSignal, current_price: float):
        """Log signal below autonomous threshold"""
        logger.info(f"Signal below threshold: {signal.signal_type.value} | Confidence: {signal.confidence:.1%} | Threshold: {self.autonomous_threshold:.1%}")

    async def _log_processing_error(self, signal: Optional[TradingSignal], error: str):
        """Log processing error"""
        logger.error(f"Signal processing error: {error}")

    # Decision Management
    async def _create_decision(self, title: str, description: str, priority: DecisionPriority,
                             options: List[str], context: Dict[str, Any], 
                             auto_action: Optional[str] = None) -> TradingDecision:
        """Create new trading decision"""
        decision = TradingDecision(
            id="",  # Will be auto-generated
            title=title,
            description=description,
            priority=priority,
            options=options,
            context=context,
            auto_action=auto_action
        )
        
        self.active_decisions[decision.id] = decision
        logger.info(f"Created decision: {decision.title} (Priority: {priority.value})")
        
        return decision

    async def _decision_management_loop(self):
        """Manage active decisions"""
        while self._running:
            try:
                await self._check_decision_points()
                await asyncio.sleep(self.decision_check_interval)
            except Exception as e:
                logger.error(f"Decision management error: {e}")
                await asyncio.sleep(self.decision_check_interval)

    async def _check_decision_points(self):
        """Check for decision points and auto-resolution"""
        # Auto-resolve old informational decisions
        current_time = datetime.now()
        for decision_id, decision in list(self.active_decisions.items()):
            if decision.priority == DecisionPriority.INFORMATIONAL:
                if (current_time - decision.created_at).total_seconds() > 3600:  # 1 hour
                    await self._resolve_decision(decision_id, "auto_expired", auto_resolved=True)

    async def _resolve_decision(self, decision_id: str, resolution: str, auto_resolved: bool = False):
        """Resolve a trading decision"""
        if decision_id in self.active_decisions:
            decision = self.active_decisions[decision_id]
            decision.resolved = True
            decision.resolution = resolution
            decision.resolved_at = datetime.now()
            
            logger.info(f"Decision resolved: {decision.title} -> {resolution}")
            
            # Execute resolution action
            await self._execute_decision_resolution(decision, resolution)
            
            # Remove from active decisions
            del self.active_decisions[decision_id]

    async def _execute_decision_resolution(self, decision: TradingDecision, resolution: str):
        """Execute decision resolution action"""
        # This would contain logic to act on decision resolutions
        # For now, just log the action
        logger.info(f"Executing resolution: {resolution} for decision: {decision.title}")

    # Pattern and Risk Analysis
    async def _check_pattern_opportunities(self):
        """Check for pattern-based trading opportunities"""
        # Placeholder for pattern recognition logic
        # This would integrate with technical analysis patterns
        pass

    async def _check_risk_adjustments(self):
        """Check if risk adjustments are needed"""
        # Placeholder for risk monitoring logic
        # This would check for position sizing, stop losses, etc.
        pass

    # Order Management
    async def _order_management_loop(self):
        """Manage pending orders"""
        while self._running:
            try:
                # Process pending orders
                if self.pending_orders:
                    order = self.pending_orders.popleft()
                    await self._process_order(order)
                
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Order management error: {e}")
                await asyncio.sleep(1)

    async def _process_order(self, order: TradeOrder):
        """Process individual order"""
        try:
            if order.order_type == ExecutionStrategy.MARKET:
                await self._execute_market_order(order)
            elif order.order_type == ExecutionStrategy.LIMIT:
                await self._execute_limit_order(order)
            elif order.order_type == ExecutionStrategy.ADAPTIVE:
                await self._execute_adaptive_order(order)
                
        except Exception as e:
            logger.error(f"Order processing error: {e}")

    async def _execute_market_order(self, order: TradeOrder):
        """Execute market order"""
        logger.info(f"Executing market order: {order.side} {order.quantity} {order.symbol}")
        # Implementation would send order to Sierra Chart

    async def _execute_limit_order(self, order: TradeOrder):
        """Execute limit order"""
        logger.info(f"Executing limit order: {order.side} {order.quantity} {order.symbol} @ ${order.price}")
        # Implementation would send limit order to Sierra Chart

    async def _execute_adaptive_order(self, order: TradeOrder):
        """Execute adaptive order with intelligent timing"""
        logger.info(f"Executing adaptive order: {order.side} {order.quantity} {order.symbol}")
        # Implementation would use smart order routing

    # Performance Tracking
    async def _performance_tracking_loop(self):
        """Track trading performance"""
        while self._running:
            try:
                await self._update_performance_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Performance tracking error: {e}")
                await asyncio.sleep(60)

    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            if self.state_manager:
                # Get current positions and P&L
                state = await self.state_manager.get_trading_state()
                if hasattr(state, 'total_pnl'):
                    self.performance_metrics['total_pnl'] = state.total_pnl
                    self.status.total_pnl = state.total_pnl
                
                # Update daily P&L
                today = datetime.now().date()
                if self.performance_metrics['last_reset'] != today:
                    self.performance_metrics['daily_pnl'] = 0.0
                    self.performance_metrics['last_reset'] = today
                
                self.status.daily_pnl = self.performance_metrics['daily_pnl']
                
        except Exception as e:
            logger.error(f"Performance update error: {e}")

    # Live Integration Methods
    async def _data_integration_loop(self):
        """Main data integration loop"""
        while self._running:
            try:
                # Ensure data flow from all sources
                if self.sierra_client and hasattr(self.sierra_client, 'get_latest_data'):
                    latest_data = await self.sierra_client.get_latest_data()
                    if latest_data:
                        await self._on_market_data(latest_data)
                
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Data integration error: {e}")
                await asyncio.sleep(5)

    async def _status_monitoring_loop(self):
        """Monitor system status"""
        while self._running:
            try:
                # Collect system status
                self.status = await self._collect_system_status()
                
                # Broadcast status to interested parties
                await self._broadcast_status(self.status)
                
                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Status monitoring error: {e}")
                await asyncio.sleep(10)

    async def _collect_system_status(self) -> LiveTradingStatus:
        """Collect comprehensive system status"""
        try:
            # Get positions
            positions = []
            if self.state_manager:
                try:
                    state = await self.state_manager.get_trading_state()
                    if hasattr(state, 'positions'):
                        positions = [asdict(pos) for pos in state.positions]
                except:
                    pass
            
            # Check service status
            services_running = {}
            for name, service in self._running_services.items():
                services_running[name] = getattr(service, 'status', None) == ServiceStatus.RUNNING if hasattr(service, 'status') else True
            
            # Collect errors
            errors = []
            if not self.sierra_client:
                errors.append("Sierra Client not connected")
            
            return LiveTradingStatus(
                is_connected=bool(self.sierra_client),
                services_running=services_running,
                positions=positions,
                daily_pnl=self.performance_metrics.get('daily_pnl', 0.0),
                total_pnl=self.performance_metrics.get('total_pnl', 0.0),
                last_update=datetime.now(),
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Status collection error: {e}")
            return self.status

    async def _broadcast_status(self, status: LiveTradingStatus):
        """Broadcast status to dashboard and other interested parties"""
        # This would send status updates to WebSocket clients, dashboard, etc.
        pass

    async def _health_check_loop(self):
        """Perform regular health checks"""
        while self._running:
            try:
                # Check service health
                for name, service in self._running_services.items():
                    if hasattr(service, 'health_check'):
                        healthy = await service.health_check()
                        if not healthy:
                            logger.warning(f"Service {name} failed health check")
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)

    # Public API Methods
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        if self.state_manager:
            try:
                state = await self.state_manager.get_trading_state()
                if hasattr(state, 'positions'):
                    return [asdict(pos) for pos in state.positions]
            except:
                pass
        return []

    async def get_status(self) -> Dict[str, Any]:
        """Get current trading service status"""
        return asdict(self.status)

    @property
    def running(self) -> bool:
        """Check if trading service is running"""
        return self._running
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the trading service"""
        return {
            "healthy": self._running,
            "running": self._running,
            "services": self.status.services_running,
            "last_update": self.status.last_update.isoformat() if self.status.last_update else None
        }

    async def get_decisions(self) -> List[Dict[str, Any]]:
        """Get active trading decisions"""
        return [asdict(decision) for decision in self.active_decisions.values()]

    def get_pending_decisions(self) -> List[TradingDecision]:
        """Get all pending decisions (synchronous method for compatibility)"""
        return [decision for decision in self.active_decisions.values() if not decision.resolved]

    async def resolve_decision(self, decision_id: str, resolution: str):
        """Resolve a trading decision"""
        await self._resolve_decision(decision_id, resolution)

    # Lifecycle Methods
    # Abstract method implementations for BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        await self._initialize_core_services()
        await self._initialize_sierra_connection()
        await self._initialize_data_collection()
        await self._initialize_trading_services()
    
    async def _start_service(self):
        """Start service-specific functionality"""
        # Start dashboard if configured
        if config.get("services.dashboard.enabled", True):
            await self._start_dashboard()
        
        # Start all processing loops
        await self._start_processing_loops()
        
        # Start integration monitoring
        await self._start_integration_loops()
        
        self.status.is_connected = True
    
    async def _stop_service(self):
        """Stop service-specific functionality"""
        self._running = False
        
        # Cancel all tasks
        tasks = [
            self._analysis_task,
            self._decision_task,
            self._order_task,
            self._performance_task,
            self._integration_task,
            self._status_task,
            self._health_task
        ]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.status.is_connected = False
    
    async def _cleanup(self):
        """Cleanup service resources"""
        # Stop all running services
        for name, service in self._running_services.items():
            try:
                if hasattr(service, 'stop'):
                    await service.stop()
                logger.info(f"Stopped {name}")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        self._running_services.clear()

    async def stop(self):
        """Stop the trading service"""
        logger.info("Stopping Trading Service...")
        await super().stop()  # Call BaseService stop method
        logger.info("Trading Service stopped")

# Service Registry Functions
_trading_service_instance = None

def get_trading_service() -> TradingService:
    """Get the global trading service instance"""
    global _trading_service_instance
    if _trading_service_instance is None:
        _trading_service_instance = TradingService()
    return _trading_service_instance

# Compatibility aliases for legacy code
TradingEngine = TradingService
get_trading_engine = get_trading_service

async def create_trading_service() -> TradingService:
    """Create and start a new trading service instance"""
    service = TradingService()
    await service.start()
    return service

# Main execution
async def main():
    """Main function for standalone execution"""
    trading_service = TradingService()
    
    try:
        await trading_service.start()
        logger.info("Trading Service running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Trading Service error: {e}")
    finally:
        await trading_service.stop()

if __name__ == "__main__":
    asyncio.run(main())