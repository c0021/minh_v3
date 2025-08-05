#!/usr/bin/env python3
"""
Quick Bridge Status Checker
Simple script to check bridge status and show results
"""

import requests
import json
import psutil
from datetime import datetime
import sys

def get_bridge_process():
    """Find the bridge process"""
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
    except Exception:
        return None

def check_bridge_health():
    """Check bridge health endpoint"""
    try:
        response = requests.get("http://localhost:8765/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("MinhOS Bridge Status Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check process
    pid = get_bridge_process()
    if pid:
        print(f"[OK] Bridge Process: Running (PID: {pid})")
    else:
        print("[ERROR] Bridge Process: Not found")
    
    # Check health endpoint
    is_healthy, health_data = check_bridge_health()
    if is_healthy:
        print(f"[OK] Health Endpoint: Responding")
        print(f"   Status: {health_data.get('status', 'unknown')}")
        print(f"   Version: {health_data.get('version', 'unknown')}")
        print(f"   Service: {health_data.get('service', 'unknown')}")
    else:
        print(f"[ERROR] Health Endpoint: Failed ({health_data})")
    
    print()
    
    # Overall status
    if pid and is_healthy:
        print("[SUCCESS] OVERALL STATUS: BRIDGE IS RUNNING SUCCESSFULLY")
        return 0
    elif pid and not is_healthy:
        print("[WARNING] OVERALL STATUS: BRIDGE PROCESS RUNNING BUT NOT RESPONDING")
        return 1
    elif not pid and is_healthy:
        print("[WARNING] OVERALL STATUS: HEALTH ENDPOINT RESPONDING BUT NO PROCESS FOUND")
        return 1
    else:
        print("[CRITICAL] OVERALL STATUS: BRIDGE IS DOWN")
        return 2

if __name__ == "__main__":
    sys.exit(main())
