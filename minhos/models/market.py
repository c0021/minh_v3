#!/usr/bin/env python3
"""
MinhOS v3 Market Data Models
===========================

Unified data models for market data across the trading system.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class MarketData:
    """
    Unified market data model for the trading system.
    
    This model is used by the unified market data store and all services.
    Supports both real-time tick data and aggregated bar data.
    """
    symbol: str
    timestamp: float  # Unix timestamp for consistency
    close: float      # Current/close price
    
    # Optional OHLC data (for bars)
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    
    # Market microstructure
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    last_size: Optional[int] = None
    
    # Volume and trade data
    volume: Optional[int] = None
    vwap: Optional[float] = None
    trades: Optional[int] = None
    
    # Metadata
    source: Optional[str] = None
    
    def __post_init__(self):
        """Validate and set defaults after initialization"""
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.source is None:
            self.source = "unknown"
        
        # Set OHLC defaults if not provided
        if self.open is None:
            self.open = self.close
        if self.high is None:
            self.high = self.close
        if self.low is None:
            self.low = self.close
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketData':
        """Create MarketData from dictionary (for API compatibility)"""
        return cls(
            symbol=data.get('symbol', 'UNKNOWN'),
            timestamp=float(data.get('timestamp', time.time())),
            close=float(data.get('close', data.get('price', 0))),
            open=data.get('open'),
            high=data.get('high'),
            low=data.get('low'),
            bid=data.get('bid'),
            ask=data.get('ask'),
            bid_size=data.get('bid_size'),
            ask_size=data.get('ask_size'),
            last_size=data.get('last_size'),
            volume=data.get('volume'),
            vwap=data.get('vwap'),
            trades=data.get('trades'),
            source=data.get('source')
        )
    
    @classmethod
    def from_sierra_data(cls, data: Dict[str, Any]) -> 'MarketData':
        """Create MarketData from Sierra Chart data format"""
        return cls(
            symbol=data.get('symbol', ''),
            timestamp=time.time(),  # Sierra sends string timestamps, we use current time
            close=float(data.get('price', data.get('close', 0))),
            bid=float(data.get('bid', 0)) if data.get('bid') else None,
            ask=float(data.get('ask', 0)) if data.get('ask') else None,
            volume=int(data.get('volume', 0)) if data.get('volume') else None,
            source='sierra_chart'
        )
    
    @property
    def price(self) -> float:
        """Alias for close price (for backward compatibility)"""
        return self.close
    
    @property
    def spread(self) -> Optional[float]:
        """Calculate bid-ask spread"""
        if self.bid is not None and self.ask is not None:
            return self.ask - self.bid
        return None
    
    @property
    def midpoint(self) -> Optional[float]:
        """Calculate bid-ask midpoint"""
        if self.bid is not None and self.ask is not None:
            return (self.bid + self.ask) / 2.0
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding None values)"""
        result = asdict(self)
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class MarketDataPoint:
    """
    Legacy market data model for backward compatibility.
    Used by StateManager and other services that expect ISO timestamp strings.
    """
    symbol: str
    close: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[int] = None
    timestamp: str = ""
    source: str = "unknown"
    received_at: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.received_at:
            self.received_at = datetime.now().isoformat()
    
    @classmethod
    def from_market_data(cls, md: MarketData) -> 'MarketDataPoint':
        """Convert from unified MarketData to legacy format"""
        return cls(
            symbol=md.symbol,
            close=md.close,
            bid=md.bid,
            ask=md.ask,
            volume=md.volume,
            timestamp=datetime.fromtimestamp(md.timestamp).isoformat() if md.timestamp else "",
            source=md.source or "unknown",
            received_at=datetime.now().isoformat()
        )


@dataclass
class MultiChartData:
    """Comprehensive multi-chart market data"""
    timestamp: str
    primary_symbol: str = "NQU25-CME"
    
    # NQ Data (multiple timeframes)
    nq_1min: Optional[MarketData] = None
    nq_30min: Optional[MarketData] = None  
    nq_daily: Optional[MarketData] = None
    
    # ES Data
    es_1min: Optional[MarketData] = None
    
    # VIX Data  
    vix_1min: Optional[MarketData] = None
    
    # Derived Analytics
    nq_es_spread: Optional[float] = None
    vix_level: Optional[str] = None  # LOW, NORMAL, HIGH, EXTREME
    market_regime: Optional[str] = None  # TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE
    timeframe_alignment: Optional[str] = None  # BULLISH, BEARISH, MIXED, NEUTRAL


@dataclass  
class ChartConfiguration:
    """Configuration for each chart"""
    symbol: str
    timeframe: str
    primary: bool = False
    weight: float = 1.0
    enabled: bool = True


# Legacy imports for backward compatibility
__all__ = [
    'MarketData',
    'MarketDataPoint',
    'MultiChartData', 
    'ChartConfiguration'
]