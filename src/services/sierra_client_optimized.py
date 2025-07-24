#!/usr/bin/env python3
"""
Optimized Sierra Chart Client with TCP optimizations for 1Hz streaming
Fixes Nagle's Algorithm and Delayed ACK issues
"""
import socket
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any


class OptimizedSierraClient:
    """Sierra Chart client with TCP optimizations and connection pooling"""
    
    def __init__(self, bridge_url: str = "http://cthinkpad:8765", db_connection=None):
        self.bridge_url = bridge_url
        self.db = db_connection
        self.session = self._create_optimized_session()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def _create_optimized_session(self) -> requests.Session:
        """Create session with TCP optimizations and connection pooling"""
        session = requests.Session()
        
        # Custom adapter with TCP_NODELAY to disable Nagle's Algorithm
        class NoDelayHTTPAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                # Critical: Disable Nagle's Algorithm
                kwargs["socket_options"] = [
                    (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
                ]
                # Linux-specific: Enable TCP_QUICKACK if available
                if hasattr(socket, 'TCP_QUICKACK'):
                    kwargs["socket_options"].append(
                        (socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
                    )
                return super().init_poolmanager(*args, **kwargs)
        
        # Configure adapter with connection pooling and retries
        adapter = NoDelayHTTPAdapter(
            pool_connections=10,  # Number of connection pools
            pool_maxsize=20,      # Connections per pool
            pool_block=False,     # Don't block when pool is full
            max_retries=Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Keep-alive headers to maintain persistent connections
        session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=30, max=100',
            'User-Agent': 'MinhOS-Sierra-Client/3.0'
        })
        
        return session
    
    def stream_market_data(self):
        """Main streaming loop with proper error handling"""
        consecutive_errors = 0
        last_data_timestamp = None
        request_count = 0
        start_time = time.time()
        
        self.logger.info("Starting optimized market data streaming...")
        
        while True:
            loop_start = time.time()
            
            try:
                # Use session for connection reuse (critical for performance)
                response = self.session.get(
                    f"{self.bridge_url}/api/market_data",
                    timeout=(3, 10)  # (connect timeout, read timeout)
                )
                
                request_count += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if data has actually updated
                    current_timestamp = data.get('timestamp')
                    if current_timestamp != last_data_timestamp:
                        self._process_market_data(data)
                        last_data_timestamp = current_timestamp
                        consecutive_errors = 0
                        
                        # Log performance metrics every 60 seconds
                        if request_count % 60 == 0:
                            elapsed = time.time() - start_time
                            avg_rate = request_count / elapsed
                            self.logger.info(
                                f"Performance: {request_count} requests, "
                                f"{avg_rate:.2f} req/s, "
                                f"uptime: {elapsed:.0f}s"
                            )
                    else:
                        self.logger.debug("Received duplicate data, skipping")
                else:
                    self.logger.warning(f"HTTP {response.status_code}: {response.text}")
                    consecutive_errors += 1
                    
            except requests.exceptions.ConnectionError as e:
                consecutive_errors += 1
                self.logger.error(f"Connection error (attempt {consecutive_errors}): {e}")
                
                # Exponential backoff on connection errors
                if consecutive_errors > 3:
                    backoff_time = min(2 ** (consecutive_errors - 3), 30)
                    self.logger.info(f"Backing off for {backoff_time}s...")
                    time.sleep(backoff_time)
                    
            except requests.exceptions.Timeout:
                consecutive_errors += 1
                self.logger.error(f"Request timeout (attempt {consecutive_errors})")
                
            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Unexpected error: {e}", exc_info=True)
            
            # Reset session if too many consecutive errors
            if consecutive_errors > 10:
                self.logger.warning("Too many errors, resetting session...")
                self.session.close()
                self.session = self._create_optimized_session()
                consecutive_errors = 0
                time.sleep(5)
            
            # Maintain 1Hz rate (adjust for processing time)
            loop_duration = time.time() - loop_start
            sleep_time = max(0, 1.0 - loop_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _process_market_data(self, data: Dict[str, Any]):
        """Process and store market data"""
        try:
            # Log the received data
            self.logger.info(
                f"Market data: {data.get('symbol', 'UNKNOWN')} "
                f"@ ${data.get('last_price', 0):.2f} "
                f"(bid: ${data.get('bid', 0):.2f}, "
                f"ask: ${data.get('ask', 0):.2f})"
            )
            
            # Your database update logic here
            if self.db:
                self.db.update_market_data(data)
            
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Sierra Bridge API"""
        try:
            response = self.session.get(
                f"{self.bridge_url}/api/market_data",
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info("Connection test successful")
                return True
            else:
                self.logger.error(f"Connection test failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def close(self):
        """Close the session properly"""
        if self.session:
            self.session.close()


def main():
    """Main entry point for standalone execution"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create and run client
    client = OptimizedSierraClient()
    
    # Test connection first
    if not client.test_connection():
        logging.error("Failed to connect to Sierra Bridge API")
        return
    
    try:
        client.stream_market_data()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        client.close()


if __name__ == "__main__":
    main()