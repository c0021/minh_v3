"""
ML Pipeline Dashboard API

FastAPI endpoints for ML pipeline monitoring, performance metrics, and health status.
Provides real-time visibility into LSTM, Ensemble, and Kelly Criterion components.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json

# Import ML Pipeline Service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from minhos.services.ml_pipeline_service import MLPipelineService, MLHealthMetrics


router = APIRouter(prefix="/api/ml", tags=["ml-pipeline"])

# Global ML Pipeline Service instance
ml_pipeline_service = None


def get_ml_pipeline_service():
    """Get or create ML pipeline service instance"""
    global ml_pipeline_service
    if ml_pipeline_service is None:
        ml_pipeline_service = MLPipelineService()
    return ml_pipeline_service


@router.get("/status")
async def get_ml_status():
    """Get overall ML pipeline status"""
    try:
        service = get_ml_pipeline_service()
        health_metrics = await service.get_health_metrics()
        
        return {
            "status": "active" if service.is_enabled else "disabled",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "lstm": health_metrics.lstm_status,
                "ensemble": health_metrics.ensemble_status,
                "kelly": health_metrics.kelly_status
            },
            "metrics": {
                "total_predictions": health_metrics.total_predictions,
                "accuracy_24h": health_metrics.accuracy_24h,
                "avg_confidence": health_metrics.avg_confidence,
                "models_agreement_rate": health_metrics.models_agreement_rate
            },
            "last_prediction": service.last_prediction_time.isoformat() if service.last_prediction_time else None
        }
    except Exception as e:
        logging.error(f"Failed to get ML status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/recent")
async def get_recent_predictions(limit: int = 20):
    """Get recent ML predictions with full details"""
    try:
        service = get_ml_pipeline_service()
        predictions = await service.get_recent_predictions(limit=limit)
        
        return {
            "predictions": predictions,
            "count": len(predictions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get recent predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/summary")
async def get_performance_summary():
    """Get ML performance summary with key metrics"""
    try:
        service = get_ml_pipeline_service()
        health_metrics = await service.get_health_metrics()
        
        # Calculate performance trends
        accuracy_trend = "stable"  # Simplified - could be calculated from historical data
        confidence_trend = "stable"
        agreement_trend = "stable"
        
        return {
            "summary": {
                "overall_health": "good" if health_metrics.accuracy_24h > 0.7 else "warning",
                "total_predictions": health_metrics.total_predictions,
                "accuracy_24h": health_metrics.accuracy_24h,
                "avg_confidence": health_metrics.avg_confidence,
                "models_agreement_rate": health_metrics.models_agreement_rate
            },
            "trends": {
                "accuracy": accuracy_trend,
                "confidence": confidence_trend,
                "agreement": agreement_trend
            },
            "components_status": {
                "lstm": {
                    "status": health_metrics.lstm_status,
                    "enabled": health_metrics.lstm_status == "enabled",
                    "last_prediction": service.last_prediction_time.isoformat() if service.last_prediction_time else None
                },
                "ensemble": {
                    "status": health_metrics.ensemble_status,
                    "enabled": health_metrics.ensemble_status == "enabled",
                    "models_count": 4  # XGBoost, LightGBM, Random Forest, CatBoost
                },
                "kelly": {
                    "status": health_metrics.kelly_status,
                    "enabled": health_metrics.kelly_status == "enabled",
                    "optimization": "half_kelly"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/alerts")
async def get_health_alerts():
    """Get current ML system health alerts"""
    try:
        service = get_ml_pipeline_service()
        alerts = await service.check_model_health()
        
        # Categorize alerts by severity
        critical_alerts = [a for a in alerts if a.get('severity') == 'error']
        warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
        info_alerts = [a for a in alerts if a.get('severity') == 'info']
        
        return {
            "alerts": {
                "critical": critical_alerts,
                "warning": warning_alerts,
                "info": info_alerts
            },
            "total_count": len(alerts),
            "health_score": max(0, 100 - (len(critical_alerts) * 30 + len(warning_alerts) * 10 + len(info_alerts) * 5)),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get health alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/lstm/status")
async def get_lstm_status():
    """Get detailed LSTM model status"""
    try:
        service = get_ml_pipeline_service()
        lstm = service.lstm_predictor
        
        return {
            "lstm": {
                "enabled": lstm.is_enabled,
                "trained": lstm.is_trained,
                "model_path": lstm.model_path,
                "sequence_length": lstm.sequence_length,
                "features": lstm.features,
                "data_buffer_size": len(lstm.data_buffer),
                "tensorflow_available": lstm.is_enabled,
                "last_training": None  # Could be added from model metadata
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get LSTM status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/ensemble/status")
async def get_ensemble_status():
    """Get detailed Ensemble models status"""
    try:
        service = get_ml_pipeline_service()
        ensemble = service.ensemble_manager
        
        return {
            "ensemble": {
                "enabled": ensemble.is_enabled,
                "trained": ensemble.is_trained,
                "model_path": ensemble.model_path,
                "models": {
                    "xgboost": {"trained": hasattr(ensemble, 'xgb_model') and ensemble.xgb_model is not None},
                    "lightgbm": {"trained": hasattr(ensemble, 'lgb_model') and ensemble.lgb_model is not None},
                    "random_forest": {"trained": hasattr(ensemble, 'rf_model') and ensemble.rf_model is not None},
                    "catboost": {"trained": hasattr(ensemble, 'cb_model') and ensemble.cb_model is not None}
                },
                "meta_learner": {"trained": hasattr(ensemble, 'meta_learner') and ensemble.meta_learner is not None},
                "libraries_available": hasattr(ensemble, 'is_enabled') and ensemble.is_enabled
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get ensemble status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/kelly/status")
async def get_kelly_status():
    """Get detailed Kelly Criterion status"""
    try:
        service = get_ml_pipeline_service()
        kelly = service.kelly_manager
        
        return {
            "kelly": {
                "enabled": kelly.is_enabled,
                "model_path": kelly.model_path,
                "max_kelly_fraction": getattr(kelly, 'max_kelly_fraction', 0.25),
                "safety_multiplier": getattr(kelly, 'safety_multiplier', 0.5),
                "min_confidence": getattr(kelly, 'min_confidence', 0.6),
                "probability_classifier": hasattr(kelly, 'probability_classifier') and kelly.probability_classifier is not None,
                "recent_calculations": getattr(kelly, 'calculation_count', 0)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get Kelly status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/statistics")
async def get_prediction_statistics():
    """Get detailed prediction statistics and analytics"""
    try:
        service = get_ml_pipeline_service()
        
        # Get recent predictions for analysis
        recent_predictions = await service.get_recent_predictions(limit=100)
        
        if not recent_predictions:
            return {
                "statistics": {
                    "total_predictions": 0,
                    "direction_distribution": {},
                    "confidence_distribution": {},
                    "agreement_rate": 0.0,
                    "avg_kelly_fraction": 0.0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate statistics
        directions = [p['direction'] for p in recent_predictions]
        confidences = [p['confidence'] for p in recent_predictions if p['confidence']]
        agreements = [p['models_agreement'] for p in recent_predictions if p['models_agreement'] is not None]
        kelly_fractions = [p['kelly_fraction'] for p in recent_predictions if p['kelly_fraction'] is not None]
        
        # Direction distribution
        direction_dist = {}
        for direction in directions:
            direction_dist[direction] = direction_dist.get(direction, 0) + 1
        
        # Confidence distribution
        confidence_ranges = {
            "0.5-0.6": 0,
            "0.6-0.7": 0, 
            "0.7-0.8": 0,
            "0.8-0.9": 0,
            "0.9-1.0": 0
        }
        
        for conf in confidences:
            if 0.5 <= conf < 0.6:
                confidence_ranges["0.5-0.6"] += 1
            elif 0.6 <= conf < 0.7:
                confidence_ranges["0.6-0.7"] += 1
            elif 0.7 <= conf < 0.8:
                confidence_ranges["0.7-0.8"] += 1
            elif 0.8 <= conf < 0.9:
                confidence_ranges["0.8-0.9"] += 1
            elif 0.9 <= conf <= 1.0:
                confidence_ranges["0.9-1.0"] += 1
        
        return {
            "statistics": {
                "total_predictions": len(recent_predictions),
                "direction_distribution": direction_dist,
                "confidence_distribution": confidence_ranges,
                "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                "agreement_rate": sum(agreements) / len(agreements) if agreements else 0.0,
                "avg_kelly_fraction": sum(kelly_fractions) / len(kelly_fractions) if kelly_fractions else 0.0,
                "high_confidence_predictions": len([c for c in confidences if c > 0.8]),
                "agreed_predictions": len([a for a in agreements if a > 0.8])
            },
            "timeframe": "Last 100 predictions",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get prediction statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/retrain")
async def trigger_model_retrain(model_type: str = "all"):
    """Trigger model retraining (placeholder for future implementation)"""
    try:
        # This would trigger model retraining in production
        # For now, return success message
        
        valid_models = ["lstm", "ensemble", "kelly", "all"]
        if model_type not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid model type. Must be one of: {valid_models}")
        
        return {
            "message": f"Model retraining triggered for: {model_type}",
            "status": "queued",
            "timestamp": datetime.now().isoformat(),
            "note": "Automatic retraining is not yet implemented"
        }
    except Exception as e:
        logging.error(f"Failed to trigger retrain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widgets")
async def get_dashboard_widgets():
    """Get ML dashboard widget data for frontend"""
    try:
        service = get_ml_pipeline_service()
        health_metrics = await service.get_health_metrics()
        alerts = await service.check_model_health()
        recent_predictions = await service.get_recent_predictions(limit=5)
        
        return {
            "widgets": {
                "status_overview": {
                    "lstm_status": health_metrics.lstm_status,
                    "ensemble_status": health_metrics.ensemble_status,
                    "kelly_status": health_metrics.kelly_status,
                    "overall_health": "good" if health_metrics.accuracy_24h > 0.7 else "warning"
                },
                "performance_metrics": {
                    "total_predictions": health_metrics.total_predictions,
                    "accuracy_24h": f"{health_metrics.accuracy_24h:.1%}",
                    "avg_confidence": f"{health_metrics.avg_confidence:.2f}",
                    "agreement_rate": f"{health_metrics.models_agreement_rate:.1%}"
                },
                "alerts_summary": {
                    "total_alerts": len(alerts),
                    "critical": len([a for a in alerts if a.get('severity') == 'error']),
                    "warning": len([a for a in alerts if a.get('severity') == 'warning']),
                    "info": len([a for a in alerts if a.get('severity') == 'info'])
                },
                "recent_activity": {
                    "last_prediction": service.last_prediction_time.isoformat() if service.last_prediction_time else None,
                    "recent_predictions_count": len(recent_predictions),
                    "latest_direction": recent_predictions[0]['direction'] if recent_predictions else None,
                    "latest_confidence": recent_predictions[0]['confidence'] if recent_predictions else None
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get dashboard widgets: {e}")
        raise HTTPException(status_code=500, detail=str(e))