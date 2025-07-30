#!/usr/bin/env python3
"""
Comprehensive MinhOS System Health Check
Tests all components after bridge migration
"""

import requests
import json
import time
from datetime import datetime

def test_component(name, url, expected_status=200):
    """Test a system component"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {name}: HEALTHY")
            return True, response.json() if response.content else {}
        else:
            print(f"⚠️  {name}: Status {response.status_code}")
            return False, {}
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False, {}

def main():
    print("🚀 MinhOS System Health Check")
    print("=" * 50)
    
    results = {}
    
    # 1. Bridge Connection (MaryPC)
    print("\n1. Testing Bridge Connection:")
    bridge_healthy, bridge_data = test_component(
        "MaryPC Bridge", 
        "http://100.123.37.79:8765/health"
    )
    results['bridge'] = bridge_healthy
    
    if bridge_healthy:
        # Test market data from bridge
        market_healthy, market_data = test_component(
            "Bridge Market Data", 
            "http://100.123.37.79:8765/api/market_data"
        )
        if market_data:
            nq_price = market_data.get('NQU25-CME', {}).get('price', 'N/A')
            print(f"   Current NQ Price: ${nq_price}")
    
    # 2. MinhOS Core Services
    print("\n2. Testing MinhOS Services:")
    minhos_healthy, minhos_data = test_component(
        "MinhOS API", 
        "http://localhost:8888/api/status"
    )
    results['minhos_api'] = minhos_healthy
    
    if minhos_healthy:
        services = minhos_data.get('services', {})
        for service, status in services.items():
            health = "✅" if status.get('health') else "❌"
            print(f"   {health} {service}")
    
    # 3. ML Systems
    print("\n3. Testing ML Systems:")
    ml_healthy, ml_data = test_component(
        "ML Status API", 
        "http://localhost:8888/api/ml/status"
    )
    results['ml_system'] = ml_healthy
    
    if ml_healthy:
        lstm = "✅" if ml_data.get('lstm_enabled') else "❌"
        ensemble = "✅" if ml_data.get('ensemble_enabled') else "❌" 
        kelly = "✅" if ml_data.get('kelly_enabled') else "❌"
        print(f"   {lstm} LSTM Model")
        print(f"   {ensemble} Ensemble Models") 
        print(f"   {kelly} Kelly Criterion")
        print(f"   Total Predictions: {ml_data.get('total_predictions', 0)}")
    
    # 4. Dashboard Access
    print("\n4. Testing Dashboard:")
    dashboard_healthy, _ = test_component(
        "Main Dashboard", 
        "http://localhost:8888/",
        expected_status=200
    )
    results['dashboard'] = dashboard_healthy
    
    # 5. Data Flow Test
    print("\n5. Testing Data Flow:")
    try:
        # Compare bridge data with MinhOS data
        bridge_resp = requests.get("http://100.123.37.79:8765/api/market_data", timeout=5)
        minhos_resp = requests.get("http://localhost:8888/api/status", timeout=5)
        
        if bridge_resp.status_code == 200 and minhos_resp.status_code == 200:
            bridge_data = bridge_resp.json()
            minhos_data = minhos_resp.json()
            
            bridge_price = bridge_data.get('NQU25-CME', {}).get('price', 0)
            minhos_price = minhos_data.get('market', {}).get('price', 0)
            
            if abs(bridge_price - minhos_price) < 1.0:  # Within $1
                print("✅ Data Flow: Bridge → MinhOS working")
                results['data_flow'] = True
            else:
                print(f"⚠️  Data Flow: Price mismatch (${bridge_price} vs ${minhos_price})")
                results['data_flow'] = False
        else:
            print("❌ Data Flow: Cannot compare data sources")
            results['data_flow'] = False
            
    except Exception as e:
        print(f"❌ Data Flow: ERROR - {e}")
        results['data_flow'] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SYSTEM HEALTH SUMMARY")
    print("=" * 50)
    
    total_components = len(results)
    healthy_components = sum(results.values())
    health_percentage = (healthy_components / total_components) * 100
    
    print(f"Overall Health: {healthy_components}/{total_components} ({health_percentage:.1f}%)")
    
    if health_percentage >= 90:
        print("🎉 SYSTEM STATUS: EXCELLENT")
    elif health_percentage >= 75:
        print("✅ SYSTEM STATUS: GOOD") 
    elif health_percentage >= 50:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
    else:
        print("❌ SYSTEM STATUS: CRITICAL ISSUES")
    
    # Recommendations
    print("\n📝 RECOMMENDATIONS:")
    if not results.get('bridge'):
        print("- Check MaryPC bridge connection")
    if not results.get('ml_system'):
        print("- ML models may need initialization")
    if not results.get('data_flow'):
        print("- Verify data pipeline between bridge and MinhOS")
    
    if all(results.values()):
        print("- System is operating optimally! ✨")
        print("- Ready for live trading operations")
    
    return results

if __name__ == "__main__":
    main()