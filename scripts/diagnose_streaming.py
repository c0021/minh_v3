#!/usr/bin/env python3
"""
Diagnostic script to verify TCP optimizations and streaming performance
"""
import requests
import time
import statistics
import socket
import sys
from typing import List, Tuple


def test_tcp_settings():
    """Check if TCP optimizations are applied"""
    print("=== TCP Settings Check ===")
    
    # Check Linux TCP settings
    tcp_settings = {
        'net.ipv4.tcp_nodelay': '1',
        'net.ipv4.tcp_low_latency': '1',
        'net.ipv4.tcp_timestamps': '1'
    }
    
    if sys.platform.startswith('linux'):
        import subprocess
        for setting, expected in tcp_settings.items():
            try:
                result = subprocess.run(
                    ['sysctl', '-n', setting],
                    capture_output=True,
                    text=True
                )
                actual = result.stdout.strip()
                status = "✓" if actual == expected else "✗"
                print(f"{status} {setting}: {actual} (expected: {expected})")
            except Exception as e:
                print(f"✗ Could not check {setting}: {e}")
    else:
        print("Not on Linux - skipping sysctl checks")
    
    print()


def measure_latency(url: str, num_requests: int = 10) -> Tuple[List[float], float, float]:
    """Measure request latencies and return times, mean, and std dev"""
    times = []
    errors = 0
    
    for i in range(num_requests):
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                times.append(elapsed)
            else:
                errors += 1
                times.append(999)  # Penalty for errors
        except Exception as e:
            errors += 1
            times.append(999)
            if i == 0:  # Print error only on first failure
                print(f"Error: {e}")
    
    if times:
        mean = statistics.mean(times)
        stdev = statistics.stdev(times) if len(times) > 1 else 0
        return times, mean, stdev
    return [], 999, 0


def diagnose_connection(url: str = "http://marypc:8765/api/market_data"):
    """Comprehensive connection diagnostics"""
    print(f"Diagnosing connection to: {url}")
    print("=" * 60)
    
    # Test TCP settings
    test_tcp_settings()
    
    # Test 1: DNS Resolution
    print("=== DNS Resolution Test ===")
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname
        start = time.time()
        ip = socket.gethostbyname(hostname)
        dns_time = time.time() - start
        print(f"✓ {hostname} resolved to {ip} in {dns_time:.3f}s")
    except Exception as e:
        print(f"✗ DNS resolution failed: {e}")
        return
    
    print()
    
    # Test 2: Single request baseline
    print("=== Single Request Test ===")
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        single_time = time.time() - start
        
        if response.status_code == 200:
            print(f"✓ Single request: {single_time:.3f}s")
            print(f"  Response size: {len(response.content)} bytes")
            data = response.json()
            print(f"  Data preview: symbol={data.get('symbol', 'N/A')}, "
                  f"price={data.get('last_price', 'N/A')}")
        else:
            print(f"✗ Single request failed: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Single request failed: {e}")
        return
    
    print()
    
    # Test 3: Multiple requests WITHOUT session (problematic scenario)
    print("=== Testing WITHOUT Connection Pooling (Problematic) ===")
    times_no_pool, avg_no_pool, std_no_pool = measure_latency(url, 10)
    
    if avg_no_pool < 900:
        print(f"Average latency: {avg_no_pool:.3f}s (±{std_no_pool:.3f}s)")
        print(f"Min/Max: {min(times_no_pool):.3f}s / {max(times_no_pool):.3f}s")
        
        # Check for Nagle's Algorithm symptoms
        if avg_no_pool > 0.2:
            print("⚠️  High latency detected - possible Nagle's Algorithm issue")
    else:
        print("✗ Connection failed")
    
    print()
    
    # Test 4: Multiple requests WITH session (optimized)
    print("=== Testing WITH Connection Pooling (Optimized) ===")
    session = requests.Session()
    session.headers['Connection'] = 'keep-alive'
    
    times_pooled = []
    for i in range(10):
        try:
            start = time.time()
            response = session.get(url, timeout=5)
            elapsed = time.time() - start
            if response.status_code == 200:
                times_pooled.append(elapsed)
        except:
            times_pooled.append(999)
    
    session.close()
    
    if times_pooled and min(times_pooled) < 900:
        avg_pooled = statistics.mean(times_pooled)
        std_pooled = statistics.stdev(times_pooled) if len(times_pooled) > 1 else 0
        
        print(f"Average latency: {avg_pooled:.3f}s (±{std_pooled:.3f}s)")
        print(f"Min/Max: {min(times_pooled):.3f}s / {max(times_pooled):.3f}s")
    else:
        print("✗ Pooled connection failed")
        avg_pooled = 999
    
    print()
    
    # Test 5: Sustained 1Hz streaming test
    print("=== 1Hz Streaming Test (10 seconds) ===")
    session = requests.Session()
    stream_times = []
    last_timestamp = None
    unique_updates = 0
    
    print("Streaming", end="", flush=True)
    start_time = time.time()
    
    for i in range(10):
        req_start = time.time()
        try:
            response = session.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                timestamp = data.get('timestamp', data.get('time'))
                if timestamp != last_timestamp:
                    unique_updates += 1
                    last_timestamp = timestamp
                stream_times.append(time.time() - req_start)
                print(".", end="", flush=True)
            else:
                print("x", end="", flush=True)
        except:
            print("!", end="", flush=True)
        
        # Maintain 1Hz rate
        elapsed = time.time() - req_start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
    
    total_time = time.time() - start_time
    session.close()
    
    print()  # New line after dots
    
    if stream_times:
        avg_stream = statistics.mean(stream_times)
        print(f"✓ Completed in {total_time:.1f}s")
        print(f"  Average request time: {avg_stream:.3f}s")
        print(f"  Unique data updates: {unique_updates}/10")
        print(f"  Effective rate: {len(stream_times)/total_time:.2f} Hz")
    else:
        print("✗ Streaming test failed")
    
    print()
    
    # Results Summary
    print("=== RESULTS SUMMARY ===")
    
    if avg_no_pool < 900 and avg_pooled < 900:
        improvement = avg_no_pool / avg_pooled
        print(f"Performance improvement with pooling: {improvement:.1f}x")
        
        if avg_pooled < 0.1:
            print("✓ EXCELLENT: Latency is optimal for 1Hz streaming")
        elif avg_pooled < 0.2:
            print("✓ GOOD: Latency is acceptable for 1Hz streaming")
        else:
            print("⚠️  WARNING: Latency may cause issues with 1Hz streaming")
            print("   Apply TCP optimizations on both systems")
    else:
        print("✗ Connection tests failed")
    
    # Recommendations
    print("\n=== RECOMMENDATIONS ===")
    
    if avg_pooled > 0.2:
        print("1. Run TCP optimization scripts on both Windows and Linux:")
        print("   - Windows: Run tcp_optimize_windows.bat as Administrator")
        print("   - Linux: sudo ./tcp_optimize_linux.sh")
        print("2. Restart the Sierra Bridge API service")
        print("3. Use the OptimizedSierraClient for streaming")
    else:
        print("✓ Performance is optimal. Use OptimizedSierraClient for streaming.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnose Sierra Chart streaming connection')
    parser.add_argument(
        '--url', 
        default='http://marypc:8765/api/market_data',
        help='Sierra Bridge API URL (default: http://marypc:8765/api/market_data)'
    )
    
    args = parser.parse_args()
    
    try:
        diagnose_connection(args.url)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()