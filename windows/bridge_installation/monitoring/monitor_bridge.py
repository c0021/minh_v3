#!/usr/bin/env python3
"""
MinhOS Bridge Monitoring Script
Monitors the bridge service for shutdowns and captures diagnostic information
"""

import os
import sys
import time
import json
import requests
import psutil
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import traceback
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Import email alerting system
try:
    from email_alerts import EmailAlerter
    EMAIL_ALERTS_AVAILABLE = True
except ImportError:
    EMAIL_ALERTS_AVAILABLE = False

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "bridge_monitor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BridgeMonitor:
    def __init__(self):
        self.bridge_url = "http://localhost:8765"
        self.health_endpoint = f"{self.bridge_url}/health"
        self.status_endpoint = f"{self.bridge_url}/status"
        self.check_interval = 10  # seconds
        self.consecutive_failures = 0
        self.max_failures_before_alert = 3
        self.last_known_pid = None
        self.bridge_was_running = False
        
        # Create monitoring log directory
        self.monitor_log_dir = Path(__file__).parent / "monitoring_logs"
        self.monitor_log_dir.mkdir(exist_ok=True)
        
        # Initialize email alerter
        self.email_alerter = None
        if EMAIL_ALERTS_AVAILABLE:
            try:
                self.email_alerter = EmailAlerter()
                if self.email_alerter.config.get('enabled', False):
                    logger.info("Email alerts enabled")
                else:
                    logger.info("Email alerts available but disabled")
            except Exception as e:
                logger.warning(f"Email alerter initialization failed: {e}")
        else:
            logger.info("Email alerts not available")
        
        logger.info("Bridge Monitor initialized")
        logger.info(f"Monitoring URL: {self.bridge_url}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info(f"Log directory: {self.monitor_log_dir}")

    def get_bridge_process(self):
        """Find the bridge process by looking for python processes running bridge.py"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'bridge.py' in cmdline:
                            return proc.info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return None
        except Exception as e:
            logger.error(f"Error finding bridge process: {e}")
            return None

    def check_bridge_health(self):
        """Check if bridge is responding to health checks"""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def get_bridge_status(self):
        """Get detailed bridge status"""
        try:
            response = requests.get(self.status_endpoint, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def capture_system_info(self):
        """Capture system information when bridge goes down"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('C:').percent
            },
            "processes": []
        }
        
        # Get all python processes
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_percent', 'cpu_percent']):
                try:
                    if proc.info['name'] == 'python.exe':
                        info["processes"].append({
                            "pid": proc.info['pid'],
                            "cmdline": proc.info['cmdline'],
                            "memory_percent": proc.info['memory_percent'],
                            "cpu_percent": proc.info['cpu_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            info["process_error"] = str(e)
        
        return info

    def save_shutdown_report(self, reason, system_info, last_health_data=None):
        """Save detailed shutdown report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.monitor_log_dir / f"shutdown_report_{timestamp}.json"
        
        report = {
            "shutdown_detected_at": datetime.now().isoformat(),
            "reason": reason,
            "last_known_pid": self.last_known_pid,
            "consecutive_failures": self.consecutive_failures,
            "last_health_data": last_health_data,
            "system_info": system_info
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.error(f"Shutdown report saved: {report_file}")
            return report  # Return report data for email alerts
        except Exception as e:
            logger.error(f"Failed to save shutdown report: {e}")
            return report  # Still return data even if file save failed

    def check_bridge_logs(self):
        """Check for recent errors in bridge logs"""
        log_files = [
            "bridge.log",
            "logs/bridge_service.log",
            "bridge_startup.log"
        ]
        
        recent_errors = []
        base_dir = Path(__file__).parent
        
        for log_file in log_files:
            log_path = base_dir / log_file
            if log_path.exists():
                try:
                    # Read last 50 lines
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_lines = lines[-50:] if len(lines) > 50 else lines
                        
                    # Look for errors in recent lines
                    for line in recent_lines:
                        if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed', 'crash']):
                            recent_errors.append({
                                "file": str(log_file),
                                "line": line.strip()
                            })
                except Exception as e:
                    logger.warning(f"Could not read log file {log_file}: {e}")
        
        return recent_errors

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting bridge monitoring...")
        
        while True:
            try:
                # Check if bridge process exists
                current_pid = self.get_bridge_process()
                
                # Check if bridge responds to health checks
                is_healthy, health_data = self.check_bridge_health()
                
                if is_healthy and current_pid:
                    # Bridge is running and healthy
                    if not self.bridge_was_running:
                        logger.info(f"Bridge detected as running (PID: {current_pid})")
                        self.bridge_was_running = True
                        
                        # Send recovery alert if we had previously detected a shutdown
                        if hasattr(self, '_shutdown_detected') and self._shutdown_detected:
                            if self.email_alerter and self.email_alerter.config.get('enabled', False):
                                try:
                                    recovery_data = {
                                        'new_pid': current_pid,
                                        'health_status': 'healthy',
                                        'response_time': 'responding'
                                    }
                                    self.email_alerter.send_recovery_alert(recovery_data)
                                    logger.info("Email recovery alert sent")
                                except Exception as e:
                                    logger.error(f"Failed to send recovery alert: {e}")
                            self._shutdown_detected = False
                    
                    self.last_known_pid = current_pid
                    self.consecutive_failures = 0
                    
                    # Log periodic status
                    if int(time.time()) % 60 == 0:  # Every minute
                        status = self.get_bridge_status()
                        logger.info(f"Bridge healthy - PID: {current_pid}, Status: {status.get('status', 'unknown')}")
                
                else:
                    # Bridge is not responding or process not found
                    self.consecutive_failures += 1
                    
                    if self.bridge_was_running and self.consecutive_failures >= self.max_failures_before_alert:
                        # Bridge was running but now appears to be down
                        logger.error("=" * 60)
                        logger.error("BRIDGE SHUTDOWN DETECTED!")
                        logger.error("=" * 60)
                        
                        # Capture diagnostic information
                        system_info = self.capture_system_info()
                        recent_errors = self.check_bridge_logs()
                        
                        reason = f"Health check failed: {health_data}" if not is_healthy else "Process not found"
                        if recent_errors:
                            reason += f" | Recent errors found in logs: {len(recent_errors)} errors"
                        
                        logger.error(f"Shutdown reason: {reason}")
                        logger.error(f"Last known PID: {self.last_known_pid}")
                        logger.error(f"Current PID: {current_pid}")
                        logger.error(f"Consecutive failures: {self.consecutive_failures}")
                        
                        if recent_errors:
                            logger.error("Recent log errors:")
                            for error in recent_errors[-5:]:  # Show last 5 errors
                                logger.error(f"  {error['file']}: {error['line']}")
                        
                        # Save detailed report
                        shutdown_report = self.save_shutdown_report(reason, system_info, health_data)
                        
                        # Send email alert if configured
                        if self.email_alerter and self.email_alerter.config.get('enabled', False):
                            try:
                                self.email_alerter.send_shutdown_alert(shutdown_report)
                                logger.info("Email alert sent for bridge shutdown")
                            except Exception as e:
                                logger.error(f"Failed to send email alert: {e}")
                        
                        # Reset state
                        self.bridge_was_running = False
                        self.consecutive_failures = 0
                        
                        logger.error("Continuing to monitor for bridge restart...")
                        logger.error("=" * 60)
                        
                        # Mark that we detected a shutdown for recovery notification
                        self._shutdown_detected = True
                    
                    elif not self.bridge_was_running:
                        # Bridge hasn't been detected as running yet
                        if self.consecutive_failures == 1:
                            logger.warning("Bridge not detected yet, waiting for startup...")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                logger.error(traceback.format_exc())
                time.sleep(self.check_interval)

if __name__ == "__main__":
    print("MinhOS Bridge Monitor")
    print("====================")
    print("This script will monitor the bridge service and alert when shutdowns occur.")
    print("Press Ctrl+C to stop monitoring.")
    print()
    
    monitor = BridgeMonitor()
    monitor.monitor_loop()
