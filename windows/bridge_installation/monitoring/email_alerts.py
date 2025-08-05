#!/usr/bin/env python3
"""
Email Alert System for MinhOS Bridge
Sends email notifications when bridge shutdowns are detected
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EmailAlerter:
    def __init__(self, config_file="email_config.json"):
        self.config_file = Path(__file__).parent / config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load email configuration from file"""
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": "",
            "enabled": False,
            "alert_cooldown_minutes": 15  # Prevent spam
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
                    return default_config
            except Exception as e:
                logger.error(f"Error loading email config: {e}")
                return default_config
        else:
            # Create default config file
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config):
        """Save email configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving email config: {e}")
    
    def setup_email_config(self, sender_email, sender_password, recipient_email, 
                          smtp_server="smtp.gmail.com", smtp_port=587):
        """Setup email configuration"""
        self.config.update({
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "sender_email": sender_email,
            "sender_password": sender_password,
            "recipient_email": recipient_email,
            "enabled": True
        })
        self.save_config(self.config)
        logger.info("Email configuration updated and enabled")
    
    def send_alert(self, subject, message, alert_type="shutdown"):
        """Send email alert"""
        if not self.config.get("enabled", False):
            logger.warning("Email alerts are disabled")
            return False
        
        if not all([self.config.get("sender_email"), 
                   self.config.get("sender_password"), 
                   self.config.get("recipient_email")]):
            logger.error("Email configuration incomplete")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config["sender_email"]
            msg['To'] = self.config["recipient_email"]
            msg['Subject'] = f"[ALERT] MinhOS Bridge: {subject}"
            
            # Create HTML email body
            html_body = f"""
            <html>
              <body>
                <h2 style="color: #d32f2f;">[ALERT] MinhOS Bridge Alert</h2>
                <p><strong>Alert Type:</strong> {alert_type.upper()}</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Subject:</strong> {subject}</p>
                
                <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f; margin: 20px 0;">
                  <h3>Alert Details:</h3>
                  <pre style="white-space: pre-wrap; font-family: monospace;">{message}</pre>
                </div>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                  This is an automated alert from your MinhOS Bridge monitoring system.<br>
                  Please check your bridge status and take appropriate action.
                </p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(self.config["sender_email"], self.config["sender_password"])
                server.sendmail(self.config["sender_email"], self.config["recipient_email"], msg.as_string())
            
            logger.info(f"Email alert sent successfully: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_shutdown_alert(self, shutdown_data):
        """Send bridge shutdown alert"""
        subject = "Bridge Shutdown Detected"
        
        message = f"""
Bridge Shutdown Details:
========================

Shutdown Time: {shutdown_data.get('shutdown_detected_at', 'Unknown')}
Reason: {shutdown_data.get('reason', 'Unknown')}
Last Known PID: {shutdown_data.get('last_known_pid', 'Unknown')}
Consecutive Failures: {shutdown_data.get('consecutive_failures', 'Unknown')}

System Information:
- CPU Usage: {shutdown_data.get('system_info', {}).get('system', {}).get('cpu_percent', 'Unknown')}%
- Memory Usage: {shutdown_data.get('system_info', {}).get('system', {}).get('memory_percent', 'Unknown')}%
- Disk Usage: {shutdown_data.get('system_info', {}).get('system', {}).get('disk_usage', 'Unknown')}%

Action Required:
- Check bridge status immediately
- Review shutdown report for detailed diagnostics
- Restart bridge if necessary

Bridge Status Check Command:
python check_bridge_status.py
        """
        
        return self.send_alert(subject, message, "shutdown")
    
    def send_recovery_alert(self, recovery_data):
        """Send bridge recovery alert"""
        subject = "Bridge Recovered Successfully"
        
        message = f"""
Bridge Recovery Details:
========================

Recovery Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
New Process ID: {recovery_data.get('new_pid', 'Unknown')}
Health Status: {recovery_data.get('health_status', 'Unknown')}
Response Time: {recovery_data.get('response_time', 'Unknown')}

The bridge has been successfully restarted and is now operational.
Normal monitoring will continue.
        """
        
        return self.send_alert(subject, message, "recovery")
    
    def test_email(self):
        """Send test email to verify configuration"""
        subject = "Test Email - Configuration Verified"
        message = """
This is a test email from your MinhOS Bridge monitoring system.

If you receive this email, your email alert configuration is working correctly.

Email alerts are now active and will notify you of:
- Bridge shutdowns
- Bridge recoveries
- Critical system events

Test completed successfully!
        """
        
        return self.send_alert(subject, message, "test")

def setup_email_alerts():
    """Interactive setup for email alerts"""
    print("=" * 60)
    print("MinhOS Bridge Email Alert Setup")
    print("=" * 60)
    print()
    
    alerter = EmailAlerter()
    
    print("This will configure email alerts for bridge shutdowns.")
    print("You'll need:")
    print("- A Gmail account (or other SMTP email)")
    print("- An App Password (for Gmail) or regular password")
    print("- The email address to receive alerts")
    print()
    
    # Get configuration
    sender_email = input("Enter sender email address (Gmail recommended): ").strip()
    sender_password = input("Enter email password (use App Password for Gmail): ").strip()
    recipient_email = input("Enter recipient email address (where to send alerts): ").strip()
    
    print()
    print("Advanced settings (press Enter for defaults):")
    smtp_server = input("SMTP server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP port [587]: ").strip() or "587"
    
    try:
        smtp_port = int(smtp_port)
    except ValueError:
        smtp_port = 587
    
    # Save configuration
    alerter.setup_email_config(sender_email, sender_password, recipient_email, smtp_server, smtp_port)
    
    print()
    print("Configuration saved! Sending test email...")
    
    # Send test email
    if alerter.test_email():
        print("✅ Test email sent successfully!")
        print("Email alerts are now active.")
    else:
        print("❌ Test email failed. Please check your configuration.")
        print("Common issues:")
        print("- Gmail requires App Passwords (not regular password)")
        print("- Check email address spelling")
        print("- Verify SMTP settings")
    
    print()
    print("Email alert setup complete!")
    return alerter

if __name__ == "__main__":
    setup_email_alerts()
