#!/usr/bin/env python3
"""
Position Sizing Service

Integrates ML-Enhanced Kelly Criterion with LSTM and Ensemble predictions
to provide optimal position sizing recommendations.

This service:
- Connects to LSTM and Ensemble predictors
- Applies Kelly Criterion with ML probabilities
- Integrates with Risk Manager constraints
- Provides real-time position sizing decisions
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np

from ..core.base_service import BaseService
from ..ml.kelly_criterion import get_kelly_criterion, KellyPosition
from .risk_manager import get_risk_manager
from .state_manager import get_state_manager
from ..core.symbol_integration import get_symbol_integration

# Import ML components via absolute paths
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
from capabilities.ensemble.ensemble_manager import EnsembleManager

logger = logging.getLogger(__name__)

class PositionSizingService(BaseService):
    """
    Service for ML-enhanced optimal position sizing
    
    Combines:
    - LSTM time series predictions
    - Ensemble model consensus
    - Kelly Criterion mathematics
    - Risk management constraints
    """
    
    def __init__(self):
        """Initialize Position Sizing Service"""
        super().__init__("PositionSizingService")
        
        # ML components
        self.kelly_criterion = get_kelly_criterion()
        self.lstm_predictor = None
        self.ensemble_predictor = None
        
        # Service connections
        self.risk_manager = None
        self.state_manager = None
        self.symbol_integration = get_symbol_integration()
        
        # Configuration
        self.config = {
            'min_confidence': 0.6,
            'max_position_size': 10,
            'use_half_kelly': True,
            'enable_ml_sizing': True
        }
        
        # Performance tracking
        self.sizing_history = []
        self.performance_metrics = {
            'total_recommendations': 0,
            'avg_kelly_fraction': 0.0,
            'avg_confidence': 0.0,
            'positions_accepted': 0,
            'positions_rejected': 0
        }
        
        # Mark service as using centralized symbol management
        self.symbol_integration.mark_service_migrated('position_sizing')
        
        logger.info("Position Sizing Service initialized")
    
    async def _initialize(self):
        """Initialize service components"""
        try:
            # Get ML predictors
            self.lstm_predictor = LSTMPredictor()
            self.ensemble_predictor = EnsembleManager()
            
            # Connect ML predictors to Kelly Criterion
            self.kelly_criterion.lstm_predictor = self.lstm_predictor
            self.kelly_criterion.ensemble_predictor = self.ensemble_predictor
            
            # Get service connections
            self.risk_manager = get_risk_manager()
            self.state_manager = get_state_manager()
            
            logger.info("Position Sizing Service components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def _start_service(self):
        """Start service-specific functionality"""
        logger.info("Position Sizing Service started")
        
        # Start performance tracking loop
        asyncio.create_task(self._performance_tracking_loop())
    
    async def _stop_service(self):
        """Stop service-specific functionality"""
        logger.info("Position Sizing Service stopped")
    
    async def _cleanup(self):
        """Cleanup service resources"""
        # Save performance history
        logger.info("Position Sizing Service cleanup completed")
    
    async def calculate_optimal_position(self,
                                       symbol: str,
                                       current_price: float,
                                       market_data: Optional[Dict[str, Any]] = None) -> KellyPosition:
        """
        Calculate optimal position size for a symbol
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            market_data: Additional market data for predictions
            
        Returns:
            KellyPosition with sizing recommendation
        """
        try:
            # Validate symbol
            tradeable_symbols = self.symbol_integration.get_trading_engine_symbols()
            if symbol not in tradeable_symbols:
                logger.warning(f"Symbol {symbol} not in tradeable list")
                return self.kelly_criterion._create_zero_position(symbol, 0.5, 0.0)
            
            # Get LSTM prediction
            lstm_prediction = await self._get_lstm_prediction(symbol, market_data)
            
            # Get Ensemble prediction
            ensemble_prediction = await self._get_ensemble_prediction(symbol, market_data)
            
            # Get risk parameters
            risk_params = await self._get_risk_parameters()
            
            # Calculate Kelly position
            kelly_position = self.kelly_criterion.calculate_position_size(
                symbol=symbol,
                current_price=current_price,
                lstm_prediction=lstm_prediction,
                ensemble_prediction=ensemble_prediction,
                risk_params=risk_params
            )
            
            # Validate against risk constraints
            validated_position = await self._validate_position_size(kelly_position)
            
            # Track recommendation
            await self._track_recommendation(validated_position)
            
            return validated_position
            
        except Exception as e:
            logger.error(f"Position calculation error: {e}")
            return self.kelly_criterion._create_zero_position(symbol, 0.5, 0.0)
    
    async def _get_lstm_prediction(self, 
                                  symbol: str,
                                  market_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get LSTM prediction for symbol"""
        try:
            if not self.lstm_predictor:
                return {'probability': 0.5, 'confidence': 0.0}
            
            # Get LSTM prediction
            prediction = self.lstm_predictor.predict_single(symbol=symbol)
            
            # Convert to probability format
            if 'direction' in prediction:
                # LSTM returns direction (-1, 0, 1) with confidence
                direction = prediction['direction']
                confidence = prediction.get('confidence', 0.5)
                
                # Convert to win probability
                if direction > 0:
                    probability = 0.5 + (confidence * 0.5)
                elif direction < 0:
                    probability = 0.5 - (confidence * 0.5)
                else:
                    probability = 0.5
                
                return {
                    'probability': probability,
                    'confidence': confidence,
                    'direction': direction,
                    'model': 'LSTM'
                }
            
            return prediction
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return {'probability': 0.5, 'confidence': 0.0}
    
    async def _get_ensemble_prediction(self,
                                     symbol: str,
                                     market_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get Ensemble prediction for symbol"""
        try:
            if not self.ensemble_predictor:
                return {'probability': 0.5, 'confidence': 0.0}
            
            # Get ensemble prediction
            prediction = self.ensemble_predictor.predict_single(symbol=symbol)
            
            # Ensemble returns consensus prediction
            if 'consensus_direction' in prediction:
                direction = prediction['consensus_direction']
                confidence = prediction.get('consensus_confidence', 0.5)
                
                # Convert to win probability
                if direction > 0:
                    probability = 0.5 + (confidence * 0.5)
                elif direction < 0:
                    probability = 0.5 - (confidence * 0.5)
                else:
                    probability = 0.5
                
                return {
                    'probability': probability,
                    'confidence': confidence,
                    'direction': direction,
                    'model': 'Ensemble',
                    'models_agree': prediction.get('models_agree', 0)
                }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Ensemble prediction error: {e}")
            return {'probability': 0.5, 'confidence': 0.0}
    
    async def _get_risk_parameters(self) -> Dict[str, Any]:
        """Get current risk parameters"""
        try:
            if not self.risk_manager or not self.state_manager:
                return {}
            
            # Get risk status
            risk_status = self.risk_manager.get_risk_status()
            
            # Get current state
            state = self.state_manager.get_current_state()
            pnl = state.get('pnl', {})
            
            # Calculate current drawdown
            total_pnl = pnl.get('total', 0.0)
            if total_pnl < 0:
                # Simplified drawdown calculation
                drawdown = abs(total_pnl) / 100000.0  # Assume $100k capital
            else:
                drawdown = 0.0
            
            # Get risk parameters
            risk_params = self.state_manager.get_risk_parameters()
            
            return {
                'max_position_size': risk_params.max_position_size,
                'current_drawdown': drawdown,
                'risk_budget_used': risk_status.get('risk_budget_used', 0.0),
                'volatility_multiplier': 1.0,  # Could be enhanced with market volatility
                'circuit_breaker_active': risk_status.get('circuit_breaker_active', False)
            }
            
        except Exception as e:
            logger.error(f"Risk parameters error: {e}")
            return {'max_position_size': 1}
    
    async def _validate_position_size(self, position: KellyPosition) -> KellyPosition:
        """Validate position size against risk constraints"""
        try:
            if not self.risk_manager:
                return position
            
            # Check if circuit breaker is active
            risk_status = self.risk_manager.get_risk_status()
            if risk_status.get('circuit_breaker_active', False):
                logger.warning("Circuit breaker active - zero position")
                return self.kelly_criterion._create_zero_position(
                    position.symbol, 
                    position.win_probability,
                    position.confidence_score
                )
            
            # Validate against maximum position size
            risk_params = await self._get_risk_parameters()
            max_size = risk_params.get('max_position_size', 10)
            
            if position.recommended_size > max_size:
                # Adjust to maximum allowed
                position.risk_adjusted_size = max_size
                position.calculation_details['risk_adjustment'] = f"Capped at max size: {max_size}"
            
            return position
            
        except Exception as e:
            logger.error(f"Position validation error: {e}")
            return position
    
    async def _track_recommendation(self, position: KellyPosition):
        """Track position sizing recommendation"""
        try:
            # Add to history
            self.sizing_history.append({
                'timestamp': position.timestamp,
                'symbol': position.symbol,
                'recommended_size': position.recommended_size,
                'kelly_fraction': position.kelly_fraction,
                'confidence': position.confidence_score,
                'win_probability': position.win_probability
            })
            
            # Update metrics
            self.performance_metrics['total_recommendations'] += 1
            
            # Update rolling averages
            recent = self.sizing_history[-100:]  # Last 100 recommendations
            if recent:
                self.performance_metrics['avg_kelly_fraction'] = np.mean(
                    [r['kelly_fraction'] for r in recent]
                )
                self.performance_metrics['avg_confidence'] = np.mean(
                    [r['confidence'] for r in recent]
                )
            
            if position.recommended_size > 0:
                self.performance_metrics['positions_accepted'] += 1
            else:
                self.performance_metrics['positions_rejected'] += 1
                
        except Exception as e:
            logger.error(f"Tracking error: {e}")
    
    async def _performance_tracking_loop(self):
        """Track performance metrics periodically"""
        while self.running:
            try:
                # Log performance summary every 5 minutes
                await asyncio.sleep(300)
                
                if self.performance_metrics['total_recommendations'] > 0:
                    accept_rate = (
                        self.performance_metrics['positions_accepted'] /
                        self.performance_metrics['total_recommendations']
                    )
                    
                    logger.info(
                        f"Position Sizing Performance: "
                        f"Total={self.performance_metrics['total_recommendations']}, "
                        f"Accept Rate={accept_rate:.1%}, "
                        f"Avg Kelly={self.performance_metrics['avg_kelly_fraction']:.3f}, "
                        f"Avg Confidence={self.performance_metrics['avg_confidence']:.2f}"
                    )
                
            except Exception as e:
                logger.error(f"Performance tracking error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'service': 'PositionSizingService',
            'running': True,  # Service is always running when initialized
            'ml_enabled': self.config['enable_ml_sizing'],
            'performance_metrics': self.performance_metrics,
            'recent_recommendations': len(self.sizing_history),
            'lstm_connected': self.lstm_predictor is not None,
            'ensemble_connected': self.ensemble_predictor is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    async def update_trade_result(self,
                                symbol: str,
                                entry_price: float,
                                exit_price: float,
                                size: int,
                                predicted_direction: int):
        """Update Kelly Criterion with trade result"""
        try:
            self.kelly_criterion.update_performance(
                symbol=symbol,
                entry_price=entry_price,
                exit_price=exit_price,
                size=size,
                predicted_direction=predicted_direction
            )
            
            logger.info(f"Trade result updated for {symbol}")
            
        except Exception as e:
            logger.error(f"Trade result update error: {e}")

# Singleton instance
_position_sizing_service = None

def get_position_sizing_service() -> PositionSizingService:
    """Get or create Position Sizing Service instance"""
    global _position_sizing_service
    if _position_sizing_service is None:
        _position_sizing_service = PositionSizingService()
    return _position_sizing_service

async def create_position_sizing_service() -> PositionSizingService:
    """Create and start Position Sizing Service"""
    service = get_position_sizing_service()
    await service.start()
    return service