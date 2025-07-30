#!/usr/bin/env python3
"""
MinhOS v3 Sierra Chart Client Service
=====================================

Connects MinhOS to Sierra Chart via Windows Bridge for live trading.

This service provides the critical bridge between MinhOS's sophisticated 
AI trading intelligence and Sierra Chart's live market data and execution.

Key Features:
- Real-time market data streaming from Sierra Chart
- Live trade execution via bridge API
- Multi-symbol data collection (NQ, ES, VIX, etc.)
- WebSocket integration with MinhOS market data service
- Robust error handling and reconnection logic

Architecture:
  Sierra Chart (Windows) → Bridge API → Sierra Client → MinhOS Services

Author: MinhOS v3 System
"""

import asyncio
import json
import logging
import os
import time
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import websockets
from dataclasses import dataclass
from enum import Enum

from minhos.core.config import config
from minhos.core.base_service import BaseService
from minhos.models.market import MarketData

logger = logging.getLogger(__name__)

# 🚀 Phase 2 Optimization: WebSocket client for event-driven data
class OptimizedWebSocketClient:
    """WebSocket client optimized for delta updates and client-side caching"""
    
    def __init__(self, bridge_url: str, symbols: List[str]):
        self.bridge_url = bridge_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.symbols = symbols
        self.connections = {}  # symbol -> websocket connection
        self.cache = {}  # symbol -> cached data with TTL
        self.cache_ttl = 5.0  # 5-second cache TTL
        self.last_heartbeat = {}
        self.reconnect_delay = 1.0
        self.max_reconnect_delay = 30.0
        self.running = False
        self.message_handler = None  # Callback for market data
        
    async def start(self, message_handler=None):
        """Start WebSocket connections for all symbols"""
        self.running = True
        self.message_handler = message_handler
        logger.info(f"🚀 Starting optimized WebSocket connections for {len(self.symbols)} symbols")
        
        # Start connections for each symbol
        tasks = []
        for symbol in self.symbols:
            task = asyncio.create_task(self._maintain_connection(symbol))
            tasks.append(task)
        
        return tasks
    
    async def stop(self):
        """Stop all WebSocket connections"""
        self.running = False
        logger.info("🛑 Stopping optimized WebSocket connections")
        
        # Close all connections
        for symbol, ws in self.connections.items():
            try:
                await ws.close()
            except:
                pass
        
        self.connections.clear()
    
    async def _maintain_connection(self, symbol: str):
        """Maintain WebSocket connection for a symbol with auto-reconnection"""
        reconnect_delay = self.reconnect_delay
        
        while self.running:
            try:
                ws_url = f"{self.bridge_url}/ws/live_data/{symbol}"
                logger.debug(f"Connecting to optimized WebSocket: {ws_url}")
                
                async with websockets.connect(
                    ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5
                ) as websocket:
                    
                    self.connections[symbol] = websocket
                    reconnect_delay = self.reconnect_delay  # Reset delay on success
                    logger.info(f"✅ Optimized WebSocket connected for {symbol}")
                    
                    # Handle messages
                    async for message in websocket:
                        if not self.running:
                            break
                            
                        market_data = await self._handle_websocket_message(symbol, message)
                        if market_data and self.message_handler:
                            await self.message_handler(symbol, market_data)
                        
            except Exception as e:
                logger.warning(f"WebSocket connection error for {symbol}: {e}")
                
                # Remove failed connection
                if symbol in self.connections:
                    del self.connections[symbol]
                
                # Exponential backoff
                if self.running:
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, self.max_reconnect_delay)
    
    async def _handle_websocket_message(self, symbol: str, message: str):
        """Handle WebSocket message with delta processing"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'market_data_delta':
                # Process delta update
                delta = data.get('delta', {})
                full_data = data.get('full_data', {})
                
                # Update cache with full data
                self.cache[symbol] = {
                    'data': full_data,
                    'timestamp': time.time()
                }
                
                logger.debug(f"📈 Delta update for {symbol}: {len(delta)} fields changed")
                return full_data
                
            elif msg_type == 'initial_state':
                # Initial state for new connection
                initial_data = data.get('data', {})
                self.cache[symbol] = {
                    'data': initial_data,
                    'timestamp': time.time()
                }
                
                logger.debug(f"📊 Initial state received for {symbol}")
                return initial_data
                
            elif msg_type == 'ping':
                # Send heartbeat response
                if symbol in self.connections:
                    await self.connections[symbol].send(json.dumps({
                        'type': 'heartbeat',
                        'timestamp': time.time()
                    }))
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message for {symbol}: {e}")
            return None
    
    async def get_cached_data(self, symbol: str) -> Optional[dict]:
        """Get cached data with TTL check"""
        if symbol not in self.cache:
            return None
            
        cache_entry = self.cache[symbol]
        age = time.time() - cache_entry['timestamp']
        
        if age <= self.cache_ttl:
            logger.debug(f"🎯 Cache hit for {symbol} (age: {age:.1f}s)")
            return cache_entry['data']
        else:
            logger.debug(f"🔄 Cache miss for {symbol} (expired: {age:.1f}s)")
            return None
    
    def get_connection_stats(self):
        """Get connection statistics with cache performance metrics"""
        active_connections = len(self.connections)
        cached_symbols = len(self.cache)
        
        # Calculate cache hit rate and freshness
        cache_stats = self.get_cache_statistics()
        
        return {
            'active_connections': active_connections,
            'cached_symbols': cached_symbols,
            'connection_symbols': list(self.connections.keys()),
            'cache_symbols': list(self.cache.keys()),
            'cache_performance': cache_stats
        }
    
    def get_cache_statistics(self):
        """Get detailed cache performance statistics"""
        current_time = time.time()
        fresh_cache_count = 0
        total_cache_age = 0
        
        for symbol, cache_entry in self.cache.items():
            age = current_time - cache_entry['timestamp']
            total_cache_age += age
            if age <= self.cache_ttl:
                fresh_cache_count += 1
        
        cache_count = len(self.cache)
        avg_cache_age = total_cache_age / cache_count if cache_count > 0 else 0
        cache_freshness = fresh_cache_count / cache_count if cache_count > 0 else 0
        
        return {
            'total_cached_symbols': cache_count,
            'fresh_cache_entries': fresh_cache_count,
            'average_cache_age_seconds': round(avg_cache_age, 2),
            'cache_freshness_ratio': round(cache_freshness, 3),
            'cache_ttl_seconds': self.cache_ttl
        }

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class TradeCommand:
    """Trade command to send to Sierra Chart"""
    command_id: str
    action: str  # BUY, SELL
    symbol: str
    quantity: int
    price: Optional[float] = None
    order_type: str = "MARKET"
    
    def to_dict(self) -> Dict:
        return {
            "command_id": self.command_id,
            "action": self.action,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "order_type": self.order_type
        }

@dataclass
class TradeResult:
    """Trade execution result from Sierra Chart"""
    command_id: str
    status: str  # FILLED, REJECTED, PENDING
    message: str
    fill_price: Optional[float] = None
    timestamp: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TradeResult':
        return cls(
            command_id=data.get('command_id', ''),
            status=data.get('status', 'UNKNOWN'),
            message=data.get('message', ''),
            fill_price=data.get('fill_price'),
            timestamp=data.get('timestamp')
        )

class SierraClient(BaseService):
    """Sierra Chart client service for live trading integration"""
    
    def __init__(self):
        super().__init__("sierra_client", 9003)  # WebSocket port for market data relay
        self.config = config
        
        # Bridge connection settings - check multiple sources
        self.bridge_hostname = self._get_bridge_hostname()
        self.bridge_port = self._get_bridge_port()
        self.bridge_url = f"http://{self.bridge_hostname}:{self.bridge_port}"
        
        # Connection management
        self.connection_state = ConnectionState.DISCONNECTED
        self.session: Optional[aiohttp.ClientSession] = None
        self.reconnect_delay = 5.0
        self.max_reconnect_attempts = 10
        self.running = False
        
        # Market data streaming
        self.market_data_subscribers = set()
        self.last_market_data: Dict[str, MarketData] = {}
        self._data_handlers = []  # Initialize data handlers list
        
        # 🚀 Phase 2 Optimization: WebSocket client
        self.optimized_client = None
        self.use_websocket_optimization = True  # Enable by default
        self.websocket_tasks = []
        
        # Trading
        self.pending_trades: Dict[str, TradeCommand] = {}
        
        # Multi-chart symbols (centralized symbol management)
        from ..core.symbol_integration import get_sierra_client_symbols, get_symbol_integration
        self.symbols = get_sierra_client_symbols()
        
        # Mark service as migrated to centralized symbol management
        get_symbol_integration().mark_service_migrated('sierra_client')
        
        logger.info(f"Sierra Client initialized - Bridge: {self.bridge_url}")
    
    def _get_bridge_hostname(self) -> str:
        """Get bridge hostname from multiple sources"""
        # 1. Check environment variable
        hostname = os.getenv('BRIDGE_HOSTNAME')
        if hostname:
            return hostname
        
        # 2. Check .env file
        env_file = os.path.join(os.path.dirname(__file__), '../../.env')
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('BRIDGE_HOSTNAME='):
                            hostname = line.split('=', 1)[1].strip()
                            if hostname:
                                return hostname
            except Exception as e:
                logger.debug(f"Could not read .env file: {e}")
        
        # 3. Default fallback
        return 'cthinkpad'
    
    def _get_bridge_port(self) -> int:
        """Get bridge port from multiple sources"""
        # 1. Check environment variable
        port = os.getenv('BRIDGE_PORT')
        if port:
            try:
                return int(port)
            except ValueError:
                logger.warning(f"Invalid BRIDGE_PORT: {port}, using default")
        
        # 2. Check .env file
        env_file = os.path.join(os.path.dirname(__file__), '../../.env')
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('BRIDGE_PORT='):
                            port = line.split('=', 1)[1].strip()
                            if port:
                                try:
                                    return int(port)
                                except ValueError:
                                    logger.warning(f"Invalid port in .env: {port}")
            except Exception as e:
                logger.debug(f"Could not read .env file: {e}")
        
        # 3. Default fallback
        return 8765
    
    async def _create_optimized_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session with TCP optimizations to fix streaming issues"""
        # Create connector with TCP_NODELAY to disable Nagle's Algorithm
        connector = aiohttp.TCPConnector(
            limit=100,  # Connection pool size
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            force_close=False,  # Keep connections alive
            keepalive_timeout=30
        )
        
        # Set TCP_NODELAY on the connector
        async def on_connection_create_func(session, trace_config_ctx, params):
            """Set TCP_NODELAY when connection is created"""
            # The params object has different attributes depending on aiohttp version
            # Try to get the transport/connection from available attributes
            transport = None
            if hasattr(params, 'transport'):
                transport = params.transport
            elif hasattr(params, 'connection'):
                transport = params.connection.transport if hasattr(params.connection, 'transport') else None
            
            if transport:
                sock = transport.get_extra_info('socket')
                if sock is not None:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    # Linux-specific: Enable TCP_QUICKACK if available
                    if hasattr(socket, 'TCP_QUICKACK'):
                        try:
                            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
                        except:
                            pass
                    logger.debug("TCP optimizations applied to connection")
        
        # Create trace config to intercept connection creation
        trace_config = aiohttp.TraceConfig()
        trace_config.on_connection_create_end.append(on_connection_create_func)
        
        # Create session with optimizations
        session = aiohttp.ClientSession(
            connector=connector,
            trace_configs=[trace_config],
            timeout=aiohttp.ClientTimeout(total=30, connect=5, sock_read=10),
            headers={
                'Connection': 'keep-alive',
                'Keep-Alive': 'timeout=30, max=100',
                'User-Agent': 'MinhOS-Sierra-Client/3.0'
            }
        )
        
        logger.info("Created optimized HTTP session with TCP_NODELAY enabled")
        return session
    
    async def start(self):
        """Start the Sierra Client service"""
        await super().start()
        
        # Set running flag for background tasks
        self.running = True
        
        # Create HTTP session with TCP optimizations
        self.session = await self._create_optimized_session()
        
        # Start connection management
        asyncio.create_task(self._connection_manager())
        
        # 🚀 Phase 2 Optimization: Start WebSocket client if enabled
        if self.use_websocket_optimization:
            await self._start_optimized_websocket_client()
        
        # Start market data streaming (will detect and use WebSocket or fallback to HTTP)
        asyncio.create_task(self._market_data_streamer())
        
        logger.info(f"✅ Sierra Client started ({'optimized WebSocket' if self.use_websocket_optimization else 'HTTP polling'})")
    
    async def stop(self):
        """Stop the Sierra Client service"""
        self.running = False
        self.connection_state = ConnectionState.DISCONNECTED
        
        # Stop optimized WebSocket client
        if self.optimized_client:
            await self.optimized_client.stop()
        
        # Cancel WebSocket tasks
        for task in self.websocket_tasks:
            task.cancel()
        
        if self.session:
            await self.session.close()
        
        await super().stop()
        logger.info("✅ Sierra Client stopped (optimized WebSocket disconnected)")
    
    async def _start_optimized_websocket_client(self):
        """Start optimized WebSocket client for event-driven data"""
        try:
            self.optimized_client = OptimizedWebSocketClient(
                bridge_url=self.bridge_url,
                symbols=self.symbols
            )
            
            # Start WebSocket connections with market data handler
            self.websocket_tasks = await self.optimized_client.start(
                message_handler=self._handle_websocket_market_data
            )
            
            logger.info(f"🚀 Optimized WebSocket client started for {len(self.symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Failed to start optimized WebSocket client: {e}")
            logger.info("Falling back to HTTP polling mode")
            self.use_websocket_optimization = False
            self.optimized_client = None
    
    async def _handle_websocket_market_data(self, symbol: str, market_data_dict: dict):
        """Handle market data from optimized WebSocket client"""
        try:
            # Convert dict to MarketData object
            # For now, create a simplified MarketData object
            market_data = MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=market_data_dict.get('price', 0.0),
                volume=market_data_dict.get('volume', 0),
                bid=market_data_dict.get('bid', 0.0),
                ask=market_data_dict.get('ask', 0.0),
                open=market_data_dict.get('open', 0.0),
                high=market_data_dict.get('high', 0.0),
                low=market_data_dict.get('low', 0.0),
                close=market_data_dict.get('close', 0.0)
            )
            
            # Store and broadcast
            self.last_market_data[symbol] = market_data
            await self._broadcast_market_data(market_data)
            
            logger.debug(f"🚀 WebSocket market data: {symbol} @ ${market_data.close}")
            
        except Exception as e:
            logger.error(f"Error handling WebSocket market data for {symbol}: {e}")
    
    async def _connection_manager(self):
        """Manage connection to Windows bridge with auto-reconnect"""
        attempt = 0
        
        while self.running:
            try:
                if self.connection_state == ConnectionState.DISCONNECTED:
                    self.connection_state = ConnectionState.CONNECTING
                    logger.info(f"Attempting to connect to bridge ({attempt + 1}/{self.max_reconnect_attempts})")
                    
                    # Test bridge health
                    health = await self._check_bridge_health()
                    logger.info(f"Health check result: {health}")
                    if health and health.get('status') == 'healthy':
                        self.connection_state = ConnectionState.CONNECTED
                        attempt = 0  # Reset attempt counter on success
                        logger.info("✅ Connected to Sierra Chart bridge successfully")
                        
                        # Notify system of connection
                        await self._broadcast_connection_status(True)
                        
                    else:
                        raise Exception(f"Bridge health check failed: {health}")
                
                elif self.connection_state == ConnectionState.CONNECTED:
                    # Periodic health check
                    if not await self._verify_connection():
                        logger.warning("Bridge connection lost - attempting reconnect")
                        self.connection_state = ConnectionState.DISCONNECTED
                        await self._broadcast_connection_status(False)
                
                # Wait before next check
                await asyncio.sleep(30 if self.connection_state == ConnectionState.CONNECTED else self.reconnect_delay)
                
            except Exception as e:
                attempt += 1
                self.connection_state = ConnectionState.ERROR
                logger.error(f"Bridge connection error (attempt {attempt}): {e}")
                
                if attempt >= self.max_reconnect_attempts:
                    logger.critical("Max reconnection attempts reached - stopping service")
                    break
                
                await asyncio.sleep(self.reconnect_delay * attempt)  # Exponential backoff
    
    async def _check_bridge_health(self) -> Optional[Dict]:
        """Check Windows bridge health"""
        try:
            if not self.session:
                logger.info("Session not initialized yet, creating temporary session for health check")
                async with aiohttp.ClientSession() as temp_session:
                    async with temp_session.get(f"{self.bridge_url}/health", timeout=10) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        else:
                            logger.error(f"Health check returned status {resp.status}")
                            return None
            else:
                async with self.session.get(f"{self.bridge_url}/health", timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Health check returned status {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Health check exception: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def _verify_connection(self) -> bool:
        """Verify bridge connection is still active AND actually providing data"""
        # First check basic health
        health = await self._check_bridge_health()
        if not health or health.get('status') != 'healthy':
            return False
        
        # More importantly - check if we're actually getting market data
        try:
<<<<<<< HEAD
            # Get primary symbol for health check from centralized management
            from ..core.symbol_integration import get_symbol_integration
            symbol_integration = get_symbol_integration()
            primary_symbol = symbol_integration.get_ai_brain_primary_symbol()
            
            # Test if we can get actual market data (not just health ping)
            async with self.session.get(f"{self.bridge_url}/api/data/{primary_symbol}", timeout=5) as resp:
=======
            # Test if we can get actual market data (not just health ping)
            async with self.session.get(f"{self.bridge_url}/api/data/NQU25-CME", timeout=5) as resp:
>>>>>>> 25301bf6f2e931ccc6aab9ec2c45b5c7f4fddfa2
                if resp.status == 200:
                    data = await resp.json()
                    # Verify we got real data, not empty/cached
                    if data.get('price', 0) > 0 and data.get('timestamp'):
                        return True
                    else:
                        logger.warning("Bridge responding but no real market data (price=0 or no timestamp)")
                        return False
                else:
                    logger.warning(f"Bridge health OK but market data endpoint failed: {resp.status}")
                    return False
        except Exception as e:
            logger.warning(f"Bridge health OK but market data fetch failed: {e}")
            return False
    
    async def _market_data_streamer(self):
        """Stream market data from bridge and relay to MinhOS services"""
        # 🚀 Phase 2 Optimization: Check if WebSocket optimization is active
        if self.use_websocket_optimization and self.optimized_client:
            logger.info("🚀 Market data streaming via optimized WebSocket (HTTP polling disabled)")
            # WebSocket handles data streaming, this method just monitors
            while self.running:
                try:
                    # Just monitor WebSocket connection health
                    if self.optimized_client:
                        stats = self.optimized_client.get_connection_stats()
                        if stats['active_connections'] == 0:
                            logger.warning("⚠️ No active WebSocket connections - potential fallback needed")
                    
                    await asyncio.sleep(30)  # Check every 30 seconds instead of 1 second
                    
                except Exception as e:
                    logger.error(f"WebSocket monitoring error: {e}")
                    await asyncio.sleep(5.0)
            return  # Exit early if using WebSocket optimization
        
        # Legacy HTTP polling mode
        logger.info("🔄 Market data streaming via HTTP polling (fallback mode)")
        
        while self.running:
            try:
                logger.debug(f"Market data streaming loop - Connection state: {self.connection_state}")
                
                if self.connection_state == ConnectionState.CONNECTED:
                    # Get market data for all symbols
                    logger.debug("Fetching all market data from bridge...")
                    all_market_data = await self.get_all_market_data()
                    
                    if all_market_data:
                        logger.info(f"🔄 Streaming {len(all_market_data)} symbols")
                        # Store and broadcast each symbol
                        for symbol, market_data in all_market_data.items():
                            logger.debug(f"📊 {symbol} @ ${market_data.close}")
                            self.last_market_data[symbol] = market_data
                            await self._broadcast_market_data(market_data)
                    else:
                        logger.debug("No market data received from bridge")
                else:
                    logger.debug(f"Not connected - state: {self.connection_state}")
                
                await asyncio.sleep(1.0)  # 1 second interval
                
            except Exception as e:
                logger.error(f"Market data streaming error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                await asyncio.sleep(5.0)
    
    
    async def get_market_data(self, symbol: str = None) -> Optional[MarketData]:
        """Get current market data from bridge"""
        if self.connection_state != ConnectionState.CONNECTED:
            return None
        
        try:
            async with self.session.get(f"{self.bridge_url}/api/market_data", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Bridge returns dictionary of symbols
                    if isinstance(data, dict) and data:
                        # If specific symbol requested, return that one
                        if symbol and symbol in data:
                            return MarketData.from_sierra_data(data[symbol])
                        # Otherwise return the first available symbol (primary)
                        first_symbol = next(iter(data.keys()))
                        return MarketData.from_sierra_data(data[first_symbol])
                    return None
                elif resp.status == 404:
                    logger.debug("No market data available from Sierra Chart")
                    return None
                else:
                    logger.warning(f"Market data request failed: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return None
    
    async def get_all_market_data(self) -> Dict[str, MarketData]:
        """Get market data for all symbols from bridge"""
        if self.connection_state != ConnectionState.CONNECTED:
            return {}
        
        try:
            async with self.session.get(f"{self.bridge_url}/api/market_data", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
<<<<<<< HEAD
                    
                    # Get expected symbols from centralized management
                    from ..core.symbol_integration import get_symbol_integration
                    symbol_integration = get_symbol_integration()
                    expected_symbols = set(symbol_integration.get_bridge_symbols())
                    
=======
>>>>>>> 25301bf6f2e931ccc6aab9ec2c45b5c7f4fddfa2
                    # Convert all symbols to MarketData objects
                    result = {}
                    for symbol, symbol_data in data.items():
                        try:
<<<<<<< HEAD
                            # Validate symbol is expected (log warning if unexpected)
                            if symbol not in expected_symbols:
                                logger.debug(f"Bridge providing unexpected symbol: {symbol}")
                            
                            result[symbol] = MarketData.from_sierra_data(symbol_data)
                        except Exception as e:
                            logger.error(f"Failed to parse market data for {symbol}: {e}")
                    
                    # Log if we're missing expected symbols
                    received_symbols = set(result.keys())
                    missing_symbols = expected_symbols - received_symbols
                    if missing_symbols:
                        logger.warning(f"Bridge missing expected symbols: {missing_symbols}")
                    
=======
                            result[symbol] = MarketData.from_sierra_data(symbol_data)
                        except Exception as e:
                            logger.error(f"Failed to parse market data for {symbol}: {e}")
>>>>>>> 25301bf6f2e931ccc6aab9ec2c45b5c7f4fddfa2
                    return result
                else:
                    return {}
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return {}
    
    async def execute_trade(self, trade_command: TradeCommand) -> Optional[TradeResult]:
        """Execute trade via bridge"""
        if self.connection_state != ConnectionState.CONNECTED:
            logger.error("Cannot execute trade - bridge not connected")
            return TradeResult(
                command_id=trade_command.command_id,
                status="REJECTED",
                message="Bridge not connected"
            )
        
        try:
            # Store pending trade
            self.pending_trades[trade_command.command_id] = trade_command
            
            # Send trade command
            async with self.session.post(
                f"{self.bridge_url}/api/trade/execute",
                json=trade_command.to_dict(),
                timeout=10
            ) as resp:
                
                if resp.status == 200:
                    response = await resp.json()
                    logger.info(f"Trade command submitted: {response}")
                    
                    # Wait for execution result
                    await asyncio.sleep(2.0)  # Allow time for execution
                    
                    # Get trade status
                    return await self.get_trade_status(trade_command.command_id)
                    
                else:
                    logger.error(f"Trade submission failed: {resp.status}")
                    return TradeResult(
                        command_id=trade_command.command_id,
                        status="REJECTED",
                        message=f"HTTP {resp.status}"
                    )
        
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return TradeResult(
                command_id=trade_command.command_id,
                status="REJECTED",
                message=str(e)
            )
        finally:
            # Clean up pending trade
            self.pending_trades.pop(trade_command.command_id, None)
    
    async def get_trade_status(self, command_id: str) -> Optional[TradeResult]:
        """Get trade execution status"""
        try:
            async with self.session.get(
                f"{self.bridge_url}/api/trade/status/{command_id}",
                timeout=5
            ) as resp:
                
                if resp.status == 200:
                    data = await resp.json()
                    return TradeResult.from_dict(data)
                else:
                    logger.warning(f"Trade status request failed: {resp.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Trade status error: {e}")
            return None
    
    async def _broadcast_market_data(self, market_data: MarketData):
        """Broadcast market data to subscribers and data handlers"""
        # Notify data handlers first
        await self._notify_data_handlers(market_data)
        
        if not self.market_data_subscribers:
            return
        
        message = {
            'type': 'market_data',
            'data': {
                'timestamp': market_data.timestamp,
                'symbol': market_data.symbol,
                'price': market_data.price,
                'volume': market_data.volume,
                'bid': market_data.bid,
                'ask': market_data.ask
            }
        }
        
        # Broadcast to WebSocket subscribers
        disconnected = []
        for websocket in self.market_data_subscribers.copy():
            try:
                await websocket.send(json.dumps(message))
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected subscribers
        for websocket in disconnected:
            self.market_data_subscribers.discard(websocket)
    
    async def _broadcast_connection_status(self, connected: bool):
        """Broadcast connection status to system"""
        status_message = {
            'type': 'sierra_connection',
            'data': {
                'connected': connected,
                'bridge_url': self.bridge_url,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Broadcast to subscribers
        for websocket in self.market_data_subscribers.copy():
            try:
                await websocket.send(json.dumps(status_message))
            except Exception:
                pass
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections from other MinhOS services"""
        self.market_data_subscribers.add(websocket)
        logger.info(f"New market data subscriber connected: {websocket.remote_address}")
        
        try:
            # Send current connection status
            await self._broadcast_connection_status(
                self.connection_state == ConnectionState.CONNECTED
            )
            
            # Send latest market data if available
            for symbol, data in self.last_market_data.items():
                await self._broadcast_market_data(data)
            
            # Keep connection alive
            async for message in websocket:
                # Handle any incoming requests from subscribers
                try:
                    request = json.loads(message)
                    await self._handle_subscriber_request(websocket, request)
                except Exception as e:
                    logger.error(f"WebSocket message error: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.market_data_subscribers.discard(websocket)
            logger.info(f"Market data subscriber disconnected")
    
    async def _handle_subscriber_request(self, websocket, request: Dict):
        """Handle requests from WebSocket subscribers"""
        req_type = request.get('type')
        
        if req_type == 'get_market_data':
            symbol = request.get('symbol')
            market_data = await self.get_market_data(symbol)
            if market_data:
                await websocket.send(json.dumps({
                    'type': 'market_data_response',
                    'data': market_data.__dict__
                }))
        
        elif req_type == 'execute_trade':
            trade_data = request.get('data', {})
            # Get default symbol from centralized management if none provided
            default_symbol = trade_data.get('symbol')
            if not default_symbol:
                from ..core.symbol_integration import get_symbol_integration
                symbol_integration = get_symbol_integration()
                default_symbol = symbol_integration.get_ai_brain_primary_symbol()
            
            trade_command = TradeCommand(
                command_id=f"minhos_{int(time.time() * 1000)}",
                action=trade_data.get('action', 'BUY'),
                symbol=default_symbol,
                quantity=int(trade_data.get('quantity', 1)),
                price=trade_data.get('price'),
                order_type=trade_data.get('order_type', 'MARKET')
            )
            
            result = await self.execute_trade(trade_command)
            if result:
                await websocket.send(json.dumps({
                    'type': 'trade_result',
                    'data': result.__dict__
                }))
    
    def add_data_handler(self, handler):
        """Add a data handler callback for market data"""
        if not hasattr(self, '_data_handlers'):
            self._data_handlers = []
        self._data_handlers.append(handler)
    
    def add_error_handler(self, handler):
        """Add an error handler callback"""
        if not hasattr(self, '_error_handlers'):
            self._error_handlers = []
        self._error_handlers.append(handler)
    
    async def _notify_data_handlers(self, market_data: MarketData):
        """Notify all data handlers of new market data"""
        if hasattr(self, '_data_handlers'):
            for handler in self._data_handlers:
                try:
                    await handler(market_data)
                except Exception as e:
                    logger.error(f"Data handler error: {e}")
    
    async def _notify_error_handlers(self, error):
        """Notify all error handlers"""
        if hasattr(self, '_error_handlers'):
            for handler in self._error_handlers:
                try:
                    await handler(error)
                except Exception as e:
                    logger.error(f"Error handler error: {e}")
    
    def get_status(self) -> Dict:
        """Get current service status"""
        return {
            'service': 'sierra_client',
            'connection_state': self.connection_state.value,
            'bridge_url': self.bridge_url,
            'symbols_configured': len(self.symbols),
            'active_subscribers': len(self.market_data_subscribers),
            'last_data_symbols': list(self.last_market_data.keys()),
            'pending_trades': len(self.pending_trades)
        }
    
    # Abstract method implementations required by BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        # Connection already set up in __init__
        pass
        
    async def _start_service(self):
        """Start service-specific functionality"""
        logger.info("Starting Sierra Client background tasks...")
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self._connection_manager())
        asyncio.create_task(self._market_data_streamer())
        
    async def _stop_service(self):
        """Stop service-specific functionality"""
        logger.info("Stopping Sierra Client...")
        self.running = False
        
    async def _cleanup(self):
        """Cleanup service resources"""
        if self.session:
            await self.session.close()
        self.pending_trades.clear()

# Service factory functions
_sierra_client_instance = None

def get_sierra_client() -> SierraClient:
    """Get shared Sierra Client instance (singleton pattern)"""
    global _sierra_client_instance
    if _sierra_client_instance is None:
        _sierra_client_instance = SierraClient()
    return _sierra_client_instance

async def create_sierra_client() -> SierraClient:
    """Create and initialize Sierra Client service"""
    client = SierraClient()
    await client.start()
    return client

if __name__ == "__main__":
    # Test mode - run sierra client standalone
    async def main():
        logging.basicConfig(level=logging.INFO)
        client = await create_sierra_client()
        
        try:
            # Keep service running
            while True:
                status = client.get_status()
                logger.info(f"Sierra Client Status: {status}")
                await asyncio.sleep(30)
        except KeyboardInterrupt:
            logger.info("Shutting down Sierra Client...")
        finally:
            await client.stop()
    
    asyncio.run(main())