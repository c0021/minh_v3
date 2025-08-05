#!/usr/bin/env python3
"""
Force Bridge to Update Market Data
This script will trigger the bridge to re-read SCID files
"""
import requests
import json
import time

BRIDGE_URL = "http://localhost:8765"
SYMBOLS = ["NQU25-CME", "ESU25-CME", "VIX_CGI"]

def main():
    print("=== Forcing Bridge Market Data Update ===\n")
    
    # Check bridge health first
    try:
        health = requests.get(f"{BRIDGE_URL}/health", timeout=5)
        print(f"✓ Bridge is healthy: {health.json()}")
    except:
        print("✗ Bridge is not responding!")
        return
    
    print("\nCurrent market data status:")
    for symbol in SYMBOLS:
        try:
            # Try to get data - this might trigger a read
            response = requests.get(f"{BRIDGE_URL}/api/data/{symbol}", timeout=5)
            data = response.json()
            print(f"\n{symbol}:")
            print(f"  Price: {data.get('last_price', 'N/A')}")
            print(f"  Volume: {data.get('volume', 'N/A')}")
            print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
        except Exception as e:
            print(f"\n{symbol}: Error - {e}")
    
    print("\nChecking SCID file info:")
    for symbol in SYMBOLS:
        try:
            # Check when SCID file was last modified
            file_info = requests.get(
                f"{BRIDGE_URL}/api/file/info",
                params={"path": f"C:\\SierraChart\\Data\\{symbol}.scid"},
                timeout=5
            )
            info = file_info.json()
            if info.get('exists'):
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(info['modified']))
                print(f"{symbol}.scid - Last modified: {mod_time}")
            else:
                print(f"{symbol}.scid - File not found")
        except Exception as e:
            print(f"{symbol}.scid - Error: {e}")
    
    print("\nAttempting to trigger file monitoring...")
    # Touch a file to trigger the watcher
    try:
        # List files to potentially trigger a refresh
        files = requests.get(
            f"{BRIDGE_URL}/api/file/list",
            params={"path": "C:\\SierraChart\\Data"},
            timeout=5
        )
        print(f"✓ Found {len(files.json().get('files', []))} files in data directory")
    except Exception as e:
        print(f"✗ Error listing files: {e}")
    
    print("\nChecking for ACSIL JSON data:")
    for symbol in SYMBOLS:
        try:
            # Check ACSIL output
            clean_symbol = symbol.replace("-", "_")
            response = requests.get(
                f"{BRIDGE_URL}/api/file/read",
                params={"path": f"C:\\SierraChart\\Data\\ACSILOutput\\{clean_symbol}.json"},
                timeout=5
            )
            if response.status_code == 200:
                content = response.json().get('content', '')
                if content:
                    data = json.loads(content)
                    print(f"\n{clean_symbol}.json (ACSIL):")
                    print(f"  Price: {data.get('price', 'N/A')}")
                    print(f"  Volume: {data.get('volume', 'N/A')}")
                    print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
        except Exception as e:
            print(f"{clean_symbol}.json - Error: {e}")

if __name__ == "__main__":
    main()