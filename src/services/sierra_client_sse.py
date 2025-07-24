#!/usr/bin/env python3
"""
Alternative Sierra Client using Server-Sent Events (SSE) for real-time streaming
This avoids TCP polling issues entirely by using a persistent connection
"""
import json
import logging
import time
import requests
import sseclient
from typing import Optional, Dict, Any
from threading import Thread, Event


class SSESierraClient:
    """Sierra Chart client using Server-Sent Events for real-time data"""
    
    def __init__(self, bridge_url: str = "http://cthinkpad:8765", db_connection=None):
        self.bridge_url = bridge_url
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.stop_event = Event()
        self.reconnect_delay = 1  # Initial reconnect delay in seconds
        
    def stream_market_data(self):
        """Main streaming loop using SSE"""
        self.logger.info("Starting SSE market data streaming...")
        
        while not self.stop_event.is_set():
            try:
                self._connect_and_stream()
            except KeyboardInterrupt:
                self.logger.info("Streaming interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"SSE connection error: {e}")
                
                # Exponential backoff for reconnection
                self.logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)
    
    def _connect_and_stream(self):
        """Connect to SSE endpoint and process stream"""
        # SSE endpoint URL
        stream_url = f"{self.bridge_url}/api/market_stream"
        
        self.logger.info(f"Connecting to SSE stream: {stream_url}")
        
        # Create SSE client with custom headers
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(stream_url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Reset reconnect delay on successful connection
        self.reconnect_delay = 1
        
        client = sseclient.SSEClient(response)
        
        self.logger.info("SSE connection established")
        
        # Process events
        for event in client.events():
            if self.stop_event.is_set():
                break
                
            try:
                # Parse market data from event
                data = json.loads(event.data)
                self._process_market_data(data)
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in SSE event: {e}")
            except Exception as e:
                self.logger.error(f"Error processing SSE event: {e}")
    
    def _process_market_data(self, data: Dict[str, Any]):
        """Process and store market data"""
        try:
            # Log the received data
            self.logger.info(
                f"SSE data: {data.get('symbol', 'UNKNOWN')} "
                f"@ ${data.get('last_price', 0):.2f} "
                f"(bid: ${data.get('bid', 0):.2f}, "
                f"ask: ${data.get('ask', 0):.2f})"
            )
            
            # Your database update logic here
            if self.db:
                self.db.update_market_data(data)
                
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
    
    def stop(self):
        """Stop the SSE client gracefully"""
        self.logger.info("Stopping SSE client...")
        self.stop_event.set()
    
    def test_connection(self) -> bool:
        """Test if SSE endpoint is available"""
        try:
            # First test regular endpoint
            response = requests.get(
                f"{self.bridge_url}/api/market_data",
                timeout=5
            )
            if response.status_code != 200:
                self.logger.error("Bridge API not responding")
                return False
            
            # Then check if SSE endpoint exists
            response = requests.head(
                f"{self.bridge_url}/api/market_stream",
                timeout=5
            )
            if response.status_code == 404:
                self.logger.warning(
                    "SSE endpoint not found. Bridge API may need SSE support added."
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


# Example Bridge API SSE endpoint implementation (for Windows side)
SSE_BRIDGE_EXAMPLE = '''
# Add this to your existing Bridge API (bridge_api.py on Windows)

from flask import Flask, Response
import json
import time
import threading

app = Flask(__name__)

def generate_sse_stream():
    """Generate Server-Sent Events stream with market data"""
    while True:
        try:
            # Get current market data from Sierra Chart
            market_data = get_sierra_chart_data()  # Your existing function
            
            # Format as SSE
            event = f"data: {json.dumps(market_data)}\\n\\n"
            yield event
            
            # Stream at 10Hz for smooth updates
            time.sleep(0.1)
            
        except Exception as e:
            # Send error event
            error_event = f"event: error\\ndata: {json.dumps({'error': str(e)})}\\n\\n"
            yield error_event
            time.sleep(1)

@app.route('/api/market_stream')
def market_stream():
    """SSE endpoint for real-time market data"""
    return Response(
        generate_sse_stream(),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable Nginx buffering
            'Connection': 'keep-alive'
        }
    )

# Your existing endpoints remain unchanged
@app.route('/api/market_data')
def market_data():
    # ... existing implementation ...
'''


def main():
    """Main entry point for standalone execution"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Check if sseclient is installed
    try:
        import sseclient
    except ImportError:
        logging.error(
            "sseclient-py not installed. Install with: pip install sseclient-py"
        )
        return
    
    # Create and run client
    client = SSESierraClient()
    
    # Test connection first
    if not client.test_connection():
        logging.warning(
            "SSE endpoint may not be available. "
            "Ensure Bridge API has SSE support implemented."
        )
        logging.info("\nTo add SSE support to your Bridge API:")
        print(SSE_BRIDGE_EXAMPLE)
        return
    
    try:
        client.stream_market_data()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        client.stop()


if __name__ == "__main__":
    main()