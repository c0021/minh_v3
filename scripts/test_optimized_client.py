#!/usr/bin/env python3
"""
Test script for the optimized Sierra Client
Run this when the Windows Bridge API is active
"""
import asyncio
import logging
import time
from datetime import datetime

# Add parent directory to path
import sys
sys.path.insert(0, '/home/colindo/Sync/minh_v3')

from minhos.services.sierra_client import SierraClient


async def test_optimized_client():
    """Test the optimized Sierra Client"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger(__name__)
    
    logger.info("=== Testing Optimized Sierra Client ===")
    
    # Create client instance
    client = SierraClient()
    
    try:
        # Start the client
        logger.info("Starting Sierra Client...")
        await client.start()
        
        # Give it time to establish connection
        logger.info("Waiting for connection...")
        await asyncio.sleep(5)
        
        # Check connection status
        status = client.get_status()
        logger.info(f"Client Status: {status}")
        
        # Monitor for 30 seconds
        logger.info("\nMonitoring market data streaming for 30 seconds...")
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < 30:
            # Check if we're getting data
            if client.last_market_data:
                for symbol, data in client.last_market_data.items():
                    logger.info(
                        f"📊 {symbol}: ${data.price:.2f} "
                        f"(bid: ${data.bid:.2f}, ask: ${data.ask:.2f})"
                    )
                request_count += 1
            
            await asyncio.sleep(1)
        
        # Final report
        elapsed = time.time() - start_time
        avg_rate = request_count / elapsed if request_count > 0 else 0
        
        logger.info("\n=== Test Results ===")
        logger.info(f"Duration: {elapsed:.1f} seconds")
        logger.info(f"Data updates received: {request_count}")
        logger.info(f"Average rate: {avg_rate:.2f} updates/second")
        logger.info(f"Connection state: {client.connection_state.value}")
        
        if avg_rate >= 0.8:  # Expecting ~1Hz
            logger.info("✅ SUCCESS: Streaming is working at expected rate!")
        elif avg_rate > 0:
            logger.warning("⚠️  WARNING: Streaming rate is below expected")
        else:
            logger.error("❌ FAILED: No data received")
            
    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)
        
    finally:
        logger.info("\nStopping client...")
        await client.stop()
        logger.info("Test complete")


async def test_direct_connection():
    """Test direct HTTP connection with optimizations"""
    import aiohttp
    import socket
    
    logger = logging.getLogger(__name__)
    logger.info("\n=== Testing Direct Connection ===")
    
    # Create optimized connector
    connector = aiohttp.TCPConnector(
        limit=10,
        force_close=False,
        keepalive_timeout=30
    )
    
    # Set TCP_NODELAY
    async def on_connection_create_func(session, trace_config_ctx, params):
        sock = params.transport.get_extra_info('socket')
        if sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            logger.debug("TCP_NODELAY set on connection")
    
    trace_config = aiohttp.TraceConfig()
    trace_config.on_connection_create_end.append(on_connection_create_func)
    
    async with aiohttp.ClientSession(
        connector=connector,
        trace_configs=[trace_config]
    ) as session:
        
        # Test 10 requests
        times = []
        for i in range(10):
            start = time.time()
            try:
                async with session.get(
                    'http://marypc:8765/api/market_data',
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        elapsed = time.time() - start
                        times.append(elapsed)
                        logger.info(f"Request {i+1}: {elapsed:.3f}s - {data.get('symbol', 'N/A')}")
                    else:
                        logger.error(f"Request {i+1}: HTTP {resp.status}")
            except Exception as e:
                logger.error(f"Request {i+1} failed: {e}")
            
            await asyncio.sleep(1)
        
        if times:
            avg_time = sum(times) / len(times)
            logger.info(f"\nAverage request time: {avg_time:.3f}s")
            if avg_time < 0.1:
                logger.info("✅ Excellent: Latency is optimal")
            elif avg_time < 0.2:
                logger.info("✅ Good: Latency is acceptable")
            else:
                logger.warning("⚠️  High latency detected")


async def main():
    """Run all tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Test direct connection first
        await test_direct_connection()
        
        # Then test the full client
        await test_optimized_client()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")


if __name__ == "__main__":
    print("MinhOS v3 Optimized Sierra Client Test")
    print("======================================")
    print("Make sure the Windows Bridge API is running at http://marypc:8765")
    print()
    
    asyncio.run(main())