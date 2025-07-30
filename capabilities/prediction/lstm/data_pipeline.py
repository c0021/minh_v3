"""
LSTM Data Pipeline

Feature engineering and data preparation for LSTM neural network.
Self-contained module for converting market data to ML features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

class LSTMDataPipeline:
    """
    Data pipeline for LSTM neural network training and inference.
    
    Handles:
    - Feature engineering from market data
    - Data normalization and scaling
    - Sequence creation for LSTM input
    - Historical data processing
    """
    
    def __init__(self, sequence_length: int = 20, features: int = 8):
        self.sequence_length = sequence_length
        self.features = features
        self.logger = logging.getLogger(__name__)
        
        # Feature names for tracking
        self.feature_names = [
            'price_change',
            'price_position',
            'volume_ratio',
            'volatility',
            'gap',
            'time_of_day',
            'market_session',
            'momentum'
        ]
    
    def create_features_from_market_data(self, market_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create comprehensive feature set from market data
        
        Args:
            market_data: List of market data dictionaries
            
        Returns:
            DataFrame with engineered features
        """
        if not market_data:
            return pd.DataFrame()
        
        try:
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(market_data)
            
            # Ensure required columns exist
            required_columns = ['price', 'volume', 'timestamp']
            for col in required_columns:
                if col not in df.columns:
                    # Try alternative column names
                    if col == 'price' and 'close' in df.columns:
                        df['price'] = df['close']
                    elif col == 'volume' and 'volume' not in df.columns:
                        df['volume'] = 1.0  # Default volume
                    elif col == 'timestamp' and 'timestamp' not in df.columns:
                        df['timestamp'] = pd.to_datetime('now').timestamp()
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Create features
            features_df = pd.DataFrame()
            
            # 1. Price change (returns)
            features_df['price_change'] = df['price'].pct_change().fillna(0)
            
            # 2. Price position within high-low range
            if 'high' in df.columns and 'low' in df.columns:
                price_range = df['high'] - df['low']
                price_range = price_range.replace(0, 1)  # Avoid division by zero
                features_df['price_position'] = (df['price'] - df['low']) / price_range
            else:
                features_df['price_position'] = 0.5  # Default to middle
            
            # 3. Volume ratio (current vs moving average)
            volume_ma = df['volume'].rolling(window=5, min_periods=1).mean()
            features_df['volume_ratio'] = df['volume'] / volume_ma.replace(0, 1)
            
            # 4. Volatility (high-low range as percentage of price)
            if 'high' in df.columns and 'low' in df.columns:
                features_df['volatility'] = (df['high'] - df['low']) / df['price'].replace(0, 1)
            else:
                features_df['volatility'] = 0.0
            
            # 5. Gap (open vs previous close)
            if 'open' in df.columns:
                prev_close = df['price'].shift(1)
                features_df['gap'] = (df['open'] - prev_close) / prev_close.replace(0, 1)
            else:
                features_df['gap'] = 0.0
            
            # 6. Time of day (normalized 0-1)
            timestamps = pd.to_datetime(df['timestamp'], unit='s')
            features_df['time_of_day'] = timestamps.dt.hour / 24.0
            
            # 7. Market session indicator
            hour = timestamps.dt.hour
            features_df['market_session'] = np.where(
                (hour >= 9) & (hour <= 16), 1.0,  # Regular session
                np.where((hour >= 17) & (hour <= 20), 0.5, 0.0)  # Extended/Overnight
            )
            
            # 8. Price momentum (3-period momentum)
            features_df['momentum'] = (df['price'] - df['price'].shift(3)) / df['price'].shift(3).replace(0, 1)
            
            # Fill NaN values
            features_df = features_df.fillna(0)
            
            # Ensure we have exactly the expected number of features
            if len(features_df.columns) < self.features:
                # Add additional features if needed
                for i in range(len(features_df.columns), self.features):
                    features_df[f'feature_{i}'] = 0.0
            elif len(features_df.columns) > self.features:
                # Keep only the first N features
                features_df = features_df.iloc[:, :self.features]
            
            # Add metadata
            features_df['timestamp'] = df['timestamp']
            features_df['price'] = df['price']
            
            return features_df
            
        except Exception as e:
            self.logger.error(f"Feature creation error: {e}")
            return pd.DataFrame()
    
    def create_lstm_sequences(self, features_df: pd.DataFrame) -> tuple:
        """
        Create LSTM input sequences and targets
        
        Args:
            features_df: DataFrame with features and prices
            
        Returns:
            Tuple of (X_sequences, y_targets)
        """
        if len(features_df) < self.sequence_length + 1:
            return np.array([]), np.array([])
        
        try:
            # Extract feature columns (exclude metadata)
            feature_cols = [col for col in features_df.columns if col not in ['timestamp', 'price']]
            feature_data = features_df[feature_cols].values
            
            # Create sequences and targets
            X_sequences = []
            y_targets = []
            
            for i in range(len(feature_data) - self.sequence_length):
                # Sequence: sequence_length rows of features
                sequence = feature_data[i:i + self.sequence_length]
                
                # Target: price direction for next step
                current_price = features_df.iloc[i + self.sequence_length - 1]['price']
                next_price = features_df.iloc[i + self.sequence_length]['price']
                
                if current_price > 0:
                    price_change = (next_price - current_price) / current_price
                    # Normalize to [-1, 1] range using tanh
                    target = np.tanh(price_change * 100)  # Scale factor for sensitivity
                else:
                    target = 0.0
                
                X_sequences.append(sequence)
                y_targets.append(target)
            
            X = np.array(X_sequences, dtype=np.float32)
            y = np.array(y_targets, dtype=np.float32)
            
            self.logger.info(f"Created {len(X)} LSTM sequences with shape {X.shape}")
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Sequence creation error: {e}")
            return np.array([]), np.array([])
    
    def prepare_training_data(self, historical_data: List[Dict[str, Any]]) -> tuple:
        """
        Complete pipeline: raw data -> features -> sequences
        
        Args:
            historical_data: Raw historical market data
            
        Returns:
            Tuple of (X_train, y_train) ready for LSTM training
        """
        # Create features
        features_df = self.create_features_from_market_data(historical_data)
        
        if features_df.empty:
            return np.array([]), np.array([])
        
        # Create sequences
        X, y = self.create_lstm_sequences(features_df)
        
        return X, y
    
    def validate_data_quality(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Validate data quality for training
        
        Args:
            data: Input data array
            
        Returns:
            Validation results
        """
        if len(data) == 0:
            return {
                'valid': False,
                'reason': 'Empty data'
            }
        
        # Check for NaN or infinite values
        has_nan = np.isnan(data).any()
        has_inf = np.isinf(data).any()
        
        if has_nan or has_inf:
            return {
                'valid': False,
                'reason': f'Invalid values (NaN: {has_nan}, Inf: {has_inf})'
            }
        
        # Check data range (features should be reasonable)
        data_min = np.min(data)
        data_max = np.max(data)
        
        if abs(data_min) > 1000 or abs(data_max) > 1000:
            return {
                'valid': False,
                'reason': f'Data range too large (min: {data_min}, max: {data_max})'
            }
        
        return {
            'valid': True,
            'samples': len(data),
            'shape': data.shape,
            'min_value': data_min,
            'max_value': data_max,
            'mean_value': np.mean(data),
            'std_value': np.std(data)
        }
    
    def get_feature_info(self) -> Dict[str, Any]:
        """Get information about features"""
        return {
            'feature_count': self.features,
            'sequence_length': self.sequence_length,
            'feature_names': self.feature_names[:self.features],
            'description': 'LSTM data pipeline for price direction prediction'
        }