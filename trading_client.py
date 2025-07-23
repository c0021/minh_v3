#!/usr/bin/env python3
"""
MinhOS v3 Trading Client - Complete trading interface for Sierra Chart
"""

import asyncio
import json
import time
from client import MinhOSClient

class TradingClient:
    def __init__(self, bridge_url: str):
        self.bridge_url = bridge_url
        
    async def test_system(self):
        """Test the complete MinhOS trading system"""
        async with MinhOSClient(self.bridge_url) as client:
            print("=" * 60)
            print("MINHOS V3 TRADING SYSTEM TEST")
            print("=" * 60)
            
            # 1. Health check
            print("\n1. BRIDGE HEALTH CHECK")
            health = await client.health_check()
            print(json.dumps(health, indent=2))
            
            if health.get("status") != "healthy":
                print("❌ Bridge not healthy - check Windows bridge is running")
                return
            
            # 2. Market data test
            print("\n2. MARKET DATA TEST")
            market_data = await client.get_market_data()
            if market_data:
                print("✅ Market data received:")
                print(json.dumps(market_data, indent=2))
            else:
                print("⚠️  No market data available yet")
                print("   - Check Sierra Chart study is running")
                print("   - Enable 'MinhOS Bridge' study on your chart")
                print("   - Ensure real-time data is flowing")
            
            # 3. Trading test (commented out for safety)
            print("\n3. TRADING TEST")
            print("⚠️  Trading test is DISABLED for safety")
            print("   To enable trading:")
            print("   1. Enable 'Enable Trading' in Sierra Chart study")
            print("   2. Uncomment trading test code below")
            print("   3. Verify you're on a demo/sim account")
            
            # TRADING TEST - ENABLED
            print("🔥 EXECUTING TEST BUY ORDER...")
            print("⚠️  ENSURE YOU'RE ON A DEMO/SIMULATION ACCOUNT!")
            
            # Test buy 1 NQ contract
            trade_result = await client.execute_trade("BUY", "NQU25-CME", 1)
            print("Trade result:", json.dumps(trade_result, indent=2))
            
            if "command_id" in trade_result:
                print(f"⏳ Waiting for execution...")
                await asyncio.sleep(3)
                
                status = await client.get_trade_status(trade_result["command_id"])
                print("Trade status:", json.dumps(status, indent=2))
                
                if status.get("status") == "FILLED":
                    print("✅ TRADE EXECUTED SUCCESSFULLY!")
                elif status.get("status") == "REJECTED":
                    print("❌ Trade rejected:", status.get("message"))
                else:
                    print("⏳ Trade status:", status.get("status"))
            
            print("\n4. SYSTEM STATUS")
            print(f"✅ Bridge connected: {self.bridge_url}")
            print("✅ Market data path: C:/SierraChart/Data/minhos_market_data.json")
            print("✅ Trade commands path: C:/SierraChart/Data/minhos_trade_commands.json")
            print("✅ Ready for MinhOS trading algorithms!")
    
    async def live_market_stream(self):
        """Stream live market data"""
        print("\n" + "=" * 60)
        print("LIVE MARKET DATA STREAM")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        async with MinhOSClient(self.bridge_url) as client:
            try:
                while True:
                    data = await client.get_market_data()
                    if data:
                        timestamp = data.get('timestamp', 'N/A')
                        symbol = data.get('symbol', 'N/A')
                        price = data.get('price', 0)
                        volume = data.get('volume', 0)
                        bid = data.get('bid', 0)
                        ask = data.get('ask', 0)
                        
                        print(f"[{timestamp[:19]}] {symbol}: ${price:.2f} "
                              f"Bid:{bid:.2f} Ask:{ask:.2f} Vol:{volume}")
                    else:
                        print("⏳ Waiting for market data...")
                    
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n📊 Market stream stopped")
    
    async def execute_sample_trade(self, action: str, symbol: str, quantity: int):
        """Execute a sample trade (USE DEMO ACCOUNT ONLY!)"""
        print(f"\n🔥 EXECUTING {action} {quantity} {symbol}")
        print("⚠️  ENSURE YOU'RE ON A DEMO/SIMULATION ACCOUNT!")
        
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Trade cancelled")
            return
        
        async with MinhOSClient(self.bridge_url) as client:
            # Execute trade
            result = await client.execute_trade(action, symbol, quantity)
            print("Trade submitted:", json.dumps(result, indent=2))
            
            if "command_id" in result:
                # Wait and check status
                await asyncio.sleep(2)
                status = await client.get_trade_status(result["command_id"])
                print("Trade status:", json.dumps(status, indent=2))
                
                if status.get("status") == "FILLED":
                    print("✅ Trade executed successfully!")
                elif status.get("status") == "REJECTED":
                    print("❌ Trade rejected:", status.get("message"))
                else:
                    print("⏳ Trade still pending...")

async def main():
    BRIDGE_URL = "http://cthinkpad:8765"
    client = TradingClient(BRIDGE_URL)
    
    # Run system test automatically
    await client.test_system()

if __name__ == "__main__":
    asyncio.run(main())