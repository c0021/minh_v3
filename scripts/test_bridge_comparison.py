#!/usr/bin/env python3
"""
Bridge Data Quality Comparison Tool
Tests and compares data from multiple Sierra Chart bridge instances
"""
import asyncio
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import aiohttp
import requests
from collections import defaultdict
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BRIDGE_HOSTNAME, BRIDGE_PORT, BRIDGE_IPS

class BridgeComparator:
    def __init__(self):
        # Use the primary bridge from config and test against fallback IPs
        self.bridges = {
            'primary': {
                'ip': BRIDGE_HOSTNAME,
                'port': BRIDGE_PORT,
                'name': f'Primary ({BRIDGE_HOSTNAME})'
            }
        }
        
        # Add fallback bridges for comparison if different from primary
        for i, ip in enumerate(BRIDGE_IPS[:2]):
            if ip != BRIDGE_HOSTNAME:
                self.bridges[f'fallback_{i}'] = {
                    'ip': ip,
                    'port': BRIDGE_PORT,
                    'name': f'Fallback {i+1} ({ip})'
                }
        
        self.test_results = defaultdict(dict)
        
    async def test_bridge(self, bridge_key: str, bridge_info: Dict) -> Dict:
        """Test a single bridge for various metrics"""
        base_url = f"http://{bridge_info['ip']}:{bridge_info['port']}"
        results = {
            'name': bridge_info['name'],
            'ip': bridge_info['ip'],
            'reachable': False,
            'latency_ms': None,
            'health_status': None,
            'market_data': None,
            'data_freshness': None,
            'tick_count': None,
            'update_frequency': None,
            'errors': []
        }
        
        print(f"\n🔍 Testing {bridge_info['name']} ({bridge_info['ip']}:{bridge_info['port']})...")
        
        # Test 1: Basic connectivity and latency
        try:
            latencies = []
            for _ in range(5):
                start = time.time()
                response = requests.get(f"{base_url}/health", timeout=5)
                latency = (time.time() - start) * 1000
                latencies.append(latency)
                
            results['reachable'] = True
            results['latency_ms'] = statistics.mean(latencies)
            results['latency_std'] = statistics.stdev(latencies) if len(latencies) > 1 else 0
            print(f"✅ Reachable - Avg latency: {results['latency_ms']:.1f}ms (±{results['latency_std']:.1f}ms)")
        except Exception as e:
            results['errors'].append(f"Connectivity: {str(e)}")
            print(f"❌ Not reachable: {e}")
            return results
            
        # Test 2: Health status
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            results['health_status'] = response.json()
            print(f"✅ Health check passed")
        except Exception as e:
            results['errors'].append(f"Health check: {str(e)}")
            print(f"⚠️  Health check failed: {e}")
            
        # Test 3: Market data quality
        try:
            response = requests.get(f"{base_url}/api/market_data", timeout=5)
            market_data = response.json()
            
            if market_data:
                # Check data freshness
                symbol_data = list(market_data.values())[0] if market_data else None
                if symbol_data and 'timestamp' in symbol_data:
                    data_time = datetime.fromisoformat(symbol_data['timestamp'].replace('Z', '+00:00'))
                    freshness = (datetime.now() - data_time).total_seconds()
                    results['data_freshness'] = freshness
                    print(f"✅ Data freshness: {freshness:.1f} seconds old")
                
                results['market_data'] = market_data
                results['symbol_count'] = len(market_data)
                print(f"✅ Market data: {len(market_data)} symbols available")
        except Exception as e:
            results['errors'].append(f"Market data: {str(e)}")
            print(f"⚠️  Market data error: {e}")
            
        # Test 4: Real-time data stream (WebSocket test)
        try:
            print("🔄 Testing real-time data stream...")
            tick_counts = await self.test_websocket_stream(base_url)
            results['tick_count'] = tick_counts
            results['update_frequency'] = sum(tick_counts.values()) / len(tick_counts) if tick_counts else 0
            print(f"✅ Real-time stream: {sum(tick_counts.values())} ticks in 10s")
        except Exception as e:
            results['errors'].append(f"WebSocket stream: {str(e)}")
            print(f"⚠️  Real-time stream error: {e}")
            
        # Test 5: File access (historical data)
        try:
            response = requests.get(f"{base_url}/api/file/list?path=C:/SierraChart/Data", timeout=5)
            if response.status_code == 200:
                file_data = response.json()
                results['historical_files'] = file_data.get('count', 0)
                print(f"✅ Historical data access: {results['historical_files']} files available")
        except Exception as e:
            results['errors'].append(f"File access: {str(e)}")
            print(f"⚠️  Historical data access error: {e}")
            
        return results
        
    async def test_websocket_stream(self, base_url: str, duration: int = 10) -> Dict[str, int]:
        """Test WebSocket stream for real-time data quality"""
        tick_counts = defaultdict(int)
        ws_url = base_url.replace('http://', 'ws://') + '/ws/market_data'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url, timeout=5) as ws:
                    end_time = time.time() + duration
                    
                    while time.time() < end_time:
                        try:
                            msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(msg.data)
                                if 'symbol' in data:
                                    tick_counts[data['symbol']] += 1
                        except asyncio.TimeoutError:
                            continue
                        except Exception:
                            break
        except Exception:
            pass
            
        return dict(tick_counts)
        
    def analyze_results(self, results: Dict[str, Dict]) -> Dict:
        """Analyze and compare test results"""
        analysis = {
            'recommendation': None,
            'winner': None,
            'comparison': {},
            'scores': {}
        }
        
        # Calculate scores for each bridge
        for bridge_key, result in results.items():
            score = 0
            max_score = 0
            
            # Connectivity (25 points)
            max_score += 25
            if result['reachable']:
                score += 25
                
            # Latency (25 points - lower is better)
            max_score += 25
            if result['latency_ms'] is not None:
                if result['latency_ms'] < 10:
                    score += 25
                elif result['latency_ms'] < 50:
                    score += 20
                elif result['latency_ms'] < 100:
                    score += 15
                elif result['latency_ms'] < 200:
                    score += 10
                else:
                    score += 5
                    
            # Data freshness (20 points)
            max_score += 20
            if result['data_freshness'] is not None:
                if result['data_freshness'] < 1:
                    score += 20
                elif result['data_freshness'] < 5:
                    score += 15
                elif result['data_freshness'] < 10:
                    score += 10
                else:
                    score += 5
                    
            # Update frequency (20 points)
            max_score += 20
            if result['update_frequency'] is not None:
                if result['update_frequency'] > 10:
                    score += 20
                elif result['update_frequency'] > 5:
                    score += 15
                elif result['update_frequency'] > 1:
                    score += 10
                else:
                    score += 5
                    
            # Error count (10 points)
            max_score += 10
            error_penalty = len(result['errors']) * 2
            score += max(0, 10 - error_penalty)
            
            analysis['scores'][bridge_key] = {
                'score': score,
                'max_score': max_score,
                'percentage': (score / max_score) * 100 if max_score > 0 else 0
            }
            
        # Determine winner
        sorted_bridges = sorted(analysis['scores'].items(), 
                              key=lambda x: x[1]['percentage'], 
                              reverse=True)
        
        if sorted_bridges:
            winner_key = sorted_bridges[0][0]
            analysis['winner'] = results[winner_key]['name']
            
            # Generate recommendation
            winner_score = sorted_bridges[0][1]['percentage']
            if len(sorted_bridges) > 1:
                runner_up_score = sorted_bridges[1][1]['percentage']
                
                if winner_score > 90:
                    analysis['recommendation'] = f"Strongly recommend {analysis['winner']}"
                elif winner_score > 75 and (winner_score - runner_up_score) > 10:
                    analysis['recommendation'] = f"Recommend {analysis['winner']}"
                elif (winner_score - runner_up_score) < 5:
                    analysis['recommendation'] = "Both bridges perform similarly"
                else:
                    analysis['recommendation'] = f"Slightly prefer {analysis['winner']}"
                    
        return analysis
        
    def print_comparison_table(self, results: Dict[str, Dict], analysis: Dict):
        """Print a formatted comparison table"""
        print("\n" + "="*80)
        print("📊 BRIDGE COMPARISON RESULTS")
        print("="*80)
        
        # Get bridge keys dynamically
        bridge_keys = list(results.keys())
        
        # Header - use actual bridge names
        if len(bridge_keys) >= 2:
            print(f"\n{'Metric':<25} {self.bridges[bridge_keys[0]]['name']:<25} {self.bridges[bridge_keys[1]]['name']:<25}")
        else:
            print(f"\n{'Metric':<25} {self.bridges[bridge_keys[0]]['name']:<25}")
        print("-"*75)
        
        # Print metrics for each bridge
        metrics = [
            ('Connectivity', lambda r: "✅ Connected" if r['reachable'] else "❌ Unreachable"),
            ('Average Latency', lambda r: f"{r['latency_ms']:.1f}ms" if r['latency_ms'] else "N/A"),
            ('Data Freshness', lambda r: f"{r['data_freshness']:.1f}s" if r['data_freshness'] else "N/A"),
            ('Update Frequency', lambda r: f"{r['update_frequency']:.1f} ticks/s" if r['update_frequency'] else "N/A"),
            ('Errors', lambda r: str(len(r['errors'])))
        ]
        
        for metric_name, format_func in metrics:
            values = []
            for key in bridge_keys[:2]:  # Compare up to 2 bridges
                if key in results:
                    values.append(format_func(results[key]))
            
            if len(values) >= 2:
                print(f"{metric_name:<25} {values[0]:<25} {values[1]:<25}")
            elif len(values) == 1:
                print(f"{metric_name:<25} {values[0]:<25}")
        
        # Scores
        score_strs = []
        for bridge_key in self.bridges.keys():
            if bridge_key in analysis['scores']:
                score_str = f"{analysis['scores'][bridge_key]['percentage']:.1f}%"
                score_strs.append(score_str)
        
        if len(score_strs) >= 2:
            print(f"{'Overall Score':<25} {score_strs[0]:<25} {score_strs[1]:<25}")
        elif len(score_strs) == 1:
            print(f"{'Overall Score':<25} {score_strs[0]:<25}")
        
        print("\n" + "="*80)
        print(f"🏆 RECOMMENDATION: {analysis['recommendation']}")
        print("="*80)
        
        # Detailed error report if any
        if any(results[k]['errors'] for k in results):
            print("\n⚠️  ERROR DETAILS:")
            for key, result in results.items():
                if result['errors']:
                    print(f"\n{result['name']}:")
                    for error in result['errors']:
                        print(f"  - {error}")
                        
    async def run_comparison(self):
        """Run the full comparison test"""
        print("🚀 Starting Sierra Chart Bridge Comparison Test")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test each bridge
        results = {}
        for bridge_key, bridge_info in self.bridges.items():
            results[bridge_key] = await self.test_bridge(bridge_key, bridge_info)
            
        # Analyze results
        analysis = self.analyze_results(results)
        
        # Print comparison
        self.print_comparison_table(results, analysis)
        
        # Save results to file
        output = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'analysis': analysis
        }
        
        with open('bridge_comparison_results.json', 'w') as f:
            json.dump(output, f, indent=2)
            
        print("\n💾 Detailed results saved to: bridge_comparison_results.json")
        
        return analysis['recommendation']

async def main():
    comparator = BridgeComparator()
    recommendation = await comparator.run_comparison()
    
    # Ask user if they want to update configuration
    if 'marypc' in recommendation.lower():
        print("\n🔄 Would you like to update the configuration to use MaryPC?")
        print("This will modify config/minhos_v4.json")
        response = input("Update configuration? (y/n): ").lower()
        
        if response == 'y':
            try:
                with open('config/minhos_v4.json', 'r') as f:
                    config = json.load(f)
                    
                # Update bridge configuration
                config['network']['bridge_host'] = '100.123.37.79'
                config['network']['bridge_fallback_host'] = 'marypc'
                config['network']['bridge_fallback_ips'] = ['172.21.128.1', '100.64.0.1']
                
                with open('config/minhos_v4.json', 'w') as f:
                    json.dump(config, f, indent=2)
                    
                print("✅ Configuration updated successfully!")
                print("⚠️  Please restart MinhOS services for changes to take effect.")
            except Exception as e:
                print(f"❌ Failed to update configuration: {e}")

if __name__ == "__main__":
    asyncio.run(main())