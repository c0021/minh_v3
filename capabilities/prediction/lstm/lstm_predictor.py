"""
LSTM Neural Network Predictor

Self-contained LSTM implementation for price direction prediction.
Designed to integrate cleanly with consolidated ai_brain_service.py.
"""

import numpy as np
import asyncio
import logging
from collections import deque
from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime

# TensorFlow imports with fallback
try:
    import tensorflow as tf
    from tensorflow import keras
    from sklearn.preprocessing import MinMaxScaler
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow not available. LSTM predictor will run in simulation mode.")

class LSTMPredictor:
    """
    Self-contained LSTM neural network for price direction prediction.
    
    Features:
    - Price direction prediction with confidence scores
    - Self-contained feature engineering
    - Automatic model training and retraining
    - Clean integration API for ai_brain_service.py
    """
    
    def __init__(self, sequence_length: int = 20, features: int = 8, model_path: str = None):
        self.sequence_length = sequence_length
        self.features = features
        self.model_path = model_path or "/home/colindo/Sync/minh_v4/ml_models/lstm_model"
        
        # Model components
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self.is_enabled = HAS_TENSORFLOW
        
        # Data buffer for sequence creation
        self.data_buffer = deque(maxlen=sequence_length * 2)
        
        # Performance tracking
        self.predictions_made = 0
        self.accuracy_window = deque(maxlen=100)
        
        # Configuration
        self.config = {
            'confidence_threshold': 0.6,
            'retrain_frequency_hours': 24,
            'min_data_points': sequence_length + 10
        }
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the LSTM predictor"""
        if not self.is_enabled:
            self.logger.warning("LSTM Predictor disabled - TensorFlow not available")
            return
            
        # Ensure model directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Try to load existing model
        if os.path.exists(f"{self.model_path}.h5"):
            try:
                # Load with custom objects for TensorFlow compatibility
                custom_objects = {
                    'mse': tf.keras.metrics.MeanSquaredError(),
                    'mae': tf.keras.metrics.MeanAbsoluteError(),
                    'mape': tf.keras.metrics.MeanAbsolutePercentageError()
                }
                self.model = keras.models.load_model(f"{self.model_path}.h5", custom_objects=custom_objects)
                self.is_trained = True
                self.logger.info("LSTM model loaded successfully")
            except Exception as e:
                self.logger.warning(f"Could not load existing model: {e}")
                # Try loading without custom objects as fallback
                try:
                    self.model = keras.models.load_model(f"{self.model_path}.h5", compile=False)
                    # Recompile with current metrics
                    self.model.compile(
                        optimizer='adam',
                        loss='mse',
                        metrics=['mae', 'mape']
                    )
                    self.is_trained = True
                    self.logger.info("LSTM model loaded successfully (recompiled)")
                except Exception as e2:
                    self.logger.error(f"Failed to load model with fallback: {e2}")
                    # Model exists but can't load - rebuild and retrain will be needed
        
        self.logger.info(f"LSTM Predictor initialized (enabled: {self.is_enabled}, trained: {self.is_trained})")
    
    def build_model(self) -> keras.Model:
        """Build optimized LSTM architecture for trading"""
        if not self.is_enabled:
            return None
            
        model = keras.Sequential([
            # First LSTM layer with return sequences
            keras.layers.LSTM(
                200, 
                return_sequences=True,
                dropout=0.2,
                recurrent_dropout=0.2,
                input_shape=(self.sequence_length, self.features)
            ),
            
            # Second LSTM layer
            keras.layers.LSTM(
                100,
                dropout=0.25
            ),
            
            # Dense layers
            keras.layers.Dense(50, activation='relu'),
            keras.layers.Dropout(0.3),
            
            # Output layer for direction prediction (-1 to 1)
            keras.layers.Dense(1, activation='tanh')
        ])
        
        # Compile with appropriate optimizer and loss
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        return model
    
    def engineer_features(self, market_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Convert market data to ML features
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Feature array or None if insufficient data
        """
        try:
            # Extract basic price data
            price = market_data.get('price', market_data.get('close', 0))
            volume = market_data.get('volume', 1)
            high = market_data.get('high', price)
            low = market_data.get('low', price)
            open_price = market_data.get('open', price)
            
            # Calculate basic features
            features = []
            
            # Price-based features
            if len(self.data_buffer) > 0:
                prev_price = self.data_buffer[-1][0] if self.data_buffer else price
                price_change = (price - prev_price) / prev_price if prev_price > 0 else 0
                features.append(price_change)
            else:
                features.append(0.0)
            
            # Normalized price position within high-low range
            if high != low:
                price_position = (price - low) / (high - low)
            else:
                price_position = 0.5
            features.append(price_position)
            
            # Volume features
            if len(self.data_buffer) >= 5:
                recent_volumes = [data[2] for data in list(self.data_buffer)[-5:]]
                avg_volume = np.mean(recent_volumes)
                volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            else:
                volume_ratio = 1.0
            features.append(volume_ratio)
            
            # Volatility proxy (high-low range)
            volatility = (high - low) / price if price > 0 else 0
            features.append(volatility)
            
            # Gap feature (open vs previous close)
            if len(self.data_buffer) > 0:
                prev_close = self.data_buffer[-1][0]
                gap = (open_price - prev_close) / prev_close if prev_close > 0 else 0
            else:
                gap = 0.0
            features.append(gap)
            
            # Time-based features (simplified)
            current_hour = datetime.now().hour
            features.append(current_hour / 24.0)  # Normalized hour
            
            # Market session feature (basic)
            if 9 <= current_hour <= 16:
                session = 1.0  # Regular session
            elif 17 <= current_hour <= 20:
                session = 0.5  # Extended session
            else:
                session = 0.0  # Overnight
            features.append(session)
            
            # Price momentum (simplified)
            if len(self.data_buffer) >= 3:
                recent_prices = [data[0] for data in list(self.data_buffer)[-3:]]
                if len(recent_prices) >= 2:
                    momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] if recent_prices[0] > 0 else 0
                else:
                    momentum = 0.0
            else:
                momentum = 0.0
            features.append(momentum)
            
            # Ensure we have exactly the expected number of features
            while len(features) < self.features:
                features.append(0.0)
            
            features = features[:self.features]  # Truncate if too many
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Feature engineering error: {e}")
            return None
    
    def update_data_buffer(self, market_data: Dict[str, Any]):
        """Update the data buffer with new market data"""
        features = self.engineer_features(market_data)
        if features is not None:
            # Store [price, timestamp, volume, features...]
            price = market_data.get('price', market_data.get('close', 0))
            volume = market_data.get('volume', 1)
            timestamp = market_data.get('timestamp', datetime.now().timestamp())
            
            data_point = [price, timestamp, volume] + features.tolist()
            self.data_buffer.append(data_point)
    
    def create_sequence(self) -> Optional[np.ndarray]:
        """Create a sequence for LSTM prediction from buffer"""
        if len(self.data_buffer) < self.sequence_length:
            return None
        
        # Extract feature sequences (skip price, timestamp, volume - use features only)
        sequence_data = []
        for data_point in list(self.data_buffer)[-self.sequence_length:]:
            features = data_point[3:]  # Skip price, timestamp, volume
            sequence_data.append(features)
        
        return np.array(sequence_data, dtype=np.float32).reshape(1, self.sequence_length, self.features)
    
    async def predict_direction(self, market_data: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """
        Predict price direction with confidence score
        
        Args:
            market_data: Current market data
            use_cache: Whether to use ML inference cache
            
        Returns:
            Dictionary with prediction results
        """
        # Use ML inference cache if available and enabled
        if use_cache:
            try:
                # Import cache here to avoid circular imports
                import sys
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                from minhos.services.ml_inference_cache import get_ml_inference_cache
                
                cache = get_ml_inference_cache()
                
                # Prepare cache input
                cache_input = {
                    'market_data': market_data,
                    'sequence_length': self.sequence_length,
                    'features': self.features,
                    'is_trained': self.is_trained,
                    'is_enabled': self.is_enabled
                }
                
                # Try to get cached result
                return await cache.get_prediction(
                    'lstm', 
                    cache_input, 
                    self._predict_without_cache
                )
                
            except Exception as e:
                self.logger.warning(f"Cache error, falling back to direct prediction: {e}")
        
        # Fall back to direct prediction
        return await self._predict_without_cache(market_data)
    
    async def _predict_without_cache(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal prediction method without caching"""
        # Extract market data from input (for cache compatibility)
        if 'market_data' in input_data:
            market_data = input_data['market_data']
        else:
            market_data = input_data
        
        # Update data buffer
        self.update_data_buffer(market_data)
        
        # Check if enabled and trained
        if not self.is_enabled:
            return {
                'direction': 0,
                'confidence': 0.0,
                'raw_prediction': 0.0,
                'source': 'lstm_disabled',
                'message': 'TensorFlow not available'
            }
        
        if not self.is_trained:
            return {
                'direction': 0,
                'confidence': 0.0,
                'raw_prediction': 0.0,
                'source': 'lstm_untrained',
                'message': 'Model not trained yet'
            }
        
        # Create sequence for prediction
        sequence = self.create_sequence()
        if sequence is None:
            return {
                'direction': 0,
                'confidence': 0.0,
                'raw_prediction': 0.0,
                'source': 'lstm_insufficient_data',
                'message': f'Need {self.sequence_length} data points, have {len(self.data_buffer)}'
            }
        
        try:
            # Run prediction
            prediction = self.model.predict(sequence, verbose=0)[0][0]
            
            # Calculate confidence and direction
            confidence = min(abs(prediction), 1.0)
            
            # Direction based on prediction strength
            if prediction > 0.05:
                direction = 1  # UP
            elif prediction < -0.05:
                direction = -1  # DOWN
            else:
                direction = 0  # NEUTRAL
            
            # Only provide signal if confidence is above threshold
            if confidence < self.config['confidence_threshold']:
                direction = 0
            
            # Track predictions
            self.predictions_made += 1
            
            return {
                'direction': direction,
                'confidence': confidence,
                'raw_prediction': float(prediction),
                'source': 'lstm_neural_network',
                'predictions_made': self.predictions_made,
                'message': 'LSTM prediction successful'
            }
            
        except Exception as e:
            self.logger.error(f"LSTM prediction error: {e}")
            return {
                'direction': 0,
                'confidence': 0.0,
                'raw_prediction': 0.0,
                'source': 'lstm_error',
                'message': f'Prediction error: {str(e)}'
            }
    
    async def train_on_historical_data(self, historical_data: List[Dict[str, Any]], epochs: int = 50) -> Dict[str, Any]:
        """
        Train LSTM model on historical data
        
        Args:
            historical_data: List of historical market data points
            epochs: Number of training epochs
            
        Returns:
            Training results
        """
        if not self.is_enabled:
            return {
                'success': False,
                'message': 'TensorFlow not available'
            }
        
        if len(historical_data) < self.config['min_data_points']:
            return {
                'success': False,
                'message': f'Insufficient data. Need {self.config["min_data_points"]}, got {len(historical_data)}'
            }
        
        try:
            self.logger.info(f"Training LSTM on {len(historical_data)} historical data points")
            
            # Prepare training data
            X, y = self._prepare_training_data(historical_data)
            
            if len(X) == 0:
                return {
                    'success': False,
                    'message': 'No valid training sequences created'
                }
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Build model
            self.model = self.build_model()
            
            # Training callbacks
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-6
                )
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=32,
                verbose=1,
                callbacks=callbacks
            )
            
            # Save model
            self.model.save(f"{self.model_path}.h5")
            self.is_trained = True
            
            # Calculate final metrics
            final_loss = history.history['loss'][-1]
            final_val_loss = history.history['val_loss'][-1]
            
            self.logger.info(f"LSTM training completed. Final loss: {final_loss:.4f}, Val loss: {final_val_loss:.4f}")
            
            return {
                'success': True,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'final_loss': final_loss,
                'final_val_loss': final_val_loss,
                'epochs_completed': len(history.history['loss']),
                'message': 'LSTM training completed successfully'
            }
            
        except Exception as e:
            self.logger.error(f"LSTM training error: {e}")
            return {
                'success': False,
                'message': f'Training error: {str(e)}'
            }
    
    def _prepare_training_data(self, historical_data: List[Dict[str, Any]]) -> tuple:
        """Prepare training sequences and targets from historical data"""
        sequences = []
        targets = []
        
        # Create feature buffer
        feature_buffer = []
        
        for i, data_point in enumerate(historical_data):
            features = self.engineer_features(data_point)
            if features is not None:
                feature_buffer.append(features)
                
                # Create sequence and target when we have enough data
                if len(feature_buffer) >= self.sequence_length + 1:
                    # Sequence is the last sequence_length features
                    sequence = feature_buffer[-self.sequence_length-1:-1]
                    
                    # Target is the price direction for next step
                    if i < len(historical_data) - 1:
                        current_price = data_point.get('price', data_point.get('close', 0))
                        next_price = historical_data[i + 1].get('price', historical_data[i + 1].get('close', 0))
                        
                        if current_price > 0:
                            price_change = (next_price - current_price) / current_price
                            # Normalize price change to [-1, 1] range
                            target = np.tanh(price_change * 100)  # Scale factor for sensitivity
                        else:
                            target = 0.0
                        
                        sequences.append(sequence)
                        targets.append(target)
        
        if len(sequences) == 0:
            return np.array([]), np.array([])
        
        X = np.array(sequences, dtype=np.float32)
        y = np.array(targets, dtype=np.float32)
        
        return X, y
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'is_enabled': self.is_enabled,
            'is_trained': self.is_trained,
            'predictions_made': self.predictions_made,
            'data_buffer_size': len(self.data_buffer),
            'required_sequence_length': self.sequence_length,
            'confidence_threshold': self.config['confidence_threshold'],
            'has_tensorflow': HAS_TENSORFLOW
        }
    
    def set_config(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated LSTM config: {key} = {value}")