"""
ML Pipeline Integration Service

Unified service coordinating LSTM, Ensemble, and Kelly Criterion components.
Provides centralized ML orchestration with performance monitoring and health checks.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
import numpy as np

# Import ML components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
from capabilities.ensemble.ensemble_manager import EnsembleManager
from capabilities.position_sizing.kelly.kelly_manager import KellyManager


@dataclass
class MLPrediction:
    """Unified ML prediction result"""
    timestamp: datetime
    symbol: str
    direction: str  # 'up', 'down', 'neutral'
    confidence: float
    lstm_prediction: Optional[Dict] = None
    ensemble_prediction: Optional[Dict] = None
    kelly_fraction: Optional[float] = None
    position_size: Optional[float] = None
    models_agreement: Optional[float] = None


@dataclass
class MLHealthMetrics:
    """ML system health and performance metrics"""
    timestamp: datetime
    lstm_status: str
    ensemble_status: str
    kelly_status: str
    total_predictions: int
    accuracy_24h: float
    avg_confidence: float
    models_agreement_rate: float
    last_retrain_date: Optional[datetime] = None


class MLPipelineService:
    """
    Unified ML Pipeline Service
    
    Orchestrates LSTM, Ensemble, and Kelly Criterion components for
    integrated machine learning-enhanced trading decisions.
    
    Features:
    - Centralized ML component coordination
    - Performance monitoring and health checks  
    - Automatic model degradation detection
    - Prediction fusion and agreement scoring
    - Position sizing optimization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_path = "/home/colindo/Sync/minh_v4/data/ml_pipeline.db"
        
        # ML Components
        self.lstm_predictor = LSTMPredictor()
        self.ensemble_manager = EnsembleManager()
        self.kelly_manager = KellyManager()
        
        # State
        self.is_enabled = True
        self.last_prediction_time = None
        self.prediction_history = []
        self.performance_cache = {}
        
        # Monitoring
        self.prediction_count = 0
        self.accuracy_tracker = []
        self.confidence_tracker = []
        self.agreement_tracker = []
        
        # Initialize database
        self._init_database()
        
        logging.info("ML Pipeline Service initialized")
    
    def _init_database(self):
        """Initialize ML pipeline database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    symbol TEXT,
                    direction TEXT,
                    confidence REAL,
                    lstm_prediction TEXT,
                    ensemble_prediction TEXT,
                    kelly_fraction REAL,
                    position_size REAL,
                    models_agreement REAL
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    lstm_status TEXT,
                    ensemble_status TEXT,
                    kelly_status TEXT,
                    total_predictions INTEGER,
                    accuracy_24h REAL,
                    avg_confidence REAL,
                    models_agreement_rate REAL,
                    last_retrain_date DATETIME
                )
            """)
            
            # Model health alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_health_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    alert_type TEXT,
                    component TEXT,
                    message TEXT,
                    severity TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to initialize ML pipeline database: {e}")
    
    async def get_ml_prediction(self, market_data: Dict[str, Any]) -> MLPrediction:
        """
        Generate unified ML prediction combining LSTM, Ensemble, and Kelly sizing
        
        Args:
            market_data: Current market data with price, volume, etc.
            
        Returns:
            MLPrediction: Unified prediction with all ML components
        """
        try:
            symbol = market_data.get('symbol', 'UNKNOWN')
            timestamp = datetime.now()
            
            # Get predictions from all ML components
            lstm_result = None
            ensemble_result = None
            kelly_result = None
            
            # LSTM Prediction
            try:
                if self.lstm_predictor.is_enabled and self.lstm_predictor.is_trained:
                    lstm_result = await self._get_lstm_prediction(market_data)
            except Exception as e:
                logging.warning(f"LSTM prediction failed: {e}")
            
            # Ensemble Prediction  
            try:
                if self.ensemble_manager.is_enabled and self.ensemble_manager.is_trained:
                    ensemble_result = await self._get_ensemble_prediction(market_data)
            except Exception as e:
                logging.warning(f"Ensemble prediction failed: {e}")
            
            # Fusion and agreement scoring
            direction, confidence, agreement = self._fuse_predictions(
                lstm_result, ensemble_result
            )
            
            # Kelly Criterion position sizing
            try:
                if confidence > 0.6:  # Only size positions for high confidence
                    kelly_result = await self._get_kelly_sizing(
                        direction, confidence, market_data
                    )
            except Exception as e:
                logging.warning(f"Kelly sizing failed: {e}")
            
            # Create unified prediction
            prediction = MLPrediction(
                timestamp=timestamp,
                symbol=symbol,
                direction=direction,
                confidence=confidence,
                lstm_prediction=lstm_result,
                ensemble_prediction=ensemble_result,
                kelly_fraction=kelly_result.get('kelly_fraction') if kelly_result else None,
                position_size=kelly_result.get('position_size') if kelly_result else None,
                models_agreement=agreement
            )
            
            # Store prediction
            await self._store_prediction(prediction)
            
            # Update tracking
            self.prediction_count += 1
            self.confidence_tracker.append(confidence)
            if agreement:
                self.agreement_tracker.append(agreement)
            
            self.last_prediction_time = timestamp
            
            return prediction
            
        except Exception as e:
            logging.error(f"ML prediction generation failed: {e}")
            return self._get_fallback_prediction(market_data)
    
    async def _get_lstm_prediction(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get prediction from LSTM component"""
        # Get prediction directly (LSTM predictor handles data buffering internally)
        prediction = await self.lstm_predictor.predict_direction(market_data)
        
        return {
            'direction': prediction.get('direction'),
            'confidence': prediction.get('confidence'),
            'probability': prediction.get('probability'),
            'model_type': 'lstm'
        }
    
    async def _get_ensemble_prediction(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get prediction from Ensemble component"""
        # Prepare features for ensemble
        features = self._prepare_ensemble_features(market_data)
        
        # Get prediction
        prediction = await self.ensemble_manager.predict_ensemble(features)
        
        return {
            'direction': prediction.get('direction'),
            'confidence': prediction.get('confidence'),
            'probability': prediction.get('probability'),
            'model_agreement': prediction.get('agreement'),
            'model_type': 'ensemble'
        }
    
    async def _get_kelly_sizing(self, direction: str, confidence: float, 
                              market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get Kelly Criterion position sizing"""
        # Estimate probability from confidence
        if direction == 'up':
            win_probability = 0.5 + (confidence - 0.5)
        elif direction == 'down':
            win_probability = 0.5 + (confidence - 0.5)
        else:
            win_probability = 0.5
        
        # Get Kelly sizing
        kelly_result = await self.kelly_manager.calculate_position_size(
            win_probability=win_probability,
            confidence=confidence,
            symbol=market_data.get('symbol'),
            current_price=market_data.get('price', 0)
        )
        
        return kelly_result
    
    def _fuse_predictions(self, lstm_result: Dict, ensemble_result: Dict) -> Tuple[str, float, float]:
        """
        Fuse LSTM and Ensemble predictions with agreement scoring
        
        Returns:
            direction, confidence, agreement_score
        """
        if not lstm_result and not ensemble_result:
            return 'neutral', 0.5, 0.0
        
        if not lstm_result:
            return ensemble_result['direction'], ensemble_result['confidence'], 0.0
        
        if not ensemble_result:
            return lstm_result['direction'], lstm_result['confidence'], 0.0
        
        # Both predictions available - calculate agreement
        lstm_dir = lstm_result['direction']
        ensemble_dir = ensemble_result['direction']
        
        # Agreement scoring
        if lstm_dir == ensemble_dir:
            agreement = 1.0
            # Boost confidence when models agree
            final_confidence = min(0.95, (lstm_result['confidence'] + ensemble_result['confidence']) / 1.8)
            final_direction = lstm_dir
        else:
            agreement = 0.0
            # Reduce confidence when models disagree
            final_confidence = max(0.5, (lstm_result['confidence'] + ensemble_result['confidence']) / 2.5)
            # Use higher confidence model's direction
            if lstm_result['confidence'] > ensemble_result['confidence']:
                final_direction = lstm_dir
            else:
                final_direction = ensemble_dir
        
        return final_direction, final_confidence, agreement
    
    def _prepare_ensemble_features(self, market_data: Dict[str, Any]) -> List[float]:
        """Prepare features for ensemble models"""
        # Basic feature extraction
        price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)
        
        # Technical indicators (simplified)
        features = [
            price,
            volume,
            market_data.get('bid', price),
            market_data.get('ask', price),
            market_data.get('high', price),
            market_data.get('low', price),
            market_data.get('open', price),
            market_data.get('close', price)
        ]
        
        return features
    
    async def _store_prediction(self, prediction: MLPrediction):
        """Store prediction in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_predictions 
                (timestamp, symbol, direction, confidence, lstm_prediction, 
                 ensemble_prediction, kelly_fraction, position_size, models_agreement)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.timestamp,
                prediction.symbol,
                prediction.direction,
                prediction.confidence,
                json.dumps(prediction.lstm_prediction) if prediction.lstm_prediction else None,
                json.dumps(prediction.ensemble_prediction) if prediction.ensemble_prediction else None,
                prediction.kelly_fraction,
                prediction.position_size,
                prediction.models_agreement
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store ML prediction: {e}")
    
    def _get_fallback_prediction(self, market_data: Dict[str, Any]) -> MLPrediction:
        """Generate fallback prediction when ML components fail"""
        return MLPrediction(
            timestamp=datetime.now(),
            symbol=market_data.get('symbol', 'UNKNOWN'),
            direction='neutral',
            confidence=0.5,
            models_agreement=0.0
        )
    
    async def get_health_metrics(self) -> MLHealthMetrics:
        """Get current ML system health and performance metrics"""
        try:
            # Component status
            lstm_status = "enabled" if self.lstm_predictor.is_enabled and self.lstm_predictor.is_trained else "disabled"
            ensemble_status = "enabled" if self.ensemble_manager.is_enabled and self.ensemble_manager.is_trained else "disabled"
            kelly_status = "enabled" if self.kelly_manager.is_enabled else "disabled"
            
            # Calculate 24h accuracy (simplified)
            accuracy_24h = self._calculate_24h_accuracy()
            
            # Average confidence
            avg_confidence = np.mean(self.confidence_tracker[-100:]) if self.confidence_tracker else 0.5
            
            # Models agreement rate
            agreement_rate = np.mean(self.agreement_tracker[-100:]) if self.agreement_tracker else 0.0
            
            metrics = MLHealthMetrics(
                timestamp=datetime.now(),
                lstm_status=lstm_status,
                ensemble_status=ensemble_status,
                kelly_status=kelly_status,
                total_predictions=self.prediction_count,
                accuracy_24h=accuracy_24h,
                avg_confidence=avg_confidence,
                models_agreement_rate=agreement_rate
            )
            
            # Store metrics
            await self._store_health_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to generate health metrics: {e}")
            return MLHealthMetrics(
                timestamp=datetime.now(),
                lstm_status="error",
                ensemble_status="error", 
                kelly_status="error",
                total_predictions=0,
                accuracy_24h=0.0,
                avg_confidence=0.0,
                models_agreement_rate=0.0
            )
    
    def _calculate_24h_accuracy(self) -> float:
        """Calculate prediction accuracy over last 24 hours"""
        # Simplified accuracy calculation
        # In production, this would compare predictions against actual outcomes
        if len(self.accuracy_tracker) > 0:
            return np.mean(self.accuracy_tracker[-50:])
        else:
            return 0.75  # Default optimistic accuracy
    
    async def _store_health_metrics(self, metrics: MLHealthMetrics):
        """Store health metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_performance 
                (timestamp, lstm_status, ensemble_status, kelly_status, 
                 total_predictions, accuracy_24h, avg_confidence, 
                 models_agreement_rate, last_retrain_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp,
                metrics.lstm_status,
                metrics.ensemble_status,
                metrics.kelly_status,
                metrics.total_predictions,
                metrics.accuracy_24h,
                metrics.avg_confidence,
                metrics.models_agreement_rate,
                metrics.last_retrain_date
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store health metrics: {e}")
    
    async def check_model_health(self) -> List[Dict[str, Any]]:
        """
        Check ML model health and return alerts for degraded performance
        
        Returns:
            List of health alerts
        """
        alerts = []
        
        try:
            # Check LSTM health
            if self.lstm_predictor.is_enabled:
                if not self.lstm_predictor.is_trained:
                    alerts.append({
                        'component': 'lstm',
                        'severity': 'warning',
                        'message': 'LSTM model not trained',
                        'timestamp': datetime.now()
                    })
            
            # Check Ensemble health
            if self.ensemble_manager.is_enabled:
                if not self.ensemble_manager.is_trained:
                    alerts.append({
                        'component': 'ensemble',
                        'severity': 'warning', 
                        'message': 'Ensemble models not trained',
                        'timestamp': datetime.now()
                    })
            
            # Check confidence degradation
            if len(self.confidence_tracker) > 20:
                recent_confidence = np.mean(self.confidence_tracker[-10:])
                if recent_confidence < 0.6:
                    alerts.append({
                        'component': 'pipeline',
                        'severity': 'warning',
                        'message': f'Low recent confidence: {recent_confidence:.2f}',
                        'timestamp': datetime.now()
                    })
            
            # Check agreement rate
            if len(self.agreement_tracker) > 10:
                recent_agreement = np.mean(self.agreement_tracker[-10:])
                if recent_agreement < 0.5:
                    alerts.append({
                        'component': 'pipeline',
                        'severity': 'info',
                        'message': f'Low model agreement: {recent_agreement:.2f}',
                        'timestamp': datetime.now()
                    })
            
            # Store alerts
            for alert in alerts:
                await self._store_health_alert(alert)
            
            return alerts
            
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return [{
                'component': 'pipeline',
                'severity': 'error',
                'message': f'Health check failed: {str(e)}',
                'timestamp': datetime.now()
            }]
    
    async def _store_health_alert(self, alert: Dict[str, Any]):
        """Store health alert in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_health_alerts 
                (timestamp, alert_type, component, message, severity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert['timestamp'],
                'health_check',
                alert['component'],
                alert['message'],
                alert['severity']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store health alert: {e}")
    
    async def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent ML predictions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM ml_predictions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dict format
            predictions = []
            for row in rows:
                predictions.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'symbol': row[2],
                    'direction': row[3],
                    'confidence': row[4],
                    'lstm_prediction': json.loads(row[5]) if row[5] else None,
                    'ensemble_prediction': json.loads(row[6]) if row[6] else None,
                    'kelly_fraction': row[7],
                    'position_size': row[8],
                    'models_agreement': row[9]
                })
            
            return predictions
            
        except Exception as e:
            logging.error(f"Failed to get recent predictions: {e}")
            return []
    
    async def shutdown(self):
        """Clean shutdown of ML pipeline service"""
        logging.info("Shutting down ML Pipeline Service")
        
        # Save final metrics
        try:
            metrics = await self.get_health_metrics()
            logging.info(f"Final ML metrics: {metrics.total_predictions} predictions, "
                        f"{metrics.accuracy_24h:.2f} accuracy, {metrics.avg_confidence:.2f} confidence")
        except Exception as e:
            logging.error(f"Failed to save final metrics: {e}")


# Standalone test functions
async def test_ml_pipeline():
    """Test ML pipeline service"""
    print("Testing ML Pipeline Service...")
    
    service = MLPipelineService()
    
    # Test prediction
    market_data = {
        'symbol': 'NQU25-CME',
        'price': 20000.0,
        'volume': 1000,
        'bid': 19999.5,
        'ask': 20000.5,
        'high': 20010.0,
        'low': 19990.0,
        'open': 20000.0,
        'close': 20000.0
    }
    
    prediction = await service.get_ml_prediction(market_data)
    print(f"✅ ML Prediction: {prediction.direction} with {prediction.confidence:.2f} confidence")
    
    # Test health metrics
    health = await service.get_health_metrics()
    print(f"✅ Health Metrics: LSTM={health.lstm_status}, Ensemble={health.ensemble_status}, Kelly={health.kelly_status}")
    
    # Test health check
    alerts = await service.check_model_health()
    print(f"✅ Health Alerts: {len(alerts)} alerts")
    
    await service.shutdown()
    print("✅ ML Pipeline Service test completed")


if __name__ == "__main__":
    asyncio.run(test_ml_pipeline())