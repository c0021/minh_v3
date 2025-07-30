#!/usr/bin/env python3
"""
Start Continuous Gap Monitoring
===============================

Enables continuous monitoring for data gaps and automatic backfill
using real Sierra Chart historical data.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from minhos.services.sierra_historical_data import get_sierra_historical_service

async def start_continuous_monitoring():
    """Start the continuous gap monitoring service"""
    print("🔄 Starting Continuous Gap Monitoring Service")
    print("=" * 50)
    print("Philosophy: Real Sierra Chart data only - no synthetic data")
    print()
    
    # Get the historical data service
    historical_service = get_sierra_historical_service()
    
    print("📊 Service Status:")
    print(f"  Bridge URL: {historical_service.bridge_url}")
    print(f"  Monitored Symbols: {historical_service.symbols}")
    print()
    
    # Start the service (includes gap monitoring loop)
    print("🚀 Starting historical data service with gap monitoring...")
    await historical_service.start()
    
    print("✅ Continuous gap monitoring is now active!")
    print("   - Checks for gaps every hour")
    print("   - Automatically fills gaps with real Sierra Chart data")
    print("   - Ensures continuous data integrity")
    print()
    print("Press Ctrl+C to stop monitoring...")
    
    try:
        # Keep the service running
        while True:
            await asyncio.sleep(60)  # Check every minute that service is running
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping continuous gap monitoring...")
        # Service cleanup would go here
        print("✅ Gap monitoring stopped")

if __name__ == "__main__":
    asyncio.run(start_continuous_monitoring())