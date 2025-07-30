"""
Kelly Manager - Unified ML-Enhanced Kelly Criterion System

Integrates probability estimation and Kelly calculation for optimal position sizing.
Provides simple API for integration with existing trading services.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .probability_estimator import ProbabilityEstimator
from .kelly_calculator import KellyCalculator

class KellyManager:
    """
    Unified manager for ML-Enhanced Kelly Criterion position sizing.
    
    Features:
    - Integrated probability estimation and Kelly calculation
    - Simple API for trading services
    - Performance monitoring and adaptation
    - Safety mechanisms and risk management
    """
    
    def __init__(self, model_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.probability_estimator = ProbabilityEstimator(model_path)
        self.kelly_calculator = KellyCalculator()
        
        # Configuration
        self.config = {
            'enabled': True,
            'min_training_trades': 100,
            'retraining_frequency_days': 30,
            'fallback_to_fixed': True,
            'fixed_position_pct': 0.02  # 2% fallback
        }
        
        # State tracking
        self.is_ready = False
        self.last_training_date = None
        self.total_predictions = 0
        
        self.logger.info("Kelly Manager initialized")
    
    async def calculate_position_size(self, 
                                    signal: Dict[str, Any],
                                    capital: float,
                                    market_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate optimal position size using ML-enhanced Kelly Criterion
        
        Args:
            signal: Trading signal with direction and confidence
            capital: Available trading capital
            market_data: Recent market data for analysis
            
        Returns:
            Position sizing recommendation with full analysis
        """
        if not self.config['enabled']:
            return self._get_fixed_size_fallback(capital, "Kelly sizing disabled")
        
        try:
            # Step 1: Estimate win probability
            prob_result = await self.probability_estimator.estimate_win_probability(
                market_data or [], signal
            )
            
            win_probability = prob_result['win_probability']
            prob_confidence = prob_result['confidence']
            
            # Step 2: Calculate Kelly position size
            kelly_result = await self.kelly_calculator.calculate_optimal_position_size(
                signal, win_probability, capital, market_data
            )
            
            # Step 3: Combine results
            self.total_predictions += 1
            
            result = {
                'position_size': kelly_result['position_size'],
                'position_pct': kelly_result['position_pct'],
                'method': 'kelly_ml_enhanced',
                
                # Kelly details
                'kelly_fraction': kelly_result['kelly_fraction'],
                'adjusted_kelly': kelly_result.get('adjusted_kelly', 0),
                'kelly_multiplier': kelly_result.get('kelly_multiplier', 1.0),
                
                # Probability details
                'win_probability': win_probability,
                'probability_confidence': prob_confidence,
                'probability_calibrated': prob_result['calibrated'],
                
                # Risk metrics
                'expected_return': kelly_result.get('expected_return', 0),
                'expected_loss': kelly_result.get('expected_loss', 0),
                'volatility': kelly_result.get('volatility', 0),
                'risk_metrics': kelly_result.get('risk_metrics', {}),
                
                # Signal analysis
                'signal_confidence': signal.get('confidence', 0),
                'signal_direction': signal.get('direction', 0),
                
                # Meta information
                'total_predictions': self.total_predictions,
                'components_ready': {
                    'probability_estimator': self.probability_estimator.is_trained,
                    'kelly_calculator': True
                },
                'reason': kelly_result.get('reason', 'Kelly calculation completed'),
                'source': 'kelly_manager'
            }
            
            self.logger.info(f"Kelly sizing: {result['position_pct']:.1%} of capital "
                           f"(${result['position_size']:.0f}) - Win prob: {win_probability:.1%}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Kelly Manager error: {e}")
            return self._get_fixed_size_fallback(capital, f"Kelly error: {str(e)}")
    
    def _get_fixed_size_fallback(self, capital: float, reason: str) -> Dict[str, Any]:
        """Get fixed size fallback when Kelly sizing fails"""
        if not self.config['fallback_to_fixed']:
            return {
                'position_size': 0.0,
                'position_pct': 0.0,
                'method': 'disabled',
                'reason': reason,
                'source': 'kelly_manager_disabled'
            }
        
        fixed_size = capital * self.config['fixed_position_pct']
        
        return {
            'position_size': fixed_size,
            'position_pct': self.config['fixed_position_pct'],
            'method': 'fixed_fallback',
            'kelly_fraction': 0.0,
            'win_probability': 0.5,
            'probability_confidence': 0.0,
            'components_ready': {
                'probability_estimator': self.probability_estimator.is_trained,
                'kelly_calculator': True
            },
            'reason': reason,
            'source': 'kelly_manager_fallback'
        }
    
    async def train_kelly_system(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the Kelly system on historical trade data
        
        Args:
            training_data: Historical trades with market data and outcomes
            
        Returns:
            Training results
        """
        if len(training_data) < self.config['min_training_trades']:
            return {
                'success': False,
                'message': f'Insufficient training data: {len(training_data)} < {self.config["min_training_trades"]}'
            }
        
        try:
            self.logger.info(f"Training Kelly system on {len(training_data)} trades")
            
            # Train probability estimator
            prob_result = await self.probability_estimator.train_probability_estimator(training_data)
            
            if not prob_result['success']:
                return {
                    'success': False,
                    'message': f'Probability estimator training failed: {prob_result["message"]}'
                }
            
            # Update Kelly calculator with historical outcomes
            for trade in training_data:
                outcome = trade.get('outcome', 0)
                pnl = trade.get('pnl', 0)
                self.kelly_calculator.update_trade_outcome(pnl, outcome > 0)
            
            # Mark as ready
            self.is_ready = True
            self.last_training_date = datetime.now()
            
            self.logger.info("Kelly system training completed successfully")
            
            return {
                'success': True,
                'probability_training': prob_result,
                'kelly_stats': self.kelly_calculator.get_performance_stats(),
                'training_trades': len(training_data),
                'training_date': self.last_training_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Kelly system training error: {e}")
            return {
                'success': False,
                'message': f'Training error: {str(e)}'
            }
    
    def update_trade_outcome(self, trade_result: Dict[str, Any]):
        """
        Update Kelly system with trade outcome for continuous learning
        
        Args:
            trade_result: Trade outcome with PnL and win/loss information
        """
        try:
            pnl = trade_result.get('pnl', 0)
            was_winning = trade_result.get('outcome', pnl) > 0
            
            # Update Kelly calculator
            self.kelly_calculator.update_trade_outcome(pnl, was_winning)
            
            self.logger.debug(f"Updated Kelly system with trade outcome: PnL={pnl:.2f}, Win={was_winning}")
            
        except Exception as e:
            self.logger.error(f"Trade outcome update error: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive Kelly system status"""
        return {
            'enabled': self.config['enabled'],
            'is_ready': self.is_ready,
            'last_training_date': self.last_training_date.isoformat() if self.last_training_date else None,
            'total_predictions': self.total_predictions,
            
            # Component status
            'probability_estimator': self.probability_estimator.get_performance_stats(),
            'kelly_calculator': self.kelly_calculator.get_performance_stats(),
            
            # Configuration
            'config': self.config
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for dashboard display"""
        kelly_stats = self.kelly_calculator.get_performance_stats()
        prob_stats = self.probability_estimator.get_performance_stats()
        
        return {
            'system_ready': self.is_ready,
            'total_predictions': self.total_predictions,
            
            # Performance metrics
            'win_rate': kelly_stats.get('win_rate', 0),
            'total_pnl': kelly_stats.get('total_pnl', 0),
            'current_drawdown': kelly_stats.get('current_drawdown', 0),
            'sharpe_ratio': kelly_stats.get('sharpe_ratio_approx', 0),
            
            # Kelly metrics
            'kelly_multiplier': kelly_stats.get('kelly_multiplier', 1.0),
            'avg_position_size': kelly_stats.get('avg_position_size', 0),
            
            # Probability metrics
            'probability_predictions': prob_stats.get('predictions_made', 0),
            'probability_trained': prob_stats.get('is_trained', False),
            
            # Status
            'enabled': self.config['enabled'],
            'last_update': datetime.now().isoformat()
        }
    
    def set_config(self, **kwargs):
        """Update Kelly Manager configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated Kelly Manager config: {key} = {value}")
            
            # Pass relevant configs to components
            if key.startswith('kelly_'):
                kelly_key = key[6:]  # Remove 'kelly_' prefix
                self.kelly_calculator.set_config(**{kelly_key: value})
            elif key.startswith('prob_'):
                # Future: pass to probability estimator if it supports config
                pass