#!/usr/bin/env python3
"""
ML-Enhanced End-to-End Trading Workflow
=======================================

Complete trading workflow integrating LSTM, Ensemble, Kelly Criterion,
and Trading Engine for automated ML-driven trading decisions.

Flow:
1. Market Data → LSTM Prediction
2. Market Data → Ensemble Prediction  
3. LSTM + Ensemble → Kelly Position Sizing
4. Kelly + Risk Management → Trade Execution
5. Trade Result → ML Performance Feedback
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .ml_performance_monitor import get_ml_performance_monitor, MetricType
from .position_sizing_service import get_position_sizing_service
from .trading_engine import get_trading_engine
from .ai_brain_service import get_ai_brain_service
from .market_data_service import get_market_data_service
from .state_manager import get_state_manager
from .risk_manager import get_risk_manager
from ..ml.kelly_criterion import KellyPosition

logger = logging.getLogger(__name__)

class TradeSignal(Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"

@dataclass
class MLTradeDecision:
    """Complete ML-enhanced trade decision"""
    timestamp: datetime
    symbol: str
    signal: TradeSignal
    confidence: float
    
    # ML Predictions
    lstm_prediction: Dict[str, Any]
    ensemble_prediction: Dict[str, Any]
    
    # Kelly Position Sizing
    kelly_position: KellyPosition
    
    # Risk Assessment
    risk_approved: bool
    risk_reason: str
    
    # Execution Details
    recommended_size: int
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Performance Tracking
    execution_latency_ms: float = 0.0
    workflow_id: str = ""

@dataclass
class WorkflowMetrics:
    """Workflow performance metrics"""
    total_decisions: int = 0
    successful_predictions: int = 0
    trades_executed: int = 0
    avg_decision_time_ms: float = 0.0
    avg_confidence: float = 0.0
    kelly_utilization_rate: float = 0.0
    risk_approval_rate: float = 0.0

class MLTradingWorkflow:
    """
    ML-Enhanced End-to-End Trading Workflow
    
    Orchestrates the complete trading decision process:
    - Collects real-time market data
    - Generates LSTM and Ensemble predictions
    - Calculates optimal position sizing with Kelly Criterion
    - Applies risk management filters
    - Executes trades through Trading Engine
    - Tracks performance and feeds back to ML models
    """
    
    def __init__(self):
        """Initialize ML Trading Workflow"""
        self.status = WorkflowStatus.IDLE
        self.running = False
        
        # Service connections
        self.performance_monitor = get_ml_performance_monitor()
        self.position_sizing = get_position_sizing_service()
        self.trading_engine = get_trading_engine()
        self.ai_brain = get_ai_brain_service()
        self.market_data = get_market_data_service()
        self.state_manager = get_state_manager()
        self.risk_manager = get_risk_manager()
        
        # Workflow configuration
        self.config = {
            'min_confidence_threshold': 0.65,  # Minimum confidence to trade
            'max_position_size': 5,  # Maximum contracts
            'decision_interval_seconds': 60,  # How often to make decisions
            'enable_auto_trading': True,  # Automatic execution enabled
            'max_daily_trades': 20,  # Risk limit
            'enable_ml_feedback': True  # Feed results back to ML models
        }
        
        # Performance tracking
        self.metrics = WorkflowMetrics()
        self.decision_history: List[MLTradeDecision] = []
        self.active_positions: Dict[str, Dict] = {}
        
        # Background tasks
        self.workflow_task = None
        self.monitoring_task = None
        
        logger.info("ML Trading Workflow initialized")
    
    async def start(self):
        """Start the ML trading workflow"""
        if self.running:
            return
        
        self.running = True
        self.status = WorkflowStatus.IDLE
        
        # Start background tasks
        self.workflow_task = asyncio.create_task(self._workflow_loop())
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("ML Trading Workflow started")
    
    async def stop(self):
        """Stop the ML trading workflow"""
        self.running = False
        self.status = WorkflowStatus.IDLE
        
        # Cancel background tasks
        for task in [self.workflow_task, self.monitoring_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("ML Trading Workflow stopped")
    
    async def _workflow_loop(self):
        """Main workflow execution loop"""
        while self.running:
            try:
                start_time = time.time()
                self.status = WorkflowStatus.PROCESSING
                
                # Execute trading decision workflow
                decision = await self._execute_trading_decision()
                
                if decision:
                    # Record decision
                    self.decision_history.append(decision)
                    self.metrics.total_decisions += 1
                    
                    # Update performance metrics
                    execution_time = (time.time() - start_time) * 1000
                    await self._update_workflow_metrics(decision, execution_time)
                    
                    # Log decision
                    logger.info(
                        f"Trading Decision: {decision.signal.value} {decision.symbol} "
                        f"Size: {decision.recommended_size} "
                        f"Confidence: {decision.confidence:.2%} "
                        f"Kelly: {decision.kelly_position.kelly_fraction:.3f}"
                    )
                
                self.status = WorkflowStatus.WAITING
                
                # Wait for next decision interval
                await asyncio.sleep(self.config['decision_interval_seconds'])
                
            except Exception as e:
                logger.error(f"Workflow loop error: {e}")
                self.status = WorkflowStatus.ERROR
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _execute_trading_decision(self) -> Optional[MLTradeDecision]:
        """Execute complete trading decision workflow"""
        try:
            workflow_start = time.time()
            workflow_id = f"workflow_{int(workflow_start)}"
            
            # Step 1: Get current market data
            market_data = await self._get_market_data()
            if not market_data:
                logger.warning("No market data available")
                return None
            
            symbol = market_data.get('symbol', 'NQU25-CME')
            current_price = market_data.get('price', market_data.get('last_price', 0.0))
            
            if current_price <= 0:
                logger.warning(f"Invalid price data: {current_price}")
                return None
            
            # Step 2: Get LSTM prediction
            lstm_start = time.time()
            lstm_prediction = await self._get_lstm_prediction(symbol, market_data)
            lstm_latency = (time.time() - lstm_start) * 1000
            
            await self.performance_monitor.record_metric(
                "lstm", MetricType.LATENCY, lstm_latency, symbol
            )
            
            # Step 3: Get Ensemble prediction
            ensemble_start = time.time()
            ensemble_prediction = await self._get_ensemble_prediction(symbol, market_data)
            ensemble_latency = (time.time() - ensemble_start) * 1000
            
            await self.performance_monitor.record_metric(
                "ensemble", MetricType.LATENCY, ensemble_latency, symbol
            )
            
            # Step 4: Calculate Kelly position sizing
            kelly_start = time.time()
            kelly_position = await self.position_sizing.calculate_optimal_position(
                symbol=symbol,
                current_price=current_price,
                market_data=market_data
            )
            kelly_latency = (time.time() - kelly_start) * 1000
            
            await self.performance_monitor.record_metric(
                "kelly", MetricType.LATENCY, kelly_latency, symbol
            )
            await self.performance_monitor.record_metric(
                "kelly", MetricType.KELLY_FRACTION, kelly_position.kelly_fraction, symbol
            )
            
            # Step 5: Determine trading signal and confidence
            signal, combined_confidence = self._determine_trading_signal(
                lstm_prediction, ensemble_prediction, kelly_position
            )
            
            # Step 6: Apply risk management
            risk_approved, risk_reason = await self._apply_risk_management(
                signal, kelly_position, current_price
            )
            
            # Step 7: Create trade decision
            decision = MLTradeDecision(
                timestamp=datetime.now(),
                symbol=symbol,
                signal=signal,
                confidence=combined_confidence,
                lstm_prediction=lstm_prediction,
                ensemble_prediction=ensemble_prediction,
                kelly_position=kelly_position,
                risk_approved=risk_approved,
                risk_reason=risk_reason,
                recommended_size=kelly_position.recommended_size if risk_approved else 0,
                entry_price=current_price,
                execution_latency_ms=(time.time() - workflow_start) * 1000,
                workflow_id=workflow_id
            )
            
            # Step 8: Execute trade if approved and auto-trading enabled
            if (risk_approved and 
                self.config['enable_auto_trading'] and 
                combined_confidence >= self.config['min_confidence_threshold']):
                
                await self._execute_trade(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Trading decision workflow error: {e}")
            return None
    
    async def _get_market_data(self) -> Optional[Dict[str, Any]]:
        """Get current market data"""
        try:
            if not self.market_data:
                return None
            
            # Get latest market data for primary symbol
            data = await self.market_data.get_current_data("NQU25-CME")
            return data
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return None
    
    async def _get_lstm_prediction(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Get LSTM prediction"""
        try:
            if not self.ai_brain:
                return {'direction': 0, 'confidence': 0.0, 'error': 'AI Brain unavailable'}
            
            # Get LSTM prediction through AI Brain
            prediction = await self.ai_brain.get_ml_prediction(symbol, "lstm")
            
            # Record confidence metric
            if prediction and 'confidence' in prediction:
                await self.performance_monitor.record_metric(
                    "lstm", MetricType.CONFIDENCE, prediction['confidence'], symbol
                )
            
            return prediction or {'direction': 0, 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return {'direction': 0, 'confidence': 0.0, 'error': str(e)}
    
    async def _get_ensemble_prediction(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Get Ensemble prediction"""
        try:
            if not self.ai_brain:
                return {'consensus_direction': 0, 'consensus_confidence': 0.0, 'error': 'AI Brain unavailable'}
            
            # Get Ensemble prediction through AI Brain
            prediction = await self.ai_brain.get_ml_prediction(symbol, "ensemble")
            
            # Record confidence metric
            if prediction and 'consensus_confidence' in prediction:
                await self.performance_monitor.record_metric(
                    "ensemble", MetricType.CONFIDENCE, prediction['consensus_confidence'], symbol
                )
            
            return prediction or {'consensus_direction': 0, 'consensus_confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Ensemble prediction error: {e}")
            return {'consensus_direction': 0, 'consensus_confidence': 0.0, 'error': str(e)}
    
    def _determine_trading_signal(self, 
                                lstm_pred: Dict,
                                ensemble_pred: Dict,
                                kelly_pos: KellyPosition) -> Tuple[TradeSignal, float]:
        """Determine trading signal from ML predictions"""
        try:
            # Extract directions and confidences
            lstm_dir = lstm_pred.get('direction', 0)
            lstm_conf = lstm_pred.get('confidence', 0.0)
            
            ensemble_dir = ensemble_pred.get('consensus_direction', 0)
            ensemble_conf = ensemble_pred.get('consensus_confidence', 0.0)
            
            # Combine predictions (weighted by confidence)
            total_confidence = lstm_conf + ensemble_conf
            if total_confidence > 0:
                combined_direction = (lstm_dir * lstm_conf + ensemble_dir * ensemble_conf) / total_confidence
                combined_confidence = total_confidence / 2.0
            else:
                combined_direction = 0
                combined_confidence = 0.0
            
            # Factor in Kelly Criterion confidence
            kelly_confidence = kelly_pos.confidence_score
            final_confidence = (combined_confidence + kelly_confidence) / 2.0
            
            # Determine signal
            if combined_direction > 0.1 and kelly_pos.recommended_size > 0:
                signal = TradeSignal.BUY
            elif combined_direction < -0.1 and kelly_pos.recommended_size > 0:
                signal = TradeSignal.SELL
            else:
                signal = TradeSignal.HOLD
            
            return signal, final_confidence
            
        except Exception as e:
            logger.error(f"Signal determination error: {e}")
            return TradeSignal.HOLD, 0.0
    
    async def _apply_risk_management(self, 
                                   signal: TradeSignal,
                                   kelly_pos: KellyPosition,
                                   current_price: float) -> Tuple[bool, str]:
        """Apply risk management filters"""
        try:
            # Check if trading is allowed
            if signal == TradeSignal.HOLD:
                return False, "Hold signal - no trade"
            
            # Check Kelly position size
            if kelly_pos.recommended_size <= 0:
                return False, "Kelly Criterion recommends zero position"
            
            # Check confidence threshold
            if kelly_pos.confidence_score < self.config['min_confidence_threshold']:
                return False, f"Confidence {kelly_pos.confidence_score:.2%} below threshold"
            
            # Check position size limits
            if kelly_pos.recommended_size > self.config['max_position_size']:
                return False, f"Position size {kelly_pos.recommended_size} exceeds limit"
            
            # Check daily trade limit
            today_trades = len([
                d for d in self.decision_history 
                if (d.timestamp.date() == datetime.now().date() and 
                    d.risk_approved and d.recommended_size > 0)
            ])
            
            if today_trades >= self.config['max_daily_trades']:
                return False, f"Daily trade limit reached: {today_trades}"
            
            # Check risk manager approval
            if self.risk_manager:
                risk_status = self.risk_manager.get_risk_status()
                if risk_status.get('circuit_breaker_active', False):
                    return False, "Risk circuit breaker active"
            
            return True, "Risk management approved"
            
        except Exception as e:
            logger.error(f"Risk management error: {e}")
            return False, f"Risk management error: {str(e)}"
    
    async def _execute_trade(self, decision: MLTradeDecision):
        """Execute the trading decision"""
        try:
            if not self.trading_engine or decision.recommended_size <= 0:
                return
            
            # Prepare trade parameters
            trade_params = {
                'symbol': decision.symbol,
                'action': decision.signal.value,
                'quantity': decision.recommended_size,
                'price': decision.entry_price,
                'order_type': 'market',
                'source': 'ml_workflow',
                'confidence': decision.confidence,
                'kelly_fraction': decision.kelly_position.kelly_fraction
            }
            
            # Execute through trading engine
            result = await self.trading_engine.execute_trade(trade_params)
            
            if result.get('success', False):
                self.metrics.trades_executed += 1
                
                # Track active position
                self.active_positions[decision.symbol] = {
                    'entry_time': decision.timestamp,
                    'entry_price': decision.entry_price,
                    'size': decision.recommended_size,
                    'direction': decision.signal.value,
                    'kelly_fraction': decision.kelly_position.kelly_fraction
                }
                
                logger.info(f"Trade executed: {decision.signal.value} {decision.recommended_size} {decision.symbol}")
            else:
                logger.warning(f"Trade execution failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
    
    async def _update_workflow_metrics(self, decision: MLTradeDecision, execution_time_ms: float):
        """Update workflow performance metrics"""
        try:
            # Update decision time
            if self.metrics.total_decisions > 0:
                self.metrics.avg_decision_time_ms = (
                    (self.metrics.avg_decision_time_ms * (self.metrics.total_decisions - 1) + execution_time_ms) /
                    self.metrics.total_decisions
                )
            else:
                self.metrics.avg_decision_time_ms = execution_time_ms
            
            # Update confidence
            if self.metrics.total_decisions > 0:
                self.metrics.avg_confidence = (
                    (self.metrics.avg_confidence * (self.metrics.total_decisions - 1) + decision.confidence) /
                    self.metrics.total_decisions
                )
            else:
                self.metrics.avg_confidence = decision.confidence
            
            # Update approval rates
            if decision.risk_approved:
                self.metrics.risk_approval_rate = (
                    (self.metrics.risk_approval_rate * (self.metrics.total_decisions - 1) + 1.0) /
                    self.metrics.total_decisions
                )
            else:
                self.metrics.risk_approval_rate = (
                    (self.metrics.risk_approval_rate * (self.metrics.total_decisions - 1) + 0.0) /
                    self.metrics.total_decisions
                )
            
            # Kelly utilization rate
            if decision.kelly_position.recommended_size > 0:
                self.metrics.kelly_utilization_rate = (
                    (self.metrics.kelly_utilization_rate * (self.metrics.total_decisions - 1) + 1.0) /
                    self.metrics.total_decisions
                )
            else:
                self.metrics.kelly_utilization_rate = (
                    (self.metrics.kelly_utilization_rate * (self.metrics.total_decisions - 1) + 0.0) /
                    self.metrics.total_decisions
                )
            
            # Record pipeline metrics
            await self.performance_monitor.record_metric(
                "pipeline", MetricType.LATENCY, execution_time_ms, decision.symbol
            )
            
        except Exception as e:
            logger.error(f"Failed to update workflow metrics: {e}")
    
    async def _monitoring_loop(self):
        """Monitoring and performance tracking loop"""
        while self.running:
            try:
                # Log workflow status every 5 minutes
                logger.info(
                    f"ML Workflow Status: {self.status.value} | "
                    f"Decisions: {self.metrics.total_decisions} | "
                    f"Trades: {self.metrics.trades_executed} | "
                    f"Avg Confidence: {self.metrics.avg_confidence:.2%} | "
                    f"Approval Rate: {self.metrics.risk_approval_rate:.1%}"
                )
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(300)
    
    def get_status(self) -> Dict[str, Any]:
        """Get workflow status and metrics"""
        return {
            'workflow_status': self.status.value,
            'running': self.running,
            'configuration': self.config,
            'metrics': asdict(self.metrics),
            'recent_decisions': len([
                d for d in self.decision_history 
                if d.timestamp >= datetime.now() - timedelta(hours=24)
            ]),
            'active_positions': len(self.active_positions),
            'timestamp': datetime.now().isoformat()
        }
    
    async def manual_decision(self, symbol: str = "NQU25-CME") -> Optional[MLTradeDecision]:
        """Manually trigger a trading decision for testing"""
        try:
            old_auto_trading = self.config['enable_auto_trading']
            self.config['enable_auto_trading'] = False  # Disable auto execution
            
            decision = await self._execute_trading_decision()
            
            self.config['enable_auto_trading'] = old_auto_trading  # Restore setting
            
            return decision
            
        except Exception as e:
            logger.error(f"Manual decision error: {e}")
            return None

# Singleton instance
_ml_trading_workflow = None

def get_ml_trading_workflow() -> MLTradingWorkflow:
    """Get or create ML Trading Workflow instance"""
    global _ml_trading_workflow
    if _ml_trading_workflow is None:
        _ml_trading_workflow = MLTradingWorkflow()
    return _ml_trading_workflow

async def create_ml_trading_workflow() -> MLTradingWorkflow:
    """Create and start ML Trading Workflow"""
    workflow = get_ml_trading_workflow()
    await workflow.start()
    return workflow