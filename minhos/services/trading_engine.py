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
            "autonomous_executions": 0,  # Track AI autonomous executions
            "decision_quality_evaluations": 0,  # Track decision quality evaluations
            "avg_decision_quality": 0.0,  # Average decision quality score
            "risk_violations": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # Decision Quality tracking
        self.recent_quality_scores = []
        
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
    
    async def _on_market_data(self, market_data):
        """Handle new market data"""
        try:
            # Handle both MarketData objects and dictionaries
            if isinstance(market_data, dict):
                data_point = {
                    'timestamp': market_data.get('timestamp'),
                    'symbol': market_data.get('symbol'),
                    'close': market_data.get('close'),
                    'bid': market_data.get('bid'),
                    'ask': market_data.get('ask'),
                    'volume': market_data.get('volume'),
                    'high': market_data.get('high', market_data.get('close')),
                    'low': market_data.get('low', market_data.get('close'))
                }
            else:
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
        """Process AI-generated trading signal with autonomous execution"""
        try:
            self.stats["ai_signals_processed"] += 1
            
            # Get current market data
            current_price = 0
            if self.market_data_buffer:
                current_price = self.market_data_buffer[-1]['close']
            
            # Log complete AI reasoning for transparency
            await self._log_ai_reasoning(signal, current_price)
            
            # Validate signal with risk manager
            if not self.risk_manager:
                logger.warning("⚠️ Risk manager not available - skipping signal")
                return
            
            # Create trade order from AI signal
            trade_order = await self._create_trade_order_from_signal(signal, current_price)
            
            if not trade_order:
                logger.warning("⚠️ Could not create valid trade order from signal")
                return
            
            # Risk validation
            risk_approved = await self._validate_trade_with_risk_manager(trade_order, signal)
            
            if not risk_approved:
                logger.warning(f"🛡️ Risk manager rejected trade: {signal.signal.value}")
                await self._log_trade_rejection(signal, trade_order, "Risk management rejection")
                return
            
            # AI AUTONOMOUS EXECUTION - No human approval needed
            if signal.confidence >= 0.75:  # High confidence threshold for autonomous execution
                logger.info(f"🤖 AUTONOMOUS EXECUTION: {signal.signal.value} (confidence: {signal.confidence:.1%})")
                success = await self._execute_autonomous_trade(trade_order, signal)
                
                if success:
                    self.stats["autonomous_executions"] += 1
                    await self._log_trade_execution(signal, trade_order, "Autonomous execution")
                    
                    # DECISION QUALITY EVALUATION - Evaluate the quality of our decision-making process
                    await self._evaluate_decision_quality(signal, trade_order, current_price, success)
                else:
                    await self._log_trade_failure(signal, trade_order, "Execution failed")
                    
                    # Still evaluate decision quality even for failed executions
                    await self._evaluate_decision_quality(signal, trade_order, current_price, success)
            
            else:
                # Log decision but don't execute - below confidence threshold
                logger.info(f"📊 AI Signal below execution threshold: {signal.signal.value} (confidence: {signal.confidence:.1%})")
                await self._log_signal_below_threshold(signal, current_price)
                
                # Evaluate decision quality for non-executed signals too
                await self._evaluate_decision_quality(signal, None, current_price, None)
            
        except Exception as e:
            logger.error(f"❌ AI signal processing error: {e}")
            await self._log_processing_error(signal if 'signal' in locals() else None, str(e))
    
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
    
    # ============================================================================
    # AI TRANSPARENCY AND EXECUTION METHODS
    # ============================================================================
    
    async def _log_ai_reasoning(self, signal: TradingSignal, current_price: float):
        """Log complete AI reasoning for transparency"""
        try:
            logger.info("=" * 80)
            logger.info("🧠 AI BRAIN REASONING - COMPLETE TRANSPARENCY")
            logger.info("=" * 80)
            logger.info(f"📊 Signal: {signal.signal.value}")
            logger.info(f"📈 Confidence: {signal.confidence:.1%}")
            logger.info(f"💰 Current Price: ${current_price:.2f}")
            logger.info(f"🎯 Target Price: ${signal.target_price:.2f}" if signal.target_price else "🎯 Target Price: Not set")
            logger.info(f"🛑 Stop Loss: ${signal.stop_loss:.2f}" if signal.stop_loss else "🛑 Stop Loss: Not set")
            logger.info(f"🔍 Analysis Type: {signal.analysis_type.value}")
            logger.info(f"📝 Reasoning: {signal.reasoning}")
            logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
            logger.info("=" * 80)
            
            # Log to file for historical analysis
            await self._save_ai_decision_log(signal, current_price)
            
        except Exception as e:
            logger.error(f"❌ AI reasoning logging error: {e}")
    
    async def _create_trade_order_from_signal(self, signal: TradingSignal, current_price: float) -> Optional[TradeOrder]:
        """Create trade order from AI signal"""
        try:
            # Skip HOLD signals
            if signal.signal == SignalType.HOLD:
                return None
            
            # Determine order side
            if signal.signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                side = "BUY"
            elif signal.signal in [SignalType.SELL, SignalType.STRONG_SELL]:
                side = "SELL"
            else:
                return None
            
            # Calculate position size based on confidence and risk management
            position_size = await self._calculate_position_size(signal, current_price)
            
            # Determine execution strategy based on signal strength
            if signal.signal in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
                execution_strategy = ExecutionStrategy.MARKET  # Execute immediately for strong signals
            else:
                execution_strategy = ExecutionStrategy.ADAPTIVE  # Use adaptive execution for regular signals
            
            # Get primary trading symbol from centralized symbol management
            from ..core.symbol_integration import get_ai_brain_primary_symbol, get_symbol_integration
            primary_symbol = get_ai_brain_primary_symbol()
            
            # Mark service as migrated to centralized symbol management
            get_symbol_integration().mark_service_migrated('trading_engine')
            
            order = TradeOrder(
                symbol=primary_symbol,  # Dynamic symbol from centralized management
                side=side,
                quantity=position_size,
                order_type=execution_strategy,
                price=signal.target_price,
                stop_price=signal.stop_loss,
                reason=f"AI Signal: {signal.reasoning}"
            )
            
            return order
            
        except Exception as e:
            logger.error(f"❌ Trade order creation error: {e}")
            return None
    
    async def _calculate_position_size(self, signal: TradingSignal, current_price: float) -> int:
        """Calculate position size based on AI confidence and risk management"""
        try:
            base_size = 1  # Base position size
            
            # Adjust size based on confidence
            confidence_multiplier = signal.confidence
            
            # Apply risk management constraints
            if self.risk_manager:
                # This would use risk manager to calculate appropriate size
                # For now, use simple logic
                max_size = 3  # Maximum contracts
                calculated_size = int(base_size * confidence_multiplier * 2)
                position_size = min(calculated_size, max_size)
            else:
                position_size = base_size
            
            logger.info(f"📏 Position Size Calculation:")
            logger.info(f"    Base Size: {base_size}")
            logger.info(f"    Confidence Multiplier: {confidence_multiplier:.2f}")
            logger.info(f"    Final Size: {position_size}")
            
            return max(1, position_size)  # Minimum 1 contract
            
        except Exception as e:
            logger.error(f"❌ Position size calculation error: {e}")
            return 1
    
    async def _validate_trade_with_risk_manager(self, order: TradeOrder, signal: TradingSignal) -> bool:
        """Validate trade with risk manager"""
        try:
            if not self.risk_manager:
                return False
            
            # TODO: Implement actual risk validation
            # For now, always approve if confidence is high enough
            approved = signal.confidence >= 0.75
            
            logger.info(f"🛡️ Risk Validation:")
            logger.info(f"    Order: {order.side} {order.quantity} {order.symbol}")
            logger.info(f"    Signal Confidence: {signal.confidence:.1%}")
            logger.info(f"    Risk Approved: {'✅ YES' if approved else '❌ NO'}")
            
            return approved
            
        except Exception as e:
            logger.error(f"❌ Risk validation error: {e}")
            return False
    
    async def _execute_autonomous_trade(self, order: TradeOrder, signal: TradingSignal) -> bool:
        """Execute trade autonomously without human intervention"""
        try:
            logger.info("🚀 AUTONOMOUS TRADE EXECUTION INITIATED")
            logger.info(f"📋 Order Details: {order.side} {order.quantity} {order.symbol}")
            logger.info(f"🎯 Strategy: {order.order_type.value}")
            
            # Execute based on strategy
            if order.order_type == ExecutionStrategy.MARKET:
                success = await self._execute_market_order(order)
            elif order.order_type == ExecutionStrategy.LIMIT:
                success = await self._execute_limit_order(order)
            elif order.order_type == ExecutionStrategy.ADAPTIVE:
                success = await self._execute_adaptive_order(order)
            else:
                logger.error(f"❌ Unknown execution strategy: {order.order_type}")
                return False
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Autonomous execution error: {e}")
            return False
    
    async def _save_ai_decision_log(self, signal: TradingSignal, current_price: float):
        """Save AI decision to log file for analysis"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "signal": signal.signal.value,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning,
                "current_price": current_price,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "analysis_type": signal.analysis_type.value
            }
            
            # TODO: Save to structured log file or database
            # For now, just log as JSON
            logger.info(f"💾 AI Decision Log: {json.dumps(log_entry, indent=2)}")
            
        except Exception as e:
            logger.error(f"❌ AI decision logging error: {e}")
    
    async def _log_trade_rejection(self, signal: TradingSignal, order: TradeOrder, reason: str):
        """Log when a trade is rejected"""
        logger.warning("🚫 TRADE REJECTED")
        logger.warning(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.warning(f"📋 Order: {order.side} {order.quantity} {order.symbol}")
        logger.warning(f"❌ Reason: {reason}")
    
    async def _log_trade_execution(self, signal: TradingSignal, order: TradeOrder, execution_type: str):
        """Log successful trade execution"""
        logger.info("✅ TRADE EXECUTED")
        logger.info(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.info(f"📋 Order: {order.side} {order.quantity} {order.symbol}")
        logger.info(f"🚀 Execution Type: {execution_type}")
    
    async def _log_trade_failure(self, signal: TradingSignal, order: TradeOrder, reason: str):
        """Log failed trade execution"""
        logger.error("❌ TRADE EXECUTION FAILED")
        logger.error(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.error(f"📋 Order: {order.side} {order.quantity} {order.symbol}")
        logger.error(f"💥 Reason: {reason}")
    
    async def _log_signal_below_threshold(self, signal: TradingSignal, current_price: float):
        """Log when signal is below execution threshold"""
        logger.info("📊 SIGNAL BELOW EXECUTION THRESHOLD")
        logger.info(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.info(f"💰 Current Price: ${current_price:.2f}")
        logger.info(f"⚖️ Threshold: 75% (current: {signal.confidence:.1%})")
        logger.info(f"📝 Reasoning: {signal.reasoning}")
    
    async def _log_processing_error(self, signal: Optional[TradingSignal], error: str):
        """Log processing errors"""
        logger.error("💥 AI SIGNAL PROCESSING ERROR")
        if signal:
            logger.error(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.error(f"❌ Error: {error}")
    
    async def _evaluate_decision_quality(self, signal: TradingSignal, 
                                        trade_order: Optional[TradeOrder], 
                                        current_price: float, 
                                        execution_success: Optional[bool]):
        """
        Evaluate the quality of our decision-making process independent of outcome.
        This is the core of our philosophy - measuring decision quality, not just results.
        """
        try:
            from ..core.decision_quality import get_decision_quality_framework
            
            # Generate unique decision ID
            decision_id = f"decision_{int(datetime.now().timestamp())}"
            
            # Prepare AI signal data for evaluation
            ai_signal_data = {
                'signal': signal.signal.value,
                'confidence': signal.confidence,
                'reasoning': signal.reasoning,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'analysis_type': signal.analysis_type.value
            }
            
            # Add decision quality context if available
            if hasattr(signal, 'decision_quality_context'):
                ai_signal_data.update(signal.decision_quality_context)
            
            # Prepare market data snapshot
            market_data_snapshot = {
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'market_session': getattr(signal, 'decision_quality_context', {}).get('market_session', 'unknown')
            }
            
            # Prepare risk metrics
            risk_metrics = {
                'position_size_calculated': trade_order is not None,
                'risk_reward_ratio': self._calculate_risk_reward_ratio(signal, current_price) if signal.target_price and signal.stop_loss else None,
                'portfolio_impact_assessed': True  # We always consider portfolio impact
            }
            
            # Prepare execution details
            execution_details = {}
            if trade_order:
                execution_details = {
                    'side': trade_order.side,
                    'quantity': trade_order.quantity,
                    'order_type': trade_order.order_type.value,
                    'signal_price': current_price,
                    'execution_price': current_price,  # Simplified - would be actual execution price
                    'execution_delay_seconds': 0,  # AI execution is immediate
                    'execution_success': execution_success
                }
            else:
                execution_details = {
                    'side': None,
                    'quantity': 0,
                    'signal_price': current_price,
                    'execution_success': None,  # Not executed
                    'reason_not_executed': 'Below confidence threshold'
                }
            
            # Get decision quality framework and evaluate
            quality_framework = get_decision_quality_framework()
            quality_score = quality_framework.evaluate_decision(
                decision_id=decision_id,
                ai_signal=ai_signal_data,
                market_data=market_data_snapshot,
                risk_metrics=risk_metrics,
                execution_details=execution_details
            )
            
            # Store the quality score for dashboard display
            if not hasattr(self, 'recent_quality_scores'):
                self.recent_quality_scores = []
            
            self.recent_quality_scores.append(quality_score)
            
            # Keep only last 20 scores for dashboard
            if len(self.recent_quality_scores) > 20:
                self.recent_quality_scores = self.recent_quality_scores[-20:]
            
            # Update stats with decision quality metrics
            self.stats["decision_quality_evaluations"] = self.stats.get("decision_quality_evaluations", 0) + 1
            self.stats["avg_decision_quality"] = sum(s.overall_score for s in self.recent_quality_scores) / len(self.recent_quality_scores)
            
            logger.info(f"📋 Decision Quality Evaluated: {quality_score.overall_score:.2f} ({quality_framework._get_quality_label(quality_score.overall_score)})")
            
        except Exception as e:
            logger.error(f"❌ Decision quality evaluation error: {e}")
    
    def _calculate_risk_reward_ratio(self, signal: TradingSignal, current_price: float) -> Optional[float]:
        """Calculate risk/reward ratio for a signal"""
        try:
            if not signal.target_price or not signal.stop_loss:
                return None
            
            if signal.signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                reward = signal.target_price - current_price
                risk = current_price - signal.stop_loss
            else:  # SELL signals
                reward = current_price - signal.target_price
                risk = signal.stop_loss - current_price
            
            if risk <= 0:
                return None
            
            return reward / risk
            
        except Exception as e:
            logger.error(f"❌ Risk/reward calculation error: {e}")
            return None
    
    # ============================================================================
    # END AI TRANSPARENCY METHODS
    # ============================================================================
    
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
        try:
            logger.info(f"📈 Executing market order: {order.side} {order.quantity} {order.symbol} at market")
            
            # TODO: Implement actual Sierra Chart execution
            # For now, simulate execution
            success = True  # Placeholder - replace with actual execution
            
            if success:
                logger.info(f"✅ Market order executed successfully")
                return True
            else:
                logger.error(f"❌ Market order execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Market order execution error: {e}")
            return False
    
    async def _execute_limit_order(self, order: TradeOrder):
        """Execute limit order"""
        try:
            logger.info(f"📈 Executing limit order: {order.side} {order.quantity} {order.symbol} at {order.price}")
            
            # TODO: Implement actual Sierra Chart execution
            # For now, simulate execution
            success = True  # Placeholder - replace with actual execution
            
            if success:
                logger.info(f"✅ Limit order placed successfully")
                return True
            else:
                logger.error(f"❌ Limit order execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Limit order execution error: {e}")
            return False
    
    async def _execute_adaptive_order(self, order: TradeOrder):
        """Execute adaptive order with intelligent timing"""
        try:
            logger.info(f"📈 Executing adaptive order: {order.side} {order.quantity} {order.symbol}")
            
            # For high-confidence signals, use market orders for speed
            # For medium confidence, use limit orders for better prices
            if hasattr(order, 'confidence') and order.confidence > 0.85:
                return await self._execute_market_order(order)
            else:
                return await self._execute_limit_order(order)
                
        except Exception as e:
            logger.error(f"❌ Adaptive order execution error: {e}")
            return False
    
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
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current trading positions"""
        if not self.state_manager:
            return []
        
        try:
            positions = self.state_manager.get_positions()
            # Convert Position objects to dictionaries
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "entry_time": pos.entry_time.isoformat() if pos.entry_time else None,
                    "side": "long" if pos.quantity > 0 else "short" if pos.quantity < 0 else "flat"
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

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
    # First try to get running instance from live trading integration
    try:
        from .live_trading_integration import get_running_service
        running_instance = get_running_service('trading_engine')
        if running_instance:
            return running_instance
    except ImportError:
        pass
    
    # Fallback to singleton pattern
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