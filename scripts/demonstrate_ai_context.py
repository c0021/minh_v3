#!/usr/bin/env python3
"""
Demonstrate AI Historical Context Usage
======================================

Shows how the AI now uses historical data for improved decision making.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from minhos.core.market_data_adapter import get_market_data_adapter

def demonstrate_ai_context():
    """Demonstrate AI using historical context"""
    print("🧠 AI Historical Context Demonstration")
    print("=" * 50)
    
    adapter = get_market_data_adapter()
    
    # Test NQU25-CME (primary trading symbol)
    symbol = "NQU25-CME"
    print(f"📊 Analyzing {symbol} with AI Historical Context:")
    print()
    
    # Get historical data that AI can now access
    historical_data = adapter.get_historical_data(symbol, limit=30)
    
    if historical_data:
        print(f"✅ AI HAS ACCESS TO {len(historical_data)} HISTORICAL RECORDS")
        print()
        
        # Show what AI can now analyze
        prices = [float(data.close) for data in historical_data]
        volumes = [int(data.volume) for data in historical_data]
        
        # AI can now perform sophisticated analysis
        current_price = prices[0]
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        price_volatility = (max_price - min_price) / min_price * 100
        
        print("🔍 AI ANALYSIS CAPABILITIES (Previously Impossible):")
        print(f"  Current Price: ${current_price:,.2f}")
        print(f"  30-Day Average: ${avg_price:,.2f}")
        print(f"  30-Day Range: ${min_price:,.2f} - ${max_price:,.2f}")
        print(f"  Volatility: {price_volatility:.1f}%")
        print()
        
        # Show price trend analysis
        if len(prices) >= 5:
            recent_trend = sum(prices[:5]) / 5
            older_trend = sum(prices[-5:]) / 5
            trend_direction = "UPWARD" if recent_trend > older_trend else "DOWNWARD"
            trend_strength = abs(recent_trend - older_trend) / older_trend * 100
            
            print("📈 AI TREND ANALYSIS:")
            print(f"  Recent 5-day avg: ${recent_trend:,.2f}")
            print(f"  Older 5-day avg: ${older_trend:,.2f}")
            print(f"  Trend Direction: {trend_direction}")
            print(f"  Trend Strength: {trend_strength:.1f}%")
            print()
        
        # Show what this means for AI decisions
        print("🎯 AI DECISION ENHANCEMENT:")
        if price_volatility > 3:
            print("  ⚠️  HIGH VOLATILITY DETECTED - AI can adjust risk accordingly")
        else:
            print("  ✅  NORMAL VOLATILITY - AI can use standard position sizing")
            
        if current_price > avg_price:
            print("  📊 ABOVE AVERAGE - AI aware of elevated price levels")
        else:
            print("  📊 BELOW AVERAGE - AI aware of discount opportunity")
            
        print()
        print("🚀 BEFORE: AI had NO historical context - blind trading")
        print("🚀 AFTER:  AI has 30+ days of market memory - informed decisions")
        
    else:
        print("❌ No historical data available for AI analysis")
    
    print()
    print("💡 To see AI make actual trading decisions with this context:")
    print("   1. Start full MinhOS: python3 minhos/main.py")
    print("   2. Open dashboard: http://localhost:3000")
    print("   3. Watch AI Transparency section show historical analysis")

if __name__ == "__main__":
    demonstrate_ai_context()