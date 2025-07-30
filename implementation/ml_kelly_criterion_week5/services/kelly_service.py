#!/usr/bin/env python3
"""
Kelly Service
=============

Main Kelly Criterion service for MinhOS integration.
Provides clean API for ML-enhanced Kelly position sizing.

Features:
- Unified ML-Kelly integration
- Clean REST API interface
- Background prediction tasks
- Performance monitoring
- Risk management integration

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict

# Import our ML service connector and Risk Manager integration
try:
    from ml_service_connector import MLServiceConnector
except ImportError:
    # Handle absolute import
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from ml_service_connector import MLServiceConnector

# Import trade history loader
try:
    from core.trade_history_loader import trade_history_loader
except ImportError:
    # Handle absolute import
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    from core.trade_history_loader import trade_history_loader

# Import Risk Manager integration
try:
    import sys
    from pathlib import Path
    integration_path = Path(__file__).parent.parent / "integration"
    sys.path.insert(0, str(integration_path))
    from risk_manager_integration import create_kelly_risk_integration, RiskAdjustedKellyResult
    RISK_INTEGRATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Risk Manager integration not available: {e}")
    RISK_INTEGRATION_AVAILABLE = False
    # Create stub class
    class RiskAdjustedKellyResult:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

logger = logging.getLogger(__name__)


@dataclass
class KellyRecommendation:
    """Kelly position recommendation result"""
    symbol: str
    timestamp: datetime
    kelly_fraction: float
    position_size: int
    confidence: float
    win_probability: float
    win_loss_ratio: float
    capital_risk: float
    reasoning: str
    status: str
    ml_models_used: List[str]
    model_agreement: bool
    constraints_applied: List[str]
    metadata: Dict[str, Any]


@dataclass
class KellyPerformanceMetrics:
    """Kelly service performance metrics"""
    timestamp: datetime
    total_recommendations: int
    successful_recommendations: int
    average_confidence: float
    average_kelly_fraction: float
    model_agreement_rate: float
    last_24h_count: int
    service_uptime_hours: float


class KellyService:
    """
    Main Kelly Criterion service for MinhOS integration
    
    Provides high-level API for:
    - ML-enhanced Kelly position sizing
    - Real-time recommendations
    - Performance monitoring
    - Risk management integration
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Kelly Service
        
        Args:
            config: Service configuration
        """
        self.config = config or self._default_config()
        self.db_path = self.config.get('db_path', '/home/colindo/Sync/minh_v4/data/kelly_service.db')
        
        # Initialize ML service connector
        self.ml_connector = MLServiceConnector(self.config.get('ml_config', {}))
        
        # Initialize Risk Manager integration
        self.risk_integration = None
        self.risk_integration_enabled = RISK_INTEGRATION_AVAILABLE and self.config.get('enable_risk_integration', True)
        
        # Service state
        self.is_running = False
        self.start_time = None
        self.last_recommendation_time = None
        
        # Performance tracking
        self.total_recommendations = 0
        self.successful_recommendations = 0
        self.recommendation_history = []
        self.performance_cache = {}
        
        # Background tasks
        self.background_tasks = set()
        self.monitoring_task = None
        
        # Initialize database
        self._init_database()
        
        logger.info("Kelly Service initialized")
    
    def _default_config(self) -> Dict:
        """Default Kelly Service configuration"""
        return {
            'db_path': '/home/colindo/Sync/minh_v4/data/kelly_service.db',
            'enable_background_monitoring': True,
            'monitoring_interval': 60,  # seconds
            'max_recommendation_history': 1000,
            'cache_ttl': 300,  # 5 minutes
            'default_account_capital': 100000.0,
            'ml_config': {
                'enable_lstm': True,
                'enable_ensemble': True,
                'prediction_timeout': 10.0,
                'kelly_config': {
                    'max_kelly_fraction': 0.25,
                    'kelly_fraction_multiplier': 0.6,
                    'confidence_threshold': 0.6
                }
            }
        }
    
    def _init_database(self):
        """Initialize Kelly service database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kelly_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    kelly_fraction REAL NOT NULL,
                    position_size INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    win_probability REAL NOT NULL,
                    win_loss_ratio REAL NOT NULL,
                    capital_risk REAL NOT NULL,
                    reasoning TEXT,
                    status TEXT NOT NULL,
                    ml_models_used TEXT,
                    model_agreement BOOLEAN,
                    constraints_applied TEXT,
                    metadata TEXT
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kelly_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_recommendations INTEGER NOT NULL,
                    successful_recommendations INTEGER NOT NULL,
                    average_confidence REAL NOT NULL,
                    average_kelly_fraction REAL NOT NULL,
                    model_agreement_rate REAL NOT NULL,
                    last_24h_count INTEGER NOT NULL,
                    service_uptime_hours REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Kelly service database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    async def start(self):
        """Start Kelly Service"""
        logger.info("Starting Kelly Service...")
        
        try:
            # Initialize ML services
            success = await self.ml_connector.initialize_services()
            if not success:
                logger.warning("Some ML services failed to initialize")
            
            # Initialize Risk Manager integration
            if self.risk_integration_enabled:
                try:
                    self.risk_integration = await create_kelly_risk_integration()
                    logger.info("Risk Manager integration initialized")
                except Exception as e:
                    logger.warning(f"Risk Manager integration failed: {e}")
                    self.risk_integration_enabled = False
            
            # Start background monitoring if enabled
            if self.config.get('enable_background_monitoring', True):
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
                self.background_tasks.add(self.monitoring_task)
            
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("Kelly Service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kelly Service: {e}")
            raise
    
    async def stop(self):
        """Stop Kelly Service"""
        logger.info("Stopping Kelly Service...")
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Kelly Service stopped")
    
    async def get_kelly_recommendation(self,
                                     symbol: str,
                                     market_data: Dict,
                                     trade_history: Optional[List[Dict]] = None,
                                     account_capital: Optional[float] = None) -> KellyRecommendation:
        """
        Get Kelly position recommendation for symbol
        
        Args:
            symbol: Trading symbol
            market_data: Current market data
            trade_history: Historical trade data
            account_capital: Account capital (uses default if None)
            
        Returns:
            Kelly recommendation
        """
        if not self.is_running:
            raise RuntimeError("Kelly Service is not running")
        
        account_capital = account_capital or self.config.get('default_account_capital', 100000.0)
        
        logger.info(f"Getting Kelly recommendation for {symbol}")
        
        # Load trade history from database if not provided
        if trade_history is None:
            trade_history = trade_history_loader.get_trade_history(
                symbol=symbol,
                lookback_days=30,
                limit=50
            )
            logger.info(f"Loaded {len(trade_history)} historical trades for {symbol}")
        
        try:
            # Get unified ML recommendation
            ml_result = await self.ml_connector.get_unified_ml_recommendation(
                symbol, market_data, trade_history, account_capital
            )
            
            # Apply Risk Manager constraints if enabled
            original_kelly_fraction = ml_result.get('kelly_fraction', 0.0)
            original_position_size = ml_result.get('position_size', 0)
            constraints_applied = ml_result.get('constraints_applied', [])
            
            if self.risk_integration_enabled and self.risk_integration:
                try:
                    current_price = market_data.get('price', market_data.get('last', 100.0))
                    risk_result = await self.risk_integration.validate_and_adjust_kelly_position(
                        symbol=symbol,
                        kelly_fraction=original_kelly_fraction,
                        position_size=original_position_size,
                        account_capital=account_capital,
                        current_price=current_price
                    )
                    
                    # Use risk-adjusted values
                    adjusted_kelly_fraction = risk_result.adjusted_kelly_fraction
                    adjusted_position_size = risk_result.adjusted_position_size
                    adjusted_capital_risk = risk_result.capital_at_risk
                    
                    # Update constraints
                    constraints_applied.extend(risk_result.risk_constraints_applied)
                    
                    # Update status if risk validation failed
                    if not risk_result.risk_validation_passed:
                        ml_result['status'] = 'risk_constrained'
                    
                    logger.info(f"Risk adjustment: Kelly {original_kelly_fraction:.4f}→{adjusted_kelly_fraction:.4f}, "
                              f"Position {original_position_size}→{adjusted_position_size}")
                    
                except Exception as e:
                    logger.error(f"Risk validation failed, using original values: {e}")
                    adjusted_kelly_fraction = original_kelly_fraction
                    adjusted_position_size = original_position_size
                    adjusted_capital_risk = ml_result.get('capital_risk', 0.0)
                    constraints_applied.append("Risk validation error - using original values")
            else:
                # No risk integration - use original values
                adjusted_kelly_fraction = original_kelly_fraction
                adjusted_position_size = original_position_size
                adjusted_capital_risk = ml_result.get('capital_risk', 0.0)
            
            # Convert to KellyRecommendation
            recommendation = KellyRecommendation(
                symbol=symbol,
                timestamp=datetime.now(),
                kelly_fraction=adjusted_kelly_fraction,
                position_size=adjusted_position_size,
                confidence=ml_result.get('confidence', 0.0),
                win_probability=ml_result.get('win_probability', 0.5),
                win_loss_ratio=ml_result.get('win_loss_ratio', 1.0),
                capital_risk=adjusted_capital_risk,
                reasoning=ml_result.get('reasoning', ''),
                status=ml_result.get('status', 'unknown'),
                ml_models_used=self._extract_models_used(ml_result),
                model_agreement=ml_result.get('model_agreement', False),
                constraints_applied=constraints_applied,
                metadata={
                    'ml_predictions': ml_result.get('ml_predictions', []),
                    'individual_probabilities': ml_result.get('individual_probabilities', []),
                    'market_data': market_data,
                    'account_capital': account_capital
                }
            )
            
            # Update counters
            self.total_recommendations += 1
            if recommendation.status == 'success':
                self.successful_recommendations += 1
            
            # Store recommendation
            await self._store_recommendation(recommendation)
            
            # Update cache
            self.last_recommendation_time = datetime.now()
            self.recommendation_history.append(recommendation)
            
            # Trim history if too long
            max_history = self.config.get('max_recommendation_history', 1000)
            if len(self.recommendation_history) > max_history:
                self.recommendation_history = self.recommendation_history[-max_history:]
            
            logger.info(f"Kelly recommendation for {symbol}: "
                       f"status={recommendation.status}, "
                       f"kelly_fraction={recommendation.kelly_fraction:.3f}, "
                       f"position_size={recommendation.position_size}")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to get Kelly recommendation for {symbol}: {e}")
            
            # Return error recommendation
            error_recommendation = KellyRecommendation(
                symbol=symbol,
                timestamp=datetime.now(),
                kelly_fraction=0.0,
                position_size=0,
                confidence=0.0,
                win_probability=0.5,
                win_loss_ratio=1.0,
                capital_risk=0.0,
                reasoning=f"Error: {str(e)}",
                status='error',
                ml_models_used=[],
                model_agreement=False,
                constraints_applied=[],
                metadata={'error': str(e)}
            )
            
            await self._store_recommendation(error_recommendation)
            return error_recommendation
    
    async def get_performance_metrics(self) -> KellyPerformanceMetrics:
        """
        Get Kelly service performance metrics
        
        Returns:
            Performance metrics
        """
        # Calculate recent metrics
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        # Count recent recommendations
        recent_count = sum(
            1 for rec in self.recommendation_history
            if rec.timestamp > last_24h
        )
        
        # Calculate averages
        successful_recs = [r for r in self.recommendation_history if r.status == 'success']
        avg_confidence = sum(r.confidence for r in successful_recs) / max(1, len(successful_recs))
        avg_kelly = sum(r.kelly_fraction for r in successful_recs) / max(1, len(successful_recs))
        
        # Model agreement rate
        agreement_rate = sum(
            1 for r in successful_recs if r.model_agreement
        ) / max(1, len(successful_recs))
        
        # Service uptime
        uptime_hours = 0.0
        if self.start_time:
            uptime_delta = now - self.start_time
            uptime_hours = uptime_delta.total_seconds() / 3600
        
        metrics = KellyPerformanceMetrics(
            timestamp=now,
            total_recommendations=self.total_recommendations,
            successful_recommendations=self.successful_recommendations,
            average_confidence=avg_confidence,
            average_kelly_fraction=avg_kelly,
            model_agreement_rate=agreement_rate,
            last_24h_count=recent_count,
            service_uptime_hours=uptime_hours
        )
        
        # Store metrics
        await self._store_performance_metrics(metrics)
        
        return metrics
    
    async def get_service_health(self) -> Dict:
        """
        Get service health status
        
        Returns:
            Health status dictionary
        """
        # Get ML connector health
        ml_health = await self.ml_connector.health_check()
        
        # Service-specific health
        service_health = {
            'timestamp': datetime.now().isoformat(),
            'service_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_recommendation': self.last_recommendation_time.isoformat() if self.last_recommendation_time else None,
            'total_recommendations': self.total_recommendations,
            'success_rate': self.successful_recommendations / max(1, self.total_recommendations),
            'background_tasks_running': len(self.background_tasks),
            'ml_connector_health': ml_health
        }
        
        return service_health
    
    async def get_recent_recommendations(self, limit: int = 10) -> List[Dict]:
        """
        Get recent Kelly recommendations
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recent recommendations
        """
        recent = self.recommendation_history[-limit:] if self.recommendation_history else []
        return [asdict(rec) for rec in reversed(recent)]
    
    # Private helper methods
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        logger.info("Starting Kelly Service monitoring loop")
        
        while self.is_running:
            try:
                # Collect performance metrics
                metrics = await self.get_performance_metrics()
                
                # Log key metrics
                logger.info(f"Kelly Service metrics: "
                           f"total_recs={metrics.total_recommendations}, "
                           f"success_rate={metrics.successful_recommendations/max(1,metrics.total_recommendations):.3f}, "
                           f"avg_confidence={metrics.average_confidence:.3f}")
                
                # Sleep until next monitoring cycle
                await asyncio.sleep(self.config.get('monitoring_interval', 60))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error
        
        logger.info("Kelly Service monitoring loop stopped")
    
    async def _store_recommendation(self, recommendation: KellyRecommendation):
        """Store recommendation in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kelly_recommendations (
                    symbol, timestamp, kelly_fraction, position_size, confidence,
                    win_probability, win_loss_ratio, capital_risk, reasoning, status,
                    ml_models_used, model_agreement, constraints_applied, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recommendation.symbol,
                recommendation.timestamp.isoformat(),
                recommendation.kelly_fraction,
                recommendation.position_size,
                recommendation.confidence,
                recommendation.win_probability,
                recommendation.win_loss_ratio,
                recommendation.capital_risk,
                recommendation.reasoning,
                recommendation.status,
                json.dumps(recommendation.ml_models_used),
                recommendation.model_agreement,
                json.dumps(recommendation.constraints_applied),
                json.dumps(recommendation.metadata, default=str)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store recommendation: {e}")
    
    async def _store_performance_metrics(self, metrics: KellyPerformanceMetrics):
        """Store performance metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kelly_performance (
                    timestamp, total_recommendations, successful_recommendations,
                    average_confidence, average_kelly_fraction, model_agreement_rate,
                    last_24h_count, service_uptime_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.total_recommendations,
                metrics.successful_recommendations,
                metrics.average_confidence,
                metrics.average_kelly_fraction,
                metrics.model_agreement_rate,
                metrics.last_24h_count,
                metrics.service_uptime_hours
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store performance metrics: {e}")
    
    def _extract_models_used(self, ml_result: Dict) -> List[str]:
        """Extract list of ML models used from result"""
        models = []
        
        if ml_result.get('lstm_available', False):
            models.append('lstm')
        
        if ml_result.get('ensemble_available', False):
            models.append('ensemble')
        
        return models
    
    def get_config(self) -> Dict:
        """Get service configuration"""
        return self.config.copy()
    
    def get_status(self) -> Dict:
        """Get service status summary"""
        return {
            'running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'total_recommendations': self.total_recommendations,
            'successful_recommendations': self.successful_recommendations,
            'success_rate': self.successful_recommendations / max(1, self.total_recommendations),
            'last_recommendation': self.last_recommendation_time.isoformat() if self.last_recommendation_time else None,
            'ml_connector_status': self.ml_connector.get_status()
        }