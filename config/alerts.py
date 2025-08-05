#!/usr/bin/env python3
"""
MinhOS Alert System Configuration
=================================
Configuration settings for the alert system.
"""

import os
from typing import Dict, Any

def get_alert_config() -> Dict[str, Any]:
    """Get alert system configuration from environment variables"""
    return {
        # Email Configuration
        "alerts.email_user": os.getenv("MINHOS_ALERT_EMAIL_USER", ""),
        "alerts.email_password": os.getenv("MINHOS_ALERT_EMAIL_PASSWORD", ""),
        "alerts.recipient_email": os.getenv("MINHOS_ALERT_RECIPIENT_EMAIL", ""),
        "alerts.smtp_server": os.getenv("MINHOS_ALERT_SMTP_SERVER", "smtp.gmail.com"),
        "alerts.smtp_port": int(os.getenv("MINHOS_ALERT_SMTP_PORT", "587")),
        
        # Monitoring Intervals (seconds)
        "alerts.process_check_interval": int(os.getenv("MINHOS_ALERT_PROCESS_INTERVAL", "60")),
        "alerts.service_check_interval": int(os.getenv("MINHOS_ALERT_SERVICE_INTERVAL", "120")),
        "alerts.bridge_check_interval": int(os.getenv("MINHOS_ALERT_BRIDGE_INTERVAL", "300")),
        
        # Alert Thresholds
        "alerts.max_memory_usage_mb": int(os.getenv("MINHOS_ALERT_MAX_MEMORY_MB", "2048")),
        "alerts.max_cpu_usage_percent": float(os.getenv("MINHOS_ALERT_MAX_CPU_PERCENT", "80.0")),
        "alerts.max_consecutive_failures": int(os.getenv("MINHOS_ALERT_MAX_FAILURES", "3")),
        
        # Alert Settings
        "alerts.cooldown_minutes": int(os.getenv("MINHOS_ALERT_COOLDOWN_MINUTES", "30")),
        "alerts.recovery_notifications": os.getenv("MINHOS_ALERT_RECOVERY_NOTIFICATIONS", "true").lower() == "true",
        
        # Enable/Disable Features
        "alerts.enabled": os.getenv("MINHOS_ALERTS_ENABLED", "true").lower() == "true",
        "alerts.email_enabled": os.getenv("MINHOS_ALERTS_EMAIL_ENABLED", "true").lower() == "true",
        "alerts.log_monitoring_enabled": os.getenv("MINHOS_ALERTS_LOG_MONITORING", "true").lower() == "true",
        "alerts.bridge_monitoring_enabled": os.getenv("MINHOS_ALERTS_BRIDGE_MONITORING", "true").lower() == "true",
    }

# Default configuration
DEFAULT_ALERT_CONFIG = get_alert_config()
