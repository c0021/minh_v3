#!/usr/bin/env python3
"""
ML Performance Dashboard API

Provides endpoints for monitoring ML model performance, accuracy tracking,
and system optimization metrics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque, defaultdict
import statistics
import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..services import get_ai_brain_service, get_trading_engine, get_state_manager
from ..services.ml_monitoring_service import get_ml_monitoring_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml", tags=["ml-performance"])

# ML Performance tracking storage
ml_performance_history = deque(maxlen=1000)
model_accuracy_history = defaultdict(lambda: deque(maxlen=100))
prediction_latency_history = deque(maxlen=100)

class MLPerformanceData(BaseModel):
    """ML Performance data model"""
    timestamp: str
    lstm_accuracy: float
    ensemble_accuracy: float
    kelly_win_rate: float
    prediction_latency: float
    models_enabled: Dict[str, bool]
    confidence_distribution: Dict[str, int]

class MLSystemStatus(BaseModel):
    """ML System status model"""
    lstm_enabled: bool
    ensemble_enabled: bool
    kelly_enabled: bool
    total_predictions: int
    avg_confidence: float
    system_health: str

@router.get("/status", response_model=MLSystemStatus)
async def get_ml_system_status():
    """Get overall ML system status"""
    try:
        ai_brain = get_ai_brain_service()
        
        if not ai_brain or not hasattr(ai_brain, 'ml_capabilities'):
            return MLSystemStatus(
                lstm_enabled=False,
                ensemble_enabled=False,
                kelly_enabled=False,
                total_predictions=0,
                avg_confidence=0.0,
                system_health="disabled"
            )
        
        ml_caps = ai_brain.ml_capabilities
        
        # Initialize defaults
        lstm_enabled = False
        lstm_predictions = 0
        ensemble_enabled = False
        ensemble_predictions = 0
        kelly_enabled = False
        
        # Check if models are available through pipeline service
        if 'pipeline' in ml_caps:
            pipeline = ml_caps['pipeline']
            
            # LSTM Predictor Status
            if hasattr(pipeline, 'lstm_predictor') and pipeline.lstm_predictor:
                # Model is loaded and available
                lstm_enabled = True
                lstm_predictions = 0  # Reset when monitoring detects activity
                
            # Ensemble Manager Status  
            if hasattr(pipeline, 'ensemble_manager') and pipeline.ensemble_manager:
                # Model is loaded and available
                ensemble_enabled = True
                ensemble_predictions = 0  # Reset when monitoring detects activity
            
            # Kelly Manager Status
            if hasattr(pipeline, 'kelly_manager') and pipeline.kelly_manager:
                # Model is loaded and available
                kelly_enabled = True
        
        # Fallback: Check individual model keys (legacy support)
        if 'lstm' in ml_caps:
            lstm_stats = ml_caps['lstm'].get_performance_stats()
            lstm_enabled = lstm_stats.get('is_enabled', False)
            lstm_predictions = lstm_stats.get('predictions_made', 0)
        
        if 'ensemble' in ml_caps:
            ensemble_stats = ml_caps['ensemble'].get_performance_stats()
            ensemble_enabled = ensemble_stats.get('is_enabled', False)
            ensemble_predictions = ensemble_stats.get('predictions_made', 0)
        
        if 'kelly' in ml_caps:
            try:
                kelly_status = ml_caps['kelly'].get_system_status()
                kelly_enabled = kelly_status.get('config', {}).get('enabled', True)
            except:
                kelly_enabled = True  # Assume enabled if no error
        
        # Calculate system health
        total_predictions = lstm_predictions + ensemble_predictions
        enabled_count = sum([lstm_enabled, ensemble_enabled, kelly_enabled])
        
        if enabled_count == 3 and total_predictions > 0:
            system_health = "optimal"
        elif enabled_count >= 2:
            system_health = "good"
        elif enabled_count >= 1:
            system_health = "limited"
        else:
            system_health = "disabled"
        
        # Calculate average confidence from recent signals
        avg_confidence = 0.5
        if hasattr(ai_brain, 'analysis_history') and ai_brain.analysis_history:
            recent_signals = []
            for analysis in list(ai_brain.analysis_history)[-20:]:
                if analysis.get('signal') and analysis['signal'].get('confidence'):
                    recent_signals.append(analysis['signal']['confidence'])
            
            if recent_signals:
                avg_confidence = statistics.mean(recent_signals)
        
        return MLSystemStatus(
            lstm_enabled=lstm_enabled,
            ensemble_enabled=ensemble_enabled,
            kelly_enabled=kelly_enabled,
            total_predictions=total_predictions,
            avg_confidence=avg_confidence,
            system_health=system_health
        )
        
    except Exception as e:
        logger.error(f"Error getting ML system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/current")
async def get_current_ml_performance():
    """Get current ML performance metrics"""
    try:
        ai_brain = get_ai_brain_service()
        
        if not ai_brain or not hasattr(ai_brain, 'ml_capabilities'):
            return {
                "error": "ML capabilities not available",
                "lstm": {"enabled": False},
                "ensemble": {"enabled": False},
                "kelly": {"enabled": False}
            }
        
        ml_caps = ai_brain.ml_capabilities
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "lstm": {"enabled": False, "predictions": 0, "confidence": 0.0},
            "ensemble": {"enabled": False, "predictions": 0, "confidence": 0.0},
            "kelly": {"enabled": False, "total_trades": 0, "win_rate": 0.0},
            "system_metrics": {
                "total_predictions": 0,
                "avg_latency": 0.0,
                "memory_usage": 0.0
            }
        }
        
        # LSTM Performance
        if 'lstm' in ml_caps:
            lstm_stats = ml_caps['lstm'].get_performance_stats()
            performance_data["lstm"] = {
                "enabled": lstm_stats.get('is_enabled', False),
                "trained": lstm_stats.get('is_trained', False),
                "predictions": lstm_stats.get('predictions_made', 0),
                "data_buffer_size": lstm_stats.get('data_buffer_size', 0),
                "confidence_threshold": lstm_stats.get('confidence_threshold', 0.6),
                "has_tensorflow": lstm_stats.get('has_tensorflow', False)
            }
        
        # Ensemble Performance
        if 'ensemble' in ml_caps:
            ensemble_stats = ml_caps['ensemble'].get_performance_stats()
            performance_data["ensemble"] = {
                "enabled": ensemble_stats.get('is_enabled', False),
                "trained": ensemble_stats.get('is_trained', False),
                "predictions": ensemble_stats.get('predictions_made', 0),
                "base_models": ensemble_stats.get('base_models', []),
                "model_weights": ensemble_stats.get('model_weights', {}),
                "feature_count": ensemble_stats.get('feature_count', 0),
                "model_performance": ensemble_stats.get('model_performance', {})
            }
        
        # Kelly Performance
        if 'kelly' in ml_caps:
            try:
                kelly_summary = ml_caps['kelly'].get_performance_summary()
                performance_data["kelly"] = {
                    "enabled": kelly_summary.get('enabled', True),
                    "system_ready": kelly_summary.get('system_ready', False),
                    "total_predictions": kelly_summary.get('total_predictions', 0),
                    "win_rate": kelly_summary.get('win_rate', 0.0),
                    "total_pnl": kelly_summary.get('total_pnl', 0.0),
                    "current_drawdown": kelly_summary.get('current_drawdown', 0.0),
                    "kelly_multiplier": kelly_summary.get('kelly_multiplier', 1.0),
                    "avg_position_size": kelly_summary.get('avg_position_size', 0.0)
                }
            except Exception as e:
                logger.warning(f"Error getting Kelly performance: {e}")
                performance_data["kelly"] = {"enabled": True, "error": str(e)}
        
        # Calculate system totals
        total_predictions = (
            performance_data["lstm"].get("predictions", 0) + 
            performance_data["ensemble"].get("predictions", 0)
        )
        performance_data["system_metrics"]["total_predictions"] = total_predictions
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Error getting current ML performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/history")
async def get_ml_performance_history(hours: int = Query(24, ge=1, le=168)):
    """Get ML performance history for specified hours"""
    try:
        # For now, return recent performance data
        # In production, this would query a time-series database
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter performance history by time
        filtered_history = []
        for entry in ml_performance_history:
            if 'timestamp' in entry:
                entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', ''))
                if entry_time >= cutoff_time:
                    filtered_history.append(entry)
        
        return {
            "timeframe_hours": hours,
            "data_points": len(filtered_history),
            "history": filtered_history[-100:],  # Limit to last 100 points
            "summary": {
                "avg_lstm_predictions": 0,
                "avg_ensemble_predictions": 0,
                "avg_kelly_performance": 0.0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting ML performance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/accuracy")
async def get_model_accuracy_metrics():
    """Get detailed accuracy metrics for each ML model"""
    try:
        ai_brain = get_ai_brain_service()
        
        if not ai_brain or not hasattr(ai_brain, 'ml_capabilities'):
            return {"error": "ML capabilities not available"}
        
        ml_caps = ai_brain.ml_capabilities
        accuracy_data = {
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }
        
        # LSTM Accuracy
        if 'lstm' in ml_caps:
            lstm_stats = ml_caps['lstm'].get_performance_stats()
            accuracy_data["models"]["lstm"] = {
                "enabled": lstm_stats.get('is_enabled', False),
                "trained": lstm_stats.get('is_trained', False),
                "predictions_made": lstm_stats.get('predictions_made', 0),
                "recent_accuracy": None,  # Would need actual prediction tracking
                "confidence_threshold": lstm_stats.get('confidence_threshold', 0.6)
            }
        
        # Ensemble Accuracy
        if 'ensemble' in ml_caps:
            ensemble_stats = ml_caps['ensemble'].get_performance_stats()
            model_performance = ensemble_stats.get('model_performance', {})
            
            accuracy_data["models"]["ensemble"] = {
                "enabled": ensemble_stats.get('is_enabled', False),
                "trained": ensemble_stats.get('is_trained', False),
                "predictions_made": ensemble_stats.get('predictions_made', 0),
                "base_model_performance": model_performance,
                "feature_importance": ensemble_stats.get('feature_importance', {})
            }
        
        # Kelly Accuracy (win rate)
        if 'kelly' in ml_caps:
            try:
                kelly_summary = ml_caps['kelly'].get_performance_summary()
                accuracy_data["models"]["kelly"] = {
                    "enabled": kelly_summary.get('enabled', True),
                    "win_rate": kelly_summary.get('win_rate', 0.0),
                    "total_predictions": kelly_summary.get('total_predictions', 0),
                    "sharpe_ratio": kelly_summary.get('sharpe_ratio', 0.0),
                    "current_drawdown": kelly_summary.get('current_drawdown', 0.0)
                }
            except Exception as e:
                accuracy_data["models"]["kelly"] = {"error": str(e)}
        
        return accuracy_data
        
    except Exception as e:
        logger.error(f"Error getting model accuracy metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/recent")
async def get_recent_predictions(limit: int = Query(20, ge=1, le=100)):
    """Get recent ML predictions with outcomes"""
    try:
        ai_brain = get_ai_brain_service()
        
        if not ai_brain or not hasattr(ai_brain, 'analysis_history'):
            return {"error": "Analysis history not available"}
        
        recent_predictions = []
        
        # Get recent analysis with ML predictions
        for analysis in list(ai_brain.analysis_history)[-limit:]:
            if not analysis.get('signal'):
                continue
                
            signal = analysis['signal']
            prediction_data = {
                "timestamp": analysis.get('timestamp'),
                "signal_type": signal.get('signal', {}).get('name', 'unknown'),
                "confidence": signal.get('confidence', 0.0),
                "reasoning": signal.get('reasoning', ''),
                "ml_enhanced": "ML" in signal.get('reasoning', ''),
                "kelly_position": signal.get('kelly_position_pct', 0.0),
                "kelly_win_prob": signal.get('kelly_win_probability', 0.5)
            }
            
            # Check if this was ML-enhanced
            if hasattr(analysis.get('analysis'), 'ml_predictions'):
                ml_preds = analysis['analysis']['ml_predictions']
                prediction_data.update({
                    "lstm_direction": ml_preds.get('lstm_prediction', {}).get('direction', 0),
                    "lstm_confidence": ml_preds.get('lstm_prediction', {}).get('confidence', 0),
                    "ensemble_direction": ml_preds.get('ensemble_prediction', {}).get('direction', 0),
                    "ensemble_confidence": ml_preds.get('ensemble_prediction', {}).get('confidence', 0),
                    "ml_agreement": ml_preds.get('ml_agreement', 0.0)
                })
            
            recent_predictions.append(prediction_data)
        
        return {
            "total_predictions": len(recent_predictions),
            "predictions": recent_predictions,
            "ml_enhanced_count": sum(1 for p in recent_predictions if p.get('ml_enhanced')),
            "avg_confidence": statistics.mean([p['confidence'] for p in recent_predictions]) if recent_predictions else 0.0
        }
        
    except Exception as e:
        logger.error(f"Error getting recent predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/performance/record")
async def record_ml_performance(data: dict):
    """Record ML performance data point"""
    try:
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Store in memory (in production, this would go to a database)
        ml_performance_history.append(data)
        
        return {"status": "recorded", "timestamp": data['timestamp']}
        
    except Exception as e:
        logger.error(f"Error recording ML performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_ml_health_check():
    """Comprehensive ML system health check"""
    try:
        ai_brain = get_ai_brain_service()
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {},
            "issues": [],
            "recommendations": []
        }
        
        if not ai_brain:
            health_data["overall_status"] = "error"
            health_data["issues"].append("AI Brain Service not available")
            return health_data
        
        if not hasattr(ai_brain, 'ml_capabilities'):
            health_data["overall_status"] = "disabled"
            health_data["issues"].append("ML capabilities not initialized")
            return health_data
        
        ml_caps = ai_brain.ml_capabilities
        healthy_components = 0
        total_components = 3
        
        # Check LSTM
        if 'lstm' in ml_caps:
            lstm_stats = ml_caps['lstm'].get_performance_stats()
            lstm_healthy = lstm_stats.get('is_enabled', False)
            
            health_data["components"]["lstm"] = {
                "status": "healthy" if lstm_healthy else "disabled",
                "enabled": lstm_stats.get('is_enabled', False),
                "trained": lstm_stats.get('is_trained', False),
                "predictions": lstm_stats.get('predictions_made', 0)
            }
            
            if lstm_healthy:
                healthy_components += 1
            else:
                health_data["issues"].append("LSTM predictor disabled or not available")
        
        # Check Ensemble
        if 'ensemble' in ml_caps:
            ensemble_stats = ml_caps['ensemble'].get_performance_stats()
            ensemble_healthy = ensemble_stats.get('is_enabled', False)
            
            health_data["components"]["ensemble"] = {
                "status": "healthy" if ensemble_healthy else "disabled",
                "enabled": ensemble_stats.get('is_enabled', False),
                "trained": ensemble_stats.get('is_trained', False),
                "predictions": ensemble_stats.get('predictions_made', 0),
                "base_models": len(ensemble_stats.get('base_models', []))
            }
            
            if ensemble_healthy:
                healthy_components += 1
            else:
                health_data["issues"].append("Ensemble models disabled or not available")
        
        # Check Kelly
        if 'kelly' in ml_caps:
            try:
                kelly_status = ml_caps['kelly'].get_system_status()
                kelly_healthy = kelly_status.get('config', {}).get('enabled', True)
                
                health_data["components"]["kelly"] = {
                    "status": "healthy" if kelly_healthy else "disabled",
                    "enabled": kelly_healthy,
                    "ready": kelly_status.get('kelly_enabled', False)
                }
                
                if kelly_healthy:
                    healthy_components += 1
                else:
                    health_data["issues"].append("Kelly Criterion disabled")
            except Exception as e:
                health_data["components"]["kelly"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_data["issues"].append(f"Kelly Criterion error: {e}")
        
        # Determine overall status
        if healthy_components == total_components:
            health_data["overall_status"] = "healthy"
        elif healthy_components >= 2:
            health_data["overall_status"] = "degraded"
            health_data["recommendations"].append("Some ML components need attention")
        elif healthy_components >= 1:
            health_data["overall_status"] = "limited"
            health_data["recommendations"].append("Most ML components need attention")
        else:
            health_data["overall_status"] = "critical"
            health_data["recommendations"].append("All ML components need immediate attention")
        
        health_data["healthy_components"] = healthy_components
        health_data["total_components"] = total_components
        
        return health_data
        
    except Exception as e:
        logger.error(f"Error in ML health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/alerts")
async def get_ml_monitoring_alerts():
    """Get current ML monitoring alerts"""
    try:
        ml_monitoring = get_ml_monitoring_service()
        alert_summary = ml_monitoring.get_alert_summary()
        
        return {
            "active_alerts": alert_summary.get('active_alerts', 0),
            "total_alerts_today": alert_summary.get('total_alerts_today', 0),
            "alerts_by_severity": alert_summary.get('alerts_by_severity', {}),
            "alerts_by_type": alert_summary.get('alerts_by_type', {}),
            "recent_alerts": alert_summary.get('recent_alerts', [])
        }
        
    except Exception as e:
        logger.error(f"Error getting ML monitoring alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/performance-trends/{model_type}")
async def get_model_performance_trends(model_type: str, hours: int = Query(24, ge=1, le=168)):
    """Get performance trends for specific model type"""
    try:
        ml_monitoring = get_ml_monitoring_service()
        
        if model_type not in ['lstm', 'ensemble', 'kelly']:
            raise HTTPException(status_code=400, detail="Invalid model type")
        
        trends = ml_monitoring.get_performance_trends(model_type, hours)
        
        return {
            "model_type": model_type,
            "time_window_hours": hours,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error getting performance trends for {model_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/system-health")
async def get_ml_system_health():
    """Get overall ML system health status"""
    try:
        ml_monitoring = get_ml_monitoring_service()
        alert_summary = ml_monitoring.get_alert_summary()
        
        # Determine system health status
        active_alerts = alert_summary.get('active_alerts', 0)
        critical_alerts = alert_summary.get('alerts_by_severity', {}).get('critical', 0)
        emergency_alerts = alert_summary.get('alerts_by_severity', {}).get('emergency', 0)
        
        if emergency_alerts > 0:
            health_status = "emergency"
        elif critical_alerts > 0:
            health_status = "critical"
        elif active_alerts > 5:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            "status": health_status,
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "emergency_alerts": emergency_alerts,
            "monitoring_enabled": True,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting ML system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/resolve-alert/{alert_id}")
async def resolve_monitoring_alert(alert_id: str, resolution_note: str = ""):
    """Resolve a monitoring alert"""
    try:
        ml_monitoring = get_ml_monitoring_service()
        ml_monitoring.resolve_alert(alert_id, resolution_note)
        
        return {"success": True, "message": f"Alert {alert_id} resolved"}
        
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))