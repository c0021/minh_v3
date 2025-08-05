#!/usr/bin/env python3
"""
Quick WebSocket test to verify handshake fix
"""
import asyncio
import websockets
import json

async def test_websocket_connection():
    """Test WebSocket connection to verify handshake works"""
    try:
        # Test the optimized WebSocket endpoint
        uri = "ws://localhost:8765/ws/live_data/NQU25-CME"
        print(f"Testing WebSocket connection to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection successful - handshake completed!")
            
            # Send a test message
            await websocket.send(json.dumps({"type": "heartbeat"}))
            print("✅ Test message sent successfully")
            
            # Try to receive a response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"✅ Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No immediate response (normal for this endpoint)")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - bridge may not be running on port 8765")
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    print("WebSocket Handshake Fix Test")
    print("=" * 40)
    asyncio.run(test_websocket_connection())