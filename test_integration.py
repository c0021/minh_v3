#!/usr/bin/env python3
"""
MinhOS v3 Integration Test
==========================

Quick test to verify the live trading integration is working properly.

This test validates:
- Sierra Chart bridge connection
- Market data flow
- Service initialization
- Basic trading functionality (demo mode)

Run this before starting the full live trading system.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add MinhOS to path
sys.path.insert(0, str(Path(__file__).parent))

from client import MinhOSClient
from minhos.services.sierra_client import SierraClient, TradeCommand
from minhos.core.config import get_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def test_bridge_connection():
    """Test connection to Windows bridge"""
    logger.info("Testing Sierra Chart bridge connection...")
    
    config = get_config()
    bridge_url = f"http://{config.get('BRIDGE_HOSTNAME', 'cthinkpad')}:8765"
    
    try:
        async with MinhOSClient(bridge_url) as client:
            # Test health
            health = await client.health_check()
            logger.info(f"Bridge Health: {health}")
            
            if health.get('status') != 'healthy':
                raise Exception(f"Bridge unhealthy: {health}")
            
            # Test market data
            market_data = await client.get_market_data()
            if market_data:
                logger.info(f"Market Data: {market_data['symbol']} @ ${market_data['price']}")
            else:
                logger.warning("No market data available")
            
            logger.info("✅ Bridge connection test PASSED")
            return True
    
    except Exception as e:
        logger.error(f"❌ Bridge connection test FAILED: {e}")
        return False

async def test_sierra_client():
    """Test Sierra Client service"""
    logger.info("Testing Sierra Client service...")
    
    try:
        # Create sierra client
        sierra_client = SierraClient()
        await sierra_client.start()
        
        # Wait for connection
        await asyncio.sleep(5)
        
        # Check status
        status = sierra_client.get_status()
        logger.info(f"Sierra Client Status: {status}")
        
        if status['connection_state'] != 'connected':
            raise Exception(f"Sierra client not connected: {status}")
        
        # Test market data
        market_data = await sierra_client.get_market_data()
        if market_data:
            logger.info(f"Sierra Market Data: {market_data.symbol} @ ${market_data.price}")
        
        # Clean shutdown
        await sierra_client.stop()
        
        logger.info("✅ Sierra Client test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Sierra Client test FAILED: {e}")
        return False

async def test_demo_trade():
    """Test demo trade execution"""
    logger.info("Testing demo trade execution...")
    
    try:
        async with MinhOSClient("http://cthinkpad:8765") as client:
            # Test trade command
            trade_result = await client.execute_trade("BUY", "NQU25-CME", 1)
            logger.info(f"Trade Result: {trade_result}")
            
            if 'command_id' in trade_result:
                # Wait and check status
                await asyncio.sleep(2)
                
                status = await client.get_trade_status(trade_result['command_id'])
                logger.info(f"Trade Status: {status}")
                
                if status.get('status') in ['FILLED', 'REJECTED']:
                    logger.info("✅ Trade execution test PASSED")
                    return True
            
            logger.warning("⚠️  Trade execution unclear")
            return False
    
    except Exception as e:
        logger.error(f"❌ Trade execution test FAILED: {e}")
        return False

async def run_integration_tests():
    """Run all integration tests"""
    logger.info("🧪 Starting MinhOS v3 Integration Tests")
    logger.info("="*50)
    
    tests = [
        ("Bridge Connection", test_bridge_connection),
        ("Sierra Client Service", test_sierra_client),
        ("Demo Trade Execution", test_demo_trade)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🔬 Running: {test_name}")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - System ready for live trading!")
    else:
        logger.error("💥 SOME TESTS FAILED - Check configuration before going live")
    
    return passed == total

if __name__ == "__main__":
    async def main():
        success = await run_integration_tests()
        sys.exit(0 if success else 1)
    
    asyncio.run(main())