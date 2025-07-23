#!/usr/bin/env python3
"""
MinhOS v3 Linux Client - Connects to Windows Bridge
"""

import json
import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinhOSClient:
    def __init__(self, bridge_url: str):
        """Initialize client with bridge URL (e.g., 'http://trading-pc:8765')"""
        self.bridge_url = bridge_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check bridge health status"""
        try:
            async with self.session.get(f"{self.bridge_url}/health") as resp:
                return await resp.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_market_data(self) -> Optional[Dict[str, Any]]:
        """Get current market data"""
        try:
            async with self.session.get(f"{self.bridge_url}/api/market_data") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"Failed to get market data: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
    
    async def execute_trade(self, action: str, symbol: str, quantity: int, 
                          price: Optional[float] = None, order_type: str = "MARKET") -> Dict[str, Any]:
        """Execute a trade command"""
        command = {
            "command_id": f"cmd_{datetime.now().timestamp()}",
            "action": action,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "order_type": order_type
        }
        
        try:
            async with self.session.post(f"{self.bridge_url}/api/trade/execute", 
                                       json=command) as resp:
                return await resp.json()
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_trade_status(self, command_id: str) -> Dict[str, Any]:
        """Get trade execution status"""
        try:
            async with self.session.get(f"{self.bridge_url}/api/trade/status/{command_id}") as resp:
                return await resp.json()
        except Exception as e:
            logger.error(f"Failed to get trade status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def stream_market_data(self):
        """Stream real-time market data via WebSocket"""
        ws_url = self.bridge_url.replace("http://", "ws://") + "/ws/market_stream"
        
        try:
            async with self.session.ws_connect(ws_url) as ws:
                logger.info("Connected to market data stream")
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        logger.info(f"Market update: {data}")
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"WebSocket error: {ws.exception()}")
                        
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")

async def main():
    """Example usage of MinhOSClient"""
    
    # Configure your Windows bridge URL here
    # Use your Tailscale hostname or IP
    BRIDGE_URL = "http://cthinkpad:8765"
    
    async with MinhOSClient(BRIDGE_URL) as client:
        # Check health
        print("\n=== Health Check ===")
        health = await client.health_check()
        print(json.dumps(health, indent=2))
        
        # Get market data
        print("\n=== Market Data ===")
        market_data = await client.get_market_data()
        if market_data:
            print(json.dumps(market_data, indent=2))
        
        # Example trade (commented out for safety)
        # print("\n=== Execute Trade ===")
        # result = await client.execute_trade("BUY", "ES", 1)
        # print(json.dumps(result, indent=2))
        
        # Stream market data (runs until interrupted)
        # print("\n=== Streaming Market Data ===")
        # await client.stream_market_data()

if __name__ == "__main__":
    asyncio.run(main())