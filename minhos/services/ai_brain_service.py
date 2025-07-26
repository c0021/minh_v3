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
from collections import deque

# Import other services
from .sierra_client import get_sierra_client
from ..models.market import MarketData
from .state_manager import get_state_manager
from ..core.market_data_adapter import get_market_data_adapter
from .sierra_historical_data import get_sierra_historical_service

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
    Advanced AI analysis service for MinhOS v3
    Provides intelligent market analysis and trading signals
    """
    
    def __init__(self):
        """Initialize AI Brain Service"""
        self.running = False
        
        # Market data buffer for analysis
        self.market_data_buffer = deque(maxlen=1000)  # Store last 1000 data points
        self.analysis_history = deque(maxlen=100)     # Store last 100 analyses
        
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
        
        # Start analysis loops
        asyncio.create_task(self._analysis_loop())
        asyncio.create_task(self._signal_validation_loop())
        asyncio.create_task(self._performance_tracking_loop())
        
        logger.info("✅ AI Brain Service started")
    
    async def stop(self):
        """Stop the AI Brain Service"""
        logger.info("🛑 Stopping AI Brain Service...")
        self.running = False
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
            
            # Trigger analysis if we have enough data
            if len(self.market_data_buffer) >= 20:
                await self._perform_analysis()
                
        except Exception as e:
            logger.error(f"❌ Market data processing error: {e}")
    
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
            analysis_data = await self._get_analysis_data()
            if not analysis_data:
                return
            
            # Perform different types of analysis
            trend_analysis = await self._analyze_trend(analysis_data)
            momentum_analysis = await self._analyze_momentum(analysis_data)
            volatility_analysis = await self._analyze_volatility(analysis_data)
            volume_analysis = await self._analyze_volume(analysis_data)
            pattern_analysis = await self._analyze_patterns(analysis_data)
            
            # Combine analyses
            combined_analysis = await self._combine_analyses(
                trend_analysis, momentum_analysis, volatility_analysis, 
                volume_analysis, pattern_analysis
            )
            
            # Generate trading signal
            signal = await self._generate_signal(combined_analysis, analysis_data)
            
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
    
    async def _get_analysis_data(self) -> List[Dict[str, Any]]:
        """Get data for analysis - real-time or historical fallback"""
        try:
            # First, check if we have sufficient real-time data with volume
            if self.market_data_buffer:
                recent_data = list(self.market_data_buffer)[-self.analysis_params["trend_period"]:]
                
                # Check if recent data has sufficient volume
                recent_volumes = [d.get('volume', 0) for d in recent_data if d.get('volume', 0) > 0]
                avg_recent_volume = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0
                
                # If we have good volume data, use real-time
                if avg_recent_volume >= self.analysis_params["min_volume_threshold"]:
                    logger.info(f"📊 Using real-time data (avg volume: {avg_recent_volume:,.0f})")
                    return recent_data
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
                        return historical_data[-self.analysis_params["trend_period"]:]  # Last N periods
                        
                except Exception as e:
                    logger.error(f"❌ Error fetching historical data: {e}")
            
            # If no historical service or error, return what we have
            if self.market_data_buffer:
                logger.warning("⚠️ Using limited real-time data despite low volume")
                return list(self.market_data_buffer)[-self.analysis_params["trend_period"]:]
            
            logger.warning("❌ No data available for analysis")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting analysis data: {e}")
            return list(self.market_data_buffer)[-self.analysis_params["trend_period"]:] if self.market_data_buffer else []
    
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
    
    async def _combine_analyses(self, trend, momentum, volatility, volume, patterns) -> MarketAnalysis:
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
            analysis = MarketAnalysis(
                trend_direction=trend_direction,
                trend_strength=adjusted_strength,
                volatility_level=vol_level,
                volume_analysis=vol_analysis,
                key_levels=[]
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis combination error: {e}")
            return MarketAnalysis(
                trend_direction="unknown",
                trend_strength=0.0,
                volatility_level="unknown",
                volume_analysis="unknown"
            )
    
    async def _generate_signal(self, analysis: MarketAnalysis, data: List[Dict[str, Any]]) -> Optional[TradingSignal]:
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
            
            # Check data freshness - only trade on recent data
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
                    if age_minutes > 5:  # Data older than 5 minutes is stale
                        logger.error(f"🚨 STALE DATA - Market data is {age_minutes:.1f} minutes old, refusing to generate signal")
                        return None
            except Exception as e:
                logger.warning(f"Could not verify data freshness: {e}")
                # If we can't verify freshness, err on the side of caution
                return None
            
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