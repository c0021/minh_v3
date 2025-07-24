#!/usr/bin/env python3
"""
Quick Test Script for Historical Data Integration
===============================================

Tests the complete historical data integration pipeline:
1. Bridge connectivity
2. File access API
3. Historical data service
4. Gap detection and filling

Usage: python3 scripts/test_historical_integration.py
"""

import asyncio
import sys
from pathlib import Path
import requests
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_bridge_connectivity():
    """Test basic bridge connectivity"""
    print("🔗 Testing bridge connectivity...")
    
    try:
        response = requests.get("http://trading-pc:8765/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bridge connected: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Bridge responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bridge connection failed: {e}")
        return False

def test_file_api():
    """Test file access API endpoints"""
    print("📂 Testing file access API...")
    
    try:
        # Test directory listing
        response = requests.get(
            "http://trading-pc:8765/api/file/list",
            params={"path": "C:\\SierraChart\\Data"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            print(f"✅ Directory listing: {len(files)} files found")
            
            # Look for .dly files
            dly_files = [f for f in files if f.get('extension') == '.dly']
            scid_files = [f for f in files if f.get('extension') == '.scid']
            
            print(f"  📊 Daily files (.dly): {len(dly_files)}")
            print(f"  📈 Tick files (.scid): {len(scid_files)}")
            
            if dly_files:
                # Test reading a .dly file
                test_file = dly_files[0]['name']
                print(f"  🔍 Testing read of {test_file}...")
                
                response = requests.get(
                    "http://trading-pc:8765/api/file/read",
                    params={"path": f"C:\\SierraChart\\Data\\{test_file}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    content = response.json().get('content', '')
                    lines = content.split('\n')
                    print(f"  ✅ File read successful: {len(lines)} lines")
                    if lines:
                        print(f"  📄 Header: {lines[0][:60]}...")
                else:
                    print(f"  ❌ File read failed: {response.status_code}")
            
            return True
        else:
            print(f"❌ File API responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File API test failed: {e}")
        return False

async def test_historical_service():
    """Test MinhOS historical data service"""
    print("🏛️ Testing MinhOS historical data service...")
    
    try:
        from minhos.services.sierra_historical_data import get_sierra_historical_service
        
        historical_service = get_sierra_historical_service()
        print("✅ Historical service imported successfully")
        
        # Test connection to bridge
        test_content = await historical_service._request_file_content("nonexistent.txt")
        if test_content is None:
            print("✅ Bridge connectivity test passed (expected null for nonexistent file)")
        else:
            print("⚠️ Unexpected response for nonexistent file")
        
        # Test historical data retrieval
        print("📊 Testing historical data retrieval...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        records = await historical_service.get_historical_data(
            "NQU25-CME", start_date, end_date, "daily"
        )
        
        print(f"✅ Historical data retrieval: {len(records)} records")
        
        if records:
            print(f"  📅 Date range: {records[0].timestamp.date()} to {records[-1].timestamp.date()}")
            print(f"  💰 Sample price: {records[-1].close}")
        
        return True
        
    except Exception as e:
        print(f"❌ Historical service test failed: {e}")
        return False

async def test_gap_detection():
    """Test gap detection functionality"""
    print("🔍 Testing gap detection...")
    
    try:
        from minhos.services.sierra_historical_data import get_sierra_historical_service
        
        historical_service = get_sierra_historical_service()
        gaps = await historical_service._detect_data_gaps("NQU25-CME")
        
        print(f"✅ Gap detection: {len(gaps)} gaps found")
        
        for i, (start, end) in enumerate(gaps[:3], 1):  # Show first 3 gaps
            duration = (end - start).days
            print(f"  Gap {i}: {start.date()} to {end.date()} ({duration} days)")
        
        return True
        
    except Exception as e:
        print(f"❌ Gap detection test failed: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("🎯 HISTORICAL DATA INTEGRATION TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("-"*60)
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Historical data integration is working!")
        print("\n🚀 Next steps:")
        print("  1. Restart MinhOS: python3 minh.py start")
        print("  2. Run backfill: python3 scripts/historical_data_manager.py backfill")
        print("  3. Check dashboard for historical data trends")
    else:
        print("⚠️  Some tests failed. Check the errors above and:")
        print("  1. Ensure Windows bridge is running with file access API")
        print("  2. Verify Tailscale connectivity")
        print("  3. Check Sierra Chart data directory access")
    
    print("="*60)

def main():
    """Run all integration tests"""
    print("🚀 MinhOS Historical Data Integration Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 1: Bridge connectivity
    results["Bridge Connectivity"] = test_bridge_connectivity()
    
    # Test 2: File access API
    if results["Bridge Connectivity"]:
        results["File Access API"] = test_file_api()
    else:
        results["File Access API"] = False
        print("⏭️  Skipping File API test (bridge not connected)")
    
    # Test 3: Historical service (async)
    try:
        results["Historical Service"] = asyncio.run(test_historical_service())
    except Exception as e:
        print(f"❌ Historical service test failed: {e}")
        results["Historical Service"] = False
    
    # Test 4: Gap detection (async)
    if results["Historical Service"]:
        try:
            results["Gap Detection"] = asyncio.run(test_gap_detection())
        except Exception as e:
            print(f"❌ Gap detection test failed: {e}")
            results["Gap Detection"] = False
    else:
        results["Gap Detection"] = False
        print("⏭️  Skipping Gap Detection test (historical service failed)")
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()