#!/usr/bin/env python
"""
MinhOS Bridge Windows Service Wrapper
Automatically restarts the bridge when it hits request limits or errors
"""
import os
import sys
import time
import subprocess
import logging
from pathlib import Path

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "bridge_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BridgeService:
    def __init__(self):
        self.bridge_dir = Path(__file__).parent
        self.venv_python = self.bridge_dir / "venv" / "Scripts" / "python.exe"
        self.bridge_script = self.bridge_dir / "bridge.py"
        self.max_restarts = 10  # Maximum restarts per hour
        self.restart_count = 0
        self.last_restart_time = 0
        
    def run_bridge(self):
        """Run the bridge process and handle restarts"""
        logger.info("Starting MinhOS Bridge Service Wrapper")
        
        while True:
            try:
                # Check restart limits
                current_time = time.time()
                if current_time - self.last_restart_time > 3600:  # Reset counter every hour
                    self.restart_count = 0
                    
                if self.restart_count >= self.max_restarts:
                    logger.error(f"Maximum restarts ({self.max_restarts}) reached in the last hour. Waiting...")
                    time.sleep(3600)  # Wait 1 hour before allowing more restarts
                    self.restart_count = 0
                
                logger.info(f"Starting bridge process (restart #{self.restart_count})")
                
                # Start the bridge process
                env = os.environ.copy()
                env['PYTHONUNBUFFERED'] = '1'
                env['PYTHONDONTWRITEBYTECODE'] = '1'
                
                process = subprocess.Popen(
                    [str(self.venv_python), str(self.bridge_script)],
                    cwd=str(self.bridge_dir),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Monitor the process
                while True:
                    output = process.stdout.readline()
                    if output:
                        # Log bridge output (without newline since it's already there)
                        logger.info(f"BRIDGE: {output.rstrip()}")
                        
                    # Check if process is still running
                    if process.poll() is not None:
                        break
                        
                    time.sleep(0.1)
                
                # Process ended
                return_code = process.returncode
                logger.warning(f"Bridge process ended with return code: {return_code}")
                
                # Check if it was a normal shutdown (Ctrl+C)
                if return_code == 0:
                    logger.info("Bridge stopped normally. Service will restart in 5 seconds...")
                else:
                    logger.error(f"Bridge crashed with error code {return_code}. Restarting in 10 seconds...")
                    
                # Update restart tracking
                self.restart_count += 1
                self.last_restart_time = time.time()
                
                # Wait before restart
                wait_time = 5 if return_code == 0 else 10
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("Service shutdown requested")
                if 'process' in locals() and process.poll() is None:
                    logger.info("Terminating bridge process...")
                    process.terminate()
                    time.sleep(5)
                    if process.poll() is None:
                        process.kill()
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in service wrapper: {e}")
                time.sleep(30)  # Wait longer on unexpected errors

if __name__ == "__main__":
    service = BridgeService()
    service.run_bridge()