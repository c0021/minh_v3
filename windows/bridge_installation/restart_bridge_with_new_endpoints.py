#!/usr/bin/env python3
"""
Bridge Restart Script with New Endpoints
========================================

This script will:
1. Test current bridge endpoints
2. Provide instructions to restart the bridge on Windows
3. Verify the new endpoints are working

The MinhOS system expects these endpoints:
- /api/symbols (list of available symbols)
- /api/data/{symbol} (current market data for a symbol)
- /api/streaming/{symbol} (real-time streaming data)
"""

import requests
import time
import json
import subprocess

# Try different bridge URLs
BRIDGE_URLS = [
    "http://cthinkpad:8765",
    "http://localhost:8765", 
    "http://127.0.0.1:8765",
]

# Get Windows host IP from WSL
try:
    result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'default via' in line:
            windows_ip = line.split('via')[1].split()[0]
            BRIDGE_URLS.insert(0, f"http://{windows_ip}:8765")
            break
except:
    pass

BRIDGE_URL = BRIDGE_URLS[0]  # Default to first URL

def test_endpoint(url, description):
    """Test a specific endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}: {response.status_code}")
            return True, response.json()
        else:
            print(f"❌ {description}: {response.status_code}")
            return False, response.text
    except Exception as e:
        print(f"❌ {description}: Connection error - {e}")
        return False, str(e)

def main():
    print("=" * 60)
    print("Bridge Endpoint Diagnostic and Restart Instructions")
    print("=" * 60)
    
    # Find working bridge URL
    print(f"\n1. Testing Bridge URLs...")
    working_url = None
    for url in BRIDGE_URLS:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Bridge found at: {url}")
                working_url = url
                break
        except:
            print(f"❌ No bridge at: {url}")
    
    if not working_url:
        print("\n❌ Bridge not accessible at any URL. Please check bridge is running.")
        return
    
    global BRIDGE_URL
    BRIDGE_URL = working_url
    
    # Test current endpoints
    print(f"\n2. Testing Bridge Status at {BRIDGE_URL}...")
    test_endpoint(f"{BRIDGE_URL}/health", "Health Check")
    test_endpoint(f"{BRIDGE_URL}/status", "Status Check")
    
    print(f"\n3. Testing Required MinhOS Endpoints...")
    success1, data1 = test_endpoint(f"{BRIDGE_URL}/api/symbols", "Symbols API")
    success2, data2 = test_endpoint(f"{BRIDGE_URL}/api/data/NQU25-CME", "Data API")
    success3, data3 = test_endpoint(f"{BRIDGE_URL}/api/streaming/NQU25-CME", "Streaming API")
    
    if success1 and success2 and success3:
        print("\n🎉 ALL ENDPOINTS WORKING! Bridge restart successful.")
        print(f"\n📊 Sample Data:")
        if isinstance(data1, dict):
            print(f"   Symbols: {data1.get('symbols', [])}")
        if isinstance(data2, dict):
            print(f"   NQU25-CME Price: ${data2.get('price', 'N/A')}")
        if isinstance(data3, dict):
            print(f"   Streaming: {data3.get('streaming', False)}")
        
        print(f"\n✅ MinhOS can now connect to: {BRIDGE_URL}")
        
        # Check if config needs updating
        if "172.21.128.1" in BRIDGE_URL and "cthinkpad" not in BRIDGE_URL:
            print(f"\n⚠️  CONFIGURATION UPDATE NEEDED:")
            print(f"   The bridge is working at {BRIDGE_URL}")
            print(f"   But MinhOS is configured to use 'cthinkpad'")
            print(f"   Update config.py or set environment variable:")
            print(f"   export BRIDGE_HOSTNAME='172.21.128.1'")
        
        return
    
    print("\n3. Bridge Restart Instructions:")
    print("   The bridge.py file has been updated with the missing endpoints.")
    print("   To restart the bridge on Windows:")
    print("")
    print("   Option 1 - Using Command Prompt:")
    print("   1. Open Command Prompt as Administrator")
    print("   2. Navigate to: C:\\Users\\cong7\\Sync\\minh_v3\\windows\\bridge_installation")
    print("   3. Stop existing bridge: taskkill /f /im python.exe")
    print("   4. Start new bridge: start_bridge.bat")
    print("")
    print("   Option 2 - Using PowerShell:")
    print("   1. Open PowerShell as Administrator")
    print("   2. Navigate to: C:\\Users\\cong7\\Sync\\minh_v3\\windows\\bridge_installation")
    print("   3. Stop existing bridge: Get-Process python | Stop-Process -Force")
    print("   4. Start new bridge: .\\start_bridge.ps1")
    print("")
    print("   Option 3 - Manual restart:")
    print("   1. Find Python process in Task Manager and end it")
    print("   2. Double-click start_bridge.bat in File Explorer")
    print("")
    
    print("4. After restarting, run this script again to verify endpoints.")
    print("")
    print("5. The new endpoints will provide:")
    print("   - /api/symbols: List of available symbols for MinhOS")
    print("   - /api/data/{symbol}: Current market data for specific symbol") 
    print("   - /api/streaming/{symbol}: Streaming data configuration")

if __name__ == "__main__":
    main()