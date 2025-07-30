#!/usr/bin/env python3
"""
ML Integration Module

Provides centralized integration for all ML components:
- LSTM Neural Network predictions
- Ensemble model predictions  
- Kelly Criterion position sizing
- Unified prediction interface
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np

from ..services.lstm_predictor import get_lstm_predictor
from ..services.ensemble_predictor import get_ensemble_predictor
from .kelly_criterion import get_kelly_criterion
from ..services.position_sizing_service import get_position_sizing_service

logger = logging.getLogger(__name__)

class MLIntegration:
    """
    Unified ML integration for MinhOS trading system
    
    Provides:
    - Combined LSTM + Ensemble predictions
    - ML-enhanced position sizing
    - Performance tracking
    - Model confidence scoring
    """
    
    def __init__(self):
        """Initialize ML Integration"""
        self.lstm_predictor = get_lstm_predictor()
        self.ensemble_predictor = get_ensemble_predictor()
        self.kelly_criterion = get_kelly_criterion()
        self.position_sizing_service = get_position_sizing_service()
        
        # Performance tracking
        self.prediction_history = []
        self.performance_metrics = {
            'lstm_accuracy': 0.0,
            'ensemble_accuracy': 0.0,
            'combined_accuracy': 0.0,
            'total_predictions': 0
        }
        
        logger.info("ML Integration initialized")
    
    async def get_ml_prediction(self, 
                               symbol: str,
                               market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get combined ML prediction from all models
        
        Returns:
            Dict containing:
            - direction: -1, 0, 1 (sell, neutral, buy)
            - confidence: 0.0 to 1.0
            - win_probability: 0.0 to 1.0
            - lstm_prediction: LSTM details
            - ensemble_prediction: Ensemble details
            - recommended_size: Kelly Criterion position size
        """
        try:
            # Get LSTM prediction
            lstm_pred = await self._get_lstm_prediction(symbol, market_data)
            
            # Get Ensemble prediction
            ensemble_pred = self._get_ensemble_prediction(symbol, market_data)
            
            # Combine predictions
            combined = self._combine_predictions(lstm_pred, ensemble_pred)
            
            # Get current price for position sizing
            current_price = market_data.get('close', market_data.get('price', 0))
            
            # Calculate optimal position size
            if current_price > 0:
                kelly_position = self.kelly_criterion.calculate_position_size(
                    symbol=symbol,
                    current_price=current_price,
                    lstm_prediction=lstm_pred,
                    ensemble_prediction=ensemble_pred
                )
                
                combined['recommended_size'] = kelly_position.risk_adjusted_size
                combined['kelly_fraction'] = kelly_position.kelly_fraction
                combined['win_probability'] = kelly_position.win_probability
            else:
                combined['recommended_size'] = 0
                combined['kelly_fraction'] = 0.0
                combined['win_probability'] = 0.5
            
            # Track prediction
            self._track_prediction(symbol, combined)
            
            return combined
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return {
                'direction': 0,
                'confidence': 0.0,
                'win_probability': 0.5,
                'recommended_size': 0,
                'error': str(e)
            }
    
    async def _get_lstm_prediction(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get LSTM prediction"""
        try:
            # Prepare features for LSTM
            features = self._prepare_lstm_features(market_data)
            
            # Get prediction
            prediction = self.lstm_predictor.predict(features)
            
            # Convert to standard format
            return {
                'direction': prediction.get('direction', 0),
                'confidence': prediction.get('confidence', 0.5),
                'model': 'LSTM',
                'features_used': len(features)
            }
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return {'direction': 0, 'confidence': 0.0, 'model': 'LSTM'}
    
    def _get_ensemble_prediction(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get Ensemble prediction"""
        try:
            # Prepare features for Ensemble
            features = self._prepare_ensemble_features(market_data)
            
            # Get prediction
            prediction = self.ensemble_predictor.predict(
                symbol=symbol,
                features=features
            )
            
            # Convert to standard format
            return {
                'direction': prediction.get('consensus_direction', 0),
                'confidence': prediction.get('consensus_confidence', 0.5),
                'model': 'Ensemble',
                'models_agree': prediction.get('models_agree', 0),
                'individual_predictions': prediction.get('predictions', {})
            }
            
        except Exception as e:
            logger.error(f"Ensemble prediction error: {e}")
            return {'direction': 0, 'confidence': 0.0, 'model': 'Ensemble'}
    
    def _prepare_lstm_features(self, market_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for LSTM model"""
        try:
            # LSTM expects time series data
            # For now, create simple feature array
            features = []
            
            # Price features
            features.append(market_data.get('close', 0))
            features.append(market_data.get('high', 0))
            features.append(market_data.get('low', 0))
            features.append(market_data.get('open', 0))
            
            # Volume
            features.append(market_data.get('volume', 0))
            
            # Technical indicators if available
            features.append(market_data.get('rsi', 50))
            features.append(market_data.get('macd', 0))
            features.append(market_data.get('bb_upper', 0))
            features.append(market_data.get('bb_lower', 0))
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"LSTM feature preparation error: {e}")
            return np.zeros((1, 9))
    
    def _prepare_ensemble_features(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Prepare features for Ensemble models"""
        try:
            # Ensemble expects dictionary of features
            features = {
                'price': market_data.get('close', 0),
                'volume': market_data.get('volume', 0),
                'price_change': market_data.get('price_change', 0),
                'volume_ratio': market_data.get('volume_ratio', 1.0),
                'rsi': market_data.get('rsi', 50),
                'macd': market_data.get('macd', 0),
                'bb_position': market_data.get('bb_position', 0.5),
                'trend_strength': market_data.get('trend_strength', 0),
                'volatility': market_data.get('volatility', 0)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Ensemble feature preparation error: {e}")
            return {}
    
    def _combine_predictions(self, lstm_pred: Dict, ensemble_pred: Dict) -> Dict[str, Any]:
        """Combine LSTM and Ensemble predictions"""
        try:
            # Get predictions
            lstm_dir = lstm_pred.get('direction', 0)
            ensemble_dir = ensemble_pred.get('direction', 0)
            
            lstm_conf = lstm_pred.get('confidence', 0.0)
            ensemble_conf = ensemble_pred.get('confidence', 0.0)
            
            # Weight by confidence
            total_conf = lstm_conf + ensemble_conf
            
            if total_conf > 0:
                # Weighted average direction
                weighted_dir = (lstm_dir * lstm_conf + ensemble_dir * ensemble_conf) / total_conf
                
                # Determine final direction
                if weighted_dir > 0.2:
                    direction = 1  # Buy
                elif weighted_dir < -0.2:
                    direction = -1  # Sell
                else:
                    direction = 0  # Neutral
                
                # Combined confidence (higher if models agree)
                if lstm_dir == ensemble_dir and lstm_dir != 0:
                    # Models agree - boost confidence
                    combined_conf = min(1.0, (lstm_conf + ensemble_conf) / 2 * 1.2)
                else:
                    # Models disagree - reduce confidence
                    combined_conf = (lstm_conf + ensemble_conf) / 2 * 0.8
            else:
                direction = 0
                combined_conf = 0.0
            
            return {
                'direction': direction,
                'confidence': combined_conf,
                'lstm_prediction': lstm_pred,
                'ensemble_prediction': ensemble_pred,
                'models_agree': lstm_dir == ensemble_dir,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction combination error: {e}")
            return {
                'direction': 0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _track_prediction(self, symbol: str, prediction: Dict[str, Any]):
        """Track prediction for performance monitoring"""
        try:
            self.prediction_history.append({
                'symbol': symbol,
                'prediction': prediction,
                'timestamp': datetime.now()
            })
            
            # Keep only recent predictions
            if len(self.prediction_history) > 1000:
                self.prediction_history = self.prediction_history[-1000:]
            
            self.performance_metrics['total_predictions'] += 1
            
        except Exception as e:
            logger.error(f"Prediction tracking error: {e}")
    
    def update_prediction_result(self, 
                               symbol: str,
                               prediction_time: datetime,
                               actual_direction: int):
        """Update prediction accuracy based on actual result"""
        try:
            # Find matching prediction
            for pred in reversed(self.prediction_history):
                if (pred['symbol'] == symbol and 
                    abs((pred['timestamp'] - prediction_time).total_seconds()) < 60):
                    
                    # Check if prediction was correct
                    predicted_dir = pred['prediction']['direction']
                    correct = (predicted_dir == actual_direction)
                    
                    pred['actual_direction'] = actual_direction
                    pred['correct'] = correct
                    
                    # Update accuracy metrics
                    self._update_accuracy_metrics()
                    break
                    
        except Exception as e:
            logger.error(f"Prediction result update error: {e}")
    
    def _update_accuracy_metrics(self):
        """Update model accuracy metrics"""
        try:
            # Get predictions with results
            evaluated = [p for p in self.prediction_history if 'correct' in p]
            
            if not evaluated:
                return
            
            # Calculate accuracies
            lstm_correct = sum(1 for p in evaluated 
                             if p['prediction']['lstm_prediction']['direction'] == p['actual_direction'])
            ensemble_correct = sum(1 for p in evaluated
                                 if p['prediction']['ensemble_prediction']['direction'] == p['actual_direction'])
            combined_correct = sum(1 for p in evaluated if p['correct'])
            
            total = len(evaluated)
            
            self.performance_metrics['lstm_accuracy'] = lstm_correct / total
            self.performance_metrics['ensemble_accuracy'] = ensemble_correct / total
            self.performance_metrics['combined_accuracy'] = combined_correct / total
            
            logger.info(f"ML Accuracy Update - LSTM: {self.performance_metrics['lstm_accuracy']:.1%}, "
                       f"Ensemble: {self.performance_metrics['ensemble_accuracy']:.1%}, "
                       f"Combined: {self.performance_metrics['combined_accuracy']:.1%}")
                       
        except Exception as e:
            logger.error(f"Accuracy metrics update error: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get ML performance summary"""
        return {
            'performance_metrics': self.performance_metrics,
            'total_predictions': len(self.prediction_history),
            'recent_predictions': self.prediction_history[-10:],
            'kelly_performance': self.kelly_criterion.get_performance_summary(),
            'timestamp': datetime.now().isoformat()
        }

# Singleton instance
_ml_integration = None

def get_ml_integration() -> MLIntegration:
    """Get or create ML Integration instance"""
    global _ml_integration
    if _ml_integration is None:
        _ml_integration = MLIntegration()
    return _ml_integration