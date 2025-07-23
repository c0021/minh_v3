#!/usr/bin/env python3
"""
MinhOS v3 Main Entry Point
==========================
Central orchestrator for the Linux-native trading system.
Manages service lifecycle, health monitoring, and graceful shutdown.

Architecture:
- Async-first design for efficient concurrent operations
- Service dependency management
- Health monitoring and automatic recovery
- Graceful shutdown handling
"""

import asyncio
import signal
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from minhos.services.orchestrator import ServiceOrchestrator
from minhos.core.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('./logs/minhos.log')
    ]
)
logger = logging.getLogger('minhos.main')


class MinhOS:
    """Main MinhOS application manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize MinhOS with configuration"""
        self.config = Config(config_path)
        self.orchestrator = ServiceOrchestrator(self.config)
        self.running = False
        self.start_time = None
        
        # Setup signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    async def start(self):
        """Start MinhOS and all services"""
        try:
            self.running = True
            self.start_time = datetime.now()
            
            logger.info("=" * 60)
            logger.info("MinhOS v3 Trading System Starting")
            logger.info("=" * 60)
            logger.info(f"Configuration loaded successfully")
            logger.info(f"Environment: {self.config.environment}")
            
            # Start service orchestrator
            await self.orchestrator.start()
            
            # Main event loop
            while self.running:
                await asyncio.sleep(1)
                
                # Check if orchestrator is still running
                if not self.orchestrator.running:
                    logger.warning("Service orchestrator stopped unexpectedly")
                    break
            
        except Exception as e:
            logger.error(f"Fatal error in MinhOS: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown of all services"""
        logger.info("Initiating MinhOS shutdown...")
        
        try:
            # Stop the orchestrator (which stops all services)
            await self.orchestrator.stop()
            
            # Calculate uptime
            if self.start_time:
                uptime = datetime.now() - self.start_time
                logger.info(f"Total uptime: {uptime}")
            
            logger.info("MinhOS shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'running': self.running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'services': self.orchestrator.get_service_status(),
            'config': {
                'environment': self.config.get('environment', 'production'),
                'debug': self.config.get('debug', False)
            }
        }


async def main():
    """Main entry point"""
    # Parse command line arguments if needed
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    # Create and start MinhOS
    app = MinhOS(config_path)
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Run the application
    asyncio.run(main())