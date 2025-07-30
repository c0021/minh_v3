#!/usr/bin/env python3
"""
MinhOS v3 Pattern Analyzer (Migrated)
=====================================
Linux-native pattern recognition and learning system that continuously learns
from market behavior, trading outcomes, and system events to improve performance
and prevent issues.

MIGRATED: Now uses unified market data store instead of local buffer.
"""

import asyncio
import json
import sqlite3
import logging
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter, deque
from enum import Enum
import statistics
import numpy as np

# Import other services
from .sierra_client import get_sierra_client
from ..models.market import MarketData
from .state_manager import get_state_manager
from ..core.symbol_integration import SymbolIntegration

# Import unified market data store
from ..core.market_data_adapter import get_market_data_adapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pattern_analyzer")

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

class PatternAnalyzer:
    """
    Advanced pattern recognition and learning system
    Learns from market data, system events, and trading outcomes
    """
    
    def __init__(self, db_path: str = None):
        """Initialize Pattern Analyzer"""
        if db_path is None:
            # Move to permanent location in data directory
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "patterns.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.running = False
        
        # Centralized symbol management
        self.symbol_integration = SymbolIntegration()
        self.tradeable_symbols = self.symbol_integration.get_pattern_analyzer_symbols()
        self.symbol_integration.mark_service_migrated('pattern_analyzer')
        
        # MIGRATED: Replace market data buffer with unified store
        self.market_data_adapter = get_market_data_adapter()
        self.event_buffer = deque(maxlen=500)
        self.pattern_history = deque(maxlen=1000)
        
        # Pattern storage
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
        
        # Service references
        self.sierra_client = None
        self.state_manager = None
        
        # Analysis parameters
        self.analysis_params = {
            'min_pattern_occurrences': 3,
            'confidence_threshold': 0.6,
            'lookback_period': 100,
            'correlation_threshold': 0.7,
            'time_window_minutes': 60
        }
        
        # Statistics
        self.stats = {
            "patterns_detected": 0,
            "patterns_learned": 0,
            "predictions_made": 0,
            "prediction_accuracy": 0.0,
            "events_analyzed": 0,
            "correlations_found": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # Machine learning models (placeholder for future ML integration)
        self.ml_models = {}
        
        # Initialize database
        self._init_database()
        
        logger.info("🧠 Pattern Analyzer initialized")
    
    def _init_database(self):
        """Initialize SQLite database for pattern storage"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Enable WAL mode for better concurrent access
                cursor.execute("PRAGMA journal_mode=WAL")
                
                # Patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT,
                        description TEXT,
                        confidence REAL,
                        context TEXT,
                        market_conditions TEXT,
                        suggestions TEXT,
                        first_seen TEXT,
                        last_seen TEXT,
                        occurrences INTEGER,
                        success_rate REAL
                    )
                ''')
                
                # Events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS learning_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT,
                        context TEXT,
                        outcome TEXT,
                        success BOOLEAN,
                        timestamp TEXT,
                        patterns_detected TEXT
                    )
                ''')
                
                # Pattern correlations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pattern_correlations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_a TEXT,
                        pattern_b TEXT,
                        correlation REAL,
                        occurrences INTEGER,
                        updated_at TEXT
                    )
                ''')
                
                # Market conditions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_conditions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        regime TEXT,
                        volatility REAL,
                        volume_profile TEXT,
                        trend_strength REAL,
                        conditions TEXT
                    )
                ''')
                
                # Predictions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        pattern_type TEXT,
                        prediction TEXT,
                        confidence REAL,
                        actual_outcome TEXT,
                        correct BOOLEAN,
                        market_conditions TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Pattern database initialized")
                
        except Exception as e:
            logger.error(f"❌ Pattern database initialization failed: {e}")
            raise
    
    async def start(self):
        """Start the Pattern Analyzer"""
        logger.info("🚀 Starting Pattern Analyzer...")
        self.running = True
        
        # Initialize service references
        self.sierra_client = get_sierra_client()
        self.state_manager = get_state_manager()
        
        # MIGRATED: Subscribe to unified market data store
        await self.market_data_adapter.start()
        await self.market_data_adapter.subscribe(self._on_market_data_update)
        
        # Load existing patterns
        await self._load_patterns()
        
        # Start analysis loops
        asyncio.create_task(self._pattern_detection_loop())
        asyncio.create_task(self._correlation_analysis_loop())
        asyncio.create_task(self._prediction_validation_loop())
        asyncio.create_task(self._learning_loop())
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Pattern Analyzer started")
    
    async def stop(self):
        """Stop the Pattern Analyzer"""
        logger.info("🛑 Stopping Pattern Analyzer...")
        self.running = False
        
        # Save current patterns
        await self._save_patterns()
        
        logger.info("Pattern Analyzer stopped")
    
    async def _on_market_data_update(self, market_data):
        """MIGRATED: Handle market data updates from unified store"""
        try:
            # Handle both MarketData objects and dictionaries
            if isinstance(market_data, dict):
                symbol = market_data.get('symbol', 'UNKNOWN')
            else:
                symbol = getattr(market_data, 'symbol', 'UNKNOWN')
            
            # Detect patterns in real-time using data from unified store
            await self._detect_realtime_patterns()
            
            logger.debug(f"📊 Pattern analysis updated for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Market data processing error: {e}")
    
    async def _pattern_detection_loop(self):
        """Main pattern detection loop"""
        while self.running:
            try:
                # MIGRATED: Get data from unified store for pattern detection
                symbols = self.market_data_adapter.get_symbols()
                if symbols:
                    # Get historical data for analysis
                    all_data_points = []
                    for symbol in symbols:
                        history = self.market_data_adapter.get_historical_data(symbol, limit=50)
                        # Convert to format expected by existing pattern detection
                        for md in history:
                            data_point = {
                                'timestamp': md.timestamp,
                                'symbol': md.symbol,
                                'close': md.close,
                                'bid': md.bid,
                                'ask': md.ask,
                                'volume': md.volume,
                                'high': getattr(md, 'high', md.close),
                                'low': getattr(md, 'low', md.close),
                                'source': md.source
                            }
                            all_data_points.append(data_point)
                    
                    if len(all_data_points) >= 50:
                        patterns = await self._detect_all_patterns_with_data(all_data_points)
                        
                        for pattern in patterns:
                            await self._process_detected_pattern(pattern)
                
                await asyncio.sleep(60)  # Analyze every minute
                
            except Exception as e:
                logger.error(f"❌ Pattern detection error: {e}")
                await asyncio.sleep(60)
    
    async def _detect_realtime_patterns(self):
        """MIGRATED: Detect patterns in real-time using unified store"""
        try:
            # Get recent data from unified store
            symbols = self.market_data_adapter.get_symbols()
            if not symbols:
                return
            
            all_recent_data = []
            for symbol in symbols:
                history = self.market_data_adapter.get_historical_data(symbol, limit=20)
                # Convert to format expected by existing pattern detection
                for md in history:
                    data_point = {
                        'timestamp': md.timestamp,
                        'symbol': md.symbol,
                        'close': md.close,
                        'bid': md.bid,
                        'ask': md.ask,
                        'volume': md.volume,
                        'high': getattr(md, 'high', md.close),
                        'low': getattr(md, 'low', md.close),
                        'source': md.source
                    }
                    all_recent_data.append(data_point)
            
            if len(all_recent_data) < 20:
                return
            
            # Quick pattern detection
            patterns = []
            
            # Price breakout detection
            breakout_pattern = await self._detect_price_breakout(all_recent_data)
            if breakout_pattern:
                patterns.append(breakout_pattern)
            
            # Volume spike detection
            volume_pattern = await self._detect_volume_spike(all_recent_data)
            if volume_pattern:
                patterns.append(volume_pattern)
            
            # Process detected patterns
            for pattern in patterns:
                await self._process_detected_pattern(pattern)
                
        except Exception as e:
            logger.error(f"❌ Real-time pattern detection error: {e}")
    
    async def _detect_all_patterns_with_data(self, data: List[Dict]) -> List[DetectedPattern]:
        """MIGRATED: Detect all types of patterns in provided market data"""
        patterns = []
        
        try:
            if len(data) < 50:
                return patterns
            
            # Market patterns
            patterns.extend(await self._detect_price_patterns(data))
            patterns.extend(await self._detect_volume_patterns(data))
            patterns.extend(await self._detect_volatility_patterns(data))
            patterns.extend(await self._detect_trend_patterns(data))
            patterns.extend(await self._detect_support_resistance(data))
            
            # System patterns (if we have system events)
            patterns.extend(await self._detect_system_patterns())
            
        except Exception as e:
            logger.error(f"❌ Pattern detection error: {e}")
        
        return patterns
    
    async def _detect_price_patterns(self, data: List[Dict[str, Any]]) -> List[DetectedPattern]:
        """Detect price-based patterns"""
        patterns = []
        
        try:
            if len(data) < 20:
                return patterns
            
            prices = [d['close'] for d in data[-50:]]
            
            # Breakout pattern
            recent_high = max(prices[-20:-1])
            current_price = prices[-1]
            
            if current_price > recent_high * 1.005:  # 0.5% breakout
                pattern = DetectedPattern(
                    pattern_type=PatternType.PRICE_BREAKOUT,
                    confidence=0.8,
                    description=f"Price breakout above {recent_high:.2f}",
                    context={
                        'breakout_level': recent_high,
                        'current_price': current_price,
                        'strength': (current_price - recent_high) / recent_high
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions(),
                    suggestions=["Consider long entry", "Monitor for continuation", "Set tight stops"]
                )
                patterns.append(pattern)
            
            # Breakdown pattern
            recent_low = min(prices[-20:-1])
            if current_price < recent_low * 0.995:  # 0.5% breakdown
                pattern = DetectedPattern(
                    pattern_type=PatternType.PRICE_BREAKDOWN,
                    confidence=0.8,
                    description=f"Price breakdown below {recent_low:.2f}",
                    context={
                        'breakdown_level': recent_low,
                        'current_price': current_price,
                        'strength': (recent_low - current_price) / recent_low
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions(),
                    suggestions=["Consider short entry", "Monitor for continuation", "Set tight stops"]
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Price pattern detection error: {e}")
        
        return patterns
    
    async def _detect_volume_patterns(self, data: List[Dict[str, Any]]) -> List[DetectedPattern]:
        """Detect volume-based patterns"""
        patterns = []
        
        try:
            volumes = [d.get('volume', 0) for d in data[-50:] if d.get('volume', 0) > 0]
            
            if len(volumes) < 20:
                return patterns
            
            avg_volume = statistics.mean(volumes[:-1])
            current_volume = volumes[-1]
            
            # Volume spike detection
            if current_volume > avg_volume * 2.0:  # 2x average volume
                pattern = DetectedPattern(
                    pattern_type=PatternType.VOLUME_SPIKE,
                    confidence=0.7,
                    description=f"Volume spike: {current_volume:.0f} vs {avg_volume:.0f} average",
                    context={
                        'current_volume': current_volume,
                        'average_volume': avg_volume,
                        'spike_ratio': current_volume / avg_volume
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions(),
                    suggestions=["Expect increased volatility", "Monitor price action", "Potential trend change"]
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Volume pattern detection error: {e}")
        
        return patterns
    
    async def _detect_volatility_patterns(self, data: List[Dict[str, Any]]) -> List[DetectedPattern]:
        """Detect volatility-based patterns"""
        patterns = []
        
        try:
            if len(data) < 30:
                return patterns
            
            prices = [d['close'] for d in data[-30:]]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            
            current_vol = statistics.stdev(returns[-10:]) if len(returns) >= 10 else 0
            historical_vol = statistics.stdev(returns) if len(returns) > 1 else 0
            
            # Volatility expansion
            if current_vol > historical_vol * 1.5:  # 50% increase in volatility
                pattern = DetectedPattern(
                    pattern_type=PatternType.VOLATILITY_EXPANSION,
                    confidence=0.75,
                    description=f"Volatility expansion: {current_vol:.4f} vs {historical_vol:.4f}",
                    context={
                        'current_volatility': current_vol,
                        'historical_volatility': historical_vol,
                        'expansion_ratio': current_vol / historical_vol if historical_vol > 0 else 0
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions(),
                    suggestions=["Reduce position sizes", "Widen stops", "Expect larger moves"]
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Volatility pattern detection error: {e}")
        
        return patterns
    
    async def _detect_trend_patterns(self, data: List[Dict[str, Any]]) -> List[DetectedPattern]:
        """Detect trend-based patterns"""
        patterns = []
        
        try:
            if len(data) < 30:
                return patterns
            
            prices = [d['close'] for d in data[-30:]]
            
            # Simple trend analysis
            sma_short = statistics.mean(prices[-10:])
            sma_long = statistics.mean(prices[-20:])
            
            # Trend reversal detection
            recent_trend = (prices[-1] - prices[-10]) / prices[-10] if prices[-10] != 0 else 0
            longer_trend = (prices[-10] - prices[-20]) / prices[-20] if prices[-20] != 0 else 0
            
            if abs(recent_trend) > 0.02 and recent_trend * longer_trend < 0:  # Trend reversal
                pattern = DetectedPattern(
                    pattern_type=PatternType.TREND_REVERSAL,
                    confidence=0.65,
                    description=f"Potential trend reversal detected",
                    context={
                        'recent_trend': recent_trend,
                        'longer_trend': longer_trend,
                        'sma_short': sma_short,
                        'sma_long': sma_long
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions(),
                    suggestions=["Wait for confirmation", "Consider counter-trend", "Monitor closely"]
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Trend pattern detection error: {e}")
        
        return patterns
    
    async def _detect_support_resistance(self, data: List[Dict[str, Any]]) -> List[DetectedPattern]:
        """Detect support and resistance levels"""
        patterns = []
        
        try:
            if len(data) < 50:
                return patterns
            
            prices = [d['close'] for d in data[-50:]]
            highs = [d.get('high', d['close']) for d in data[-50:]]
            lows = [d.get('low', d['close']) for d in data[-50:]]
            
            # Simple support/resistance detection
            # Find price levels that have been tested multiple times
            current_price = prices[-1]
            
            # Look for levels within 1% that have been touched multiple times
            level_tests = defaultdict(int)
            
            for price in prices[:-5]:  # Exclude very recent prices
                price_level = round(price, 0)  # Round to nearest dollar
                if abs(price_level - current_price) / current_price < 0.05:  # Within 5%
                    level_tests[price_level] += 1
            
            # Find levels tested 3+ times
            for level, tests in level_tests.items():
                if tests >= 3:
                    level_type = "resistance" if level > current_price else "support"
                    
                    pattern = DetectedPattern(
                        pattern_type=PatternType.SUPPORT_RESISTANCE,
                        confidence=min(0.9, 0.5 + tests * 0.1),
                        description=f"{level_type.title()} level at {level:.0f} (tested {tests} times)",
                        context={
                            'level': level,
                            'type': level_type,
                            'tests': tests,
                            'current_price': current_price,
                            'distance_pct': abs(level - current_price) / current_price
                        },
                        timestamp=datetime.now(),
                        market_conditions=await self._get_current_market_conditions(),
                        suggestions=[f"Watch for {level_type} at {level:.0f}", "Plan entry/exit around level"]
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Support/resistance detection error: {e}")
        
        return patterns
    
    async def _detect_system_patterns(self) -> List[DetectedPattern]:
        """Detect system-related patterns"""
        patterns = []
        
        try:
            # This would analyze system performance, connectivity, etc.
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ System pattern detection error: {e}")
        
        return patterns
    
    async def _detect_price_breakout(self, data: List[Dict[str, Any]]) -> Optional[DetectedPattern]:
        """Quick breakout detection for real-time processing"""
        try:
            if len(data) < 10:
                return None
            
            prices = [d['close'] for d in data]
            recent_high = max(prices[:-1])
            current_price = prices[-1]
            
            if current_price > recent_high * 1.003:  # 0.3% breakout
                return DetectedPattern(
                    pattern_type=PatternType.PRICE_BREAKOUT,
                    confidence=0.7,
                    description=f"Real-time breakout above {recent_high:.2f}",
                    context={
                        'breakout_level': recent_high,
                        'current_price': current_price
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions()
                )
            
        except Exception:
            pass
        
        return None
    
    async def _detect_volume_spike(self, data: List[Dict[str, Any]]) -> Optional[DetectedPattern]:
        """Quick volume spike detection for real-time processing"""
        try:
            volumes = [d.get('volume', 0) for d in data if d.get('volume', 0) > 0]
            
            if len(volumes) < 10:
                return None
            
            avg_volume = statistics.mean(volumes[:-1])
            current_volume = volumes[-1]
            
            if current_volume > avg_volume * 1.8:  # 80% above average
                return DetectedPattern(
                    pattern_type=PatternType.VOLUME_SPIKE,
                    confidence=0.6,
                    description=f"Real-time volume spike: {current_volume:.0f}",
                    context={
                        'current_volume': current_volume,
                        'average_volume': avg_volume
                    },
                    timestamp=datetime.now(),
                    market_conditions=await self._get_current_market_conditions()
                )
            
        except Exception:
            pass
        
        return None
    
    async def _process_detected_pattern(self, pattern: DetectedPattern):
        """Process and store a detected pattern"""
        try:
            self.pattern_history.append(pattern)
            self.stats["patterns_detected"] += 1
            
            # Store in database
            await self._save_pattern_to_db(pattern)
            
            # Learn from pattern
            await self._learn_from_pattern(pattern)
            
            # Update correlations
            await self._update_pattern_correlations(pattern)
            
            logger.info(f"🔍 Pattern detected: {pattern.pattern_type.value} (confidence: {pattern.confidence:.1%})")
            logger.debug(f"   Description: {pattern.description}")
            
        except Exception as e:
            logger.error(f"❌ Pattern processing error: {e}")
    
    async def _correlation_analysis_loop(self):
        """Analyze correlations between patterns"""
        while self.running:
            try:
                await self._analyze_pattern_correlations()
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Correlation analysis error: {e}")
                await asyncio.sleep(300)
    
    async def _prediction_validation_loop(self):
        """Validate previous predictions"""
        while self.running:
            try:
                await self._validate_predictions()
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"❌ Prediction validation error: {e}")
                await asyncio.sleep(600)
    
    async def _learning_loop(self):
        """Main learning loop"""
        while self.running:
            try:
                # Learn from recent events
                await self._process_learning_events()
                
                # Update pattern success rates
                await self._update_pattern_success_rates()
                
                await asyncio.sleep(900)  # Every 15 minutes
                
            except Exception as e:
                logger.error(f"❌ Learning loop error: {e}")
                await asyncio.sleep(900)
    
    async def _cleanup_loop(self):
        """Cleanup old data and optimize database"""
        while self.running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _get_current_market_conditions(self) -> Dict[str, Any]:
        """MIGRATED: Get current market conditions from unified store"""
        try:
            symbols = self.market_data_adapter.get_symbols()
            if not symbols:
                return {}
            
            all_recent_data = []
            for symbol in symbols:
                history = self.market_data_adapter.get_historical_data(symbol, limit=20)
                all_recent_data.extend(history)
            
            if not all_recent_data:
                return {}
            
            prices = [md.close for md in all_recent_data]
            
            if len(prices) < 10:
                return {}
            
            # Calculate basic market conditions
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = statistics.stdev(returns) if len(returns) > 1 else 0
            trend = (prices[-1] - prices[0]) / prices[0] if prices[0] != 0 else 0
            
            return {
                'volatility': volatility,
                'trend': trend,
                'current_price': prices[-1],
                'price_range': max(prices) - min(prices),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Market conditions error: {e}")
            return {}
    
    async def _save_pattern_to_db(self, pattern: DetectedPattern):
        """Save detected pattern to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO patterns 
                    (pattern_type, description, confidence, context, market_conditions, 
                     suggestions, first_seen, last_seen, occurrences, success_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.pattern_type.value,
                    pattern.description,
                    pattern.confidence,
                    json.dumps(pattern.context),
                    json.dumps(pattern.market_conditions),
                    json.dumps(pattern.suggestions),
                    pattern.timestamp.isoformat(),
                    pattern.timestamp.isoformat(),
                    1,
                    0.0  # Initial success rate
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Pattern save error: {e}")
    
    async def _learn_from_pattern(self, pattern: DetectedPattern):
        """Learn from detected pattern"""
        try:
            # Update known patterns
            pattern_key = f"{pattern.pattern_type.value}_{pattern.description}"
            
            if pattern_key not in self.known_patterns:
                self.known_patterns[pattern_key] = {
                    'count': 0,
                    'total_confidence': 0,
                    'outcomes': [],
                    'contexts': []
                }
            
            self.known_patterns[pattern_key]['count'] += 1
            self.known_patterns[pattern_key]['total_confidence'] += pattern.confidence
            self.known_patterns[pattern_key]['contexts'].append(pattern.context)
            
            self.stats["patterns_learned"] += 1
            
        except Exception as e:
            logger.error(f"❌ Pattern learning error: {e}")
    
    async def _update_pattern_correlations(self, pattern: DetectedPattern):
        """Update correlations between patterns"""
        try:
            # Find patterns that occurred around the same time
            recent_patterns = [
                p for p in self.pattern_history 
                if abs((p.timestamp - pattern.timestamp).total_seconds()) < 3600  # Within 1 hour
            ]
            
            for other_pattern in recent_patterns:
                if other_pattern.pattern_type != pattern.pattern_type:
                    key = f"{pattern.pattern_type.value}_{other_pattern.pattern_type.value}"
                    
                    if key not in self.pattern_correlations:
                        self.pattern_correlations[key] = {}
                    
                    if 'count' not in self.pattern_correlations[key]:
                        self.pattern_correlations[key]['count'] = 0
                    
                    self.pattern_correlations[key]['count'] += 1
            
        except Exception as e:
            logger.error(f"❌ Correlation update error: {e}")
    
    async def _analyze_pattern_correlations(self):
        """Analyze correlations between different patterns"""
        try:
            # This would perform more sophisticated correlation analysis
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Correlation analysis error: {e}")
    
    async def _validate_predictions(self):
        """Validate previous predictions against actual outcomes"""
        try:
            # This would check previous predictions against actual market movements
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Prediction validation error: {e}")
    
    async def _process_learning_events(self):
        """Process events for learning"""
        try:
            # This would process trading outcomes, system events, etc.
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Learning events processing error: {e}")
    
    async def _update_pattern_success_rates(self):
        """Update success rates for known patterns"""
        try:
            # This would track pattern success rates over time
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Success rate update error: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old data from database"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Clean old events
                cursor.execute("DELETE FROM learning_events WHERE timestamp < ?", (cutoff_date,))
                
                # Clean old market conditions
                cursor.execute("DELETE FROM market_conditions WHERE timestamp < ?", (cutoff_date,))
                
                # Clean old predictions
                cursor.execute("DELETE FROM predictions WHERE timestamp < ?", (cutoff_date,))
                
                conn.commit()
                
            logger.debug("🧹 Pattern database cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
    
    async def _load_patterns(self):
        """Load existing patterns from database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM patterns WHERE confidence > ?", (0.5,))
                
                for row in cursor.fetchall():
                    # Load pattern data
                    pattern_key = f"{row[1]}_{row[2]}"  # pattern_type_description
                    
                    self.known_patterns[pattern_key] = {
                        'count': row[9] or 0,  # occurrences
                        'total_confidence': 0,
                        'outcomes': [],
                        'contexts': [json.loads(row[4])] if row[4] else [],
                        'success_rate': row[10] or 0.0
                    }
                
                logger.info(f"✅ Loaded {len(self.known_patterns)} known patterns")
                
        except Exception as e:
            logger.error(f"❌ Pattern loading error: {e}")
    
    async def _save_patterns(self):
        """Save current patterns to database"""
        try:
            # Update pattern statistics in database
            # For now, just log
            logger.debug("💾 Saving pattern updates to database")
            
        except Exception as e:
            logger.error(f"❌ Pattern saving error: {e}")
    
    # Public API methods
    def get_recent_patterns(self, limit: int = 10) -> List[DetectedPattern]:
        """Get recently detected patterns"""
        return list(self.pattern_history)[-limit:]
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get pattern analysis statistics"""
        return {
            "total_patterns": len(self.known_patterns),
            "recent_patterns": len(self.pattern_history),
            "correlations_tracked": len(self.pattern_correlations),
            "stats": self.stats.copy(),
            "analysis_params": self.analysis_params.copy()
        }
    
    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights from pattern analysis"""
        try:
            # Most common patterns
            pattern_counts = {}
            for pattern in self.pattern_history:
                pattern_type = pattern.pattern_type.value
                pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
            
            most_common = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "most_common_patterns": most_common,
                "total_patterns_detected": self.stats["patterns_detected"],
                "patterns_learned": self.stats["patterns_learned"],
                "prediction_accuracy": self.stats["prediction_accuracy"],
                "analysis_active": self.running,
                "data_points": len(self.market_data_adapter.get_symbols()),  # MIGRATED: Show symbol count instead
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Pattern insights error: {e}")
            return {"error": str(e)}

# Global pattern analyzer instance
_pattern_analyzer: Optional[PatternAnalyzer] = None

def get_pattern_analyzer() -> PatternAnalyzer:
    """Get global pattern analyzer instance"""
    global _pattern_analyzer
    if _pattern_analyzer is None:
        _pattern_analyzer = PatternAnalyzer()
    return _pattern_analyzer

async def main():
    """Test the Pattern Analyzer"""
    analyzer = PatternAnalyzer()
    
    try:
        await analyzer.start()
        logger.info("Pattern Analyzer running. Press Ctrl+C to stop...")
        
        # Keep running
        while analyzer.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await analyzer.stop()

if __name__ == "__main__":
    asyncio.run(main())