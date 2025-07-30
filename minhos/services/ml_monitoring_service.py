#!/usr/bin/env python3
"""
ML Monitoring and Alerts Service

Monitors ML model performance, detects degradation, and triggers alerts
for automated model management and maintenance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from enum import Enum
import statistics
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(Enum):
    """Types of ML alerts"""
    ACCURACY_DEGRADATION = "accuracy_degradation"
    LATENCY_SPIKE = "latency_spike"
    MODEL_ERROR = "model_error"
    CACHE_PERFORMANCE = "cache_performance"
    DATA_QUALITY = "data_quality"
    SYSTEM_HEALTH = "system_health"

@dataclass
class MLAlert:
    """ML monitoring alert"""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    model_type: str
    metric_value: float
    threshold: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    model_type: str
    metric_name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

class MLMonitoringService:
    """
    ML monitoring service for performance tracking and alerting
    
    Features:
    - Real-time performance monitoring
    - Automated degradation detection
    - Configurable alerting thresholds
    - Performance trend analysis
    - Automated remediation triggers
    """
    
    def __init__(self, alert_retention_hours: int = 168):  # 7 days
        """
        Initialize ML monitoring service
        
        Args:
            alert_retention_hours: How long to keep alert history
        """
        self.alert_retention_hours = alert_retention_hours
        
        # Alert storage
        self.active_alerts: Dict[str, MLAlert] = {}
        self.alert_history = deque(maxlen=1000)
        
        # Performance data storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        
        # Monitoring configuration
        self.config = {
            'accuracy_degradation_threshold': 0.15,  # 15% accuracy drop
            'latency_spike_threshold': 2.0,  # 2x normal latency
            'error_rate_threshold': 0.10,  # 10% error rate
            'cache_hit_rate_threshold': 0.5,  # 50% cache hit rate
            'baseline_calculation_window': 100,  # Samples for baseline
            'alert_cooldown_minutes': 15,  # Minutes between same alerts
            'monitoring_enabled': True
        }
        
        # Alert handlers
        self.alert_handlers: Dict[AlertType, List[Callable]] = defaultdict(list)
        
        # Performance thresholds for each model type
        self.model_thresholds = {
            'lstm': {
                'max_latency_ms': 200,
                'min_accuracy': 0.55,
                'max_error_rate': 0.05
            },
            'ensemble': {
                'max_latency_ms': 300,
                'min_accuracy': 0.60,
                'max_error_rate': 0.05
            },
            'kelly': {
                'max_latency_ms': 100,
                'min_win_rate': 0.45,
                'max_error_rate': 0.02
            }
        }
        
        # Background monitoring
        self.monitoring_task = None
        self.running = False
        
        logger.info("ML Monitoring Service initialized")
    
    async def start(self):
        """Start background monitoring tasks"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("ML Monitoring Service started")
    
    async def stop(self):
        """Stop monitoring service"""
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("ML Monitoring Service stopped")
    
    def record_performance_metric(self, model_type: str, metric_name: str, 
                                value: float, metadata: Dict[str, Any] = None):
        """
        Record a performance metric for monitoring
        
        Args:
            model_type: Type of ML model
            metric_name: Name of the metric (accuracy, latency, etc.)
            value: Metric value
            metadata: Additional metadata
        """
        try:
            metric = PerformanceMetric(
                model_type=model_type,
                metric_name=metric_name,
                value=value,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            metric_key = f"{model_type}_{metric_name}"
            self.metrics_history[metric_key].append(metric)
            
            # Check for alerts on this metric
            asyncio.create_task(self._check_metric_alerts(metric))
            
            logger.debug(f"Recorded {metric_key}: {value}")
            
        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")
    
    async def _check_metric_alerts(self, metric: PerformanceMetric):
        """Check if a metric triggers any alerts"""
        try:
            model_type = metric.model_type
            metric_name = metric.metric_name
            value = metric.value
            
            # Get model-specific thresholds
            thresholds = self.model_thresholds.get(model_type, {})
            
            # Check latency alerts
            if metric_name == 'latency_ms':
                max_latency = thresholds.get('max_latency_ms', 1000)
                if value > max_latency:
                    await self._create_alert(
                        AlertType.LATENCY_SPIKE,
                        AlertSeverity.WARNING,
                        f"{model_type} latency spike: {value:.1f}ms > {max_latency}ms",
                        model_type,
                        value,
                        max_latency
                    )
            
            # Check accuracy alerts
            elif metric_name == 'accuracy':
                min_accuracy = thresholds.get('min_accuracy', 0.5)
                if value < min_accuracy:
                    await self._create_alert(
                        AlertType.ACCURACY_DEGRADATION,
                        AlertSeverity.CRITICAL,
                        f"{model_type} accuracy degradation: {value:.1%} < {min_accuracy:.1%}",
                        model_type,
                        value,
                        min_accuracy
                    )
            
            # Check error rate alerts
            elif metric_name == 'error_rate':
                max_error_rate = thresholds.get('max_error_rate', 0.1)
                if value > max_error_rate:
                    await self._create_alert(
                        AlertType.MODEL_ERROR,
                        AlertSeverity.CRITICAL,
                        f"{model_type} error rate too high: {value:.1%} > {max_error_rate:.1%}",
                        model_type,
                        value,
                        max_error_rate
                    )
            
            # Check for performance degradation vs baseline
            await self._check_baseline_degradation(metric)
            
        except Exception as e:
            logger.error(f"Error checking metric alerts: {e}")
    
    async def _check_baseline_degradation(self, metric: PerformanceMetric):
        """Check if metric shows degradation vs baseline"""
        try:
            metric_key = f"{metric.model_type}_{metric.metric_name}"
            history = self.metrics_history[metric_key]
            
            if len(history) < self.config['baseline_calculation_window']:
                return  # Not enough data for baseline
            
            # Calculate baseline (average of older data)
            baseline_data = list(history)[:-20]  # Exclude recent 20 samples
            if len(baseline_data) < 50:
                return  # Not enough baseline data
            
            baseline_value = statistics.mean([m.value for m in baseline_data])
            current_value = metric.value
            
            # Check for degradation based on metric type
            if metric.metric_name in ['accuracy', 'win_rate', 'cache_hit_rate']:
                # Higher is better metrics
                degradation_pct = (baseline_value - current_value) / baseline_value
                if degradation_pct > self.config['accuracy_degradation_threshold']:
                    await self._create_alert(
                        AlertType.ACCURACY_DEGRADATION,
                        AlertSeverity.WARNING,
                        f"{metric.model_type} {metric.metric_name} degraded by {degradation_pct:.1%}",
                        metric.model_type,
                        current_value,
                        baseline_value
                    )
            
            elif metric.metric_name in ['latency_ms', 'error_rate']:
                # Lower is better metrics
                spike_ratio = current_value / baseline_value
                if spike_ratio > self.config['latency_spike_threshold']:
                    await self._create_alert(
                        AlertType.LATENCY_SPIKE if 'latency' in metric.metric_name else AlertType.MODEL_ERROR,
                        AlertSeverity.WARNING,
                        f"{metric.model_type} {metric.metric_name} spiked by {spike_ratio:.1f}x",
                        metric.model_type,
                        current_value,
                        baseline_value
                    )
            
        except Exception as e:
            logger.error(f"Error checking baseline degradation: {e}")
    
    async def _create_alert(self, alert_type: AlertType, severity: AlertSeverity,
                          message: str, model_type: str, metric_value: float,
                          threshold: float, metadata: Dict[str, Any] = None):
        """Create and process a new alert"""
        try:
            # Generate alert ID
            alert_id = f"{alert_type.value}_{model_type}_{datetime.now().timestamp()}"
            
            # Check cooldown period
            if self._is_in_cooldown(alert_type, model_type):
                logger.debug(f"Alert {alert_type.value} for {model_type} in cooldown, skipping")
                return
            
            # Create alert
            alert = MLAlert(
                alert_type=alert_type,
                severity=severity,
                message=message,
                model_type=model_type,
                metric_value=metric_value,
                threshold=threshold,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Trigger alert handlers
            await self._trigger_alert_handlers(alert)
            
            logger.warning(f"🚨 ML Alert: {severity.value.upper()} - {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _is_in_cooldown(self, alert_type: AlertType, model_type: str) -> bool:
        """Check if alert type is in cooldown period"""
        cooldown_minutes = self.config['alert_cooldown_minutes']
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        # Check recent alerts of same type and model
        for alert in list(self.alert_history)[-50:]:  # Check last 50 alerts
            if (alert.alert_type == alert_type and 
                alert.model_type == model_type and
                alert.timestamp > cutoff_time):
                return True
        
        return False
    
    async def _trigger_alert_handlers(self, alert: MLAlert):
        """Trigger registered alert handlers"""
        try:
            handlers = self.alert_handlers.get(alert.alert_type, [])
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
            # Built-in alert responses
            await self._built_in_alert_response(alert)
            
        except Exception as e:
            logger.error(f"Error triggering alert handlers: {e}")
    
    async def _built_in_alert_response(self, alert: MLAlert):
        """Built-in automated responses to alerts"""
        try:
            # Cache performance issues
            if alert.alert_type == AlertType.CACHE_PERFORMANCE:
                # Clear cache if hit rate is too low
                if alert.metric_value < 0.3:  # Less than 30% hit rate
                    try:
                        from .ml_inference_cache import get_ml_inference_cache
                        cache = get_ml_inference_cache()
                        cache.clear_cache()
                        logger.info("Cleared ML inference cache due to poor performance")
                    except Exception as e:
                        logger.warning(f"Failed to clear cache: {e}")
            
            # Model error alerts
            elif alert.alert_type == AlertType.MODEL_ERROR:
                if alert.severity == AlertSeverity.CRITICAL:
                    # Disable model temporarily if error rate is very high
                    logger.warning(f"Consider disabling {alert.model_type} model due to high error rate")
            
            # Latency spike alerts
            elif alert.alert_type == AlertType.LATENCY_SPIKE:
                if alert.metric_value > 1000:  # > 1 second
                    logger.warning(f"Severe latency spike in {alert.model_type}: {alert.metric_value:.1f}ms")
            
        except Exception as e:
            logger.error(f"Error in built-in alert response: {e}")
    
    def register_alert_handler(self, alert_type: AlertType, handler: Callable):
        """Register a custom alert handler"""
        self.alert_handlers[alert_type].append(handler)
        logger.info(f"Registered alert handler for {alert_type.value}")
    
    def resolve_alert(self, alert_id: str, resolution_note: str = ""):
        """Mark an alert as resolved"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            alert.metadata['resolution_note'] = resolution_note
            
            del self.active_alerts[alert_id]
            logger.info(f"Resolved alert: {alert.message}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Cleanup old alerts
                self._cleanup_old_alerts()
                
                # Check system health
                await self._check_system_health()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _cleanup_old_alerts(self):
        """Remove old alerts from active list"""
        cutoff_time = datetime.now() - timedelta(hours=self.alert_retention_hours)
        
        expired_alerts = []
        for alert_id, alert in self.active_alerts.items():
            if alert.timestamp < cutoff_time:
                expired_alerts.append(alert_id)
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
        
        if expired_alerts:
            logger.debug(f"Cleaned up {len(expired_alerts)} old alerts")
    
    async def _check_system_health(self):
        """Check overall ML system health"""
        try:
            # Check if we have recent metrics for each model type
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(minutes=5)
            
            for model_type in ['lstm', 'ensemble', 'kelly']:
                # Check if model has recent activity
                has_recent_activity = False
                
                for metric_key, history in self.metrics_history.items():
                    if metric_key.startswith(model_type) and history:
                        latest_metric = history[-1]
                        if latest_metric.timestamp > cutoff_time:
                            has_recent_activity = True
                            break
                
                if not has_recent_activity:
                    await self._create_alert(
                        AlertType.SYSTEM_HEALTH,
                        AlertSeverity.WARNING,
                        f"{model_type} model appears inactive - no recent metrics",
                        model_type,
                        0.0,
                        1.0,
                        {'last_activity': 'unknown'}
                    )
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get current alert summary"""
        return {
            'active_alerts': len(self.active_alerts),
            'total_alerts_today': len([a for a in self.alert_history 
                                     if a.timestamp.date() == datetime.now().date()]),
            'alerts_by_severity': {
                severity.value: len([a for a in self.active_alerts.values() 
                                   if a.severity == severity])
                for severity in AlertSeverity
            },
            'alerts_by_type': {
                alert_type.value: len([a for a in self.active_alerts.values() 
                                     if a.alert_type == alert_type])
                for alert_type in AlertType
            },
            'recent_alerts': [asdict(alert) for alert in list(self.alert_history)[-10:]]
        }
    
    def get_performance_trends(self, model_type: str, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends for a model"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        trends = {}
        for metric_key, history in self.metrics_history.items():
            if metric_key.startswith(model_type):
                metric_name = metric_key.split('_', 1)[1]
                
                recent_metrics = [m for m in history if m.timestamp > cutoff_time]
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    trends[metric_name] = {
                        'current': values[-1] if values else 0,
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'count': len(values),
                        'trend': 'improving' if len(values) > 1 and values[-1] > values[0] else 'stable'
                    }
        
        return trends
    
    def set_config(self, **kwargs):
        """Update monitoring configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated monitoring config: {key} = {value}")

# Global monitoring service instance
_ml_monitoring_service = None

def get_ml_monitoring_service() -> MLMonitoringService:
    """Get global ML monitoring service instance"""
    global _ml_monitoring_service
    if _ml_monitoring_service is None:
        _ml_monitoring_service = MLMonitoringService()
    return _ml_monitoring_service