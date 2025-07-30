"""
Probability Estimator for Kelly Criterion

Uses XGBoost classifier to estimate win probability for trades.
Includes isotonic regression calibration for better probability estimates.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import pickle
from pathlib import Path

# ML imports with fallback
try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.isotonic import IsotonicRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import brier_score_loss, log_loss
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logging.warning("XGBoost not available. Probability estimator will use fallback methods.")

class ProbabilityEstimator:
    """
    ML-based probability estimation for Kelly Criterion position sizing.
    
    Features:
    - XGBoost classifier for base probability estimation
    - Isotonic regression for probability calibration
    - Feature importance tracking
    - Historical performance monitoring
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "/home/colindo/Sync/minh_v4/ml_models/kelly"
        self.logger = logging.getLogger(__name__)
        
        # Model components
        self.classifier = None
        self.calibrator = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.is_enabled = HAS_XGBOOST
        
        # Configuration
        self.config = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'min_samples_leaf': 20,
            'calibration_bins': 10,
            'confidence_threshold': 0.55
        }
        
        # Feature tracking
        self.feature_names = []
        self.feature_importance = {}
        
        # Performance tracking
        self.predictions_made = 0
        self.calibration_history = []
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the probability estimator"""
        if not self.is_enabled:
            self.logger.warning("Probability Estimator disabled - XGBoost not available")
            return
        
        # Ensure model directory exists
        Path(self.model_path).mkdir(parents=True, exist_ok=True)
        
        # Try to load existing model
        model_file = Path(self.model_path) / "probability_classifier.pkl"
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    model_data = pickle.load(f)
                    self.classifier = model_data['classifier']
                    self.calibrator = model_data['calibrator']
                    self.scaler = model_data['scaler']
                    self.feature_names = model_data['feature_names']
                    self.is_trained = True
                    self.logger.info("Probability estimator loaded successfully")
            except Exception as e:
                self.logger.warning(f"Could not load existing model: {e}")
        
        self.logger.info(f"Probability Estimator initialized (enabled: {self.is_enabled}, trained: {self.is_trained})")
    
    def engineer_features(self, market_data: List[Dict[str, Any]], 
                         trade_signal: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Engineer features for probability estimation
        
        Args:
            market_data: Recent market data
            trade_signal: Current trading signal
            
        Returns:
            Feature array or None if insufficient data
        """
        if not market_data or len(market_data) < 10:
            return None
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(market_data)
            
            # Ensure required columns
            if 'price' not in df.columns and 'close' in df.columns:
                df['price'] = df['close']
            if 'volume' not in df.columns:
                df['volume'] = 1.0
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            features = []
            
            # Market state features
            current_price = df['price'].iloc[-1]
            price_ma_5 = df['price'].rolling(5, min_periods=1).mean().iloc[-1]
            price_ma_20 = df['price'].rolling(20, min_periods=1).mean().iloc[-1]
            
            # Price position relative to moving averages
            features.append((current_price - price_ma_5) / price_ma_5 if price_ma_5 > 0 else 0)
            features.append((current_price - price_ma_20) / price_ma_20 if price_ma_20 > 0 else 0)
            
            # Volatility features
            returns = df['price'].pct_change().dropna()
            if len(returns) >= 5:
                volatility_5d = returns.rolling(5, min_periods=1).std().iloc[-1]
                volatility_20d = returns.rolling(20, min_periods=1).std().iloc[-1]
                features.append(volatility_5d)
                features.append(volatility_20d if volatility_20d > 0 else volatility_5d)
                features.append(volatility_5d / volatility_20d if volatility_20d > 0 else 1.0)
            else:
                features.extend([0.01, 0.01, 1.0])
            
            # Momentum features
            if len(df) >= 5:
                momentum_5 = (current_price - df['price'].iloc[-5]) / df['price'].iloc[-5]
                features.append(momentum_5)
            else:
                features.append(0.0)
            
            if len(df) >= 10:
                momentum_10 = (current_price - df['price'].iloc[-10]) / df['price'].iloc[-10]
                features.append(momentum_10)
            else:
                features.append(0.0)
            
            # Volume features
            volume_ma = df['volume'].rolling(10, min_periods=1).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            features.append(current_volume / volume_ma if volume_ma > 0 else 1.0)
            
            # Signal strength features
            signal_confidence = trade_signal.get('confidence', 0.5)
            signal_direction = trade_signal.get('direction', 0)
            features.append(signal_confidence)
            features.append(float(signal_direction))
            
            # Technical indicator agreement
            rsi = self._calculate_rsi(df['price'])
            macd = self._calculate_macd(df['price'])
            bb_position = self._calculate_bollinger_position(df['price'])
            
            features.extend([rsi, macd, bb_position])
            
            # Market timing features
            current_hour = datetime.now().hour
            features.append(current_hour / 24.0)
            features.append(1.0 if 9 <= current_hour <= 16 else 0.0)  # Market hours
            
            # Trend consistency
            if len(returns) >= 5:
                trend_consistency = np.mean(np.sign(returns.iloc[-5:]) == np.sign(signal_direction))
                features.append(trend_consistency)
            else:
                features.append(0.5)
            
            # Risk-adjusted signal strength
            if len(returns) >= 10:
                signal_to_noise = abs(signal_confidence) / (volatility_5d + 1e-6)
                features.append(min(signal_to_noise, 10.0))  # Cap at 10
            else:
                features.append(0.0)
            
            # Store feature names if not set
            if not self.feature_names:
                self.feature_names = [
                    'price_ma5_ratio', 'price_ma20_ratio', 'volatility_5d', 'volatility_20d', 
                    'volatility_ratio', 'momentum_5', 'momentum_10', 'volume_ratio',
                    'signal_confidence', 'signal_direction', 'rsi', 'macd', 'bb_position',
                    'hour_normalized', 'is_market_hours', 'trend_consistency', 'signal_to_noise'
                ]
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Feature engineering error: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
            rs = gain.iloc[-1] / (loss.iloc[-1] + 1e-6)
            rsi = 100 - (100 / (1 + rs))
            return rsi / 100.0  # Normalize to 0-1
        except:
            return 0.5
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> float:
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd = (ema_fast - ema_slow).iloc[-1]
            return (macd / prices.iloc[-1]) if prices.iloc[-1] > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_bollinger_position(self, prices: pd.Series, period: int = 20) -> float:
        """Calculate position within Bollinger Bands"""
        try:
            ma = prices.rolling(window=period, min_periods=1).mean()
            std = prices.rolling(window=period, min_periods=1).std()
            upper = ma + (std * 2)
            lower = ma - (std * 2)
            current_price = prices.iloc[-1]
            position = (current_price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
            return max(0.0, min(1.0, position))
        except:
            return 0.5
    
    async def train_probability_estimator(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train probability estimator on historical trades
        
        Args:
            training_data: List of historical trade data with outcomes
            
        Returns:
            Training results and metrics
        """
        if not self.is_enabled:
            return {
                'success': False,
                'message': 'XGBoost not available'
            }
        
        if len(training_data) < 100:
            return {
                'success': False,
                'message': f'Insufficient data. Need at least 100 trades, got {len(training_data)}'
            }
        
        try:
            self.logger.info(f"Training probability estimator on {len(training_data)} trades")
            
            # Prepare features and targets
            features_list = []
            targets = []
            
            for trade in training_data:
                # Extract market data and signal
                market_data = trade.get('market_data', [])
                signal = trade.get('signal', {})
                outcome = trade.get('outcome', 0)  # 1 for win, 0 for loss
                
                if len(market_data) < 10:
                    continue
                
                features = self.engineer_features(market_data, signal)
                if features is not None:
                    features_list.append(features)
                    targets.append(int(outcome > 0))  # Binary classification
            
            if len(features_list) < 50:
                return {
                    'success': False,
                    'message': f'Insufficient valid samples after feature engineering: {len(features_list)}'
                }
            
            X = np.array(features_list)
            y = np.array(targets)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, shuffle=True, random_state=42,
                stratify=y if len(np.unique(y)) > 1 else None
            )
            
            self.logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
            self.logger.info(f"Win rate in training: {np.mean(y_train):.1%}")
            
            # Train XGBoost classifier
            self.classifier = xgb.XGBClassifier(
                n_estimators=self.config['n_estimators'],
                max_depth=self.config['max_depth'],
                learning_rate=self.config['learning_rate'],
                min_child_weight=self.config['min_samples_leaf'],
                random_state=42,
                eval_metric='logloss'
            )
            
            self.classifier.fit(X_train, y_train)
            
            # Get probabilities for calibration
            train_probs = self.classifier.predict_proba(X_train)[:, 1]
            test_probs = self.classifier.predict_proba(X_test)[:, 1]
            
            # Train isotonic calibrator
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(train_probs, y_train)
            
            # Get calibrated probabilities
            train_probs_cal = self.calibrator.predict(train_probs)
            test_probs_cal = self.calibrator.predict(test_probs)
            
            # Calculate metrics
            train_accuracy = np.mean((train_probs_cal > 0.5) == y_train)
            test_accuracy = np.mean((test_probs_cal > 0.5) == y_test)
            
            # Calibration metrics
            train_brier = brier_score_loss(y_train, train_probs_cal)
            test_brier = brier_score_loss(y_test, test_probs_cal)
            
            # Feature importance
            if hasattr(self.classifier, 'feature_importances_'):
                self.feature_importance = dict(zip(
                    self.feature_names,
                    self.classifier.feature_importances_
                ))
            
            # Mark as trained
            self.is_trained = True
            
            # Save model
            await self._save_model()
            
            self.logger.info(f"Training completed. Test accuracy: {test_accuracy:.1%}, Brier score: {test_brier:.4f}")
            
            return {
                'success': True,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'train_accuracy': train_accuracy,
                'test_accuracy': test_accuracy,
                'train_brier_score': train_brier,
                'test_brier_score': test_brier,
                'win_rate': np.mean(y),
                'feature_importance': self.feature_importance
            }
            
        except Exception as e:
            self.logger.error(f"Training error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Training error: {str(e)}'
            }
    
    async def estimate_win_probability(self, market_data: List[Dict[str, Any]], 
                                      trade_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate win probability for a trade signal
        
        Args:
            market_data: Recent market data
            trade_signal: Current trading signal
            
        Returns:
            Probability estimate with confidence metrics
        """
        if not self.is_enabled:
            return {
                'win_probability': 0.5,
                'confidence': 0.0,
                'calibrated': False,
                'source': 'probability_estimator_disabled',
                'message': 'XGBoost not available'
            }
        
        if not self.is_trained:
            # Fallback to signal confidence
            signal_conf = trade_signal.get('confidence', 0.5)
            fallback_prob = 0.5 + (signal_conf - 0.5) * 0.3  # Conservative scaling
            return {
                'win_probability': max(0.1, min(0.9, fallback_prob)),
                'confidence': signal_conf * 0.5,  # Lower confidence for untrained
                'calibrated': False,
                'source': 'probability_estimator_untrained',
                'message': 'Using signal confidence fallback'
            }
        
        try:
            # Engineer features
            features = self.engineer_features(market_data, trade_signal)
            if features is None:
                return {
                    'win_probability': 0.5,
                    'confidence': 0.0,
                    'calibrated': False,
                    'source': 'probability_estimator_insufficient_data',
                    'message': 'Insufficient data for feature engineering'
                }
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Get raw probability
            raw_prob = self.classifier.predict_proba(features_scaled)[0, 1]
            
            # Apply calibration
            calibrated_prob = self.calibrator.predict([raw_prob])[0]
            
            # Calculate confidence based on distance from 0.5
            confidence = abs(calibrated_prob - 0.5) * 2  # Scale to 0-1
            
            # Apply minimum/maximum bounds
            final_prob = max(0.1, min(0.9, calibrated_prob))
            
            # Track predictions
            self.predictions_made += 1
            
            result = {
                'win_probability': float(final_prob),
                'raw_probability': float(raw_prob),
                'confidence': float(confidence),
                'calibrated': True,
                'predictions_made': self.predictions_made,
                'source': 'probability_estimator_ml',
                'message': 'ML probability estimation successful'
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Probability estimation error: {e}")
            # Fallback to signal-based estimate
            signal_conf = trade_signal.get('confidence', 0.5)
            fallback_prob = 0.5 + (signal_conf - 0.5) * 0.3
            return {
                'win_probability': max(0.1, min(0.9, fallback_prob)),
                'confidence': signal_conf * 0.5,
                'calibrated': False,
                'source': 'probability_estimator_error',
                'message': f'Error fallback: {str(e)}'
            }
    
    async def _save_model(self):
        """Save trained probability estimator"""
        try:
            model_dir = Path(self.model_path)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'classifier': self.classifier,
                'calibrator': self.calibrator,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'config': self.config,
                'timestamp': datetime.now().isoformat()
            }
            
            model_file = model_dir / "probability_classifier.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            # Save metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'config': self.config,
                'feature_names': self.feature_names,
                'feature_importance': self.feature_importance,
                'predictions_made': self.predictions_made
            }
            
            metadata_file = model_dir / "probability_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Probability estimator saved to {model_dir}")
            
        except Exception as e:
            self.logger.error(f"Model saving error: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get probability estimator performance statistics"""
        return {
            'is_enabled': self.is_enabled,
            'is_trained': self.is_trained,
            'predictions_made': self.predictions_made,
            'feature_count': len(self.feature_names),
            'feature_importance': dict(sorted(
                self.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]) if self.feature_importance else {},
            'config': self.config
        }