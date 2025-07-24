#!/usr/bin/env python3
"""
Test TCP Optimizations on Windows
Run this after applying tcp_optimize_windows.bat
"""

import socket
import time
import requests
import statistics
from datetime import datetime


def test_socket_options():
    """Test if TCP_NODELAY can be set on sockets"""
    print("=== Testing Socket Options ===")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Try to set TCP_NODELAY
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        value = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
        
        if value == 1:
            print("✓ TCP_NODELAY is enabled (Nagle's Algorithm disabled)")
        else:
            print("✗ TCP_NODELAY is not enabled")
            
        s.close()
    except Exception as e:
        print(f"✗ Socket test failed: {e}")
    
    print()


def test_local_api_performance():
    """Test local Bridge API performance"""
    print("=== Testing Local Bridge API Performance ===")
    
    api_url = "http://localhost:8765/api/market_data"
    
    # Test 1: Single request
    print("\n1. Single Request Test:")
    try:
        start = time.time()
        response = requests.get(api_url, timeout=5)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f"✓ Response time: {elapsed*1000:.1f}ms")
            print(f"  Status: {response.status_code}")
            print(f"  Size: {len(response.content)} bytes")
        else:
            print(f"✗ Request failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return
    
    # Test 2: Multiple requests without session
    print("\n2. Multiple Requests WITHOUT Session (10 requests):")
    times = []
    for i in range(10):
        try:
            start = time.time()
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  Request {i+1}: {elapsed*1000:.1f}ms")
        except:
            print(f"  Request {i+1}: Failed")
        time.sleep(0.1)
    
    if times:
        avg_time = statistics.mean(times) * 1000
        print(f"\n  Average: {avg_time:.1f}ms")
    
    # Test 3: Multiple requests with session
    print("\n3. Multiple Requests WITH Session (10 requests):")
    session = requests.Session()
    session.headers['Connection'] = 'keep-alive'
    
    times = []
    for i in range(10):
        try:
            start = time.time()
            response = session.get(api_url, timeout=5)
            if response.status_code == 200:
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"  Request {i+1}: {elapsed*1000:.1f}ms")
        except:
            print(f"  Request {i+1}: Failed")
        time.sleep(0.1)
    
    session.close()
    
    if times:
        avg_time = statistics.mean(times) * 1000
        print(f"\n  Average: {avg_time:.1f}ms")
        
        if avg_time < 50:
            print("\n✓ EXCELLENT: Performance is optimal for 1Hz streaming")
        elif avg_time < 100:
            print("\n✓ GOOD: Performance is acceptable for 1Hz streaming")
        else:
            print("\n⚠ WARNING: High latency detected. Check TCP optimizations.")


def test_continuous_streaming():
    """Test continuous 1Hz streaming"""
    print("\n=== Testing 1Hz Continuous Streaming (10 seconds) ===")
    
    api_url = "http://localhost:8765/api/market_data"
    session = requests.Session()
    
    print("Streaming", end="", flush=True)
    
    times = []
    errors = 0
    start_time = time.time()
    
    for i in range(10):
        req_start = time.time()
        try:
            response = session.get(api_url, timeout=2)
            if response.status_code == 200:
                times.append(time.time() - req_start)
                print(".", end="", flush=True)
            else:
                errors += 1
                print("x", end="", flush=True)
        except:
            errors += 1
            print("!", end="", flush=True)
        
        # Wait for next second
        elapsed = time.time() - req_start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
    
    total_time = time.time() - start_time
    session.close()
    
    print()  # New line
    
    if times:
        avg_time = statistics.mean(times) * 1000
        print(f"\n✓ Completed in {total_time:.1f}s")
        print(f"  Successful requests: {len(times)}/10")
        print(f"  Average latency: {avg_time:.1f}ms")
        print(f"  Errors: {errors}")
        
        if errors == 0 and avg_time < 100:
            print("\n✓ SUCCESS: 1Hz streaming is working perfectly!")
        elif errors > 0:
            print("\n⚠ WARNING: Some requests failed during streaming")
        else:
            print("\n⚠ WARNING: High latency during streaming")
    else:
        print("\n✗ FAILED: No successful requests")


def main():
    """Run all tests"""
    print("TCP Optimization Test for Windows")
    print("=================================")
    print(f"Time: {datetime.now()}")
    print()
    
    # Test socket options
    test_socket_options()
    
    # Test API performance
    test_local_api_performance()
    
    # Test continuous streaming
    test_continuous_streaming()
    
    print("\n=================================")
    print("Test complete!")
    print("\nIf you see high latency or errors:")
    print("1. Run tcp_optimize_windows.bat as Administrator")
    print("2. Restart the Bridge API service")
    print("3. Consider rebooting Windows")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")