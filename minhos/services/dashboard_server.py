#!/usr/bin/env python3
"""
MinhOS v4 Dashboard Server (Consolidated)
=========================================
Unified dashboard server for serving web interface and managing frontend functionality.
Separates UI concerns from API logic, focusing on template rendering and static file serving.

Consolidates:
- dashboard/main.py (Web interface and template serving)
- WebSocket connection management for dashboard updates
- Static file serving and frontend resource management

Key Features:
- HTML template rendering with Jinja2
- Static asset serving (CSS, JS, images)
- Real-time WebSocket connections for dashboard updates
- Frontend routing and navigation
- Dashboard switching between views
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Core MinhOS imports
from minhos.core.base_service import BaseService
from minhos.core.config import config

# Service imports for data integration
from .api_server import get_api_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard_server")

class ConnectionManager:
    """
    Manages WebSocket connections for real-time dashboard updates
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Optional[Dict[str, Any]] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = client_info or {}
        logger.info(f"Dashboard client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_info.pop(websocket, None)
            logger.info(f"Dashboard client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connected dashboard clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_status_update(self, status_data: Dict[str, Any]):
        """Broadcast system status update to all clients"""
        await self.broadcast({
            "type": "status_update",
            "data": status_data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_market_update(self, market_data: Dict[str, Any]):
        """Broadcast market data update to all clients"""
        await self.broadcast({
            "type": "market_update",
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

class DashboardServer(BaseService):
    """
    Consolidated Dashboard Server for MinhOS v4
    
    Provides web interface for the trading system with real-time updates,
    template rendering, and static file serving. Separates UI concerns
    from API logic for cleaner architecture.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        super().__init__("DashboardServer")
        self.host = host
        self.port = port
        
        # Create FastAPI app
        self.app = FastAPI(
            title="MinhOS v4 Dashboard Server",
            description="Trading System Web Interface",
            version="4.0.0",
            docs_url="/dashboard-docs",  # Separate from API docs
            redoc_url="/dashboard-redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # WebSocket connection manager
        self.connection_manager = ConnectionManager()
        
        # Reference to API server for data
        self.api_server = None
        
        # Dashboard state
        self.start_time = datetime.now()
        self.page_views = {}
        
        # Setup directories and routes
        self._setup_directories()
        self._setup_routes()
    
    def _setup_directories(self):
        """Setup static files and templates directories"""
        # Get dashboard directory path
        dashboard_dir = Path(__file__).parent.parent / "dashboard"
        
        self.static_dir = dashboard_dir / "static"
        self.templates_dir = dashboard_dir / "templates"
        
        # Create directories if they don't exist
        self.static_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Mount static files
        if self.static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
        
        # Setup Jinja2 templates
        if self.templates_dir.exists():
            self.templates = Jinja2Templates(directory=str(self.templates_dir))
        else:
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            self.templates = None
    
    def _setup_routes(self):
        """Setup all dashboard routes"""
        self._setup_page_routes()
        self._setup_websocket_routes()
        self._setup_utility_routes()
    
    def _setup_page_routes(self):
        """Setup HTML page routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Main dashboard page"""
            self._track_page_view("home")
            
            if not self.templates:
                return HTMLResponse("<h1>Dashboard templates not available</h1>", status_code=503)
            
            return self.templates.TemplateResponse("index.html", {
                "request": request,
                "title": "MinhOS v4 Dashboard",
                "version": "4.0.0",
                "api_base_url": f"http://{self.host}:8000",  # API server URL
                "websocket_url": f"ws://{self.host}:{self.port}/ws"
            })
        
        @self.app.get("/enhanced", response_class=HTMLResponse)
        async def enhanced_dashboard(request: Request):
            """Enhanced dashboard with autonomous trading, pattern learning, and advanced features"""
            self._track_page_view("enhanced")
            
            if not self.templates:
                return HTMLResponse("<h1>Dashboard templates not available</h1>", status_code=503)
            
            return self.templates.TemplateResponse("dashboard_enhanced.html", {
                "request": request,
                "title": "MinhOS v4 Enhanced Dashboard",
                "version": "4.0.0",
                "api_base_url": f"http://{self.host}:8000",
                "websocket_url": f"ws://{self.host}:{self.port}/ws"
            })
        
        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def dashboard_redirect(request: Request):
            """Redirect to enhanced dashboard"""
            self._track_page_view("dashboard")
            
            if not self.templates:
                return HTMLResponse("<h1>Dashboard templates not available</h1>", status_code=503)
            
            return self.templates.TemplateResponse("dashboard_enhanced.html", {
                "request": request,
                "title": "MinhOS v4 Enhanced Dashboard",
                "version": "4.0.0",
                "api_base_url": f"http://{self.host}:8000",
                "websocket_url": f"ws://{self.host}:{self.port}/ws"
            })
        
        @self.app.get("/trading", response_class=HTMLResponse)
        async def trading_dashboard(request: Request):
            """Trading-focused dashboard view"""
            self._track_page_view("trading")
            
            if not self.templates:
                return HTMLResponse("<h1>Dashboard templates not available</h1>", status_code=503)
            
            # Try to serve trading-specific template, fallback to enhanced
            template_name = "trading_dashboard.html" if (self.templates_dir / "trading_dashboard.html").exists() else "dashboard_enhanced.html"
            
            return self.templates.TemplateResponse(template_name, {
                "request": request,
                "title": "MinhOS v4 Trading Dashboard",
                "version": "4.0.0",
                "api_base_url": f"http://{self.host}:8000",
                "websocket_url": f"ws://{self.host}:{self.port}/ws"
            })
        
        @self.app.get("/chat", response_class=HTMLResponse)
        async def chat_interface(request: Request):
            """Chat interface dashboard view"""
            self._track_page_view("chat")
            
            if not self.templates:
                return HTMLResponse("<h1>Dashboard templates not available</h1>", status_code=503)
            
            # Try to serve chat-specific template, fallback to enhanced
            template_name = "chat_dashboard.html" if (self.templates_dir / "chat_dashboard.html").exists() else "dashboard_enhanced.html"
            
            return self.templates.TemplateResponse(template_name, {
                "request": request,
                "title": "MinhOS v4 Chat Interface",
                "version": "4.0.0",
                "api_base_url": f"http://{self.host}:8000",
                "websocket_url": f"ws://{self.host}:{self.port}/ws"
            })
    
    def _setup_websocket_routes(self):
        """Setup WebSocket routes for real-time updates"""
        
        @self.app.websocket("/ws/dashboard")
        async def dashboard_websocket(websocket: WebSocket):
            """Main dashboard WebSocket endpoint"""
            await self.connection_manager.connect(websocket, {"type": "dashboard"})
            
            try:
                # Send initial status
                await self._send_initial_data(websocket)
                
                # Keep connection alive and handle messages
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Handle different message types
                    await self._handle_websocket_message(websocket, message)
                    
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"Dashboard WebSocket error: {e}")
                self.connection_manager.disconnect(websocket)
        
        @self.app.websocket("/ws/status")
        async def status_websocket(websocket: WebSocket):
            """System status WebSocket endpoint"""
            await self.connection_manager.connect(websocket, {"type": "status"})
            
            try:
                while True:
                    # Send status updates every 5 seconds
                    status_data = await self._get_system_status()
                    await self.connection_manager.send_personal_message(
                        {"type": "status", "data": status_data},
                        websocket
                    )
                    await asyncio.sleep(5)
                    
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"Status WebSocket error: {e}")
                self.connection_manager.disconnect(websocket)
        
        @self.app.websocket("/ws/market")
        async def market_websocket(websocket: WebSocket):
            """Market data WebSocket endpoint"""
            await self.connection_manager.connect(websocket, {"type": "market"})
            
            try:
                while True:
                    # Send market data updates every second
                    market_data = await self._get_market_data()
                    if market_data:
                        await self.connection_manager.send_personal_message(
                            {"type": "market", "data": market_data},
                            websocket
                        )
                    await asyncio.sleep(1)
                    
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"Market WebSocket error: {e}")
                self.connection_manager.disconnect(websocket)
    
    def _setup_utility_routes(self):
        """Setup utility and health check routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Dashboard server health check"""
            return {
                "status": "healthy",
                "service": "dashboard_server",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "active_connections": self.connection_manager.get_connection_count(),
                "page_views": self.page_views
            }
        
        @self.app.get("/dashboard/info")
        async def dashboard_info():
            """Dashboard server information"""
            return {
                "name": self.name,
                "version": "4.0.0",
                "host": self.host,
                "port": self.port,
                "start_time": self.start_time.isoformat(),
                "templates_available": self.templates is not None,
                "static_dir": str(self.static_dir),
                "templates_dir": str(self.templates_dir),
                "active_connections": self.connection_manager.get_connection_count()
            }
        
        @self.app.get("/dashboard/connections")
        async def connection_info():
            """WebSocket connection information"""
            connections_info = []
            for ws, info in self.connection_manager.connection_info.items():
                connections_info.append({
                    "connection_id": id(ws),
                    "type": info.get("type", "unknown"),
                    "connected_at": info.get("connected_at", "unknown")
                })
            
            return {
                "total_connections": self.connection_manager.get_connection_count(),
                "connections": connections_info
            }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _track_page_view(self, page: str):
        """Track page view statistics"""
        if page not in self.page_views:
            self.page_views[page] = 0
        self.page_views[page] += 1
    
    async def _send_initial_data(self, websocket: WebSocket):
        """Send initial data to newly connected client"""
        try:
            # Send system status
            status_data = await self._get_system_status()
            await self.connection_manager.send_personal_message(
                {"type": "initial_status", "data": status_data},
                websocket
            )
            
            # Send market data
            market_data = await self._get_market_data()
            if market_data:
                await self.connection_manager.send_personal_message(
                    {"type": "initial_market", "data": market_data},
                    websocket
                )
            
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def _handle_websocket_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                await self.connection_manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    websocket
                )
            elif message_type == "request_status":
                status_data = await self._get_system_status()
                await self.connection_manager.send_personal_message(
                    {"type": "status_response", "data": status_data},
                    websocket
                )
            elif message_type == "request_market":
                market_data = await self._get_market_data()
                await self.connection_manager.send_personal_message(
                    {"type": "market_response", "data": market_data},
                    websocket
                )
            else:
                logger.warning(f"Unknown WebSocket message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get system status from API server"""
        try:
            if self.api_server:
                return await self.api_server._get_system_status()
            else:
                return {
                    "status": "api_unavailable",
                    "timestamp": datetime.now().isoformat(),
                    "services": {},
                    "message": "API server not connected"
                }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _get_market_data(self) -> Optional[Dict[str, Any]]:
        """Get market data from API server"""
        try:
            if self.api_server:
                return await self.api_server._get_live_market_data()
            return None
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
    
    # ========================================================================
    # Broadcasting Methods
    # ========================================================================
    
    async def broadcast_system_update(self, update_data: Dict[str, Any]):
        """Broadcast system update to all connected clients"""
        await self.connection_manager.broadcast_status_update(update_data)
    
    async def broadcast_market_update(self, market_data: Dict[str, Any]):
        """Broadcast market data update to all connected clients"""
        await self.connection_manager.broadcast_market_update(market_data)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alert to all connected clients"""
        await self.connection_manager.broadcast({
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        })
    
    # ========================================================================
    # Service Lifecycle
    # ========================================================================
    
    # Abstract method implementations for BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        # Get API server reference for data
        try:
            self.api_server = get_api_server()
        except:
            logger.warning("API server not available - dashboard will have limited functionality")
    
    async def _start_service(self):
        """Start service-specific functionality"""
        # Start the server
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        # Store server for shutdown
        self._server = server
        
        # Start server in background task
        self._server_task = asyncio.create_task(server.serve())
        
        logger.info(f"Dashboard Server started successfully on {self.host}:{self.port}")
        logger.info(f"Dashboard available at http://{self.host}:{self.port}/")
        logger.info(f"Enhanced Dashboard at http://{self.host}:{self.port}/enhanced")
    
    async def _stop_service(self):
        """Stop service-specific functionality"""
        # Disconnect all WebSocket clients
        for connection in list(self.connection_manager.active_connections):
            try:
                await connection.close()
            except:
                pass
        
        # Stop server
        if hasattr(self, '_server'):
            self._server.should_exit = True
        
        if hasattr(self, '_server_task'):
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup(self):
        """Cleanup service resources"""
        # Clear connection manager
        self.connection_manager.active_connections.clear()
        self.connection_manager.connection_info.clear()

    async def start(self):
        """Start the dashboard server"""
        logger.info(f"Starting Dashboard Server on {self.host}:{self.port}")
        
        try:
            # Use BaseService start method
            await super().start()
            
        except Exception as e:
            logger.error(f"Failed to start Dashboard Server: {e}")
            raise
    
    async def stop(self):
        """Stop the dashboard server"""
        logger.info("Stopping Dashboard Server...")
        
        try:
            # Use BaseService stop method
            await super().stop()
            logger.info("Dashboard Server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Dashboard Server: {e}")

# ============================================================================
# Service Registry
# ============================================================================

_dashboard_server_instance = None

def get_dashboard_server() -> DashboardServer:
    """Get the global dashboard server instance"""
    global _dashboard_server_instance
    if _dashboard_server_instance is None:
        _dashboard_server_instance = DashboardServer()
    return _dashboard_server_instance

async def create_dashboard_server(host: str = "0.0.0.0", port: int = 8888) -> DashboardServer:
    """Create and start a new dashboard server instance"""
    server = DashboardServer(host=host, port=port)
    await server.start()
    return server

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main function for standalone execution"""
    dashboard_server = DashboardServer()
    
    try:
        await dashboard_server.start()
        logger.info("Dashboard Server running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Dashboard Server error: {e}")
    finally:
        await dashboard_server.stop()

if __name__ == "__main__":
    asyncio.run(main())