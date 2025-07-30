#!/usr/bin/env python3
"""
MinhOS v3 AI Brain Service
==========================
Linux-native AI analysis and trading signal generation service.
Provides intelligent market analysis, pattern recognition, and trading signals
without Windows dependencies.

Replaces ai_brain_service.py with enhanced AI capabilities and clean architecture.
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import deque, defaultdict, Counter
import sqlite3
import pickle

# Import ML capabilities - Enhanced with detailed error logging
try:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from capabilities.prediction.lstm import LSTMPredictor
    from capabilities.ensemble import EnsembleManager
    from capabilities.position_sizing.api import PositionSizingAPI
    from .ml_pipeline_service import MLPipelineService
    HAS_LSTM = True
    HAS_ENSEMBLE = True
    HAS_KELLY = True
    HAS_ML_PIPELINE = True
    print(f"✅ ML capabilities imported successfully - LSTM:{HAS_LSTM}, Ensemble:{HAS_ENSEMBLE}, Kelly:{HAS_KELLY}, Pipeline:{HAS_ML_PIPELINE}")
except ImportError as e:
    print(f"❌ ML capabilities import failed: {e}")
    import traceback
    traceback.print_exc()
    HAS_LSTM = False
    HAS_ENSEMBLE = False
    HAS_KELLY = False
    HAS_ML_PIPELINE = False
    LSTMPredictor = None
    EnsembleManager = None
    PositionSizingAPI = None
    MLPipelineService = None

# Import other services
from .sierra_client import get_sierra_client
from ..models.market import MarketData
from .state_manager import get_state_manager
from ..core.market_data_adapter import get_market_data_adapter
from .sierra_historical_data import get_sierra_historical_service
from .ab_testing_service import get_ab_testing_service
from .ml_monitoring_service import get_ml_monitoring_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_brain")

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class AnalysisType(Enum):
    TECHNICAL = "technical"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    PATTERN = "pattern"

class PatternType(Enum):
    # Market patterns
    PRICE_BREAKOUT = "price_breakout"
    PRICE_BREAKDOWN = "price_breakdown"
    VOLUME_SPIKE = "volume_spike"
    VOLATILITY_EXPANSION = "volatility_expansion"
    TREND_REVERSAL = "trend_reversal"
    SUPPORT_RESISTANCE = "support_resistance"
    
    # System patterns
    DATA_LATENCY = "data_latency"
    CONNECTION_ISSUE = "connection_issue"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    
    # Trading patterns
    PROFITABLE_SETUP = "profitable_setup"
    LOSS_PATTERN = "loss_pattern"
    ENTRY_TIMING = "entry_timing"
    EXIT_TIMING = "exit_timing"
    
    # Risk patterns
    RISK_THRESHOLD_BREACH = "risk_threshold_breach"
    DRAWDOWN_PATTERN = "drawdown_pattern"
    POSITION_SIZING_ERROR = "position_sizing_error"

class PatternConfidence(Enum):
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

@dataclass
class TradingSignal:
    signal: SignalType
    confidence: float  # 0.0 to 1.0
    reasoning: str
    analysis_type: AnalysisType
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class DetectedPattern:
    """Represents a detected pattern"""
    pattern_type: PatternType
    confidence: float
    description: str
    context: Dict[str, Any]
    timestamp: datetime
    market_conditions: Dict[str, Any]
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

@dataclass
class LearningEvent:
    """Represents an event that can be learned from"""
    event_type: str
    context: Dict[str, Any]
    outcome: str
    success: bool
    timestamp: datetime
    patterns_detected: List[str] = None
    
    def __post_init__(self):
        if self.patterns_detected is None:
            self.patterns_detected = []

@dataclass
class MarketAnalysis:
    trend_direction: str  # "up", "down", "sideways"
    trend_strength: float  # 0.0 to 1.0
    volatility_level: str  # "low", "medium", "high"
    volume_analysis: str  # "increasing", "decreasing", "normal"
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    key_levels: List[float] = None
    
    def __post_init__(self):
        if self.key_levels is None:
            self.key_levels = []

class AIBrainService:
    """
    Consolidated AI analysis service for MinhOS v3
    Provides intelligent market analysis, pattern recognition, and trading signals
    """
    
    def __init__(self, db_path: str = None):
        """Initialize AI Brain Service with pattern recognition and ML capabilities"""
        self.running = False
        
        # Market data buffer for analysis
        self.market_data_buffer = deque(maxlen=1000)  # Store last 1000 data points
        self.analysis_history = deque(maxlen=100)     # Store last 100 analyses
        
        # Pattern recognition components (from pattern_analyzer)
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "patterns.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize ML capabilities
        self.ml_capabilities = {}
        self._initialize_ml_capabilities()
        
        # Initialize A/B testing service
        self.ab_testing = get_ab_testing_service()
        
        # Initialize ML monitoring service
        self.ml_monitoring = get_ml_monitoring_service()
        
        # Pattern storage
        self.pattern_history = deque(maxlen=1000)
        self.known_patterns: Dict[str, Dict[str, Any]] = {}
        self.pattern_correlations: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.pattern_outcomes: Dict[str, List[bool]] = defaultdict(list)
        
        # Time-based pattern tracking
        self.time_patterns = {
            'hourly': defaultdict(list),
            'daily': defaultdict(list),
            'weekly': defaultdict(list)
        }
        
        # Market condition patterns
        self.market_regime_patterns = defaultdict(list)
        
        # Analysis parameters
        self.analysis_params = {
            "trend_period": 20,
            "momentum_period": 14,
            "volatility_period": 20,
            "volume_period": 20,
            "confidence_threshold": 0.6,
            "strong_signal_threshold": 0.8,
            "min_volume_threshold": 100,  # Minimum volume for real-time analysis
            "historical_fallback_days": 7  # Days of historical data to use as fallback
        }
        
        # Historical data service
        self.historical_service = None
        
        # Current state
        self.current_signal: Optional[TradingSignal] = None
        self.current_analysis: Optional[MarketAnalysis] = None
        self.last_analysis_time = None
        
        # Service references
        self.sierra_client = None
        self.state_manager = None
        self.market_data_adapter = get_market_data_adapter()
        
        # Statistics
        self.stats = {
            "analyses_performed": 0,
            "signals_generated": 0,
            "buy_signals": 0,
            "sell_signals": 0,
            "hold_signals": 0,
            "accuracy_tracker": deque(maxlen=100),
            "start_time": datetime.now().isoformat()
        }
        
        # Pattern recognition
        self.pattern_detector = PatternDetector()
        
        logger.info("🧠 AI Brain Service initialized")
    
    def _initialize_ml_capabilities(self):
        """Initialize ML capabilities (LSTM, Ensemble, etc.)"""
        logger.info(f"🔄 Initializing ML capabilities - HAS_ML_PIPELINE:{HAS_ML_PIPELINE}, HAS_LSTM:{HAS_LSTM}, HAS_ENSEMBLE:{HAS_ENSEMBLE}, HAS_KELLY:{HAS_KELLY}")
        
        try:
            project_root = Path(__file__).parent.parent.parent
            
            # Initialize unified ML Pipeline Service
            if HAS_ML_PIPELINE:
                logger.info("🔄 Attempting to initialize ML Pipeline Service...")
                from .ml_pipeline_service import MLPipelineService
                self.ml_capabilities['pipeline'] = MLPipelineService()
                logger.info("✅ ML Pipeline Service initialized (LSTM + Ensemble + Kelly)")
            else:
                logger.warning(f"⚠️ ML Pipeline Service not available - HAS_ML_PIPELINE:{HAS_ML_PIPELINE}, MLPipelineService:{MLPipelineService is not None}")
                
                # Fallback to individual components
                # Initialize LSTM predictor
                if HAS_LSTM and LSTMPredictor:
                    logger.info("🔄 Attempting to initialize LSTM predictor...")
                    model_path = project_root / "ml_models" / "lstm_model"
                    
                    self.ml_capabilities['lstm'] = LSTMPredictor(
                        sequence_length=20,
                        features=8,
                        model_path=str(model_path)
                    )
                    logger.info("✅ LSTM predictor initialized")
                else:
                    logger.warning(f"⚠️ LSTM predictor disabled - HAS_LSTM:{HAS_LSTM}, LSTMPredictor:{LSTMPredictor is not None}")
                
                # Initialize Ensemble Manager
                if HAS_ENSEMBLE and EnsembleManager:
                    logger.info("🔄 Attempting to initialize Ensemble Manager...")
                    ensemble_path = project_root / "ml_models" / "ensemble"
                    
                    self.ml_capabilities['ensemble'] = EnsembleManager(
                        model_path=str(ensemble_path)
                    )
                    logger.info("✅ Ensemble manager initialized")
                else:
                    logger.warning(f"⚠️ Ensemble models disabled - HAS_ENSEMBLE:{HAS_ENSEMBLE}, EnsembleManager:{EnsembleManager is not None}")
                
                # Initialize Kelly Criterion Position Sizing
                if HAS_KELLY and PositionSizingAPI:
                    logger.info("🔄 Attempting to initialize Kelly Criterion...")
                    self.ml_capabilities['kelly'] = PositionSizingAPI()
                    logger.info("✅ Kelly Criterion position sizing initialized")
                else:
                    logger.warning(f"⚠️ Kelly Criterion disabled - HAS_KELLY:{HAS_KELLY}, PositionSizingAPI:{PositionSizingAPI is not None}")
                
        except Exception as e:
            logger.error(f"❌ ML capabilities initialization error: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
        logger.info(f"🤖 ML Capabilities: {list(self.ml_capabilities.keys())}")
        
        # Force enable at least one capability for testing
        if not self.ml_capabilities:
            logger.warning("⚠️ No ML capabilities loaded, attempting force initialization...")
            try:
                from .ml_pipeline_service import MLPipelineService
                self.ml_capabilities['pipeline'] = MLPipelineService()
                logger.info("✅ Force-initialized ML Pipeline Service")
            except Exception as e:
                logger.error(f"❌ Force initialization failed: {e}")
    
    async def _load_historical_context(self):
        """Load historical market data for AI context"""
        try:
            # Get primary trading symbol (centralized symbol management)
            from ..core.symbol_integration import get_ai_brain_primary_symbol, get_symbol_integration
            primary_symbol = get_ai_brain_primary_symbol()
            
            # Mark service as migrated to centralized symbol management
            get_symbol_integration().mark_service_migrated('ai_brain_service')
            
            # Load substantial historical context (200 records for deep analysis)
            historical_data = self.market_data_adapter.get_historical_data(primary_symbol, limit=200)
            
            if historical_data:
                logger.info(f"🧠 Loading {len(historical_data)} historical records for AI context...")
                
                # Convert to AI Brain format and populate buffer
                for data in reversed(historical_data):  # Reverse to maintain chronological order
                    try:
                        data_point = {
                            'timestamp': data.timestamp,
                            'symbol': data.symbol,
                            'close': data.close,
                            'bid': getattr(data, 'bid', data.close),
                            'ask': getattr(data, 'ask', data.close), 
                            'volume': getattr(data, 'volume', 0),
                            'high': getattr(data, 'high', data.close),
                            'low': getattr(data, 'low', data.close),
                            'source': data.source
                        }
                        self.market_data_buffer.append(data_point)
                    except Exception as e:
                        logger.debug(f"Skipping invalid historical record: {e}")
                        continue
                
                logger.info(f"✅ AI Brain loaded {len(self.market_data_buffer)} historical records")
                logger.info(f"🧠 AI now has substantial market context for intelligent analysis")
                
                # Get price range for context
                if len(self.market_data_buffer) > 0:
                    prices = [d['close'] for d in self.market_data_buffer if d['close'] is not None and d['close'] > 0]
                    if prices:
                        min_price, max_price = min(prices), max(prices)
                        logger.info(f"📊 Historical price range: ${min_price:.2f} - ${max_price:.2f}")
            else:
                logger.warning("⚠️ No historical data available - AI will start with minimal context")
                
        except Exception as e:
            logger.error(f"❌ Error loading historical context: {e}")
            logger.info("🧠 AI Brain will start with real-time data only")
    
    async def start(self):
        """Start the AI Brain Service"""
        logger.info("🚀 Starting AI Brain Service...")
        self.running = True
        
        # Load historical data for AI context
        await self._load_historical_context()
        
        # Initialize service references
        self.sierra_client = get_sierra_client()
        self.state_manager = get_state_manager()
        
        # Initialize historical data service
        try:
            self.historical_service = get_sierra_historical_service()
            logger.info("✅ Historical data service connected for AI analysis")
        except Exception as e:
            logger.warning(f"⚠️ Historical data service unavailable: {e}")
        
        # Subscribe to market data updates
        if hasattr(self.sierra_client, 'add_data_handler'):
            self.sierra_client.add_data_handler(self._on_market_data)
        
        # Start ML monitoring service
        await self.ml_monitoring.start()
        
        # Start analysis loops
        asyncio.create_task(self._analysis_loop())
        asyncio.create_task(self._signal_validation_loop())
        asyncio.create_task(self._performance_tracking_loop())
        
        logger.info("✅ AI Brain Service started")
    
    async def stop(self):
        """Stop the AI Brain Service"""
        logger.info("🛑 Stopping AI Brain Service...")
        self.running = False
        
        # Stop ML monitoring service
        await self.ml_monitoring.stop()
        
        logger.info("AI Brain Service stopped")
    
    async def _on_market_data(self, market_data):
        """Handle new market data"""
        try:
            # Handle both MarketData objects and dictionaries
            if isinstance(market_data, dict):
                data_point = {
                    'timestamp': market_data.get('timestamp'),
                    'symbol': market_data.get('symbol'),
                    'close': market_data.get('close'),
                    'bid': market_data.get('bid'),
                    'ask': market_data.get('ask'),
                    'volume': market_data.get('volume'),
                    'high': market_data.get('high', market_data.get('close')),
                    'low': market_data.get('low', market_data.get('close')),
                    'source': market_data.get('source')
                }
            else:
                data_point = {
                    'timestamp': market_data.timestamp,
                    'symbol': market_data.symbol,
                    'close': market_data.close,
                    'bid': market_data.bid,
                    'ask': market_data.ask,
                    'volume': market_data.volume,
                    'high': getattr(market_data, 'high', market_data.close),
                    'low': getattr(market_data, 'low', market_data.close),
                    'source': market_data.source
                }
            
            self.market_data_buffer.append(data_point)
            
            # Feed data to ML Pipeline if available
            if 'pipeline' in self.ml_capabilities:
                try:
                    ml_prediction = await self.ml_capabilities['pipeline'].get_ml_prediction(data_point)
                    self._integrate_ml_prediction(ml_prediction)
                except Exception as e:
                    logger.warning(f"ML Pipeline prediction failed: {e}")
            
            # Trigger analysis if we have enough data
            if len(self.market_data_buffer) >= 20:
                await self._perform_analysis()
                
        except Exception as e:
            logger.error(f"❌ Market data processing error: {e}")
    
    def _integrate_ml_prediction(self, ml_prediction):
        """Integrate ML pipeline prediction into AI Brain analysis"""
        try:
            # Store ML prediction for use in analysis
            self.ml_prediction = ml_prediction
            
            # Update confidence based on ML agreement
            if ml_prediction.models_agreement and ml_prediction.models_agreement > 0.8:
                logger.info(f"🤖 High ML agreement: {ml_prediction.models_agreement:.2f} for {ml_prediction.direction}")
            
            # Store ML metrics for dashboard
            if hasattr(self, 'ml_metrics'):
                self.ml_metrics.append({
                    'timestamp': ml_prediction.timestamp,
                    'direction': ml_prediction.direction,
                    'confidence': ml_prediction.confidence,
                    'agreement': ml_prediction.models_agreement,
                    'kelly_fraction': ml_prediction.kelly_fraction
                })
            else:
                self.ml_metrics = []
                
        except Exception as e:
            logger.error(f"Failed to integrate ML prediction: {e}")
    
    async def _analysis_loop(self):
        """Main analysis loop"""
        while self.running:
            try:
                # Perform analysis every 30 seconds if we have data
                if len(self.market_data_buffer) >= self.analysis_params["trend_period"]:
                    await self._perform_analysis()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Analysis loop error: {e}")
                await asyncio.sleep(30)
    
    async def _perform_analysis(self):
        """Perform comprehensive market analysis with historical data fallback"""
        try:
            # Check if we have sufficient real-time data
            analysis_result = await self._get_analysis_data()
            if not analysis_result:
                return
            
            # Unpack analysis data and source indicator
            if isinstance(analysis_result, dict) and 'data' in analysis_result:
                analysis_data = analysis_result['data']
                data_source = analysis_result.get('source', 'unknown')
            else:
                # Backwards compatibility
                analysis_data = analysis_result
                data_source = 'realtime'
            
            # Perform different types of analysis
            trend_analysis = await self._analyze_trend(analysis_data)
            momentum_analysis = await self._analyze_momentum(analysis_data)
            volatility_analysis = await self._analyze_volatility(analysis_data)
            volume_analysis = await self._analyze_volume(analysis_data)
            pattern_analysis = await self._analyze_patterns(analysis_data)
            
            # Perform ML analysis
            ml_analysis = await self._analyze_ml_predictions(analysis_data)
            
            # Combine analyses
            combined_analysis = await self._combine_analyses(
                trend_analysis, momentum_analysis, volatility_analysis, 
                volume_analysis, pattern_analysis, ml_analysis
            )
            
            # Generate trading signal with data source context and A/B testing
            signal = await self._generate_signal(combined_analysis, analysis_data, data_source)
            
            # Update current state
            self.current_analysis = combined_analysis
            self.current_signal = signal
            self.last_analysis_time = datetime.now()
            
            # Update statistics
            self.stats["analyses_performed"] += 1
            if signal:
                self.stats["signals_generated"] += 1
                if signal.signal == SignalType.BUY or signal.signal == SignalType.STRONG_BUY:
                    self.stats["buy_signals"] += 1
                elif signal.signal == SignalType.SELL or signal.signal == SignalType.STRONG_SELL:
                    self.stats["sell_signals"] += 1
                else:
                    self.stats["hold_signals"] += 1
            
            # Store analysis history
            self.analysis_history.append({
                'timestamp': datetime.now().isoformat(),
                'analysis': asdict(combined_analysis) if combined_analysis else None,
                'signal': asdict(signal) if signal else None
            })
            
            if signal and signal.confidence > self.analysis_params["confidence_threshold"]:
                logger.info(f"🎯 Signal: {signal.signal.value} ({signal.confidence:.1%} confidence) - {signal.reasoning}")
            
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
    
    async def _get_analysis_data(self) -> Dict[str, Any]:
        """Get data for analysis - real-time or historical fallback"""
        try:
            # First, check if we have sufficient and fresh real-time data with volume
            if self.market_data_buffer:
                recent_data = list(self.market_data_buffer)[-self.analysis_params["trend_period"]:]
                
                # Check if recent data has sufficient volume
                recent_volumes = [d.get('volume', 0) for d in recent_data if d.get('volume', 0) > 0]
                avg_recent_volume = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0
                
                # Check data freshness
                data_is_fresh = False
                if recent_data:
                    try:
                        last_timestamp = recent_data[-1].get('timestamp')
                        if last_timestamp:
                            from datetime import datetime, timedelta
                            if isinstance(last_timestamp, str):
                                last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                            elif isinstance(last_timestamp, (int, float)):
                                last_time = datetime.fromtimestamp(last_timestamp)
                            else:
                                last_time = last_timestamp
                            
                            age_minutes = (datetime.now() - last_time.replace(tzinfo=None)).total_seconds() / 60
                            data_is_fresh = age_minutes <= 5  # Fresh within 5 minutes
                    except Exception as e:
                        logger.warning(f"Could not verify data freshness: {e}")
                        data_is_fresh = False
                
                # If we have good volume AND fresh data, use real-time
                if avg_recent_volume >= self.analysis_params["min_volume_threshold"] and data_is_fresh:
                    logger.info(f"📊 Using real-time data (avg volume: {avg_recent_volume:,.0f})")
                    return {'data': recent_data, 'source': 'realtime'}
                elif avg_recent_volume >= self.analysis_params["min_volume_threshold"] and not data_is_fresh:
                    logger.info(f"⚠️ Real-time data has good volume ({avg_recent_volume:,.0f}) but is stale, falling back to historical data")
                else:
                    logger.info(f"⚠️ Low real-time volume ({avg_recent_volume:.0f}), falling back to historical data")
            
            # Fallback to historical data
            if self.historical_service:
                try:
                    end_date = datetime.utcnow()
                    start_date = end_date - timedelta(days=self.analysis_params["historical_fallback_days"])
                    
                    # Get historical data for NQU25-CME (primary symbol)
                    historical_records = await self.historical_service.get_historical_data(
                        'NQU25-CME', start_date, end_date
                    )
                    
                    if historical_records:
                        # Convert to format expected by analysis methods
                        historical_data = []
                        for record in historical_records:
                            historical_data.append({
                                'timestamp': record.timestamp,
                                'open': record.open,
                                'high': record.high,
                                'low': record.low,
                                'close': record.close,
                                'volume': record.volume
                            })
                        
                        logger.info(f"📈 Using historical data: {len(historical_data)} records, "
                                  f"avg volume: {sum(d['volume'] for d in historical_data)/len(historical_data):,.0f}")
                        return {'data': historical_data[-self.analysis_params["trend_period"]:], 'source': 'historical'}
                        
                except Exception as e:
                    logger.error(f"❌ Error fetching historical data: {e}")
            
            # If no historical service or error, return what we have
            if self.market_data_buffer:
                logger.warning("⚠️ Using limited real-time data despite low volume")
                return {'data': list(self.market_data_buffer)[-self.analysis_params["trend_period"]:], 'source': 'realtime_limited'}
            
            logger.warning("❌ No data available for analysis")
            return {'data': [], 'source': 'none'}
            
        except Exception as e:
            logger.error(f"❌ Error getting analysis data: {e}")
            fallback_data = list(self.market_data_buffer)[-self.analysis_params["trend_period"]:] if self.market_data_buffer else []
            return {'data': fallback_data, 'source': 'error_fallback'}
    
    async def _analyze_trend(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market trend"""
        try:
            if len(data) < 10:
                return {"direction": "unknown", "strength": 0.0}
            
            prices = [d['close'] for d in data if d['close'] is not None]
            
            if not prices:
                return {"direction": "unknown", "strength": 0.0}
            
            # Simple moving averages
            sma_short = statistics.mean(prices[-10:])
            sma_long = statistics.mean(prices[-20:]) if len(prices) >= 20 else statistics.mean(prices)
            
            # Trend direction
            if sma_short > sma_long * 1.002:  # 0.2% threshold
                direction = "up"
            elif sma_short < sma_long * 0.998:
                direction = "down"
            else:
                direction = "sideways"
            
            # Trend strength (based on price momentum)
            price_change = (prices[-1] - prices[0]) / prices[0] if prices[0] != 0 else 0
            strength = min(1.0, abs(price_change) * 100)  # Scale to 0-1
            
            return {
                "direction": direction,
                "strength": strength,
                "sma_short": sma_short,
                "sma_long": sma_long,
                "price_change_pct": price_change * 100
            }
            
        except Exception as e:
            logger.error(f"❌ Trend analysis error: {e}")
            return {"direction": "unknown", "strength": 0.0}
    
    async def _analyze_momentum(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze momentum indicators"""
        try:
            if len(data) < self.analysis_params["momentum_period"]:
                return {"rsi": 50.0, "momentum": "neutral"}
            
            prices = [d['close'] for d in data if d['close'] is not None]
            
            if not prices or len(prices) < 2:
                return {"rsi": 50.0, "momentum": "neutral"}
            
            # Simple RSI calculation
            price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [change if change > 0 else 0 for change in price_changes]
            losses = [-change if change < 0 else 0 for change in price_changes]
            
            if len(gains) >= 14:
                avg_gain = statistics.mean(gains[-14:])
                avg_loss = statistics.mean(losses[-14:])
                
                if avg_loss == 0:
                    rsi = 100.0
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50.0  # Neutral
            
            # Momentum classification
            if rsi > 70:
                momentum = "overbought"
            elif rsi < 30:
                momentum = "oversold"
            elif rsi > 55:
                momentum = "bullish"
            elif rsi < 45:
                momentum = "bearish"
            else:
                momentum = "neutral"
            
            return {
                "rsi": rsi,
                "momentum": momentum,
                "avg_gain": avg_gain if 'avg_gain' in locals() else 0,
                "avg_loss": avg_loss if 'avg_loss' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Momentum analysis error: {e}")
            return {"rsi": 50.0, "momentum": "neutral"}
    
    async def _analyze_volatility(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market volatility"""
        try:
            if len(data) < self.analysis_params["volatility_period"]:
                return {"level": "unknown", "value": 0.0}
            
            prices = [d['close'] for d in data if d['close'] is not None]
            
            if not prices or len(prices) < 2:
                return {"level": "unknown", "value": 0.0}
            
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] != 0]
            
            if not returns:
                return {"level": "unknown", "value": 0.0}
            
            volatility = statistics.stdev(returns) if len(returns) > 1 else 0.0
            
            # Classify volatility level
            if volatility > 0.02:  # 2%
                level = "high"
            elif volatility > 0.01:  # 1%
                level = "medium"
            else:
                level = "low"
            
            return {
                "level": level,
                "value": volatility,
                "returns_std": volatility,
                "avg_return": statistics.mean(returns)
            }
            
        except Exception as e:
            logger.error(f"❌ Volatility analysis error: {e}")
            return {"level": "unknown", "value": 0.0}
    
    async def _analyze_volume(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze volume patterns"""
        try:
            volumes = [d.get('volume', 0) for d in data if d.get('volume') is not None]
            
            if len(volumes) < 10:
                return {"trend": "unknown", "relative_volume": 1.0}
            
            # Remove zeros for analysis
            volumes = [v for v in volumes if v > 0]
            if not volumes:
                return {"trend": "unknown", "relative_volume": 1.0}
            
            avg_volume = statistics.mean(volumes)
            recent_volume = statistics.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
            
            relative_volume = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volume trend
            if relative_volume > 1.2:
                trend = "increasing"
            elif relative_volume < 0.8:
                trend = "decreasing"
            else:
                trend = "normal"
            
            return {
                "trend": trend,
                "relative_volume": relative_volume,
                "avg_volume": avg_volume,
                "recent_volume": recent_volume
            }
            
        except Exception as e:
            logger.error(f"❌ Volume analysis error: {e}")
            return {"trend": "unknown", "relative_volume": 1.0}
    
    async def _analyze_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze chart patterns"""
        try:
            if len(data) < 20:
                return {"patterns": [], "confidence": 0.0}
            
            patterns = self.pattern_detector.detect_patterns(data)
            
            return {
                "patterns": patterns,
                "confidence": max([p.get('confidence', 0) for p in patterns]) if patterns else 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ Pattern analysis error: {e}")
            return {"patterns": [], "confidence": 0.0}
    
    async def _analyze_ml_predictions(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze using ML capabilities (LSTM, Ensemble, etc.)"""
        import time
        
        ml_results = {
            "lstm_prediction": None,
            "ensemble_prediction": None,
            "ml_confidence": 0.0,
            "ml_direction": 0,
            "ml_enabled": False,
            "ml_agreement": 0.0
        }
        
        try:
            if not data:
                return ml_results
            
            # Get latest market data for ML prediction
            latest_data = data[-1] if data else {}
            
            # ML Pipeline Prediction (LSTM + Ensemble)
            lstm_confidence = 0.0
            lstm_direction = 0
            ensemble_confidence = 0.0
            ensemble_direction = 0
            pipeline_result = None
            
            if 'pipeline' in self.ml_capabilities:
                # Use unified ML Pipeline Service
                start_time = time.time()
                
                pipeline_service = self.ml_capabilities['pipeline']
                pipeline_prediction = await pipeline_service.get_ml_prediction(latest_data)
                
                # Extract results from unified prediction
                pipeline_result = {}
                if pipeline_prediction:
                    if hasattr(pipeline_prediction, 'lstm_prediction') and pipeline_prediction.lstm_prediction:
                        pipeline_result['lstm'] = pipeline_prediction.lstm_prediction
                    if hasattr(pipeline_prediction, 'ensemble_prediction') and pipeline_prediction.ensemble_prediction:
                        pipeline_result['ensemble'] = pipeline_prediction.ensemble_prediction
                
                if pipeline_result and 'lstm' in pipeline_result:
                    lstm_result = pipeline_result['lstm']
                    ml_results["lstm_prediction"] = lstm_result
                    ml_results["ml_enabled"] = True
                    
                    if lstm_result.get('confidence', 0) > 0:
                        lstm_confidence = lstm_result.get('confidence', 0)
                        lstm_direction = lstm_result.get('direction', 0)
                
                # Record performance metrics
                latency_ms = (time.time() - start_time) * 1000
                self.ml_monitoring.record_performance_metric('lstm', 'latency_ms', latency_ms)
                self.ml_monitoring.record_performance_metric('lstm', 'confidence', lstm_confidence)
                
            elif 'lstm' in self.ml_capabilities:
                start_time = time.time()
                
                lstm_predictor = self.ml_capabilities['lstm']
                lstm_result = await lstm_predictor.predict_direction(latest_data)
                ml_results["lstm_prediction"] = lstm_result
                ml_results["ml_enabled"] = True
                
                # Record performance metrics for monitoring
                latency_ms = (time.time() - start_time) * 1000
                self.ml_monitoring.record_performance_metric('lstm', 'latency_ms', latency_ms)
                
                if lstm_result.get('confidence', 0) > 0:
                    lstm_confidence = lstm_result.get('confidence', 0)
                    lstm_direction = lstm_result.get('direction', 0)
                    
                    # Record prediction accuracy metric
                    self.ml_monitoring.record_performance_metric('lstm', 'confidence', lstm_confidence)
                    
                # Record error rate if prediction failed
                if 'error' in lstm_result:
                    self.ml_monitoring.record_performance_metric('lstm', 'error_rate', 1.0)
                else:
                    self.ml_monitoring.record_performance_metric('lstm', 'error_rate', 0.0)
            
                # Handle Ensemble results from pipeline
                if pipeline_result and 'ensemble' in pipeline_result:
                    ensemble_result = pipeline_result['ensemble']
                    ml_results["ensemble_prediction"] = ensemble_result
                    ml_results["ml_enabled"] = True
                    
                    if ensemble_result.get('confidence', 0) > 0:
                        ensemble_confidence = ensemble_result.get('confidence', 0)
                        ensemble_direction = ensemble_result.get('direction', 0)
                    
                    # Record performance metrics
                    self.ml_monitoring.record_performance_metric('ensemble', 'confidence', ensemble_confidence)
                
            elif 'ensemble' in self.ml_capabilities:
                start_time = time.time()
                
                ensemble_manager = self.ml_capabilities['ensemble']
                ensemble_result = await ensemble_manager.predict_ensemble(data)
                ml_results["ensemble_prediction"] = ensemble_result
                ml_results["ml_enabled"] = True
                
                # Record performance metrics for monitoring
                latency_ms = (time.time() - start_time) * 1000
                self.ml_monitoring.record_performance_metric('ensemble', 'latency_ms', latency_ms)
                
                if ensemble_result.get('confidence', 0) > 0:
                    ensemble_confidence = ensemble_result.get('confidence', 0)
                    ensemble_direction = ensemble_result.get('direction', 0)
                    
                    # Record prediction accuracy metric
                    self.ml_monitoring.record_performance_metric('ensemble', 'confidence', ensemble_confidence)
                
                # Record error rate if prediction failed
                if 'error' in ensemble_result:
                    self.ml_monitoring.record_performance_metric('ensemble', 'error_rate', 1.0)
                else:
                    self.ml_monitoring.record_performance_metric('ensemble', 'error_rate', 0.0)
            
            # Calculate combined ML metrics
            if ml_results["ml_enabled"]:
                # Weighted combination of LSTM and Ensemble
                if lstm_confidence > 0 and ensemble_confidence > 0:
                    # Both models available - use weighted average
                    total_confidence = lstm_confidence + ensemble_confidence
                    lstm_weight = lstm_confidence / total_confidence
                    ensemble_weight = ensemble_confidence / total_confidence
                    
                    ml_results["ml_confidence"] = (lstm_confidence + ensemble_confidence) / 2
                    
                    # Direction based on agreement
                    if lstm_direction == ensemble_direction:
                        ml_results["ml_direction"] = lstm_direction
                        ml_results["ml_agreement"] = 1.0  # Perfect agreement
                    else:
                        # Disagreement - use the more confident model
                        if lstm_confidence > ensemble_confidence:
                            ml_results["ml_direction"] = lstm_direction
                        else:
                            ml_results["ml_direction"] = ensemble_direction
                        ml_results["ml_agreement"] = 0.0  # No agreement
                
                elif lstm_confidence > 0:
                    # Only LSTM available
                    ml_results["ml_confidence"] = lstm_confidence
                    ml_results["ml_direction"] = lstm_direction
                    ml_results["ml_agreement"] = 1.0  # Single model agreement
                
                elif ensemble_confidence > 0:
                    # Only Ensemble available
                    ml_results["ml_confidence"] = ensemble_confidence
                    ml_results["ml_direction"] = ensemble_direction
                    ml_results["ml_agreement"] = 1.0  # Single model agreement
            
            logger.debug(f"🤖 ML Analysis: {ml_results}")
            
        except Exception as e:
            logger.error(f"❌ ML analysis error: {e}")
            
        return ml_results
    
    async def _combine_analyses(self, trend, momentum, volatility, volume, patterns, ml_analysis=None) -> MarketAnalysis:
        """Combine all analyses into comprehensive market analysis"""
        try:
            # Determine overall trend
            trend_direction = trend.get("direction", "unknown")
            trend_strength = trend.get("strength", 0.0)
            
            # Adjust trend strength based on momentum and volume
            momentum_factor = 1.0
            if momentum.get("momentum") in ["bullish", "overbought"] and trend_direction == "up":
                momentum_factor = 1.2
            elif momentum.get("momentum") in ["bearish", "oversold"] and trend_direction == "down":
                momentum_factor = 1.2
            elif momentum.get("momentum") in ["overbought"] and trend_direction == "up":
                momentum_factor = 0.8  # Potential reversal
            elif momentum.get("momentum") in ["oversold"] and trend_direction == "down":
                momentum_factor = 0.8  # Potential reversal
            
            volume_factor = 1.0
            if volume.get("trend") == "increasing":
                volume_factor = 1.1  # Volume confirms trend
            elif volume.get("trend") == "decreasing":
                volume_factor = 0.9  # Weak volume
            
            adjusted_strength = min(1.0, trend_strength * momentum_factor * volume_factor)
            
            # Determine volatility level
            vol_level = volatility.get("level", "unknown")
            
            # Determine volume analysis
            vol_analysis = volume.get("trend", "unknown")
            
            # Create market analysis
            # Create comprehensive analysis including ML predictions
            analysis = MarketAnalysis(
                trend_direction=trend_direction,
                trend_strength=adjusted_strength,
                volatility_level=vol_level,
                volume_analysis=vol_analysis,
                key_levels=[]
            )
            
            # Add ML analysis as additional attributes
            if ml_analysis:
                analysis.ml_predictions = ml_analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis combination error: {e}")
            return MarketAnalysis(
                trend_direction="unknown",
                trend_strength=0.0,
                volatility_level="unknown",
                volume_analysis="unknown"
            )
    
    async def _generate_signal(self, analysis: MarketAnalysis, data: List[Dict[str, Any]], data_source: str = 'realtime') -> Optional[TradingSignal]:
        """Generate trading signal based on analysis - REAL DATA ONLY"""
        try:
            if not analysis or not data:
                logger.error("🚨 NO REAL DATA - Cannot generate signal without market data")
                return None
            
            current_price = data[-1]['close']
            
            # CRITICAL: Verify we have REAL market data, not cached/fake
            if current_price is None or current_price <= 0:
                logger.error("🚨 NO REAL DATA - Invalid price data, refusing to generate signal")
                return None
            
            # Check data freshness - only apply strict freshness check for real-time data
            if data_source == 'realtime':
                try:
                    last_timestamp = data[-1].get('timestamp')
                    if last_timestamp:
                        from datetime import datetime, timedelta
                        if isinstance(last_timestamp, str):
                            last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                        elif isinstance(last_timestamp, (int, float)):
                            # Handle Unix timestamp
                            last_time = datetime.fromtimestamp(last_timestamp)
                        else:
                            last_time = last_timestamp
                        
                        age_minutes = (datetime.now() - last_time.replace(tzinfo=None)).total_seconds() / 60
                        if age_minutes > 5:  # Data older than 5 minutes is stale for real-time
                            logger.error(f"🚨 STALE REAL-TIME DATA - Market data is {age_minutes:.1f} minutes old, refusing to generate signal")
                            return None
                except Exception as e:
                    logger.warning(f"Could not verify data freshness: {e}")
                    # If we can't verify freshness, err on the side of caution
                    return None
            else:
                # For historical data, log the data source and age for transparency
                try:
                    last_timestamp = data[-1].get('timestamp')
                    if last_timestamp:
                        from datetime import datetime, timedelta
                        if isinstance(last_timestamp, str):
                            last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                        elif isinstance(last_timestamp, (int, float)):
                            last_time = datetime.fromtimestamp(last_timestamp)
                        else:
                            last_time = last_timestamp
                        
                        age_hours = (datetime.now() - last_time.replace(tzinfo=None)).total_seconds() / 3600
                        logger.info(f"📈 Using {data_source} data from {age_hours:.1f} hours ago for weekend analysis")
                except Exception as e:
                    logger.info(f"📈 Using {data_source} data for weekend analysis (timestamp parse error: {e})")
            
            # Base signal logic
            signal_type = SignalType.HOLD
            confidence = 0.5
            reasoning = "Insufficient data for signal"
            
            # Trend-based signals
            if analysis.trend_direction == "up" and analysis.trend_strength > 0.6:
                if analysis.volume_analysis == "increasing":
                    signal_type = SignalType.STRONG_BUY if analysis.trend_strength > 0.8 else SignalType.BUY
                    confidence = min(0.95, 0.6 + analysis.trend_strength * 0.3)
                    reasoning = f"Strong upward trend (strength: {analysis.trend_strength:.1%}) with volume confirmation"
                else:
                    signal_type = SignalType.BUY
                    confidence = min(0.8, 0.5 + analysis.trend_strength * 0.3)
                    reasoning = f"Upward trend (strength: {analysis.trend_strength:.1%}) but weak volume"
            
            elif analysis.trend_direction == "down" and analysis.trend_strength > 0.6:
                if analysis.volume_analysis == "increasing":
                    signal_type = SignalType.STRONG_SELL if analysis.trend_strength > 0.8 else SignalType.SELL
                    confidence = min(0.95, 0.6 + analysis.trend_strength * 0.3)
                    reasoning = f"Strong downward trend (strength: {analysis.trend_strength:.1%}) with volume confirmation"
                else:
                    signal_type = SignalType.SELL
                    confidence = min(0.8, 0.5 + analysis.trend_strength * 0.3)
                    reasoning = f"Downward trend (strength: {analysis.trend_strength:.1%}) but weak volume"
            
            # Volatility adjustments
            if analysis.volatility_level == "high":
                confidence *= 0.8  # Reduce confidence in high volatility
                reasoning += " (high volatility reduces confidence)"
            elif analysis.volatility_level == "low":
                confidence *= 1.1  # Increase confidence in stable conditions
                reasoning += " (low volatility increases confidence)"
            
            # ML predictions enhancement (LSTM + Ensemble)
            ml_boost = 0.0
            if hasattr(analysis, 'ml_predictions') and analysis.ml_predictions:
                ml_pred = analysis.ml_predictions
                
                # Check ML prediction alignment
                if ml_pred.get('ml_enabled') and ml_pred.get('ml_confidence', 0) > 0.4:
                    ml_direction = ml_pred.get('ml_direction', 0)
                    ml_confidence = ml_pred.get('ml_confidence', 0)
                    ml_agreement = ml_pred.get('ml_agreement', 0)
                    
                    # Check if ML and traditional analysis agree
                    traditional_bullish = signal_type in [SignalType.BUY, SignalType.STRONG_BUY]
                    traditional_bearish = signal_type in [SignalType.SELL, SignalType.STRONG_SELL]
                    ml_bullish = ml_direction > 0
                    ml_bearish = ml_direction < 0
                    
                    if (traditional_bullish and ml_bullish) or (traditional_bearish and ml_bearish):
                        # Agreement between traditional and ML analysis
                        base_boost = ml_confidence * 0.20  # Up to 20% base boost
                        agreement_multiplier = 1.0 + (ml_agreement * 0.5)  # Up to 50% extra for model agreement
                        ml_boost = base_boost * agreement_multiplier
                        
                        # Add detailed reasoning
                        if ml_pred.get('lstm_prediction') and ml_pred.get('ensemble_prediction'):
                            reasoning += f" (LSTM+Ensemble confirm: {ml_confidence:.1%}, agreement: {ml_agreement:.1%})"
                        elif ml_pred.get('lstm_prediction'):
                            reasoning += f" (LSTM confirms: {ml_confidence:.1%})"
                        elif ml_pred.get('ensemble_prediction'):
                            reasoning += f" (Ensemble confirms: {ml_confidence:.1%})"
                            
                    elif ml_direction != 0:
                        # Disagreement - reduce confidence
                        ml_boost = -0.05 * (1.0 + ml_confidence)  # Stronger reduction for more confident disagreement
                        reasoning += f" (ML disagrees: {ml_confidence:.1%})"
                    
                    # Additional boost for high model agreement
                    if ml_agreement > 0.8:
                        ml_boost += 0.05  # Extra 5% for strong model agreement
                        reasoning += " (strong ML consensus)"
            
            # Apply ML boost
            confidence = min(0.98, confidence + ml_boost)
            
            # Don't generate weak signals
            if confidence < self.analysis_params["confidence_threshold"]:
                signal_type = SignalType.HOLD
                reasoning = f"Low confidence signal ({confidence:.1%}) - holding position"
            
            # Calculate target and stop loss (simplified)
            target_price = None
            stop_loss = None
            
            if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                target_price = current_price * 1.01  # 1% target
                stop_loss = current_price * 0.995    # 0.5% stop
            elif signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
                target_price = current_price * 0.99  # 1% target
                stop_loss = current_price * 1.005    # 0.5% stop
            
            signal = TradingSignal(
                signal=signal_type,
                confidence=min(0.95, confidence),  # Cap at 95%
                reasoning=reasoning,
                analysis_type=AnalysisType.TECHNICAL,
                target_price=target_price,
                stop_loss=stop_loss
            )
            
            # A/B Testing: Determine if this should use ML enhancements
            ab_test_group = self.ab_testing.assign_test_group({
                'signal_type': signal_type.name,
                'confidence': confidence,
                'current_price': current_price,
                'analysis_type': analysis.analysis_type.name if hasattr(analysis, 'analysis_type') else 'technical'
            })
            
            # Record signal for A/B testing
            signal_data = {
                'signal_type': signal_type.name,
                'confidence': confidence,
                'current_price': current_price,
                'reasoning': reasoning
            }
            
            # Apply A/B testing logic
            use_ml_enhancements = ab_test_group == 'ml_enhanced'
            
            # Add Kelly Criterion position sizing (based on A/B test group)
            if use_ml_enhancements and 'kelly' in self.ml_capabilities:
                try:
                    start_time = time.time()
                    
                    kelly_api = self.ml_capabilities['kelly']
                    
                    # Prepare signal for Kelly calculation
                    kelly_signal = {
                        'direction': 1 if signal_type in [SignalType.BUY, SignalType.STRONG_BUY] else -1 if signal_type in [SignalType.SELL, SignalType.STRONG_SELL] else 0,
                        'confidence': confidence,
                        'source': 'ai_brain_service'
                    }
                    
                    # Get position sizing recommendation (assume $100k capital for demo)
                    # In production, this would come from account management
                    capital = 100000  # TODO: Get from account service
                    
                    position_result = await kelly_api.calculate_position_size(
                        kelly_signal, capital, data[-30:] if len(data) >= 30 else data
                    )
                    
                    # Record performance metrics for monitoring
                    latency_ms = (time.time() - start_time) * 1000
                    self.ml_monitoring.record_performance_metric('kelly', 'latency_ms', latency_ms)
                    
                    # Add Kelly results to signal as additional attributes
                    signal.kelly_position_size = position_result.get('position_size', 0)
                    signal.kelly_position_pct = position_result.get('position_pct', 0)
                    signal.kelly_win_probability = position_result.get('win_probability', 0.5)
                    signal.kelly_method = position_result.get('method', 'unknown')
                    
                    # Record Kelly-specific metrics
                    self.ml_monitoring.record_performance_metric('kelly', 'win_rate', signal.kelly_win_probability)
                    self.ml_monitoring.record_performance_metric('kelly', 'position_pct', signal.kelly_position_pct)
                    self.ml_monitoring.record_performance_metric('kelly', 'error_rate', 0.0)
                    
                    # Update signal data for A/B testing
                    signal_data['position_size'] = signal.kelly_position_size
                    signal_data['kelly_enhanced'] = True
                    
                    logger.debug(f"Kelly sizing: {position_result.get('position_pct', 0):.1%} "
                               f"(${position_result.get('position_size', 0):.0f}) "
                               f"Win prob: {position_result.get('win_probability', 0.5):.1%}")
                    
                except Exception as e:
                    logger.warning(f"Kelly sizing calculation failed: {e}")
                    
                    # Record error metrics
                    self.ml_monitoring.record_performance_metric('kelly', 'error_rate', 1.0)
                    
                    # Add fallback Kelly attributes
                    signal.kelly_position_size = 0
                    signal.kelly_position_pct = 0
                    signal.kelly_win_probability = 0.5
                    signal.kelly_method = 'error'
                    signal_data['kelly_enhanced'] = False
            else:
                # Traditional position sizing (fixed percentage)
                capital = 100000
                fixed_position_pct = 0.02  # 2% fixed position
                signal.kelly_position_size = capital * fixed_position_pct
                signal.kelly_position_pct = fixed_position_pct
                signal.kelly_win_probability = 0.5
                signal.kelly_method = 'fixed_traditional'
                
                signal_data['position_size'] = signal.kelly_position_size
                signal_data['kelly_enhanced'] = False
            
            # Record the signal assignment for A/B testing
            test_id = self.ab_testing.record_signal(ab_test_group, signal_data)
            
            # Add A/B testing metadata to signal
            signal.ab_test_group = ab_test_group
            signal.ab_test_id = test_id
            signal.ml_enhanced = use_ml_enhancements
            
            # Add decision quality context for later evaluation
            signal.decision_quality_context = {
                'timeframes_analyzed': 1,  # Currently single timeframe
                'volume_analysis': analysis.volume_analysis,
                'indicators_used': ['trend', 'volume', 'volatility'],
                'market_regime': getattr(analysis, 'market_regime', None),
                'confidence_breakdown': {
                    'trend_component': analysis.trend_strength,
                    'volume_component': 1.0 if analysis.volume_analysis == "increasing" else 0.5,
                    'volatility_adjustment': 0.8 if analysis.volatility_level == "high" else 1.0
                },
                'pattern_context': "Technical analysis based on trend and volume",
                'market_session': self._get_market_session(),
                'volatility_assessment': analysis.volatility_level,
                'correlated_markets_checked': False,  # TODO: Implement
                'event_risk_considered': False  # TODO: Implement
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            return None
    
    def _get_market_session(self) -> str:
        """Determine current market session"""
        from datetime import datetime, time
        now = datetime.now().time()
        
        # US market hours (Eastern Time)
        pre_market = time(4, 0)
        market_open = time(9, 30)
        market_close = time(16, 0)
        after_hours = time(20, 0)
        
        if pre_market <= now < market_open:
            return "pre_market"
        elif market_open <= now < market_close:
            return "regular_hours"
        elif market_close <= now < after_hours:
            return "after_hours"
        else:
            return "closed"
    
    async def _signal_validation_loop(self):
        """Validate and track signal performance"""
        while self.running:
            try:
                # This would track signal performance over time
                # For now, just a placeholder
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Signal validation error: {e}")
                await asyncio.sleep(300)
    
    async def _performance_tracking_loop(self):
        """Track AI performance metrics"""
        while self.running:
            try:
                # Update performance metrics
                # This would track actual trading performance vs signals
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"❌ Performance tracking error: {e}")
                await asyncio.sleep(600)
    
    # Public API methods
    async def process_market_data(self, market_data: MarketData) -> None:
        """Process market data for analysis"""
        await self._on_market_data(market_data)
    
    def get_current_signal(self) -> Optional[TradingSignal]:
        """Get current trading signal"""
        return self.current_signal
    
    def get_current_analysis(self) -> Optional[MarketAnalysis]:
        """Get current market analysis"""
        return self.current_analysis
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get comprehensive AI status"""
        try:
            # Check if we have recent analysis
            is_connected = (
                self.last_analysis_time is not None and
                (datetime.now() - self.last_analysis_time).total_seconds() < 300
            )
            
            signal_data = None
            if self.current_signal:
                signal_data = {
                    "signal": self.current_signal.signal.value,
                    "confidence": self.current_signal.confidence,
                    "reasoning": self.current_signal.reasoning,
                    "timestamp": self.current_signal.timestamp
                }
            
            analysis_data = None
            if self.current_analysis:
                analysis_data = {
                    "trend_direction": self.current_analysis.trend_direction,
                    "trend_strength": self.current_analysis.trend_strength,
                    "volatility_level": self.current_analysis.volatility_level,
                    "volume_analysis": self.current_analysis.volume_analysis
                }
            
            # Add historical context information
            historical_info = {}
            if len(self.market_data_buffer) > 0:
                prices = [d['close'] for d in self.market_data_buffer if d['close'] is not None and d['close'] > 0]
                if prices:
                    historical_info = {
                        "min_price": min(prices),
                        "max_price": max(prices),
                        "avg_price": sum(prices) / len(prices),
                        "historical_range_days": len(self.market_data_buffer),
                        "has_historical_context": len(self.market_data_buffer) > 20
                    }
            
            return {
                "connected": is_connected,
                "signal": signal_data,
                "analysis": analysis_data,
                "data_points": len(self.market_data_buffer),
                "historical_context": historical_info,
                "last_analysis": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
                "stats": self.stats.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI status error: {e}")
            return {
                "connected": False,
                "signal": None,
                "analysis": None,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history"""
        return list(self.analysis_history)[-limit:]

class PatternDetector:
    """Simple pattern detection for market data"""
    
    def detect_patterns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect chart patterns in market data"""
        patterns = []
        
        try:
            if len(data) < 10:
                return patterns
            
            prices = [d['close'] for d in data if d['close'] is not None]
            
            if not prices or len(prices) < 10:
                return patterns
            
            # Simple breakout detection
            recent_high = max(prices[-10:-1])
            current_price = prices[-1]
            
            if current_price > recent_high * 1.002:  # 0.2% breakout
                patterns.append({
                    'type': 'breakout_up',
                    'confidence': 0.7,
                    'description': f'Price broke above recent high of {recent_high:.2f}'
                })
            
            recent_low = min(prices[-10:-1])
            if current_price < recent_low * 0.998:  # 0.2% breakdown
                patterns.append({
                    'type': 'breakdown',
                    'confidence': 0.7,
                    'description': f'Price broke below recent low of {recent_low:.2f}'
                })
            
        except Exception as e:
            logger.error(f"❌ Pattern detection error: {e}")
        
        return patterns

# Global AI Brain instance
_ai_brain_service: Optional[AIBrainService] = None

def get_ai_brain_service() -> AIBrainService:
    """Get global AI Brain service instance"""
    # First try to get running instance from live trading integration
    try:
        from .live_trading_integration import get_running_service
        running_instance = get_running_service('ai_brain')
        if running_instance:
            return running_instance
    except ImportError:
        pass
    
    # Fallback to singleton pattern
    global _ai_brain_service
    if _ai_brain_service is None:
        _ai_brain_service = AIBrainService()
    return _ai_brain_service

# Legacy compatibility function
def get_ai_status() -> Dict[str, Any]:
    """Legacy compatibility function for AI status"""
    ai_service = get_ai_brain_service()
    return ai_service.get_ai_status()

async def main():
    """Test the AI Brain Service"""
    ai_service = AIBrainService()
    
    try:
        await ai_service.start()
        logger.info("AI Brain Service running. Press Ctrl+C to stop...")
        
        # Keep running
        while ai_service.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await ai_service.stop()

if __name__ == "__main__":
    asyncio.run(main())