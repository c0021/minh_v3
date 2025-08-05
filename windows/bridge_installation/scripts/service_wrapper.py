#!/usr/bin/env python
"""
Simple service wrapper that runs start_bridge.bat
"""
import subprocess
import sys
import os
import time

def run_service():
    """Run the bridge via start_bridge.bat"""
    bridge_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(bridge_dir)
    
    batch_file = os.path.join(bridge_dir, "start_bridge.bat")
    
    while True:
        try:
            # Run the batch file
            process = subprocess.Popen(
                [batch_file],
                cwd=bridge_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Wait for process to complete
            process.wait()
            
            # If it exits, wait and restart
            time.sleep(5)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_service()