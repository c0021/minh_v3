"""
ML Health Monitor Service

Automated monitoring and alerting for ML model health, performance degradation,
and system anomalies. Provides real-time alerts and automatic retraining triggers.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import numpy as np
from collections import deque, defaultdict
import statistics

# Import ML Pipeline Service
from .ml_pipeline_service import MLPipelineService


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of ML health alerts"""
    MODEL_DEGRADATION = "model_degradation"
    CONFIDENCE_DECLINE = "confidence_decline"
    AGREEMENT_DECLINE = "agreement_decline"
    PREDICTION_FAILURE = "prediction_failure"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    PERFORMANCE_ANOMALY = "performance_anomaly"
    SYSTEM_ERROR = "system_error"


@dataclass
class HealthAlert:
    """ML health alert"""
    timestamp: datetime
    alert_type: AlertType
    severity: AlertSeverity
    component: str
    message: str
    metrics: Dict[str, Any]
    threshold_breached: Optional[str] = None
    recommended_action: Optional[str] = None
    resolved: bool = False


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: datetime
    accuracy_7d: float
    accuracy_24h: float
    avg_confidence: float
    models_agreement_rate: float
    prediction_count: int
    error_rate: float
    latency_ms: float


class MLHealthMonitor:
    """
    ML Health Monitoring Service
    
    Provides automated monitoring of ML model health with:
    - Performance degradation detection
    - Real-time alerting system
    - Automated retraining triggers
    - Health score calculation
    - Anomaly detection
    """
    
    def __init__(self, ml_pipeline_service: MLPipelineService = None):
        self.ml_pipeline = ml_pipeline_service or MLPipelineService()
        self.db_path = "/home/colindo/Sync/minh_v4/data/ml_health_monitor.db"
        
        # Monitoring parameters
        self.monitoring_config = {
            "check_interval_seconds": 60,  # Check health every minute
            "accuracy_threshold_warning": 0.65,  # Warning below 65%
            "accuracy_threshold_critical": 0.55,  # Critical below 55%
            "confidence_threshold_warning": 0.6,  # Warning below 60%
            "agreement_threshold_warning": 0.5,  # Warning below 50%
            "error_rate_threshold": 0.1,  # Warning above 10% errors
            "performance_window_hours": 24,  # Performance analysis window
            "alert_cooldown_minutes": 30,  # Minimum time between same alerts
            "auto_retrain_threshold": 0.5,  # Trigger retraining below 50% accuracy
        }
        
        # State tracking
        self.is_monitoring = False
        self.alert_history = deque(maxlen=1000)
        self.active_alerts = {}
        self.performance_history = deque(maxlen=168)  # 7 days of hourly metrics
        self.last_alert_times = defaultdict(datetime)
        
        # Performance tracking
        self.accuracy_tracker = deque(maxlen=100)
        self.confidence_tracker = deque(maxlen=100)
        self.agreement_tracker = deque(maxlen=100)
        self.latency_tracker = deque(maxlen=50)
        self.error_count = 0
        self.total_predictions = 0
        
        # Initialize database
        self._init_database()
        
        logging.info("🩺 ML Health Monitor initialized")
    
    def _init_database(self):
        """Initialize health monitoring database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Health alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    alert_type TEXT,
                    severity TEXT,
                    component TEXT,
                    message TEXT,
                    metrics TEXT,
                    threshold_breached TEXT,
                    recommended_action TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    accuracy_7d REAL,
                    accuracy_24h REAL,
                    avg_confidence REAL,
                    models_agreement_rate REAL,
                    prediction_count INTEGER,
                    error_rate REAL,
                    latency_ms REAL
                )
            """)
            
            # Health scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    overall_score REAL,
                    lstm_score REAL,
                    ensemble_score REAL,
                    kelly_score REAL,
                    system_score REAL
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to initialize health monitor database: {e}")
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.is_monitoring:
            logging.warning("Health monitoring already running")
            return
        
        self.is_monitoring = True
        logging.info("🩺 Starting ML health monitoring")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        logging.info("🩺 ML health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect current metrics
                metrics = await self._collect_performance_metrics()
                
                # Analyze health
                alerts = await self._analyze_health(metrics)
                
                # Process alerts
                for alert in alerts:
                    await self._process_alert(alert)
                
                # Store metrics
                await self._store_performance_metrics(metrics)
                
                # Calculate and store health score
                health_score = await self._calculate_health_score(metrics)
                await self._store_health_score(health_score)
                
                # Check for auto-retraining triggers
                await self._check_retrain_triggers(metrics)
                
                # Sleep until next check
                await asyncio.sleep(self.monitoring_config["check_interval_seconds"])
                
            except Exception as e:
                logging.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        try:
            # Get ML pipeline health metrics
            ml_health = await self.ml_pipeline.get_health_metrics()
            
            # Calculate additional metrics
            current_time = datetime.now()
            
            # Calculate error rate
            error_rate = (self.error_count / max(1, self.total_predictions)) if self.total_predictions > 0 else 0.0
            
            # Calculate average latency
            avg_latency = statistics.mean(self.latency_tracker) if self.latency_tracker else 0.0
            
            # Calculate 7-day accuracy (simplified - would need historical data)
            accuracy_7d = ml_health.accuracy_24h  # Placeholder
            
            metrics = PerformanceMetrics(
                timestamp=current_time,
                accuracy_7d=accuracy_7d,
                accuracy_24h=ml_health.accuracy_24h,
                avg_confidence=ml_health.avg_confidence,
                models_agreement_rate=ml_health.models_agreement_rate,
                prediction_count=ml_health.total_predictions,
                error_rate=error_rate,
                latency_ms=avg_latency
            )
            
            # Update tracking
            self.performance_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to collect performance metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                accuracy_7d=0.0,
                accuracy_24h=0.0,
                avg_confidence=0.0,
                models_agreement_rate=0.0,
                prediction_count=0,
                error_rate=1.0,  # High error rate for failure case
                latency_ms=0.0
            )
    
    async def _analyze_health(self, metrics: PerformanceMetrics) -> List[HealthAlert]:
        """Analyze metrics and generate health alerts"""
        alerts = []
        
        try:
            # Check accuracy degradation
            if metrics.accuracy_24h < self.monitoring_config["accuracy_threshold_critical"]:
                alerts.append(HealthAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.MODEL_DEGRADATION,
                    severity=AlertSeverity.CRITICAL,
                    component="prediction_accuracy",
                    message=f"Critical accuracy degradation: {metrics.accuracy_24h:.1%}",
                    metrics={"accuracy_24h": metrics.accuracy_24h},
                    threshold_breached="accuracy_critical",
                    recommended_action="Immediate model retraining required"
                ))
            elif metrics.accuracy_24h < self.monitoring_config["accuracy_threshold_warning"]:
                alerts.append(HealthAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.MODEL_DEGRADATION,
                    severity=AlertSeverity.WARNING,
                    component="prediction_accuracy",
                    message=f"Accuracy below warning threshold: {metrics.accuracy_24h:.1%}",
                    metrics={"accuracy_24h": metrics.accuracy_24h},
                    threshold_breached="accuracy_warning",
                    recommended_action="Monitor closely, consider retraining"
                ))
            
            # Check confidence decline
            if metrics.avg_confidence < self.monitoring_config["confidence_threshold_warning"]:
                alerts.append(HealthAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.CONFIDENCE_DECLINE,
                    severity=AlertSeverity.WARNING,
                    component="prediction_confidence",
                    message=f"Low average confidence: {metrics.avg_confidence:.2f}",
                    metrics={"avg_confidence": metrics.avg_confidence},
                    threshold_breached="confidence_warning",
                    recommended_action="Review model training data quality"
                ))
            
            # Check model agreement
            if metrics.models_agreement_rate < self.monitoring_config["agreement_threshold_warning"]:
                alerts.append(HealthAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.AGREEMENT_DECLINE,
                    severity=AlertSeverity.WARNING,
                    component="model_agreement",
                    message=f"Low model agreement: {metrics.models_agreement_rate:.1%}",
                    metrics={"agreement_rate": metrics.models_agreement_rate},
                    threshold_breached="agreement_warning",
                    recommended_action="Check individual model performance"
                ))
            
            # Check error rate
            if metrics.error_rate > self.monitoring_config["error_rate_threshold"]:
                alerts.append(HealthAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.SYSTEM_ERROR,
                    severity=AlertSeverity.ERROR,
                    component="system_errors",
                    message=f"High error rate: {metrics.error_rate:.1%}",
                    metrics={"error_rate": metrics.error_rate},
                    threshold_breached="error_rate",
                    recommended_action="Investigate system errors and data quality"
                ))
            
            # Check for performance anomalies
            if len(self.performance_history) > 5:
                recent_accuracy = [m.accuracy_24h for m in list(self.performance_history)[-5:]]
                if len(recent_accuracy) > 1:
                    accuracy_trend = statistics.mean(recent_accuracy[-3:]) - statistics.mean(recent_accuracy[:2])
                    if accuracy_trend < -0.1:  # 10% decline
                        alerts.append(HealthAlert(
                            timestamp=datetime.now(),
                            alert_type=AlertType.PERFORMANCE_ANOMALY,
                            severity=AlertSeverity.WARNING,
                            component="performance_trend",
                            message=f"Declining accuracy trend: {accuracy_trend:.1%}",
                            metrics={"accuracy_trend": accuracy_trend},
                            threshold_breached="trend_decline",
                            recommended_action="Investigate data drift or model degradation"
                        ))
            
            return alerts
            
        except Exception as e:
            logging.error(f"Health analysis failed: {e}")
            return []
    
    async def _process_alert(self, alert: HealthAlert):
        """Process and store health alert"""
        try:
            # Check cooldown period
            alert_key = f"{alert.alert_type.value}_{alert.component}"
            last_alert_time = self.last_alert_times.get(alert_key)
            cooldown_minutes = self.monitoring_config["alert_cooldown_minutes"]
            
            if last_alert_time and (datetime.now() - last_alert_time).total_seconds() < cooldown_minutes * 60:
                return  # Skip duplicate alert within cooldown period
            
            # Store alert
            await self._store_alert(alert)
            
            # Update tracking
            self.alert_history.append(alert)
            self.active_alerts[alert_key] = alert
            self.last_alert_times[alert_key] = datetime.now()
            
            # Log alert
            severity_emoji = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🚨"
            }
            
            logging.warning(f"{severity_emoji[alert.severity]} ML Health Alert: {alert.message}")
            
            # Send critical alerts to external systems (placeholder)
            if alert.severity == AlertSeverity.CRITICAL:
                await self._send_critical_alert(alert)
            
        except Exception as e:
            logging.error(f"Failed to process alert: {e}")
    
    async def _send_critical_alert(self, alert: HealthAlert):
        """Send critical alert to external monitoring systems"""
        try:
            # This would integrate with external alerting systems
            # For now, just log the critical alert
            logging.critical(f"🚨 CRITICAL ML ALERT: {alert.message} - Action: {alert.recommended_action}")
            
            # In production, this could send:
            # - Email notifications
            # - Slack/Discord messages
            # - PagerDuty alerts
            # - SMS notifications
            
        except Exception as e:
            logging.error(f"Failed to send critical alert: {e}")
    
    async def _check_retrain_triggers(self, metrics: PerformanceMetrics):
        """Check if automatic retraining should be triggered"""
        try:
            retrain_threshold = self.monitoring_config["auto_retrain_threshold"]
            
            if metrics.accuracy_24h < retrain_threshold:
                logging.warning(f"🔄 Auto-retrain trigger: Accuracy {metrics.accuracy_24h:.1%} below threshold {retrain_threshold:.1%}")
                
                # In production, this would trigger model retraining
                # For now, just log the trigger
                await self._trigger_model_retraining("accuracy_degradation", metrics)
            
        except Exception as e:
            logging.error(f"Failed to check retrain triggers: {e}")
    
    async def _trigger_model_retraining(self, reason: str, metrics: PerformanceMetrics):
        """Trigger model retraining (placeholder)"""
        try:
            logging.info(f"🔄 Triggering model retraining: {reason}")
            
            # Create alert for retraining trigger
            alert = HealthAlert(
                timestamp=datetime.now(),
                alert_type=AlertType.MODEL_DEGRADATION,
                severity=AlertSeverity.WARNING,
                component="auto_retrain",
                message=f"Automatic retraining triggered: {reason}",
                metrics=asdict(metrics),
                recommended_action="Model retraining in progress"
            )
            
            await self._store_alert(alert)
            
            # In production, this would:
            # - Queue retraining job
            # - Backup current models
            # - Start training pipeline
            # - Monitor training progress
            # - Validate new models
            # - Deploy if successful
            
        except Exception as e:
            logging.error(f"Failed to trigger retraining: {e}")
    
    async def _calculate_health_score(self, metrics: PerformanceMetrics) -> Dict[str, float]:
        """Calculate overall health score"""
        try:
            # Component scores (0-100)
            accuracy_score = min(100, metrics.accuracy_24h * 125)  # 80% accuracy = 100 score
            confidence_score = min(100, metrics.avg_confidence * 125)
            agreement_score = min(100, metrics.models_agreement_rate * 125)
            error_score = max(0, 100 - (metrics.error_rate * 1000))  # 0% error = 100 score
            
            # Overall score
            overall_score = (accuracy_score + confidence_score + agreement_score + error_score) / 4
            
            return {
                "overall": overall_score,
                "accuracy": accuracy_score,
                "confidence": confidence_score,
                "agreement": agreement_score,
                "errors": error_score,
                "lstm": 85.0,  # Placeholder individual model scores
                "ensemble": 90.0,
                "kelly": 95.0
            }
            
        except Exception as e:
            logging.error(f"Failed to calculate health score: {e}")
            return {"overall": 0.0, "accuracy": 0.0, "confidence": 0.0, "agreement": 0.0, "errors": 0.0}
    
    async def _store_alert(self, alert: HealthAlert):
        """Store alert in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO health_alerts 
                (timestamp, alert_type, severity, component, message, 
                 metrics, threshold_breached, recommended_action, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.timestamp,
                alert.alert_type.value,
                alert.severity.value,
                alert.component,
                alert.message,
                json.dumps(alert.metrics),
                alert.threshold_breached,
                alert.recommended_action,
                alert.resolved
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store alert: {e}")
    
    async def _store_performance_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics 
                (timestamp, accuracy_7d, accuracy_24h, avg_confidence, 
                 models_agreement_rate, prediction_count, error_rate, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp,
                metrics.accuracy_7d,
                metrics.accuracy_24h,
                metrics.avg_confidence,
                metrics.models_agreement_rate,
                metrics.prediction_count,
                metrics.error_rate,
                metrics.latency_ms
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store performance metrics: {e}")
    
    async def _store_health_score(self, health_scores: Dict[str, float]):
        """Store health scores in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO health_scores 
                (timestamp, overall_score, lstm_score, ensemble_score, kelly_score, system_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                health_scores.get("overall", 0),
                health_scores.get("lstm", 0),
                health_scores.get("ensemble", 0),
                health_scores.get("kelly", 0),
                health_scores.get("errors", 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store health scores: {e}")
    
    async def get_current_health_status(self) -> Dict[str, Any]:
        """Get current health status summary"""
        try:
            if not self.performance_history:
                return {"status": "no_data", "message": "No performance data available"}
            
            latest_metrics = self.performance_history[-1]
            health_scores = await self._calculate_health_score(latest_metrics)
            
            # Count active alerts by severity
            alert_counts = defaultdict(int)
            for alert in self.alert_history:
                if not alert.resolved:
                    alert_counts[alert.severity.value] += 1
            
            overall_status = "healthy"
            if health_scores["overall"] < 50:
                overall_status = "critical"
            elif health_scores["overall"] < 70:
                overall_status = "warning"
            elif health_scores["overall"] < 85:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "health_score": health_scores["overall"],
                "component_scores": health_scores,
                "active_alerts": dict(alert_counts),
                "metrics": {
                    "accuracy_24h": latest_metrics.accuracy_24h,
                    "avg_confidence": latest_metrics.avg_confidence,
                    "agreement_rate": latest_metrics.models_agreement_rate,
                    "error_rate": latest_metrics.error_rate,
                    "prediction_count": latest_metrics.prediction_count
                },
                "last_updated": latest_metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            logging.error(f"Failed to get health status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health alerts"""
        try:
            recent_alerts = list(self.alert_history)[-limit:]
            return [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "component": alert.component,
                    "message": alert.message,
                    "metrics": alert.metrics,
                    "recommended_action": alert.recommended_action,
                    "resolved": alert.resolved
                }
                for alert in recent_alerts
            ]
        except Exception as e:
            logging.error(f"Failed to get recent alerts: {e}")
            return []
    
    def record_prediction_result(self, prediction_successful: bool, confidence: float, 
                               agreement: Optional[float] = None, latency_ms: float = 0):
        """Record prediction result for tracking"""
        try:
            self.total_predictions += 1
            
            if not prediction_successful:
                self.error_count += 1
            
            if confidence:
                self.confidence_tracker.append(confidence)
            
            if agreement is not None:
                self.agreement_tracker.append(agreement)
            
            if latency_ms > 0:
                self.latency_tracker.append(latency_ms)
                
        except Exception as e:
            logging.error(f"Failed to record prediction result: {e}")


# Standalone test function
async def test_health_monitor():
    """Test ML health monitoring service"""
    print("Testing ML Health Monitor...")
    
    monitor = MLHealthMonitor()
    
    # Start monitoring for a short period
    await monitor.start_monitoring()
    await asyncio.sleep(5)  # Monitor for 5 seconds
    
    # Record some test prediction results
    monitor.record_prediction_result(True, 0.8, 0.9, 150.0)
    monitor.record_prediction_result(True, 0.7, 0.8, 200.0)
    monitor.record_prediction_result(False, 0.5, 0.3, 500.0)  # Failed prediction
    
    # Get health status
    status = await monitor.get_current_health_status()
    print(f"✅ Health Status: {status['status']} (Score: {status['health_score']:.1f})")
    
    # Get recent alerts
    alerts = await monitor.get_recent_alerts()
    print(f"✅ Recent Alerts: {len(alerts)} alerts")
    
    await monitor.stop_monitoring()
    print("✅ ML Health Monitor test completed")


if __name__ == "__main__":
    asyncio.run(test_health_monitor())