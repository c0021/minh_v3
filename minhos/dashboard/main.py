#!/usr/bin/env python3
"""
MinhOS v3 Web Dashboard
=======================
FastAPI-based web interface for monitoring and controlling the trading system.

Features:
- Real-time status monitoring via WebSocket
- Trading controls and configuration
- Performance metrics and charts
- System health monitoring
- Historical data visualization
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from minhos.dashboard.api import router as api_router
from minhos.dashboard.api_enhanced import router as enhanced_api_router
from minhos.dashboard.websocket_chat import websocket_router as chat_router
from minhos.dashboard.api_trading import router as trading_router
from minhos.dashboard.api_ml_performance import router as ml_performance_router
from minhos.dashboard.api_ml_pipeline import router as ml_pipeline_router
from minhos.dashboard.api_kelly import router as kelly_router
from minhos.dashboard.api_risk_validation_fastapi import router as risk_validation_router
from minhos.services import (
    get_market_data_service, get_state_manager, 
    get_ai_brain_service, get_trading_engine
)
# Removed resilient market data imports - NO FAKE DATA PHILOSOPHY

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MinhOS v3 Dashboard",
    description="Trading System Control Center",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Include API routes
app.include_router(api_router, prefix="/api")
app.include_router(enhanced_api_router, prefix="/api")  # Enhanced API routes  
app.include_router(trading_router)  # Trading API routes
app.include_router(ml_performance_router)  # ML Performance API routes
app.include_router(ml_pipeline_router)  # ML Pipeline API routes
app.include_router(kelly_router)  # Kelly Criterion API routes
app.include_router(risk_validation_router)  # Risk Validation API routes - Phase 3

# Include WebSocket chat routes
app.include_router(chat_router)

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

# Create connection manager
manager = ConnectionManager()

# Dashboard state
class DashboardState:
    """Maintains dashboard state and data"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.update_interval = 1.0  # seconds
        self.running = False
        self._update_task = None
    
    async def start(self):
        """Start dashboard background tasks"""
        self.running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Dashboard state manager started")
    
    async def stop(self):
        """Stop dashboard background tasks"""
        self.running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Dashboard state manager stopped")
    
    async def _update_loop(self):
        """Send periodic updates to all connected clients"""
        while self.running:
            try:
                # Gather system state
                update = self._gather_system_state()
                
                # Broadcast to all clients
                await manager.broadcast(update)
                
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5)  # Back off on error
    
    def _gather_system_state(self) -> Dict[str, Any]:
        """Gather current system state from all services"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'uptime': str(datetime.now() - self.start_time),
            'connections': len(manager.active_connections)
        }
        
        try:
            # Get state from services
            state_manager = get_state_manager()
            market_data = get_market_data_service()
            ai_brain = get_ai_brain_service()
            trading_engine = get_trading_engine()
            
            # System state
            system_state = state_manager.get_current_state()
            state['system'] = {
                'mode': system_state.get('system_state', 'UNKNOWN'),
                'health': system_state.get('system_state', 'UNKNOWN'),
                'active': system_state.get('system_state', 'UNKNOWN') != 'OFFLINE'
            }
            
            # Market data - get from running Sierra Client
            sierra_client = None
            try:
                from minhos.services.live_trading_integration import get_running_service
                sierra_client = get_running_service('sierra_client')
            except ImportError:
                pass
            
            if sierra_client and hasattr(sierra_client, 'last_market_data'):
                # Get the most recent market data from Sierra Client (centralized symbol management)
                from minhos.core.symbol_integration import get_ai_brain_primary_symbol
                primary_symbol = get_ai_brain_primary_symbol()
                
                market_data_dict = sierra_client.last_market_data
                if market_data_dict and primary_symbol in market_data_dict:
                    primary_data = market_data_dict[primary_symbol]
                    state['market'] = {
                        'connected': True,
                        'symbol': primary_data.symbol,
                        'price': primary_data.close,
                        'bid': primary_data.bid,
                        'ask': primary_data.ask,
                        'volume': primary_data.volume,
                        'last_update': primary_data.timestamp.isoformat() if hasattr(primary_data.timestamp, 'isoformat') else str(primary_data.timestamp),
                        'data_points': len(market_data_dict)
                    }
                else:
                    state['market'] = {
                        'connected': True,
                        'symbol': primary_symbol,
                        'price': 0,
                        'bid': 0,
                        'ask': 0,
                        'volume': 0,
                        'last_update': 'No data',
                        'data_points': 0
                    }
            else:
                state['market'] = {
                    'connected': False,
                    'last_update': None,
                    'data_points': 0
                }
            
            # AI Brain status
            if hasattr(ai_brain, 'get_status'):
                ai_status = ai_brain.get_status()
                state['ai'] = {
                    'active': ai_status.get('active', False),
                    'model': ai_status.get('model', 'Unknown'),
                    'signals': ai_status.get('signals_generated', 0)
                }
            else:
                state['ai'] = {
                    'active': True if ai_brain else False,
                    'model': 'Claude-3',
                    'signals': 0
                }
            
            # Trading engine
            if hasattr(trading_engine, 'get_status'):
                trading_status = trading_engine.get_status()
                state['trading'] = {
                    'active': trading_status.get('active', False),
                    'positions': len(trading_status.get('positions', [])),
                    'pnl': trading_status.get('total_pnl', 0)
                }
            else:
                state['trading'] = {
                    'active': True if trading_engine else False,
                    'positions': 0,
                    'pnl': 0.0
                }
            
        except Exception as e:
            logger.error(f"Error gathering system state: {e}")
            state['error'] = str(e)
        
        return state

# Create dashboard state
dashboard_state = DashboardState()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "MinhOS v4 Trading Dashboard",
        "version": "4.0.0"
    })

@app.get("/enhanced", response_class=RedirectResponse)
async def enhanced_redirect():
    """Redirect enhanced dashboard to main consolidated dashboard"""
    return RedirectResponse(url="/", status_code=301)

@app.get("/dashboard", response_class=RedirectResponse)
async def dashboard_redirect():
    """Redirect to main consolidated dashboard"""
    return RedirectResponse(url="/", status_code=301)

@app.get("/risk-validation", response_class=HTMLResponse)
async def risk_validation_dashboard(request: Request):
    """Risk Validation Dashboard page - Phase 3"""
    return templates.TemplateResponse("risk_validation.html", {
        "request": request,
        "title": "Risk Validation Dashboard - Phase 3 - MinhOS v3",
        "current_time": datetime.now().isoformat()
    })

@app.get("/ml-performance", response_class=HTMLResponse)
async def ml_performance_dashboard(request: Request):
    """ML Performance Dashboard page"""
    return templates.TemplateResponse("ml_performance.html", {
        "request": request,
        "title": "ML Performance Dashboard - MinhOS v3",
        "version": "3.0.0"
    })

@app.get("/ml-pipeline", response_class=RedirectResponse)
async def ml_pipeline_redirect():
    """Redirect ML pipeline dashboard to ML performance dashboard"""
    return RedirectResponse(url="/ml-performance", status_code=301)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - dashboard_state.start_time),
        "connections": len(manager.active_connections)
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        initial_state = dashboard_state._gather_system_state()
        await websocket.send_json({
            "type": "initial",
            "data": initial_state
        })
        
        # Keep connection alive
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Handle client commands
            if data == "ping":
                await websocket.send_text("pong")
            else:
                # Echo back for now
                await websocket.send_json({
                    "type": "echo",
                    "data": data
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize dashboard on startup"""
    logger.info("Starting MinhOS Dashboard...")
    await dashboard_state.start()
    
    # NO FAKE DATA - System fails honestly when no real Sierra Chart data available
    logger.info("✅ Dashboard initialized - REAL DATA ONLY, fails honestly when disconnected")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down MinhOS Dashboard...")
    await dashboard_state.stop()


class DashboardServer:
    """Dashboard server wrapper for integration with MinhOS"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        self.host = host
        self.port = port
        self.server = None
    
    async def start(self):
        """Start the dashboard server"""
        # Check if port is available before starting
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((self.host, self.port))
            sock.close()
        except OSError as e:
            logger.error(f"Port {self.port} is already in use. Please stop any existing MinhOS processes first.")
            raise e
        
        config = uvicorn.Config(
            app=app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        self.server = uvicorn.Server(config)
        
        logger.info(f"Starting dashboard server on {self.host}:{self.port}")
        await self.server.serve()
    
    async def stop(self):
        """Stop the dashboard server"""
        if self.server:
            try:
                if hasattr(self.server, 'should_exit'):
                    self.server.should_exit = True
                if hasattr(self.server, 'shutdown'):
                    await self.server.shutdown()
            except Exception as e:
                logger.error(f"Error during server shutdown: {e}")


# For standalone testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")