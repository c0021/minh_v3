"""
ML-Enhanced Kelly Criterion Calculator

Calculates optimal position sizes using the Kelly Criterion with ML-based win probability
and risk adjustments for trading safety.
"""

import numpy as np
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import json

class KellyCalculator:
    """
    ML-Enhanced Kelly Criterion calculator for optimal position sizing.
    
    Features:
    - Quarter Kelly (25%) implementation for safety
    - Volatility scaling and correlation adjustments
    - Maximum position constraints and circuit breakers
    - Risk management with drawdown protection
    - Performance tracking and adaptation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Kelly configuration
        self.config = {
            'kelly_fraction': 0.25,  # Quarter Kelly for safety
            'max_position_pct': 0.05,  # Maximum 5% of capital
            'min_win_probability': 0.51,  # Minimum edge required
            'risk_free_rate': 0.02,  # Annual risk-free rate
            'volatility_lookback_days': 30,
            'correlation_threshold': 0.7,
            'drawdown_threshold': 0.10,  # 10% drawdown triggers reduction
            'circuit_breaker_loss': 0.03,  # 3% daily loss stops new positions
            'min_confidence': 0.6  # Minimum signal confidence for Kelly sizing
        }
        
        # Risk tracking
        self.position_history = deque(maxlen=1000)
        self.pnl_history = deque(maxlen=1000)
        self.volatility_history = deque(maxlen=100)
        self.current_drawdown = 0.0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        
        # Adaptive parameters
        self.kelly_multiplier = 1.0  # Adaptive multiplier based on performance
        self.volatility_estimate = 0.02  # Current volatility estimate
        
        self.logger.info("Kelly Calculator initialized")
    
    async def calculate_optimal_position_size(self, 
                                            signal: Dict[str, Any],
                                            win_probability: float,
                                            capital: float,
                                            market_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate optimal position size using ML-enhanced Kelly Criterion
        
        Args:
            signal: Trading signal with direction and confidence
            win_probability: ML-estimated win probability
            capital: Available trading capital
            market_data: Recent market data for volatility calculation
            
        Returns:
            Position sizing recommendation with risk metrics
        """
        try:
            # Update daily PnL tracking
            self._update_daily_tracking()
            
            # Initial safety checks
            safety_check = self._perform_safety_checks(signal, win_probability, capital)
            if not safety_check['passed']:
                return {
                    'position_size': 0.0,
                    'position_pct': 0.0,
                    'kelly_fraction': 0.0,
                    'win_probability': win_probability,
                    'reason': safety_check['reason'],
                    'risk_metrics': self._get_risk_metrics(),
                    'source': 'kelly_safety_block'
                }
            
            # Calculate market volatility
            volatility = self._calculate_volatility(market_data) if market_data else self.volatility_estimate
            self.volatility_estimate = volatility
            
            # Extract signal parameters
            signal_direction = signal.get('direction', 0)
            signal_confidence = signal.get('confidence', 0.5)
            
            if signal_direction == 0 or signal_confidence < self.config['min_confidence']:
                return {
                    'position_size': 0.0,
                    'position_pct': 0.0,
                    'kelly_fraction': 0.0,
                    'win_probability': win_probability,
                    'reason': 'Insufficient signal strength',
                    'risk_metrics': self._get_risk_metrics(),
                    'source': 'kelly_no_signal'
                }
            
            # Estimate expected returns and loss
            expected_return, expected_loss = self._estimate_trade_outcomes(
                signal, market_data, volatility
            )
            
            # Calculate Kelly fraction
            kelly_fraction = self._calculate_kelly_fraction(
                win_probability, expected_return, expected_loss
            )
            
            # Apply safety adjustments
            adjusted_kelly = self._apply_safety_adjustments(
                kelly_fraction, signal_confidence, volatility
            )
            
            # Calculate position size
            position_pct = min(adjusted_kelly, self.config['max_position_pct'])
            position_size = capital * position_pct
            
            # Volatility adjustment
            volatility_adjusted_size = self._adjust_for_volatility(
                position_size, volatility
            )
            
            # Final position
            final_position_size = volatility_adjusted_size
            final_position_pct = final_position_size / capital if capital > 0 else 0
            
            # Track position
            self._track_position({
                'timestamp': datetime.now(),
                'position_size': final_position_size,
                'position_pct': final_position_pct,
                'kelly_fraction': kelly_fraction,
                'win_probability': win_probability,
                'volatility': volatility,
                'signal_confidence': signal_confidence
            })
            
            return {
                'position_size': final_position_size,
                'position_pct': final_position_pct,
                'kelly_fraction': kelly_fraction,
                'adjusted_kelly': adjusted_kelly,
                'win_probability': win_probability,
                'expected_return': expected_return,
                'expected_loss': expected_loss,
                'volatility': volatility,
                'signal_confidence': signal_confidence,
                'kelly_multiplier': self.kelly_multiplier,
                'risk_metrics': self._get_risk_metrics(),
                'reason': 'Kelly calculation successful',
                'source': 'kelly_ml_enhanced'
            }
            
        except Exception as e:
            self.logger.error(f"Kelly calculation error: {e}")
            # Safe fallback
            safe_size = capital * 0.01  # 1% fallback
            return {
                'position_size': safe_size,
                'position_pct': 0.01,
                'kelly_fraction': 0.0,
                'win_probability': win_probability,
                'reason': f'Calculation error, using 1% fallback: {str(e)}',
                'risk_metrics': self._get_risk_metrics(),
                'source': 'kelly_error_fallback'
            }
    
    def _perform_safety_checks(self, signal: Dict[str, Any], 
                              win_probability: float, capital: float) -> Dict[str, Any]:
        """Perform comprehensive safety checks before position sizing"""
        
        # Check win probability edge
        if win_probability < self.config['min_win_probability']:
            return {
                'passed': False,
                'reason': f'Insufficient edge: {win_probability:.1%} < {self.config["min_win_probability"]:.1%}'
            }
        
        # Check drawdown limit
        if self.current_drawdown > self.config['drawdown_threshold']:
            return {
                'passed': False,
                'reason': f'Drawdown limit exceeded: {self.current_drawdown:.1%}'
            }
        
        # Check daily loss circuit breaker
        daily_loss_pct = abs(self.daily_pnl) / capital if capital > 0 else 0
        if self.daily_pnl < 0 and daily_loss_pct > self.config['circuit_breaker_loss']:
            return {
                'passed': False,
                'reason': f'Daily loss circuit breaker: {daily_loss_pct:.1%}'
            }
        
        # Check capital availability
        if capital <= 0:
            return {
                'passed': False,
                'reason': 'No available capital'
            }
        
        return {'passed': True, 'reason': 'All safety checks passed'}
    
    def _calculate_volatility(self, market_data: List[Dict[str, Any]]) -> float:
        """Calculate current market volatility"""
        if not market_data or len(market_data) < 10:
            return self.volatility_estimate
        
        try:
            # Extract prices
            prices = []
            for data in market_data[-30:]:  # Last 30 data points
                price = data.get('price', data.get('close', 0))
                if price > 0:
                    prices.append(price)
            
            if len(prices) < 5:
                return self.volatility_estimate
            
            # Calculate returns
            returns = []
            for i in range(1, len(prices)):
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
            
            # Calculate volatility (annualized)
            if len(returns) > 0:
                volatility = np.std(returns) * np.sqrt(252)  # Assuming daily data
                # Store in history
                self.volatility_history.append(volatility)
                return max(0.005, min(0.20, volatility))  # Clamp between 0.5% and 20%
            
        except Exception as e:
            self.logger.warning(f"Volatility calculation error: {e}")
        
        return self.volatility_estimate
    
    def _estimate_trade_outcomes(self, signal: Dict[str, Any], 
                               market_data: List[Dict[str, Any]], 
                               volatility: float) -> Tuple[float, float]:
        """Estimate expected return and loss for the trade"""
        
        # Base return estimate on volatility and signal strength
        signal_confidence = signal.get('confidence', 0.5)
        
        # Expected return: scale with confidence and volatility
        # Higher confidence = higher expected return
        # But cap based on realistic volatility
        base_return = volatility * 0.5  # 50% of daily volatility as base
        confidence_multiplier = 1 + (signal_confidence - 0.5) * 2  # 0.5 to 1.5 range
        expected_return = base_return * confidence_multiplier
        
        # Expected loss: assume symmetric but with risk adjustment
        # Losses tend to be faster/larger than gains in volatile markets
        loss_multiplier = 1.2  # Losses 20% larger on average
        expected_loss = expected_return * loss_multiplier
        
        # Cap returns at reasonable levels
        expected_return = min(expected_return, 0.05)  # Max 5% expected return
        expected_loss = min(expected_loss, 0.06)  # Max 6% expected loss
        
        return expected_return, expected_loss
    
    def _calculate_kelly_fraction(self, win_prob: float, 
                                expected_return: float, 
                                expected_loss: float) -> float:
        """Calculate raw Kelly fraction"""
        
        if expected_loss <= 0:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds received, p = win probability, q = loss probability
        
        # Calculate odds and probabilities
        p = win_prob
        q = 1 - win_prob
        
        # Odds based on expected return/loss ratio
        b = expected_return / expected_loss
        
        # Kelly fraction
        kelly_f = (b * p - q) / b
        
        # Ensure positive and reasonable
        kelly_f = max(0.0, kelly_f)
        
        # Apply quarter Kelly scaling
        kelly_f *= self.config['kelly_fraction']
        
        return min(kelly_f, 0.25)  # Cap at 25%
    
    def _apply_safety_adjustments(self, kelly_fraction: float, 
                                signal_confidence: float, 
                                volatility: float) -> float:
        """Apply safety adjustments to Kelly fraction"""
        
        adjusted_kelly = kelly_fraction
        
        # Confidence adjustment
        confidence_adjustment = 0.5 + (signal_confidence - 0.5) * 1.0
        adjusted_kelly *= confidence_adjustment
        
        # Volatility adjustment (reduce in high volatility)
        if volatility > 0.03:  # Above 3% daily volatility
            vol_adjustment = 1.0 - min(0.5, (volatility - 0.03) * 10)
            adjusted_kelly *= vol_adjustment
        
        # Performance-based adjustment
        adjusted_kelly *= self.kelly_multiplier
        
        # Drawdown adjustment
        if self.current_drawdown > 0.05:  # Above 5% drawdown
            drawdown_adjustment = 1.0 - (self.current_drawdown * 2)
            adjusted_kelly *= max(0.1, drawdown_adjustment)
        
        return max(0.0, adjusted_kelly)
    
    def _adjust_for_volatility(self, position_size: float, volatility: float) -> float:
        """Final volatility-based position adjustment"""
        
        # Target risk per trade (as % of capital)
        target_risk = 0.02  # 2% risk per trade
        
        # Adjust position size based on volatility
        if volatility > 0:
            risk_adjusted_size = position_size * (target_risk / volatility)
            return min(position_size, risk_adjusted_size)
        
        return position_size
    
    def _update_daily_tracking(self):
        """Update daily PnL tracking and reset if new day"""
        current_date = datetime.now().date()
        
        if current_date != self.last_reset_date:
            # New day - reset daily PnL
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
    
    def _track_position(self, position_info: Dict[str, Any]):
        """Track position for performance monitoring"""
        self.position_history.append(position_info)
        self.total_trades += 1
    
    def update_trade_outcome(self, trade_pnl: float, was_winning: bool):
        """Update Kelly calculator with trade outcome"""
        
        # Update trade statistics
        if was_winning:
            self.winning_trades += 1
        
        self.total_pnl += trade_pnl
        self.daily_pnl += trade_pnl
        
        # Update PnL history
        self.pnl_history.append({
            'timestamp': datetime.now(),
            'pnl': trade_pnl,
            'cumulative_pnl': self.total_pnl
        })
        
        # Update drawdown
        self._update_drawdown()
        
        # Adapt Kelly multiplier based on performance
        self._adapt_kelly_multiplier()
        
        self.logger.info(f"Trade outcome updated: PnL={trade_pnl:.2f}, Win={was_winning}, "
                        f"Total PnL={self.total_pnl:.2f}, Drawdown={self.current_drawdown:.1%}")
    
    def _update_drawdown(self):
        """Update current drawdown calculation"""
        if not self.pnl_history:
            return
        
        # Find peak equity
        peak_equity = 0.0
        current_equity = 0.0
        
        for pnl_entry in self.pnl_history:
            current_equity = pnl_entry['cumulative_pnl']
            peak_equity = max(peak_equity, current_equity)
        
        # Calculate drawdown
        if peak_equity > 0:
            self.current_drawdown = (peak_equity - current_equity) / peak_equity
        else:
            self.current_drawdown = max(0.0, -current_equity / 10000)  # Assume 10k starting capital
        
        # Update max drawdown
        self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
    
    def _adapt_kelly_multiplier(self):
        """Adapt Kelly multiplier based on recent performance"""
        
        if self.total_trades < 10:
            return  # Need more trades
        
        # Calculate recent win rate
        recent_trades = min(20, self.total_trades)
        recent_wins = sum(1 for entry in list(self.pnl_history)[-recent_trades:] 
                         if entry['pnl'] > 0)
        recent_win_rate = recent_wins / recent_trades
        
        # Adjust multiplier based on performance
        if recent_win_rate > 0.6:
            # Good performance - slightly increase
            self.kelly_multiplier = min(1.2, self.kelly_multiplier * 1.05)
        elif recent_win_rate < 0.4:
            # Poor performance - decrease
            self.kelly_multiplier = max(0.3, self.kelly_multiplier * 0.95)
        
        # Additional adjustment for drawdown
        if self.current_drawdown > 0.15:  # 15% drawdown
            self.kelly_multiplier = max(0.2, self.kelly_multiplier * 0.8)
    
    def _get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0.0
        
        return {
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'daily_pnl': self.daily_pnl,
            'total_pnl': self.total_pnl,
            'total_trades': self.total_trades,
            'win_rate': win_rate,
            'kelly_multiplier': self.kelly_multiplier,
            'volatility_estimate': self.volatility_estimate
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        risk_metrics = self._get_risk_metrics()
        
        # Calculate Sharpe ratio approximation
        if len(self.pnl_history) > 0:
            pnl_values = [entry['pnl'] for entry in self.pnl_history]
            avg_return = np.mean(pnl_values) if pnl_values else 0
            return_std = np.std(pnl_values) if len(pnl_values) > 1 else 1
            sharpe_approx = avg_return / return_std if return_std > 0 else 0
        else:
            sharpe_approx = 0
        
        return {
            **risk_metrics,
            'sharpe_ratio_approx': sharpe_approx,
            'avg_position_size': np.mean([p['position_pct'] for p in self.position_history]) 
                               if self.position_history else 0,
            'config': self.config,
            'positions_tracked': len(self.position_history)
        }
    
    def set_config(self, **kwargs):
        """Update Kelly calculator configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated Kelly config: {key} = {value}")