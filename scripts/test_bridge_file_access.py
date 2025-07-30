#!/usr/bin/env python3
"""
Test Bridge File Access API
===========================

Tests the existing bridge file access API to retrieve real Sierra Chart data.
"""

import requests
import json

def test_file_access():
    """Test bridge file access API"""
    bridge_url = "http://cthinkpad:8765"
    
    print("🌉 Testing Bridge File Access API")
    print("=" * 40)
    
    # Test various Sierra Chart file patterns
    test_files = [
        "C:/SierraChart/Data/NQU25.dly",
        "C:/SierraChart/Data/NQ 03-25.dly", 
        "C:/SierraChart/Data/ESU25.dly",
        "C:/SierraChart/Data/ES 09-25.dly"
    ]
    
    for file_path in test_files:
        print(f"\n📁 Testing: {file_path}")
        
        try:
            response = requests.get(
                f"{bridge_url}/api/file/read",
                params={"path": file_path},
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text
                lines = content.split('\n')
                print(f"  ✅ Success! File has {len(lines)} lines")
                if lines:
                    print(f"  📊 First line: {lines[0][:100]}")
                    if len(lines) > 1:
                        print(f"  📊 Last line: {lines[-2][:100]}")  # -2 because last is usually empty
                        
            elif response.status_code == 404:
                print(f"  ❌ File not found")
            else:
                try:
                    error_data = response.json()
                    print(f"  ⚠️  Status {response.status_code}: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"  ⚠️  Status {response.status_code}: {response.text[:100]}")
                    
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection failed to bridge")
            break
        except Exception as e:
            print(f"  ❓ Error: {e}")

if __name__ == "__main__":
    test_file_access()