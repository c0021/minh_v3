#!/usr/bin/env python3
"""
MinhOS v3 State Manager (Migrated)
=================================
Linux-native centralized state management for MinhOS trading system.
Provides single source of truth for all system state with SQLite persistence
and real-time event publishing.

MIGRATED: Now uses unified market data store instead of local storage.
"""

import asyncio
import json
import sqlite3
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from contextlib import asynccontextmanager

# Import unified market data store
from ..core.market_data_adapter import get_market_data_adapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("state_manager")

class TradingState(Enum):
    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"
    TRANSITIONING = "TRANSITIONING"

class SystemState(Enum):
    OFFLINE = "OFFLINE"
    STARTING = "STARTING"
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    INITIALIZING = "INITIALIZING"

class AIState(Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ANALYZING = "ANALYZING"
    ERROR = "ERROR"

@dataclass
class Position:
    symbol: str
    quantity: int
    side: str  # LONG, SHORT, FLAT
    entry_price: float
    current_price: float
    unrealized_pnl: float
    entry_time: datetime
    last_update: datetime

@dataclass
class RiskParameters:
    max_position_size: int = 5
    max_daily_loss: float = 1000.0
    max_drawdown_percent: float = 10.0
    position_size_percent: float = 2.0
    stop_loss_points: float = 10.0
    take_profit_points: float = 20.0
    enabled: bool = False
    max_positions: int = 3
    stop_loss_ticks: int = 4

@dataclass
class SystemConfig:
    auto_trade_enabled: bool = False
    market_data_source: str = "sierra_chart"
    trading_enabled: bool = False
    risk_check_level: str = "strict"
    log_level: str = "info"
    debug_mode: bool = False
    max_orders_per_minute: int = 10
    data_validation_enabled: bool = True
    emergency_stop_triggered: bool = False

@dataclass
class MarketDataPoint:
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

class StateManager:
    """
    Centralized state manager for MinhOS v3
    Linux-native with SQLite persistence and event system
    """
    
    def __init__(self, db_path: str = "/tmp/minhos/state.db"):
        """Initialize State Manager"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Current state
        self.system_state = SystemState.INITIALIZING
        self.trading_state = TradingState.FLAT
        self.ai_state = AIState.OFFLINE
        self.positions: Dict[str, Position] = {}
        self.risk_params = RiskParameters()
        self.system_config = SystemConfig()
        
        # MIGRATED: Use unified market data store instead of local storage
        self.market_data_adapter = get_market_data_adapter()
        self.last_market_update = None
        
        # P&L tracking
        self.pnl = {
            "today": 0.0,
            "total": 0.0,
            "unrealized": 0.0,
            "realized": 0.0
        }
        
        # Event system
        self.event_subscribers: Dict[str, List[Callable]] = {}
        self.state_lock = asyncio.Lock()
        
        # WebSocket notifications
        self.websocket_notify_url = "http://localhost:9002/api/notify"
        self.websocket_enabled = True
        
        # Statistics
        self.stats = {
            "state_updates": 0,
            "database_writes": 0,
            "events_published": 0,
            "market_data_updates": 0,
            "position_updates": 0,
            "risk_updates": 0,
            "last_save": None,
            "start_time": datetime.now().isoformat()
        }
        
        # Initialize database
        self._init_database()
        asyncio.create_task(self._load_state())
        
        logger.info("🏛️ State Manager initialized (Linux-native)")
    
    def _init_database(self):
        """Initialize SQLite database for state persistence"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Enable WAL mode for better concurrent access
                cursor.execute("PRAGMA journal_mode=WAL")
                
                # Positions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS positions (
                        symbol TEXT PRIMARY KEY,
                        quantity INTEGER,
                        side TEXT,
                        entry_price REAL,
                        current_price REAL,
                        unrealized_pnl REAL,
                        entry_time TEXT,
                        last_update TEXT
                    )
                ''')
                
                # Risk parameters table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS risk_parameters (
                        id INTEGER PRIMARY KEY,
                        max_position_size INTEGER,
                        max_daily_loss REAL,
                        max_drawdown_percent REAL,
                        position_size_percent REAL,
                        stop_loss_points REAL,
                        take_profit_points REAL,
                        enabled BOOLEAN,
                        max_positions INTEGER,
                        stop_loss_ticks INTEGER,
                        updated_at TEXT
                    )
                ''')
                
                # System config table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_config (
                        id INTEGER PRIMARY KEY,
                        auto_trade_enabled BOOLEAN,
                        trading_enabled BOOLEAN,
                        debug_mode BOOLEAN,
                        max_orders_per_minute INTEGER,
                        data_validation_enabled BOOLEAN,
                        emergency_stop_triggered BOOLEAN,
                        updated_at TEXT
                    )
                ''')
                
                # Market data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        close REAL,
                        bid REAL,
                        ask REAL,
                        volume INTEGER,
                        timestamp TEXT,
                        received_at TEXT,
                        source TEXT
                    )
                ''')
                
                # State history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS state_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        event_type TEXT,
                        old_state TEXT,
                        new_state TEXT,
                        data TEXT
                    )
                ''')
                
                # P&L history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pnl_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        realized_pnl REAL,
                        unrealized_pnl REAL,
                        total_pnl REAL,
                        timestamp TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("✅ State database initialized")
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def _load_state(self):
        """Load state from database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Load positions
                cursor.execute("SELECT * FROM positions")
                for row in cursor.fetchall():
                    symbol, quantity, side, entry_price, current_price, unrealized_pnl, entry_time_str, last_update_str = row
                    
                    try:
                        entry_time = datetime.fromisoformat(entry_time_str)
                        last_update = datetime.fromisoformat(last_update_str)
                        
                        self.positions[symbol] = Position(
                            symbol=symbol,
                            quantity=quantity,
                            side=side,
                            entry_price=entry_price,
                            current_price=current_price,
                            unrealized_pnl=unrealized_pnl,
                            entry_time=entry_time,
                            last_update=last_update
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load position {symbol}: {e}")
                
                # Load risk parameters (latest)
                cursor.execute("SELECT * FROM risk_parameters ORDER BY id DESC LIMIT 1")
                risk_row = cursor.fetchone()
                if risk_row:
                    try:
                        self.risk_params = RiskParameters(
                            max_position_size=risk_row[1],
                            max_daily_loss=risk_row[2],
                            max_drawdown_percent=risk_row[3],
                            position_size_percent=risk_row[4],
                            stop_loss_points=risk_row[5],
                            take_profit_points=risk_row[6],
                            enabled=bool(risk_row[7]),
                            max_positions=risk_row[8] if risk_row[8] is not None else 3,
                            stop_loss_ticks=risk_row[9] if risk_row[9] is not None else 4
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load risk parameters: {e}")
                
                # Load system config (latest)
                cursor.execute("SELECT * FROM system_config ORDER BY id DESC LIMIT 1")
                config_row = cursor.fetchone()
                if config_row:
                    try:
                        self.system_config = SystemConfig(
                            auto_trade_enabled=bool(config_row[1]),
                            trading_enabled=bool(config_row[2]),
                            debug_mode=bool(config_row[3]),
                            max_orders_per_minute=config_row[4],
                            data_validation_enabled=bool(config_row[5]),
                            emergency_stop_triggered=bool(config_row[6])
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load system config: {e}")
                
                logger.info("✅ State loaded from database")
                
        except Exception as e:
            logger.error(f"❌ Error loading state from database: {e}")
    
    async def start(self):
        """Start the State Manager"""
        logger.info("🚀 Starting State Manager (with unified market data store)...")
        
        # MIGRATED: Start unified market data store
        await self.market_data_adapter.start()
        
        # Subscribe to market data updates
        await self.market_data_adapter.subscribe(self._on_market_data_update)
        
        # Set system state to starting
        await self.set_system_state(SystemState.STARTING)
        
        # Start background tasks
        asyncio.create_task(self._periodic_save_loop())
        asyncio.create_task(self._pnl_calculation_loop())
        asyncio.create_task(self._cleanup_loop())
        
        # Set system state to online
        await self.set_system_state(SystemState.ONLINE)
        
        logger.info("✅ State Manager started")
    
    async def stop(self):
        """Stop the State Manager"""
        logger.info("🛑 Stopping State Manager...")
        
        await self.set_system_state(SystemState.OFFLINE)
        await self._save_state()
        
        logger.info("State Manager stopped")
    
    # MIGRATED: Market data update handler from unified store
    async def _on_market_data_update(self, data):
        """Handle market data updates from unified store"""
        try:
            # Convert MarketData to MarketDataPoint for compatibility
            market_data = MarketDataPoint(
                symbol=data.symbol,
                close=data.close,
                bid=data.bid,
                ask=data.ask,
                volume=data.volume,
                timestamp=datetime.fromtimestamp(data.timestamp).isoformat() if data.timestamp else "",
                source=data.source or "unified_store",
                received_at=datetime.now().isoformat()
            )
            
            self.last_market_update = datetime.now()
            self.stats["market_data_updates"] += 1
            
            # Update position P&L if we have positions
            if market_data.symbol in self.positions:
                await self._update_position_pnl(market_data.symbol, market_data.close)
            
            # Publish event
            await self._publish_event("market_data_updated", {
                "symbol": market_data.symbol,
                "data": asdict(market_data)
            })
            
            # Send WebSocket notification
            await self._notify_websocket("market_data_update", asdict(market_data))
            
            logger.debug(f"📊 Market data processed: {market_data.symbol} @ ${market_data.close}")
            
        except Exception as e:
            logger.error(f"❌ Market data update error: {e}")
    
    # Core state management methods
    async def update_market_data(self, data: Union[Dict[str, Any], MarketDataPoint]):
        """Update market data state"""
        async with self.state_lock:
            try:
                # Convert dict to MarketDataPoint if needed
                if isinstance(data, dict):
                    market_data = MarketDataPoint(
                        symbol=data.get('symbol', 'UNKNOWN'),
                        close=float(data.get('close', data.get('price', 0))),
                        bid=data.get('bid'),
                        ask=data.get('ask'),
                        volume=data.get('volume'),
                        timestamp=data.get('timestamp', datetime.now().isoformat()),
                        source=data.get('source', 'unknown'),
                        received_at=data.get('received_at', datetime.now().isoformat())
                    )
                else:
                    market_data = data
                
                # MIGRATED: Store in unified store instead of local storage
                # Convert to unified store format
                from ..models.market import MarketData
                import time
                
                unified_data = MarketData(
                    symbol=market_data.symbol,
                    timestamp=time.time(),
                    close=market_data.close,
                    bid=market_data.bid,
                    ask=market_data.ask,
                    volume=market_data.volume,
                    source=market_data.source
                )
                
                # Store in unified store - this will trigger our _on_market_data_update callback
                await self.market_data_adapter.async_add_data(unified_data)
                
                logger.debug(f"📊 Market data forwarded to unified store: {market_data.symbol} @ ${market_data.close}")
                
            except Exception as e:
                logger.error(f"❌ Market data update error: {e}")
    
    async def update_position(self, symbol: str, quantity: int, side: str, 
                            entry_price: Optional[float] = None, current_price: Optional[float] = None):
        """Update position information"""
        async with self.state_lock:
            try:
                old_state = self.trading_state
                
                if symbol in self.positions:
                    position = self.positions[symbol]
                    position.quantity = quantity
                    position.side = side
                    if current_price is not None:
                        position.current_price = current_price
                        position.unrealized_pnl = self._calculate_position_pnl(position)
                    position.last_update = datetime.now()
                else:
                    # New position
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=quantity,
                        side=side,
                        entry_price=entry_price or current_price or 0,
                        current_price=current_price or 0,
                        unrealized_pnl=0,
                        entry_time=datetime.now(),
                        last_update=datetime.now()
                    )
                
                # Update trading state based on positions
                await self._update_trading_state()
                
                self.stats["position_updates"] += 1
                await self._save_position(self.positions[symbol])
                
                # Publish events
                await self._publish_event("position_updated", {
                    "symbol": symbol,
                    "position": asdict(self.positions[symbol]),
                    "trading_state": self.trading_state.value
                })
                
                if old_state != self.trading_state:
                    await self._publish_event("trading_state_changed", {
                        "old_state": old_state.value,
                        "new_state": self.trading_state.value
                    })
                
                logger.info(f"📊 Position updated: {symbol} {side} {quantity} @ ${current_price or 0}")
                
            except Exception as e:
                logger.error(f"❌ Position update error: {e}")
    
    async def update_risk_parameters(self, **kwargs):
        """Update risk parameters"""
        async with self.state_lock:
            try:
                old_params = asdict(self.risk_params)
                
                # Update parameters
                for key, value in kwargs.items():
                    if hasattr(self.risk_params, key):
                        setattr(self.risk_params, key, value)
                
                # Validation
                if self.risk_params.enabled and self.system_config.auto_trade_enabled:
                    if (self.risk_params.max_position_size <= 0 or 
                        self.risk_params.max_daily_loss <= 0 or
                        self.risk_params.position_size_percent <= 0):
                        
                        logger.error("❌ Cannot enable auto-trade with zero risk parameters")
                        self.system_config.auto_trade_enabled = False
                
                self.stats["risk_updates"] += 1
                await self._save_risk_parameters()
                
                await self._publish_event("risk_parameters_updated", {
                    "old_params": old_params,
                    "new_params": asdict(self.risk_params)
                })
                
                logger.info(f"⚖️ Risk parameters updated: {kwargs}")
                
            except Exception as e:
                logger.error(f"❌ Risk parameters update error: {e}")
    
    async def update_system_config(self, **kwargs):
        """Update system configuration"""
        async with self.state_lock:
            try:
                old_config = asdict(self.system_config)
                
                # Update configuration
                for key, value in kwargs.items():
                    if hasattr(self.system_config, key):
                        setattr(self.system_config, key, value)
                
                # Safety checks
                if self.system_config.auto_trade_enabled:
                    if not self.risk_params.enabled:
                        logger.error("❌ Cannot enable auto-trade without risk parameters")
                        self.system_config.auto_trade_enabled = False
                    
                    if self.system_state != SystemState.ONLINE:
                        logger.error("❌ Cannot enable auto-trade when system not online")
                        self.system_config.auto_trade_enabled = False
                
                await self._save_system_config()
                
                await self._publish_event("system_config_updated", {
                    "old_config": old_config,
                    "new_config": asdict(self.system_config)
                })
                
                logger.info(f"⚙️ System config updated: {kwargs}")
                
            except Exception as e:
                logger.error(f"❌ System config update error: {e}")
    
    async def set_system_state(self, new_state: SystemState):
        """Update system state"""
        async with self.state_lock:
            try:
                old_state = self.system_state
                self.system_state = new_state
                
                # Auto-disable trading if system goes offline
                if new_state != SystemState.ONLINE and self.system_config.auto_trade_enabled:
                    self.system_config.auto_trade_enabled = False
                    logger.warning("⚠️ Auto-trade disabled due to system state change")
                
                await self._save_state_history("system_state_changed", old_state.value, new_state.value)
                
                await self._publish_event("system_state_changed", {
                    "old_state": old_state.value,
                    "new_state": new_state.value
                })
                
                logger.info(f"🏛️ System state: {old_state.value} → {new_state.value}")
                
            except Exception as e:
                logger.error(f"❌ System state update error: {e}")
    
    async def emergency_stop(self, reason: str):
        """Trigger emergency stop"""
        async with self.state_lock:
            try:
                logger.error(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")
                
                self.system_config.emergency_stop_triggered = True
                self.system_config.auto_trade_enabled = False
                await self.set_system_state(SystemState.EMERGENCY_STOP)
                
                await self._save_state()
                
                await self._publish_event("emergency_stop", {
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Send critical WebSocket notification
                await self._notify_websocket("emergency_stop", {
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"❌ Emergency stop error: {e}")
    
    # Event system
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to state change events"""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
    
    async def _publish_event(self, event_type: str, data: Any):
        """Publish state change event to subscribers"""
        try:
            if event_type in self.event_subscribers:
                tasks = []
                for callback in self.event_subscribers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            tasks.append(callback(data))
                        else:
                            callback(data)
                    except Exception as e:
                        logger.error(f"❌ Event callback error: {e}")
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
            self.stats["events_published"] += 1
            
        except Exception as e:
            logger.error(f"❌ Event publishing error: {e}")
    
    # State retrieval methods
    def get_current_state(self) -> Dict[str, Any]:
        """Get complete current state"""
        return {
            "trading_state": self.trading_state.value,
            "system_state": self.system_state.value,
            "ai_state": self.ai_state.value,
            "positions": {k: asdict(v) for k, v in self.positions.items()},
            "risk_parameters": asdict(self.risk_params),
            "system_config": asdict(self.system_config),
            "pnl": self.pnl.copy(),
            "market_data": {k: asdict(v) for k, v in self.get_market_data().items()},  # MIGRATED: Get from unified store
            "last_market_update": self.last_market_update.isoformat() if self.last_market_update else None,
            "stats": self.stats.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_positions(self) -> Dict[str, Position]:
        """Get all current positions"""
        return self.positions.copy()
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all current positions (alias for get_positions)"""
        return self.get_positions()
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        return self.positions.get(symbol)
    
    def get_market_data(self, symbol: str = None) -> Union[Dict[str, MarketDataPoint], Optional[MarketDataPoint]]:
        """MIGRATED: Get market data from unified store"""
        try:
            if symbol:
                # Get specific symbol from unified store
                unified_data = self.market_data_adapter.get_market_data(symbol)
                if unified_data:
                    # Convert to MarketDataPoint for backward compatibility
                    return MarketDataPoint(
                        symbol=unified_data.symbol,
                        close=unified_data.close,
                        bid=unified_data.bid,
                        ask=unified_data.ask,
                        volume=unified_data.volume,
                        timestamp=datetime.fromtimestamp(unified_data.timestamp).isoformat() if unified_data.timestamp else "",
                        source=unified_data.source or "unified_store"
                    )
                return None
            else:
                # Get all data from unified store
                all_unified_data = self.market_data_adapter.get_all_market_data()
                result = {}
                for sym, unified_data in all_unified_data.items():
                    if unified_data:
                        result[sym] = MarketDataPoint(
                            symbol=unified_data.symbol,
                            close=unified_data.close,
                            bid=unified_data.bid,
                            ask=unified_data.ask,
                            volume=unified_data.volume,
                            timestamp=datetime.fromtimestamp(unified_data.timestamp).isoformat() if unified_data.timestamp else "",
                            source=unified_data.source or "unified_store"
                        )
                return result
        except Exception as e:
            logger.error(f"❌ Error getting market data: {e}")
            return {} if symbol is None else None
    
    def get_risk_parameters(self) -> RiskParameters:
        """Get current risk parameters"""
        return self.risk_params
    
    def get_system_config(self) -> SystemConfig:
        """Get current system configuration"""
        return self.system_config
    
    # Helper methods
    async def _update_trading_state(self):
        """Update trading state based on current positions"""
        try:
            total_long = sum(pos.quantity for pos in self.positions.values() if pos.side == "LONG")
            total_short = sum(abs(pos.quantity) for pos in self.positions.values() if pos.side == "SHORT")
            
            if total_long == 0 and total_short == 0:
                self.trading_state = TradingState.FLAT
            elif total_long > total_short:
                self.trading_state = TradingState.LONG
            elif total_short > total_long:
                self.trading_state = TradingState.SHORT
            else:
                self.trading_state = TradingState.TRANSITIONING
                
        except Exception as e:
            logger.error(f"❌ Trading state update error: {e}")
    
    async def _update_position_pnl(self, symbol: str, current_price: float):
        """Update P&L for a specific position"""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                position.current_price = current_price
                position.unrealized_pnl = self._calculate_position_pnl(position)
                position.last_update = datetime.now()
                
        except Exception as e:
            logger.error(f"❌ Position P&L update error: {e}")
    
    def _calculate_position_pnl(self, position: Position) -> float:
        """Calculate P&L for a position"""
        try:
            if position.side == "LONG":
                return (position.current_price - position.entry_price) * position.quantity
            elif position.side == "SHORT":
                return (position.entry_price - position.current_price) * abs(position.quantity)
            else:
                return 0.0
        except Exception:
            return 0.0
    
    # Database operations
    async def _save_state(self):
        """Save complete state to database"""
        try:
            tasks = [
                self._save_risk_parameters(),
                self._save_system_config()
            ]
            
            # Save all positions
            for position in self.positions.values():
                tasks.append(self._save_position(position))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self.stats["database_writes"] += 1
            self.stats["last_save"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ State save error: {e}")
    
    async def _save_position(self, position: Position):
        """Save position to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO positions 
                    (symbol, quantity, side, entry_price, current_price, unrealized_pnl, entry_time, last_update)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    position.symbol,
                    position.quantity,
                    position.side,
                    position.entry_price,
                    position.current_price,
                    position.unrealized_pnl,
                    position.entry_time.isoformat(),
                    position.last_update.isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Position save error: {e}")
    
    # MIGRATED: _save_market_data method removed - now handled by unified store
    
    async def _save_risk_parameters(self):
        """Save risk parameters to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO risk_parameters 
                    (max_position_size, max_daily_loss, max_drawdown_percent, position_size_percent,
                     stop_loss_points, take_profit_points, enabled, max_positions, stop_loss_ticks, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.risk_params.max_position_size,
                    self.risk_params.max_daily_loss,
                    self.risk_params.max_drawdown_percent,
                    self.risk_params.position_size_percent,
                    self.risk_params.stop_loss_points,
                    self.risk_params.take_profit_points,
                    self.risk_params.enabled,
                    self.risk_params.max_positions,
                    self.risk_params.stop_loss_ticks,
                    datetime.now().isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Risk parameters save error: {e}")
    
    async def _save_system_config(self):
        """Save system configuration to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_config 
                    (auto_trade_enabled, trading_enabled, debug_mode, max_orders_per_minute,
                     data_validation_enabled, emergency_stop_triggered, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.system_config.auto_trade_enabled,
                    self.system_config.trading_enabled,
                    self.system_config.debug_mode,
                    self.system_config.max_orders_per_minute,
                    self.system_config.data_validation_enabled,
                    self.system_config.emergency_stop_triggered,
                    datetime.now().isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ System config save error: {e}")
    
    async def _save_state_history(self, event_type: str, old_state: str, new_state: str, data: str = None):
        """Save state change history"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO state_history (timestamp, event_type, old_state, new_state, data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    event_type,
                    old_state,
                    new_state,
                    data or json.dumps({})
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ State history save error: {e}")
    
    # Background tasks
    async def _periodic_save_loop(self):
        """Periodically save state to database"""
        while True:
            try:
                await asyncio.sleep(60)  # Save every minute
                await self._save_state()
                
            except Exception as e:
                logger.error(f"❌ Periodic save error: {e}")
    
    async def _pnl_calculation_loop(self):
        """Periodically calculate and update P&L"""
        while True:
            try:
                await asyncio.sleep(10)  # Calculate every 10 seconds
                
                # Calculate unrealized P&L
                unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
                self.pnl["unrealized"] = unrealized_pnl
                self.pnl["total"] = self.pnl["today"] + unrealized_pnl
                
            except Exception as e:
                logger.error(f"❌ P&L calculation error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_loop(self):
        """Periodically clean up old data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Clean every hour
                
                # Clean old market data
                cutoff_time = (datetime.now() - timedelta(days=7)).isoformat()
                
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM market_data WHERE timestamp < ?", (cutoff_time,))
                    cursor.execute("DELETE FROM state_history WHERE timestamp < ?", (cutoff_time,))
                    conn.commit()
                
                logger.debug("🧹 Database cleanup completed")
                
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
    
    # WebSocket notifications
    async def _notify_websocket(self, event_type: str, data: Dict[str, Any]):
        """Send notification to WebSocket server"""
        if not self.websocket_enabled:
            return
        
        try:
            timeout = aiohttp.ClientTimeout(total=1)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                payload = {
                    "type": event_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                
                async with session.post(self.websocket_notify_url, json=payload) as response:
                    if response.status != 200:
                        logger.debug(f"WebSocket notification failed: {response.status}")
                        
        except Exception as e:
            # Don't log connection errors as they're expected during startup
            if "Connection refused" not in str(e):
                logger.debug(f"WebSocket notification error: {e}")

# Global state manager instance
_state_manager: Optional[StateManager] = None

def get_state_manager() -> StateManager:
    """Get global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager

async def main():
    """Test the State Manager"""
    state_mgr = StateManager()
    
    try:
        await state_mgr.start()
        
        # Test state updates
        await state_mgr.update_risk_parameters(
            max_position_size=5,
            max_daily_loss=1000.0,
            position_size_percent=2.0,
            enabled=True
        )
        
        await state_mgr.update_position("NQ", 2, "LONG", 21800.0, 21850.0)
        
        # Show current state
        state = state_mgr.get_current_state()
        print(json.dumps(state, indent=2, default=str))
        
        # Keep running for a bit
        await asyncio.sleep(10)
        
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await state_mgr.stop()

if __name__ == "__main__":
    asyncio.run(main())