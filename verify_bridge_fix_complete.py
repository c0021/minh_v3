#!/usr/bin/env python3
"""
Complete Bridge Fix Verification
================================

This script verifies that the bridge API endpoints are fixed and MinhOS can connect properly.
"""

import asyncio
import requests
import json
from datetime import datetime

def test_all_endpoints():
    """Test all bridge endpoints that MinhOS needs"""
    bridge_url = "http://172.21.128.1:8765"
    
    print("=" * 70)
    print("BRIDGE API ENDPOINTS VERIFICATION - COMPLETE TEST")
    print("=" * 70)
    print(f"Testing bridge at: {bridge_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    endpoints = [
        ("/health", "Health Check"),
        ("/status", "Status Check"),
        ("/api/symbols", "Symbols API (NEW)"),
        ("/api/data/NQU25-CME", "Data API (NEW)"),
        ("/api/streaming/NQU25-CME", "Streaming API (NEW)"),
        ("/api/market_data", "Market Data API (Existing)"),
    ]
    
    results = {}
    
    print(f"\n🔍 Testing {len(endpoints)} endpoints...")
    print("-" * 70)
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{bridge_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {"status": "✅ PASS", "data": data}
                print(f"✅ {description:25} | Status: {response.status_code} | Data: {type(data).__name__}")
                
                # Show sample data for key endpoints
                if endpoint == "/api/symbols":
                    symbols = data.get('symbols', [])
                    print(f"   📊 Symbols: {len(symbols)} available - {symbols[:3]}...")
                elif endpoint == "/api/data/NQU25-CME":
                    price = data.get('price', 'N/A')
                    source = data.get('source', 'unknown')
                    print(f"   📊 NQU25-CME: ${price} from {source}")
                elif endpoint == "/api/streaming/NQU25-CME":
                    streaming = data.get('streaming', False)
                    websocket_url = data.get('websocket_url', 'N/A')
                    print(f"   📊 Streaming: {streaming}, WebSocket: {websocket_url}")
                    
            else:
                results[endpoint] = {"status": f"❌ FAIL ({response.status_code})", "data": None}
                print(f"❌ {description:25} | Status: {response.status_code}")
                
        except Exception as e:
            results[endpoint] = {"status": f"❌ ERROR", "data": str(e)}
            print(f"❌ {description:25} | Error: {str(e)[:50]}...")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if "✅" in r["status"])
    total = len(results)
    
    print(f"Endpoints Tested: {total}")
    print(f"Endpoints Passed: {passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL BRIDGE API ENDPOINTS WORKING!")
        print("✅ Bridge restart successful")
        print("✅ Missing endpoints added:")
        print("   - /api/symbols (returns symbol list)")
        print("   - /api/data/{symbol} (returns market data)")
        print("   - /api/streaming/{symbol} (returns streaming config)")
        print("\n🚀 MinhOS can now connect to bridge without 'Not Found' errors")
        
        print(f"\n📋 NEXT STEPS:")
        print("1. ✅ Bridge endpoints fixed")
        print("2. ✅ Config updated to use 172.21.128.1")
        print("3. 🔄 Start MinhOS services with: python3 minh.py")
        print("4. 🔄 Verify dashboard shows live data")
        
    else:
        print(f"\n⚠️  {total-passed} endpoints still failing")
        print("❌ Bridge may need additional troubleshooting")
    
    return passed == total

if __name__ == "__main__":
    success = test_all_endpoints()
    exit(0 if success else 1)