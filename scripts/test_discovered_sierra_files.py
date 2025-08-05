#!/usr/bin/env python3
"""
Test Discovered Sierra Chart Files
==================================

Tests access to the actual Sierra Chart files discovered on Windows.
"""

import requests

def test_sierra_files():
    """Test access to discovered Sierra Chart files"""
    bridge_url = "http://marypc:8765"
    
    print("🧪 Testing Discovered Sierra Chart Files")
    print("=" * 50)
    
    # Files discovered from Windows investigation
    test_files = {
        "Daily Files (.dly)": [
            "NQU25-CME.dly",  # 28KB - NASDAQ Sep 2025
            "NQM25-CME.dly",  # 32KB - NASDAQ Jun 2025  
            "EURUSD.dly",     # 547KB - Forex
            "XAUUSD.dly"      # 1.1MB - Gold
        ],
        "Tick Files (.scid)": [
            "NQU25-CME.scid", # 403MB - NASDAQ Sep 2025 (active)
            "ESU25-CME.scid", # 866MB - S&P Sep 2025 (active)
            "AAPL.scid",      # 105MB - Apple stock
            "BTCUSD_PERP_BINANCE.scid" # 274MB - Bitcoin
        ]
    }
    
    for category, files in test_files.items():
        print(f"\n📂 {category}:")
        
        for filename in files:
            file_path = f"C:/SierraChart/Data/{filename}"
            
            try:
                response = requests.get(
                    f"{bridge_url}/api/file/read",
                    params={"path": file_path},
                    timeout=15
                )
                
                if response.status_code == 200:
                    content = response.text
                    lines = content.split('\n')
                    
                    print(f"  ✅ {filename}: {len(lines)} lines")
                    
                    # Show sample data for .dly files
                    if filename.endswith('.dly') and len(lines) > 1:
                        header = lines[0].strip() if lines else ""
                        first_data = lines[1].strip() if len(lines) > 1 else ""
                        last_data = lines[-2].strip() if len(lines) > 2 else ""
                        
                        print(f"     📊 Header: {header}")
                        print(f"     📈 First: {first_data}")
                        if last_data and last_data != first_data:
                            print(f"     📉 Last:  {last_data}")
                        
                elif response.status_code == 404:
                    print(f"  ❌ {filename}: File not found")
                else:
                    try:
                        error_data = response.json()
                        print(f"  ⚠️  {filename}: {error_data.get('error', 'Unknown error')}")
                    except:
                        print(f"  ⚠️  {filename}: Status {response.status_code}")
                        
            except requests.exceptions.Timeout:
                print(f"  ⏱️  {filename}: Request timeout (large file)")
            except Exception as e:
                print(f"  ❓ {filename}: Error - {e}")

if __name__ == "__main__":
    test_sierra_files()