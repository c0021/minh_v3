#!/usr/bin/env python3
"""
MinhOS v3 Market Data Service
============================
Linux-native real-time market data streaming service.
Replaces websocket_server.py with clean architecture and no Windows dependencies.

Provides WebSocket streaming, HTTP API, and real-time data distribution
for all connected clients and services.
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
        
        # Market data
        self.latest_data: Dict[str, MarketData] = {}
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
            "slow_broadcasts": 0,
            "fast_broadcasts": 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🔥 Market Data Service initialized (Linux-native)")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start(self):
        """Start the market data service"""
        logger.info("🚀 Starting Market Data Service...")
        self.running = True
        
        try:
            # Initialize Sierra Chart client
            self.sierra_client = get_sierra_client()
            self.sierra_client.add_data_handler(self._on_market_data)
            self.sierra_client.add_error_handler(self._on_sierra_error)
            
            # Start WebSocket server
            await self._start_websocket_server()
            
            # Start HTTP server
            await self._start_http_server()
            
            # Start Sierra Chart client
            asyncio.create_task(self.sierra_client.start())
            
            # Start service loops
            asyncio.create_task(self._health_broadcast_loop())
            asyncio.create_task(self._statistics_loop())
            
            logger.info("✅ Market Data Service started successfully")
            logger.info(f"   WebSocket: ws://localhost:{self.ws_port}")
            logger.info(f"   HTTP API: http://localhost:{self.http_port}")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Failed to start Market Data Service: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the market data service"""
        logger.info("🛑 Stopping Market Data Service...")
        self.running = False
        
        # Stop Sierra Chart client
        if self.sierra_client:
            await self.sierra_client.stop()
        
        # Notify clients
        if self.clients:
            await self._broadcast_message({
                "type": MessageType.SYSTEM_STATUS.value,
                "data": {
                    "status": "stopping",
                    "message": "Server is shutting down"
                }
            })
            
            # Close all client connections
            for client in self.clients.copy():
                try:
                    await client.close()
                except:
                    pass
        
        # Stop servers
        if self.ws_server:
            self.ws_server.close()
            await self.ws_server.wait_closed()
            logger.info("WebSocket server stopped")
        
        if self.http_server:
            await self.http_server.stop()
            logger.info("HTTP server stopped")
    
    async def _start_websocket_server(self):
        """Start WebSocket server"""
        try:
            self.ws_server = await websockets.serve(
                self._handle_websocket_client,
                "0.0.0.0",
                self.ws_port
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
        if self.latest_data:
            for symbol, data in self.latest_data.items():
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
    
    async def _unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        self.client_subscriptions.pop(websocket, None)
        self.stats["clients_connected"] = len(self.clients)
        
        try:
            client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            logger.info(f"❌ Client disconnected: {client_info} (Total: {len(self.clients)})")
        except:
            logger.info(f"❌ Client disconnected (Total: {len(self.clients)})")
    
    async def _handle_client_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            self.stats["messages_received"] += 1
            
            if msg_type == "ping":
                await self._send_to_client(websocket, {
                    "type": MessageType.PONG.value,
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "server_time": time.time()
                    }
                })
            
            elif msg_type == "subscribe":
                # Update client subscriptions
                subscriptions = data.get("subscriptions", ["market_data"])
                self.client_subscriptions[websocket] = set(subscriptions)
                
                await self._send_to_client(websocket, {
                    "type": MessageType.SUBSCRIPTION.value,
                    "data": {
                        "subscriptions": list(subscriptions),
                        "status": "confirmed"
                    }
                })
            
            elif msg_type == "get_status":
                status = self._get_service_status()
                await self._send_to_client(websocket, {
                    "type": MessageType.SYSTEM_STATUS.value,
                    "data": status
                })
            
            elif msg_type == "chat":
                await self._handle_chat_message(websocket, data.get("data", {}))
            
            elif msg_type == "get_symbols":
                symbols_data = {symbol: asdict(data) for symbol, data in self.latest_data.items()}
                await self._send_to_client(websocket, {
                    "type": "symbols",
                    "data": symbols_data
                })
            
        except json.JSONDecodeError:
            await self._send_to_client(websocket, {
                "type": MessageType.ERROR.value,
                "data": {
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }
            })
        except Exception as e:
            logger.error(f"❌ Client message handling error: {e}")
    
    async def _handle_chat_message(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle chat messages"""
        try:
            username = data.get("username", "Anonymous")
            message = data.get("message", "").strip()
            
            if not message:
                return
            
            chat_message = {
                "id": len(self.chat_messages) + 1,
                "username": username,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "client_ip": websocket.remote_address[0] if hasattr(websocket, 'remote_address') else "unknown"
            }
            
            self.chat_messages.append(chat_message)
            
            # Keep only recent messages
            if len(self.chat_messages) > self.max_chat_messages:
                self.chat_messages = self.chat_messages[-self.max_chat_messages:]
            
            # Broadcast to all clients
            await self._broadcast_message({
                "type": MessageType.CHAT.value,
                "data": {
                    "message": chat_message
                }
            })
            
            logger.info(f"💬 {username}: {message}")
            
        except Exception as e:
            logger.error(f"❌ Chat message error: {e}")
    
    async def _send_to_client(self, websocket: websockets.WebSocketServerProtocol, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(message))
            self.stats["messages_sent"] += 1
            
        except websockets.exceptions.ConnectionClosed:
            await self._unregister_client(websocket)
        except Exception as e:
            logger.error(f"❌ Send to client error: {e}")
            await self._unregister_client(websocket)
    
    async def _broadcast_message(self, message: Dict[str, Any], subscription_filter: str = None):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        start_time = time.time()
        
        # Filter clients by subscription
        target_clients = []
        for client in self.clients.copy():
            if subscription_filter:
                client_subs = self.client_subscriptions.get(client, set())
                if subscription_filter in client_subs:
                    target_clients.append(client)
            else:
                target_clients.append(client)
        
        # Send to all target clients
        if target_clients:
            tasks = [self._send_to_client(client, message) for client in target_clients]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Track performance
        broadcast_time_ms = (time.time() - start_time) * 1000
        self._update_broadcast_performance(broadcast_time_ms)
    
    def _update_broadcast_performance(self, broadcast_time_ms: float):
        """Update broadcast performance metrics"""
        # Update average
        if self.performance_metrics["avg_broadcast_time_ms"] == 0:
            self.performance_metrics["avg_broadcast_time_ms"] = broadcast_time_ms
        else:
            # Simple moving average
            self.performance_metrics["avg_broadcast_time_ms"] = (
                self.performance_metrics["avg_broadcast_time_ms"] * 0.9 + 
                broadcast_time_ms * 0.1
            )
        
        # Update max
        if broadcast_time_ms > self.performance_metrics["max_broadcast_time_ms"]:
            self.performance_metrics["max_broadcast_time_ms"] = broadcast_time_ms
        
        # Track slow vs fast broadcasts
        if broadcast_time_ms > 50:  # 50ms threshold
            self.performance_metrics["slow_broadcasts"] += 1
            logger.warning(f"⚠️ Slow broadcast: {broadcast_time_ms:.1f}ms to {len(self.clients)} clients")
        else:
            self.performance_metrics["fast_broadcasts"] += 1
    
    async def _on_market_data(self, market_data: MarketData):
        """Handle market data from Sierra Chart client"""
        try:
            self.latest_data[market_data.symbol] = market_data
            self.last_data_time = datetime.now()
            self.data_sequence += 1
            self.stats["data_updates"] += 1
            
            # Broadcast to WebSocket clients
            await self._broadcast_message({
                "type": MessageType.MARKET_DATA.value,
                "data": asdict(market_data),
                "sequence": self.data_sequence,
                "timestamp": datetime.now().isoformat()
            }, "market_data")
            
            logger.debug(f"📊 Broadcasted: {market_data.symbol} @ ${market_data.close}")
            
        except Exception as e:
            logger.error(f"❌ Market data broadcast error: {e}")
            self.stats["errors"] += 1
    
    async def _on_sierra_error(self, error: Exception):
        """Handle errors from Sierra Chart client"""
        logger.error(f"❌ Sierra Chart error: {error}")
        self.stats["errors"] += 1
        
        # Broadcast error to clients
        await self._broadcast_message({
            "type": MessageType.ERROR.value,
            "data": {
                "source": "sierra_client",
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def _health_broadcast_loop(self):
        """Broadcast health status periodically"""
        while self.running:
            try:
                health_data = self._get_service_status()
                
                await self._broadcast_message({
                    "type": MessageType.SYSTEM_STATUS.value,
                    "data": health_data
                }, "system_status")
                
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Health broadcast error: {e}")
                await asyncio.sleep(30)
    
    async def _statistics_loop(self):
        """Update statistics periodically"""
        while self.running:
            try:
                self.stats["uptime_seconds"] = (datetime.now() - self.start_time).total_seconds()
                await asyncio.sleep(10)  # Every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Statistics loop error: {e}")
                await asyncio.sleep(10)
    
    def _get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        sierra_status = {}
        if self.sierra_client:
            sierra_status = self.sierra_client.get_health_status()
        
        return {
            "service": "market_data",
            "status": "online" if self.running else "offline",
            "uptime_seconds": uptime,
            "clients_connected": len(self.clients),
            "symbols_tracked": len(self.latest_data),
            "last_data_age": (datetime.now() - self.last_data_time).total_seconds() if self.last_data_time else None,
            "data_sequence": self.data_sequence,
            "sierra_client": sierra_status,
            "performance": self.performance_metrics,
            "stats": self.stats,
            "timestamp": datetime.now().isoformat()
        }
    
    # HTTP API handlers
    async def _handle_health(self, request):
        """Health check endpoint"""
        status = self._get_service_status()
        return web.json_response(status)
    
    async def _handle_api_market_data(self, request):
        """Market data API endpoint"""
        symbol = request.query.get('symbol')
        
        if symbol and symbol in self.latest_data:
            data = asdict(self.latest_data[symbol])
        elif symbol:
            return web.json_response(
                {"error": f"Symbol {symbol} not found"}, 
                status=404
            )
        else:
            # Return all symbols
            data = {symbol: asdict(market_data) for symbol, market_data in self.latest_data.items()}
        
        return web.json_response({
            "symbols" if not symbol else "data": data,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
    
    async def _handle_api_symbols(self, request):
        """Symbols list endpoint"""
        symbols = list(self.latest_data.keys())
        return web.json_response({
            "symbols": symbols,
            "count": len(symbols),
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_api_stats(self, request):
        """Statistics endpoint"""
        stats = self._get_service_status()
        return web.json_response(stats)
    
    async def _handle_api_notify(self, request):
        """External notification endpoint"""
        try:
            data = await request.json()
            msg_type = data.get('type', 'notification')
            
            # Broadcast notification to WebSocket clients
            await self._broadcast_message({
                "type": msg_type,
                "data": data.get('data', {}),
                "timestamp": datetime.now().isoformat()
            })
            
            return web.json_response({
                "success": True,
                "clients_notified": len(self.clients),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return web.json_response(
                {"success": False, "error": str(e)}, 
                status=500
            )

# Global service instance
_market_data_service = None

def get_market_data_service(ws_port: int = 9001, http_port: int = 9002) -> MarketDataService:
    """Get global market data service instance"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService(ws_port, http_port)
    return _market_data_service

async def main():
    """Test the market data service"""
    service = MarketDataService()
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Stopping service...")
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())