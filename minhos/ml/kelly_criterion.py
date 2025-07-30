#!/usr/bin/env python3
"""
ML-Enhanced Kelly Criterion Position Sizing

Implements mathematically optimal position sizing using Kelly Criterion
enhanced with ML model predictions from LSTM and Ensemble systems.

The Kelly Criterion formula:
f* = (p * b - q) / b

Where:
- f* = fraction of capital to wager
- p = probability of winning (from ML models)
- q = probability of losing (1 - p)
- b = odds received on the wager (avg_win / avg_loss)

Enhanced with:
- LSTM time series predictions
- Ensemble model consensus
- Confidence-weighted adjustments
- Risk parameter constraints
"""

import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class KellyPosition:
    """Result of Kelly Criterion calculation"""
    symbol: str
    recommended_size: int
    kelly_fraction: float
    win_probability: float
    loss_probability: float
    expected_win: float
    expected_loss: float
    confidence_score: float
    risk_adjusted_size: int
    calculation_details: Dict[str, Any]
    timestamp: datetime

class MLEnhancedKellyCriterion:
    """
    ML-Enhanced Kelly Criterion for optimal position sizing
    
    Integrates predictions from:
    - LSTM neural network (time series patterns)
    - Ensemble models (XGBoost, LightGBM, Random Forest, CatBoost)
    - Historical win/loss ratios
    - Risk management constraints
    """
    
    def __init__(self, 
                 capital: float = 100000.0,
                 max_kelly_fraction: float = 0.25,
                 confidence_threshold: float = 0.6):
        """
        Initialize ML-Enhanced Kelly Criterion
        
        Args:
            capital: Total trading capital
            max_kelly_fraction: Maximum fraction of capital to risk (Kelly can be aggressive)
            confidence_threshold: Minimum ML confidence to trade
        """
        self.capital = capital
        self.max_kelly_fraction = max_kelly_fraction  # Cap at 25% for safety
        self.confidence_threshold = confidence_threshold
        
        # Performance tracking
        self.win_loss_history = []
        self.prediction_accuracy = []
        
        # ML model connections (to be set)
        self.lstm_predictor = None
        self.ensemble_predictor = None
        
        # Historical statistics
        self.historical_stats = {
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'sharpe_ratio': 0.0
        }
        
        logger.info(f"ML-Enhanced Kelly Criterion initialized with capital: ${capital:,.2f}")
    
    def calculate_position_size(self, 
                              symbol: str,
                              current_price: float,
                              lstm_prediction: Dict[str, Any],
                              ensemble_prediction: Dict[str, Any],
                              risk_params: Optional[Dict[str, Any]] = None) -> KellyPosition:
        """
        Calculate optimal position size using ML-enhanced Kelly Criterion
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            lstm_prediction: LSTM model prediction with confidence
            ensemble_prediction: Ensemble model prediction with confidence
            risk_params: Risk management parameters
            
        Returns:
            KellyPosition with recommended sizing
        """
        try:
            # Extract ML predictions
            lstm_prob = self._extract_win_probability(lstm_prediction)
            ensemble_prob = self._extract_win_probability(ensemble_prediction)
            
            # Combine probabilities with confidence weighting
            lstm_confidence = lstm_prediction.get('confidence', 0.5)
            ensemble_confidence = ensemble_prediction.get('confidence', 0.5)
            
            # Weighted average based on confidence
            total_confidence = lstm_confidence + ensemble_confidence
            if total_confidence > 0:
                win_probability = (
                    (lstm_prob * lstm_confidence + ensemble_prob * ensemble_confidence) / 
                    total_confidence
                )
                combined_confidence = total_confidence / 2.0
            else:
                win_probability = 0.5  # No edge
                combined_confidence = 0.0
            
            # Check confidence threshold
            if combined_confidence < self.confidence_threshold:
                logger.info(f"Confidence {combined_confidence:.2f} below threshold {self.confidence_threshold}")
                return self._create_zero_position(symbol, win_probability, combined_confidence)
            
            # Get historical win/loss statistics
            avg_win, avg_loss = self._get_historical_stats(symbol)
            
            # Calculate Kelly fraction
            kelly_fraction = self._calculate_kelly_fraction(
                win_probability=win_probability,
                avg_win=avg_win,
                avg_loss=avg_loss
            )
            
            # Apply risk adjustments
            adjusted_kelly = self._apply_risk_adjustments(
                kelly_fraction=kelly_fraction,
                confidence=combined_confidence,
                risk_params=risk_params
            )
            
            # Calculate position size
            position_value = self.capital * adjusted_kelly
            recommended_size = int(position_value / current_price)
            
            # Apply minimum and maximum constraints
            recommended_size = self._apply_size_constraints(
                recommended_size, 
                risk_params
            )
            
            # Create detailed result
            return KellyPosition(
                symbol=symbol,
                recommended_size=recommended_size,
                kelly_fraction=kelly_fraction,
                win_probability=win_probability,
                loss_probability=1 - win_probability,
                expected_win=avg_win,
                expected_loss=avg_loss,
                confidence_score=combined_confidence,
                risk_adjusted_size=recommended_size,
                calculation_details={
                    'lstm_probability': lstm_prob,
                    'ensemble_probability': ensemble_prob,
                    'lstm_confidence': lstm_confidence,
                    'ensemble_confidence': ensemble_confidence,
                    'raw_kelly_fraction': kelly_fraction,
                    'adjusted_kelly_fraction': adjusted_kelly,
                    'position_value': position_value,
                    'current_price': current_price
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Kelly calculation error: {e}")
            return self._create_zero_position(symbol, 0.5, 0.0)
    
    def _extract_win_probability(self, prediction: Dict[str, Any]) -> float:
        """Extract win probability from ML prediction"""
        try:
            # Handle different prediction formats
            if 'probability' in prediction:
                return float(prediction['probability'])
            elif 'win_probability' in prediction:
                return float(prediction['win_probability'])
            elif 'direction' in prediction and 'confidence' in prediction:
                # Convert direction prediction to probability
                direction = prediction['direction']
                confidence = prediction['confidence']
                
                if direction > 0:  # Bullish
                    return 0.5 + (confidence * 0.5)
                else:  # Bearish
                    return 0.5 - (confidence * 0.5)
            else:
                # Default to 50/50
                return 0.5
                
        except Exception as e:
            logger.error(f"Error extracting win probability: {e}")
            return 0.5
    
    def _get_historical_stats(self, symbol: str) -> Tuple[float, float]:
        """Get historical win/loss statistics"""
        # Use default values if no history
        if not self.win_loss_history:
            # Conservative defaults based on typical futures trading
            return 50.0, 40.0  # $50 avg win, $40 avg loss (1.25 reward/risk)
        
        # Calculate from actual history
        wins = [trade['pnl'] for trade in self.win_loss_history 
                if trade['symbol'] == symbol and trade['pnl'] > 0]
        losses = [abs(trade['pnl']) for trade in self.win_loss_history 
                  if trade['symbol'] == symbol and trade['pnl'] < 0]
        
        avg_win = np.mean(wins) if wins else 50.0
        avg_loss = np.mean(losses) if losses else 40.0
        
        return avg_win, avg_loss
    
    def _calculate_kelly_fraction(self, 
                                 win_probability: float,
                                 avg_win: float,
                                 avg_loss: float) -> float:
        """
        Calculate raw Kelly fraction
        
        Kelly formula: f* = (p * b - q) / b
        Where b = avg_win / avg_loss
        """
        try:
            # Avoid division by zero
            if avg_loss <= 0:
                return 0.0
            
            # Calculate odds
            b = avg_win / avg_loss
            
            # Kelly calculation
            p = win_probability
            q = 1 - p
            
            kelly_fraction = (p * b - q) / b
            
            # Kelly can be negative (don't trade) or very large (cap it)
            kelly_fraction = max(0.0, min(kelly_fraction, self.max_kelly_fraction))
            
            logger.debug(f"Kelly calculation: p={p:.3f}, b={b:.3f}, f*={kelly_fraction:.3f}")
            
            return kelly_fraction
            
        except Exception as e:
            logger.error(f"Kelly calculation error: {e}")
            return 0.0
    
    def _apply_risk_adjustments(self,
                               kelly_fraction: float,
                               confidence: float,
                               risk_params: Optional[Dict[str, Any]] = None) -> float:
        """Apply risk management adjustments to Kelly fraction"""
        adjusted = kelly_fraction
        
        # Confidence adjustment (scale down if not highly confident)
        confidence_multiplier = min(1.0, confidence / 0.8)  # Full Kelly only at 80%+ confidence
        adjusted *= confidence_multiplier
        
        # Volatility adjustment (if provided)
        if risk_params and 'volatility_multiplier' in risk_params:
            vol_mult = risk_params['volatility_multiplier']
            # Higher volatility = smaller position
            adjusted *= (1.0 / max(1.0, vol_mult))
        
        # Drawdown protection
        if risk_params and 'current_drawdown' in risk_params:
            drawdown = risk_params['current_drawdown']
            if drawdown > 0.05:  # 5% drawdown
                # Reduce position size during drawdowns
                drawdown_multiplier = max(0.5, 1.0 - drawdown)
                adjusted *= drawdown_multiplier
        
        # Conservative factor for safety
        adjusted *= 0.5  # Half-Kelly is often recommended
        
        return adjusted
    
    def _apply_size_constraints(self, 
                               size: int,
                               risk_params: Optional[Dict[str, Any]] = None) -> int:
        """Apply minimum and maximum position size constraints"""
        # Minimum position size (at least 1 contract)
        size = max(1, size)
        
        # Maximum from risk parameters
        if risk_params and 'max_position_size' in risk_params:
            size = min(size, risk_params['max_position_size'])
        
        # Default maximum (e.g., 10 contracts)
        size = min(size, 10)
        
        return size
    
    def _create_zero_position(self, 
                            symbol: str,
                            win_probability: float,
                            confidence: float) -> KellyPosition:
        """Create a zero-size position result"""
        return KellyPosition(
            symbol=symbol,
            recommended_size=0,
            kelly_fraction=0.0,
            win_probability=win_probability,
            loss_probability=1 - win_probability,
            expected_win=0.0,
            expected_loss=0.0,
            confidence_score=confidence,
            risk_adjusted_size=0,
            calculation_details={
                'reason': 'Below confidence threshold or no edge'
            },
            timestamp=datetime.now()
        )
    
    def update_performance(self, 
                          symbol: str,
                          entry_price: float,
                          exit_price: float,
                          size: int,
                          predicted_direction: int):
        """Update performance tracking with trade result"""
        pnl = (exit_price - entry_price) * size * predicted_direction
        
        trade_result = {
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': size,
            'pnl': pnl,
            'predicted_direction': predicted_direction,
            'actual_direction': 1 if exit_price > entry_price else -1,
            'timestamp': datetime.now()
        }
        
        self.win_loss_history.append(trade_result)
        
        # Update prediction accuracy
        correct = (predicted_direction > 0 and exit_price > entry_price) or \
                 (predicted_direction < 0 and exit_price < entry_price)
        self.prediction_accuracy.append(correct)
        
        # Update historical statistics
        self._update_historical_stats()
        
        logger.info(f"Trade result: {symbol} PnL=${pnl:.2f}, "
                   f"Accuracy={sum(self.prediction_accuracy)/len(self.prediction_accuracy):.2%}")
    
    def _update_historical_stats(self):
        """Update historical performance statistics"""
        if not self.win_loss_history:
            return
        
        wins = [t['pnl'] for t in self.win_loss_history if t['pnl'] > 0]
        losses = [abs(t['pnl']) for t in self.win_loss_history if t['pnl'] < 0]
        
        self.historical_stats['avg_win'] = np.mean(wins) if wins else 0.0
        self.historical_stats['avg_loss'] = np.mean(losses) if losses else 0.0
        self.historical_stats['win_rate'] = len(wins) / len(self.win_loss_history)
        self.historical_stats['total_trades'] = len(self.win_loss_history)
        
        # Calculate Sharpe ratio
        if len(self.win_loss_history) > 1:
            returns = [t['pnl'] / self.capital for t in self.win_loss_history]
            self.historical_stats['sharpe_ratio'] = (
                np.mean(returns) / np.std(returns) * np.sqrt(252)  # Annualized
                if np.std(returns) > 0 else 0.0
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'historical_stats': self.historical_stats,
            'total_trades': len(self.win_loss_history),
            'prediction_accuracy': sum(self.prediction_accuracy) / len(self.prediction_accuracy) 
                                 if self.prediction_accuracy else 0.0,
            'total_pnl': sum(t['pnl'] for t in self.win_loss_history),
            'average_kelly_fraction': np.mean([t.get('kelly_fraction', 0) 
                                             for t in self.win_loss_history[-20:]]),
            'capital': self.capital,
            'timestamp': datetime.now().isoformat()
        }

# Singleton instance
_kelly_criterion = None

def get_kelly_criterion(capital: float = 100000.0) -> MLEnhancedKellyCriterion:
    """Get or create Kelly Criterion instance"""
    global _kelly_criterion
    if _kelly_criterion is None:
        _kelly_criterion = MLEnhancedKellyCriterion(capital=capital)
    return _kelly_criterion