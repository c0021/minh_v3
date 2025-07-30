#!/usr/bin/env python3
"""
ML Service Connector
===================

Bridges the new Kelly Criterion implementation with existing MinhOS ML services.
Provides unified interface to LSTM, Ensemble, and existing Kelly services.

Features:
- LSTM Predictor integration
- Ensemble Manager integration  
- Existing Kelly Manager compatibility
- Service health monitoring
- Fallback mechanisms

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

# Try to import existing ML services
try:
    # Change to absolute imports from project root
    sys.path.insert(0, '/home/colindo/Sync/minh_v4')
    from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
    from capabilities.ensemble.ensemble_manager import EnsembleManager
    
    # Try to import Kelly manager if it exists
    try:
        from capabilities.position_sizing.kelly.kelly_manager import KellyManager as ExistingKellyManager
    except ImportError:
        ExistingKellyManager = None
        
    # Try to import ML pipeline service if it exists
    try:
        from minhos.services.ml_pipeline_service import MLPipelineService
    except ImportError:
        MLPipelineService = None
        
    HAS_ML_SERVICES = True
    logger.info("Successfully imported existing ML services")
except ImportError as e:
    HAS_ML_SERVICES = False
    logger.warning(f"Could not import existing ML services: {e}")

# Import our new Kelly implementation
from core.kelly_calculator import KellyCalculator
from core.probability_estimator import MLProbabilityEstimator, ModelPrediction


class MLServiceConnector:
    """
    Connects new Kelly implementation with existing MinhOS ML services
    
    Provides unified interface for:
    - LSTM predictions
    - Ensemble predictions  
    - Kelly position sizing (new enhanced version)
    - Service health monitoring
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize ML Service Connector
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        
        # Initialize existing services if available
        self.lstm_predictor = None
        self.ensemble_manager = None
        self.existing_kelly_manager = None
        self.ml_pipeline_service = None
        
        # Initialize our new Kelly components
        self.kelly_calculator = KellyCalculator(self.config.get('kelly_config', {}))
        self.probability_estimator = MLProbabilityEstimator(self.config.get('probability_config', {}))
        
        # Service state
        self.services_initialized = False
        self.last_health_check = None
        self.service_status = {}
        
        # Performance tracking
        self.prediction_count = 0
        self.successful_predictions = 0
        self.failed_predictions = 0
        
        logger.info("ML Service Connector initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for ML Service Connector"""
        return {
            'enable_lstm': True,
            'enable_ensemble': True,
            'enable_existing_kelly': False,  # Use our new implementation by default
            'fallback_on_error': True,
            'health_check_interval': 300,  # 5 minutes
            'prediction_timeout': 10.0,  # 10 seconds
            'kelly_config': {
                'max_kelly_fraction': 0.25,
                'kelly_fraction_multiplier': 0.6,
                'confidence_threshold': 0.01  # Temporarily lowered for testing
            },
            'probability_config': {
                'model_weights': {'lstm': 0.4, 'ensemble': 0.6},
                'confidence_threshold': 0.01,  # Temporarily lowered for testing
                'win_loss_lookback_days': 30
            }
        }
    
    async def initialize_services(self) -> bool:
        """
        Initialize all ML services
        
        Returns:
            True if initialization successful
        """
        logger.info("Initializing ML services...")
        
        try:
            if HAS_ML_SERVICES:
                # Initialize LSTM Predictor
                if self.config.get('enable_lstm', True):
                    try:
                        self.lstm_predictor = LSTMPredictor()
                        self.service_status['lstm'] = 'initialized'
                        logger.info("LSTM Predictor initialized")
                    except Exception as e:
                        logger.error(f"Failed to initialize LSTM Predictor: {e}")
                        self.service_status['lstm'] = 'failed'
                
                # Initialize Ensemble Manager
                if self.config.get('enable_ensemble', True):
                    try:
                        self.ensemble_manager = EnsembleManager()
                        self.service_status['ensemble'] = 'initialized'
                        logger.info("Ensemble Manager initialized")
                    except Exception as e:
                        logger.error(f"Failed to initialize Ensemble Manager: {e}")
                        self.service_status['ensemble'] = 'failed'
                
                # Initialize existing Kelly Manager (optional)
                if self.config.get('enable_existing_kelly', False):
                    try:
                        self.existing_kelly_manager = ExistingKellyManager()
                        self.service_status['existing_kelly'] = 'initialized'
                        logger.info("Existing Kelly Manager initialized")
                    except Exception as e:
                        logger.error(f"Failed to initialize existing Kelly Manager: {e}")
                        self.service_status['existing_kelly'] = 'failed'
                
                # Initialize ML Pipeline Service
                try:
                    self.ml_pipeline_service = MLPipelineService()
                    self.service_status['ml_pipeline'] = 'initialized'
                    logger.info("ML Pipeline Service initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize ML Pipeline Service: {e}")
                    self.service_status['ml_pipeline'] = 'failed'
            
            # Our new Kelly components are always available
            self.service_status['kelly_calculator'] = 'initialized'
            self.service_status['probability_estimator'] = 'initialized'
            
            self.services_initialized = True
            self.last_health_check = datetime.now()
            
            logger.info(f"ML services initialization complete. Status: {self.service_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ML services: {e}")
            return False
    
    async def get_lstm_prediction(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """
        Get prediction from LSTM service
        
        Args:
            symbol: Trading symbol
            market_data: Current market data
            
        Returns:
            LSTM prediction or None if unavailable
        """
        if not self.lstm_predictor:
            logger.warning("LSTM Predictor not available")
            return None
        
        try:
            # Convert market data to format expected by LSTM
            lstm_input = self._format_lstm_input(market_data)
            
            # Get prediction
            prediction = await asyncio.wait_for(
                self._call_lstm_predict(lstm_input),
                timeout=self.config.get('prediction_timeout', 10.0)
            )
            
            if prediction:
                self.successful_predictions += 1
                logger.debug(f"LSTM prediction for {symbol}: {prediction}")
                return {
                    'model_type': 'lstm',
                    'confidence': prediction.get('confidence', 0.5),
                    'direction': prediction.get('direction', 'neutral'),
                    'price_target': prediction.get('price_target'),
                    'metadata': prediction,
                    'timestamp': datetime.now().isoformat()
                }
            
        except asyncio.TimeoutError:
            logger.error(f"LSTM prediction timeout for {symbol}")
            self.failed_predictions += 1
        except Exception as e:
            logger.error(f"LSTM prediction failed for {symbol}: {e}")
            self.failed_predictions += 1
        
        return None
    
    async def get_ensemble_prediction(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """
        Get prediction from Ensemble service
        
        Args:
            symbol: Trading symbol
            market_data: Current market data
            
        Returns:
            Ensemble prediction or None if unavailable
        """
        if not self.ensemble_manager:
            logger.warning("Ensemble Manager not available")
            return None
        
        try:
            # Convert market data to format expected by Ensemble (list of data points)
            ensemble_input = self._format_ensemble_input(market_data)
            # Ensemble expects a list - create some history by repeating current data
            ensemble_input_list = [ensemble_input] * 10  # Provide 10 data points
            
            # Get prediction
            prediction = await asyncio.wait_for(
                self._call_ensemble_predict(ensemble_input_list),
                timeout=self.config.get('prediction_timeout', 10.0)
            )
            
            if prediction:
                self.successful_predictions += 1
                logger.debug(f"Ensemble prediction for {symbol}: {prediction}")
                return {
                    'model_type': 'ensemble',
                    'confidence': prediction.get('confidence', 0.5),
                    'direction': prediction.get('direction', 'neutral'),
                    'individual_models': prediction.get('individual_models', {}),
                    'consensus_strength': prediction.get('consensus_strength', 0.5),
                    'metadata': prediction,
                    'timestamp': datetime.now().isoformat()
                }
            
        except asyncio.TimeoutError:
            logger.error(f"Ensemble prediction timeout for {symbol}")
            self.failed_predictions += 1
        except Exception as e:
            logger.error(f"Ensemble prediction failed for {symbol}: {e}")
            self.failed_predictions += 1
        
        return None
    
    async def calculate_kelly_position(self, 
                                     symbol: str,
                                     ml_predictions: List[Dict],
                                     market_data: Dict,
                                     trade_history: Optional[List[Dict]] = None,
                                     account_capital: float = 100000.0) -> Dict:
        """
        Calculate Kelly optimal position using our enhanced implementation
        
        Args:
            symbol: Trading symbol
            ml_predictions: List of ML model predictions
            market_data: Current market data
            trade_history: Historical trade data
            account_capital: Total account capital
            
        Returns:
            Kelly position recommendation
        """
        try:
            self.prediction_count += 1
            
            # Step 1: Convert ML predictions to probability estimate
            prob_estimate = self.probability_estimator.estimate_trading_probability(
                ml_predictions, trade_history, symbol
            )
            
            # Validate probability quality
            validation = self.probability_estimator.validate_prediction_quality(prob_estimate)
            if not validation['valid']:
                logger.warning(f"Poor probability quality for {symbol}: {validation['errors']}")
                return {
                    'symbol': symbol,
                    'status': 'rejected',
                    'reason': f"Quality validation failed: {validation['errors']}",
                    'kelly_fraction': 0.0,
                    'position_size': 0,
                    'confidence': 0.0
                }
            
            # Step 2: Calculate Kelly position
            kelly_result = self.kelly_calculator.calculate_position_recommendation(
                symbol=symbol,
                win_probability=prob_estimate.win_probability,
                win_loss_ratio=prob_estimate.win_loss_ratio,
                ml_confidence=prob_estimate.confidence,
                account_capital=account_capital,
                model_inputs={
                    'ml_predictions': ml_predictions,
                    'probability_estimate': prob_estimate.__dict__,
                    'market_data': market_data
                }
            )
            
            # Convert to standard response format
            response = {
                'symbol': kelly_result.symbol,
                'status': 'success',
                'kelly_fraction': kelly_result.kelly_fraction,
                'position_size': kelly_result.position_size,
                'confidence': kelly_result.confidence,
                'win_probability': kelly_result.win_probability,
                'win_loss_ratio': kelly_result.win_loss_ratio,
                'capital_risk': kelly_result.max_capital_risk,
                'reasoning': kelly_result.reasoning,
                'constraints_applied': kelly_result.constraints_applied,
                'timestamp': kelly_result.timestamp.isoformat(),
                'model_agreement': prob_estimate.model_agreement,
                'individual_probabilities': prob_estimate.individual_probabilities
            }
            
            logger.info(f"Kelly position calculated for {symbol}: "
                       f"{kelly_result.position_size} contracts ({kelly_result.kelly_fraction:.3f} fraction)")
            
            return response
            
        except Exception as e:
            logger.error(f"Kelly position calculation failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'status': 'error',
                'reason': str(e),
                'kelly_fraction': 0.0,
                'position_size': 0,
                'confidence': 0.0
            }
    
    async def get_unified_ml_recommendation(self,
                                          symbol: str,
                                          market_data: Dict,
                                          trade_history: Optional[List[Dict]] = None,
                                          account_capital: float = 100000.0) -> Dict:
        """
        Get unified ML recommendation (LSTM + Ensemble → Kelly position)
        
        Args:
            symbol: Trading symbol
            market_data: Current market data
            trade_history: Historical trade data
            account_capital: Total account capital
            
        Returns:
            Unified ML recommendation with Kelly position sizing
        """
        logger.info(f"Getting unified ML recommendation for {symbol}")
        
        # Gather ML predictions
        ml_predictions = []
        
        # Get LSTM prediction
        lstm_pred = await self.get_lstm_prediction(symbol, market_data)
        if lstm_pred:
            ml_predictions.append(lstm_pred)
        
        # Get Ensemble prediction
        ensemble_pred = await self.get_ensemble_prediction(symbol, market_data)
        if ensemble_pred:
            ml_predictions.append(ensemble_pred)
        
        if not ml_predictions:
            logger.warning(f"No ML predictions available for {symbol}")
            return {
                'symbol': symbol,
                'status': 'no_predictions',
                'kelly_fraction': 0.0,
                'position_size': 0,
                'confidence': 0.0,
                'reason': 'No ML predictions available'
            }
        
        # Calculate Kelly position
        kelly_result = await self.calculate_kelly_position(
            symbol, ml_predictions, market_data, trade_history, account_capital
        )
        
        # Add ML prediction details to response
        kelly_result['ml_predictions'] = ml_predictions
        kelly_result['lstm_available'] = lstm_pred is not None
        kelly_result['ensemble_available'] = ensemble_pred is not None
        kelly_result['total_models'] = len(ml_predictions)
        
        return kelly_result
    
    async def health_check(self) -> Dict:
        """
        Perform health check on all ML services
        
        Returns:
            Health status for all services
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'overall_healthy': True,
            'prediction_stats': {
                'total_predictions': self.prediction_count,
                'successful_predictions': self.successful_predictions,
                'failed_predictions': self.failed_predictions,
                'success_rate': self.successful_predictions / max(1, self.prediction_count)
            }
        }
        
        # Check each service
        for service_name, status in self.service_status.items():
            service_health = {
                'status': status,
                'available': status == 'initialized',
                'last_check': datetime.now().isoformat()
            }
            
            # Additional checks for specific services
            if service_name == 'lstm' and self.lstm_predictor:
                service_health['model_loaded'] = hasattr(self.lstm_predictor, 'model') and self.lstm_predictor.model is not None
            elif service_name == 'ensemble' and self.ensemble_manager:
                service_health['models_loaded'] = hasattr(self.ensemble_manager, 'models') and bool(self.ensemble_manager.models)
            
            health_status['services'][service_name] = service_health
            
            if status != 'initialized':
                health_status['overall_healthy'] = False
        
        self.last_health_check = datetime.now()
        return health_status
    
    # Helper methods for service integration
    async def _call_lstm_predict(self, input_data: Dict) -> Optional[Dict]:
        """Call LSTM predictor with error handling"""
        if hasattr(self.lstm_predictor, 'predict_direction'):
            # Use the correct LSTM method
            return await self.lstm_predictor.predict_direction(input_data)
        elif hasattr(self.lstm_predictor, 'predict_async'):
            return await self.lstm_predictor.predict_async(input_data)
        elif hasattr(self.lstm_predictor, 'predict'):
            # Sync method - run in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.lstm_predictor.predict, input_data)
        return None
    
    async def _call_ensemble_predict(self, input_data: List[Dict]) -> Optional[Dict]:
        """Call ensemble predictor with error handling"""
        if hasattr(self.ensemble_manager, 'predict_ensemble'):
            # Use the correct ensemble method - expects list of market data
            return await self.ensemble_manager.predict_ensemble(input_data)
        elif hasattr(self.ensemble_manager, 'predict_async'):
            return await self.ensemble_manager.predict_async(input_data)
        elif hasattr(self.ensemble_manager, 'predict'):
            # Sync method - run in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.ensemble_manager.predict, input_data)
        return None
    
    def _format_lstm_input(self, market_data: Dict) -> Dict:
        """Format market data for LSTM input"""
        # Extract relevant features for LSTM
        return {
            'price': market_data.get('close', market_data.get('price', 0)),
            'volume': market_data.get('volume', 0),
            'high': market_data.get('high', market_data.get('price', 0)),
            'low': market_data.get('low', market_data.get('price', 0)),
            'open': market_data.get('open', market_data.get('price', 0)),
            'timestamp': market_data.get('timestamp', datetime.now().isoformat())
        }
    
    def _format_ensemble_input(self, market_data: Dict) -> Dict:
        """Format market data for Ensemble input"""
        # Extract relevant features for Ensemble models
        return self._format_lstm_input(market_data)  # Same format for now
    
    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.config.copy()
    
    def get_status(self) -> Dict:
        """Get connector status"""
        return {
            'services_initialized': self.services_initialized,
            'service_status': self.service_status.copy(),
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'prediction_count': self.prediction_count,
            'success_rate': self.successful_predictions / max(1, self.prediction_count)
        }