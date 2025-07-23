#!/usr/bin/env python3
"""
MinhOS v3 Dashboard API Routes
==============================
REST API endpoints for system control and monitoring.

Endpoints:
- System status and control
- Trading operations
- Market data queries
- Configuration management
- Historical data access
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from minhos.services import (
    get_sierra_client, get_market_data_service, get_web_api_service,
    get_state_manager, get_ai_brain_service, get_trading_engine,
    get_pattern_analyzer, get_risk_manager
)
from minhos.services.state_manager import TradingState, SystemState
from minhos.services.trading_engine import MarketRegime
from minhos.services.risk_manager import RiskLevel

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Pydantic models for request/response
class SystemStatusResponse(BaseModel):
    """System status response model"""
    timestamp: datetime
    status: str
    services: Dict[str, Any]
    trading: Dict[str, Any]
    market: Dict[str, Any]
    risk: Dict[str, Any]

class TradingModeRequest(BaseModel):
    """Trading mode change request"""
    mode: str = Field(..., description="Trading mode: manual, semi_auto, full_auto")
    reason: Optional[str] = Field(None, description="Reason for mode change")

class PositionRequest(BaseModel):
    """Position management request"""
    symbol: str
    quantity: int
    side: str = Field(..., description="BUY or SELL")
    order_type: str = Field("MARKET", description="Order type: MARKET, LIMIT")
    price: Optional[float] = None

class ConfigUpdateRequest(BaseModel):
    """Configuration update request"""
    section: str
    key: str
    value: Any

# System endpoints
@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        state_manager = get_state_manager()
        trading_engine = get_trading_engine()
        market_data = get_market_data_service()
        risk_manager = get_risk_manager()
        
        # Get current states
        system_state = state_manager.get_current_state()
        trading_status = trading_engine.get_engine_status()
        market_status = await market_data.get_status() if hasattr(market_data, 'get_status') else {"connected": False}
        risk_status = risk_manager.get_detailed_status() if hasattr(risk_manager, 'get_detailed_status') else {"active": False}
        
        # Get AI Brain status
        ai_brain = get_ai_brain_service()
        ai_status = ai_brain.get_ai_status() if hasattr(ai_brain, 'get_ai_status') else {"connected": False}
        
        return SystemStatusResponse(
            timestamp=datetime.now(),
            status="operational" if system_state.get("system_state") == "ONLINE" else "degraded",
            services={
                "state_manager": {"health": system_state.get("system_state") == "ONLINE"},
                "trading_engine": {"health": trading_status.get("active", False), "mode": trading_status.get("mode", "Manual")},
                "market_data": {"health": market_status.get("connected", False), "symbols": market_status.get("symbols_count", 0)},
                "risk_manager": {"health": risk_status.get("active", False)},
                "ai_brain": {"health": ai_status.get("connected", False), "signals_generated": ai_status.get("stats", {}).get("signals_generated", 0), "analyses_performed": ai_status.get("stats", {}).get("analyses_performed", 0)}
            },
            trading={
                "mode": system_state.get("trading_state", "MANUAL"),
                "active": system_state.get("system_state") == "ONLINE",
                "positions": len(system_state.get("positions", {})),
                "total_pnl": sum(pos.get("unrealized_pnl", 0) for pos in system_state.get("positions", {}).values()),
                "last_update": system_state.get("last_market_update", "Never")
            },
            market={
                "connected": market_status.get("connected", False),
                "last_update": market_status.get("last_update"),
                "data_points": market_status.get("data_points", 0),
                "symbols": market_status.get("symbols", [])
            },
            risk={
                "level": risk_status.get("risk_level", "unknown"),
                "exposure": risk_status.get("total_exposure", 0),
                "margin_used": risk_status.get("margin_used", 0),
                "violations": risk_status.get("violations", [])
            }
        )
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trading/mode")
async def set_trading_mode(request: TradingModeRequest):
    """Change trading mode"""
    try:
        state_manager = get_state_manager()
        
        # Validate mode
        try:
            new_mode = TradingState[request.mode.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")
        
        # Update mode
        await state_manager.set_trading_mode(new_mode)
        
        logger.info(f"Trading mode changed to {new_mode.value} - {request.reason or 'No reason provided'}")
        
        return {
            "success": True,
            "mode": new_mode.value,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error setting trading mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trading/emergency-stop")
async def emergency_stop():
    """Emergency stop - halt all trading"""
    try:
        state_manager = get_state_manager()
        trading_engine = get_trading_engine()
        
        # Set mode to manual
        await state_manager.set_trading_mode(TradingState.MANUAL)
        
        # Stop trading engine
        await trading_engine.emergency_stop()
        
        logger.warning("EMERGENCY STOP activated")
        
        return {
            "success": True,
            "message": "Emergency stop activated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market data endpoints
@router.get("/market/data/{symbol}")
async def get_market_data(
    symbol: str,
    timeframe: str = Query("1m", description="Timeframe: 1m, 5m, 15m, 1h, 1d"),
    limit: int = Query(100, description="Number of bars to return")
):
    """Get market data for a symbol"""
    try:
        market_data = get_market_data_service()
        
        # Get historical data
        data = await market_data.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/symbols")
async def get_available_symbols():
    """Get list of available trading symbols"""
    try:
        sierra_client = get_sierra_client()
        symbols = await sierra_client.get_available_symbols()
        
        return {
            "symbols": symbols,
            "count": len(symbols),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Trading endpoints
@router.get("/trading/positions")
async def get_positions():
    """Get current positions"""
    try:
        trading_engine = get_trading_engine()
        positions = await trading_engine.get_positions()
        
        return {
            "positions": positions,
            "count": len(positions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trading/position")
async def manage_position(request: PositionRequest):
    """Open or close a position"""
    try:
        trading_engine = get_trading_engine()
        risk_manager = get_risk_manager()
        
        # Check risk before executing
        risk_check = await risk_manager.check_trade_risk(
            symbol=request.symbol,
            quantity=request.quantity,
            side=request.side
        )
        
        if not risk_check["approved"]:
            raise HTTPException(
                status_code=400,
                detail=f"Trade rejected by risk manager: {risk_check['reason']}"
            )
        
        # Execute trade
        result = await trading_engine.execute_trade(
            symbol=request.symbol,
            quantity=request.quantity,
            side=request.side,
            order_type=request.order_type,
            price=request.price
        )
        
        return {
            "success": True,
            "order_id": result.get("order_id"),
            "status": result.get("status"),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error managing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading/orders")
async def get_orders(
    status: Optional[str] = Query(None, description="Filter by status: open, filled, cancelled")
):
    """Get orders"""
    try:
        trading_engine = get_trading_engine()
        orders = await trading_engine.get_orders(status=status)
        
        return {
            "orders": orders,
            "count": len(orders),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI/Analysis endpoints
@router.get("/ai/signals")
async def get_ai_signals(
    symbol: Optional[str] = None,
    limit: int = Query(10, description="Number of signals to return")
):
    """Get recent AI trading signals"""
    try:
        ai_brain = get_ai_brain_service()
        signals = await ai_brain.get_recent_signals(symbol=symbol, limit=limit)
        
        return {
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting AI signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/market-analysis")
async def get_market_analysis():
    """Get current market analysis from AI"""
    try:
        ai_brain = get_ai_brain_service()
        analysis = await ai_brain.get_market_analysis()
        
        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pattern analysis endpoints
@router.get("/patterns/detected")
async def get_detected_patterns(
    symbol: Optional[str] = None,
    pattern_type: Optional[str] = None,
    limit: int = Query(20, description="Number of patterns to return")
):
    """Get recently detected patterns"""
    try:
        pattern_analyzer = get_pattern_analyzer()
        patterns = await pattern_analyzer.get_recent_patterns(
            symbol=symbol,
            pattern_type=pattern_type,
            limit=limit
        )
        
        return {
            "patterns": patterns,
            "count": len(patterns),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Risk management endpoints
@router.get("/risk/status")
async def get_risk_status():
    """Get current risk status"""
    try:
        risk_manager = get_risk_manager()
        status = await risk_manager.get_detailed_status()
        
        return {
            "risk_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting risk status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/parameters")
async def update_risk_parameters(parameters: Dict[str, Any] = Body(...)):
    """Update risk parameters"""
    try:
        risk_manager = get_risk_manager()
        await risk_manager.update_parameters(parameters)
        
        return {
            "success": True,
            "message": "Risk parameters updated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating risk parameters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@router.get("/config/{section}")
async def get_config_section(section: str):
    """Get configuration section"""
    try:
        state_manager = get_state_manager()
        config = await state_manager.get_config(section)
        
        return {
            "section": section,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/update")
async def update_config(request: ConfigUpdateRequest):
    """Update configuration value"""
    try:
        state_manager = get_state_manager()
        await state_manager.update_config(
            section=request.section,
            key=request.key,
            value=request.value
        )
        
        return {
            "success": True,
            "message": f"Updated {request.section}.{request.key}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Sierra Chart integration endpoints
@router.get("/sierra/status")
async def get_sierra_status():
    """Get Sierra Chart connection status"""
    try:
        sierra_client = get_sierra_client()
        status = await sierra_client.get_connection_status()
        
        return {
            "sierra_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Sierra status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sierra/command")
async def send_sierra_command(command: Dict[str, Any] = Body(...)):
    """Send command to Sierra Chart"""
    try:
        sierra_client = get_sierra_client()
        result = await sierra_client.send_command(command)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error sending Sierra command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def api_health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }