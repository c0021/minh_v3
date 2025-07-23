"""
Bridge connection tests
=======================

Tests for validating connection to Windows bridge.
These tests require an actual bridge running.
"""

import asyncio
import pytest
import aiohttp
import websockets
from minhos.core.config import config


@pytest.mark.bridge
@pytest.mark.asyncio 
async def test_bridge_health():
    """Test bridge health endpoint"""
    url = f"http://{config.sierra.host}:{config.sierra.port}/health"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                assert response.status == 200
                data = await response.json()
                assert "status" in data
                
        except aiohttp.ClientError:
            pytest.skip(f"Bridge not available at {url}")


@pytest.mark.bridge 
@pytest.mark.asyncio
async def test_bridge_market_data():
    """Test bridge market data endpoint"""
    url = f"http://{config.sierra.host}:{config.sierra.port}/api/market_data"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "symbol" in data
                    assert "price" in data
                    assert data["price"] > 0
                elif response.status == 404:
                    # No market data available is acceptable
                    pass
                else:
                    pytest.fail(f"Unexpected status: {response.status}")
                    
        except aiohttp.ClientError:
            pytest.skip(f"Bridge not available at {url}")


@pytest.mark.bridge
@pytest.mark.asyncio
async def test_bridge_websocket():
    """Test bridge WebSocket connection"""
    ws_url = f"ws://{config.sierra.host}:{config.sierra.port}/ws/market_stream"
    
    try:
        async with websockets.connect(ws_url, timeout=5) as websocket:
            # Try to receive a message within timeout
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                assert message  # Should receive something
            except asyncio.TimeoutError:
                # No message received is acceptable for test
                pass
                
    except (websockets.exceptions.ConnectionRefusedError, OSError):
        pytest.skip(f"WebSocket not available at {ws_url}")


@pytest.mark.bridge
@pytest.mark.slow
@pytest.mark.asyncio
async def test_sierra_client_integration():
    """Integration test with actual Sierra client"""
    from minhos.core.sierra_client import SierraClient
    
    client = SierraClient()
    
    # Test connection
    connected = await client.connect()
    if not connected:
        pytest.skip("Could not connect to bridge")
    
    try:
        # Test market data
        market_data = await client.get_market_data()
        if market_data:
            assert market_data.symbol
            assert market_data.price > 0
        
        # Test stats
        stats = client.get_stats()
        assert "status" in stats
        
    finally:
        await client.disconnect()