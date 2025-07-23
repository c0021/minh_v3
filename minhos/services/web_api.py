#!/usr/bin/env python3
"""
MinhOS v3 Web API Service
=========================
Linux-native REST API service providing HTTP endpoints for market data,
system status, and trading operations. Replaces http_server.py with
comprehensive API functionality and no Windows dependencies.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import asdict
from aiohttp import web, ClientTimeout
import aiohttp
import time

# Import other services
from .sierra_client import get_sierra_client
from .market_data import get_market_data_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_api")

class WebAPIService:
    """
    Comprehensive REST API service for MinhOS v3
    Provides HTTP endpoints for all system functionality
    """
    
    def __init__(self, port: int = 8080):
        """Initialize Web API service"""
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.running = False
        
        # Service references
        self.sierra_client = None
        self.market_data_service = None
        
        # Statistics
        self.stats = {
            "requests_total": 0,
            "requests_market_data": 0,
            "requests_health": 0,
            "requests_debug": 0,
            "requests_api": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
            "uptime_seconds": 0
        }
        
        # Request rate limiting
        self.rate_limiter = {}
        self.rate_limit_window = 60  # 1 minute
        self.rate_limit_max = 100    # requests per window
        
        # Setup routes
        self._setup_routes()
        
        logger.info("🌐 Web API Service initialized")
    
    def _setup_routes(self):
        """Setup API routes"""
        # Health and status
        self.app.router.add_get('/health', self._handle_health)
        self.app.router.add_get('/api/health', self._handle_health)
        self.app.router.add_get('/api/status', self._handle_status)
        
        # Market data endpoints
        self.app.router.add_get('/api/market_data', self._handle_market_data)
        self.app.router.add_get('/api/market/latest', self._handle_market_latest)
        self.app.router.add_get('/api/latest-data', self._handle_market_latest)  # Compatibility
        self.app.router.add_get('/api/symbols', self._handle_symbols)
        self.app.router.add_get('/market_data', self._handle_legacy_market_data)  # Legacy support
        
        # System endpoints
        self.app.router.add_get('/api/services', self._handle_services_status)
        self.app.router.add_get('/api/stats', self._handle_statistics)
        self.app.router.add_get('/api/performance', self._handle_performance)
        
        # Debug endpoints
        self.app.router.add_get('/api/debug/data-age', self._handle_debug_data_age)
        self.app.router.add_get('/api/debug/last-update', self._handle_debug_last_update)
        self.app.router.add_get('/api/debug/file-stats', self._handle_debug_file_stats)
        self.app.router.add_get('/api/debug/connections', self._handle_debug_connections)
        
        # Trading endpoints (placeholder for future implementation)
        self.app.router.add_get('/api/trading_status', self._handle_trading_status)
        self.app.router.add_get('/api/ai_status', self._handle_ai_status)
        
        # Configuration endpoints
        self.app.router.add_get('/api/config', self._handle_config_get)
        self.app.router.add_post('/api/config', self._handle_config_post)
        
        # CORS middleware
        self.app.middlewares.append(self._cors_middleware)
        self.app.middlewares.append(self._rate_limit_middleware)
        self.app.middlewares.append(self._logging_middleware)
    
    async def _cors_middleware(self, request, handler):
        """CORS middleware"""
        try:
            response = await handler(request)
        except Exception as ex:
            # Handle errors and still add CORS headers
            response = web.json_response(
                {'error': str(ex)}, 
                status=500
            )
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    async def _rate_limit_middleware(self, request, handler):
        """Rate limiting middleware"""
        client_ip = request.remote
        current_time = time.time()
        
        # Clean old entries
        cutoff_time = current_time - self.rate_limit_window
        self.rate_limiter = {
            ip: requests for ip, requests in self.rate_limiter.items()
            if any(req_time > cutoff_time for req_time in requests)
        }
        
        # Update current IP
        if client_ip not in self.rate_limiter:
            self.rate_limiter[client_ip] = []
        
        # Clean old requests for this IP
        self.rate_limiter[client_ip] = [
            req_time for req_time in self.rate_limiter[client_ip]
            if req_time > cutoff_time
        ]
        
        # Check rate limit
        if len(self.rate_limiter[client_ip]) >= self.rate_limit_max:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return web.json_response(
                {'error': 'Rate limit exceeded'}, 
                status=429
            )
        
        # Add current request
        self.rate_limiter[client_ip].append(current_time)
        
        return await handler(request)
    
    async def _logging_middleware(self, request, handler):
        """Request logging middleware"""
        start_time = time.time()
        self.stats["requests_total"] += 1
        
        try:
            response = await handler(request)
            
            # Update endpoint-specific stats
            path = request.path
            if 'market' in path:
                self.stats["requests_market_data"] += 1
            elif 'health' in path:
                self.stats["requests_health"] += 1
            elif 'debug' in path:
                self.stats["requests_debug"] += 1
            elif path.startswith('/api/'):
                self.stats["requests_api"] += 1
            
            # Log slow requests
            duration = time.time() - start_time
            if duration > 1.0:
                logger.warning(f"Slow request: {request.method} {path} took {duration:.2f}s")
            
            return response
            
        except Exception as e:
            self.stats["errors"] += 1
            duration = time.time() - start_time
            logger.error(f"Request error: {request.method} {path} - {e} (took {duration:.2f}s)")
            raise
    
    async def start(self):
        """Start the Web API service"""
        logger.info(f"🚀 Starting Web API Service on port {self.port}...")
        self.running = True
        
        try:
            # Initialize service references
            self.sierra_client = get_sierra_client()
            
            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            
            logger.info(f"✅ Web API Service started on http://localhost:{self.port}")
            logger.info("📋 Available endpoints:")
            logger.info("   GET  /health - Service health check")
            logger.info("   GET  /api/market_data - Current market data")
            logger.info("   GET  /api/symbols - Available symbols")
            logger.info("   GET  /api/status - System status")
            logger.info("   GET  /api/debug/* - Debug endpoints")
            
            # Start background tasks
            asyncio.create_task(self._statistics_loop())
            
        except Exception as e:
            logger.error(f"❌ Failed to start Web API Service: {e}")
            self.running = False
            raise
    
    async def stop(self):
        """Stop the Web API service"""
        logger.info("🛑 Stopping Web API Service...")
        self.running = False
        
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        
        logger.info("Web API Service stopped")
    
    async def _statistics_loop(self):
        """Update statistics periodically"""
        start_time = datetime.fromisoformat(self.stats["start_time"])
        
        while self.running:
            try:
                self.stats["uptime_seconds"] = (datetime.now() - start_time).total_seconds()
                await asyncio.sleep(10)  # Every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Statistics loop error: {e}")
                await asyncio.sleep(10)
    
    # Health and Status handlers
    async def _handle_health(self, request):
        """Health check endpoint"""
        uptime = (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        
        sierra_connected = False
        if self.sierra_client:
            sierra_connected = self.sierra_client.is_connected()
        
        health_data = {
            "status": "healthy" if self.running else "unhealthy",
            "service": "web_api",
            "uptime_seconds": uptime,
            "sierra_client_connected": sierra_connected,
            "requests_total": self.stats["requests_total"],
            "errors": self.stats["errors"],
            "timestamp": datetime.now().isoformat()
        }
        
        status_code = 200 if self.running else 503
        return web.json_response(health_data, status=status_code)
    
    async def _handle_status(self, request):
        """System status endpoint"""
        status_data = {
            "status": "ONLINE" if self.running else "OFFLINE",
            "service": "MinhOS v3",
            "version": "3.0.0",
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds(),
            "api_version": "1.0",
            "features": ["market_data", "websocket", "real_time", "linux_native"],
            "timestamp": datetime.now().isoformat()
        }
        
        return web.json_response(status_data)
    
    # Market Data handlers
    async def _handle_market_data(self, request):
        """Main market data endpoint"""
        symbol = request.query.get('symbol')
        
        try:
            if self.sierra_client:
                if symbol:
                    data = self.sierra_client.get_latest_data(symbol)
                    if data:
                        # Check data freshness
                        data_age = self._calculate_data_age(data.timestamp)
                        
                        response = {
                            "status": "CONNECTED" if data_age < 30 else "STALE",
                            "connected": data_age < 30,
                            "symbol": data.symbol,
                            "price": data.close,
                            "bid": data.bid,
                            "ask": data.ask,
                            "volume": data.volume,
                            "timestamp": data.timestamp,
                            "source": data.source,
                            "age_seconds": data_age
                        }
                    else:
                        response = {
                            "status": "NO DATA",
                            "connected": False,
                            "message": f"No data available for symbol {symbol}",
                            "symbol": symbol,
                            "price": None,
                            "timestamp": None
                        }
                else:
                    # Return all symbols
                    all_data = self.sierra_client.get_all_symbols()
                    symbols_response = {}
                    
                    for sym, data in all_data.items():
                        data_age = self._calculate_data_age(data.timestamp)
                        symbols_response[sym] = {
                            "price": data.close,
                            "bid": data.bid,
                            "ask": data.ask,
                            "volume": data.volume,
                            "timestamp": data.timestamp,
                            "age_seconds": data_age,
                            "connected": data_age < 30
                        }
                    
                    response = {
                        "status": "SUCCESS",
                        "symbols": symbols_response,
                        "count": len(symbols_response),
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                response = {
                    "status": "NO DATA",
                    "connected": False,
                    "message": "Sierra client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"❌ Market data endpoint error: {e}")
            return web.json_response({
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
    
    async def _handle_market_latest(self, request):
        """Latest market data in multi-symbol format"""
        try:
            symbols_data = {}
            
            if self.sierra_client:
                all_data = self.sierra_client.get_all_symbols()
                
                for symbol, data in all_data.items():
                    data_age = self._calculate_data_age(data.timestamp)
                    
                    symbols_data[symbol] = {
                        'last': data.close,
                        'bid': data.bid or (data.close - 0.25) if data.close else 0,
                        'ask': data.ask or (data.close + 0.25) if data.close else 0,
                        'volume': int(data.volume or 0),
                        'timestamp': data.timestamp,
                        'age_seconds': data_age
                    }
            
            response = {
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols_data,
                'status': 'success' if symbols_data else 'no_data'
            }
            
            # Add warning for stale data
            if symbols_data:
                max_age = max(s.get('age_seconds', 0) for s in symbols_data.values())
                if max_age > 60:
                    response['status'] = 'warning'
                    response['message'] = f'Data is {int(max_age)} seconds old'
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"❌ Market latest endpoint error: {e}")
            return web.json_response({
                'timestamp': datetime.now().isoformat(),
                'symbols': {},
                'status': 'error',
                'message': f'Error retrieving market data: {str(e)}'
            }, status=500)
    
    async def _handle_symbols(self, request):
        """Available symbols endpoint"""
        try:
            symbols = []
            if self.sierra_client:
                all_data = self.sierra_client.get_all_symbols()
                symbols = list(all_data.keys())
            
            return web.json_response({
                "symbols": symbols,
                "count": len(symbols),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return web.json_response({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)
    
    async def _handle_legacy_market_data(self, request):
        """Legacy market data endpoint for backward compatibility"""
        # Handle both GET and POST for legacy support
        return await self._handle_market_data(request)
    
    # Service Status handlers
    async def _handle_services_status(self, request):
        """Services status endpoint"""
        services_status = {
            "sierra_client": {
                "connected": False,
                "status": "offline"
            },
            "market_data": {
                "connected": False,
                "status": "offline"
            },
            "web_api": {
                "connected": True,
                "status": "online",
                "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
            }
        }
        
        # Check Sierra Client
        if self.sierra_client:
            sierra_health = self.sierra_client.get_health_status()
            services_status["sierra_client"] = {
                "connected": sierra_health.get("connected", False),
                "status": "online" if sierra_health.get("connected") else "offline",
                "data_age_seconds": sierra_health.get("data_age_seconds"),
                "symbols_tracked": sierra_health.get("symbols_tracked", 0)
            }
        
        # Check Market Data Service (if available)
        try:
            market_service = get_market_data_service()
            if hasattr(market_service, 'running') and market_service.running:
                services_status["market_data"] = {
                    "connected": True,
                    "status": "online",
                    "clients_connected": len(getattr(market_service, 'clients', [])),
                    "data_updates": getattr(market_service, 'data_sequence', 0)
                }
        except:
            # Market data service might not be running
            pass
        
        return web.json_response({
            "services": services_status,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_statistics(self, request):
        """Statistics endpoint"""
        return web.json_response({
            "api_stats": self.stats,
            "rate_limiter": {
                "active_ips": len(self.rate_limiter),
                "rate_limit_window": self.rate_limit_window,
                "rate_limit_max": self.rate_limit_max
            },
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_performance(self, request):
        """Performance metrics endpoint"""
        uptime = (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        
        performance = {
            "requests_per_second": self.stats["requests_total"] / uptime if uptime > 0 else 0,
            "error_rate": (self.stats["errors"] / self.stats["requests_total"]) * 100 if self.stats["requests_total"] > 0 else 0,
            "uptime_seconds": uptime,
            "memory_usage": "N/A",  # Could add psutil for actual memory usage
            "timestamp": datetime.now().isoformat()
        }
        
        return web.json_response(performance)
    
    # Debug handlers
    async def _handle_debug_data_age(self, request):
        """Debug data age endpoint"""
        debug_info = {
            "sierra_client_status": "not_available",
            "data_files_checked": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if self.sierra_client:
            health = self.sierra_client.get_health_status()
            debug_info["sierra_client_status"] = "connected" if health.get("connected") else "disconnected"
            debug_info["data_age_seconds"] = health.get("data_age_seconds")
            debug_info["last_update"] = health.get("last_update")
        
        # Check data files
        data_paths = [
            Path("/tmp/minhos/latest_market_data.json"),
            Path("/tmp/sierra_data/market_data.json"),
            Path("/var/tmp/minhos_market_data.json")
        ]
        
        for path in data_paths:
            file_info = {"path": str(path), "exists": False}
            
            if path.exists():
                stat = path.stat()
                file_info.update({
                    "exists": True,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "age_seconds": int(time.time() - stat.st_mtime),
                    "size_bytes": stat.st_size
                })
            
            debug_info["data_files_checked"].append(file_info)
        
        return web.json_response(debug_info)
    
    async def _handle_debug_last_update(self, request):
        """Debug last update endpoint"""
        debug_info = {
            "sierra_client": {},
            "data_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if self.sierra_client:
            latest = self.sierra_client.get_latest_data()
            if latest:
                debug_info["sierra_client"] = {
                    "symbol": latest.symbol,
                    "price": latest.close,
                    "timestamp": latest.timestamp,
                    "source": latest.source,
                    "age_seconds": self._calculate_data_age(latest.timestamp)
                }
        
        return web.json_response(debug_info)
    
    async def _handle_debug_file_stats(self, request):
        """Debug file statistics endpoint"""
        file_stats = {}
        
        # Check various data file locations
        data_files = [
            "/tmp/minhos/latest_market_data.json",
            "/tmp/minhos/multi_symbol_data.json",
            "/tmp/minhos/market_data_history.json",
            "/tmp/sierra_data/market_data.json",
            "/var/tmp/minhos_market_data.json"
        ]
        
        for file_path in data_files:
            path = Path(file_path)
            filename = path.name
            
            if path.exists():
                stat = path.stat()
                file_stats[filename] = {
                    "exists": True,
                    "path": str(path),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "age_seconds": int(time.time() - stat.st_mtime)
                }
            else:
                file_stats[filename] = {"exists": False, "path": str(path)}
        
        return web.json_response({
            "files": file_stats,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_debug_connections(self, request):
        """Debug connections endpoint"""
        connections = {
            "sierra_client": {
                "initialized": self.sierra_client is not None,
                "connected": False,
                "bridge_url": "unknown"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if self.sierra_client:
            health = self.sierra_client.get_health_status()
            connections["sierra_client"].update({
                "connected": health.get("connected", False),
                "bridge_url": health.get("bridge_url", "unknown"),
                "connection_attempts": health.get("connection_attempts", 0),
                "symbols_tracked": health.get("symbols_tracked", 0)
            })
        
        return web.json_response(connections)
    
    # Trading and AI handlers (placeholders)
    async def _handle_trading_status(self, request):
        """Trading status endpoint"""
        # This would integrate with actual trading system
        return web.json_response({
            "status": "NO DATA",
            "trading_enabled": False,
            "message": "Trading system not yet implemented",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_ai_status(self, request):
        """AI status endpoint"""
        # This would integrate with actual AI system
        return web.json_response({
            "connected": False,
            "signal": None,
            "confidence": None,
            "analysis": "AI system not yet implemented",
            "timestamp": datetime.now().isoformat()
        })
    
    # Configuration handlers
    async def _handle_config_get(self, request):
        """Get configuration endpoint"""
        config = {
            "api": {
                "port": self.port,
                "rate_limit_max": self.rate_limit_max,
                "rate_limit_window": self.rate_limit_window
            },
            "sierra_client": {
                "bridge_url": self.sierra_client.bridge_url if self.sierra_client else None
            },
            "features": {
                "market_data": True,
                "websocket": False,  # Provided by market_data service
                "trading": False,
                "ai_analysis": False
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return web.json_response(config)
    
    async def _handle_config_post(self, request):
        """Update configuration endpoint"""
        try:
            data = await request.json()
            
            # This would update actual configuration
            # For now, just acknowledge the request
            
            return web.json_response({
                "success": True,
                "message": "Configuration update acknowledged",
                "received_config": data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=400)
    
    def _calculate_data_age(self, timestamp_str: str) -> float:
        """Calculate age of data in seconds"""
        try:
            if not timestamp_str:
                return float('inf')
            
            # Handle various timestamp formats
            if 'T' in timestamp_str:
                data_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if data_time.tzinfo:
                    data_time = data_time.replace(tzinfo=None)
            else:
                data_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            return (datetime.now() - data_time).total_seconds()
            
        except Exception as e:
            logger.debug(f"Error calculating data age: {e}")
            return float('inf')

# Global service instance
_web_api_service = None

def get_web_api_service(port: int = 8080) -> WebAPIService:
    """Get global Web API service instance"""
    global _web_api_service
    if _web_api_service is None:
        _web_api_service = WebAPIService(port)
    return _web_api_service

async def main():
    """Test the Web API service"""
    service = WebAPIService()
    
    try:
        await service.start()
        logger.info("Service running. Press Ctrl+C to stop...")
        
        # Keep running
        while service.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping service...")
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())