#!/usr/bin/env python3
"""
Start Dashboard with Kelly Service Integration
===========================================

Starts the MinhOS dashboard with a running Kelly service instance.
This ensures the Kelly API endpoints are available and operational.
"""

import asyncio
import sys
import signal
import logging
from pathlib import Path

# Add Kelly implementation path
kelly_impl_path = Path(__file__).parent / "implementation" / "ml_kelly_criterion_week5"
sys.path.insert(0, str(kelly_impl_path.absolute()))
sys.path.insert(0, str(kelly_impl_path / "services"))

from kelly_service import KellyService
from minhos.dashboard.main import DashboardServer

# Global Kelly service instance
kelly_service = None
dashboard_server = None

async def startup():
    """Start Kelly service and dashboard"""
    global kelly_service, dashboard_server
    
    print("🚀 Starting Kelly Service...")
    kelly_service = KellyService()
    await kelly_service.start()
    print("✅ Kelly Service started")
    
    print("🚀 Starting Dashboard...")
    dashboard_server = DashboardServer()
    await dashboard_server.start()
    print("✅ Dashboard started on http://localhost:8888")

async def shutdown():
    """Graceful shutdown"""
    global kelly_service, dashboard_server
    
    print("🛑 Shutting down...")
    if dashboard_server:
        await dashboard_server.stop()
    if kelly_service:
        await kelly_service.stop()
    print("✅ Shutdown complete")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print(f"\n📡 Received signal {sig}")
    if dashboard_server:
        asyncio.create_task(shutdown())

async def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await startup()
        
        # Keep running until interrupted
        print("📊 Dashboard with Kelly service running...")
        print("🔗 Kelly API: http://localhost:8888/api/kelly/")
        print("📈 Dashboard: http://localhost:8888/")
        print("Press Ctrl+C to stop")
        
        # Run forever
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())