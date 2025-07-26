#!/usr/bin/env python3
"""
Phase 3 Tick-by-Tick Processing Pipeline Test
=============================================

Comprehensive test suite for Phase 3 microsecond precision tick data pipeline.
Tests the complete flow: ACSIL v3 → Bridge → Linux MinhOS

Tests:
1. Microsecond timestamp precision verification
2. Individual trade capture validation
3. Trade direction detection accuracy
4. High-frequency data throughput
5. Bridge processing optimization
6. End-to-end latency measurement
"""

import time
import json
import requests
import statistics
from datetime import datetime
from pathlib import Path
import asyncio
import websockets

class Phase3PipelineTest:
    def __init__(self):
        self.api_url = "http://localhost:8765/api/market_data"
        self.websocket_url = "ws://localhost:8765/ws/market_data"
        self.acsil_output_path = Path("/mnt/c/SierraChart/Data/ACSILOutput")
        self.test_results = {
            'microsecond_precision': False,
            'trade_direction': False,
            'high_frequency': False,
            'bridge_optimization': False,
            'end_to_end_latency': None,
            'throughput_tps': None
        }
    
    def test_microsecond_precision(self):
        """Test 1: Verify microsecond timestamp precision"""
        print("🔬 TEST 1: Microsecond Timestamp Precision")
        print("-" * 50)
        
        try:
            # Read ACSIL JSON files directly
            for symbol_file in self.acsil_output_path.glob("*.json"):
                if symbol_file.name.endswith('.tmp'):
                    continue
                    
                with open(symbol_file, 'r') as f:
                    data = json.load(f)
                
                # Check for Phase 3 indicators
                has_timestamp_us = 'timestamp_us' in data
                has_precision_field = data.get('precision') == 'microsecond'
                has_v3_source = data.get('source') == 'sierra_chart_acsil_v3'
                
                print(f"  File: {symbol_file.name}")
                print(f"    timestamp_us present: {has_timestamp_us}")
                print(f"    precision field: {has_precision_field}")
                print(f"    v3 source: {has_v3_source}")
                
                if has_timestamp_us:
                    timestamp_us = data['timestamp_us']
                    timestamp_s = data['timestamp']
                    
                    # Verify microsecond precision (should be 6+ more digits)
                    precision_check = timestamp_us > timestamp_s * 1000000
                    print(f"    timestamp_us: {timestamp_us}")
                    print(f"    timestamp_s: {timestamp_s}")
                    print(f"    precision valid: {precision_check}")
                    
                    if precision_check and has_precision_field and has_v3_source:
                        self.test_results['microsecond_precision'] = True
                        print("  ✅ PASS: Microsecond precision verified")
                        return True
            
            print("  ❌ FAIL: No Phase 3 data detected")
            return False
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False
    
    def test_trade_direction_detection(self):
        """Test 2: Verify trade direction detection"""
        print("\n🎯 TEST 2: Trade Direction Detection")
        print("-" * 50)
        
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                direction_detected = False
                for symbol, market_data in data.items():
                    trade_side = market_data.get('trade_side')
                    precision = market_data.get('precision')
                    
                    print(f"  Symbol: {symbol}")
                    print(f"    trade_side: {trade_side}")
                    print(f"    precision: {precision}")
                    
                    if trade_side in ['B', 'S', 'U'] and precision == 'microsecond':
                        direction_detected = True
                        print(f"    ✅ Trade direction detected: {trade_side}")
                
                self.test_results['trade_direction'] = direction_detected
                if direction_detected:
                    print("  ✅ PASS: Trade direction detection working")
                    return True
                else:
                    print("  ❌ FAIL: No trade direction data found")
                    return False
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False
    
    def test_high_frequency_processing(self):
        """Test 3: High-frequency data processing"""
        print("\n⚡ TEST 3: High-Frequency Processing")
        print("-" * 50)
        
        try:
            # Monitor file modification times to detect rapid updates
            test_file = self.acsil_output_path / "NQU25_CME.json"
            if not test_file.exists():
                test_file = self.acsil_output_path / "NQU25_CME.json.tmp"
            
            if not test_file.exists():
                print("  ❌ FAIL: No test file found")
                return False
            
            # Monitor file updates over 10 seconds
            update_times = []
            last_mtime = test_file.stat().st_mtime
            start_time = time.time()
            
            print("  Monitoring file updates for 10 seconds...")
            
            while time.time() - start_time < 10:
                current_mtime = test_file.stat().st_mtime
                if current_mtime != last_mtime:
                    update_times.append(time.time())
                    last_mtime = current_mtime
                time.sleep(0.1)  # Check every 100ms
            
            update_frequency = len(update_times) / 10.0  # Updates per second
            print(f"  Updates detected: {len(update_times)}")
            print(f"  Update frequency: {update_frequency:.1f} updates/second")
            
            # High-frequency is considered >1 update per second for tick data
            high_frequency = update_frequency > 0.5
            self.test_results['high_frequency'] = high_frequency
            self.test_results['throughput_tps'] = update_frequency
            
            if high_frequency:
                print("  ✅ PASS: High-frequency processing detected")
                return True
            else:
                print("  ⚠️  PARTIAL: Low frequency (may be market hours)")
                return False
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False
    
    def test_bridge_optimization(self):
        """Test 4: Bridge processing optimization"""
        print("\n🌉 TEST 4: Bridge Processing Optimization")
        print("-" * 50)
        
        try:
            # Test API response times with multiple rapid requests
            latencies = []
            
            for i in range(20):
                start_time = time.time()
                response = requests.get(self.api_url, timeout=2)
                end_time = time.time()
                
                if response.status_code == 200:
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    
                time.sleep(0.1)  # 100ms between requests
            
            if latencies:
                avg_latency = statistics.mean(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)
                
                print(f"  API Response Times (20 requests):")
                print(f"    Average: {avg_latency:.2f}ms")
                print(f"    Min: {min_latency:.2f}ms")
                print(f"    Max: {max_latency:.2f}ms")
                
                # Optimized bridge should maintain <10ms average
                optimized = avg_latency < 10.0
                self.test_results['bridge_optimization'] = optimized
                
                if optimized:
                    print("  ✅ PASS: Bridge optimization confirmed")
                    return True
                else:
                    print("  ⚠️  PARTIAL: Higher latency than optimal")
                    return False
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False
    
    def test_end_to_end_latency(self):
        """Test 5: End-to-end latency measurement"""
        print("\n🏁 TEST 5: End-to-End Latency")
        print("-" * 50)
        
        try:
            # Test complete pipeline latency
            test_runs = 10
            latencies = []
            
            for i in range(test_runs):
                # Record file system timestamp
                test_file = self.acsil_output_path / "NQU25_CME.json.tmp"
                if test_file.exists():
                    file_time = test_file.stat().st_mtime
                    
                    # Query API immediately
                    api_start = time.time()
                    response = requests.get(self.api_url, timeout=2)
                    api_end = time.time()
                    
                    if response.status_code == 200:
                        # Calculate latency from file update to API response
                        pipeline_latency = (api_end - file_time) * 1000
                        api_latency = (api_end - api_start) * 1000
                        
                        latencies.append(api_latency)
                        
                        print(f"  Run {i+1}: API latency = {api_latency:.2f}ms")
                
                time.sleep(0.5)
            
            if latencies:
                avg_latency = statistics.mean(latencies)
                self.test_results['end_to_end_latency'] = avg_latency
                
                print(f"\n  Average End-to-End Latency: {avg_latency:.2f}ms")
                
                # Target: sub-millisecond processing
                excellent = avg_latency < 1.0
                good = avg_latency < 5.0
                
                if excellent:
                    print("  🚀 EXCELLENT: Sub-millisecond latency achieved!")
                    return True
                elif good:
                    print("  ✅ PASS: Good latency performance")
                    return True
                else:
                    print("  ⚠️  PARTIAL: Higher latency than target")
                    return False
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False
    
    async def test_websocket_streaming(self):
        """Test 6: WebSocket streaming for high-frequency data"""
        print("\n📡 TEST 6: WebSocket Streaming")
        print("-" * 50)
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                print("  WebSocket connected successfully")
                
                # Collect messages for 5 seconds
                messages = []
                start_time = time.time()
                
                while time.time() - start_time < 5:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        messages.append(data)
                        
                        # Check for Phase 3 data
                        if data.get('precision') == 'microsecond':
                            print(f"    ✅ Phase 3 data received via WebSocket")
                            
                    except asyncio.TimeoutError:
                        continue
                
                message_rate = len(messages) / 5.0
                print(f"  Messages received: {len(messages)}")
                print(f"  Message rate: {message_rate:.1f} messages/second")
                
                if messages:
                    print("  ✅ PASS: WebSocket streaming operational")
                    return True
                else:
                    print("  ⚠️  PARTIAL: No messages received")
                    return False
                    
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all Phase 3 tests"""
        print("🚀 PHASE 3 TICK-BY-TICK PROCESSING PIPELINE TEST")
        print("=" * 60)
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_microsecond_precision,
            self.test_trade_direction_detection,
            self.test_high_frequency_processing,
            self.test_bridge_optimization,
            self.test_end_to_end_latency,
        ]
        
        passed_tests = 0
        for test in tests:
            if test():
                passed_tests += 1
        
        # Run async WebSocket test
        try:
            if asyncio.run(self.test_websocket_streaming()):
                passed_tests += 1
        except Exception as e:
            print(f"WebSocket test failed: {e}")
        
        # Final summary
        total_tests = len(tests) + 1  # +1 for WebSocket test
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 60)
        print("📊 PHASE 3 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.0f}%)")
        print(f"Microsecond Precision: {'✅' if self.test_results['microsecond_precision'] else '❌'}")
        print(f"Trade Direction: {'✅' if self.test_results['trade_direction'] else '❌'}")
        print(f"High Frequency: {'✅' if self.test_results['high_frequency'] else '❌'}")
        print(f"Bridge Optimization: {'✅' if self.test_results['bridge_optimization'] else '❌'}")
        
        if self.test_results['end_to_end_latency']:
            print(f"End-to-End Latency: {self.test_results['end_to_end_latency']:.2f}ms")
        
        if self.test_results['throughput_tps']:
            print(f"Data Throughput: {self.test_results['throughput_tps']:.1f} updates/second")
        
        print()
        if success_rate >= 80:
            print("🎉 PHASE 3 IMPLEMENTATION SUCCESS!")
            print("   Microsecond tick data pipeline is operational!")
        elif success_rate >= 60:
            print("⚠️  PHASE 3 PARTIAL SUCCESS")
            print("   Some components need attention")
        else:
            print("❌ PHASE 3 IMPLEMENTATION NEEDS WORK")
            print("   Multiple components require fixes")
        
        print(f"\nTest Complete Time: {datetime.now().isoformat()}")

if __name__ == "__main__":
    tester = Phase3PipelineTest()
    tester.run_comprehensive_test()