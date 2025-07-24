#!/usr/bin/env python3
"""
MinhOS Historical Data Management Script
=======================================

Command-line tool for managing Sierra Chart historical data integration.
Provides gap analysis, backfill operations, and data quality reports.

Usage:
    python3 scripts/historical_data_manager.py --help
    python3 scripts/historical_data_manager.py gaps --symbol NQU25-CME
    python3 scripts/historical_data_manager.py backfill --symbol NQU25-CME --days 30
    python3 scripts/historical_data_manager.py report --symbol NQU25-CME
"""

import asyncio
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from minhos.services.sierra_historical_data import get_sierra_historical_service
from minhos.core.market_data_adapter import get_market_data_adapter

async def analyze_gaps(symbol: str = "NQU25-CME"):
    """Analyze data gaps for a symbol"""
    print(f"🔍 Analyzing data gaps for {symbol}...")
    
    historical_service = get_sierra_historical_service()
    gaps = await historical_service._detect_data_gaps(symbol)
    
    if gaps:
        print(f"📊 Found {len(gaps)} data gaps:")
        for i, (start, end) in enumerate(gaps, 1):
            duration = (end - start).days
            print(f"  Gap {i}: {start.date()} to {end.date()} ({duration} days)")
    else:
        print("✅ No data gaps found")

async def backfill_data(symbol: str = "NQU25-CME", days: int = 30):
    """Backfill historical data for a symbol"""
    print(f"🔄 Backfilling {days} days of data for {symbol}...")
    
    historical_service = get_sierra_historical_service()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    print(f"📅 Date range: {start_date.date()} to {end_date.date()}")
    
    # Get historical data
    records = await historical_service.get_historical_data(
        symbol, start_date, end_date, "daily"
    )
    
    if records:
        print(f"📈 Retrieved {len(records)} historical records")
        
        # Fill the data gap
        await historical_service._fill_data_gap(symbol, start_date, end_date)
        print("✅ Backfill completed")
    else:
        print("❌ No historical data retrieved")

async def generate_report(symbol: str = "NQU25-CME"):
    """Generate data quality report for a symbol"""
    print(f"📋 Generating data quality report for {symbol}...")
    
    market_adapter = get_market_data_adapter()
    historical_service = get_sierra_historical_service()
    
    # Get current data range
    try:
        existing_data = await market_adapter.get_historical_range(symbol)
        
        if existing_data:
            print("📊 Current Data Summary:")
            print(f"  Earliest record: {existing_data[0]}")
            print(f"  Latest record: {existing_data[1]}")
            print(f"  Total days: {(existing_data[1] - existing_data[0]).days}")
        else:
            print("❌ No existing data found in MinhOS database")
    except Exception as e:
        print(f"❌ Error accessing existing data: {e}")
    
    # Check Sierra Chart availability
    try:
        # Test Sierra Chart access
        test_data = await historical_service.get_historical_data(
            symbol, 
            datetime.now() - timedelta(days=1), 
            datetime.now(), 
            "daily"
        )
        
        if test_data:
            print("✅ Sierra Chart historical data access: WORKING")
            print(f"  Sample records available: {len(test_data)}")
        else:
            print("⚠️ Sierra Chart historical data access: NO DATA")
    except Exception as e:
        print(f"❌ Sierra Chart access error: {e}")

async def list_available_data():
    """List available data files from Sierra Chart"""
    print("📂 Listing available Sierra Chart data files...")
    
    historical_service = get_sierra_historical_service()
    
    try:
        # This would require the bridge file API to be implemented
        print("🔄 Connecting to Sierra Chart bridge...")
        print("⚠️ Bridge file API implementation needed")
    except Exception as e:
        print(f"❌ Error listing files: {e}")

async def test_connection():
    """Test connection to Sierra Chart bridge"""
    print("🔗 Testing Sierra Chart bridge connection...")
    
    historical_service = get_sierra_historical_service()
    
    try:
        # Test basic connectivity
        test_result = await historical_service._request_file_content("test.txt")
        
        if test_result is not None:
            print("✅ Bridge connection: WORKING")
        else:
            print("❌ Bridge connection: FAILED")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="MinhOS Historical Data Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Gaps command
    gaps_parser = subparsers.add_parser('gaps', help='Analyze data gaps')
    gaps_parser.add_argument('--symbol', default='NQU25-CME', help='Trading symbol')
    
    # Backfill command
    backfill_parser = subparsers.add_parser('backfill', help='Backfill historical data')
    backfill_parser.add_argument('--symbol', default='NQU25-CME', help='Trading symbol')
    backfill_parser.add_argument('--days', type=int, default=30, help='Number of days to backfill')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate data quality report')
    report_parser.add_argument('--symbol', default='NQU25-CME', help='Trading symbol')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available data files')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test bridge connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run async command
    if args.command == 'gaps':
        asyncio.run(analyze_gaps(args.symbol))
    elif args.command == 'backfill':
        asyncio.run(backfill_data(args.symbol, args.days))
    elif args.command == 'report':
        asyncio.run(generate_report(args.symbol))
    elif args.command == 'list':
        asyncio.run(list_available_data())
    elif args.command == 'test':
        asyncio.run(test_connection())

if __name__ == "__main__":
    main()