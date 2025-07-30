#!/usr/bin/env python3
"""
MinhOS v3 Trading Dashboard API
================================
Trading-specific API endpoints for configuration, history, and performance tracking.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# API Router
router = APIRouter(prefix="/api/trading", tags=["trading"])

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"

class TradingConfig(BaseModel):
    """Trading configuration model"""
    auto_trade_enabled: bool = Field(..., description="Enable autonomous trading")
    trading_enabled: bool = Field(..., description="Enable manual trading")
    max_orders_per_minute: int = Field(default=10, description="Rate limiting")
    confidence_threshold: float = Field(default=75.0, description="Min confidence for auto-trade (%)")
    max_position_size: int = Field(default=1, description="Max contracts per position")
    daily_loss_limit: float = Field(default=1000.0, description="Daily loss limit ($)")
    risk_per_trade: float = Field(default=2.0, description="Risk per trade (% of account)")

class TradeRecord(BaseModel):
    """Trade history record"""
    id: int
    timestamp: datetime
    symbol: str
    side: str
    quantity: int
    price: float
    pnl: Optional[float] = None
    signal_confidence: float
    execution_time_ms: int

class PerformanceMetrics(BaseModel):
    """Trading performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    sharpe_ratio: float
    max_drawdown: float
    current_streak: int
    best_trade: float
    worst_trade: float

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATA_DIR / "state.db")

@router.get("/config", response_model=TradingConfig)
async def get_trading_config():
    """Get current trading configuration"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get latest config
        cursor.execute("""
            SELECT auto_trade_enabled, trading_enabled, max_orders_per_minute 
            FROM system_config 
            ORDER BY id DESC LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            config = TradingConfig(
                auto_trade_enabled=bool(result[0]),
                trading_enabled=bool(result[1]),
                max_orders_per_minute=result[2],
                confidence_threshold=75.0,  # TODO: Store in DB
                max_position_size=1,
                daily_loss_limit=1000.0,
                risk_per_trade=2.0
            )
        else:
            # Default config
            config = TradingConfig(
                auto_trade_enabled=False,
                trading_enabled=False,
                max_orders_per_minute=10,
                confidence_threshold=75.0,
                max_position_size=1,
                daily_loss_limit=1000.0,
                risk_per_trade=2.0
            )
        
        conn.close()
        return config
        
    except Exception as e:
        logger.error(f"Error getting trading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
async def update_trading_config(config: TradingConfig):
    """Update trading configuration"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert new config record
        cursor.execute("""
            INSERT INTO system_config 
            (auto_trade_enabled, trading_enabled, debug_mode, max_orders_per_minute, 
             data_validation_enabled, emergency_stop_triggered, updated_at)
            VALUES (?, ?, 0, ?, 1, 0, ?)
        """, (
            int(config.auto_trade_enabled),
            int(config.trading_enabled),
            config.max_orders_per_minute,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Trading config updated: auto_trade={config.auto_trade_enabled}, "
                   f"trading={config.trading_enabled}")
        
        return {"status": "success", "message": "Configuration updated"}
        
    except Exception as e:
        logger.error(f"Error updating trading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[TradeRecord])
async def get_trade_history(
    limit: int = Query(default=100, description="Number of trades to return"),
    symbol: Optional[str] = Query(default=None, description="Filter by symbol")
):
    """Get trade history"""
    try:
        # For now, return empty list since no trades have been executed
        # TODO: Implement actual trade tracking
        return []
        
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    period: str = Query(default="all", description="Time period: today, week, month, all")
):
    """Get trading performance metrics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate date filter
        start_date = None
        if period == "today":
            start_date = datetime.utcnow().date()
        elif period == "week":
            start_date = (datetime.utcnow() - timedelta(days=7)).date()
        elif period == "month":
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        
        # Get PnL history
        query = "SELECT * FROM pnl_history"
        params = []
        if start_date:
            query += " WHERE date >= ?"
            params.append(start_date.isoformat())
        
        cursor.execute(query, params)
        pnl_records = cursor.fetchall()
        
        # Calculate metrics
        if pnl_records:
            total_pnl = sum(r[4] for r in pnl_records)  # total_pnl column
            # TODO: Calculate actual metrics from trade history
            metrics = PerformanceMetrics(
                total_trades=len(pnl_records),
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=total_pnl,
                average_win=0.0,
                average_loss=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                current_streak=0,
                best_trade=0.0,
                worst_trade=0.0
            )
        else:
            # No trades yet
            metrics = PerformanceMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                average_win=0.0,
                average_loss=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                current_streak=0,
                best_trade=0.0,
                worst_trade=0.0
            )
        
        conn.close()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_current_positions():
    """Get current open positions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM positions")
        positions = cursor.fetchall()
        
        result = []
        for pos in positions:
            result.append({
                "symbol": pos[0],
                "quantity": pos[1],
                "side": pos[2],
                "entry_price": pos[3],
                "current_price": pos[4],
                "unrealized_pnl": pos[5],
                "entry_time": pos[6],
                "last_update": pos[7]
            })
        
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-stop")
async def trigger_emergency_stop():
    """Trigger emergency stop - closes all positions and disables trading"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Disable trading and set emergency stop
        cursor.execute("""
            INSERT INTO system_config 
            (auto_trade_enabled, trading_enabled, debug_mode, max_orders_per_minute, 
             data_validation_enabled, emergency_stop_triggered, updated_at)
            VALUES (0, 0, 0, 10, 1, 1, ?)
        """, (datetime.utcnow().isoformat(),))
        
        conn.commit()
        conn.close()
        
        logger.warning("EMERGENCY STOP TRIGGERED")
        
        # TODO: Close all open positions via Sierra Chart
        
        return {"status": "success", "message": "Emergency stop activated"}
        
    except Exception as e:
        logger.error(f"Error triggering emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))