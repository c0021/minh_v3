"""
LSTM Training Pipeline

Self-contained training system for LSTM neural network using Sierra Chart historical data.
Integrates with consolidated market_data_service.py for historical data access.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import pickle

# TensorFlow imports with fallback
try:
    import tensorflow as tf
    from tensorflow import keras
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow not available. LSTM trainer will run in simulation mode.")

from .lstm_predictor import LSTMPredictor
from .data_pipeline import LSTMDataPipeline

class LSTMTrainer:
    """
    Self-contained LSTM training pipeline.
    
    Features:
    - Historical data integration with Sierra Chart
    - Automated feature engineering
    - Model training with validation
    - Performance evaluation
    - Model persistence and versioning
    """
    
    def __init__(self, predictor: LSTMPredictor = None):
        self.predictor = predictor
        self.data_pipeline = LSTMDataPipeline()
        self.logger = logging.getLogger(__name__)
        
        # Training configuration
        self.config = {
            'epochs': 50,
            'batch_size': 32,
            'validation_split': 0.2,
            'early_stopping_patience': 10,
            'learning_rate': 0.001,
            'min_data_points': 500,
            'sequence_length': 20,
            'features': 8
        }
        
        # Training history
        self.training_history = []
        self.best_model_path = None
        
        # Historical data service reference
        self.historical_service = None
        
    async def get_historical_service(self):
        """Get historical data service for training data"""
        if self.historical_service is None:
            try:
                # Import here to avoid circular imports
                import sys
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                
                from minhos.services.sierra_historical_data import get_sierra_historical_service
                self.historical_service = get_sierra_historical_service()
                
            except ImportError as e:
                self.logger.error(f"Could not import historical service: {e}")
                
        return self.historical_service
    
    async def load_training_data(self, symbol: str = 'NQ', days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Load historical data for training
        
        Args:
            symbol: Trading symbol (e.g., 'NQ')
            days_back: Number of days of historical data
            
        Returns:
            List of historical market data points
        """
        try:
            historical_service = await self.get_historical_service()
            
            if historical_service is None:
                # Fallback to synthetic data for testing
                self.logger.warning("No historical service available, generating synthetic data")
                return self._generate_synthetic_data(days_back)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Loading {days_back} days of {symbol} data from {start_date.date()} to {end_date.date()}")
            
            # Load historical data
            historical_data = await historical_service.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe='1min'  # 1-minute bars for detailed training
            )
            
            if not historical_data:
                self.logger.warning("No historical data returned, generating synthetic data")
                return self._generate_synthetic_data(days_back)
            
            # Convert to standard format
            training_data = []
            for data_point in historical_data:
                if isinstance(data_point, dict):
                    # Ensure required fields
                    standardized = {
                        'timestamp': data_point.get('timestamp', datetime.now().timestamp()),
                        'open': float(data_point.get('open', data_point.get('price', 0))),
                        'high': float(data_point.get('high', data_point.get('price', 0))),
                        'low': float(data_point.get('low', data_point.get('price', 0))),
                        'close': float(data_point.get('close', data_point.get('price', 0))),
                        'price': float(data_point.get('price', data_point.get('close', 0))),
                        'volume': float(data_point.get('volume', 1))
                    }
                    training_data.append(standardized)
            
            self.logger.info(f"Loaded {len(training_data)} data points for training")
            return training_data
            
        except Exception as e:
            self.logger.error(f"Error loading training data: {e}")
            return self._generate_synthetic_data(days_back)
    
    def _generate_synthetic_data(self, days_back: int) -> List[Dict[str, Any]]:
        """Generate synthetic market data for testing when real data unavailable"""
        synthetic_data = []
        base_price = 23400.0
        base_time = datetime.now() - timedelta(days=days_back)
        
        # Generate realistic price movement
        np.random.seed(42)  # Reproducible
        price_changes = np.random.normal(0, 2.0, days_back * 24 * 60)  # 1-minute intervals
        
        current_price = base_price
        current_time = base_time
        
        for i, change in enumerate(price_changes):
            current_price += change
            current_time += timedelta(minutes=1)
            
            # Generate OHLC from price movement
            high = current_price + abs(np.random.normal(0, 1.0))
            low = current_price - abs(np.random.normal(0, 1.0))
            open_price = current_price + np.random.normal(0, 0.5)
            
            synthetic_data.append({
                'timestamp': current_time.timestamp(),
                'open': open_price,
                'high': max(high, open_price, current_price),
                'low': min(low, open_price, current_price),
                'close': current_price,
                'price': current_price,
                'volume': max(1, int(np.random.normal(1500, 300)))
            })
        
        self.logger.info(f"Generated {len(synthetic_data)} synthetic data points")
        return synthetic_data
    
    async def train_lstm_model(self, 
                              symbol: str = 'NQ', 
                              days_back: int = 30,
                              save_model: bool = True) -> Dict[str, Any]:
        """
        Complete LSTM training pipeline
        
        Args:
            symbol: Trading symbol
            days_back: Days of historical data
            save_model: Whether to save the trained model
            
        Returns:
            Training results and metrics
        """
        if not HAS_TENSORFLOW:
            return {
                'success': False,
                'message': 'TensorFlow not available'
            }
        
        if not self.predictor:
            return {
                'success': False,
                'message': 'No LSTM predictor provided'
            }
        
        try:
            self.logger.info(f"🧠 Starting LSTM training for {symbol} with {days_back} days of data")
            
            # Step 1: Load historical data
            self.logger.info("📊 Loading historical data...")
            training_data = await self.load_training_data(symbol, days_back)
            
            if len(training_data) < self.config['min_data_points']:
                return {
                    'success': False,
                    'message': f'Insufficient data. Need {self.config["min_data_points"]}, got {len(training_data)}'
                }
            
            # Step 2: Prepare training data
            self.logger.info("🔧 Preparing training sequences...")
            X, y = self.data_pipeline.prepare_training_data(training_data)
            
            if len(X) == 0:
                return {
                    'success': False,
                    'message': 'No valid training sequences created'
                }
            
            # Step 3: Validate data quality
            validation_result = self.data_pipeline.validate_data_quality(X)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': f'Data quality check failed: {validation_result["reason"]}'
                }
            
            # Step 4: Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, 
                test_size=self.config['validation_split'],
                shuffle=False  # Keep temporal order
            )
            
            self.logger.info(f"📈 Training set: {len(X_train)} samples, Validation set: {len(X_val)} samples")
            
            # Step 5: Build and compile model
            self.logger.info("🏗️ Building LSTM model...")
            self.predictor.model = self.predictor.build_model()
            
            if self.predictor.model is None:
                return {
                    'success': False,
                    'message': 'Failed to build LSTM model'
                }
            
            # Step 6: Setup callbacks
            callbacks = self._create_training_callbacks()
            
            # Step 7: Train model
            self.logger.info("🚀 Starting model training...")
            
            # Set TensorFlow to only show errors to reduce log noise
            tf.get_logger().setLevel('ERROR')
            
            history = self.predictor.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=self.config['epochs'],
                batch_size=self.config['batch_size'],
                verbose=1,
                callbacks=callbacks
            )
            
            # Step 8: Evaluate model
            self.logger.info("📊 Evaluating model performance...")
            evaluation_results = self._evaluate_model(X_val, y_val, history)
            
            # Step 9: Save model if requested
            if save_model:
                save_result = await self._save_model(symbol, evaluation_results)
                evaluation_results.update(save_result)
            
            # Step 10: Update predictor state
            self.predictor.is_trained = True
            
            # Record training session
            training_session = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'days_back': days_back,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'results': evaluation_results
            }
            self.training_history.append(training_session)
            
            self.logger.info("✅ LSTM training completed successfully!")
            
            return {
                'success': True,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'data_points_used': len(training_data),
                'epochs_completed': len(history.history['loss']),
                **evaluation_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ LSTM training failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Training error: {str(e)}'
            }
    
    def _create_training_callbacks(self) -> List:
        """Create training callbacks for model optimization"""
        callbacks = []
        
        # Early stopping
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=self.config['early_stopping_patience'],
            restore_best_weights=True,
            verbose=1
        )
        callbacks.append(early_stop)
        
        # Learning rate reduction
        lr_reducer = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
        callbacks.append(lr_reducer)
        
        # Model checkpoint (save best model)
        if self.predictor and self.predictor.model_path:
            checkpoint_path = f"{self.predictor.model_path}_checkpoint.h5"
            checkpoint = keras.callbacks.ModelCheckpoint(
                checkpoint_path,
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
            callbacks.append(checkpoint)
            self.best_model_path = checkpoint_path
        
        return callbacks
    
    def _evaluate_model(self, X_val: np.ndarray, y_val: np.ndarray, history) -> Dict[str, Any]:
        """Evaluate trained model performance"""
        results = {}
        
        try:
            # Training history metrics
            final_loss = history.history['loss'][-1]
            final_val_loss = history.history['val_loss'][-1]
            
            results.update({
                'final_loss': float(final_loss),
                'final_val_loss': float(final_val_loss),
                'best_val_loss': float(min(history.history['val_loss'])),
                'training_epochs': len(history.history['loss'])
            })
            
            # Prediction accuracy evaluation
            if len(X_val) > 0:
                predictions = self.predictor.model.predict(X_val, verbose=0)
                
                # Direction accuracy (most important for trading)
                pred_directions = np.sign(predictions.flatten())
                true_directions = np.sign(y_val)
                direction_accuracy = np.mean(pred_directions == true_directions)
                
                # Regression metrics
                mse = np.mean((predictions.flatten() - y_val) ** 2)
                mae = np.mean(np.abs(predictions.flatten() - y_val))
                
                results.update({
                    'direction_accuracy': float(direction_accuracy),
                    'mse': float(mse),
                    'mae': float(mae),
                    'prediction_samples': len(predictions)
                })
                
                self.logger.info(f"📈 Direction Accuracy: {direction_accuracy:.1%}")
                self.logger.info(f"📉 MSE: {mse:.6f}, MAE: {mae:.6f}")
            
        except Exception as e:
            self.logger.error(f"Model evaluation error: {e}")
            results['evaluation_error'] = str(e)
        
        return results
    
    async def _save_model(self, symbol: str, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Save trained model with metadata"""
        try:
            if not self.predictor or not self.predictor.model:
                return {'save_error': 'No model to save'}
            
            # Save model
            model_path = f"{self.predictor.model_path}.h5"
            self.predictor.model.save(model_path)
            
            # Save metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'model_path': model_path,
                'config': self.config,
                'evaluation_results': evaluation_results,
                'feature_info': self.data_pipeline.get_feature_info()
            }
            
            metadata_path = f"{self.predictor.model_path}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"💾 Model saved: {model_path}")
            self.logger.info(f"📋 Metadata saved: {metadata_path}")
            
            return {
                'model_saved': True,
                'model_path': model_path,
                'metadata_path': metadata_path
            }
            
        except Exception as e:
            self.logger.error(f"Model saving error: {e}")
            return {'save_error': str(e)}
    
    def get_training_config(self) -> Dict[str, Any]:
        """Get current training configuration"""
        return self.config.copy()
    
    def update_training_config(self, **kwargs):
        """Update training configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated training config: {key} = {value}")
    
    def get_training_history(self) -> List[Dict[str, Any]]:
        """Get history of training sessions"""
        return self.training_history.copy()
    
    async def retrain_model(self, symbol: str = 'NQ', days_back: int = 30) -> Dict[str, Any]:
        """Retrain existing model with fresh data"""
        self.logger.info("🔄 Retraining LSTM model with fresh data...")
        return await self.train_lstm_model(symbol, days_back, save_model=True)