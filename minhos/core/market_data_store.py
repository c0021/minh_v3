#!/usr/bin/env python3
"""
Unified Market Data Store
========================

Single source of truth for all market data in MinhOS v3.
Provides high-performance data access with SQLite persistence.
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Deque
from collections import deque, defaultdict
import threading
import json
from dataclasses import dataclass, asdict
import logging

from ..models.market import MarketData


logger = logging.getLogger(__name__)


@dataclass
class MarketDataConfig:
    """Configuration for market data storage"""
    db_path: Path
    max_memory_records: int = 1000  # Per symbol
    retention_days: int = 30
    cleanup_interval: int = 3600  # 1 hour
    enable_compression: bool = True
    enable_wal_mode: bool = True


class MarketDataStore:
    """
    Unified market data storage with:
    - In-memory cache for recent data
    - SQLite persistence for historical data
    - Automatic cleanup and compression
    - Thread-safe operations
    """
    
    def __init__(self, config: MarketDataConfig):
        self.config = config
        self._lock = threading.RLock()
        self._memory_cache: Dict[str, Deque[MarketData]] = defaultdict(
            lambda: deque(maxlen=config.max_memory_records)
        )
        self._latest_data: Dict[str, MarketData] = {}
        self._subscribers: List[asyncio.Queue] = []
        self._cleanup_task = None
        
        # Initialize database
        self._init_database()
        
        # Load recent data into memory
        self._load_recent_data()
        
        logger.info(f"Market data store initialized at {config.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with optimized settings"""
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(self.config.db_path)) as conn:
            if self.config.enable_wal_mode:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL NOT NULL,
                    volume INTEGER,
                    bid REAL,
                    ask REAL,
                    bid_size INTEGER,
                    ask_size INTEGER,
                    last_size INTEGER,
                    vwap REAL,
                    trades INTEGER,
                    source TEXT,
                    metadata TEXT,
                    created_at REAL DEFAULT (julianday('now'))
                )
            """)
            
            # Create indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
                ON market_data(symbol, timestamp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_market_data_created_at
                ON market_data(created_at)
            """)
            
            # Create aggregated data table for faster queries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data_1min (
                    symbol TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER,
                    vwap REAL,
                    trades INTEGER,
                    PRIMARY KEY (symbol, timestamp)
                )
            """)
            
            conn.commit()
    
    def _load_recent_data(self):
        """Load recent data from database into memory cache"""
        cutoff = datetime.now().timestamp() - (24 * 3600)  # Last 24 hours
        
        with sqlite3.connect(str(self.config.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM market_data 
                WHERE timestamp > ? 
                ORDER BY symbol, timestamp DESC
                LIMIT ?
            """, (cutoff, self.config.max_memory_records * 10))
            
            for row in cursor:
                market_data = self._row_to_market_data(row)
                if market_data:
                    self._memory_cache[market_data.symbol].appendleft(market_data)
                    
                    # Update latest data
                    if (market_data.symbol not in self._latest_data or 
                        market_data.timestamp > self._latest_data[market_data.symbol].timestamp):
                        self._latest_data[market_data.symbol] = market_data
    
    def _row_to_market_data(self, row: sqlite3.Row) -> Optional[MarketData]:
        """Convert database row to MarketData object"""
        try:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            return MarketData(
                symbol=row['symbol'],
                timestamp=row['timestamp'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
                bid=row['bid'],
                ask=row['ask'],
                bid_size=row['bid_size'],
                ask_size=row['ask_size'],
                last_size=row['last_size'],
                vwap=row['vwap'],
                trades=row['trades'],
                source=row['source'],
                **metadata
            )
        except Exception as e:
            logger.error(f"Error converting row to MarketData: {e}")
            return None
    
    async def add(self, data: MarketData) -> None:
        """Add new market data point"""
        with self._lock:
            # Update memory cache
            self._memory_cache[data.symbol].append(data)
            self._latest_data[data.symbol] = data
            
            # Persist to database
            self._persist_data(data)
            
            # Notify subscribers
            await self._notify_subscribers(data)
    
    def _persist_data(self, data: MarketData):
        """Persist market data to SQLite"""
        try:
            # Extract base fields and metadata
            base_fields = {
                'symbol', 'timestamp', 'open', 'high', 'low', 'close',
                'volume', 'bid', 'ask', 'bid_size', 'ask_size', 
                'last_size', 'vwap', 'trades', 'source'
            }
            
            data_dict = asdict(data)
            base_data = {k: v for k, v in data_dict.items() if k in base_fields}
            metadata = {k: v for k, v in data_dict.items() if k not in base_fields}
            
            with sqlite3.connect(str(self.config.db_path)) as conn:
                conn.execute("""
                    INSERT INTO market_data 
                    (symbol, timestamp, open, high, low, close, volume,
                     bid, ask, bid_size, ask_size, last_size, vwap, 
                     trades, source, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    base_data['symbol'],
                    base_data['timestamp'],
                    base_data.get('open'),
                    base_data.get('high'),
                    base_data.get('low'),
                    base_data['close'],
                    base_data.get('volume'),
                    base_data.get('bid'),
                    base_data.get('ask'),
                    base_data.get('bid_size'),
                    base_data.get('ask_size'),
                    base_data.get('last_size'),
                    base_data.get('vwap'),
                    base_data.get('trades'),
                    base_data.get('source'),
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error persisting market data: {e}")
    
    async def _notify_subscribers(self, data: MarketData):
        """Notify all subscribers of new data"""
        for queue in self._subscribers[:]:  # Copy list to avoid modification during iteration
            try:
                await queue.put(data)
            except asyncio.QueueFull:
                logger.warning("Subscriber queue full, skipping")
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
                self._subscribers.remove(queue)
    
    def get_latest(self, symbol: Optional[str] = None) -> Dict[str, MarketData]:
        """Get latest market data for symbol(s)"""
        with self._lock:
            if symbol:
                return {symbol: self._latest_data.get(symbol)}
            return self._latest_data.copy()
    
    def get_history(self, symbol: str, limit: Optional[int] = 1000) -> List[MarketData]:
        """Get historical data for a symbol"""
        with self._lock:
            # First check memory cache
            memory_data = list(self._memory_cache.get(symbol, []))
            
            if limit is not None and len(memory_data) >= limit:
                return memory_data[:limit]
            
            # Fetch additional data from database if needed
            if limit is None or len(memory_data) < limit:
                # Query database for more data
                with sqlite3.connect(str(self.config.db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    
                    if memory_data:
                        # Get data older than what we have in memory
                        oldest_timestamp = memory_data[-1].timestamp
                        remaining = (limit - len(memory_data)) if limit is not None else None
                        
                        if remaining is not None:
                            cursor = conn.execute("""
                                SELECT * FROM market_data
                                WHERE symbol = ? AND timestamp < ?
                                ORDER BY timestamp DESC
                                LIMIT ?
                            """, (symbol, oldest_timestamp, remaining))
                        else:
                            cursor = conn.execute("""
                                SELECT * FROM market_data
                                WHERE symbol = ? AND timestamp < ?
                                ORDER BY timestamp DESC
                            """, (symbol, oldest_timestamp))
                    else:
                        # No memory data, get from database
                        if limit is not None:
                            cursor = conn.execute("""
                                SELECT * FROM market_data
                                WHERE symbol = ?
                                ORDER BY timestamp DESC
                                LIMIT ?
                            """, (symbol, limit))
                        else:
                            cursor = conn.execute("""
                                SELECT * FROM market_data
                                WHERE symbol = ?
                                ORDER BY timestamp DESC
                            """, (symbol,))
                    
                    db_data = [self._row_to_market_data(row) for row in cursor]
                    memory_data.extend([d for d in db_data if d])
            
            return memory_data[:limit] if limit is not None else memory_data
    
    def get_timerange_data(
        self, 
        symbol: str, 
        start_time: float, 
        end_time: float
    ) -> List[MarketData]:
        """Get data for a specific time range"""
        with sqlite3.connect(str(self.config.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM market_data
                WHERE symbol = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (symbol, start_time, end_time))
            
            return [d for d in (self._row_to_market_data(row) for row in cursor) if d]
    
    def get_symbols(self) -> List[str]:
        """Get list of all symbols with data"""
        with self._lock:
            memory_symbols = set(self._latest_data.keys())
            
        with sqlite3.connect(str(self.config.db_path)) as conn:
            cursor = conn.execute("SELECT DISTINCT symbol FROM market_data")
            db_symbols = {row[0] for row in cursor}
            
        return sorted(memory_symbols | db_symbols)
    
    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to real-time market data updates"""
        queue = asyncio.Queue(maxsize=1000)
        self._subscribers.append(queue)
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from market data updates"""
        if queue in self._subscribers:
            self._subscribers.remove(queue)
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self):
        """Background task to cleanup old data"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                self._cleanup_old_data()
                self._aggregate_minute_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    def _cleanup_old_data(self):
        """Remove data older than retention period"""
        cutoff = datetime.now().timestamp() - (self.config.retention_days * 24 * 3600)
        
        try:
            with sqlite3.connect(str(self.config.db_path)) as conn:
                # Delete old tick data
                conn.execute(
                    "DELETE FROM market_data WHERE timestamp < ?",
                    (cutoff,)
                )
                
                # Delete old aggregated data
                conn.execute(
                    "DELETE FROM market_data_1min WHERE timestamp < ?",
                    (cutoff - 30 * 24 * 3600,)  # Keep aggregated data longer
                )
                
                # Vacuum if enabled
                if self.config.enable_compression:
                    conn.execute("VACUUM")
                
                conn.commit()
                
                logger.info(f"Cleaned up data older than {self.config.retention_days} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _aggregate_minute_data(self):
        """Aggregate tick data into 1-minute bars"""
        try:
            # Get the last aggregated timestamp
            with sqlite3.connect(str(self.config.db_path)) as conn:
                cursor = conn.execute(
                    "SELECT MAX(timestamp) FROM market_data_1min"
                )
                last_agg = cursor.fetchone()[0] or 0
                
                # Aggregate new data
                current_minute = int(datetime.now().timestamp() / 60) * 60
                
                conn.execute("""
                    INSERT OR REPLACE INTO market_data_1min 
                    (symbol, timestamp, open, high, low, close, volume, vwap, trades)
                    SELECT 
                        symbol,
                        CAST(timestamp/60 AS INTEGER) * 60 as minute,
                        (SELECT close FROM market_data md2 
                         WHERE md2.symbol = md.symbol 
                         AND CAST(md2.timestamp/60 AS INTEGER) * 60 = CAST(md.timestamp/60 AS INTEGER) * 60
                         ORDER BY timestamp ASC LIMIT 1) as open,
                        MAX(high) as high,
                        MIN(low) as low,
                        (SELECT close FROM market_data md3
                         WHERE md3.symbol = md.symbol
                         AND CAST(md3.timestamp/60 AS INTEGER) * 60 = CAST(md.timestamp/60 AS INTEGER) * 60  
                         ORDER BY timestamp DESC LIMIT 1) as close,
                        SUM(volume) as volume,
                        AVG(vwap) as vwap,
                        SUM(trades) as trades
                    FROM market_data md
                    WHERE timestamp > ? AND timestamp < ?
                    GROUP BY symbol, minute
                """, (last_agg, current_minute))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error aggregating minute data: {e}")
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        with self._lock:
            memory_stats = {
                'symbols': len(self._latest_data),
                'memory_records': sum(len(dq) for dq in self._memory_cache.values()),
                'subscribers': len(self._subscribers)
            }
        
        with sqlite3.connect(str(self.config.db_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM market_data")
            total_records = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
            total_symbols = cursor.fetchone()[0]
            
            # Get database file size
            db_size = self.config.db_path.stat().st_size if self.config.db_path.exists() else 0
        
        return {
            **memory_stats,
            'total_records': total_records,
            'total_symbols': total_symbols,
            'db_size_mb': round(db_size / 1024 / 1024, 2)
        }


# Singleton instance
_store_instance: Optional[MarketDataStore] = None
_store_lock = threading.Lock()


def get_market_data_store(config_path: Optional[Path] = None) -> MarketDataStore:
    """Get or create the singleton market data store instance"""
    global _store_instance
    
    with _store_lock:
        if _store_instance is None:
            if config_path is None:
                from .config import config
                config_path = config.get_data_dir() / "market_data.db"
            
            store_config = MarketDataConfig(db_path=config_path)
            _store_instance = MarketDataStore(store_config)
        
        return _store_instance