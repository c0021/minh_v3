#!/usr/bin/env python3
"""
Example: Using the Unified Market Data Store
===========================================

This example demonstrates how to use the new unified market data store
as a single source of truth for all market data operations.
"""

import asyncio
import time
from datetime import datetime
from minhos.core.market_data_adapter import get_market_data_adapter
from minhos.models.market import MarketData


async def example_producer(adapter):
    """Example of a service that produces market data"""
    print("📊 Producer: Generating sample market data...")
    
    symbols = ["NQ", "ES", "CL", "GC"]
    base_prices = {"NQ": 15000, "ES": 4500, "CL": 80, "GC": 2000}
    
    for i in range(10):
        for symbol in symbols:
            # Generate sample data
            price = base_prices[symbol] + (i * 0.1)
            data = MarketData(
                symbol=symbol,
                timestamp=time.time(),
                close=price,
                bid=price - 0.25,
                ask=price + 0.25,
                volume=100 + i * 10,
                source="example_producer"
            )
            
            # Add to unified store
            await adapter.async_add_data(data)
            print(f"  ✅ Added {symbol} @ ${price:.2f}")
        
        await asyncio.sleep(1)


async def example_consumer(adapter, name):
    """Example of a service that consumes market data"""
    print(f"👀 {name}: Subscribing to market data updates...")
    
    # Define callback
    def on_data(data: MarketData):
        print(f"  📡 {name} received: {data.symbol} @ ${data.close:.2f}")
    
    # Subscribe to updates
    await adapter.subscribe(on_data)
    
    # Keep running
    await asyncio.sleep(12)
    
    # Unsubscribe
    adapter.unsubscribe(on_data)


async def example_query(adapter):
    """Example of querying the unified store"""
    await asyncio.sleep(5)  # Wait for some data
    
    print("\n🔍 Querying unified store...")
    
    # Get latest data for all symbols
    latest = adapter.get_latest_data()
    print(f"\n📊 Latest data for {len(latest)} symbols:")
    for symbol, data in latest.items():
        print(f"  - {symbol}: ${data.close:.2f} (bid: ${data.bid:.2f}, ask: ${data.ask:.2f})")
    
    # Get historical data for one symbol
    history = adapter.get_historical_data("NQ", limit=5)
    print(f"\n📈 Last 5 data points for NQ:")
    for data in history:
        print(f"  - ${data.close:.2f} at {datetime.fromtimestamp(data.timestamp).strftime('%H:%M:%S')}")
    
    # Get all available symbols
    symbols = adapter.get_symbols()
    print(f"\n🏷️  Available symbols: {', '.join(symbols)}")
    
    # Get storage statistics
    stats = adapter.get_stats()
    print(f"\n📊 Storage statistics:")
    print(f"  - Symbols: {stats['symbols']}")
    print(f"  - Memory records: {stats['memory_records']}")
    print(f"  - Total records: {stats['total_records']}")
    print(f"  - Database size: {stats['db_size_mb']} MB")


async def main():
    """Run the example"""
    print("🚀 Unified Market Data Store Example\n")
    
    # Get the singleton adapter
    adapter = get_market_data_adapter()
    
    # Start the adapter
    await adapter.start()
    
    try:
        # Run example tasks concurrently
        await asyncio.gather(
            example_producer(adapter),
            example_consumer(adapter, "Consumer 1"),
            example_consumer(adapter, "Consumer 2"),
            example_query(adapter)
        )
    finally:
        # Stop the adapter
        await adapter.stop()
    
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())