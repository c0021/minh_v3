"""
Ensemble Manager

Self-contained ensemble system for multi-model trading signal fusion.
Combines XGBoost, LightGBM, Random Forest, and CatBoost for robust predictions.
"""

import numpy as np
import pandas as pd
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import pickle
import warnings

# ML model imports with fallback
try:
    import xgboost as xgb
    import lightgbm as lgb
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.isotonic import IsotonicRegression
    import catboost as cb
    HAS_ENSEMBLE_LIBS = True
except ImportError as e:
    HAS_ENSEMBLE_LIBS = False
    logging.warning(f"Ensemble libraries not available: {e}")

# Suppress warnings from ML libraries
warnings.filterwarnings('ignore', category=UserWarning)

class EnsembleManager:
    """
    Self-contained ensemble learning system for trading signal generation.
    
    Features:
    - Multiple base models (XGBoost, LightGBM, Random Forest, CatBoost)
    - Meta-learning with stacking
    - Dynamic model weighting
    - Agreement scoring and confidence calibration
    - Real-time inference optimization
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "/home/colindo/Sync/minh_v4/ml_models/ensemble"
        self.logger = logging.getLogger(__name__)
        
        # Ensemble configuration
        self.config = {
            'base_models': ['xgboost', 'lightgbm', 'random_forest', 'catboost'],
            'meta_learner': 'linear',
            'stacking_enabled': True,
            'agreement_threshold': 0.7,
            'confidence_threshold': 0.6,
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1
        }
        
        # Model components
        self.base_models = {}
        self.meta_learner = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.is_enabled = HAS_ENSEMBLE_LIBS
        
        # Model weights and performance tracking
        self.model_weights = {}
        self.model_performance = {}
        self.prediction_history = []
        
        # Feature engineering
        self.feature_names = []
        self.feature_importance = {}
        
        # Initialize models
        self._initialize_models()
        
        # Try to load existing trained models
        self._load_trained_models()
        
        # Performance tracking
        self.predictions_made = 0
        self.accuracy_window = []
        
        self.logger.info(f"Ensemble Manager initialized (enabled: {self.is_enabled})")
    
    def _initialize_models(self):
        """Initialize base models and meta-learner"""
        if not self.is_enabled:
            self.logger.warning("Ensemble models disabled - required libraries not available")
            return
        
        try:
            # XGBoost
            self.base_models['xgboost'] = xgb.XGBRegressor(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                learning_rate=self.config['learning_rate'],
                random_state=42,
                verbosity=0
            )
            
            # LightGBM
            self.base_models['lightgbm'] = lgb.LGBMRegressor(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                learning_rate=self.config['learning_rate'],
                random_state=42,
                verbosity=-1
            )
            
            # Random Forest
            self.base_models['random_forest'] = RandomForestRegressor(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                random_state=42,
                n_jobs=-1
            )
            
            # CatBoost
            self.base_models['catboost'] = cb.CatBoostRegressor(
                iterations=self.config['n_estimators'],
                depth=self.config['max_depth'],
                learning_rate=self.config['learning_rate'],
                random_state=42,
                verbose=False
            )
            
            # Meta-learner for stacking
            if self.config['meta_learner'] == 'linear':
                self.meta_learner = LinearRegression()
            elif self.config['meta_learner'] == 'isotonic':
                self.meta_learner = IsotonicRegression()
            
            self.logger.info(f"Initialized {len(self.base_models)} base models")
            
        except Exception as e:
            self.logger.error(f"Model initialization error: {e}")
            self.is_enabled = False
    
    def _load_trained_models(self):
        """Load trained models from disk if they exist"""
        if not self.is_enabled:
            return
            
        model_dir = Path(self.model_path)
        if not model_dir.exists():
            self.logger.info("No trained models found - models will need to be trained")
            return
        
        try:
            # Load metadata to check model compatibility
            metadata_file = model_dir / "ensemble_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                self.logger.info(f"Found ensemble metadata from {metadata.get('timestamp', 'unknown')}")
            
            # Load trained base models
            models_loaded = 0
            for model_name in self.config['base_models']:
                model_file = model_dir / f"{model_name}_model.pkl"
                if model_file.exists():
                    try:
                        with open(model_file, 'rb') as f:
                            trained_model = pickle.load(f)
                        self.base_models[model_name] = trained_model
                        models_loaded += 1
                        self.logger.debug(f"Loaded trained {model_name} model")
                    except Exception as e:
                        self.logger.warning(f"Failed to load {model_name} model: {e}")
            
            # Load meta-learner
            meta_file = model_dir / "meta_learner.pkl"
            if meta_file.exists():
                try:
                    with open(meta_file, 'rb') as f:
                        self.meta_learner = pickle.load(f)
                    self.logger.debug("Loaded trained meta-learner")
                except Exception as e:
                    self.logger.warning(f"Failed to load meta-learner: {e}")
            
            # Load scaler
            scaler_file = model_dir / "scaler.pkl"
            if scaler_file.exists():
                try:
                    with open(scaler_file, 'rb') as f:
                        self.scaler = pickle.load(f)
                    self.logger.debug("Loaded trained scaler")
                except Exception as e:
                    self.logger.warning(f"Failed to load scaler: {e}")
            
            # Update training status
            if models_loaded > 0:
                self.is_trained = True
                self.logger.info(f"Successfully loaded {models_loaded}/{len(self.config['base_models'])} trained models")
            else:
                self.logger.info("No trained models loaded - training will be required")
                
        except Exception as e:
            self.logger.error(f"Error loading trained models: {e}")
    
    def engineer_features(self, market_data: List[Dict[str, Any]]) -> Optional[pd.DataFrame]:
        """
        Engineer features for ensemble models from market data
        
        Args:
            market_data: List of market data points
            
        Returns:
            DataFrame with engineered features or None if insufficient data
        """
        if not market_data or len(market_data) < 10:
            return None
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(market_data)
            
            # Ensure required columns
            required_cols = ['price', 'volume', 'timestamp']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'price' and 'close' in df.columns:
                        df['price'] = df['close']
                    elif col == 'volume':
                        df['volume'] = 1.0
                    elif col == 'timestamp':
                        df['timestamp'] = pd.to_datetime('now').timestamp()
            
            # Convert timestamp column to numeric if it's string format
            if 'timestamp' in df.columns:
                if df['timestamp'].dtype == 'object':
                    try:
                        # Handle ISO format timestamps properly
                        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).astype('int64') // 10**9
                    except Exception as e:
                        self.logger.warning(f"Timestamp conversion warning: {e}, using current time")
                        df['timestamp'] = pd.Timestamp.now().timestamp()
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Create feature DataFrame
            features = pd.DataFrame()
            
            # Price-based features
            features['price_change_1'] = df['price'].pct_change().fillna(0)
            features['price_change_5'] = df['price'].pct_change(periods=5).fillna(0)
            features['price_volatility'] = df['price'].rolling(window=10, min_periods=1).std().fillna(0)
            features['price_ma_ratio'] = df['price'] / df['price'].rolling(window=10, min_periods=1).mean()
            features['price_ma_ratio'] = features['price_ma_ratio'].fillna(1.0)
            
            # Technical indicators
            features['rsi'] = self._calculate_rsi(df['price'])
            features['macd'] = self._calculate_macd(df['price'])
            features['bollinger_position'] = self._calculate_bollinger_position(df['price'])
            
            # Volume features
            features['volume_ma'] = df['volume'].rolling(window=10, min_periods=1).mean()
            features['volume_ratio'] = df['volume'] / features['volume_ma']
            features['volume_ratio'] = features['volume_ratio'].fillna(1.0)
            features['volume_change'] = df['volume'].pct_change().fillna(0)
            
            # Momentum features
            features['momentum_5'] = (df['price'] - df['price'].shift(5)) / df['price'].shift(5)
            features['momentum_10'] = (df['price'] - df['price'].shift(10)) / df['price'].shift(10)
            features['momentum_5'] = features['momentum_5'].fillna(0)
            features['momentum_10'] = features['momentum_10'].fillna(0)
            
            # Time-based features
            timestamps = pd.to_datetime(df['timestamp'], unit='s')
            features['hour'] = timestamps.dt.hour / 24.0
            features['day_of_week'] = timestamps.dt.dayofweek / 6.0
            features['is_market_hours'] = ((timestamps.dt.hour >= 9) & (timestamps.dt.hour <= 16)).astype(float)
            
            # High-low features (if available)
            if 'high' in df.columns and 'low' in df.columns:
                features['hl_ratio'] = (df['high'] - df['low']) / df['price']
                features['close_position'] = (df['price'] - df['low']) / (df['high'] - df['low'])
                features['hl_ratio'] = features['hl_ratio'].fillna(0)
                features['close_position'] = features['close_position'].fillna(0.5)
            else:
                features['hl_ratio'] = 0.0
                features['close_position'] = 0.5
            
            # Lag features
            for lag in [1, 2, 3]:
                features[f'price_lag_{lag}'] = df['price'].shift(lag) / df['price']
                features[f'price_lag_{lag}'] = features[f'price_lag_{lag}'].fillna(1.0)
            
            # Fill any remaining NaN values
            features = features.fillna(0)
            
            # Store feature names
            self.feature_names = list(features.columns)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature engineering error: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
            rs = gain / loss.replace(0, 1)  # Avoid division by zero
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50) / 100.0  # Normalize to 0-1
        except:
            return pd.Series([0.5] * len(prices), index=prices.index)
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            return (macd / prices).fillna(0)  # Normalize by price
        except:
            return pd.Series([0.0] * len(prices), index=prices.index)
    
    def _calculate_bollinger_position(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """Calculate position within Bollinger Bands"""
        try:
            ma = prices.rolling(window=period, min_periods=1).mean()
            std = prices.rolling(window=period, min_periods=1).std()
            upper = ma + (std * 2)
            lower = ma - (std * 2)
            position = (prices - lower) / (upper - lower)
            return position.fillna(0.5).clip(0, 1)
        except:
            return pd.Series([0.5] * len(prices), index=prices.index)
    
    async def train_ensemble(self, 
                            training_data: List[Dict[str, Any]], 
                            validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train ensemble models on historical data
        
        Args:
            training_data: Historical market data
            validation_split: Fraction of data for validation
            
        Returns:
            Training results and metrics
        """
        if not self.is_enabled:
            return {
                'success': False,
                'message': 'Ensemble libraries not available'
            }
        
        if len(training_data) < 50:
            return {
                'success': False,
                'message': f'Insufficient data. Need at least 50 points, got {len(training_data)}'
            }
        
        try:
            self.logger.info(f"Training ensemble on {len(training_data)} data points")
            
            # Engineer features
            features_df = self.engineer_features(training_data)
            if features_df is None or len(features_df) == 0:
                return {
                    'success': False,
                    'message': 'Feature engineering failed'
                }
            
            # Prepare targets (next period price change)
            targets = []
            for i in range(len(training_data) - 1):
                current_price = training_data[i].get('price', training_data[i].get('close', 0))
                next_price = training_data[i + 1].get('price', training_data[i + 1].get('close', 0))
                
                if current_price > 0:
                    price_change = (next_price - current_price) / current_price
                    # Normalize using tanh for better training
                    target = np.tanh(price_change * 100)
                else:
                    target = 0.0
                
                targets.append(target)
            
            # Align features and targets
            X = features_df.iloc[:-1].values  # Remove last row to match targets
            y = np.array(targets)
            
            if len(X) != len(y):
                return {
                    'success': False,
                    'message': f'Feature-target mismatch: {len(X)} features, {len(y)} targets'
                }
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=validation_split, shuffle=False
            )
            
            self.logger.info(f"Training: {len(X_train)} samples, Validation: {len(X_val)} samples")
            
            # Train base models
            base_predictions_train = {}
            base_predictions_val = {}
            
            for name, model in self.base_models.items():
                self.logger.info(f"Training {name}...")
                
                # Train model
                model.fit(X_train, y_train)
                
                # Get predictions
                train_pred = model.predict(X_train)
                val_pred = model.predict(X_val)
                
                base_predictions_train[name] = train_pred
                base_predictions_val[name] = val_pred
                
                # Calculate individual model performance
                val_accuracy = self._calculate_direction_accuracy(val_pred, y_val)
                self.model_performance[name] = {
                    'direction_accuracy': val_accuracy,
                    'mse': np.mean((val_pred - y_val) ** 2),
                    'mae': np.mean(np.abs(val_pred - y_val))
                }
                
                self.logger.info(f"{name} validation accuracy: {val_accuracy:.1%}")
            
            # Train meta-learner for stacking
            if self.config['stacking_enabled'] and self.meta_learner is not None:
                self.logger.info("Training meta-learner...")
                
                # Create meta-features
                meta_features_train = np.column_stack(list(base_predictions_train.values()))
                meta_features_val = np.column_stack(list(base_predictions_val.values()))
                
                # Train meta-learner
                self.meta_learner.fit(meta_features_train, y_train)
                
                # Get meta-predictions
                meta_pred_val = self.meta_learner.predict(meta_features_val)
                meta_accuracy = self._calculate_direction_accuracy(meta_pred_val, y_val)
                
                self.logger.info(f"Meta-learner validation accuracy: {meta_accuracy:.1%}")
                
                # Store meta-learner performance
                self.model_performance['meta_learner'] = {
                    'direction_accuracy': meta_accuracy,
                    'mse': np.mean((meta_pred_val - y_val) ** 2),
                    'mae': np.mean(np.abs(meta_pred_val - y_val))
                }
            
            # Calculate model weights based on performance
            self._calculate_model_weights()
            
            # Calculate feature importance
            self._calculate_feature_importance()
            
            # Mark as trained
            self.is_trained = True
            
            # Save models
            await self._save_models()
            
            self.logger.info("Ensemble training completed successfully!")
            
            return {
                'success': True,
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'features': len(self.feature_names),
                'base_models': len(self.base_models),
                'model_performance': self.model_performance,
                'model_weights': self.model_weights,
                'feature_names': self.feature_names
            }
            
        except Exception as e:
            self.logger.error(f"Ensemble training error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Training error: {str(e)}'
            }
    
    def _calculate_direction_accuracy(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate directional accuracy (most important for trading)"""
        pred_directions = np.sign(predictions)
        true_directions = np.sign(targets)
        return np.mean(pred_directions == true_directions)
    
    def _calculate_model_weights(self):
        """Calculate model weights based on performance"""
        if not self.model_performance:
            return
        
        # Weight based on direction accuracy
        total_accuracy = sum(perf['direction_accuracy'] for perf in self.model_performance.values())
        
        if total_accuracy > 0:
            for model_name, performance in self.model_performance.items():
                self.model_weights[model_name] = performance['direction_accuracy'] / total_accuracy
        else:
            # Equal weights if no performance data
            num_models = len(self.model_performance)
            for model_name in self.model_performance.keys():
                self.model_weights[model_name] = 1.0 / num_models
        
        self.logger.info(f"Model weights: {self.model_weights}")
    
    def _calculate_feature_importance(self):
        """Calculate feature importance from base models"""
        if not self.feature_names:
            return
        
        # Initialize importance dict
        self.feature_importance = {name: 0.0 for name in self.feature_names}
        
        # Aggregate importance from models that support it
        total_weight = 0.0
        
        for model_name, model in self.base_models.items():
            if hasattr(model, 'feature_importances_'):
                weight = self.model_weights.get(model_name, 1.0)
                importances = model.feature_importances_
                
                for i, feature_name in enumerate(self.feature_names):
                    if i < len(importances):
                        self.feature_importance[feature_name] += importances[i] * weight
                
                total_weight += weight
        
        # Normalize
        if total_weight > 0:
            for feature_name in self.feature_importance:
                self.feature_importance[feature_name] /= total_weight
    
    async def predict_ensemble(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate ensemble prediction from market data
        
        Args:
            market_data: Recent market data for prediction
            
        Returns:
            Ensemble prediction with confidence and component details
        """
        if not self.is_enabled:
            return {
                'direction': 0,
                'confidence': 0.0,
                'ensemble_prediction': 0.0,
                'model_agreement': 0.0,
                'base_predictions': {},
                'source': 'ensemble_disabled',
                'message': 'Ensemble libraries not available'
            }
        
        if not self.is_trained:
            return {
                'direction': 0,
                'confidence': 0.0,
                'ensemble_prediction': 0.0,
                'model_agreement': 0.0,
                'base_predictions': {},
                'source': 'ensemble_untrained',
                'message': 'Ensemble not trained yet'
            }
        
        try:
            # Engineer features
            features_df = self.engineer_features(market_data)
            if features_df is None or len(features_df) == 0:
                return {
                    'direction': 0,
                    'confidence': 0.0,
                    'ensemble_prediction': 0.0,
                    'model_agreement': 0.0,
                    'base_predictions': {},
                    'source': 'ensemble_insufficient_data',
                    'message': 'Insufficient data for feature engineering'
                }
            
            # Use latest features
            latest_features = features_df.iloc[-1].values.reshape(1, -1)
            features_scaled = self.scaler.transform(latest_features)
            
            # Get predictions from base models
            base_predictions = {}
            for name, model in self.base_models.items():
                pred = model.predict(features_scaled)[0]
                base_predictions[name] = float(pred)
            
            # Calculate ensemble prediction
            if self.config['stacking_enabled'] and self.meta_learner is not None:
                # Use meta-learner
                meta_features = np.array(list(base_predictions.values())).reshape(1, -1)
                ensemble_pred = self.meta_learner.predict(meta_features)[0]
                ensemble_method = 'stacking'
            else:
                # Weighted average
                ensemble_pred = sum(
                    pred * self.model_weights.get(name, 1.0 / len(base_predictions))
                    for name, pred in base_predictions.items()
                )
                ensemble_method = 'weighted_average'
            
            # Calculate model agreement
            agreement = self._calculate_model_agreement(list(base_predictions.values()))
            
            # Calculate confidence
            confidence = min(abs(ensemble_pred) * agreement, 1.0)
            
            # Determine direction
            if ensemble_pred > 0.05:
                direction = 1  # UP
            elif ensemble_pred < -0.05:
                direction = -1  # DOWN
            else:
                direction = 0  # NEUTRAL
            
            # Apply confidence threshold
            if confidence < self.config['confidence_threshold']:
                direction = 0
            
            # Track predictions
            self.predictions_made += 1
            
            result = {
                'direction': direction,
                'confidence': float(confidence),
                'ensemble_prediction': float(ensemble_pred),
                'model_agreement': float(agreement),
                'base_predictions': base_predictions,
                'ensemble_method': ensemble_method,
                'predictions_made': self.predictions_made,
                'source': 'ensemble_ml_models',
                'message': 'Ensemble prediction successful'
            }
            
            # Store prediction history
            self.prediction_history.append({
                'timestamp': datetime.now().isoformat(),
                'prediction': result
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ensemble prediction error: {e}")
            return {
                'direction': 0,
                'confidence': 0.0,
                'ensemble_prediction': 0.0,
                'model_agreement': 0.0,
                'base_predictions': {},
                'source': 'ensemble_error',
                'message': f'Prediction error: {str(e)}'
            }
    
    def _calculate_model_agreement(self, predictions: List[float]) -> float:
        """Calculate agreement between model predictions"""
        if len(predictions) < 2:
            return 0.0
        
        # Calculate pairwise agreement based on direction
        directions = [np.sign(pred) for pred in predictions]
        agreements = []
        
        for i in range(len(directions)):
            for j in range(i + 1, len(directions)):
                if directions[i] == directions[j]:
                    agreements.append(1.0)
                else:
                    agreements.append(0.0)
        
        return np.mean(agreements) if agreements else 0.0
    
    async def _save_models(self):
        """Save trained ensemble models"""
        try:
            model_dir = Path(self.model_path)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Save base models
            for name, model in self.base_models.items():
                model_file = model_dir / f"{name}_model.pkl"
                with open(model_file, 'wb') as f:
                    pickle.dump(model, f)
            
            # Save meta-learner
            if self.meta_learner is not None:
                meta_file = model_dir / "meta_learner.pkl"
                with open(meta_file, 'wb') as f:
                    pickle.dump(self.meta_learner, f)
            
            # Save scaler
            scaler_file = model_dir / "scaler.pkl"
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'config': self.config,
                'feature_names': self.feature_names,
                'model_weights': self.model_weights,
                'model_performance': self.model_performance,
                'feature_importance': self.feature_importance
            }
            
            metadata_file = model_dir / "ensemble_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Ensemble models saved to {model_dir}")
            
        except Exception as e:
            self.logger.error(f"Model saving error: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get ensemble performance statistics"""
        return {
            'is_enabled': self.is_enabled,
            'is_trained': self.is_trained,
            'predictions_made': self.predictions_made,
            'base_models': list(self.base_models.keys()),
            'model_weights': self.model_weights,
            'model_performance': self.model_performance,
            'feature_count': len(self.feature_names),
            'feature_importance': dict(sorted(
                self.feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]) if self.feature_importance else {},
            'config': self.config
        }
    
    def set_config(self, **kwargs):
        """Update ensemble configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated ensemble config: {key} = {value}")