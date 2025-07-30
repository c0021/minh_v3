#!/usr/bin/env python3
"""
ML Probability Estimator
========================

Converts ML model outputs to Kelly Criterion-compatible probabilities.
Handles confidence score calibration, model aggregation, and historical validation.

Features:
- ML confidence to probability conversion
- Multi-model probability aggregation
- Historical accuracy-based weighting
- Confidence calibration and validation
- Win/loss ratio calculation from trading history

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import logging
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ModelPrediction:
    """Structured ML model prediction for Kelly calculation"""
    model_type: str  # 'lstm', 'ensemble', 'xgboost', etc.
    confidence: float  # Raw model confidence [0, 1]
    direction: str  # 'long', 'short', 'neutral'
    probability: Optional[float] = None  # Calibrated probability
    historical_accuracy: Optional[float] = None  # Historical model accuracy
    weight: Optional[float] = None  # Weight in ensemble
    metadata: Optional[Dict] = None  # Additional model-specific data
    timestamp: Optional[datetime] = None


@dataclass
class ProbabilityEstimate:
    """Final probability estimate for Kelly calculation"""
    win_probability: float  # Estimated P(profitable trade)
    win_loss_ratio: float  # Historical win/loss ratio
    confidence: float  # Aggregate confidence
    model_agreement: bool  # Whether models agree on direction
    individual_probabilities: List[float]  # Individual model probabilities
    reasoning: str  # Explanation of probability calculation
    metadata: Dict  # Additional calculation data


class MLProbabilityEstimator:
    """
    Converts ML model predictions to Kelly Criterion probabilities
    
    Handles:
    - Confidence score calibration
    - Multi-model aggregation
    - Historical accuracy weighting
    - Win/loss ratio calculation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize ML Probability Estimator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        
        # Model weights (should sum to 1.0)
        self.model_weights = self.config.get('model_weights', {
            'lstm': 0.4,
            'ensemble': 0.6
        })
        
        # Confidence thresholds
        self.min_confidence = self.config.get('confidence_threshold', 0.6)
        self.min_agreement_threshold = self.config.get('agreement_threshold', 0.8)
        
        # Historical data parameters
        self.lookback_days = self.config.get('win_loss_lookback_days', 30)
        self.min_trades_for_ratio = self.config.get('min_trades_for_ratio', 10)
        
        # Calibration parameters
        self.enable_calibration = self.config.get('enable_calibration', True)
        self.calibration_alpha = self.config.get('calibration_alpha', 0.1)  # For exponential smoothing
        
        # Default historical accuracies (will be updated with real data)
        self.default_accuracies = {
            'lstm': 0.65,
            'ensemble': 0.70,
            'xgboost': 0.68,
            'lightgbm': 0.67,
            'random_forest': 0.64,
            'catboost': 0.69
        }
        
        logger.info(f"Probability Estimator initialized with weights: {self.model_weights}")
    
    def _default_config(self) -> Dict:
        """Default configuration for probability estimator"""
        return {
            'model_weights': {'lstm': 0.4, 'ensemble': 0.6},
            'confidence_threshold': 0.6,
            'agreement_threshold': 0.8,
            'win_loss_lookback_days': 30,
            'min_trades_for_ratio': 10,
            'enable_calibration': True,
            'calibration_alpha': 0.1,
            'default_win_loss_ratio': 1.2,
            'neutral_probability': 0.5
        }
    
    def calibrate_confidence_to_probability(self, 
                                          confidence: float, 
                                          model_type: str,
                                          historical_accuracy: Optional[float] = None) -> float:
        """
        Convert raw ML confidence to calibrated probability
        
        Args:
            confidence: Raw model confidence [0, 1]
            model_type: Type of ML model
            historical_accuracy: Historical accuracy of this model
            
        Returns:
            Calibrated probability for Kelly calculation
        """
        if not self.enable_calibration:
            return confidence
        
        # Get historical accuracy
        if historical_accuracy is None:
            historical_accuracy = self.default_accuracies.get(model_type, 0.65)
        
        # Simple calibration: adjust confidence based on historical accuracy
        # More sophisticated approaches: Platt scaling, isotonic regression
        
        if confidence < 0.5:
            # Model predicts negative outcome - convert to probability of opposite
            raw_negative_prob = 1 - confidence
            calibrated_prob = raw_negative_prob * historical_accuracy + (1 - historical_accuracy) * 0.5
            return 1 - calibrated_prob  # Return probability of positive outcome
        else:
            # Model predicts positive outcome
            calibrated_prob = confidence * historical_accuracy + (1 - historical_accuracy) * 0.5
            return calibrated_prob
    
    def aggregate_model_predictions(self, predictions: List[ModelPrediction]) -> ProbabilityEstimate:
        """
        Aggregate multiple ML model predictions into single probability estimate
        
        Args:
            predictions: List of ML model predictions
            
        Returns:
            Aggregated probability estimate
        """
        if not predictions:
            logger.warning("No predictions provided, returning neutral probability")
            return ProbabilityEstimate(
                win_probability=0.5,
                win_loss_ratio=1.0,
                confidence=0.0,
                model_agreement=False,
                individual_probabilities=[],
                reasoning="No predictions available",
                metadata={'error': 'no_predictions'}
            )
        
        # Step 1: Calibrate individual predictions
        calibrated_predictions = []
        individual_probs = []
        
        for pred in predictions:
            # Calibrate confidence to probability
            calibrated_prob = self.calibrate_confidence_to_probability(
                pred.confidence, pred.model_type, pred.historical_accuracy
            )
            
            # Store calibrated prediction
            calibrated_pred = ModelPrediction(
                model_type=pred.model_type,
                confidence=pred.confidence,
                direction=pred.direction,
                probability=calibrated_prob,
                historical_accuracy=pred.historical_accuracy or self.default_accuracies.get(pred.model_type, 0.65),
                weight=self.model_weights.get(pred.model_type, 1.0 / len(predictions)),
                metadata=pred.metadata,
                timestamp=pred.timestamp
            )
            
            calibrated_predictions.append(calibrated_pred)
            individual_probs.append(calibrated_prob)
        
        # Step 2: Check model agreement
        directions = [pred.direction for pred in predictions]
        direction_counts = defaultdict(int)
        for direction in directions:
            direction_counts[direction] += 1
        
        most_common_direction = max(direction_counts, key=direction_counts.get)
        agreement_ratio = direction_counts[most_common_direction] / len(directions)
        model_agreement = agreement_ratio >= self.min_agreement_threshold
        
        # Step 3: Calculate weighted probability
        if not model_agreement:
            # Models disagree - return neutral probability
            logger.info(f"Models disagree on direction: {direction_counts}")
            return ProbabilityEstimate(
                win_probability=0.5,
                win_loss_ratio=1.0,
                confidence=0.0,
                model_agreement=False,
                individual_probabilities=individual_probs,
                reasoning=f"Model disagreement: {dict(direction_counts)}",
                metadata={'direction_counts': dict(direction_counts)}
            )
        
        # Models agree - calculate weighted average
        total_weight = sum(pred.weight for pred in calibrated_predictions)
        if total_weight == 0:
            total_weight = len(calibrated_predictions)
            # Assign equal weights
            for pred in calibrated_predictions:
                pred.weight = 1.0 / len(calibrated_predictions)
        
        weighted_probability = sum(
            pred.probability * (pred.weight / total_weight) 
            for pred in calibrated_predictions
        )
        
        # Calculate aggregate confidence
        weighted_confidence = sum(
            pred.confidence * (pred.weight / total_weight)
            for pred in calibrated_predictions
        )
        
        # Build reasoning string
        model_details = []
        for pred in calibrated_predictions:
            model_details.append(f"{pred.model_type}:{pred.confidence:.3f}→{pred.probability:.3f}")
        reasoning = f"Weighted avg: {' + '.join(model_details)} = {weighted_probability:.3f}"
        
        # Metadata
        metadata = {
            'total_models': len(predictions),
            'agreement_ratio': agreement_ratio,
            'dominant_direction': most_common_direction,
            'model_weights': {pred.model_type: pred.weight for pred in calibrated_predictions},
            'raw_confidences': {pred.model_type: pred.confidence for pred in calibrated_predictions}
        }
        
        return ProbabilityEstimate(
            win_probability=weighted_probability,
            win_loss_ratio=1.0,  # Will be calculated separately
            confidence=weighted_confidence,
            model_agreement=model_agreement,
            individual_probabilities=individual_probs,
            reasoning=reasoning,
            metadata=metadata
        )
    
    def calculate_historical_win_loss_ratio(self, 
                                          trade_history: List[Dict], 
                                          symbol: Optional[str] = None,
                                          lookback_days: Optional[int] = None) -> float:
        """
        Calculate win/loss ratio from historical trading data
        
        Args:
            trade_history: List of trade records with 'pnl', 'timestamp', 'symbol'
            symbol: Filter trades for specific symbol (None for all)
            lookback_days: Days to look back (None for config default)
            
        Returns:
            Historical win/loss ratio
        """
        lookback_days = lookback_days or self.lookback_days
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        # Filter trades
        filtered_trades = []
        for trade in trade_history:
            # Date filter
            trade_date = trade.get('timestamp')
            if isinstance(trade_date, str):
                trade_date = datetime.fromisoformat(trade_date.replace('Z', '+00:00'))
            
            if trade_date < cutoff_date:
                continue
            
            # Symbol filter
            if symbol and trade.get('symbol') != symbol:
                continue
            
            filtered_trades.append(trade)
        
        if len(filtered_trades) < self.min_trades_for_ratio:
            logger.warning(f"Insufficient trade history: {len(filtered_trades)} trades, "
                          f"minimum {self.min_trades_for_ratio}")
            return self.config.get('default_win_loss_ratio', 1.2)
        
        # Separate wins and losses
        wins = []
        losses = []
        
        for trade in filtered_trades:
            pnl = trade.get('pnl', 0)
            if pnl > 0:
                wins.append(pnl)
            elif pnl < 0:
                losses.append(abs(pnl))
        
        if not wins or not losses:
            logger.warning(f"Missing wins or losses: {len(wins)} wins, {len(losses)} losses")
            return self.config.get('default_win_loss_ratio', 1.2)
        
        # Calculate averages
        avg_win = sum(wins) / len(wins)
        avg_loss = sum(losses) / len(losses)
        
        win_loss_ratio = avg_win / avg_loss
        
        logger.info(f"Historical W/L ratio: {win_loss_ratio:.3f} "
                   f"(avg_win: ${avg_win:.2f}, avg_loss: ${avg_loss:.2f}, "
                   f"trades: {len(filtered_trades)})")
        
        return win_loss_ratio
    
    def estimate_trading_probability(self,
                                   ml_predictions: List[Dict],
                                   trade_history: Optional[List[Dict]] = None,
                                   symbol: Optional[str] = None) -> ProbabilityEstimate:
        """
        Main entry point: convert ML predictions to Kelly probabilities
        
        Args:
            ml_predictions: List of ML model predictions
            trade_history: Historical trade data for win/loss ratio
            symbol: Trading symbol
            
        Returns:
            Complete probability estimate for Kelly calculation
        """
        logger.info(f"Estimating probabilities for {symbol} with {len(ml_predictions)} models")
        
        # Convert dict predictions to ModelPrediction objects
        model_predictions = []
        for pred in ml_predictions:
            model_pred = ModelPrediction(
                model_type=pred.get('model_type', 'unknown'),
                confidence=pred.get('confidence', 0.5),
                direction=pred.get('direction', 'neutral'),
                historical_accuracy=pred.get('historical_accuracy'),
                metadata=pred.get('metadata', {}),
                timestamp=datetime.now()
            )
            model_predictions.append(model_pred)
        
        # Aggregate model predictions
        prob_estimate = self.aggregate_model_predictions(model_predictions)
        
        # Calculate win/loss ratio from historical data
        if trade_history:
            win_loss_ratio = self.calculate_historical_win_loss_ratio(
                trade_history, symbol
            )
        else:
            win_loss_ratio = self.config.get('default_win_loss_ratio', 1.2)
            logger.warning(f"No trade history provided, using default W/L ratio: {win_loss_ratio}")
        
        # Update probability estimate with win/loss ratio
        prob_estimate.win_loss_ratio = win_loss_ratio
        prob_estimate.reasoning += f" | W/L: {win_loss_ratio:.3f}"
        
        logger.info(f"Final probability estimate: win_prob={prob_estimate.win_probability:.3f}, "
                   f"win_loss={prob_estimate.win_loss_ratio:.3f}, "
                   f"confidence={prob_estimate.confidence:.3f}")
        
        return prob_estimate
    
    def validate_prediction_quality(self, prob_estimate: ProbabilityEstimate) -> Dict:
        """
        Validate quality of probability estimate for Kelly calculation
        
        Args:
            prob_estimate: Probability estimate to validate
            
        Returns:
            Validation results with recommendations
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Check model agreement
        if not prob_estimate.model_agreement:
            validation['warnings'].append("Models disagree on direction")
            validation['recommendations'].append("Consider not trading when models disagree")
        
        # Check confidence threshold
        if prob_estimate.confidence < self.min_confidence:
            validation['errors'].append(f"Confidence below threshold: {prob_estimate.confidence:.3f} < {self.min_confidence}")
            validation['valid'] = False
        
        # Check probability bounds
        if not (0 <= prob_estimate.win_probability <= 1):
            validation['errors'].append(f"Invalid win probability: {prob_estimate.win_probability}")
            validation['valid'] = False
        
        # Check win/loss ratio
        if prob_estimate.win_loss_ratio <= 0:
            validation['errors'].append(f"Invalid win/loss ratio: {prob_estimate.win_loss_ratio}")
            validation['valid'] = False
        elif prob_estimate.win_loss_ratio < 1.0:
            validation['warnings'].append(f"Unfavorable win/loss ratio: {prob_estimate.win_loss_ratio:.3f}")
            validation['recommendations'].append("Consider improving strategy or position sizing")
        
        # Check for extreme probabilities
        if prob_estimate.win_probability > 0.9:
            validation['warnings'].append(f"Very high win probability: {prob_estimate.win_probability:.3f}")
            validation['recommendations'].append("Verify model calibration - may be overconfident")
        elif prob_estimate.win_probability < 0.1:
            validation['warnings'].append(f"Very low win probability: {prob_estimate.win_probability:.3f}")
            validation['recommendations'].append("Consider inverse position or no trade")
        
        return validation
    
    def update_model_accuracy(self, model_type: str, accuracy: float) -> None:
        """
        Update historical accuracy for a model type
        
        Args:
            model_type: Type of ML model
            accuracy: New accuracy measurement [0, 1]
        """
        if not (0 <= accuracy <= 1):
            logger.error(f"Invalid accuracy for {model_type}: {accuracy}")
            return
        
        # Exponential smoothing update
        current_accuracy = self.default_accuracies.get(model_type, 0.65)
        updated_accuracy = (1 - self.calibration_alpha) * current_accuracy + self.calibration_alpha * accuracy
        
        self.default_accuracies[model_type] = updated_accuracy
        
        logger.info(f"Updated {model_type} accuracy: {current_accuracy:.3f} -> {updated_accuracy:.3f}")
    
    def get_model_accuracies(self) -> Dict[str, float]:
        """Get current model accuracy estimates"""
        return self.default_accuracies.copy()
    
    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.config.copy()


# Utility functions
def simple_confidence_to_probability(confidence: float, historical_accuracy: float = 0.65) -> float:
    """
    Simple confidence to probability conversion
    
    Args:
        confidence: Model confidence [0, 1]
        historical_accuracy: Historical model accuracy [0, 1]
        
    Returns:
        Calibrated probability
    """
    if confidence < 0.5:
        return (1 - confidence) * historical_accuracy + (1 - historical_accuracy) * 0.5
    else:
        return confidence * historical_accuracy + (1 - historical_accuracy) * 0.5


def calculate_edge(win_probability: float, win_loss_ratio: float) -> float:
    """
    Calculate expected edge for Kelly calculation
    
    Args:
        win_probability: P(win)
        win_loss_ratio: Average win / Average loss
        
    Returns:
        Expected edge (positive means profitable)
    """
    return (win_loss_ratio * win_probability) - (1 - win_probability)