#!/usr/bin/env python3
"""
MinhOS Alert System
==================
Comprehensive monitoring and email notification system for MinhOS health and status.

Features:
- Process health monitoring
- Service status monitoring
- Critical error detection
- Bridge connectivity monitoring
- Email notifications for issues and recovery
- Configurable alert thresholds
- Alert suppression to prevent spam
"""

import asyncio
import smtplib
import json
import logging
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    # Fallback for older Python versions
    from email.MIMEText import MIMEText
    from email.MIMEMultipart import MIMEMultipart

from minhos.core.base_service import BaseService
from minhos.core.config import config

logger = logging.getLogger("alert_system")

@dataclass
class AlertConfig:
    """Alert system configuration"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    recipient_email: str = ""
    
    # Monitoring intervals (seconds)
    process_check_interval: int = 60
    service_check_interval: int = 120
    bridge_check_interval: int = 300
    
    # Alert thresholds
    max_memory_usage_mb: int = 2048
    max_cpu_usage_percent: float = 80.0
    max_consecutive_failures: int = 3
    
    # Alert suppression (minutes)
    alert_cooldown_minutes: int = 30
    recovery_notification_enabled: bool = True

@dataclass
class Alert:
    """Represents an alert event"""
    id: str
    severity: str  # "critical", "warning", "info"
    title: str
    message: str
    component: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SystemHealth:
    """System health status"""
    process_running: bool
    services_healthy: Dict[str, bool]
    bridge_connected: bool
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_usage_percent: float
    uptime_hours: float
    last_error: Optional[str]
    timestamp: datetime

class AlertSystem(BaseService):
    """MinhOS Alert System - Monitors system health and sends email notifications"""
    
    def __init__(self):
        super().__init__("AlertSystem")
        
        # Load configuration
        self.config = self._load_config()
        
        # State tracking
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.consecutive_failures: Dict[str, int] = {}
        self.last_health_status: Optional[SystemHealth] = None
        
        # Monitoring tasks
        self._process_monitor_task = None
        self._service_monitor_task = None
        self._bridge_monitor_task = None
        self._log_monitor_task = None
        
        # MinhOS process info
        self.minhos_process_name = "minh.py"
        self.minhos_pid = None
        
        logger.info("Alert System initialized")
    
    def _load_config(self) -> AlertConfig:
        """Load alert configuration from environment and config files"""
        config_data = {}
        
        # Load from environment variables
        config_data["email_user"] = config.get("alerts.email_user", "")
        config_data["email_password"] = config.get("alerts.email_password", "")
        config_data["recipient_email"] = config.get("alerts.recipient_email", "")
        config_data["smtp_server"] = config.get("alerts.smtp_server", "smtp.gmail.com")
        config_data["smtp_port"] = config.get("alerts.smtp_port", 587)
        
        # Monitoring settings
        config_data["process_check_interval"] = config.get("alerts.process_check_interval", 60)
        config_data["service_check_interval"] = config.get("alerts.service_check_interval", 120)
        config_data["bridge_check_interval"] = config.get("alerts.bridge_check_interval", 300)
        
        # Thresholds
        config_data["max_memory_usage_mb"] = config.get("alerts.max_memory_usage_mb", 2048)
        config_data["max_cpu_usage_percent"] = config.get("alerts.max_cpu_usage_percent", 80.0)
        config_data["max_consecutive_failures"] = config.get("alerts.max_consecutive_failures", 3)
        
        # Alert settings
        config_data["alert_cooldown_minutes"] = config.get("alerts.cooldown_minutes", 30)
        config_data["recovery_notification_enabled"] = config.get("alerts.recovery_notifications", True)
        
        return AlertConfig(**config_data)
    
    async def _initialize(self):
        """Initialize alert system components"""
        logger.info("Initializing Alert System...")
        
        # Find MinhOS process
        await self._find_minhos_process()
        
        # Validate email configuration
        if not all([self.config.email_user, self.config.email_password, self.config.recipient_email]):
            logger.warning("Email configuration incomplete - alerts will be logged only")
        
        logger.info("Alert System initialized successfully")
    
    async def _start_service(self):
        """Start monitoring tasks"""
        logger.info("Starting Alert System monitoring...")
        
        # Start monitoring tasks
        self._process_monitor_task = asyncio.create_task(self._process_monitor_loop())
        self._service_monitor_task = asyncio.create_task(self._service_monitor_loop())
        self._bridge_monitor_task = asyncio.create_task(self._bridge_monitor_loop())
        self._log_monitor_task = asyncio.create_task(self._log_monitor_loop())
        
        # Send startup notification
        await self._send_alert(
            "system_startup",
            "info",
            "MinhOS Alert System Started",
            "Alert system monitoring has been activated and is now watching MinhOS health.",
            "alert_system"
        )
        
        logger.info("Alert System monitoring started")
    
    async def _stop_service(self):
        """Stop monitoring tasks"""
        logger.info("Stopping Alert System...")
        
        # Cancel monitoring tasks
        tasks = [
            self._process_monitor_task,
            self._service_monitor_task,
            self._bridge_monitor_task,
            self._log_monitor_task
        ]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Send shutdown notification
        await self._send_alert(
            "system_shutdown",
            "warning",
            "MinhOS Alert System Stopped",
            "Alert system monitoring has been deactivated.",
            "alert_system"
        )
        
        logger.info("Alert System stopped")
    
    async def _cleanup(self):
        """Cleanup resources"""
        # Save alert history
        await self._save_alert_history()
    
    async def _find_minhos_process(self):
        """Find the MinhOS process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python3' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if self.minhos_process_name in cmdline:
                        self.minhos_pid = proc.info['pid']
                        logger.info(f"Found MinhOS process: PID {self.minhos_pid}")
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.warning("MinhOS process not found")
    
    async def _process_monitor_loop(self):
        """Monitor MinhOS process health"""
        while True:
            try:
                await self._check_process_health()
                await asyncio.sleep(self.config.process_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Process monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _service_monitor_loop(self):
        """Monitor MinhOS services health"""
        while True:
            try:
                await self._check_service_health()
                await asyncio.sleep(self.config.service_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Service monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _bridge_monitor_loop(self):
        """Monitor bridge connectivity"""
        while True:
            try:
                await self._check_bridge_connectivity()
                await asyncio.sleep(self.config.bridge_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Bridge monitor error: {e}")
                await asyncio.sleep(120)
    
    async def _log_monitor_loop(self):
        """Monitor logs for critical errors"""
        while True:
            try:
                await self._check_critical_errors()
                await asyncio.sleep(60)  # Check logs every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Log monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _check_process_health(self):
        """Check if MinhOS process is running and healthy"""
        try:
            if not self.minhos_pid:
                await self._find_minhos_process()
            
            if not self.minhos_pid:
                await self._handle_process_down()
                return
            
            # Check if process is still running
            try:
                proc = psutil.Process(self.minhos_pid)
                
                # Get process metrics
                memory_info = proc.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                cpu_percent = proc.cpu_percent()
                
                # Check memory usage
                if memory_mb > self.config.max_memory_usage_mb:
                    await self._send_alert(
                        "high_memory_usage",
                        "warning",
                        "High Memory Usage Detected",
                        f"MinhOS is using {memory_mb:.1f}MB of memory (threshold: {self.config.max_memory_usage_mb}MB)",
                        "process"
                    )
                
                # Check CPU usage
                if cpu_percent > self.config.max_cpu_usage_percent:
                    await self._send_alert(
                        "high_cpu_usage",
                        "warning",
                        "High CPU Usage Detected",
                        f"MinhOS is using {cpu_percent:.1f}% CPU (threshold: {self.config.max_cpu_usage_percent}%)",
                        "process"
                    )
                
                # Reset failure counter on success
                self.consecutive_failures["process"] = 0
                
                # Resolve process down alert if it was active
                if "process_down" in self.active_alerts:
                    await self._resolve_alert("process_down", "Process is running normally")
                
            except psutil.NoSuchProcess:
                await self._handle_process_down()
                
        except Exception as e:
            logger.error(f"Process health check error: {e}")
            await self._increment_failure_counter("process")
    
    async def _handle_process_down(self):
        """Handle MinhOS process down scenario"""
        await self._increment_failure_counter("process")
        
        if self.consecutive_failures.get("process", 0) >= self.config.max_consecutive_failures:
            await self._send_alert(
                "process_down",
                "critical",
                "MinhOS Process Down",
                "MinhOS main process is not running. System may be offline.",
                "process"
            )
    
    async def _check_service_health(self):
        """Check MinhOS services health via API"""
        try:
            # Try to get system status from API
            response = requests.get("http://localhost:8888/api/status", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Check individual services
                services = status_data.get("services", {})
                unhealthy_services = []
                
                for service_name, service_info in services.items():
                    if isinstance(service_info, dict):
                        health = service_info.get("health", False)
                    else:
                        health = bool(service_info)
                    
                    if not health:
                        unhealthy_services.append(service_name)
                
                if unhealthy_services:
                    await self._send_alert(
                        "services_unhealthy",
                        "warning",
                        "Unhealthy Services Detected",
                        f"The following services are unhealthy: {', '.join(unhealthy_services)}",
                        "services"
                    )
                else:
                    # Resolve services alert if it was active
                    if "services_unhealthy" in self.active_alerts:
                        await self._resolve_alert("services_unhealthy", "All services are healthy")
                
                # Reset failure counter
                self.consecutive_failures["services"] = 0
                
            else:
                await self._increment_failure_counter("services")
                
        except Exception as e:
            logger.error(f"Service health check error: {e}")
            await self._increment_failure_counter("services")
            
            if self.consecutive_failures.get("services", 0) >= self.config.max_consecutive_failures:
                await self._send_alert(
                    "api_unreachable",
                    "critical",
                    "MinhOS API Unreachable",
                    f"Cannot reach MinhOS API for health checks. Error: {str(e)}",
                    "services"
                )
    
    async def _check_bridge_connectivity(self):
        """Check Sierra Chart bridge connectivity"""
        try:
            response = requests.get("http://marypc:8765/status", timeout=5)
            
            if response.status_code == 200:
                # Bridge is connected
                if "bridge_disconnected" in self.active_alerts:
                    await self._resolve_alert("bridge_disconnected", "Bridge connectivity restored")
                
                self.consecutive_failures["bridge"] = 0
            else:
                await self._increment_failure_counter("bridge")
                
        except Exception as e:
            await self._increment_failure_counter("bridge")
            
            if self.consecutive_failures.get("bridge", 0) >= self.config.max_consecutive_failures:
                await self._send_alert(
                    "bridge_disconnected",
                    "warning",
                    "Sierra Chart Bridge Disconnected",
                    f"Cannot connect to Sierra Chart bridge at marypc:8765. Error: {str(e)}",
                    "bridge"
                )
    
    async def _check_critical_errors(self):
        """Monitor logs for critical errors"""
        try:
            # Check recent log files for critical errors
            log_files = [
                "/home/colindo/Sync/minh_v4/minh_output_auto.log",
                "/home/colindo/Sync/minh_v4/startup_fixed.log"
            ]
            
            critical_patterns = [
                "CRITICAL",
                "FATAL",
                "Exception",
                "Traceback",
                "Error:",
                "Failed to start"
            ]
            
            for log_file in log_files:
                if Path(log_file).exists():
                    # Read last 50 lines
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-50:]
                    
                    recent_errors = []
                    for line in lines:
                        for pattern in critical_patterns:
                            if pattern in line and datetime.now().strftime("%Y-%m-%d") in line:
                                recent_errors.append(line.strip())
                                break
                    
                    if recent_errors:
                        error_summary = "\n".join(recent_errors[-3:])  # Last 3 errors
                        await self._send_alert(
                            "critical_errors",
                            "warning",
                            "Critical Errors Detected in Logs",
                            f"Recent critical errors found:\n{error_summary}",
                            "logs"
                        )
                        
        except Exception as e:
            logger.error(f"Log monitoring error: {e}")
    
    async def _increment_failure_counter(self, component: str):
        """Increment failure counter for a component"""
        self.consecutive_failures[component] = self.consecutive_failures.get(component, 0) + 1
        logger.warning(f"{component} failure count: {self.consecutive_failures[component]}")
    
    async def _send_alert(self, alert_id: str, severity: str, title: str, message: str, component: str):
        """Send an alert notification"""
        # Check alert cooldown
        if alert_id in self.last_alert_times:
            time_since_last = datetime.now() - self.last_alert_times[alert_id]
            if time_since_last < timedelta(minutes=self.config.alert_cooldown_minutes):
                return  # Skip due to cooldown
        
        # Create alert
        alert = Alert(
            id=alert_id,
            severity=severity,
            title=title,
            message=message,
            component=component,
            timestamp=datetime.now()
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_times[alert_id] = alert.timestamp
        
        # Log alert
        logger.warning(f"ALERT [{severity.upper()}] {title}: {message}")
        
        # Send email notification
        await self._send_email_notification(alert)
        
        # Save alert to file
        await self._save_alert_to_file(alert)
    
    async def _resolve_alert(self, alert_id: str, resolution_message: str):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            logger.info(f"RESOLVED: {alert.title} - {resolution_message}")
            
            # Send recovery notification if enabled
            if self.config.recovery_notification_enabled:
                recovery_alert = Alert(
                    id=f"{alert_id}_resolved",
                    severity="info",
                    title=f"RESOLVED: {alert.title}",
                    message=f"Issue has been resolved: {resolution_message}",
                    component=alert.component,
                    timestamp=datetime.now()
                )
                
                await self._send_email_notification(recovery_alert)
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification for alert"""
        if not all([self.config.email_user, self.config.email_password, self.config.recipient_email]):
            logger.warning("Email configuration incomplete - skipping email notification")
            return
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_user
            msg['To'] = self.config.recipient_email
            msg['Subject'] = f"MinhOS Alert: {alert.title}"
            
            # Email body
            body = f"""
MinhOS Alert Notification
========================

Severity: {alert.severity.upper()}
Component: {alert.component}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Message:
{alert.message}

---
This is an automated notification from MinhOS Alert System.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.email_user, self.config.email_password)
            text = msg.as_string()
            server.sendmail(self.config.email_user, self.config.recipient_email, text)
            server.quit()
            
            logger.info(f"Email notification sent for alert: {alert.title}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _save_alert_to_file(self, alert: Alert):
        """Save alert to file"""
        try:
            alert_file = Path("/home/colindo/Sync/minh_v4/logs/alerts.json")
            alert_file.parent.mkdir(exist_ok=True)
            
            alerts_data = []
            if alert_file.exists():
                with open(alert_file, 'r') as f:
                    alerts_data = json.load(f)
            
            # Add new alert
            alert_dict = alert.to_dict()
            alert_dict['timestamp'] = alert.timestamp.isoformat()
            if alert.resolved_at:
                alert_dict['resolved_at'] = alert.resolved_at.isoformat()
            
            alerts_data.append(alert_dict)
            
            # Keep only last 1000 alerts
            alerts_data = alerts_data[-1000:]
            
            with open(alert_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save alert to file: {e}")
    
    async def _save_alert_history(self):
        """Save complete alert history"""
        try:
            history_file = Path("/home/colindo/Sync/minh_v4/logs/alert_history.json")
            history_file.parent.mkdir(exist_ok=True)
            
            history_data = []
            for alert in self.alert_history:
                alert_dict = alert.to_dict()
                alert_dict['timestamp'] = alert.timestamp.isoformat()
                if alert.resolved_at:
                    alert_dict['resolved_at'] = alert.resolved_at.isoformat()
                history_data.append(alert_dict)
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save alert history: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        recent_alerts = self.alert_history[-limit:] if limit else self.alert_history
        return [alert.to_dict() for alert in recent_alerts]
    
    async def test_email_configuration(self) -> bool:
        """Test email configuration"""
        try:
            test_alert = Alert(
                id="test_alert",
                severity="info",
                title="MinhOS Alert System Test",
                message="This is a test notification to verify email configuration.",
                component="test",
                timestamp=datetime.now()
            )
            
            await self._send_email_notification(test_alert)
            return True
            
        except Exception as e:
            logger.error(f"Email test failed: {e}")
            return False

# Global instance
_alert_system_instance = None

def get_alert_system() -> AlertSystem:
    """Get the global alert system instance"""
    global _alert_system_instance
    if _alert_system_instance is None:
        _alert_system_instance = AlertSystem()
    return _alert_system_instance

async def create_alert_system() -> AlertSystem:
    """Create and start a new alert system instance"""
    alert_system = AlertSystem()
    await alert_system.start()
    return alert_system

if __name__ == "__main__":
    async def main():
        alert_system = await create_alert_system()
        try:
            # Keep running
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down alert system...")
            await alert_system.stop()
    
    asyncio.run(main())
