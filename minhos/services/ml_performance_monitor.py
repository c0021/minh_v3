#!/usr/bin/env python3
"""
Comprehensive ML Performance Monitor
====================================

Enhanced ML monitoring system for Phase 2 Week 7-8 System Integration.
Provides end-to-end performance monitoring across the entire ML pipeline.

Features:
- LSTM + Ensemble + Kelly performance tracking
- Real-time accuracy and latency monitoring
- System health dashboards
- Automated performance alerts
- Trade execution integration monitoring
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import statistics
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of ML metrics to track"""
    ACCURACY = "accuracy"
    LATENCY = "latency" 
    CONFIDENCE = "confidence"
    PREDICTION_COUNT = "prediction_count"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    KELLY_FRACTION = "kelly_fraction"
    POSITION_SIZE = "position_size"
    TRADE_EXECUTION = "trade_execution"

@dataclass
class MLMetric:
    """ML performance metric data point"""
    timestamp: datetime
    model_type: str  # 'lstm', 'ensemble', 'kelly', 'pipeline'
    metric_type: MetricType
    value: float
    symbol: str
    metadata: Dict[str, Any] = None

@dataclass
class SystemHealthSnapshot:
    """Complete system health snapshot"""
    timestamp: datetime
    lstm_health: Dict[str, Any]
    ensemble_health: Dict[str, Any] 
    kelly_health: Dict[str, Any]
    pipeline_health: Dict[str, Any]
    overall_score: float
    alerts: List[str]

class MLPerformanceMonitor:
    """
    Comprehensive ML Performance Monitor
    
    Monitors the entire ML pipeline including:
    - LSTM predictor performance
    - Ensemble model consensus
    - Kelly Criterion accuracy  
    - End-to-end trade execution
    - System resource utilization
    """
    
    def __init__(self, db_path: str = "/home/colindo/Sync/minh_v4/data/ml_performance.db"):
        """Initialize ML Performance Monitor"""
        self.db_path = db_path
        self.running = False
        
        # Metrics storage
        self.metrics_buffer = deque(maxlen=10000)  # In-memory buffer
        self.health_snapshots = deque(maxlen=1000)
        
        # Performance baselines (rolling averages)
        self.baselines = {
            'lstm': {'accuracy': 0.60, 'latency_ms': 150, 'confidence': 0.65},
            'ensemble': {'accuracy': 0.65, 'latency_ms': 250, 'confidence': 0.70},
            'kelly': {'win_rate': 0.55, 'avg_kelly_fraction': 0.15, 'latency_ms': 50},
            'pipeline': {'end_to_end_latency_ms': 500, 'success_rate': 0.95}
        }
        
        # Alert thresholds (percentage degradation from baseline)
        self.alert_thresholds = {
            'accuracy_degradation': 0.20,  # 20% drop
            'latency_spike': 2.0,  # 2x normal latency
            'confidence_drop': 0.25,  # 25% confidence drop
            'error_rate_spike': 0.15  # 15% error rate
        }
        
        # Service connections
        self.ml_pipeline = None
        self.position_sizing = None
        self.trading_engine = None
        self.ai_brain = None
        
        # Background tasks
        self.monitor_task = None
        self.health_check_task = None
        self.cleanup_task = None
        
        # Statistics tracking
        self.prediction_stats = {
            'lstm': {'total': 0, 'correct': 0, 'avg_confidence': 0.0},
            'ensemble': {'total': 0, 'correct': 0, 'avg_confidence': 0.0},
            'kelly': {'total': 0, 'profitable': 0, 'avg_fraction': 0.0}
        }
        
        # Initialize database
        self._init_database()
        
        logger.info("ML Performance Monitor initialized")
    
    def _init_database(self):
        """Initialize performance monitoring database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ML metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    symbol TEXT,
                    metadata TEXT
                )
            """)
            
            # System health snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    lstm_health TEXT,
                    ensemble_health TEXT,
                    kelly_health TEXT,
                    pipeline_health TEXT,
                    alerts TEXT
                )
            """)
            
            # Performance alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    model_type TEXT,
                    message TEXT,
                    metric_value REAL,
                    threshold REAL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("ML Performance database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    async def start(self):
        """Start ML performance monitoring"""
        if self.running:
            return
        
        self.running = True
        
        # Initialize service connections
        await self._initialize_services()
        
        # Start background monitoring tasks
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("ML Performance Monitor started")
    
    async def stop(self):
        """Stop ML performance monitoring"""
        self.running = False
        
        # Cancel background tasks
        for task in [self.monitor_task, self.health_check_task, self.cleanup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("ML Performance Monitor stopped")
    
    async def _initialize_services(self):
        """Initialize connections to ML services"""
        try:
            from .ml_pipeline_service import MLPipelineService
            from .position_sizing_service import get_position_sizing_service
            from .trading_engine import get_trading_engine
            from .ai_brain_service import get_ai_brain_service
            
            self.ml_pipeline = MLPipelineService()
            self.position_sizing = get_position_sizing_service()
            self.trading_engine = get_trading_engine()
            self.ai_brain = get_ai_brain_service()
            
            logger.info("ML Performance Monitor connected to all services")
            
        except Exception as e:
            logger.error(f"Failed to initialize service connections: {e}")
    
    async def record_metric(self, 
                          model_type: str,
                          metric_type: MetricType,
                          value: float,
                          symbol: str = "NQU25-CME",
                          metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        try:
            metric = MLMetric(
                timestamp=datetime.now(),
                model_type=model_type,
                metric_type=metric_type,
                value=value,
                symbol=symbol,
                metadata=metadata or {}
            )
            
            # Add to buffer
            self.metrics_buffer.append(metric)
            
            # Store in database (async)
            await self._store_metric(metric)
            
            # Update running statistics
            self._update_statistics(metric)
            
            # Check for alerts
            await self._check_alert_conditions(metric)
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    async def _store_metric(self, metric: MLMetric):
        """Store metric in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_metrics 
                (timestamp, model_type, metric_type, value, symbol, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.timestamp.isoformat(),
                metric.model_type,
                metric.metric_type.value,
                metric.value,
                metric.symbol,
                json.dumps(metric.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    def _update_statistics(self, metric: MLMetric):
        """Update running statistics for performance tracking"""
        try:
            model_type = metric.model_type
            metric_type = metric.metric_type
            
            if model_type in self.prediction_stats:
                stats = self.prediction_stats[model_type]
                
                if metric_type == MetricType.ACCURACY:
                    stats['total'] += 1
                    if metric.value > 0.5:  # Correct prediction
                        stats['correct'] += 1
                
                elif metric_type == MetricType.CONFIDENCE:
                    # Update rolling average confidence
                    current_avg = stats.get('avg_confidence', 0.0)
                    total = stats.get('total', 1)
                    stats['avg_confidence'] = (current_avg * (total - 1) + metric.value) / total
                
                elif metric_type == MetricType.KELLY_FRACTION and model_type == 'kelly':
                    # Track Kelly fraction usage
                    current_avg = stats.get('avg_fraction', 0.0)
                    total = stats.get('total', 1)
                    stats['avg_fraction'] = (current_avg * (total - 1) + metric.value) / total
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
    
    async def _check_alert_conditions(self, metric: MLMetric):
        """Check if metric triggers any alert conditions"""
        try:
            model_type = metric.model_type
            metric_type = metric.metric_type
            value = metric.value
            
            # Get baseline for this model and metric
            baseline = self.baselines.get(model_type, {}).get(metric_type.value)
            if not baseline:
                return
            
            # Check for degradation
            if metric_type == MetricType.ACCURACY:
                degradation = (baseline - value) / baseline
                if degradation > self.alert_thresholds['accuracy_degradation']:
                    await self._trigger_alert(
                        f"Accuracy degradation detected for {model_type}",
                        "warning",
                        model_type,
                        value,
                        baseline
                    )
            
            elif metric_type == MetricType.LATENCY:
                spike = value / baseline
                if spike > self.alert_thresholds['latency_spike']:
                    await self._trigger_alert(
                        f"Latency spike detected for {model_type}",
                        "warning", 
                        model_type,
                        value,
                        baseline
                    )
            
            elif metric_type == MetricType.CONFIDENCE:
                drop = (baseline - value) / baseline
                if drop > self.alert_thresholds['confidence_drop']:
                    await self._trigger_alert(
                        f"Confidence drop detected for {model_type}",
                        "info",
                        model_type,
                        value,
                        baseline
                    )
            
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")
    
    async def _trigger_alert(self, 
                           message: str,
                           severity: str,
                           model_type: str,
                           value: float,
                           threshold: float):
        """Trigger a performance alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_alerts
                (timestamp, alert_type, severity, model_type, message, metric_value, threshold)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                "performance_degradation",
                severity,
                model_type,
                message,
                value,
                threshold
            ))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"ALERT: {message} (Value: {value:.3f}, Threshold: {threshold:.3f})")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect metrics from all services
                await self._collect_service_metrics()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error
    
    async def _collect_service_metrics(self):
        """Collect performance metrics from all ML services"""
        try:
            timestamp = datetime.now()
            
            # LSTM Metrics
            if self.ml_pipeline and hasattr(self.ml_pipeline, 'lstm_predictor'):
                try:
                    # Simulate LSTM prediction to measure performance
                    start_time = time.time()
                    prediction = self.ml_pipeline.lstm_predictor.predict_single("NQU25-CME")
                    latency = (time.time() - start_time) * 1000
                    
                    await self.record_metric("lstm", MetricType.LATENCY, latency)
                    
                    if prediction and 'confidence' in prediction:
                        await self.record_metric("lstm", MetricType.CONFIDENCE, prediction['confidence'])
                    
                except Exception as e:
                    logger.debug(f"LSTM metrics collection error: {e}")
            
            # Ensemble Metrics
            if self.ml_pipeline and hasattr(self.ml_pipeline, 'ensemble_manager'):
                try:
                    start_time = time.time()
                    prediction = self.ml_pipeline.ensemble_manager.predict_single("NQU25-CME")
                    latency = (time.time() - start_time) * 1000
                    
                    await self.record_metric("ensemble", MetricType.LATENCY, latency)
                    
                    if prediction and 'consensus_confidence' in prediction:
                        await self.record_metric("ensemble", MetricType.CONFIDENCE, prediction['consensus_confidence'])
                    
                except Exception as e:
                    logger.debug(f"Ensemble metrics collection error: {e}")
            
            # Kelly Metrics
            if self.position_sizing:
                try:
                    status = self.position_sizing.get_status()
                    metrics = status.get('performance_metrics', {})
                    
                    if metrics.get('total_recommendations', 0) > 0:
                        await self.record_metric("kelly", MetricType.PREDICTION_COUNT, 
                                                metrics['total_recommendations'])
                        
                        if 'avg_kelly_fraction' in metrics:
                            await self.record_metric("kelly", MetricType.KELLY_FRACTION,
                                                    metrics['avg_kelly_fraction'])
                    
                except Exception as e:
                    logger.debug(f"Kelly metrics collection error: {e}")
            
        except Exception as e:
            logger.error(f"Service metrics collection error: {e}")
    
    async def _health_check_loop(self):
        """System health check loop"""
        while self.running:
            try:
                # Generate health snapshot
                snapshot = await self._generate_health_snapshot()
                self.health_snapshots.append(snapshot)
                
                # Store in database
                await self._store_health_snapshot(snapshot)
                
                # Sleep for health check interval
                await asyncio.sleep(300)  # 5 minute intervals
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(300)
    
    async def _generate_health_snapshot(self) -> SystemHealthSnapshot:
        """Generate comprehensive system health snapshot"""
        try:
            timestamp = datetime.now()
            
            # LSTM Health
            lstm_health = {
                'status': 'operational',
                'avg_latency_ms': self._get_recent_avg('lstm', MetricType.LATENCY),
                'avg_confidence': self._get_recent_avg('lstm', MetricType.CONFIDENCE),
                'predictions_24h': self._get_count_24h('lstm')
            }
            
            # Ensemble Health  
            ensemble_health = {
                'status': 'operational',
                'avg_latency_ms': self._get_recent_avg('ensemble', MetricType.LATENCY),
                'avg_confidence': self._get_recent_avg('ensemble', MetricType.CONFIDENCE),
                'predictions_24h': self._get_count_24h('ensemble')
            }
            
            # Kelly Health
            kelly_health = {
                'status': 'operational',
                'avg_kelly_fraction': self._get_recent_avg('kelly', MetricType.KELLY_FRACTION),
                'recommendations_24h': self._get_count_24h('kelly'),
                'service_running': self.position_sizing is not None
            }
            
            # Pipeline Health
            pipeline_health = {
                'status': 'operational',
                'lstm_connected': lstm_health['predictions_24h'] > 0,
                'ensemble_connected': ensemble_health['predictions_24h'] > 0,
                'kelly_connected': kelly_health['recommendations_24h'] > 0,
                'overall_latency_ms': (lstm_health['avg_latency_ms'] or 0) + 
                                     (ensemble_health['avg_latency_ms'] or 0)
            }
            
            # Calculate overall health score (0-100)
            overall_score = self._calculate_health_score(
                lstm_health, ensemble_health, kelly_health, pipeline_health
            )
            
            # Active alerts
            alerts = await self._get_active_alerts()
            
            return SystemHealthSnapshot(
                timestamp=timestamp,
                lstm_health=lstm_health,
                ensemble_health=ensemble_health,
                kelly_health=kelly_health,
                pipeline_health=pipeline_health,
                overall_score=overall_score,
                alerts=alerts
            )
            
        except Exception as e:
            logger.error(f"Failed to generate health snapshot: {e}")
            return SystemHealthSnapshot(
                timestamp=datetime.now(),
                lstm_health={'status': 'error'},
                ensemble_health={'status': 'error'},
                kelly_health={'status': 'error'},
                pipeline_health={'status': 'error'},
                overall_score=0.0,
                alerts=[f"Health check error: {str(e)}"]
            )
    
    def _get_recent_avg(self, model_type: str, metric_type: MetricType, minutes: int = 60) -> Optional[float]:
        """Get recent average for a metric"""
        try:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            values = [
                m.value for m in self.metrics_buffer 
                if (m.model_type == model_type and 
                    m.metric_type == metric_type and 
                    m.timestamp >= cutoff)
            ]
            return statistics.mean(values) if values else None
        except:
            return None
    
    def _get_count_24h(self, model_type: str) -> int:
        """Get prediction count in last 24 hours"""
        try:
            cutoff = datetime.now() - timedelta(hours=24)
            return len([
                m for m in self.metrics_buffer
                if (m.model_type == model_type and m.timestamp >= cutoff)
            ])
        except:
            return 0
    
    def _calculate_health_score(self, lstm_health, ensemble_health, kelly_health, pipeline_health) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            score = 100.0
            
            # Deduct points for issues
            if not pipeline_health.get('lstm_connected', False):
                score -= 25
            if not pipeline_health.get('ensemble_connected', False):
                score -= 25  
            if not pipeline_health.get('kelly_connected', False):
                score -= 25
            
            # Deduct for high latency
            total_latency = pipeline_health.get('overall_latency_ms', 0)
            if total_latency > 1000:  # > 1 second
                score -= 15
            elif total_latency > 500:  # > 0.5 seconds
                score -= 10
            
            # Deduct for low confidence
            lstm_conf = lstm_health.get('avg_confidence', 1.0) or 1.0
            ensemble_conf = ensemble_health.get('avg_confidence', 1.0) or 1.0
            if lstm_conf < 0.5 or ensemble_conf < 0.5:
                score -= 10
            
            return max(0.0, min(100.0, score))
            
        except:
            return 50.0  # Default middle score on error
    
    async def _get_active_alerts(self) -> List[str]:
        """Get list of active alert messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get unresolved alerts from last 24 hours
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute("""
                SELECT message FROM performance_alerts 
                WHERE timestamp > ? AND resolved = FALSE
                ORDER BY timestamp DESC
                LIMIT 10
            """, (cutoff,))
            
            alerts = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def _store_health_snapshot(self, snapshot: SystemHealthSnapshot):
        """Store health snapshot in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO health_snapshots
                (timestamp, overall_score, lstm_health, ensemble_health, 
                 kelly_health, pipeline_health, alerts)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.timestamp.isoformat(),
                snapshot.overall_score,
                json.dumps(snapshot.lstm_health),
                json.dumps(snapshot.ensemble_health),
                json.dumps(snapshot.kelly_health),
                json.dumps(snapshot.pipeline_health),
                json.dumps(snapshot.alerts)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store health snapshot: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup old data periodically"""
        while self.running:
            try:
                # Clean up old metrics (keep 7 days)
                cutoff = datetime.now() - timedelta(days=7)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM ml_metrics WHERE timestamp < ?", 
                             (cutoff.isoformat(),))
                cursor.execute("DELETE FROM health_snapshots WHERE timestamp < ?",
                             (cutoff.isoformat(),))
                cursor.execute("DELETE FROM performance_alerts WHERE timestamp < ?",
                             (cutoff.isoformat(),))
                
                conn.commit()
                conn.close()
                
                logger.info("Cleaned up old monitoring data")
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            latest_snapshot = self.health_snapshots[-1] if self.health_snapshots else None
            
            return {
                'monitoring_status': 'running' if self.running else 'stopped',
                'metrics_collected': len(self.metrics_buffer),
                'health_snapshots': len(self.health_snapshots),
                'prediction_statistics': self.prediction_stats,
                'latest_health_score': latest_snapshot.overall_score if latest_snapshot else 0.0,
                'active_alerts_count': len(latest_snapshot.alerts) if latest_snapshot else 0,
                'lstm_status': latest_snapshot.lstm_health if latest_snapshot else {},
                'ensemble_status': latest_snapshot.ensemble_health if latest_snapshot else {},
                'kelly_status': latest_snapshot.kelly_health if latest_snapshot else {},
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

# Singleton instance
_ml_performance_monitor = None

def get_ml_performance_monitor() -> MLPerformanceMonitor:
    """Get or create ML Performance Monitor instance"""
    global _ml_performance_monitor
    if _ml_performance_monitor is None:
        _ml_performance_monitor = MLPerformanceMonitor()
    return _ml_performance_monitor

async def create_ml_performance_monitor() -> MLPerformanceMonitor:
    """Create and start ML Performance Monitor"""
    monitor = get_ml_performance_monitor()
    await monitor.start()
    return monitor