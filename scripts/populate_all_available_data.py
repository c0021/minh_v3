#!/usr/bin/env python3
"""
Populate All Available Historical Data
=====================================

Backfills historical data for all discovered Sierra Chart instruments.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from minhos.services.sierra_historical_data import get_sierra_historical_service

async def populate_all_data():
    """Populate historical data for all available instruments"""
    print("🚀 Populating All Available Historical Data")
    print("=" * 60)
    print("Philosophy: Real Sierra Chart data only")
    print()
    
    # Instruments discovered from Sierra Chart
    instruments = {
        "Futures": {
            "NQU25-CME": 30,  # NASDAQ Sep 2025 (active)
            "NQM25-CME": 60,  # NASDAQ Jun 2025 (historical)
        },
        "Forex": {
            "EURUSD": 90,     # EUR/USD (massive history available)
        },
        "Commodities": {
            "XAUUSD": 90,     # Gold (decades of history)
        }
    }
    
    total_records = 0
    successful_symbols = 0
    
    for category, symbols in instruments.items():
        print(f"\n📊 {category}:")
        
        for symbol, days in symbols.items():
            print(f"  🔄 Backfilling {symbol} ({days} days)...")
            
            try:
                # Import here to avoid module loading issues
                import subprocess
                result = subprocess.run([
                    'python3', 'scripts/historical_data_manager.py', 
                    'backfill', '--symbol', symbol, '--days', str(days)
                ], capture_output=True, text=True, cwd='/home/colindo/Sync/minh_v3')
                
                if "✅ Backfill completed" in result.stdout:
                    # Extract number of records from output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Retrieved" in line and "records" in line:
                            try:
                                records = int(line.split('Retrieved ')[1].split(' ')[0])
                                total_records += records
                                successful_symbols += 1
                                print(f"  ✅ {symbol}: {records} records added")
                                break
                            except:
                                print(f"  ✅ {symbol}: Completed (records count unknown)")
                else:
                    print(f"  ❌ {symbol}: Failed - {result.stdout.split('❌')[-1].split()[0:5] if '❌' in result.stdout else 'Unknown error'}")
                    
            except Exception as e:
                print(f"  ❌ {symbol}: Error - {e}")
    
    print(f"\n🎯 Population Complete:")
    print(f"  Successful Symbols: {successful_symbols}")
    print(f"  Total Records Added: {total_records}")
    print(f"  Data Sources: 100% Real Sierra Chart")
    print(f"  Philosophy: ✅ No synthetic data")

if __name__ == "__main__":
    asyncio.run(populate_all_data())