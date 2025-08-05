#!/usr/bin/env python3
"""
MinhOS v4 API Server (Consolidated)
===================================
Unified API server combining all HTTP endpoints from:
- web_api.py (Market data and system APIs)
- dashboard/api.py (Dashboard system control APIs)
- dashboard/api_enhanced.py (Enhanced dashboard features)
- dashboard/api_trading.py (Trading configuration APIs)

Provides complete REST API interface for MinhOS system.
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from minhos.core.base_service import ServiceStatus
from dataclasses import asdict
from enum import Enum

from fastapi import FastAPI, APIRouter, HTTPException, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# Core MinhOS imports
from minhos.core.base_service import BaseService
from minhos.core.config import config

# Service imports  
from .sierra_client import get_sierra_client
from .state_manager import get_state_manager, TradingState, SystemState
from .ai_brain_service import get_ai_brain_service
from .risk_manager import get_risk_manager, RiskLevel
from .trading_service import get_trading_service
from .chat_service import get_chat_service

# Data models and utilities
from ..models.market import MarketData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# ============================================================================
# Pydantic Models for API Requests/Responses
# ============================================================================

class SystemStatusResponse(BaseModel):
    """System status response model"""
    status: str
    timestamp: datetime
    services: Dict[str, bool]
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    
class MarketDataResponse(BaseModel):
    """Market data response model"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    last_trade_size: Optional[int] = None

class TradingConfig(BaseModel):
    """Trading configuration model"""
    auto_trade_enabled: bool = Field(..., description="Enable autonomous trading")
    trading_enabled: bool = Field(..., description="Enable manual trading")
    max_orders_per_minute: int = Field(default=10, description="Rate limiting")
    confidence_threshold: float = Field(default=75.0, description="Min confidence for auto-trade (%)")
    max_position_size: int = Field(default=5, description="Maximum position size")
    daily_loss_limit: float = Field(default=500.0, description="Daily loss limit ($)")

class TradingCommand(BaseModel):
    """Trading command model"""
    action: str = Field(..., description="BUY, SELL, or CLOSE")
    symbol: str = Field(..., description="Trading symbol")
    quantity: int = Field(..., description="Number of contracts")
    price: Optional[float] = Field(None, description="Limit price (optional)")
    reason: str = Field("Manual trade", description="Reason for trade")

class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")

class DecisionResolution(BaseModel):
    """Decision resolution model"""
    resolution: str = Field(..., description="Decision resolution")

# Enhanced dashboard models
class AutonomousStatus(BaseModel):
    """Autonomous trading status"""
    enabled: bool
    confidence_threshold: float
    trades_today: int
    success_rate: float
    last_signal: Optional[Dict[str, Any]] = None

class PatternLearningData(BaseModel):
    """Pattern learning visualization data"""
    patterns_learned: int
    accuracy_improvement: float
    recent_patterns: List[Dict[str, Any]]

class HistoricalScope(BaseModel):
    """Historical data scope metrics"""
    total_data_points: int
    date_range_start: datetime
    date_range_end: datetime
    coverage_percentage: float
    data_quality_score: float

class RiskControlsData(BaseModel):
    """Advanced risk controls data"""
    daily_loss_limit: float
    current_exposure: float
    max_position_size: int
    risk_score: float
    active_alerts: List[str]

# ============================================================================
# API Server Class
# ============================================================================

class APIServer(BaseService):
    """
    Consolidated API Server for MinhOS v4
    
    Combines all HTTP endpoints from multiple API files into a single FastAPI application.
    Provides comprehensive REST API interface for market data, trading, system control,
    and dashboard functionality.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        super().__init__("APIServer")
        self.host = host
        self.port = port
        
        # Create FastAPI app
        self.app = FastAPI(
            title="MinhOS v4 API Server",
            description="Consolidated REST API for MinhOS trading system",
            version="4.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Service references
        self.sierra_client = None
        self.state_manager = None
        self.ai_brain = None
        self.risk_manager = None
        self.trading_service = None
        self.chat_service = None
        
        # Server state
        self.start_time = datetime.now()
        self.request_count = 0
        self.active_websockets = set()
        
        # Initialize routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        # System routes
        self._setup_system_routes()
        
        # Market data routes
        self._setup_market_data_routes()
        
        # Trading routes
        self._setup_trading_routes()
        
        # Chat routes
        self._setup_chat_routes()
        
        # Enhanced dashboard routes
        self._setup_enhanced_routes()
        
        # Static file serving
        self._setup_static_routes()
        
        # WebSocket routes
        self._setup_websocket_routes()
    
    # ========================================================================
    # System Routes (from dashboard/api.py)
    # ========================================================================
    
    def _setup_system_routes(self):
        """Setup system control and monitoring routes"""
        
        @self.app.get("/api/system/status", response_model=SystemStatusResponse)
        async def get_system_status():
            """Get comprehensive system status"""
            try:
                self.request_count += 1
                
                # Collect service status
                services = {}
                if self.sierra_client:
                    services["sierra_client"] = getattr(self.sierra_client, 'status', None) == ServiceStatus.RUNNING
                if self.state_manager:
                    services["state_manager"] = getattr(self.state_manager, 'status', None) == ServiceStatus.RUNNING
                if self.ai_brain:
                    services["ai_brain"] = getattr(self.ai_brain, 'status', None) == ServiceStatus.RUNNING
                if self.risk_manager:
                    services["risk_manager"] = getattr(self.risk_manager, 'status', None) == ServiceStatus.RUNNING
                if self.trading_service:
                    services["trading_service"] = getattr(self.trading_service, 'status', None) == ServiceStatus.RUNNING
                
                # Calculate uptime
                uptime = (datetime.now() - self.start_time).total_seconds()
                
                return SystemStatusResponse(
                    status="operational" if any(services.values()) else "starting",
                    timestamp=datetime.now(),
                    services=services,
                    uptime_seconds=uptime,
                    memory_usage_mb=0.0,  # TODO: Add actual memory monitoring
                    cpu_usage_percent=0.0  # TODO: Add actual CPU monitoring
                )
                
            except Exception as e:
                logger.error(f"System status error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/system/health")
        async def health_check():
            """Simple health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now()}
        
        @self.app.post("/api/system/restart")
        async def restart_system():
            """Restart system services"""
            try:
                # This would restart services - implementation depends on deployment
                logger.info("System restart requested")
                return {"status": "restart_initiated", "timestamp": datetime.now()}
            except Exception as e:
                logger.error(f"System restart error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    # ========================================================================
    # Market Data Routes (from web_api.py and dashboard/api.py)
    # ========================================================================
    
    def _setup_market_data_routes(self):
        """Setup market data API routes"""
        
        @self.app.get("/api/market/latest", response_model=MarketDataResponse)
        async def get_latest_market_data():
            """Get latest market data"""
            try:
                if not self.sierra_client:
                    raise HTTPException(status_code=503, detail="Sierra client not available")
                
                # Get live market data
                data = await self._get_live_market_data()
                if not data:
                    raise HTTPException(status_code=503, detail="No market data available")
                
                return MarketDataResponse(
                    symbol=data.get('symbol', 'UNKNOWN'),
                    price=data.get('price', 0.0),
                    volume=data.get('volume', 0),
                    timestamp=datetime.now(),
                    bid=data.get('bid'),
                    ask=data.get('ask'),
                    last_trade_size=data.get('last_trade_size')
                )
                
            except Exception as e:
                logger.error(f"Market data error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/market/historical")
        async def get_historical_data(
            symbol: str = Query(..., description="Trading symbol"),
            days: int = Query(default=30, description="Number of days")
        ):
            """Get historical market data"""
            try:
                # Implementation would fetch historical data
                # For now, return empty structure
                return {
                    "symbol": symbol,
                    "days": days,
                    "data": [],
                    "message": "Historical data implementation pending"
                }
                
            except Exception as e:
                logger.error(f"Historical data error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/market/symbols")
        async def get_available_symbols():
            """Get list of available trading symbols"""
            try:
                # Get symbols from centralized symbol management
                from ..core.symbol_integration import get_symbol_integration
                symbol_integration = get_symbol_integration()
                
                if symbol_integration:
                    symbols = symbol_integration.get_available_symbols()
                    return {"symbols": symbols}
                else:
                    return {"symbols": ["NQU25-CME"], "fallback": True}
                
            except Exception as e:
                logger.error(f"Symbols error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    # ========================================================================
    # Trading Routes (from dashboard/api_trading.py)
    # ========================================================================
    
    def _setup_trading_routes(self):
        """Setup trading API routes"""
        
        @self.app.get("/api/trading/config", response_model=TradingConfig)
        async def get_trading_config():
            """Get current trading configuration"""
            try:
                if self.state_manager:
                    state = await self.state_manager.get_trading_state()
                    return TradingConfig(
                        auto_trade_enabled=getattr(state, 'auto_trade_enabled', False),
                        trading_enabled=getattr(state, 'trading_enabled', True),
                        max_orders_per_minute=10,
                        confidence_threshold=75.0,
                        max_position_size=5,
                        daily_loss_limit=500.0
                    )
                else:
                    # Default configuration
                    return TradingConfig(
                        auto_trade_enabled=False,
                        trading_enabled=True,
                        max_orders_per_minute=10,
                        confidence_threshold=75.0,
                        max_position_size=5,
                        daily_loss_limit=500.0
                    )
                    
            except Exception as e:
                logger.error(f"Trading config error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/trading/config")
        async def update_trading_config(config: TradingConfig):
            """Update trading configuration"""
            try:
                # Update configuration through state manager
                if self.state_manager:
                    # Implementation would update the trading config
                    logger.info(f"Trading config updated: {config}")
                
                return {"status": "updated", "config": config}
                
            except Exception as e:
                logger.error(f"Trading config update error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/trading/execute")
        async def execute_trade(command: TradingCommand):
            """Execute a trading command"""
            try:
                if not self.trading_service:
                    raise HTTPException(status_code=503, detail="Trading service not available")
                
                # Validate command
                if command.action not in ["BUY", "SELL", "CLOSE"]:
                    raise HTTPException(status_code=400, detail="Invalid trading action")
                
                # Execute through trading service
                # Implementation would create and execute trade order
                logger.info(f"Trade command received: {command}")
                
                return {
                    "status": "submitted",
                    "command": command,
                    "timestamp": datetime.now()
                }
                
            except Exception as e:
                logger.error(f"Trade execution error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/trading/positions")
        async def get_positions():
            """Get current trading positions"""
            try:
                if self.trading_service:
                    positions = await self.trading_service.get_positions()
                    return {"positions": positions}
                else:
                    return {"positions": []}
                    
            except Exception as e:
                logger.error(f"Positions error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/trading/performance")
        async def get_trading_performance():
            """Get trading performance metrics"""
            try:
                # Implementation would return performance data
                return {
                    "daily_pnl": 0.0,
                    "total_pnl": 0.0,
                    "trades_today": 0,
                    "win_rate": 0.0,
                    "avg_trade_duration": 0.0
                }
                
            except Exception as e:
                logger.error(f"Performance error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    # ========================================================================
    # Chat Routes (from websocket_chat.py)
    # ========================================================================
    
    def _setup_chat_routes(self):
        """Setup chat API routes"""
        
        @self.app.post("/api/chat/message")
        async def send_chat_message(message: ChatMessage):
            """Send a chat message"""
            try:
                if not self.chat_service:
                    raise HTTPException(status_code=503, detail="Chat service not available")
                
                # Process message through chat service
                response = await self.chat_service.process_message(
                    message.message,
                    session_id=message.session_id
                )
                
                return {
                    "response": response,
                    "timestamp": datetime.now(),
                    "session_id": message.session_id
                }
                
            except Exception as e:
                logger.error(f"Chat message error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/chat/history")
        async def get_chat_history(
            session_id: Optional[str] = Query(None),
            limit: int = Query(default=50)
        ):
            """Get chat conversation history"""
            try:
                if self.chat_service:
                    history = await self.chat_service.get_history(session_id, limit)
                    return {"history": history}
                else:
                    return {"history": []}
                    
            except Exception as e:
                logger.error(f"Chat history error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    # ========================================================================
    # Enhanced Dashboard Routes (from dashboard/api_enhanced.py)
    # ========================================================================
    
    def _setup_enhanced_routes(self):
        """Setup enhanced dashboard API routes"""
        
        @self.app.get("/api/enhanced/autonomous-status", response_model=AutonomousStatus)
        async def get_autonomous_status():
            """Get autonomous trading status"""
            try:
                if self.trading_service:
                    status = await self.trading_service.get_status()
                    return AutonomousStatus(
                        enabled=status.get('autonomous_enabled', False),
                        confidence_threshold=75.0,
                        trades_today=status.get('trades_today', 0),
                        success_rate=status.get('success_rate', 0.0),
                        last_signal=status.get('last_signal')
                    )
                else:
                    return AutonomousStatus(
                        enabled=False,
                        confidence_threshold=75.0,
                        trades_today=0,
                        success_rate=0.0
                    )
                    
            except Exception as e:
                logger.error(f"Autonomous status error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/enhanced/pattern-learning", response_model=PatternLearningData)
        async def get_pattern_learning_data():
            """Get pattern learning visualization data"""
            try:
                if self.ai_brain:
                    # Get pattern data from AI brain
                    patterns = await self.ai_brain.get_pattern_analysis()
                    return PatternLearningData(
                        patterns_learned=patterns.get('patterns_learned', 0),
                        accuracy_improvement=patterns.get('accuracy_improvement', 0.0),
                        recent_patterns=patterns.get('recent_patterns', [])
                    )
                else:
                    return PatternLearningData(
                        patterns_learned=0,
                        accuracy_improvement=0.0,
                        recent_patterns=[]
                    )
                    
            except Exception as e:
                logger.error(f"Pattern learning error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/enhanced/historical-scope", response_model=HistoricalScope)
        async def get_historical_scope():
            """Get historical data scope metrics"""
            try:
                # Implementation would return actual historical data metrics
                return HistoricalScope(
                    total_data_points=1000000,
                    date_range_start=datetime.now() - timedelta(days=365),
                    date_range_end=datetime.now(),
                    coverage_percentage=95.0,
                    data_quality_score=98.5
                )
                
            except Exception as e:
                logger.error(f"Historical scope error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/enhanced/risk-controls", response_model=RiskControlsData)
        async def get_risk_controls():
            """Get advanced risk controls data"""
            try:
                if self.risk_manager:
                    status = self.risk_manager.get_risk_status()
                    return RiskControlsData(
                        daily_loss_limit=status.get('daily_loss_limit', 500.0),
                        current_exposure=status.get('current_exposure', 0.0),
                        max_position_size=status.get('max_position_size', 5),
                        risk_score=status.get('risk_score', 0.0),
                        active_alerts=status.get('active_alerts', [])
                    )
                else:
                    return RiskControlsData(
                        daily_loss_limit=500.0,
                        current_exposure=0.0,
                        max_position_size=5,
                        risk_score=0.0,
                        active_alerts=[]
                    )
                    
            except Exception as e:
                logger.error(f"Risk controls error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/symbols/rollover-status")
        async def get_rollover_status():
            """Get symbol rollover status for dashboard alerts"""
            try:
                from ..core.symbol_integration import get_symbol_integration
                symbol_integration = get_symbol_integration()
                
                if symbol_integration:
                    rollover_data = symbol_integration.get_rollover_alerts(days_ahead=60)
                    return {"rollover_alerts": rollover_data}
                else:
                    # Fallback data
                    return {
                        "rollover_alerts": [{
                            "symbol": "NQU25-CME",
                            "next_symbol": "NQZ25-CME",
                            "expiration_date": "2025-09-09",
                            "days_until_rollover": 45,
                            "alert_level": "info"
                        }]
                    }
                    
            except Exception as e:
                logger.error(f"Rollover status error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    # ========================================================================
    # Static File and WebSocket Routes
    # ========================================================================
    
    def _setup_static_routes(self):
        """Setup static file serving"""
        # Mount static files directory if it exists
        static_dir = Path(__file__).parent.parent / "dashboard" / "static"
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    def _setup_websocket_routes(self):
        """Setup WebSocket routes"""
        
        @self.app.websocket("/ws/status")
        async def websocket_status(websocket: WebSocket):
            """WebSocket endpoint for real-time status updates"""
            await websocket.accept()
            self.active_websockets.add(websocket)
            
            try:
                while True:
                    # Send status update every 5 seconds
                    status = await self._get_system_status()
                    await websocket.send_json(status)
                    await asyncio.sleep(5)
                    
            except WebSocketDisconnect:
                self.active_websockets.discard(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.active_websockets.discard(websocket)
        
        @self.app.websocket("/ws/market")
        async def websocket_market_data(websocket: WebSocket):
            """WebSocket endpoint for real-time market data"""
            await websocket.accept()
            self.active_websockets.add(websocket)
            
            try:
                while True:
                    # Send market data update every second
                    data = await self._get_live_market_data()
                    if data:
                        await websocket.send_json(data)
                    await asyncio.sleep(1)
                    
            except WebSocketDisconnect:
                self.active_websockets.discard(websocket)
            except Exception as e:
                logger.error(f"Market WebSocket error: {e}")
                self.active_websockets.discard(websocket)
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _get_live_market_data(self) -> Optional[Dict[str, Any]]:
        """Get live market data from Sierra client"""
        try:
            if self.sierra_client and hasattr(self.sierra_client, 'last_market_data'):
                return self.sierra_client.last_market_data
            return None
        except Exception as e:
            logger.error(f"Live market data error: {e}")
            return None
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            services = {}
            if self.sierra_client:
                services["sierra_client"] = getattr(self.sierra_client, 'status', None) == ServiceStatus.RUNNING
            if self.state_manager:
                services["state_manager"] = getattr(self.state_manager, 'status', None) == ServiceStatus.RUNNING
            if self.ai_brain:
                services["ai_brain"] = getattr(self.ai_brain, 'status', None) == ServiceStatus.RUNNING
            if self.risk_manager:
                services["risk_manager"] = getattr(self.risk_manager, 'status', None) == ServiceStatus.RUNNING
            if self.trading_service:
                services["trading_service"] = getattr(self.trading_service, 'status', None) == ServiceStatus.RUNNING
            
            return {
                "status": "operational" if any(services.values()) else "starting",
                "timestamp": datetime.now().isoformat(),
                "services": services,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "request_count": self.request_count,
                "active_websockets": len(self.active_websockets)
            }
        except Exception as e:
            logger.error(f"System status error: {e}")
            return {"status": "error", "error": str(e)}
    
    # ========================================================================
    # Service Lifecycle
    # ========================================================================
    
    # Abstract method implementations for BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        # Get service references
        self.sierra_client = get_sierra_client()
        self.state_manager = get_state_manager()
        self.ai_brain = get_ai_brain_service()
        self.risk_manager = get_risk_manager()
        self.trading_service = get_trading_service()
        
        try:
            self.chat_service = get_chat_service()
        except:
            logger.warning("Chat service not available")
    
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
        
        logger.info(f"API Server started successfully on {self.host}:{self.port}")
        logger.info(f"API documentation available at http://{self.host}:{self.port}/docs")
    
    async def _stop_service(self):
        """Stop service-specific functionality"""
        # Close all WebSocket connections
        for websocket in list(self.active_websockets):
            try:
                await websocket.close()
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
        self.active_websockets.clear()

    async def start(self):
        """Start the API server"""
        logger.info(f"Starting API Server on {self.host}:{self.port}")
        
        try:
            # Use BaseService start method
            await super().start()
            
        except Exception as e:
            logger.error(f"Failed to start API Server: {e}")
            raise
    
    async def stop(self):
        """Stop the API server"""
        logger.info("Stopping API Server...")
        
        try:
            # Use BaseService stop method
            await super().stop()
            logger.info("API Server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping API Server: {e}")

# ============================================================================
# Service Registry
# ============================================================================

_api_server_instance = None

def get_api_server() -> APIServer:
    """Get the global API server instance"""
    global _api_server_instance
    if _api_server_instance is None:
        _api_server_instance = APIServer()
    return _api_server_instance

async def create_api_server(host: str = "0.0.0.0", port: int = 8000) -> APIServer:
    """Create and start a new API server instance"""
    server = APIServer(host=host, port=port)
    await server.start()
    return server

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main function for standalone execution"""
    api_server = APIServer()
    
    try:
        await api_server.start()
        logger.info("API Server running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"API Server error: {e}")
    finally:
        await api_server.stop()

if __name__ == "__main__":
    asyncio.run(main())