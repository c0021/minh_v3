"""
ML Confidence Tracker Service

Advanced confidence tracking and calibration for ML predictions.
Provides confidence analytics, calibration monitoring, and prediction quality metrics.
"""

import asyncio
import logging
import json
import sqlite3
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from enum import Enum
import statistics


class ConfidenceZone(Enum):
    """Confidence zones for prediction categorization"""
    VERY_LOW = "very_low"      # 0.0 - 0.5
    LOW = "low"                # 0.5 - 0.6
    MEDIUM = "medium"          # 0.6 - 0.7
    HIGH = "high"              # 0.7 - 0.8
    VERY_HIGH = "very_high"    # 0.8 - 1.0


@dataclass
class ConfidencePrediction:
    """Individual prediction with confidence tracking"""
    id: str
    timestamp: datetime
    symbol: str
    direction: str
    confidence: float
    confidence_zone: ConfidenceZone
    lstm_confidence: Optional[float] = None
    ensemble_confidence: Optional[float] = None
    models_agreement: Optional[float] = None
    actual_outcome: Optional[bool] = None  # Set when outcome is known
    correct_prediction: Optional[bool] = None


@dataclass
class ConfidenceCalibration:
    """Confidence calibration metrics"""
    timestamp: datetime
    confidence_zone: ConfidenceZone
    predicted_confidence: float
    actual_accuracy: float
    calibration_error: float
    sample_count: int
    reliability_diagram_data: Dict[str, List[float]]


@dataclass
class ConfidenceMetrics:
    """Comprehensive confidence metrics"""
    timestamp: datetime
    total_predictions: int
    avg_confidence: float
    confidence_std: float
    calibration_score: float
    overconfidence_rate: float
    underconfidence_rate: float
    zone_accuracy: Dict[str, float]
    zone_counts: Dict[str, int]


class MLConfidenceTracker:
    """
    ML Confidence Tracking Service
    
    Provides comprehensive confidence analysis including:
    - Confidence calibration monitoring
    - Prediction quality analytics
    - Overconfidence/underconfidence detection
    - Reliability diagram generation
    - Confidence zone performance tracking
    """
    
    def __init__(self):
        self.db_path = "/home/colindo/Sync/minh_v4/data/ml_confidence_tracker.db"
        
        # Prediction tracking
        self.predictions = {}  # id -> ConfidencePrediction
        self.prediction_history = deque(maxlen=1000)
        
        # Confidence zone tracking
        self.zone_predictions = defaultdict(list)
        self.zone_accuracy = defaultdict(list)
        
        # Calibration tracking
        self.calibration_history = deque(maxlen=100)
        self.confidence_bins = np.linspace(0.0, 1.0, 11)  # 10 bins from 0-1
        
        # Performance tracking
        self.confidence_tracker = deque(maxlen=500)
        self.accuracy_tracker = deque(maxlen=500)
        
        # Analytics
        self.overconfident_predictions = deque(maxlen=100)
        self.underconfident_predictions = deque(maxlen=100)
        
        # Initialize database
        self._init_database()
        
        logging.info("📊 ML Confidence Tracker initialized")
    
    def _init_database(self):
        """Initialize confidence tracking database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confidence_predictions (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    symbol TEXT,
                    direction TEXT,
                    confidence REAL,
                    confidence_zone TEXT,
                    lstm_confidence REAL,
                    ensemble_confidence REAL,
                    models_agreement REAL,
                    actual_outcome BOOLEAN,
                    correct_prediction BOOLEAN
                )
            """)
            
            # Calibration metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confidence_calibration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    confidence_zone TEXT,
                    predicted_confidence REAL,
                    actual_accuracy REAL,
                    calibration_error REAL,
                    sample_count INTEGER,
                    reliability_data TEXT
                )
            """)
            
            # Confidence metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confidence_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    total_predictions INTEGER,
                    avg_confidence REAL,
                    confidence_std REAL,
                    calibration_score REAL,
                    overconfidence_rate REAL,
                    underconfidence_rate REAL,
                    zone_accuracy TEXT,
                    zone_counts TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to initialize confidence tracker database: {e}")
    
    def _get_confidence_zone(self, confidence: float) -> ConfidenceZone:
        """Classify confidence into zones"""
        if confidence < 0.5:
            return ConfidenceZone.VERY_LOW
        elif confidence < 0.6:
            return ConfidenceZone.LOW
        elif confidence < 0.7:
            return ConfidenceZone.MEDIUM
        elif confidence < 0.8:
            return ConfidenceZone.HIGH
        else:
            return ConfidenceZone.VERY_HIGH
    
    async def record_prediction(
        self, 
        prediction_id: str,
        symbol: str,
        direction: str,
        confidence: float,
        lstm_confidence: Optional[float] = None,
        ensemble_confidence: Optional[float] = None,
        models_agreement: Optional[float] = None
    ) -> ConfidencePrediction:
        """Record a new prediction with confidence"""
        try:
            confidence_zone = self._get_confidence_zone(confidence)
            
            prediction = ConfidencePrediction(
                id=prediction_id,
                timestamp=datetime.now(),
                symbol=symbol,
                direction=direction,
                confidence=confidence,
                confidence_zone=confidence_zone,
                lstm_confidence=lstm_confidence,
                ensemble_confidence=ensemble_confidence,
                models_agreement=models_agreement
            )
            
            # Store prediction
            self.predictions[prediction_id] = prediction
            self.prediction_history.append(prediction)
            
            # Track by zone
            self.zone_predictions[confidence_zone.value].append(prediction)
            
            # Update tracking
            self.confidence_tracker.append(confidence)
            
            # Store in database
            await self._store_prediction(prediction)
            
            logging.info(f"📊 Recorded prediction {prediction_id}: {direction} with {confidence:.2f} confidence ({confidence_zone.value})")
            
            return prediction
            
        except Exception as e:
            logging.error(f"Failed to record prediction: {e}")
            return None
    
    async def update_prediction_outcome(
        self, 
        prediction_id: str, 
        actual_outcome: bool
    ):
        """Update prediction with actual outcome"""
        try:
            if prediction_id not in self.predictions:
                logging.warning(f"Prediction {prediction_id} not found")
                return
            
            prediction = self.predictions[prediction_id]
            prediction.actual_outcome = actual_outcome
            
            # Determine if prediction was correct based on direction and outcome
            if prediction.direction == "up":
                prediction.correct_prediction = actual_outcome
            elif prediction.direction == "down":
                prediction.correct_prediction = not actual_outcome
            else:  # neutral
                prediction.correct_prediction = True  # Neutral predictions are always "correct"
            
            # Update zone accuracy tracking
            self.zone_accuracy[prediction.confidence_zone.value].append(prediction.correct_prediction)
            
            # Update accuracy tracker
            self.accuracy_tracker.append(prediction.correct_prediction)
            
            # Check for over/underconfidence
            await self._analyze_confidence_calibration(prediction)
            
            # Update database
            await self._update_prediction_outcome(prediction)
            
            logging.info(f"📊 Updated prediction {prediction_id}: {'✅' if prediction.correct_prediction else '❌'} (confidence: {prediction.confidence:.2f})")
            
        except Exception as e:
            logging.error(f"Failed to update prediction outcome: {e}")
    
    async def _analyze_confidence_calibration(self, prediction: ConfidencePrediction):
        """Analyze confidence calibration for a prediction"""
        try:
            if prediction.actual_outcome is None or prediction.correct_prediction is None:
                return
            
            # Check for overconfidence (high confidence but wrong)
            if prediction.confidence > 0.8 and not prediction.correct_prediction:
                self.overconfident_predictions.append(prediction)
                logging.warning(f"📊 Overconfident prediction: {prediction.confidence:.2f} confidence but incorrect")
            
            # Check for underconfidence (low confidence but correct)
            if prediction.confidence < 0.6 and prediction.correct_prediction:
                self.underconfident_predictions.append(prediction)
                logging.info(f"📊 Underconfident prediction: {prediction.confidence:.2f} confidence but correct")
            
        except Exception as e:
            logging.error(f"Failed to analyze confidence calibration: {e}")
    
    async def calculate_confidence_metrics(self) -> ConfidenceMetrics:
        """Calculate comprehensive confidence metrics"""
        try:
            current_time = datetime.now()
            
            if not self.confidence_tracker:
                return ConfidenceMetrics(
                    timestamp=current_time,
                    total_predictions=0,
                    avg_confidence=0.0,
                    confidence_std=0.0,
                    calibration_score=0.0,
                    overconfidence_rate=0.0,
                    underconfidence_rate=0.0,
                    zone_accuracy={},
                    zone_counts={}
                )
            
            # Basic confidence statistics
            confidences = list(self.confidence_tracker)
            avg_confidence = statistics.mean(confidences)
            confidence_std = statistics.stdev(confidences) if len(confidences) > 1 else 0.0
            
            # Zone accuracy and counts
            zone_accuracy = {}
            zone_counts = {}
            
            for zone in ConfidenceZone:
                zone_name = zone.value
                zone_predictions = self.zone_predictions[zone_name]
                zone_accuracies = self.zone_accuracy[zone_name]
                
                zone_counts[zone_name] = len(zone_predictions)
                if zone_accuracies:
                    zone_accuracy[zone_name] = statistics.mean(zone_accuracies)
                else:
                    zone_accuracy[zone_name] = 0.0
            
            # Calibration score (simplified Expected Calibration Error)
            calibration_score = await self._calculate_calibration_score()
            
            # Over/underconfidence rates
            total_predictions_with_outcome = len([p for p in self.predictions.values() if p.actual_outcome is not None])
            overconfidence_rate = len(self.overconfident_predictions) / max(1, total_predictions_with_outcome)
            underconfidence_rate = len(self.underconfident_predictions) / max(1, total_predictions_with_outcome)
            
            metrics = ConfidenceMetrics(
                timestamp=current_time,
                total_predictions=len(self.predictions),
                avg_confidence=avg_confidence,
                confidence_std=confidence_std,
                calibration_score=calibration_score,
                overconfidence_rate=overconfidence_rate,
                underconfidence_rate=underconfidence_rate,
                zone_accuracy=zone_accuracy,
                zone_counts=zone_counts
            )
            
            # Store metrics
            await self._store_confidence_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to calculate confidence metrics: {e}")
            return ConfidenceMetrics(
                timestamp=datetime.now(),
                total_predictions=0,
                avg_confidence=0.0,
                confidence_std=0.0,
                calibration_score=1.0,  # Worst calibration score
                overconfidence_rate=0.0,
                underconfidence_rate=0.0,
                zone_accuracy={},
                zone_counts={}
            )
    
    async def _calculate_calibration_score(self) -> float:
        """Calculate Expected Calibration Error (ECE)"""
        try:
            # Get predictions with outcomes
            predictions_with_outcomes = [
                p for p in self.predictions.values() 
                if p.actual_outcome is not None and p.correct_prediction is not None
            ]
            
            if len(predictions_with_outcomes) < 10:
                return 0.0  # Not enough data for calibration
            
            # Bin predictions by confidence
            bin_boundaries = np.linspace(0.0, 1.0, 11)
            bin_lowers = bin_boundaries[:-1]
            bin_uppers = bin_boundaries[1:]
            
            ece = 0.0
            total_samples = len(predictions_with_outcomes)
            
            for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
                # Get predictions in this bin
                bin_predictions = [
                    p for p in predictions_with_outcomes
                    if bin_lower <= p.confidence < bin_upper
                ]
                
                if not bin_predictions:
                    continue
                
                # Calculate bin accuracy and confidence
                bin_accuracy = statistics.mean([p.correct_prediction for p in bin_predictions])
                bin_confidence = statistics.mean([p.confidence for p in bin_predictions])
                bin_weight = len(bin_predictions) / total_samples
                
                # Add to ECE
                ece += bin_weight * abs(bin_accuracy - bin_confidence)
            
            return ece
            
        except Exception as e:
            logging.error(f"Failed to calculate calibration score: {e}")
            return 1.0  # Return worst score on error
    
    async def generate_reliability_diagram_data(self) -> Dict[str, List[float]]:
        """Generate data for reliability diagram"""
        try:
            # Get predictions with outcomes
            predictions_with_outcomes = [
                p for p in self.predictions.values() 
                if p.actual_outcome is not None and p.correct_prediction is not None
            ]
            
            if len(predictions_with_outcomes) < 10:
                return {"confidence_bins": [], "accuracy_bins": [], "counts": []}
            
            # Bin predictions by confidence
            bin_boundaries = np.linspace(0.0, 1.0, 11)
            bin_centers = (bin_boundaries[:-1] + bin_boundaries[1:]) / 2
            
            confidence_bins = []
            accuracy_bins = []
            counts = []
            
            for i, (bin_lower, bin_upper) in enumerate(zip(bin_boundaries[:-1], bin_boundaries[1:])):
                # Get predictions in this bin
                bin_predictions = [
                    p for p in predictions_with_outcomes
                    if bin_lower <= p.confidence < bin_upper
                ]
                
                if bin_predictions:
                    bin_accuracy = statistics.mean([p.correct_prediction for p in bin_predictions])
                    bin_confidence = statistics.mean([p.confidence for p in bin_predictions])
                    
                    confidence_bins.append(bin_confidence)
                    accuracy_bins.append(bin_accuracy)
                    counts.append(len(bin_predictions))
                else:
                    confidence_bins.append(bin_centers[i])
                    accuracy_bins.append(0.0)
                    counts.append(0)
            
            return {
                "confidence_bins": confidence_bins,
                "accuracy_bins": accuracy_bins,
                "counts": counts,
                "bin_centers": bin_centers.tolist()
            }
            
        except Exception as e:
            logging.error(f"Failed to generate reliability diagram data: {e}")
            return {"confidence_bins": [], "accuracy_bins": [], "counts": []}
    
    async def get_confidence_analytics(self) -> Dict[str, Any]:
        """Get comprehensive confidence analytics"""
        try:
            metrics = await self.calculate_confidence_metrics()
            reliability_data = await self.generate_reliability_diagram_data()
            
            # Recent performance by zone
            recent_zone_performance = {}
            for zone in ConfidenceZone:
                zone_name = zone.value
                recent_predictions = [
                    p for p in list(self.prediction_history)[-100:]  # Last 100 predictions
                    if p.confidence_zone == zone and p.correct_prediction is not None
                ]
                
                if recent_predictions:
                    recent_accuracy = statistics.mean([p.correct_prediction for p in recent_predictions])
                    recent_zone_performance[zone_name] = {
                        "accuracy": recent_accuracy,
                        "count": len(recent_predictions),
                        "avg_confidence": statistics.mean([p.confidence for p in recent_predictions])
                    }
                else:
                    recent_zone_performance[zone_name] = {
                        "accuracy": 0.0,
                        "count": 0,
                        "avg_confidence": 0.0
                    }
            
            # Calibration issues
            calibration_issues = []
            if metrics.overconfidence_rate > 0.2:
                calibration_issues.append("High overconfidence rate")
            if metrics.underconfidence_rate > 0.2:
                calibration_issues.append("High underconfidence rate")
            if metrics.calibration_score > 0.1:
                calibration_issues.append("Poor calibration")
            
            return {
                "metrics": asdict(metrics),
                "reliability_diagram": reliability_data,
                "recent_zone_performance": recent_zone_performance,
                "calibration_issues": calibration_issues,
                "recommendations": await self._generate_recommendations(metrics),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Failed to get confidence analytics: {e}")
            return {"error": str(e)}
    
    async def _generate_recommendations(self, metrics: ConfidenceMetrics) -> List[str]:
        """Generate recommendations based on confidence metrics"""
        recommendations = []
        
        try:
            # Calibration recommendations
            if metrics.calibration_score > 0.15:
                recommendations.append("Consider confidence calibration training to improve reliability")
            
            # Overconfidence recommendations
            if metrics.overconfidence_rate > 0.25:
                recommendations.append("Model shows overconfidence - consider temperature scaling or confidence penalties")
            
            # Underconfidence recommendations
            if metrics.underconfidence_rate > 0.25:
                recommendations.append("Model may be underconfident - consider confidence boosting techniques")
            
            # Zone-specific recommendations
            for zone_name, accuracy in metrics.zone_accuracy.items():
                count = metrics.zone_counts.get(zone_name, 0)
                if count > 10:  # Enough samples
                    if zone_name == "very_high" and accuracy < 0.8:
                        recommendations.append(f"Very high confidence predictions underperforming ({accuracy:.1%})")
                    elif zone_name == "high" and accuracy < 0.7:
                        recommendations.append(f"High confidence predictions underperforming ({accuracy:.1%})")
            
            # Confidence spread recommendations
            if metrics.confidence_std < 0.1:
                recommendations.append("Low confidence variance - model may benefit from confidence diversity training")
            elif metrics.confidence_std > 0.3:
                recommendations.append("High confidence variance - consider confidence regularization")
            
            if not recommendations:
                recommendations.append("Confidence calibration appears healthy")
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Failed to generate recommendations: {e}")
            return ["Unable to generate recommendations"]
    
    async def _store_prediction(self, prediction: ConfidencePrediction):
        """Store prediction in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO confidence_predictions 
                (id, timestamp, symbol, direction, confidence, confidence_zone,
                 lstm_confidence, ensemble_confidence, models_agreement, 
                 actual_outcome, correct_prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.id,
                prediction.timestamp,
                prediction.symbol,
                prediction.direction,
                prediction.confidence,
                prediction.confidence_zone.value,
                prediction.lstm_confidence,
                prediction.ensemble_confidence,
                prediction.models_agreement,
                prediction.actual_outcome,
                prediction.correct_prediction
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store prediction: {e}")
    
    async def _update_prediction_outcome(self, prediction: ConfidencePrediction):
        """Update prediction outcome in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE confidence_predictions 
                SET actual_outcome = ?, correct_prediction = ?
                WHERE id = ?
            """, (
                prediction.actual_outcome,
                prediction.correct_prediction,
                prediction.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to update prediction outcome: {e}")
    
    async def _store_confidence_metrics(self, metrics: ConfidenceMetrics):
        """Store confidence metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO confidence_metrics 
                (timestamp, total_predictions, avg_confidence, confidence_std, 
                 calibration_score, overconfidence_rate, underconfidence_rate,
                 zone_accuracy, zone_counts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp,
                metrics.total_predictions,
                metrics.avg_confidence,
                metrics.confidence_std,
                metrics.calibration_score,
                metrics.overconfidence_rate,
                metrics.underconfidence_rate,
                json.dumps(metrics.zone_accuracy),
                json.dumps(metrics.zone_counts)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store confidence metrics: {e}")


# Standalone test function
async def test_confidence_tracker():
    """Test confidence tracking service"""
    print("Testing ML Confidence Tracker...")
    
    tracker = MLConfidenceTracker()
    
    # Record some test predictions
    await tracker.record_prediction("pred_1", "NQU25", "up", 0.85, 0.8, 0.9, 0.95)
    await tracker.record_prediction("pred_2", "NQU25", "down", 0.65, 0.7, 0.6, 0.8)
    await tracker.record_prediction("pred_3", "NQU25", "up", 0.55, 0.5, 0.6, 0.4)
    
    # Simulate outcomes
    await tracker.update_prediction_outcome("pred_1", True)   # Correct high confidence
    await tracker.update_prediction_outcome("pred_2", False)  # Incorrect medium confidence  
    await tracker.update_prediction_outcome("pred_3", True)   # Correct low confidence (underconfident)
    
    # Calculate metrics
    metrics = await tracker.calculate_confidence_metrics()
    print(f"✅ Confidence Metrics: Avg={metrics.avg_confidence:.2f}, Calibration={metrics.calibration_score:.3f}")
    
    # Get analytics
    analytics = await tracker.get_confidence_analytics()
    print(f"✅ Analytics: {len(analytics['recommendations'])} recommendations")
    
    print("✅ ML Confidence Tracker test completed")


if __name__ == "__main__":
    asyncio.run(test_confidence_tracker())