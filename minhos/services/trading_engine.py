#!/usr/bin/env python3
"""
MinhOS v3 Trading Engine
========================
Linux-native intelligent trading engine with decision support and risk management.
Provides advanced trading logic, pattern-based execution, and human oversight.

Replaces trading_copilot.py with enhanced capabilities and clean Linux architecture.
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Tuple, Callable
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# Import other services
from .sierra_client import get_sierra_client
from ..models.market import MarketData
from .state_manager import get_state_manager, Position, TradingState, SystemState
from .ai_brain_service import get_ai_brain_service, TradingSignal, SignalType
from .risk_manager import get_risk_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_engine")

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

class TradingEngine:
    """
    Advanced trading engine with intelligent decision support
    Linux-native with comprehensive risk management and human oversight
    """
    
    def __init__(self):
        """Initialize Trading Engine"""
        self.running = False
        
        # Service references
        self.sierra_client = None
        self.state_manager = None
        self.ai_brain = None
        self.risk_manager = None
        
        # Trading state
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_history = deque(maxlen=100)
        self.market_data_buffer = deque(maxlen=1000)
        
        # Decision management
        self.pending_decisions: List[TradingDecision] = []
        self.decision_history = deque(maxlen=500)
        self.auto_decision_handlers: Dict[str, Callable] = {}
        
        # Trade management
        self.pending_orders: List[TradeOrder] = []
        self.order_history = deque(maxlen=1000)
        self.execution_strategies: Dict[str, Callable] = {}
        
        # Performance tracking
        self.performance_metrics = {
            "trades_today": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "total_pnl": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "last_trade_time": None
        }
        
        # Market insights
        self.market_insights = {
            "trend_strength": 0.0,
            "volatility_rank": 0.5,
            "volume_profile": "normal",
            "support_levels": [],
            "resistance_levels": [],
            "market_bias": "neutral"
        }
        
        # Configuration
        self.config = {
            "auto_execution_enabled": False,
            "max_position_size": 5,
            "risk_per_trade": 0.02,
            "volatility_threshold": 2.0,
            "trend_threshold": 0.7,
            "decision_timeout_seconds": {
                DecisionPriority.CRITICAL: 300,    # 5 minutes
                DecisionPriority.HIGH: 1800,       # 30 minutes
                DecisionPriority.MEDIUM: 3600,     # 1 hour
                DecisionPriority.LOW: 14400,       # 4 hours
                DecisionPriority.INFORMATIONAL: 86400  # 24 hours
            }
        }
        
        # Statistics
        self.stats = {
            "decisions_created": 0,
            "decisions_resolved": 0,
            "orders_created": 0,
            "orders_executed": 0,
            "market_regime_changes": 0,
            "ai_signals_processed": 0,
            "risk_violations": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # Setup execution strategies
        self._setup_execution_strategies()
        self._setup_auto_decision_handlers()
        
        logger.info("🎯 Trading Engine initialized")
    
    async def start(self):
        """Start the Trading Engine"""
        logger.info("🚀 Starting Trading Engine...")
        self.running = True
        
        # Initialize service references
        self.sierra_client = get_sierra_client()
        self.state_manager = get_state_manager()
        self.ai_brain = get_ai_brain_service()
        self.risk_manager = get_risk_manager()
        
        # Subscribe to market data
        if hasattr(self.sierra_client, 'add_data_handler'):
            self.sierra_client.add_data_handler(self._on_market_data)
        
        # Start engine loops
        asyncio.create_task(self._market_analysis_loop())
        asyncio.create_task(self._decision_management_loop())
        asyncio.create_task(self._order_management_loop())
        asyncio.create_task(self._performance_tracking_loop())
        asyncio.create_task(self._regime_detection_loop())
        
        logger.info("✅ Trading Engine started")
    
    async def stop(self):
        """Stop the Trading Engine"""
        logger.info("🛑 Stopping Trading Engine...")
        self.running = False
        
        # Cancel all pending orders
        for order in self.pending_orders:
            logger.info(f"Cancelling pending order: {order.symbol} {order.side}")
        self.pending_orders.clear()
        
        logger.info("Trading Engine stopped")
    
    async def _on_market_data(self, market_data: MarketData):
        """Handle new market data"""
        try:
            # Add to analysis buffer
            data_point = {
                'timestamp': market_data.timestamp,
                'symbol': market_data.symbol,
                'close': market_data.close,
                'bid': market_data.bid,
                'ask': market_data.ask,
                'volume': market_data.volume,
                'high': getattr(market_data, 'high', market_data.close),
                'low': getattr(market_data, 'low', market_data.close)
            }
            
            self.market_data_buffer.append(data_point)
            
            # Update market insights
            await self._update_market_insights()
            
            # Check for trading opportunities
            await self._evaluate_trading_opportunities()
            
        except Exception as e:
            logger.error(f"❌ Market data processing error: {e}")
    
    async def _market_analysis_loop(self):
        """Continuous market analysis and regime detection"""
        while self.running:
            try:
                if len(self.market_data_buffer) >= 50:
                    # Detect market regime
                    new_regime = await self._detect_market_regime()
                    if new_regime != self.current_regime:
                        await self._on_regime_change(new_regime)
                    
                    # Update market insights
                    await self._update_market_insights()
                    
                    # Check for decision points
                    await self._check_decision_points()
                
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Market analysis error: {e}")
                await asyncio.sleep(30)
    
    async def _detect_market_regime(self) -> MarketRegime:
        """Detect current market regime"""
        try:
            if len(self.market_data_buffer) < 50:
                return MarketRegime.UNKNOWN
            
            # Get recent price data
            recent_data = list(self.market_data_buffer)[-50:]
            prices = [d['close'] for d in recent_data]
            volumes = [d.get('volume', 0) for d in recent_data if d.get('volume', 0) > 0]
            
            # Calculate returns
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            
            # Calculate metrics
            volatility = statistics.stdev(returns) if len(returns) > 1 else 0
            trend_strength = abs(statistics.mean(returns)) if returns else 0
            
            # Volume analysis
            avg_volume = statistics.mean(volumes) if volumes else 0
            recent_volume = statistics.mean(volumes[-10:]) if len(volumes) >= 10 else avg_volume
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Regime classification
            if volatility > 0.025:  # 2.5%
                return MarketRegime.VOLATILE
            elif trend_strength > 0.01 and volume_ratio > 1.2:  # Strong trend with volume
                if statistics.mean(returns) > 0:
                    return MarketRegime.TRENDING_UP
                else:
                    return MarketRegime.TRENDING_DOWN
            elif volatility < 0.005:  # 0.5%
                return MarketRegime.QUIET
            else:
                return MarketRegime.RANGING
                
        except Exception as e:
            logger.error(f"❌ Regime detection error: {e}")
            return MarketRegime.UNKNOWN
    
    async def _on_regime_change(self, new_regime: MarketRegime):
        """Handle market regime change"""
        try:
            old_regime = self.current_regime
            self.current_regime = new_regime
            
            # Record regime change
            self.regime_history.append({
                'from': old_regime.value,
                'to': new_regime.value,
                'timestamp': datetime.now().isoformat()
            })
            
            self.stats["market_regime_changes"] += 1
            
            logger.info(f"📊 Market regime changed: {old_regime.value} → {new_regime.value}")
            
            # Create decision for significant regime changes
            if old_regime == MarketRegime.QUIET and new_regime == MarketRegime.VOLATILE:
                await self._create_decision(
                    "Market Volatility Spike",
                    "Market transitioned from quiet to volatile. Consider position adjustments.",
                    DecisionPriority.HIGH,
                    ["Reduce position sizes", "Close positions", "Maintain current strategy", "Switch to volatility strategy"],
                    {
                        'old_regime': old_regime.value,
                        'new_regime': new_regime.value,
                        'volatility_increase': True
                    },
                    "Reduce position sizes"  # Auto action
                )
            
            elif new_regime in [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
                await self._create_decision(
                    "Trending Market Detected",
                    f"Market is now {new_regime.value.replace('_', ' ')}. Consider trend-following strategies.",
                    DecisionPriority.MEDIUM,
                    ["Follow trend", "Wait for pullback", "Counter-trend", "Stay flat"],
                    {
                        'old_regime': old_regime.value,
                        'new_regime': new_regime.value,
                        'trend_direction': 'up' if new_regime == MarketRegime.TRENDING_UP else 'down'
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Regime change handling error: {e}")
    
    async def _update_market_insights(self):
        """Update market insights based on current data"""
        try:
            if len(self.market_data_buffer) < 20:
                return
            
            recent_data = list(self.market_data_buffer)[-50:]
            prices = [d['close'] for d in recent_data]
            volumes = [d.get('volume', 0) for d in recent_data if d.get('volume', 0) > 0]
            
            # Trend strength
            if len(prices) >= 20:
                sma_10 = statistics.mean(prices[-10:])
                sma_20 = statistics.mean(prices[-20:])
                self.market_insights['trend_strength'] = (sma_10 - sma_20) / sma_20 if sma_20 != 0 else 0
            
            # Volatility rank
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            if len(returns) >= 20:
                current_vol = statistics.stdev(returns[-10:]) if len(returns) >= 10 else 0
                historical_vol = statistics.stdev(returns) if len(returns) > 1 else 0
                self.market_insights['volatility_rank'] = current_vol / historical_vol if historical_vol > 0 else 1
            
            # Volume profile
            if volumes:
                avg_volume = statistics.mean(volumes)
                current_volume = volumes[-1] if volumes else 0
                if current_volume > avg_volume * 1.5:
                    self.market_insights['volume_profile'] = 'high'
                elif current_volume < avg_volume * 0.5:
                    self.market_insights['volume_profile'] = 'low'
                else:
                    self.market_insights['volume_profile'] = 'normal'
            
            # Market bias
            trend_strength = self.market_insights.get('trend_strength', 0)
            if trend_strength > 0.005:
                self.market_insights['market_bias'] = 'bullish'
            elif trend_strength < -0.005:
                self.market_insights['market_bias'] = 'bearish'
            else:
                self.market_insights['market_bias'] = 'neutral'
            
        except Exception as e:
            logger.error(f"❌ Market insights update error: {e}")
    
    async def _evaluate_trading_opportunities(self):
        """Evaluate current trading opportunities"""
        try:
            # Get AI signal if available
            ai_signal = self.ai_brain.get_current_signal() if self.ai_brain else None
            
            if ai_signal and ai_signal.confidence > 0.7:
                await self._process_ai_signal(ai_signal)
            
            # Check for pattern-based opportunities
            await self._check_pattern_opportunities()
            
            # Risk-based position adjustments
            await self._check_risk_adjustments()
            
        except Exception as e:
            logger.error(f"❌ Opportunity evaluation error: {e}")
    
    async def _process_ai_signal(self, signal: TradingSignal):
        """Process AI-generated trading signal"""
        try:
            self.stats["ai_signals_processed"] += 1
            
            # Validate signal with risk manager
            if self.risk_manager:
                # Create trade request for validation
                current_price = 0
                if self.market_data_buffer:
                    current_price = self.market_data_buffer[-1]['close']
                
                # This would normally create a proper trade request
                # For now, just log the signal
                logger.info(f"🤖 AI Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
                logger.info(f"    Reasoning: {signal.reasoning}")
                
                # Create decision for human review
                await self._create_decision(
                    f"AI Trading Signal: {signal.signal.value}",
                    f"AI suggests {signal.signal.value} with {signal.confidence:.1%} confidence. {signal.reasoning}",
                    DecisionPriority.HIGH if signal.confidence > 0.8 else DecisionPriority.MEDIUM,
                    ["Execute signal", "Modify size", "Wait for confirmation", "Ignore signal"],
                    {
                        'signal': signal.signal.value,
                        'confidence': signal.confidence,
                        'reasoning': signal.reasoning,
                        'target_price': signal.target_price,
                        'stop_loss': signal.stop_loss,
                        'current_price': current_price
                    },
                    "Wait for confirmation" if signal.confidence < 0.8 else None
                )
            
        except Exception as e:
            logger.error(f"❌ AI signal processing error: {e}")
    
    async def _check_pattern_opportunities(self):
        """Check for pattern-based trading opportunities"""
        try:
            # This would implement pattern recognition logic
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Pattern opportunity check error: {e}")
    
    async def _check_risk_adjustments(self):
        """Check if positions need risk-based adjustments"""
        try:
            if not self.state_manager:
                return
            
            positions = self.state_manager.get_positions()
            
            for symbol, position in positions.items():
                # Check if position needs adjustment based on risk
                if position.unrealized_pnl < -100:  # $100 loss threshold
                    await self._create_decision(
                        f"Position Risk Alert: {symbol}",
                        f"Position in {symbol} showing unrealized loss of ${position.unrealized_pnl:.2f}",
                        DecisionPriority.HIGH,
                        ["Close position", "Reduce size", "Add stop loss", "Hold position"],
                        {
                            'symbol': symbol,
                            'position': asdict(position),
                            'unrealized_pnl': position.unrealized_pnl
                        },
                        "Add stop loss"
                    )
            
        except Exception as e:
            logger.error(f"❌ Risk adjustment check error: {e}")
    
    async def _check_decision_points(self):
        """Check for time-based and condition-based decision points"""
        try:
            now = datetime.now()
            
            # Pre-market analysis (9:00 AM ET)
            if now.time() == time(9, 0) and now.weekday() < 5:
                await self._create_decision(
                    "Pre-Market Analysis",
                    "Market opening soon. Review overnight developments and set trading plan.",
                    DecisionPriority.MEDIUM,
                    ["Aggressive strategy", "Normal strategy", "Defensive strategy", "Stay flat"],
                    {
                        'market_insights': self.market_insights.copy(),
                        'current_regime': self.current_regime.value
                    }
                )
            
            # End of day review (3:45 PM ET)
            if now.time() == time(15, 45) and now.weekday() < 5:
                await self._create_decision(
                    "End of Day Review",
                    "Market closing soon. Review positions and prepare for overnight.",
                    DecisionPriority.MEDIUM,
                    ["Close all positions", "Hold positions", "Adjust stops", "Add hedges"],
                    {
                        'performance': self.performance_metrics.copy(),
                        'positions': len(self.state_manager.get_positions()) if self.state_manager else 0
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Decision points check error: {e}")
    
    async def _decision_management_loop(self):
        """Manage pending decisions and auto-resolution"""
        while self.running:
            try:
                now = datetime.now()
                
                for decision in self.pending_decisions[:]:  # Copy to avoid modification during iteration
                    if decision.resolved:
                        continue
                    
                    # Check for timeout
                    age_seconds = (now - decision.created_at).total_seconds()
                    timeout = self.config["decision_timeout_seconds"].get(decision.priority, 3600)
                    
                    if age_seconds > timeout:
                        if decision.auto_action:
                            await self._resolve_decision(decision.id, decision.auto_action, auto_resolved=True)
                        else:
                            await self._resolve_decision(decision.id, "timeout", auto_resolved=True)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Decision management error: {e}")
                await asyncio.sleep(60)
    
    async def _order_management_loop(self):
        """Manage pending orders and execution"""
        while self.running:
            try:
                # Process pending orders
                for order in self.pending_orders[:]:
                    await self._process_order(order)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Order management error: {e}")
                await asyncio.sleep(5)
    
    async def _performance_tracking_loop(self):
        """Track and update performance metrics"""
        while self.running:
            try:
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Check for performance alerts
                if self.performance_metrics["trades_today"] > 10 and self.performance_metrics["win_rate"] < 0.3:
                    await self._create_decision(
                        "Performance Alert",
                        f"Win rate today: {self.performance_metrics['win_rate']:.1%} from {self.performance_metrics['trades_today']} trades",
                        DecisionPriority.HIGH,
                        ["Stop trading", "Reduce size", "Change strategy", "Continue"],
                        self.performance_metrics.copy(),
                        "Reduce size"
                    )
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Performance tracking error: {e}")
                await asyncio.sleep(300)
    
    async def _regime_detection_loop(self):
        """Dedicated loop for market regime detection"""
        while self.running:
            try:
                if len(self.market_data_buffer) >= 50:
                    new_regime = await self._detect_market_regime()
                    if new_regime != self.current_regime:
                        await self._on_regime_change(new_regime)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Regime detection loop error: {e}")
                await asyncio.sleep(60)
    
    # Decision management methods
    async def _create_decision(self, title: str, description: str, priority: DecisionPriority,
                             options: List[str], context: Dict[str, Any], auto_action: Optional[str] = None):
        """Create a new trading decision"""
        try:
            # Check for duplicate decisions
            for existing in self.pending_decisions:
                if existing.title == title and not existing.resolved:
                    return  # Don't create duplicate
            
            decision = TradingDecision(
                id="",  # Will be set in __post_init__
                title=title,
                description=description,
                priority=priority,
                options=options,
                context=context,
                auto_action=auto_action
            )
            
            self.pending_decisions.append(decision)
            self.stats["decisions_created"] += 1
            
            logger.info(f"📋 Decision created: {title} (Priority: {priority.value})")
            
            # Execute auto handler if available
            handler_key = f"{priority.value}_{title.lower().replace(' ', '_')}"
            if handler_key in self.auto_decision_handlers:
                await self.auto_decision_handlers[handler_key](decision)
            
        except Exception as e:
            logger.error(f"❌ Decision creation error: {e}")
    
    async def _resolve_decision(self, decision_id: str, resolution: str, auto_resolved: bool = False):
        """Resolve a pending decision"""
        try:
            for decision in self.pending_decisions:
                if decision.id == decision_id:
                    decision.resolved = True
                    decision.resolution = resolution
                    decision.resolved_at = datetime.now()
                    
                    self.decision_history.append(decision)
                    self.pending_decisions.remove(decision)
                    self.stats["decisions_resolved"] += 1
                    
                    resolution_type = "Auto" if auto_resolved else "Manual"
                    logger.info(f"✅ Decision resolved ({resolution_type}): {decision.title} → {resolution}")
                    
                    # Execute resolution action
                    await self._execute_decision_resolution(decision, resolution)
                    break
            
        except Exception as e:
            logger.error(f"❌ Decision resolution error: {e}")
    
    async def _execute_decision_resolution(self, decision: TradingDecision, resolution: str):
        """Execute the action based on decision resolution"""
        try:
            # This would contain the logic to execute the decided action
            # For now, just log
            logger.info(f"🎯 Executing decision: {resolution} for {decision.title}")
            
        except Exception as e:
            logger.error(f"❌ Decision execution error: {e}")
    
    # Order management methods
    async def _process_order(self, order: TradeOrder):
        """Process a pending order"""
        try:
            # This would contain actual order execution logic
            # For now, simulate order processing
            logger.info(f"📊 Processing order: {order.symbol} {order.side} {order.quantity}")
            
            # Remove from pending orders
            self.pending_orders.remove(order)
            self.order_history.append(order)
            self.stats["orders_executed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Order processing error: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        try:
            # This would calculate actual performance metrics
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Performance update error: {e}")
    
    def _setup_execution_strategies(self):
        """Setup different execution strategies"""
        self.execution_strategies = {
            ExecutionStrategy.MARKET.value: self._execute_market_order,
            ExecutionStrategy.LIMIT.value: self._execute_limit_order,
            ExecutionStrategy.ADAPTIVE.value: self._execute_adaptive_order
        }
    
    def _setup_auto_decision_handlers(self):
        """Setup handlers for automatic decision resolution"""
        self.auto_decision_handlers = {
            "high_market_volatility_spike": self._handle_volatility_spike,
            "high_position_risk_alert": self._handle_position_risk
        }
    
    async def _execute_market_order(self, order: TradeOrder):
        """Execute market order"""
        # Placeholder for market order execution
        pass
    
    async def _execute_limit_order(self, order: TradeOrder):
        """Execute limit order"""
        # Placeholder for limit order execution
        pass
    
    async def _execute_adaptive_order(self, order: TradeOrder):
        """Execute adaptive order with intelligent timing"""
        # Placeholder for adaptive execution
        pass
    
    async def _handle_volatility_spike(self, decision: TradingDecision):
        """Auto handler for volatility spike decisions"""
        try:
            # Automatically reduce position sizes
            logger.info("🔄 Auto-handling volatility spike: reducing position sizes")
            await self._resolve_decision(decision.id, "Reduce position sizes", auto_resolved=True)
            
        except Exception as e:
            logger.error(f"❌ Volatility spike handler error: {e}")
    
    async def _handle_position_risk(self, decision: TradingDecision):
        """Auto handler for position risk alerts"""
        try:
            # Automatically add stop loss
            logger.info("🛡️ Auto-handling position risk: adding stop loss")
            await self._resolve_decision(decision.id, "Add stop loss", auto_resolved=True)
            
        except Exception as e:
            logger.error(f"❌ Position risk handler error: {e}")
    
    # Public API methods
    def get_pending_decisions(self) -> List[TradingDecision]:
        """Get all pending decisions"""
        return [d for d in self.pending_decisions if not d.resolved]
    
    def get_market_regime(self) -> MarketRegime:
        """Get current market regime"""
        return self.current_regime
    
    def get_market_insights(self) -> Dict[str, Any]:
        """Get current market insights"""
        return self.market_insights.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        return {
            "running": self.running,
            "current_regime": self.current_regime.value,
            "pending_decisions": len(self.get_pending_decisions()),
            "pending_orders": len(self.pending_orders),
            "market_data_points": len(self.market_data_buffer),
            "performance": self.performance_metrics.copy(),
            "market_insights": self.market_insights.copy(),
            "stats": self.stats.copy(),
            "timestamp": datetime.now().isoformat()
        }

# Global trading engine instance
_trading_engine: Optional[TradingEngine] = None

def get_trading_engine() -> TradingEngine:
    """Get global trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = TradingEngine()
    return _trading_engine

async def main():
    """Test the Trading Engine"""
    engine = TradingEngine()
    
    try:
        await engine.start()
        logger.info("Trading Engine running. Press Ctrl+C to stop...")
        
        # Keep running
        while engine.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())