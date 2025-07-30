#!/usr/bin/env python3
"""
Test AI Dashboard Integration
============================

Tests if the AI Brain's historical context appears in the dashboard API.
"""

import sys
import requests
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_dashboard_api():
    """Test dashboard API for historical context"""
    print("🖥️ Testing Dashboard API for Historical Context")
    print("=" * 55)
    
    # Typical MinhOS dashboard URLs
    test_urls = [
        "http://localhost:3000/api/ai-brain/status",
        "http://localhost:3000/api/status", 
        "http://localhost:8000/api/ai-brain/status",
        "http://localhost:8000/api/status"
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔍 Testing: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for historical context
                if 'historical_context' in data:
                    print(f"  ✅ Historical Context Found!")
                    hist_ctx = data['historical_context']
                    
                    if hist_ctx.get('has_historical_context'):
                        print(f"     📊 Price Range: ${hist_ctx.get('min_price', 0):.2f} - ${hist_ctx.get('max_price', 0):.2f}")
                        print(f"     📈 Average Price: ${hist_ctx.get('avg_price', 0):.2f}")
                        print(f"     📅 Historical Days: {hist_ctx.get('historical_range_days', 0)}")
                    else:
                        print(f"     ⚠️ AI reports no historical context")
                        
                if 'data_points' in data:
                    print(f"  📊 AI Data Points: {data['data_points']}")
                    
                if 'analysis' in data and data['analysis']:
                    analysis = data['analysis']
                    print(f"  🧠 AI Analysis Available:")
                    print(f"     Trend: {analysis.get('trend_direction', 'unknown')}")
                    print(f"     Confidence: {analysis.get('overall_confidence', 0):.1%}")
                    
                # Show we found working endpoint
                print(f"  ✅ Dashboard API working at {url}")
                return True
                
            elif response.status_code == 404:
                print(f"  ❌ Endpoint not found")
            else:
                print(f"  ⚠️ Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection failed - MinhOS not running?")
        except Exception as e:
            print(f"  ❓ Error: {e}")
    
    print(f"\n💡 To see historical context in dashboard:")
    print(f"   1. Start MinhOS: python3 minh.py start")
    print(f"   2. Wait for 'AI Brain loaded XX historical records'")
    print(f"   3. Open dashboard URL shown in startup logs")
    print(f"   4. Look for AI Transparency section with historical data")
    
    return False

if __name__ == "__main__":
    test_dashboard_api()