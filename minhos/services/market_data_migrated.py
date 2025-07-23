#!/usr/bin/env python3
"""
MinhOS v3 Market Data Service (Migrated)
=======================================
Linux-native real-time market data streaming service.
Now uses unified market data store as single source of truth.
"""

import asyncio
import websockets
import json
import logging
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Set, Dict, Any, Optional, List, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import signal
from aiohttp import web
from enum import Enum

# Import Sierra client
from .sierra_client import SierraClient, get_sierra_client
from ..models.market import MarketData

# Import unified market data store
from ..core.market_data_adapter import get_market_data_adapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market_data")

class MessageType(Enum):
    MARKET_DATA = "market_data"
    SYSTEM_STATUS = "system_status"
    SUBSCRIPTION = "subscription"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"
    CHAT = "chat"

@dataclass
class WebSocketMessage:
    type: MessageType
    data: Dict[str, Any]
    timestamp: str = ""
    sequence: int = 0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class MarketDataService:
    """
    Real-time market data streaming service
    Linux-native with WebSocket and HTTP APIs
    Now uses unified market data store
    """
    
    def __init__(self, ws_port: int = 9001, http_port: int = 9002):
        """Initialize market data service"""
        self.ws_port = ws_port
        self.http_port = http_port
        
        # WebSocket clients
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_subscriptions: Dict[websockets.WebSocketServerProtocol, Set[str]] = {}
        
        # Service state
        self.running = False
        self.ws_server = None
        self.http_server = None
        self.start_time = datetime.now()
        
        # Market data - NOW USING UNIFIED STORE
        self.market_data_adapter = get_market_data_adapter()
        self.last_data_time = None
        self.data_sequence = 0
        
        # Chat functionality
        self.chat_messages = []
        self.max_chat_messages = 100
        
        # Statistics
        self.stats = {
            "clients_connected": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "data_updates": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
            "uptime_seconds": 0
        }
        
        # Sierra Chart client
        self.sierra_client: Optional[SierraClient] = None
        
        # Performance monitoring
        self.performance_metrics = {
            "avg_broadcast_time_ms": 0.0,
            "max_broadcast_time_ms": 0.0,
            "broadcast_count": 0,
            "slow_broadcasts": 0,
            "fast_broadcasts": 0
        }
    
    @property
    def latest_data(self) -> Dict[str, MarketData]:
        """Get latest data from unified store"""
        return self.market_data_adapter.get_latest_data()
    
    async def start(self):
        """Start the market data service"""
        logger.info("🚀 Starting Market Data Service (with unified store)...")
        
        try:
            # Start unified data store
            await self.market_data_adapter.start()
            
            # Subscribe to market data updates
            await self.market_data_adapter.subscribe(self._on_market_data_update)
            
            # Initialize Sierra Chart client
            self.sierra_client = get_sierra_client()
            self.sierra_client.add_data_handler(self._on_market_data)
            self.sierra_client.add_error_handler(self._on_sierra_error)
            
            # Start servers
            await self._start_websocket_server()
            await self._start_http_server()
            
            # Start health check loop
            asyncio.create_task(self._health_broadcast_loop())
            
            self.running = True
            logger.info("✅ Market Data Service started successfully")
            
            # Keep running
            await self._run_forever()
            
        except Exception as e:
            logger.error(f"❌ Failed to start service: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the market data service"""
        logger.info("🛑 Stopping Market Data Service...")
        self.running = False
        
        try:
            # Stop unified data store
            await self.market_data_adapter.stop()
            
            # Close WebSocket connections
            if self.clients:
                await asyncio.gather(*[
                    client.close() for client in self.clients
                ], return_exceptions=True)
            
            # Stop servers
            if self.ws_server:
                self.ws_server.close()
                await self.ws_server.wait_closed()
            
            if self.http_server:
                await self.http_server.stop()
            
            logger.info("✅ Market Data Service stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping service: {e}")
    
    async def _start_websocket_server(self):
        """Start WebSocket server"""
        try:
            self.ws_server = await websockets.serve(
                self._handle_websocket_client,
                "0.0.0.0",
                self.ws_port,
                max_size=10 * 1024 * 1024,  # 10MB max message size
                ping_interval=30,
                ping_timeout=10
            )
            logger.info(f"✅ WebSocket server started on port {self.ws_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")
            raise
    
    async def _start_http_server(self):
        """Start HTTP API server"""
        try:
            app = web.Application()
            
            # API routes
            app.router.add_get('/health', self._handle_health)
            app.router.add_get('/api/market_data', self._handle_api_market_data)
            app.router.add_get('/api/symbols', self._handle_api_symbols)
            app.router.add_get('/api/stats', self._handle_api_stats)
            app.router.add_post('/api/notify', self._handle_api_notify)
            
            # Start server
            runner = web.AppRunner(app)
            await runner.setup()
            self.http_server = web.TCPSite(runner, '0.0.0.0', self.http_port)
            await self.http_server.start()
            
            logger.info(f"✅ HTTP server started on port {self.http_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start HTTP server: {e}")
            raise
    
    async def _handle_websocket_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle WebSocket client connections"""
        await self._register_client(websocket)
        
        try:
            async for message in websocket:
                await self._handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Client connection closed")
        except Exception as e:
            logger.error(f"❌ WebSocket client error: {e}")
        finally:
            await self._unregister_client(websocket)
    
    async def _register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        self.client_subscriptions[websocket] = {"market_data", "system_status"}  # Default subscriptions
        self.stats["clients_connected"] = len(self.clients)
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"✅ Client connected: {client_info} (Total: {len(self.clients)})")
        
        # Send current data to new client
        latest_data = self.market_data_adapter.get_latest_data()
        if latest_data:
            for symbol, data in latest_data.items():
                await self._send_to_client(websocket, {
                    "type": MessageType.MARKET_DATA.value,
                    "data": asdict(data),
                    "symbol": symbol
                })
        
        # Send recent chat messages
        if self.chat_messages:
            await self._send_to_client(websocket, {
                "type": MessageType.CHAT.value,
                "data": {
                    "messages": self.chat_messages[-20:]  # Last 20 messages
                }
            })
    
    async def _on_market_data(self, market_data: MarketData):
        """Handle market data from Sierra Chart client"""
        try:
            # Store in unified data store
            await self.market_data_adapter.async_add_data(market_data)
            
            self.last_data_time = datetime.now()
            self.data_sequence += 1
            self.stats["data_updates"] += 1
            
            logger.debug(f"📊 Stored in unified store: {market_data.symbol} @ ${market_data.close}")
            
        except Exception as e:
            logger.error(f"❌ Market data storage error: {e}")
            self.stats["errors"] += 1
    
    async def _on_market_data_update(self, market_data: MarketData):
        """Handle market data updates from unified store"""
        try:
            # Broadcast to WebSocket clients
            await self._broadcast_message({
                "type": MessageType.MARKET_DATA.value,
                "data": asdict(market_data),
                "sequence": self.data_sequence,
                "timestamp": datetime.now().isoformat()
            }, "market_data")
            
            logger.debug(f"📡 Broadcasted from store: {market_data.symbol} @ ${market_data.close}")
            
        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}")
    
    # ... rest of the methods remain the same ...
    
    async def _handle_api_market_data(self, request):
        """Handle market data API request"""
        symbol = request.query.get('symbol')
        
        if symbol:
            data = self.market_data_adapter.get_market_data(symbol)
            if data:
                return web.json_response({
                    "status": "success",
                    "data": asdict(data),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return web.json_response({
                    "status": "error",
                    "error": f"No data for symbol: {symbol}"
                }, status=404)
        else:
            # Return all data
            all_data = self.market_data_adapter.get_all_market_data()
            return web.json_response({
                "status": "success",
                "data": {symbol: asdict(data) for symbol, data in all_data.items()},
                "count": len(all_data),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_api_symbols(self, request):
        """Handle symbols API request"""
        symbols = self.market_data_adapter.get_symbols()
        return web.json_response({
            "status": "success",
            "symbols": symbols,
            "count": len(symbols),
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_api_stats(self, request):
        """Handle stats API request"""
        # Get store statistics
        store_stats = self.market_data_adapter.get_stats()
        
        return web.json_response({
            "status": "success",
            "service_stats": self.stats,
            "store_stats": store_stats,
            "performance": self.performance_metrics,
            "timestamp": datetime.now().isoformat()
        })


async def main():
    """Main entry point"""
    service = MarketDataService()
    
    # Handle signals
    def signal_handler(sig, frame):
        logger.info("🛑 Received shutdown signal")
        asyncio.create_task(service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await service.start()
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())