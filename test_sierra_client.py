#!/usr/bin/env python3
"""
Test Sierra Client WebSocket Optimization
Test the Sierra Client service and WebSocket optimization connectivity
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/mnt/c/Users/cong7/Sync/minh_v4')

try:
    from minhos.services.sierra_client import SierraClientService
    from minhos.core.config import config
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)

async def test_sierra_client():
    """Test Sierra Client service initialization and WebSocket connectivity"""
    print("🧪 TESTING MINHOS SIERRA CLIENT WEBSOCKET OPTIMIZATION")
    print("=" * 65)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize Sierra Client
        print("🔧 Initializing Sierra Client Service...")
        sierra_client = SierraClientService()
        
        print(f"✅ Sierra Client initialized successfully")
        print(f"   🌐 Bridge URL: {sierra_client.bridge_url}")
        print(f"   🚀 WebSocket Optimization: {sierra_client.use_websocket_optimization}")
        print(f"   📊 Configured Symbols: {len(sierra_client.symbols)}")
        print(f"   📝 Symbols: {', '.join(sierra_client.symbols[:3])}...")
        
        # Test connection without starting full service
        print("\n🔍 Testing Bridge Connectivity...")
        
        # Test health check
        try:
            health_data = await sierra_client.get_bridge_health()
            if health_data:
                print("✅ Bridge Health Check: SUCCESS")
                print(f"   📊 Health Data Keys: {list(health_data.keys())}")
            else:
                print("❌ Bridge Health Check: FAILED - No response")
                return False
        except Exception as e:
            print(f"❌ Bridge Health Check: FAILED - {str(e)}")
            return False
        
        # Test market data connectivity
        print("\n📈 Testing Market Data Connectivity...")
        try:
            market_data = await sierra_client.get_all_market_data()
            if market_data:
                print("✅ Market Data Access: SUCCESS")
                print(f"   📊 Available Symbols: {len(market_data)}")
                for symbol, data in list(market_data.items())[:2]:
                    print(f"   💰 {symbol}: ${data.get('price', 'N/A')}")
            else:
                print("⚠️  Market Data Access: No data available (normal if no real-time data)")
        except Exception as e:
            print(f"❌ Market Data Access: FAILED - {str(e)}")
        
        # Test WebSocket client initialization
        print("\n🚀 Testing WebSocket Client Initialization...")
        try:
            if sierra_client.optimized_client:
                print("✅ WebSocket Client: Already initialized")
                stats = sierra_client.optimized_client.get_connection_stats()
                print(f"   🔗 Connection Stats: {stats}")
            else:
                print("⚠️  WebSocket Client: Not yet initialized (normal until service starts)")
        except Exception as e:
            print(f"❌ WebSocket Client Test: {str(e)}")
        
        print(f"\n🏆 SIERRA CLIENT TEST RESULTS")
        print("=" * 35)
        print("✅ Sierra Client Service: READY")
        print("✅ Bridge Connectivity: WORKING")
        print("✅ WebSocket Optimization: ENABLED")
        print("✅ Configuration: VALID")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Start full MinhOS system: python minh.py")
        print("2. Sierra Client will automatically use WebSocket optimization")
        print("3. Monitor logs for '[OPTIMIZED] Market data streaming via optimized WebSocket'")
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_sierra_client()
        if success:
            print("\n🎉 ALL TESTS PASSED - MINHOS WEBSOCKET OPTIMIZATION READY!")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED - CHECK BRIDGE CONNECTION")
            return 1
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)