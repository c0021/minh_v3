#!/usr/bin/env python3
"""
MinhOS v3 Consolidated Market Data Service
==========================================
Unified market data service combining all data-related functionality:
- Real-time data streaming from Sierra Chart bridge
- Historical data access and management
- Multi-timeframe data collection and aggregation
- WebSocket distribution to clients
- HTTP API endpoints for data access
- Unified data store management

Consolidates functionality from:
- market_data.py - WebSocket streaming and HTTP API
- market_data_migrated.py - Unified data store integration
- sierra_client.py - Sierra Chart bridge connection
- sierra_historical_data.py - Historical data access
- multi_chart_collector.py - Multi-timeframe collection
"""

import asyncio
import websockets
import json
import logging
import aiohttp
import time
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Set, Dict, Any, Optional, List, Callable, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import signal
from aiohttp import web
from enum import Enum
import statistics
from collections import defaultdict, deque

# Import models and core components
from ..models.market import MarketData
from ..core.market_data_adapter import get_market_data_adapter
from ..core.base_service import BaseService
from ..core.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market_data_service")

class MessageType(Enum):
    MARKET_DATA = "market_data"
    SYSTEM_STATUS = "system_status"
    SUBSCRIPTION = "subscription"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"
    CHAT = "chat"

class DataSource(Enum):
    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    AGGREGATED = "aggregated"

@dataclass
class WebSocketMessage:
    type: MessageType
    data: Dict[str, Any]
    timestamp: str = ""
    sequence: int = 0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class SierraChartRecord:
    """Represents a single Sierra Chart historical data record"""
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    symbol: str
    timeframe: str
    source_file: str = ""

@dataclass
class MultiChartData:
    """Multi-timeframe market data container"""
    symbol: str
    timestamp: datetime
    timeframes: Dict[str, Dict[str, Any]]  # timeframe -> OHLCV data
    source: DataSource
    
    def get_timeframe_data(self, timeframe: str) -> Optional[Dict[str, Any]]:
        """Get data for specific timeframe"""
        return self.timeframes.get(timeframe)

class MarketDataService(BaseService):
    """
    Consolidated market data service for MinhOS v3
    
    Combines all market data functionality:
    - Real-time streaming from Sierra Chart
    - Historical data access
    - Multi-timeframe collection
    - WebSocket distribution
    - HTTP API endpoints
    """
    
    def __init__(self, ws_port: int = 9001, http_port: int = 9002, sierra_port: int = 9003):
        """Initialize consolidated market data service"""
        super().__init__("market_data_service")
        
        # Port configuration
        self.ws_port = ws_port
        self.http_port = http_port
        self.sierra_port = sierra_port
        
        # Bridge connection settings (from sierra_client.py)
        self.bridge_hostname = self._get_bridge_hostname()
        self.bridge_port = self._get_bridge_port()
        self.bridge_url = f"http://{self.bridge_hostname}:{self.bridge_port}"
        
        # Service state
        self.running = False
        self.connected_to_bridge = False
        
        # WebSocket clients
        self.ws_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_subscriptions: Dict[websockets.WebSocketServerProtocol, Set[str]] = {}
        
        # Data management
        self.market_data_adapter = get_market_data_adapter()
        self.data_buffer = deque(maxlen=1000)  # Recent data buffer
        self.historical_cache = {}  # Symbol -> historical data
        
        # Multi-timeframe configuration
        self.timeframes = ['1min', '5min', '15min', '30min', '1hour', '4hour', 'daily']
        self.timeframe_buffers = {tf: deque(maxlen=1000) for tf in self.timeframes}
        
        # Sierra Chart integration
        self.sierra_session = None
        self.symbols = self._get_symbols()
        self.last_update_time = {}
        
        # Historical data paths
        self.historical_data_paths = self._get_historical_paths()
        
        # Message sequence
        self.message_sequence = 0
        
        # Performance metrics
        self.metrics = {
            'messages_sent': 0,
            'data_points_processed': 0,
            'clients_connected': 0,
            'bridge_reconnections': 0
        }

    def _get_bridge_hostname(self) -> str:
        """Get bridge hostname from configuration"""
        # Try environment variable first
        if 'BRIDGE_HOST' in os.environ:
            return os.environ['BRIDGE_HOST']
        
        # Try config
        if hasattr(config, 'BRIDGE_HOST'):
            return config.BRIDGE_HOST
        
        # Default fallbacks
        return "172.21.128.1"  # Default from minhos_v4.json

    def _get_bridge_port(self) -> int:
        """Get bridge port from configuration"""
        # Try environment variable first
        if 'BRIDGE_PORT' in os.environ:
            return int(os.environ['BRIDGE_PORT'])
        
        # Try config
        if hasattr(config, 'BRIDGE_PORT'):
            return config.BRIDGE_PORT
        
        # Default
        return 8765

    def _get_symbols(self) -> Dict[str, Dict[str, Any]]:
        """Get symbol configuration"""
        # Default symbol configuration
        return {
            'NQU25-CME': {
                'timeframes': ['1min', '5min', '15min', '30min', '1hour', 'daily'],
                'priority': 1,
                'enabled': True
            },
            'ESU25-CME': {
                'timeframes': ['1min', '5min', '30min'],
                'priority': 2,
                'enabled': True
            }
        }

    def _get_historical_paths(self) -> List[Path]:
        """Get Sierra Chart historical data paths"""
        possible_paths = [
            Path("C:/SierraChart/Data"),  # Windows default
            Path("/mnt/c/SierraChart/Data"),  # WSL
            Path("./data/sierra_chart"),  # Local development
            Path("./data/historical")  # Fallback
        ]
        
        valid_paths = [path for path in possible_paths if path.exists()]
        if not valid_paths:
            # Create local data directory
            local_path = Path("./data/historical")
            local_path.mkdir(parents=True, exist_ok=True)
            valid_paths = [local_path]
        
        return valid_paths

    # ========== SIERRA CHART BRIDGE CONNECTION (from sierra_client.py) ==========
    
    async def connect_to_sierra_bridge(self) -> bool:
        """Establish connection to Sierra Chart bridge"""
        try:
            logger.info(f"🔌 Connecting to Sierra Chart bridge at {self.bridge_url}")
            
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=10)
            self.sierra_session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection
            async with self.sierra_session.get(f"{self.bridge_url}/status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    logger.info(f"✅ Connected to Sierra Chart bridge: {status_data}")
                    self.connected_to_bridge = True
                    return True
                else:
                    logger.error(f"❌ Bridge connection failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Sierra Chart bridge connection error: {e}")
            self.connected_to_bridge = False
            return False

    async def fetch_realtime_data(self) -> Optional[Dict[str, Any]]:
        """Fetch real-time data from Sierra Chart bridge"""
        if not self.connected_to_bridge or not self.sierra_session:
            return None
        
        try:
            # Get latest data for all symbols
            async with self.sierra_session.get(f"{self.bridge_url}/latest") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process and standardize data
                    if 'data' in data:
                        processed_data = self._process_sierra_data(data['data'])
                        return processed_data
                else:
                    logger.warning(f"⚠️ Failed to fetch data: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Real-time data fetch error: {e}")
            return None

    def _process_sierra_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Sierra Chart data into standardized format"""
        try:
            # Standardize Sierra Chart data format
            processed = {
                'timestamp': raw_data.get('timestamp', datetime.now().isoformat()),
                'symbol': raw_data.get('symbol', 'UNKNOWN'),
                'open': float(raw_data.get('open', 0)),
                'high': float(raw_data.get('high', 0)),
                'low': float(raw_data.get('low', 0)),
                'close': float(raw_data.get('close', 0)),
                'volume': int(raw_data.get('volume', 0)),
                'bid': float(raw_data.get('bid', 0)),
                'ask': float(raw_data.get('ask', 0)),
                'source': 'sierra_chart'
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"❌ Data processing error: {e}")
            return {}

    # ========== HISTORICAL DATA ACCESS (from sierra_historical_data.py) ==========
    
    async def get_historical_data(self, symbol: str, start_date: str, end_date: str, 
                                timeframe: str = "1min") -> List[SierraChartRecord]:
        """Get historical data for symbol between dates"""
        try:
            records = []
            
            # Try to load from Sierra Chart files
            sierra_records = await self._load_sierra_historical_files(symbol, start_date, end_date, timeframe)
            records.extend(sierra_records)
            
            # If no Sierra Chart data, try database
            if not records:
                db_records = await self._load_historical_from_db(symbol, start_date, end_date, timeframe)
                records.extend(db_records)
            
            logger.info(f"📊 Loaded {len(records)} historical records for {symbol}")
            return records
            
        except Exception as e:
            logger.error(f"❌ Historical data error for {symbol}: {e}")
            return []

    async def _load_sierra_historical_files(self, symbol: str, start_date: str, 
                                          end_date: str, timeframe: str) -> List[SierraChartRecord]:
        """Load historical data from Sierra Chart files"""
        records = []
        
        try:
            for data_path in self.historical_data_paths:
                # Look for symbol files in Sierra Chart format
                pattern = f"{symbol}*.dly"  # Daily files
                if timeframe == "1min":
                    pattern = f"{symbol}*.scid"  # Intraday files
                
                for file_path in data_path.glob(pattern):
                    file_records = await self._parse_sierra_file(file_path, symbol, timeframe)
                    
                    # Filter by date range
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    
                    filtered_records = [
                        record for record in file_records
                        if start_dt <= record.timestamp <= end_dt
                    ]
                    
                    records.extend(filtered_records)
                    
                if records:  # Found data in this path
                    break
                    
        except Exception as e:
            logger.error(f"❌ Sierra Chart file loading error: {e}")
        
        return records

    async def _parse_sierra_file(self, file_path: Path, symbol: str, timeframe: str) -> List[SierraChartRecord]:
        """Parse Sierra Chart data file"""
        records = []
        
        try:
            # Simple CSV-like parsing for Sierra Chart files
            # Note: This is a simplified parser - real Sierra Chart files are binary
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f):
                    if line_num > 1000:  # Limit for performance
                        break
                    
                    try:
                        # Parse comma-separated values
                        parts = line.strip().split(',')
                        if len(parts) >= 6:
                            timestamp = datetime.fromisoformat(parts[0])
                            record = SierraChartRecord(
                                timestamp=timestamp,
                                open_price=float(parts[1]),
                                high_price=float(parts[2]),
                                low_price=float(parts[3]),
                                close_price=float(parts[4]),
                                volume=int(float(parts[5])),
                                symbol=symbol,
                                timeframe=timeframe,
                                source_file=str(file_path)
                            )
                            records.append(record)
                    except (ValueError, IndexError):
                        continue  # Skip malformed lines
                        
        except Exception as e:
            logger.debug(f"File parsing error for {file_path}: {e}")
        
        return records

    async def _load_historical_from_db(self, symbol: str, start_date: str, 
                                     end_date: str, timeframe: str) -> List[SierraChartRecord]:
        """Load historical data from local database"""
        # TODO: Implement database historical data loading
        return []

    # ========== MULTI-TIMEFRAME COLLECTION (from multi_chart_collector.py) ==========
    
    async def collect_multi_timeframe_data(self, symbol: str) -> MultiChartData:
        """Collect data across multiple timeframes for symbol"""
        try:
            timeframe_data = {}
            
            for timeframe in self.timeframes:
                # Get latest data for this timeframe
                data = await self._get_timeframe_data(symbol, timeframe)
                if data:
                    timeframe_data[timeframe] = data
            
            multi_data = MultiChartData(
                symbol=symbol,
                timestamp=datetime.now(),
                timeframes=timeframe_data,
                source=DataSource.REAL_TIME
            )
            
            return multi_data
            
        except Exception as e:
            logger.error(f"❌ Multi-timeframe collection error for {symbol}: {e}")
            return MultiChartData(symbol, datetime.now(), {}, DataSource.REAL_TIME)

    async def _get_timeframe_data(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """Get latest data for specific symbol and timeframe"""
        try:
            # Try to get from buffer first
            if timeframe in self.timeframe_buffers:
                buffer = self.timeframe_buffers[timeframe]
                if buffer:
                    latest = buffer[-1]
                    if latest.get('symbol') == symbol:
                        return latest
            
            # If not in buffer, fetch from real-time
            current_data = await self.fetch_realtime_data()
            if current_data and current_data.get('symbol') == symbol:
                return current_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Timeframe data error for {symbol}/{timeframe}: {e}")
            return None

    async def aggregate_timeframes(self, symbol: str, base_timeframe: str = "1min") -> Dict[str, Any]:
        """Aggregate base timeframe data into higher timeframes"""
        try:
            # Get base timeframe data
            base_data = await self._get_timeframe_data(symbol, base_timeframe)
            if not base_data:
                return {}
            
            aggregated = {}
            
            # Simple aggregation logic (can be enhanced)
            for target_timeframe in ['5min', '15min', '30min', '1hour']:
                if target_timeframe != base_timeframe:
                    agg_data = self._aggregate_ohlcv(base_data, target_timeframe)
                    if agg_data:
                        aggregated[target_timeframe] = agg_data
            
            return aggregated
            
        except Exception as e:
            logger.error(f"❌ Timeframe aggregation error: {e}")
            return {}

    def _aggregate_ohlcv(self, base_data: Dict[str, Any], target_timeframe: str) -> Dict[str, Any]:
        """Aggregate OHLCV data to target timeframe"""
        # Simplified aggregation - in production this would use proper time-based grouping
        return {
            'symbol': base_data.get('symbol'),
            'timestamp': base_data.get('timestamp'),
            'open': base_data.get('open'),
            'high': base_data.get('high'),
            'low': base_data.get('low'),
            'close': base_data.get('close'),
            'volume': base_data.get('volume'),
            'timeframe': target_timeframe,
            'source': 'aggregated'
        }

    # ========== WEBSOCKET STREAMING (from market_data.py/migrated) ==========
    
    async def start_websocket_server(self):
        """Start WebSocket server for real-time data distribution"""
        try:
            logger.info(f"🚀 Starting WebSocket server on port {self.ws_port}")
            
            start_server = websockets.serve(
                self.handle_websocket_client,
                "0.0.0.0",
                self.ws_port,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.ws_server = await start_server
            logger.info(f"✅ WebSocket server running on ws://0.0.0.0:{self.ws_port}")
            
        except Exception as e:
            logger.error(f"❌ WebSocket server start error: {e}")
            raise

    async def handle_websocket_client(self, websocket, path):
        """Handle individual WebSocket client connections"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"👤 WebSocket client connected: {client_id}")
        
        self.ws_clients.add(websocket)
        self.client_subscriptions[websocket] = set()
        self.metrics['clients_connected'] = len(self.ws_clients)
        
        try:
            await self._send_welcome_message(websocket)
            
            async for message in websocket:
                await self._handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"👋 WebSocket client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"❌ WebSocket client error for {client_id}: {e}")
        finally:
            self.ws_clients.discard(websocket)
            self.client_subscriptions.pop(websocket, None)
            self.metrics['clients_connected'] = len(self.ws_clients)

    async def _send_welcome_message(self, websocket):
        """Send welcome message to new client"""
        welcome_msg = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={
                "status": "connected",
                "server": "MinhOS Market Data Service",
                "version": "3.0.0",
                "available_symbols": list(self.symbols.keys()),
                "available_timeframes": self.timeframes
            }
        )
        await self._send_message(websocket, welcome_msg)

    async def _handle_client_message(self, websocket, message: str):
        """Handle incoming client messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type', '')
            
            if msg_type == 'subscribe':
                symbols = data.get('symbols', [])
                await self._handle_subscription(websocket, symbols)
            elif msg_type == 'unsubscribe':
                symbols = data.get('symbols', [])
                await self._handle_unsubscription(websocket, symbols)
            elif msg_type == 'ping':
                await self._handle_ping(websocket)
            else:
                logger.warning(f"⚠️ Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON from client")
        except Exception as e:
            logger.error(f"❌ Client message handling error: {e}")

    async def _handle_subscription(self, websocket, symbols: List[str]):
        """Handle client symbol subscriptions"""
        if websocket in self.client_subscriptions:
            self.client_subscriptions[websocket].update(symbols)
            
            response = WebSocketMessage(
                type=MessageType.SUBSCRIPTION,
                data={
                    "action": "subscribed",
                    "symbols": symbols,
                    "total_subscriptions": len(self.client_subscriptions[websocket])
                }
            )
            await self._send_message(websocket, response)

    async def _handle_unsubscription(self, websocket, symbols: List[str]):
        """Handle client symbol unsubscriptions"""
        if websocket in self.client_subscriptions:
            self.client_subscriptions[websocket] -= set(symbols)
            
            response = WebSocketMessage(
                type=MessageType.SUBSCRIPTION,
                data={
                    "action": "unsubscribed",
                    "symbols": symbols,
                    "total_subscriptions": len(self.client_subscriptions[websocket])
                }
            )
            await self._send_message(websocket, response)

    async def _handle_ping(self, websocket):
        """Handle ping messages"""
        pong_msg = WebSocketMessage(
            type=MessageType.PONG,
            data={"timestamp": datetime.now().isoformat()}
        )
        await self._send_message(websocket, pong_msg)

    async def _send_message(self, websocket, message: WebSocketMessage):
        """Send message to specific client"""
        try:
            message.sequence = self.message_sequence
            self.message_sequence += 1
            
            json_data = json.dumps(asdict(message))
            await websocket.send(json_data)
            self.metrics['messages_sent'] += 1
            
        except Exception as e:
            logger.error(f"❌ Message send error: {e}")

    async def broadcast_market_data(self, market_data: Dict[str, Any]):
        """Broadcast market data to subscribed clients"""
        if not self.ws_clients:
            return
        
        try:
            symbol = market_data.get('symbol', '')
            
            # Create broadcast message
            broadcast_msg = WebSocketMessage(
                type=MessageType.MARKET_DATA,
                data=market_data
            )
            
            # Send to subscribed clients
            disconnected_clients = set()
            
            for websocket in self.ws_clients:
                try:
                    client_subscriptions = self.client_subscriptions.get(websocket, set())
                    
                    # Send if client is subscribed to this symbol or subscribed to all
                    if not client_subscriptions or symbol in client_subscriptions or '*' in client_subscriptions:
                        await self._send_message(websocket, broadcast_msg)
                        
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(websocket)
                except Exception as e:
                    logger.error(f"❌ Broadcast error: {e}")
                    disconnected_clients.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected_clients:
                self.ws_clients.discard(websocket)
                self.client_subscriptions.pop(websocket, None)
            
            self.metrics['clients_connected'] = len(self.ws_clients)
            
        except Exception as e:
            logger.error(f"❌ Market data broadcast error: {e}")

    # ========== HTTP API (from market_data.py/migrated) ==========
    
    async def start_http_server(self):
        """Start HTTP API server"""
        try:
            app = web.Application()
            
            # Add routes
            app.router.add_get('/latest', self.handle_latest_data)
            app.router.add_get('/latest/{symbol}', self.handle_latest_symbol_data)
            app.router.add_get('/historical/{symbol}', self.handle_historical_data)
            app.router.add_get('/symbols', self.handle_symbols_list)
            app.router.add_get('/status', self.handle_status)
            app.router.add_get('/metrics', self.handle_metrics)
            
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', self.http_port)
            await site.start()
            
            logger.info(f"✅ HTTP API server running on http://0.0.0.0:{self.http_port}")
            
        except Exception as e:
            logger.error(f"❌ HTTP server start error: {e}")
            raise

    async def handle_latest_data(self, request):
        """Handle /latest endpoint"""
        try:
            # Get latest data for all symbols
            latest_data = {}
            
            for symbol in self.symbols.keys():
                data = await self.fetch_realtime_data()
                if data and data.get('symbol') == symbol:
                    latest_data[symbol] = data
            
            return web.json_response({
                "timestamp": datetime.now().isoformat(),
                "data": latest_data,
                "count": len(latest_data)
            })
            
        except Exception as e:
            logger.error(f"❌ Latest data endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_latest_symbol_data(self, request):
        """Handle /latest/{symbol} endpoint"""
        try:
            symbol = request.match_info['symbol']
            
            # Get multi-timeframe data for symbol
            multi_data = await self.collect_multi_timeframe_data(symbol)
            
            return web.json_response({
                "symbol": symbol,
                "timestamp": multi_data.timestamp.isoformat(),
                "timeframes": multi_data.timeframes,
                "source": multi_data.source.value
            })
            
        except Exception as e:
            logger.error(f"❌ Symbol data endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_historical_data(self, request):
        """Handle /historical/{symbol} endpoint"""
        try:
            symbol = request.match_info['symbol']
            start_date = request.query.get('start', (datetime.now() - timedelta(days=7)).isoformat())
            end_date = request.query.get('end', datetime.now().isoformat())
            timeframe = request.query.get('timeframe', '1min')
            
            records = await self.get_historical_data(symbol, start_date, end_date, timeframe)
            
            # Convert records to JSON-serializable format
            data = []
            for record in records:
                data.append({
                    "timestamp": record.timestamp.isoformat(),
                    "open": record.open_price,
                    "high": record.high_price,
                    "low": record.low_price,
                    "close": record.close_price,
                    "volume": record.volume,
                    "symbol": record.symbol,
                    "timeframe": record.timeframe
                })
            
            return web.json_response({
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "timeframe": timeframe,
                "count": len(data),
                "data": data
            })
            
        except Exception as e:
            logger.error(f"❌ Historical data endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_symbols_list(self, request):
        """Handle /symbols endpoint"""
        return web.json_response({
            "symbols": list(self.symbols.keys()),
            "symbol_config": self.symbols,
            "timeframes": self.timeframes
        })

    async def handle_status(self, request):
        """Handle /status endpoint"""
        return web.json_response({
            "service": "MinhOS Market Data Service",
            "version": "3.0.0",
            "status": "running" if self.running else "stopped",
            "bridge_connected": self.connected_to_bridge,
            "bridge_url": self.bridge_url,
            "websocket_clients": len(self.ws_clients),
            "timestamp": datetime.now().isoformat()
        })

    async def handle_metrics(self, request):
        """Handle /metrics endpoint"""
        return web.json_response({
            "metrics": self.metrics,
            "websocket_clients": len(self.ws_clients),
            "active_subscriptions": sum(len(subs) for subs in self.client_subscriptions.values()),
            "symbols_tracked": len(self.symbols),
            "timeframes_supported": len(self.timeframes),
            "timestamp": datetime.now().isoformat()
        })

    # ========== SERVICE LIFECYCLE ==========
    
    async def start(self):
        """Start the consolidated market data service"""
        try:
            logger.info("🚀 Starting consolidated Market Data Service...")
            self.running = True
            
            # Connect to Sierra Chart bridge
            await self.connect_to_sierra_bridge()
            
            # Start WebSocket server
            await self.start_websocket_server()
            
            # Start HTTP API server
            await self.start_http_server()
            
            # Start data collection loop
            asyncio.create_task(self.data_collection_loop())
            
            logger.info("✅ Market Data Service fully operational")
            
        except Exception as e:
            logger.error(f"❌ Market Data Service start error: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stop the market data service"""
        try:
            logger.info("🛑 Stopping Market Data Service...")
            self.running = False
            
            # Close WebSocket connections
            if self.ws_clients:
                await asyncio.gather(
                    *[ws.close() for ws in self.ws_clients],
                    return_exceptions=True
                )
                self.ws_clients.clear()
                self.client_subscriptions.clear()
            
            # Close Sierra Chart session
            if self.sierra_session:
                await self.sierra_session.close()
                self.sierra_session = None
            
            self.connected_to_bridge = False
            logger.info("✅ Market Data Service stopped")
            
        except Exception as e:
            logger.error(f"❌ Market Data Service stop error: {e}")

    async def data_collection_loop(self):
        """Main data collection and distribution loop"""
        logger.info("🔄 Starting data collection loop...")
        
        while self.running:
            try:
                # Fetch real-time data
                data = await self.fetch_realtime_data()
                
                if data:
                    # Store in unified data store
                    await self.market_data_adapter.store_market_data(data)
                    
                    # Add to buffer
                    self.data_buffer.append(data)
                    
                    # Update timeframe buffers
                    await self._update_timeframe_buffers(data)
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_market_data(data)
                    
                    # Update metrics
                    self.metrics['data_points_processed'] += 1
                    
                    # Update last update time
                    symbol = data.get('symbol', '')
                    self.last_update_time[symbol] = datetime.now()
                
                # Sleep briefly to avoid overwhelming the system
                await asyncio.sleep(1.0)  # 1 second interval
                
            except Exception as e:
                logger.error(f"❌ Data collection loop error: {e}")
                await asyncio.sleep(5.0)  # Longer sleep on error

    async def _update_timeframe_buffers(self, data: Dict[str, Any]):
        """Update timeframe-specific data buffers"""
        try:
            # For now, just store in 1min buffer
            # In production, this would aggregate data by timeframes
            if '1min' in self.timeframe_buffers:
                self.timeframe_buffers['1min'].append(data)
                
        except Exception as e:
            logger.error(f"❌ Timeframe buffer update error: {e}")
    
    # Implement required abstract methods from BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        # Initialize session and adapters
        self.sierra_session = aiohttp.ClientSession()
        
    async def _start_service(self):
        """Start service-specific functionality"""
        # Connect to Sierra Chart bridge
        await self.connect_to_sierra_bridge()
        
        # Start WebSocket server
        await self.start_websocket_server()
        
        # Start HTTP API server
        await self.start_http_server()
        
        # Start data collection loop
        asyncio.create_task(self.data_collection_loop())
        
        self.running = True
        logger.info("✅ Market Data Service fully operational")
        
    async def _stop_service(self):
        """Stop service-specific functionality"""
        self.running = False
        
        # Close WebSocket connections
        if self.ws_clients:
            await asyncio.gather(*[ws.close() for ws in self.ws_clients])
            
        # Close HTTP session
        if self.sierra_session:
            await self.sierra_session.close()
            
    async def _cleanup(self):
        """Cleanup service resources"""
        # Clear data buffers
        self.data_buffer.clear()
        self.historical_cache.clear()
        for buffer in self.timeframe_buffers.values():
            buffer.clear()
    
    async def get_current_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current market data for a symbol"""
        # Get latest data from market data adapter
        latest_data = self.market_data_adapter.get_latest_data(symbol)
        if latest_data:
            # Check if it's a dataclass or dict
            if hasattr(latest_data, '__dataclass_fields__'):
                return asdict(latest_data)
            elif isinstance(latest_data, dict):
                return latest_data
            else:
                # Convert to dict if it has the necessary attributes
                return {
                    'symbol': getattr(latest_data, 'symbol', symbol),
                    'price': getattr(latest_data, 'price', 0),
                    'timestamp': str(getattr(latest_data, 'timestamp', datetime.now())),
                    'volume': getattr(latest_data, 'volume', 0),
                    'bid': getattr(latest_data, 'bid', 0),
                    'ask': getattr(latest_data, 'ask', 0)
                }
        
        # Fallback to fetching from bridge
        bridge_data = await self.fetch_realtime_data()
        if bridge_data and symbol in bridge_data:
            return bridge_data[symbol]
            
        return None

# Global service instance
_market_data_service = None

def get_market_data_service() -> MarketDataService:
    """Get global market data service instance"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service


# For backward compatibility
def get_sierra_client():
    """Legacy compatibility - redirects to market data service"""
    return get_market_data_service()

def get_sierra_historical_service():
    """Legacy compatibility - redirects to market data service"""
    return get_market_data_service()

async def main():
    """Test the Market Data Service"""
    service = MarketDataService()
    
    try:
        await service.start()
        logger.info("Market Data Service running. Press Ctrl+C to stop...")
        
        # Keep running
        while service.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())