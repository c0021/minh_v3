#!/usr/bin/env python3
"""
Bridge Optimization Endpoint Testing Script
Tests all Phase 2 optimization endpoints from local machine
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(name, url, description):
    """Test a single endpoint and return results"""
    print(f"\n🧪 Testing: {name}")
    print(f"   URL: {url}")
    print(f"   Description: {description}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code} - SUCCESS")
            
            # Parse JSON if possible
            try:
                data = response.json()
                
                # Show key metrics for important endpoints
                if 'api/bridge/stats' in url:
                    cache = data.get('file_cache', {})
                    ws = data.get('websocket_connections', {})
                    print(f"      📊 Cache Hit Rate: {cache.get('hit_rate', 0)*100:.1f}%")
                    print(f"      🔗 WebSocket Connections: {ws.get('total_connections', 0)}")
                    print(f"      📁 Cached Files: {cache.get('cached_files', 0)}")
                    
                elif 'health_monitoring' in url:
                    health = data.get('health', {})
                    circuit = data.get('circuit_breaker', {})
                    print(f"      💚 Health Score: {health.get('health_score', 0)}/100 ({health.get('status', 'unknown')})")
                    print(f"      🔒 Circuit Breaker: {circuit.get('state', 'unknown')}")
                    print(f"      🚀 Production Ready: {data.get('production_ready', False)}")
                    
                elif 'api/market_data' in url:
                    if isinstance(data, dict):
                        symbols = len(data.keys())
                        print(f"      📈 Active Symbols: {symbols}")
                        # Show first symbol data if available
                        if symbols > 0:
                            first_symbol = list(data.keys())[0]
                            symbol_data = data[first_symbol]
                            print(f"      💰 Sample ({first_symbol}): ${symbol_data.get('price', 0)}")
                            
                elif 'api/symbols' in url:
                    if isinstance(data, list):
                        print(f"      📊 Available Symbols: {len(data)}")
                        print(f"      📝 Symbols: {', '.join(data[:3])}...")
                        
            except json.JSONDecodeError:
                print(f"      📄 Response: {response.text[:100]}...")
                
        else:
            print(f"   ❌ Status: {response.status_code} - FAILED")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: {str(e)}")
        return False
        
    return True

def main():
    print("🎯 MINHOS BRIDGE OPTIMIZATION ENDPOINT TESTING")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Use Tailscale IP for cross-platform testing
    base_url = "http://100.85.224.58:8765"
    
    endpoints = [
        ("Health Check", f"{base_url}/health", "Basic health status"),
        ("Market Data", f"{base_url}/api/market_data", "Current market data"),
        ("Bridge Stats", f"{base_url}/api/bridge/stats", "Performance statistics"),
        ("Health Monitoring", f"{base_url}/api/bridge/health_monitoring", "Comprehensive health with circuit breaker"),
        ("Detailed Health", f"{base_url}/api/bridge/health_detailed", "Detailed health metrics"),
        ("Symbols API", f"{base_url}/api/symbols", "Available symbols"),
    ]
    
    successful_tests = 0
    total_tests = len(endpoints)
    
    for name, url, description in endpoints:
        if test_endpoint(name, url, description):
            successful_tests += 1
        time.sleep(0.5)  # Small delay between tests
    
    print(f"\n🏆 TEST RESULTS")
    print("=" * 30)
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    print(f"📊 Success Rate: {successful_tests/total_tests*100:.1f}%")
    
    print(f"\n🔗 WEBSOCKET ENDPOINTS")
    print(f"   🚀 Optimized: ws://localhost:8765/ws/live_data/{{symbol}}")
    print(f"   📡 Legacy: ws://localhost:8765/ws/market_data")
    
    print("\n✅ Bridge optimization endpoint testing complete!")
    
    if successful_tests == total_tests:
        print("🎉 ALL ENDPOINTS OPERATIONAL - READY FOR MINHOS INTEGRATION!")
        return True
    else:
        print("⚠️  Some endpoints failed - check bridge service status")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)