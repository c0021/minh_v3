"""
ML Retrain Scheduler Service

Automated retraining scheduler and management for ML models.
Provides intelligent retraining triggers, job scheduling, and model lifecycle management.
"""

import asyncio
import logging
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import os
import shutil
from pathlib import Path


class RetrainTrigger(Enum):
    """Types of retraining triggers"""
    ACCURACY_DEGRADATION = "accuracy_degradation"
    CONFIDENCE_DECLINE = "confidence_decline"
    DATA_DRIFT = "data_drift"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    PERFORMANCE_ANOMALY = "performance_anomaly"


class RetrainStatus(Enum):
    """Retraining job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RetrainJob:
    """Retraining job definition"""
    id: str
    model_type: str  # 'lstm', 'ensemble', 'kelly', 'all'
    trigger: RetrainTrigger
    trigger_reason: str
    trigger_metrics: Dict[str, Any]
    scheduled_time: datetime
    status: RetrainStatus
    created_time: datetime
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    error_message: Optional[str] = None
    backup_path: Optional[str] = None
    new_model_path: Optional[str] = None
    validation_metrics: Optional[Dict[str, Any]] = None


@dataclass
class RetrainConfig:
    """Retraining configuration"""
    model_type: str
    trigger_thresholds: Dict[str, float]
    schedule_interval_hours: int
    min_data_points: int
    validation_threshold: float
    backup_retention_days: int
    max_concurrent_jobs: int


class MLRetrainScheduler:
    """
    ML Retraining Scheduler Service
    
    Provides automated model retraining with:
    - Intelligent trigger detection
    - Scheduled retraining jobs
    - Model backup and rollback
    - Validation and deployment
    - Performance monitoring
    """
    
    def __init__(self):
        self.db_path = "/home/colindo/Sync/minh_v4/data/ml_retrain_scheduler.db"
        self.models_path = Path("/home/colindo/Sync/minh_v4/ml_models")
        self.backup_path = Path("/home/colindo/Sync/minh_v4/ml_models_backup")
        
        # Scheduler state
        self.is_running = False
        self.active_jobs = {}  # job_id -> RetrainJob
        self.job_queue = []
        self.max_concurrent_jobs = 2
        
        # Default configurations
        self.retrain_configs = {
            "lstm": RetrainConfig(
                model_type="lstm",
                trigger_thresholds={
                    "accuracy_threshold": 0.6,
                    "confidence_threshold": 0.65,
                    "data_drift_threshold": 0.8
                },
                schedule_interval_hours=168,  # Weekly
                min_data_points=1000,
                validation_threshold=0.7,
                backup_retention_days=30,
                max_concurrent_jobs=1
            ),
            "ensemble": RetrainConfig(
                model_type="ensemble",
                trigger_thresholds={
                    "accuracy_threshold": 0.65,
                    "confidence_threshold": 0.7,
                    "agreement_threshold": 0.5
                },
                schedule_interval_hours=72,  # Every 3 days
                min_data_points=500,
                validation_threshold=0.75,
                backup_retention_days=30,
                max_concurrent_jobs=1
            ),
            "kelly": RetrainConfig(
                model_type="kelly",
                trigger_thresholds={
                    "accuracy_threshold": 0.7,
                    "calibration_threshold": 0.1
                },
                schedule_interval_hours=336,  # Every 2 weeks
                min_data_points=200,
                validation_threshold=0.8,
                backup_retention_days=30,
                max_concurrent_jobs=1
            )
        }
        
        # Trigger callbacks
        self.trigger_callbacks = {}
        
        # Create directories
        self.backup_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logging.info("🔄 ML Retrain Scheduler initialized")
    
    def _init_database(self):
        """Initialize retraining scheduler database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Retrain jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS retrain_jobs (
                    id TEXT PRIMARY KEY,
                    model_type TEXT,
                    trigger_type TEXT,
                    trigger_reason TEXT,
                    trigger_metrics TEXT,
                    scheduled_time DATETIME,
                    status TEXT,
                    created_time DATETIME,
                    started_time DATETIME,
                    completed_time DATETIME,
                    error_message TEXT,
                    backup_path TEXT,
                    new_model_path TEXT,
                    validation_metrics TEXT
                )
            """)
            
            # Retrain history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS retrain_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    model_type TEXT,
                    trigger_type TEXT,
                    previous_accuracy REAL,
                    new_accuracy REAL,
                    improvement REAL,
                    deployment_decision TEXT,
                    deployment_reason TEXT
                )
            """)
            
            # Trigger logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trigger_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    trigger_type TEXT,
                    model_type TEXT,
                    trigger_metrics TEXT,
                    threshold_breached TEXT,
                    action_taken TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to initialize retrain scheduler database: {e}")
    
    async def start_scheduler(self):
        """Start the retraining scheduler"""
        if self.is_running:
            logging.warning("Retrain scheduler already running")
            return
        
        self.is_running = True
        logging.info("🔄 Starting ML retrain scheduler")
        
        # Start scheduler loop
        asyncio.create_task(self._scheduler_loop())
        
        # Load pending jobs
        await self._load_pending_jobs()
    
    async def stop_scheduler(self):
        """Stop the retraining scheduler"""
        self.is_running = False
        logging.info("🔄 ML retrain scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Process job queue
                await self._process_job_queue()
                
                # Check for scheduled retraining
                await self._check_scheduled_retraining()
                
                # Clean up old jobs and backups
                await self._cleanup_old_data()
                
                # Sleep for a minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(60)
    
    async def register_trigger_callback(self, trigger_type: RetrainTrigger, callback: Callable):
        """Register callback for trigger evaluation"""
        self.trigger_callbacks[trigger_type] = callback
        logging.info(f"🔄 Registered trigger callback for {trigger_type.value}")
    
    async def check_retrain_triggers(self, model_type: str, current_metrics: Dict[str, Any]) -> bool:
        """Check if retraining should be triggered"""
        try:
            if model_type not in self.retrain_configs:
                return False
            
            config = self.retrain_configs[model_type]
            thresholds = config.trigger_thresholds
            triggers_fired = []
            
            # Check accuracy degradation
            accuracy = current_metrics.get("accuracy_24h", 1.0)
            if accuracy < thresholds.get("accuracy_threshold", 0.6):
                triggers_fired.append({
                    "trigger": RetrainTrigger.ACCURACY_DEGRADATION,
                    "reason": f"Accuracy {accuracy:.2%} below threshold {thresholds['accuracy_threshold']:.2%}",
                    "metrics": {"accuracy": accuracy, "threshold": thresholds["accuracy_threshold"]}
                })
            
            # Check confidence decline
            confidence = current_metrics.get("avg_confidence", 1.0)
            if confidence < thresholds.get("confidence_threshold", 0.65):
                triggers_fired.append({
                    "trigger": RetrainTrigger.CONFIDENCE_DECLINE,
                    "reason": f"Confidence {confidence:.2f} below threshold {thresholds['confidence_threshold']:.2f}",
                    "metrics": {"confidence": confidence, "threshold": thresholds["confidence_threshold"]}
                })
            
            # Check agreement (for ensemble)
            if model_type == "ensemble":
                agreement = current_metrics.get("models_agreement_rate", 1.0)
                if agreement < thresholds.get("agreement_threshold", 0.5):
                    triggers_fired.append({
                        "trigger": RetrainTrigger.PERFORMANCE_ANOMALY,
                        "reason": f"Model agreement {agreement:.2%} below threshold {thresholds['agreement_threshold']:.2%}",
                        "metrics": {"agreement": agreement, "threshold": thresholds["agreement_threshold"]}
                    })
            
            # Schedule retraining if triggers fired
            if triggers_fired:
                for trigger_info in triggers_fired:
                    await self._log_trigger(trigger_info, model_type)
                    await self.schedule_retrain_job(
                        model_type=model_type,
                        trigger=trigger_info["trigger"],
                        trigger_reason=trigger_info["reason"],
                        trigger_metrics=trigger_info["metrics"]
                    )
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to check retrain triggers: {e}")
            return False
    
    async def schedule_retrain_job(
        self,
        model_type: str,
        trigger: RetrainTrigger = RetrainTrigger.MANUAL,
        trigger_reason: str = "Manual trigger",
        trigger_metrics: Dict[str, Any] = None,
        scheduled_time: datetime = None
    ) -> str:
        """Schedule a retraining job"""
        try:
            job_id = f"retrain_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if there's already a pending/running job for this model
            existing_jobs = [
                job for job in self.active_jobs.values()
                if job.model_type == model_type and job.status in [RetrainStatus.PENDING, RetrainStatus.RUNNING]
            ]
            
            if existing_jobs:
                logging.warning(f"Retrain job already exists for {model_type}: {existing_jobs[0].id}")
                return existing_jobs[0].id
            
            job = RetrainJob(
                id=job_id,
                model_type=model_type,
                trigger=trigger,
                trigger_reason=trigger_reason,
                trigger_metrics=trigger_metrics or {},
                scheduled_time=scheduled_time or datetime.now(),
                status=RetrainStatus.PENDING,
                created_time=datetime.now()
            )
            
            # Add to queue and database
            self.job_queue.append(job)
            self.active_jobs[job_id] = job
            await self._store_retrain_job(job)
            
            logging.info(f"🔄 Scheduled retrain job {job_id} for {model_type}: {trigger_reason}")
            
            return job_id
            
        except Exception as e:
            logging.error(f"Failed to schedule retrain job: {e}")
            return None
    
    async def _process_job_queue(self):
        """Process pending retraining jobs"""
        try:
            # Get jobs ready to run
            ready_jobs = [
                job for job in self.job_queue
                if job.status == RetrainStatus.PENDING and job.scheduled_time <= datetime.now()
            ]
            
            # Check concurrent job limit
            running_jobs = [job for job in self.active_jobs.values() if job.status == RetrainStatus.RUNNING]
            available_slots = self.max_concurrent_jobs - len(running_jobs)
            
            # Start jobs up to the limit
            for job in ready_jobs[:available_slots]:
                await self._start_retrain_job(job)
            
        except Exception as e:
            logging.error(f"Failed to process job queue: {e}")
    
    async def _start_retrain_job(self, job: RetrainJob):
        """Start a retraining job"""
        try:
            logging.info(f"🔄 Starting retrain job {job.id} for {job.model_type}")
            
            # Update job status
            job.status = RetrainStatus.RUNNING
            job.started_time = datetime.now()
            await self._update_retrain_job(job)
            
            # Create backup
            backup_path = await self._create_model_backup(job.model_type)
            job.backup_path = backup_path
            
            # Start retraining task
            asyncio.create_task(self._execute_retrain(job))
            
        except Exception as e:
            logging.error(f"Failed to start retrain job {job.id}: {e}")
            job.status = RetrainStatus.FAILED
            job.error_message = str(e)
            await self._update_retrain_job(job)
    
    async def _execute_retrain(self, job: RetrainJob):
        """Execute the actual retraining"""
        try:
            logging.info(f"🔄 Executing retrain for {job.model_type}")
            
            # Simulate retraining (in production, this would call actual training scripts)
            await self._simulate_model_training(job)
            
            # Validate new model
            validation_metrics = await self._validate_new_model(job)
            job.validation_metrics = validation_metrics
            
            # Decide whether to deploy
            should_deploy = await self._evaluate_deployment(job)
            
            if should_deploy:
                await self._deploy_new_model(job)
                job.status = RetrainStatus.COMPLETED
                logging.info(f"✅ Retrain job {job.id} completed successfully")
            else:
                await self._rollback_model(job)
                job.status = RetrainStatus.COMPLETED
                logging.info(f"🔄 Retrain job {job.id} completed - rollback due to poor performance")
            
            job.completed_time = datetime.now()
            await self._update_retrain_job(job)
            
            # Log to history
            await self._log_retrain_history(job)
            
        except Exception as e:
            logging.error(f"Retrain job {job.id} failed: {e}")
            job.status = RetrainStatus.FAILED
            job.error_message = str(e)
            job.completed_time = datetime.now()
            await self._update_retrain_job(job)
            
            # Attempt rollback
            try:
                await self._rollback_model(job)
            except Exception as rollback_error:
                logging.error(f"Rollback failed for job {job.id}: {rollback_error}")
        
        finally:
            # Remove from queue
            if job in self.job_queue:
                self.job_queue.remove(job)
    
    async def _simulate_model_training(self, job: RetrainJob):
        """Simulate model training (placeholder)"""
        # In production, this would:
        # 1. Prepare training data
        # 2. Train the specific model type
        # 3. Save the new model
        
        logging.info(f"🔄 Training {job.model_type} model...")
        await asyncio.sleep(2)  # Simulate training time
        
        # Create dummy new model path
        job.new_model_path = str(self.models_path / f"{job.model_type}_retrained_{job.id}")
        
        logging.info(f"🔄 Training completed for {job.model_type}")
    
    async def _validate_new_model(self, job: RetrainJob) -> Dict[str, Any]:
        """Validate the newly trained model"""
        try:
            # In production, this would run validation tests
            # For now, simulate validation metrics
            
            base_accuracy = 0.75
            improvement = 0.02  # Simulate 2% improvement
            
            validation_metrics = {
                "accuracy": base_accuracy + improvement,
                "precision": 0.78,
                "recall": 0.76,
                "f1_score": 0.77,
                "validation_loss": 0.25,
                "improvement_over_previous": improvement
            }
            
            logging.info(f"🔄 Validation completed for {job.model_type}: {validation_metrics['accuracy']:.2%} accuracy")
            
            return validation_metrics
            
        except Exception as e:
            logging.error(f"Validation failed for job {job.id}: {e}")
            return {"accuracy": 0.0, "error": str(e)}
    
    async def _evaluate_deployment(self, job: RetrainJob) -> bool:
        """Evaluate whether to deploy the new model"""
        try:
            if not job.validation_metrics:
                return False
            
            config = self.retrain_configs.get(job.model_type)
            if not config:
                return False
            
            new_accuracy = job.validation_metrics.get("accuracy", 0.0)
            threshold = config.validation_threshold
            
            # Deploy if accuracy meets threshold
            should_deploy = new_accuracy >= threshold
            
            logging.info(f"🔄 Deployment decision for {job.model_type}: {'Deploy' if should_deploy else 'Rollback'} "
                        f"(accuracy: {new_accuracy:.2%}, threshold: {threshold:.2%})")
            
            return should_deploy
            
        except Exception as e:
            logging.error(f"Deployment evaluation failed for job {job.id}: {e}")
            return False
    
    async def _deploy_new_model(self, job: RetrainJob):
        """Deploy the new model"""
        try:
            # In production, this would:
            # 1. Stop the current model
            # 2. Replace model files
            # 3. Restart the model service
            # 4. Verify deployment
            
            logging.info(f"🔄 Deploying new {job.model_type} model")
            # Simulate deployment
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Deployment failed for job {job.id}: {e}")
            raise
    
    async def _rollback_model(self, job: RetrainJob):
        """Rollback to previous model"""
        try:
            if job.backup_path:
                logging.info(f"🔄 Rolling back {job.model_type} model from backup")
                # In production, this would restore from backup
                await asyncio.sleep(0.5)
            
        except Exception as e:
            logging.error(f"Rollback failed for job {job.id}: {e}")
            raise
    
    async def _create_model_backup(self, model_type: str) -> str:
        """Create backup of current model"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_path / f"{model_type}_backup_{timestamp}"
            
            # In production, this would copy model files
            backup_path.mkdir(exist_ok=True)
            
            logging.info(f"🔄 Created backup for {model_type} at {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logging.error(f"Failed to create backup for {model_type}: {e}")
            return None
    
    async def _check_scheduled_retraining(self):
        """Check for scheduled retraining intervals"""
        try:
            current_time = datetime.now()
            
            for model_type, config in self.retrain_configs.items():
                # Check if it's time for scheduled retraining
                last_retrain = await self._get_last_retrain_time(model_type)
                
                if last_retrain:
                    time_since_retrain = current_time - last_retrain
                    if time_since_retrain.total_seconds() >= config.schedule_interval_hours * 3600:
                        await self.schedule_retrain_job(
                            model_type=model_type,
                            trigger=RetrainTrigger.SCHEDULED,
                            trigger_reason=f"Scheduled retraining (interval: {config.schedule_interval_hours}h)",
                            scheduled_time=current_time
                        )
                
        except Exception as e:
            logging.error(f"Failed to check scheduled retraining: {e}")
    
    async def _get_last_retrain_time(self, model_type: str) -> Optional[datetime]:
        """Get the last retraining time for a model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT MAX(completed_time) FROM retrain_jobs 
                WHERE model_type = ? AND status = 'completed'
            """, (model_type,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return datetime.fromisoformat(result[0])
            return None
            
        except Exception as e:
            logging.error(f"Failed to get last retrain time: {e}")
            return None
    
    async def _cleanup_old_data(self):
        """Clean up old jobs and backups"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Clean up old job records
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM retrain_jobs 
                WHERE completed_time < ? AND status IN ('completed', 'failed', 'cancelled')
            """, (cutoff_date,))
            
            conn.commit()
            conn.close()
            
            # Clean up old backup directories
            for backup_dir in self.backup_path.iterdir():
                if backup_dir.is_dir():
                    try:
                        # Extract date from directory name
                        parts = backup_dir.name.split('_')
                        if len(parts) >= 3:
                            date_str = f"{parts[-2]}_{parts[-1]}"
                            backup_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                            
                            if backup_date < cutoff_date:
                                shutil.rmtree(backup_dir)
                                logging.info(f"🔄 Cleaned up old backup: {backup_dir}")
                    except Exception as e:
                        logging.warning(f"Failed to clean up backup {backup_dir}: {e}")
            
        except Exception as e:
            logging.error(f"Failed to cleanup old data: {e}")
    
    async def _store_retrain_job(self, job: RetrainJob):
        """Store retraining job in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO retrain_jobs 
                (id, model_type, trigger_type, trigger_reason, trigger_metrics,
                 scheduled_time, status, created_time, started_time, completed_time,
                 error_message, backup_path, new_model_path, validation_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.model_type,
                job.trigger.value,
                job.trigger_reason,
                json.dumps(job.trigger_metrics),
                job.scheduled_time,
                job.status.value,
                job.created_time,
                job.started_time,
                job.completed_time,
                job.error_message,
                job.backup_path,
                job.new_model_path,
                json.dumps(job.validation_metrics) if job.validation_metrics else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to store retrain job: {e}")
    
    async def _update_retrain_job(self, job: RetrainJob):
        """Update retraining job in database"""
        await self._store_retrain_job(job)  # Same as store, using REPLACE
    
    async def _log_trigger(self, trigger_info: Dict[str, Any], model_type: str):
        """Log trigger event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trigger_logs 
                (timestamp, trigger_type, model_type, trigger_metrics, 
                 threshold_breached, action_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                trigger_info["trigger"].value,
                model_type,
                json.dumps(trigger_info["metrics"]),
                json.dumps(trigger_info.get("threshold")),
                "retrain_scheduled"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to log trigger: {e}")
    
    async def _log_retrain_history(self, job: RetrainJob):
        """Log retraining history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            previous_accuracy = job.trigger_metrics.get("accuracy", 0.0)
            new_accuracy = job.validation_metrics.get("accuracy", 0.0) if job.validation_metrics else 0.0
            improvement = new_accuracy - previous_accuracy
            
            deployment_decision = "deployed" if job.status == RetrainStatus.COMPLETED and new_accuracy > previous_accuracy else "rollback"
            deployment_reason = job.trigger_reason
            
            cursor.execute("""
                INSERT INTO retrain_history 
                (timestamp, model_type, trigger_type, previous_accuracy, 
                 new_accuracy, improvement, deployment_decision, deployment_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                job.model_type,
                job.trigger.value,
                previous_accuracy,
                new_accuracy,
                improvement,
                deployment_decision,
                deployment_reason
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Failed to log retrain history: {e}")
    
    async def _load_pending_jobs(self):
        """Load pending jobs from database on startup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM retrain_jobs 
                WHERE status IN ('pending', 'running')
                ORDER BY scheduled_time
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                # Reconstruct job object
                job = RetrainJob(
                    id=row[0],
                    model_type=row[1],
                    trigger=RetrainTrigger(row[2]),
                    trigger_reason=row[3],
                    trigger_metrics=json.loads(row[4]) if row[4] else {},
                    scheduled_time=datetime.fromisoformat(row[5]),
                    status=RetrainStatus(row[6]),
                    created_time=datetime.fromisoformat(row[7]),
                    started_time=datetime.fromisoformat(row[8]) if row[8] else None,
                    completed_time=datetime.fromisoformat(row[9]) if row[9] else None,
                    error_message=row[10],
                    backup_path=row[11],
                    new_model_path=row[12],
                    validation_metrics=json.loads(row[13]) if row[13] else None
                )
                
                self.active_jobs[job.id] = job
                if job.status == RetrainStatus.PENDING:
                    self.job_queue.append(job)
            
            logging.info(f"🔄 Loaded {len(self.active_jobs)} pending retrain jobs")
            
        except Exception as e:
            logging.error(f"Failed to load pending jobs: {e}")
    
    async def get_retrain_status(self) -> Dict[str, Any]:
        """Get current retraining status"""
        try:
            return {
                "is_running": self.is_running,
                "active_jobs": len(self.active_jobs),
                "queued_jobs": len(self.job_queue),
                "running_jobs": len([j for j in self.active_jobs.values() if j.status == RetrainStatus.RUNNING]),
                "recent_jobs": [
                    {
                        "id": job.id,
                        "model_type": job.model_type,
                        "status": job.status.value,
                        "trigger": job.trigger.value,
                        "created": job.created_time.isoformat(),
                        "completed": job.completed_time.isoformat() if job.completed_time else None
                    }
                    for job in list(self.active_jobs.values())[-5:]
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to get retrain status: {e}")
            return {"error": str(e)}


# Standalone test function
async def test_retrain_scheduler():
    """Test retraining scheduler service"""
    print("Testing ML Retrain Scheduler...")
    
    scheduler = MLRetrainScheduler()
    await scheduler.start_scheduler()
    
    # Test trigger checking
    test_metrics = {
        "accuracy_24h": 0.55,  # Below threshold
        "avg_confidence": 0.6,
        "models_agreement_rate": 0.8
    }
    
    triggered = await scheduler.check_retrain_triggers("lstm", test_metrics)
    print(f"✅ Trigger check: {'Triggered' if triggered else 'No trigger'}")
    
    # Test manual job scheduling
    job_id = await scheduler.schedule_retrain_job(
        model_type="ensemble",
        trigger=RetrainTrigger.MANUAL,
        trigger_reason="Test manual trigger"
    )
    print(f"✅ Manual job scheduled: {job_id}")
    
    # Wait for job processing
    await asyncio.sleep(3)
    
    # Get status
    status = await scheduler.get_retrain_status()
    print(f"✅ Scheduler status: {status['active_jobs']} active jobs")
    
    await scheduler.stop_scheduler()
    print("✅ ML Retrain Scheduler test completed")


if __name__ == "__main__":
    asyncio.run(test_retrain_scheduler())