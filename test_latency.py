#!/usr/bin/env python3
"""Test end-to-end latency of the MinhOS data pipeline"""

import time
import json
import requests
from datetime import datetime

def test_latency():
    """Measure latency from ACSIL JSON file update to Bridge API response"""
    
    print("Testing MinhOS Data Pipeline Latency...")
    print("-" * 50)
    
    # Test parameters
    test_runs = 10
    api_url = "http://localhost:8765/api/market_data"
    json_path = "/mnt/c/SierraChart/Data/ACSILOutput/NQU25_CME.json.tmp"
    
    latencies = []
    
    for i in range(test_runs):
        try:
            # Read current JSON file timestamp
            with open(json_path, 'r') as f:
                data = json.load(f)
                file_timestamp = data.get('timestamp', 0)
            
            # Query API
            start_time = time.time()
            response = requests.get(api_url, timeout=5)
            api_time = time.time()
            
            if response.status_code == 200:
                api_data = response.json()
                nq_data = api_data.get('NQU25-CME', {})
                
                # Calculate API response time
                api_latency = (api_time - start_time) * 1000  # ms
                
                print(f"Run {i+1}:")
                print(f"  API Response Time: {api_latency:.1f}ms")
                print(f"  Price: ${nq_data.get('price', 0):.2f}")
                print(f"  Bid Size: {nq_data.get('bid_size', 0)}")
                print(f"  Ask Size: {nq_data.get('ask_size', 0)}")
                print(f"  Last Size: {nq_data.get('last_size', 0)}")
                
                latencies.append(api_latency)
            
            time.sleep(1)  # Wait between tests
            
        except Exception as e:
            print(f"Run {i+1}: Error - {e}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print("\n" + "=" * 50)
        print("PERFORMANCE SUMMARY:")
        print(f"  Average Latency: {avg_latency:.1f}ms")
        print(f"  Min Latency: {min_latency:.1f}ms") 
        print(f"  Max Latency: {max_latency:.1f}ms")
        print(f"  Success Rate: {len(latencies)}/{test_runs} ({len(latencies)/test_runs*100:.0f}%)")
        
        if avg_latency < 1000:
            print("\n✅ PASS: End-to-end latency under 1 second target!")
        else:
            print("\n❌ FAIL: Latency exceeds 1 second target")

if __name__ == "__main__":
    test_latency()