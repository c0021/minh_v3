#!/usr/bin/env python3
"""
Emergency Bridge Restart Script
Kills any existing bridge processes and starts fresh
"""
import subprocess
import time
import os
import sys

def kill_existing_bridge():
    """Kill any existing bridge processes"""
    print("Killing existing bridge processes...")
    
    # Try multiple methods to ensure bridge is killed
    commands = [
        'taskkill /F /IM python.exe /FI "WINDOWTITLE eq *bridge*"',
        'taskkill /F /IM python.exe /FI "COMMANDLINE eq *bridge.py*"',
        'wmic process where "commandline like \'%bridge.py%\'" delete',
        'powershell "Get-Process python | Where-Object {$_.CommandLine -like \'*bridge.py*\'} | Stop-Process -Force"'
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        except:
            pass
    
    time.sleep(2)
    print("Existing processes killed")

def start_bridge():
    """Start the bridge using the batch file"""
    print("Starting bridge...")
    
    bridge_dir = os.path.dirname(os.path.abspath(__file__))
    batch_file = os.path.join(bridge_dir, "start_bridge.bat")
    
    if not os.path.exists(batch_file):
        print(f"ERROR: {batch_file} not found!")
        return False
    
    # Start the bridge in a new window
    subprocess.Popen(f'start cmd /k "{batch_file}"', shell=True, cwd=bridge_dir)
    
    print("Bridge start command issued")
    print("Waiting for bridge to initialize...")
    time.sleep(5)
    
    # Check if bridge is responding
    try:
        import requests
        response = requests.get("http://localhost:8765/health", timeout=5)
        if response.status_code == 200:
            print("✓ Bridge is running and healthy!")
            return True
    except:
        pass
    
    print("⚠ Bridge may still be starting up. Check the command window for details.")
    return False

def main():
    print("=== MinhOS Bridge Emergency Restart ===")
    print("This will kill existing bridge processes and start fresh")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    kill_existing_bridge()
    if start_bridge():
        print("\n✓ Bridge restarted successfully!")
        print("You can now check http://localhost:8765/health")
    else:
        print("\n⚠ Bridge may need manual intervention")
        print("Check the command window for error messages")

if __name__ == "__main__":
    main()