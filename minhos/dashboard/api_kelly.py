#!/usr/bin/env python3
"""
MinhOS Kelly Criterion API Routes
=================================
REST API endpoints for ML-enhanced Kelly position sizing.

Endpoints:
- Kelly recommendations and position sizing
- Kelly performance metrics and history
- Risk-adjusted Kelly calculations
- Model confidence and predictions
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Add Kelly implementation to path - use absolute path
kelly_impl_path = Path(__file__).parent.parent.parent / "implementation" / "ml_kelly_criterion_week5"
sys.path.insert(0, str(kelly_impl_path.absolute()))

try:
    # Import Kelly services from the unified service architecture
    from ..services.position_sizing_service import get_position_sizing_service
    from ..ml.kelly_criterion import get_kelly_criterion, KellyPosition
    KELLY_SERVICES_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import Kelly services: {e}")
    # Create stub classes for API compatibility
    def get_position_sizing_service(): return None
    def get_kelly_criterion(): return None
    class KellyPosition: pass
    KELLY_SERVICES_AVAILABLE = False

from minhos.services import (
    get_market_data_service, get_state_manager, 
    get_ai_brain_service, get_risk_manager
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kelly", tags=["kelly"])

# Global Kelly service instance
kelly_service = None

# Response Models
class KellyRecommendationResponse(BaseModel):
    """Kelly recommendation API response"""
    symbol: str
    timestamp: datetime
    kelly_fraction: float
    position_size: int
    confidence: float
    win_probability: float
    win_loss_ratio: float
    capital_risk: float
    reasoning: str
    status: str
    ml_models_used: List[str]
    model_agreement: bool
    constraints_applied: List[str]

class KellyMetricsResponse(BaseModel):
    """Kelly performance metrics API response"""
    service_status: str
    total_recommendations: int
    avg_response_time_ms: float
    success_rate: float
    avg_kelly_fraction: float
    avg_position_size: int
    model_availability: Dict[str, bool]
    recent_performance: Dict[str, Any]

class KellyHealthResponse(BaseModel):
    """Kelly service health API response"""
    status: str
    ml_services_available: Dict[str, bool]
    last_recommendation_time: Optional[datetime]
    error_count: int
    uptime_seconds: float

async def get_kelly_service():
    """Get or initialize Kelly service"""
    global kelly_service
    if kelly_service is None:
        try:
            kelly_service = get_position_sizing_service()
            # Position sizing service doesn't need to be started separately
            # It's initialized when imported
        except Exception as e:
            logger.error(f"Failed to initialize Kelly service: {e}")
            kelly_service = None
    return kelly_service

@router.get("/current-recommendation", response_model=KellyRecommendationResponse)
async def get_current_kelly_recommendation(
    symbol: str = Query("NQU25-CME", description="Trading symbol"),
    account_capital: float = Query(100000.0, description="Account capital in USD")
):
    """Get current Kelly position size recommendation"""
    try:
        # Get current market data
        market_data_service = get_market_data_service()
        if not market_data_service:
            raise HTTPException(status_code=503, detail="Market data service unavailable")
        
        # Get current market data for symbol
        current_data = await market_data_service.get_current_data(symbol)
        if not current_data:
            raise HTTPException(status_code=404, detail=f"No market data for symbol {symbol}")
        
        # Get trading history for Kelly calculation
        state_manager = get_state_manager()
        trade_history = []
        if state_manager:
            recent_trades = await state_manager.get_recent_trades(days=30)
            trade_history = [trade for trade in recent_trades if trade.get('symbol') == symbol]
        
        # Get Kelly recommendation
        kelly_svc = await get_kelly_service()
        if not kelly_svc:
            raise HTTPException(status_code=503, detail="Kelly service unavailable")
        
        current_price = current_data.get('price', current_data.get('last_price', 100.0))
        recommendation = await kelly_svc.calculate_optimal_position(
            symbol=symbol,
            current_price=current_price,
            market_data=current_data
        )
        
        if not recommendation:
            raise HTTPException(status_code=503, detail="Kelly service unavailable")
        
        return KellyRecommendationResponse(
            symbol=recommendation.symbol,
            timestamp=recommendation.timestamp,
            kelly_fraction=recommendation.kelly_fraction,
            position_size=recommendation.recommended_size,
            confidence=recommendation.confidence_score,
            win_probability=recommendation.win_probability,
            win_loss_ratio=recommendation.expected_win / max(recommendation.expected_loss, 1.0),
            capital_risk=recommendation.kelly_fraction * account_capital,
            reasoning=recommendation.calculation_details.get('reason', 'ML-enhanced Kelly Criterion'),
            status='active' if recommendation.recommended_size > 0 else 'inactive',
            ml_models_used=['LSTM', 'Ensemble', 'Kelly'],
            model_agreement=recommendation.confidence_score > 0.7,
            constraints_applied=['risk_adjusted']
        )
        
    except Exception as e:
        logger.error(f"Error getting Kelly recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Kelly calculation failed: {str(e)}")

@router.get("/performance-metrics", response_model=KellyMetricsResponse)
async def get_kelly_performance_metrics():
    """Get Kelly service performance metrics"""
    try:
        kelly_svc = await get_kelly_service()
        if not kelly_svc:
            raise HTTPException(status_code=503, detail="Kelly service unavailable")
            
        status = kelly_svc.get_status()
        metrics = status.get('performance_metrics', {})
        
        return KellyMetricsResponse(
            service_status='running' if kelly_svc else 'stopped',
            total_recommendations=metrics.get('total_recommendations', 0),
            avg_response_time_ms=50.0,  # Placeholder
            success_rate=metrics.get('positions_accepted', 0) / max(metrics.get('total_recommendations', 1), 1),
            avg_kelly_fraction=metrics.get('avg_kelly_fraction', 0.0),
            avg_position_size=1,  # Placeholder
            model_availability={
                'lstm': status.get('lstm_connected', False),
                'ensemble': status.get('ensemble_connected', False),
                'kelly': True
            },
            recent_performance={'enabled': status.get('ml_enabled', False)}
        )
        
    except Exception as e:
        logger.error(f"Error getting Kelly metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@router.get("/service-health", response_model=KellyHealthResponse)
async def get_kelly_service_health():
    """Get Kelly service health status"""
    try:
        kelly_svc = await get_kelly_service()
        if not kelly_svc:
            return KellyHealthResponse(
                status='unavailable',
                ml_services_available={'lstm': False, 'ensemble': False, 'kelly': False},
                last_recommendation_time=None,
                error_count=1,
                uptime_seconds=0.0
            )
        
        status = kelly_svc.get_status()
        
        return KellyHealthResponse(
            status='running' if kelly_svc else 'stopped',
            ml_services_available={
                'lstm': status.get('lstm_connected', False),
                'ensemble': status.get('ensemble_connected', False),
                'kelly': True
            },
            last_recommendation_time=datetime.now() if status.get('recent_recommendations', 0) > 0 else None,
            error_count=0,
            uptime_seconds=3600.0  # Placeholder
        )
        
    except Exception as e:
        logger.error(f"Error getting Kelly health: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/recent-recommendations")
async def get_recent_kelly_recommendations(
    limit: int = Query(10, description="Number of recent recommendations"),
    symbol: Optional[str] = Query(None, description="Filter by symbol")
):
    """Get recent Kelly recommendations history"""
    try:
        kelly_svc = await get_kelly_service()
        recommendations = await kelly_svc.get_recent_recommendations(
            limit=limit,
            symbol=symbol
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

@router.post("/calculate-position-size")
async def calculate_kelly_position_size(
    request: Dict[str, Any]
):
    """Calculate Kelly position size for specific parameters"""
    try:
        required_fields = ['symbol', 'account_capital', 'win_probability', 'win_loss_ratio']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Use Kelly calculator directly for custom calculations
        kelly_svc = await get_kelly_service()
        
        # Mock market data for calculation
        mock_market_data = {
            'price': request.get('current_price', 100.0),
            'timestamp': datetime.now()
        }
        
        recommendation = await kelly_svc.get_kelly_recommendation(
            symbol=request['symbol'],
            market_data=mock_market_data,
            trade_history=[],  # Use empty history for pure calculation
            account_capital=request['account_capital'],
            override_probability=request['win_probability'],
            override_win_loss_ratio=request['win_loss_ratio']
        )
        
        return {
            "kelly_fraction": recommendation.kelly_fraction if recommendation else 0.0,
            "position_size": recommendation.position_size if recommendation else 0,
            "capital_risk": recommendation.capital_risk if recommendation else 0.0,
            "reasoning": recommendation.reasoning if recommendation else "Calculation failed",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error calculating position size: {e}")
        raise HTTPException(status_code=500, detail=f"Position size calculation failed: {str(e)}")

# Dashboard widget endpoints
@router.get("/dashboard-data")
async def get_kelly_dashboard_data(
    symbol: str = Query("NQU25-CME", description="Trading symbol")
):
    """Get Kelly data for dashboard widgets"""
    try:
        # Get current recommendation
        rec_response = await get_current_kelly_recommendation(symbol=symbol)
        
        # Get performance metrics
        metrics_response = await get_kelly_performance_metrics()
        
        # Get service health
        health_response = await get_kelly_service_health()
        
        return {
            "current_recommendation": rec_response.dict(),
            "performance_metrics": metrics_response.dict(),
            "service_health": health_response.dict(),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            "current_recommendation": None,
            "performance_metrics": None,
            "service_health": {"status": "error"},
            "error": str(e),
            "timestamp": datetime.now()
        }