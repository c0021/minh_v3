#!/usr/bin/env python3
"""
MinhOS v3 Windows Bridge - Minimal Sierra Chart Interface

This bridge runs on Windows PC and provides a simple REST/WebSocket API
to expose Sierra Chart data to the Linux MinhOS v3 system via Tailscale.

Key Features:
- Minimal dependencies (FastAPI, uvicorn only)
- File-based Sierra Chart communication
- WebSocket streaming for real-time data
- Health monitoring endpoints
- Tailscale-ready networking
"""

import asyncio
import json
import logging
import os
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIERRA_DATA_PATH = Path("C:/SierraChart/Data")
MARKET_DATA_FILE = SIERRA_DATA_PATH / "minhos_market_data.json"
TRADE_COMMANDS_FILE = SIERRA_DATA_PATH / "minhos_trade_commands.json"
TRADE_RESPONSES_FILE = SIERRA_DATA_PATH / "minhos_trade_responses.json"

# Pydantic models
class MarketData(BaseModel):
    timestamp: str
    symbol: str
    price: float
    volume: int
    bid: float
    ask: float
    
class TradeCommand(BaseModel):
    command_id: str
    action: str  # "BUY" or "SELL"
    symbol: str
    quantity: int
    price: Optional[float] = None
    order_type: str = "MARKET"

class TradeResponse(BaseModel):
    command_id: str
    status: str  # "PENDING", "FILLED", "REJECTED"
    message: str
    fill_price: Optional[float] = None
    timestamp: str

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    sierra_connected: bool
    data_file_exists: bool
    last_data_update: Optional[str]

# FastAPI app
app = FastAPI(
    title="MinhOS v3 Windows Bridge",
    description="Sierra Chart bridge for MinhOS v3 Linux system",
    version="3.0.0"
)

# CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        if self.active_connections:
            message = json.dumps(data)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Utility functions
def read_json_file(file_path: Path) -> Optional[dict]:
    """Read JSON file safely"""
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading {file_path}: {e}")
    return None

def write_json_file(file_path: Path, data: dict) -> bool:
    """Write JSON file safely"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Error writing {file_path}: {e}")
        return False

def get_latest_market_data() -> Optional[MarketData]:
    """Get the latest market data from Sierra Chart file"""
    data = read_json_file(MARKET_DATA_FILE)
    if data:
        try:
            return MarketData(**data)
        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
    return None

# REST API Endpoints
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    sierra_connected = SIERRA_DATA_PATH.exists()
    data_exists = MARKET_DATA_FILE.exists()
    
    last_update = None
    if data_exists:
        try:
            stat = MARKET_DATA_FILE.stat()
            last_update = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except:
            pass
    
    return HealthStatus(
        status="healthy" if sierra_connected else "degraded",
        timestamp=datetime.now().isoformat(),
        sierra_connected=sierra_connected,
        data_file_exists=data_exists,
        last_data_update=last_update
    )

@app.get("/api/market_data", response_model=MarketData)
async def get_market_data():
    """Get current market data snapshot"""
    market_data = get_latest_market_data()
    if not market_data:
        raise HTTPException(status_code=404, detail="No market data available")
    return market_data

@app.post("/api/trade/execute")
async def execute_trade(command: TradeCommand):
    """Execute a trade command"""
    logger.info(f"Executing trade: {command}")
    
    # Write command to Sierra Chart file
    command_data = command.dict()
    command_data["timestamp"] = datetime.now().isoformat()
    
    success = write_json_file(TRADE_COMMANDS_FILE, command_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to write trade command")
    
    return {"status": "submitted", "command_id": command.command_id}

@app.get("/api/trade/status/{command_id}")
async def get_trade_status(command_id: str):
    """Get trade execution status"""
    response_data = read_json_file(TRADE_RESPONSES_FILE)
    if response_data and response_data.get("command_id") == command_id:
        return TradeResponse(**response_data)
    
    return {"command_id": command_id, "status": "PENDING", "message": "No response yet"}

@app.websocket("/ws/market_stream")
async def websocket_market_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time market data streaming"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send current market data every second
            market_data = get_latest_market_data()
            if market_data:
                await websocket.send_text(market_data.json())
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Background task for file monitoring
async def monitor_sierra_files():
    """Monitor Sierra Chart files for changes and broadcast updates"""
    last_modified = None
    
    while True:
        try:
            if MARKET_DATA_FILE.exists():
                current_modified = MARKET_DATA_FILE.stat().st_mtime
                
                if last_modified is None or current_modified != last_modified:
                    last_modified = current_modified
                    market_data = get_latest_market_data()
                    
                    if market_data:
                        await manager.broadcast({
                            "type": "market_update",
                            "data": market_data.dict()
                        })
            
            await asyncio.sleep(0.1)  # Check every 100ms
            
        except Exception as e:
            logger.error(f"File monitoring error: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(monitor_sierra_files())
    
    # Log startup information
    hostname = socket.gethostname()
    logger.info("="*60)
    logger.info("MinhOS v3 Windows Bridge Started")
    logger.info("="*60)
    logger.info(f"Hostname: {hostname}")
    logger.info(f"Sierra Data Path: {SIERRA_DATA_PATH}")
    logger.info(f"Market Data File: {MARKET_DATA_FILE}")
    logger.info("Available via Tailscale at:")
    logger.info(f"  - http://{hostname}:8765")
    logger.info(f"  - http://trading-pc:8765  (if hostname is 'trading-pc')")
    logger.info("Endpoints:")
    logger.info("  - GET  /health")
    logger.info("  - GET  /api/market_data")
    logger.info("  - POST /api/trade/execute")
    logger.info("  - GET  /api/trade/status/{command_id}")
    logger.info("  - WS   /ws/market_stream")
    logger.info("="*60)

if __name__ == "__main__":
    # Ensure Sierra Chart data directory exists
    SIERRA_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces (including Tailscale)
        port=8765,
        log_level="info"
    )