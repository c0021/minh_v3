#!/usr/bin/env python3
"""
Sierra Chart Bridge API Enhancement - Add SSE Support
Add this code to your existing bridge_api.py on Windows
"""

from flask import Flask, Response, jsonify
import json
import time
import threading
from datetime import datetime

# Add this to your existing Bridge API

def generate_sse_stream(get_sierra_data_func):
    """
    Generate Server-Sent Events stream with market data
    
    Args:
        get_sierra_data_func: Your existing function to get Sierra Chart data
    """
    while True:
        try:
            # Get current market data from Sierra Chart
            market_data = get_sierra_data_func()
            
            # Add timestamp if not present
            if 'timestamp' not in market_data:
                market_data['timestamp'] = datetime.now().isoformat()
            
            # Format as SSE
            event = f"data: {json.dumps(market_data)}\n\n"
            yield event
            
            # Stream at 10Hz for smooth updates
            time.sleep(0.1)
            
        except Exception as e:
            # Send error event
            error_event = f"event: error\ndata: {json.dumps({'error': str(e), 'timestamp': datetime.now().isoformat()})}\n\n"
            yield error_event
            time.sleep(1)


# Add this route to your Flask app
def add_sse_endpoint(app, get_sierra_data_func):
    """
    Add SSE endpoint to existing Flask app
    
    Args:
        app: Your Flask application instance
        get_sierra_data_func: Function to get Sierra Chart data
    """
    
    @app.route('/api/market_stream')
    def market_stream():
        """SSE endpoint for real-time market data streaming"""
        return Response(
            generate_sse_stream(get_sierra_data_func),
            mimetype="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',  # Disable Nginx buffering
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'  # Adjust for security
            }
        )
    
    # Also add a heartbeat endpoint
    @app.route('/api/stream_health')
    def stream_health():
        """Check if SSE streaming is available"""
        return jsonify({
            'status': 'healthy',
            'sse_enabled': True,
            'timestamp': datetime.now().isoformat()
        })


# Example integration with your existing bridge:
"""
# In your existing bridge_api.py:

from bridge_api_sse_enhancement import add_sse_endpoint

# Your existing Flask app
app = Flask(__name__)

# Your existing function to get Sierra data
def get_sierra_chart_data():
    # Your existing implementation
    return {
        'symbol': 'NQU25-CME',
        'last_price': 21500.25,
        'bid': 21500.00,
        'ask': 21500.50,
        'volume': 12345,
        'timestamp': datetime.now().isoformat()
    }

# Add SSE support
add_sse_endpoint(app, get_sierra_chart_data)

# Your existing routes remain unchanged
@app.route('/api/market_data')
def market_data():
    # Your existing implementation
    pass
"""