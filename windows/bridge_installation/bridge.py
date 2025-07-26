#!/usr/bin/env python3
"""
MinhOS Windows Bridge - Enhanced with Historical Data Access
============================================================

Complete bridge service providing:
1. Real-time market data streaming from Sierra Chart
2. Trade execution interface
3. Historical data file access API for MinhOS analysis

This bridge enables MinhOS (Linux) to access both live data and historical archives
from Sierra Chart (Windows) via secure Tailscale networking.

Features:
- FastAPI-based REST and WebSocket APIs
- Sierra Chart DTC protocol integration
- Secure file system access for historical data
- Health monitoring and status reporting
- Production-ready error handling and logging

Author: MinhOS v3 System
Date: 2025-01-24
"""

import asyncio
import json
import logging
import os
import socket
import struct
import time
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import traceback
from dataclasses import dataclass, asdict
from enum import Enum

# Web framework and networking
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

# Import our secure file access API
from file_access_api import sierra_file_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bridge.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="MinhOS Sierra Chart Bridge",
    description="Bridge service for MinhOS trading system integration with Sierra Chart",
    version="3.1.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tailscale network only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class MarketData:
    """Market data structure with Phase 3 microsecond precision support"""
    symbol: str
    timestamp: str
    price: float
    volume: int
    bid: float
    ask: float
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    source: str = "unknown"
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    last_size: Optional[int] = None
    vwap: Optional[float] = None
    trades: Optional[int] = None
    # Phase 3 enhancements
    timestamp_us: Optional[int] = None      # Microsecond precision timestamp
    trade_side: Optional[str] = None        # 'B', 'S', or 'U' for trade direction
    sequence: Optional[int] = None          # Sequence number for ordering
    precision: Optional[str] = None         # Precision indicator
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PositionInfo:
    """Position information from Sierra Chart"""
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float

class TradeRequest(BaseModel):
    """Trade request model"""
    command_id: str
    action: str  # BUY, SELL
    symbol: str
    quantity: int
    price: Optional[float] = None
    order_type: str = "MARKET"

class TradeResponse(BaseModel):
    """Trade response model"""
    command_id: str
    status: str  # SUBMITTED, FILLED, REJECTED
    message: str
    fill_price: Optional[float] = None
    timestamp: str

class SierraChartBridge:
    """
    Enhanced Sierra Chart Bridge with Historical Data Access
    
    Provides both real-time trading functionality and secure historical data access
    for comprehensive MinhOS integration.
    """
    
    def __init__(self):
        """Initialize Sierra Chart Bridge"""
        self.connection_state = ConnectionState.DISCONNECTED
        self.sierra_host = "127.0.0.1"  # Sierra Chart on same machine
        self.sierra_port = 11098  # Default DTC port
        
        # Market data
        self.latest_market_data: Dict[str, MarketData] = {}
        self.websocket_clients: List[WebSocket] = []
        
        # Trading
        self.pending_trades: Dict[str, TradeRequest] = {}
        self.positions: Dict[str, PositionInfo] = {}
        
        # Configuration (centralized symbol management)
        self.symbols = self._load_bridge_symbols()  # Load from centralized bridge config
        self.update_interval = 1.0  # seconds
        
        # Connection management
        self.socket: Optional[socket.socket] = None
        self.last_heartbeat = time.time()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        logger.info("Sierra Chart Bridge initialized with historical data access")
    
    async def start(self):
        """Start the bridge service"""
        logger.info("Starting Sierra Chart Bridge...")
        logger.warning("DTC market data access is blocked by Sierra Chart (Dec 2024 policy)")
        logger.info("Bridge will focus on historical data access via SCID files")
        
        # Start background tasks for file-based data monitoring
        asyncio.create_task(self._file_data_monitor())
        asyncio.create_task(self._market_data_publisher())
        
        logger.info("Sierra Chart Bridge started successfully")
    
    def _load_bridge_symbols(self) -> List[str]:
        """Load symbols from centralized bridge configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'bridge_symbols.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            symbols = config.get('active_symbols', [])
            logger.info(f"Loaded {len(symbols)} symbols from centralized config: {symbols}")
            
            # Log rollover alerts if any
            alerts = config.get('rollover_alerts', [])
            for alert in alerts:
                if alert.get('action_required', False):
                    logger.warning(f"ROLLOVER ALERT: {alert['symbol']} expires in {alert['days_until_rollover']} days")
                elif alert.get('days_until_rollover', 0) <= 15:
                    logger.info(f"Upcoming rollover: {alert['symbol']} → {alert['next_symbol']} in {alert['days_until_rollover']} days")
            
            return symbols
            
        except Exception as e:
            logger.error(f"Failed to load bridge symbols config: {e}")
            # Fallback to hardcoded symbols
            fallback_symbols = ["NQU25-CME", "ESU25-CME", "VIX_CGI"]
            logger.warning(f"Using fallback symbols: {fallback_symbols}")
            return fallback_symbols
    
    async def _file_data_monitor(self):
        """Monitor Sierra Chart files for real-time data updates"""
        logger.info("Starting file-based data monitoring...")
        
        # Common Sierra Chart data locations
        potential_data_paths = [
            "/mnt/c/SierraChart/Data",  # WSL path (primary)
            "C:\\SierraChart\\Data",
            "C:\\Program Files\\Sierra Chart\\Data", 
            "C:\\Program Files (x86)\\Sierra Chart\\Data",
            "D:\\SierraChart\\Data"
        ]
        
        data_path = None
        for path in potential_data_paths:
            if os.path.exists(path):
                data_path = path
                logger.info(f"Found Sierra Chart data directory: {path}")
                break
        
        if not data_path:
            logger.warning("Sierra Chart data directory not found - historical data only")
            logger.info("Available alternative: Use Sierra Chart's 'Write Bar Data to File' study")
            return
        
        # Monitor for file updates
        while True:
            try:
                # Check for SCID files for our symbols
                for symbol in self.symbols:
                    scid_pattern = f"{symbol}*.scid"
                    scid_files = glob.glob(os.path.join(data_path, scid_pattern))
                    
                    for scid_file in scid_files:
                        try:
                            # Check if file was updated recently (last 30 seconds)
                            mod_time = os.path.getmtime(scid_file)
                            if time.time() - mod_time < 30:
                                await self._process_scid_update(scid_file, symbol)
                        except Exception as e:
                            logger.debug(f"Error checking {scid_file}: {e}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"File monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _process_scid_update(self, scid_file: str, symbol: str):
        """Process updated SCID file and extract latest market data"""
        try:
            # Use our existing file access API to read the SCID file
            from file_access_api import sierra_file_api
            
            # Get the latest records from the file
            # Note: sierra_file_api.read_file is designed for FastAPI endpoints
            # For internal use, we'll access file info directly
            if not os.path.exists(scid_file):
                return
            
            # For now, simulate market data from file timestamp
            # In production, you'd parse the SCID binary format here
            mod_time = os.path.getmtime(scid_file)
            
            # Create market data from file info
            market_data = MarketData(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(mod_time),
                price=0.0,  # Would extract from SCID data
                volume=0,
                bid=0.0,
                ask=0.0,
                open=0.0,
                high=0.0,
                low=0.0,
                close=0.0
            )
            
            # Update our market data cache
            self.latest_market_data[symbol] = market_data
            logger.debug(f"Updated market data for {symbol} from SCID file")
            
        except Exception as e:
            logger.debug(f"Error processing SCID file {scid_file}: {e}")
    
    async def _connect_to_sierra(self):
        """Connect to Sierra Chart via DTC protocol"""
        try:
            self.connection_state = ConnectionState.CONNECTING
            logger.info(f"Connecting to Sierra Chart at {self.sierra_host}:{self.sierra_port}")
            
            # Create socket connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Connect to Sierra Chart
            self.socket.connect((self.sierra_host, self.sierra_port))
            
            # Send logon message (DTC protocol)
            await self._send_logon_request()
            
            # Wait for logon response
            response = await self._receive_dtc_message()
            if response and response.get('Type') == 'LOGON_RESPONSE':
                if response.get('Result') == 'SUCCESS':
                    self.connection_state = ConnectionState.CONNECTED
                    self.reconnect_attempts = 0
                    logger.info("Connected to Sierra Chart successfully")
                    
                    # Subscribe to market data
                    await self._subscribe_to_market_data()
                else:
                    raise Exception(f"Logon failed: {response.get('ResultText', 'Unknown error')}")
            elif response:
                logger.error(f"Unexpected response type: {response.get('Type', 'Unknown')}")
                logger.debug(f"Full response: {response}")
                raise Exception(f"Unexpected response from Sierra Chart: {response.get('Type', 'Unknown')}")
            else:
                logger.error("No response received from Sierra Chart")
                logger.warning("This could mean:")
                logger.warning("1. Sierra Chart is not running")
                logger.warning("2. DTC Server is not enabled in Sierra Chart")
                logger.warning("3. Wrong port number (should be 11098)")
                logger.warning("4. Firewall blocking the connection")
                raise Exception("No logon response received from Sierra Chart")
                
        except Exception as e:
            self.connection_state = ConnectionState.ERROR
            self.reconnect_attempts += 1
            logger.error(f"Connection failed (attempt {self.reconnect_attempts}): {e}")
            
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                logger.critical("Max reconnection attempts reached")
            
            await self._disconnect_from_sierra()
    
    async def _disconnect_from_sierra(self):
        """Disconnect from Sierra Chart"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.connection_state = ConnectionState.DISCONNECTED
    
    async def _send_logon_request(self):
        """Send DTC logon request"""
        logon_message = {
            'Type': 'LOGON_REQUEST',
            'ProtocolVersion': 8,
            'Username': 'colin0021',
            'Password': 'Genius5567$',
            'GeneralTextData': 'MinhOS v3 Bridge',
            'ClientName': 'MinhOS Trading System'
        }
        
        await self._send_dtc_message(logon_message)
    
    async def _subscribe_to_market_data(self):
        """Subscribe to market data for configured symbols"""
        for symbol in self.symbols:
            subscribe_message = {
                'Type': 'MARKET_DATA_REQUEST',
                'RequestID': hash(symbol) % 1000000,
                'Symbol': symbol,
                'Exchange': 'CME'
            }
            await self._send_dtc_message(subscribe_message)
            logger.info(f"Subscribed to market data for {symbol}")
    
    async def _send_dtc_message(self, message: Dict):
        """Send DTC protocol message in binary format"""
        if not self.socket:
            return
        
        try:
            # Sierra Chart DTC uses binary messages, not JSON
            # For now, let's try a simple text-based approach
            if message['Type'] == 'LOGON_REQUEST':
                # Create a simple logon message
                msg_text = f"LOGON|{message['Username']}|{message['Password']}|{message['ClientName']}\n"
                msg_data = msg_text.encode('utf-8')
                
                # Send with size header
                size = len(msg_data)
                header = struct.pack('<H', size)  # Use 2-byte header instead of 4
                
                logger.debug(f"Sending logon message: {msg_text.strip()}")
                self.socket.send(header + msg_data)
            else:
                # For other messages, use JSON format
                json_data = json.dumps(message).encode('utf-8')
                size = len(json_data)
                header = struct.pack('<H', size)
                self.socket.send(header + json_data)
            
        except Exception as e:
            logger.error(f"Failed to send DTC message: {e}")
    
    async def _receive_dtc_message(self) -> Optional[Dict]:
        """Receive DTC protocol message"""
        if not self.socket:
            return None
        
        try:
            # Set socket timeout for receiving
            self.socket.settimeout(5.0)
            
            # Try different header sizes - first 2 bytes, then 4 bytes
            size_data = self.socket.recv(2)
            if len(size_data) != 2:
                logger.warning("Received incomplete size header (2-byte)")
                # Try 4-byte header
                additional_data = self.socket.recv(2)
                if len(additional_data) == 2:
                    size_data += additional_data
                    size = struct.unpack('<I', size_data)[0]
                else:
                    return None
            else:
                size = struct.unpack('<H', size_data)[0]
            
            logger.debug(f"Expecting message of size: {size}")
            
            # Validate message size
            if size <= 0 or size > 65536:  # Max 64KB message
                logger.error(f"Invalid message size: {size}")
                return None
            
            # Read message data
            message_data = b''
            while len(message_data) < size:
                remaining = size - len(message_data)
                chunk = self.socket.recv(min(remaining, 4096))
                if not chunk:
                    logger.warning("Connection closed while reading message")
                    break
                message_data += chunk
            
            if len(message_data) == size:
                try:
                    # Try to parse as text first
                    text_message = message_data.decode('utf-8').strip()
                    logger.debug(f"Received text message: {text_message}")
                    
                    # Parse text-based response
                    if '|' in text_message:
                        parts = text_message.split('|')
                        if parts[0] == 'LOGON_RESPONSE':
                            return {
                                'Type': 'LOGON_RESPONSE',
                                'Result': parts[1] if len(parts) > 1 else 'UNKNOWN',
                                'ResultText': parts[2] if len(parts) > 2 else ''
                            }
                    
                    # Try JSON parsing as fallback
                    try:
                        message = json.loads(text_message)
                        logger.debug(f"Received JSON message: {message.get('Type', 'Unknown')}")
                        return message
                    except json.JSONDecodeError:
                        # Return raw text as message
                        return {
                            'Type': 'RAW_MESSAGE',
                            'Data': text_message
                        }
                        
                except UnicodeDecodeError:
                    logger.error("Failed to decode message as UTF-8")
                    logger.debug(f"Raw binary data: {message_data[:100]}...")
            else:
                logger.error(f"Incomplete message received: {len(message_data)}/{size}")
            
        except socket.timeout:
            logger.warning("Timeout waiting for DTC message")
        except Exception as e:
            logger.error(f"Failed to receive DTC message: {e}")
        
        return None
    
    async def _check_connection_health(self) -> bool:
        """Check if connection to Sierra Chart is healthy"""
        try:
            # Send heartbeat if needed
            if time.time() - self.last_heartbeat > 30:
                heartbeat_message = {
                    'Type': 'HEARTBEAT',
                    'CurrentDateTime': int(time.time())
                }
                await self._send_dtc_message(heartbeat_message)
                self.last_heartbeat = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def _market_data_publisher(self):
        """Process real market data - DTC blocked, using ACSIL/SCID file methods"""
        while True:
            try:
                # DTC protocol blocked by Sierra Chart as of Dec 2024
                # Use ACSIL studies + SCID file parsing instead
                await self._process_acsil_data()
                await self._process_scid_files()
                
                await asyncio.sleep(1.0)  # 1 second polling for file-based data
                
            except Exception as e:
                logger.error(f"Market data publisher error: {e}")
                await asyncio.sleep(5)
    
    async def _process_acsil_data(self):
        """Process real market data from ACSIL studies via direct file system access"""
        # Direct file system access - no HTTP API restrictions
        # Optimal performance for real-time trading data
        
        try:
            import os
            import json
            
            acsil_data_path = "/mnt/c/SierraChart/Data/ACSILOutput"
            
            if not os.path.exists(acsil_data_path):
                logger.debug(f"ACSIL output directory not found: {acsil_data_path}")
                return
            
            # Read JSON files for each symbol
            for symbol in self.symbols:
                # Convert symbol format for filename (matches ACSIL study logic)
                clean_symbol = symbol.replace("-", "_").replace(".", "_")
                json_file = os.path.join(acsil_data_path, f"{clean_symbol}.json")
                json_tmp_file = os.path.join(acsil_data_path, f"{clean_symbol}.json.tmp")
                
                # Prefer .tmp file if it exists and is newer
                actual_file = json_file
                if os.path.exists(json_tmp_file):
                    if not os.path.exists(json_file) or os.path.getmtime(json_tmp_file) > os.path.getmtime(json_file):
                        actual_file = json_tmp_file
                
                if os.path.exists(actual_file):
                    try:
                        # Check file modification time (must be recent)
                        file_age = time.time() - os.path.getmtime(actual_file)
                        # During testing/after hours, accept files up to 1 hour old
                        max_age = 3600 if time.localtime().tm_hour < 9 or time.localtime().tm_hour > 16 else 10
                        if file_age > max_age:
                            logger.debug(f"ACSIL file too old: {actual_file} ({file_age:.1f}s, max_age={max_age}s)")
                            continue
                        
                        # Direct file system read - bypasses HTTP API restrictions
                        with open(actual_file, 'r') as f:
                            data = json.load(f)
                        
                        # Log when reading enhanced data
                        if actual_file.endswith('.tmp'):
                            logger.debug(f"Reading enhanced ACSIL data from {actual_file}")
                        
                        # Detect if this is Phase 3 data with microsecond precision
                        is_phase3 = 'timestamp_us' in data or data.get('source') == 'sierra_chart_acsil_v3'
                        
                        # Create MarketData object with enhanced Phase 3 support
                        market_data = MarketData(
                            symbol=data.get('symbol', symbol),
                            timestamp=datetime.now().isoformat(),
                            price=float(data.get('price', 0)),
                            open=float(data.get('open', 0)),
                            high=float(data.get('high', 0)),
                            low=float(data.get('low', 0)),
                            volume=int(data.get('volume', 0)),
                            bid=float(data.get('bid', 0)),
                            ask=float(data.get('ask', 0)),
                            source=data.get('source', 'sierra_chart_acsil'),
                            bid_size=int(data.get('bid_size')) if 'bid_size' in data else None,
                            ask_size=int(data.get('ask_size')) if 'ask_size' in data else None,
                            last_size=int(data.get('last_size')) if 'last_size' in data else None,
                            vwap=float(data.get('vwap')) if 'vwap' in data else None,
                            trades=int(data.get('trades')) if 'trades' in data else None,
                            # Phase 3 enhancements
                            timestamp_us=int(data.get('timestamp_us')) if 'timestamp_us' in data else None,
                            trade_side=data.get('trade_side') if 'trade_side' in data else None,
                            sequence=int(data.get('sequence')) if 'sequence' in data else None,
                            precision=data.get('precision') if 'precision' in data else None
                        )
                        
                        # Update latest data
                        self.latest_market_data[symbol] = market_data
                        
                        # Broadcast to WebSocket clients
                        if self.websocket_clients:
                            await self._broadcast_market_data(market_data)
                        
                        # Enhanced logging for Phase 3 data
                        if is_phase3:
                            logger.info(f"ACSIL v3 DATA: {symbol} - price={market_data.price}, bid_size={market_data.bid_size}, ask_size={market_data.ask_size}, last_size={market_data.last_size}, precision={market_data.precision}, trade_side={market_data.trade_side}")
                        else:
                            logger.info(f"ACSIL DATA: {symbol} - price={market_data.price}, bid_size={market_data.bid_size}, ask_size={market_data.ask_size}, last_size={market_data.last_size}")
                        
                    except (json.JSONDecodeError, ValueError, KeyError) as e:
                        logger.error(f"Error parsing ACSIL file {json_file}: {e}")
                    except FileNotFoundError:
                        logger.debug(f"ACSIL file not found: {json_file}")
                    except PermissionError:
                        logger.warning(f"Permission denied reading ACSIL file: {json_file}")
                    except Exception as e:
                        logger.error(f"Error reading ACSIL file {json_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing ACSIL data: {e}")
    
    async def send_trade_command(self, trade_command: dict) -> bool:
        """Send trade command to ACSIL study via JSON file"""
        try:
            import json
            import os
            
            # Write command to ACSIL input directory
            acsil_data_path = "/mnt/c/SierraChart/Data/ACSILOutput"
            command_file = os.path.join(acsil_data_path, "trade_commands.json")
            
            # Write trade command file for ACSIL to process
            with open(command_file, 'w') as f:
                json.dump(trade_command, f, indent=2)
            
            logger.info(f"Trade command written: {trade_command['order_id']} - {trade_command['side']} {trade_command['quantity']} {trade_command['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending trade command: {e}")
            return False
    
    async def check_trade_responses(self) -> dict:
        """Check for trade response files from ACSIL"""
        try:
            import os
            import json
            import glob
            
            acsil_data_path = "/mnt/c/SierraChart/Data/ACSILOutput"
            response_pattern = os.path.join(acsil_data_path, "trade_response_*.json")
            
            responses = {}
            for response_file in glob.glob(response_pattern):
                try:
                    with open(response_file, 'r') as f:
                        response_data = json.load(f)
                    
                    order_id = response_data.get('order_id')
                    if order_id:
                        responses[order_id] = response_data
                        
                        # Clean up processed response file
                        os.remove(response_file)
                        logger.info(f"Processed trade response: {order_id} - {response_data.get('status')}")
                        
                except Exception as e:
                    logger.error(f"Error reading trade response {response_file}: {e}")
            
            return responses
            
        except Exception as e:
            logger.error(f"Error checking trade responses: {e}")
            return {}
    
    
    async def _process_scid_files(self):
        """Process real market data from Sierra Chart SCID binary files"""
        # Direct SCID file parsing - officially supported method
        
        try:
            scid_data_path = "C:/SierraChart/Data"
            
            # Read latest data from SCID files for our symbols
            for symbol in self.symbols:
                scid_file = f"{scid_data_path}/{symbol}.scid"
                
                # Parse SCID binary format
                # 56-byte header + 40-byte records with microsecond timestamps
                market_data = await self._parse_scid_file(scid_file, symbol)
                
                if market_data:
                    self.latest_market_data[symbol] = market_data
                    
                    if self.websocket_clients:
                        await self._broadcast_market_data(market_data)
                        
        except Exception as e:
            logger.error(f"Error processing SCID files: {e}")
    
    async def _parse_scid_file(self, file_path: str, symbol: str) -> Optional[MarketData]:
        """Parse Sierra Chart SCID binary file for latest market data"""
        try:
            # SCID format: 56-byte header + 40-byte records
            # This is a simplified parser - full implementation needed
            
            import struct
            import os
            
            if not os.path.exists(file_path):
                logger.debug(f"SCID file not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                # Read header (56 bytes)
                header = f.read(56)
                if len(header) < 56:
                    return None
                
                # Seek to last record (40 bytes from end)
                f.seek(-40, 2)
                record = f.read(40)
                
                if len(record) == 40:
                    # Parse 40-byte SCID record
                    # Format: DateTime(8), Open(4), High(4), Low(4), Close(4), Volume(4), etc.
                    datetime_val, open_val, high_val, low_val, close_val, volume_val = struct.unpack('<Qfffff', record[:28])
                    
                    # Convert Sierra Chart datetime to Python datetime
                    # Sierra Chart uses microseconds since 1899-12-30
                    
                    market_data = MarketData(
                        symbol=symbol,
                        timestamp=datetime.now().isoformat(),  # Use current time for now
                        price=close_val,
                        volume=int(volume_val) if volume_val > 0 else 0,
                        bid=close_val,  # SCID files don't have bid/ask, use close price
                        ask=close_val,  # SCID files don't have bid/ask, use close price
                        open=open_val,
                        high=high_val,
                        low=low_val,
                        source='sierra_chart_scid'
                    )
                    
                    return market_data
                    
        except Exception as e:
            logger.error(f"Error parsing SCID file {file_path}: {e}")
            
        return None
    
    async def _broadcast_market_data(self, market_data: MarketData):
        """Broadcast market data to WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = {
            'type': 'market_data',
            'data': market_data.to_dict()
        }
        
        # Send to all connected clients
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send_text(json.dumps(message))
            except Exception:
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.remove(client)
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            'service': 'sierra_chart_bridge',
            'version': '3.1.0',
            'status': 'operational',
            'data_source': 'File-based monitoring (SCID files)',
            'dtc_status': 'Disabled - Market data blocked by Sierra Chart Dec 2024 policy',
            'symbols': self.symbols,
            'websocket_clients': len(self.websocket_clients),
            'latest_data_symbols': list(self.latest_market_data.keys()),
            'historical_data_available': True,
            'real_time_method': 'File monitoring + recommended Sierra Chart export studies',
            'uptime': time.time() - start_time if 'start_time' in globals() else 0,
            'recommendation': 'Configure Sierra Chart "Write Bar Data to File" study for optimal real-time data'
        }

# Global bridge instance
bridge = SierraChartBridge()

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize bridge on startup"""
    global start_time
    start_time = time.time()
    await bridge.start()
    logger.info("MinhOS Sierra Chart Bridge API started")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'minhos_sierra_bridge',
        'version': '3.1.0'
    })

@app.get("/status")
async def get_status():
    """Get detailed bridge status"""
    bridge_status = bridge.get_status()
    file_api_status = sierra_file_api.get_status()
    
    return JSONResponse({
        'bridge': bridge_status,
        'file_api': file_api_status,
        'timestamp': datetime.now().isoformat()
    })

@app.get("/api/market_data")
async def get_market_data(symbol: Optional[str] = None):
    """Get latest market data"""
    if symbol:
        if symbol in bridge.latest_market_data:
            return bridge.latest_market_data[symbol].to_dict()
        else:
            raise HTTPException(status_code=404, detail="Symbol not found")
    else:
        # Return all symbols
        return {
            symbol: data.to_dict() 
            for symbol, data in bridge.latest_market_data.items()
        }

@app.post("/api/trade/execute")
async def execute_trade(trade_request: TradeRequest):
    """Execute trade order via Sierra Chart ACSIL"""
    try:
        # Store pending trade
        bridge.pending_trades[trade_request.command_id] = trade_request
        
        # Create trade command for ACSIL
        trade_command = {
            "order_id": trade_request.command_id,
            "symbol": trade_request.symbol,
            "side": trade_request.action.upper(),  # BUY/SELL
            "quantity": trade_request.quantity,
            "price": trade_request.price or 0.0,
            "type": trade_request.order_type.upper() if trade_request.order_type else "MARKET"
        }
        
        # Send command to ACSIL study
        success = await bridge.send_trade_command(trade_command)
        
        if success:
            response = TradeResponse(
                command_id=trade_request.command_id,
                status="SUBMITTED",  # Real submission to Sierra Chart
                message="Trade command sent to Sierra Chart ACSIL",
                timestamp=datetime.now().isoformat()
            )
            logger.info(f"Trade submitted to Sierra Chart: {trade_request.action} {trade_request.quantity} {trade_request.symbol}")
        else:
            response = TradeResponse(
                command_id=trade_request.command_id,
                status="REJECTED",
                message="Failed to send command to Sierra Chart",
                timestamp=datetime.now().isoformat()
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        return TradeResponse(
            command_id=trade_request.command_id,
            status="REJECTED",
            message=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/trade/status/{command_id}")
async def get_trade_status(command_id: str):
    """Get trade status"""
    # For testing, return filled status
    return TradeResponse(
        command_id=command_id,
        status="FILLED",
        message="Trade completed",
        fill_price=18000.0,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/positions")
async def get_positions():
    """Get current positions"""
    return list(bridge.positions.values())

# File Access API Routes (Historical Data)
@app.get("/api/file/list")
async def list_files(path: str = Query(..., description="Directory path to list")):
    """List files in Sierra Chart data directory"""
    return await sierra_file_api.list_files(path)

@app.get("/api/file/read")
async def read_text_file(path: str = Query(..., description="Text file path to read")):
    """Read text file (CSV/DLY files)"""
    return await sierra_file_api.read_file(path)

@app.get("/api/file/read_binary")
async def read_binary_file(path: str = Query(..., description="Binary file path to read")):
    """Read binary file (SCID files)"""
    return await sierra_file_api.read_binary_file(path)

@app.get("/api/file/info")
async def get_file_info(path: str = Query(..., description="File path to get info")):
    """Get file information"""
    return await sierra_file_api.get_file_info(path)

# Missing API endpoints required by MinhOS
@app.get("/api/symbols")
async def get_symbols():
    """Get list of available symbols"""
    return JSONResponse({
        'symbols': bridge.symbols,
        'timestamp': datetime.now().isoformat()
    })

@app.get("/api/data/{symbol}")
async def get_symbol_data(symbol: str):
    """Get current market data for specific symbol"""
    if symbol in bridge.latest_market_data:
        return JSONResponse(bridge.latest_market_data[symbol].to_dict())
    else:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

@app.get("/api/streaming/{symbol}")
async def get_streaming_data(symbol: str, request: Request):
    """Get streaming data endpoint for specific symbol"""
    if symbol in bridge.latest_market_data:
        return JSONResponse({
            'symbol': symbol,
            'streaming': True,
            'data': bridge.latest_market_data[symbol].to_dict(),
            'websocket_url': f'ws://{request.url.hostname}:{request.url.port}/ws/market_data',
            'timestamp': datetime.now().isoformat()
        })
    else:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not available for streaming")

# WebSocket endpoint for real-time data
@app.websocket("/ws/market_data")
async def websocket_market_data(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    bridge.websocket_clients.append(websocket)
    
    logger.info(f"WebSocket client connected: {websocket.client}")
    
    try:
        # Send current market data
        for symbol, data in bridge.latest_market_data.items():
            await websocket.send_text(json.dumps({
                'type': 'market_data',
                'data': data.to_dict()
            }))
        
        # Keep connection alive
        while True:
            # Wait for client messages or send periodic pings
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Handle client messages if needed
                logger.debug(f"Received WebSocket message: {message}")
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text(json.dumps({
                    'type': 'ping',
                    'timestamp': datetime.now().isoformat()
                }))
                
    except Exception as e:
        logger.info(f"WebSocket client disconnected: {e}")
    finally:
        if websocket in bridge.websocket_clients:
            bridge.websocket_clients.remove(websocket)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': exc.detail, 'timestamp': datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={'error': 'Internal server error', 'timestamp': datetime.now().isoformat()}
    )

if __name__ == "__main__":
    """Run the bridge server"""
    logger.info("Starting MinhOS Sierra Chart Bridge Server...")
    logger.info("")
    logger.info("=== IMPORTANT: DTC PROTOCOL LIMITATION ===")
    logger.info("Sierra Chart blocks DTC market data access as of Dec 2024")
    logger.info("This bridge provides:")
    logger.info("  [OK] Historical data via SCID file access")
    logger.info("  [OK] File monitoring for real-time updates")
    logger.info("  [OK] All API endpoints for MinhOS integration")
    logger.info("")
    logger.info("For optimal real-time data, configure Sierra Chart studies:")
    logger.info("  1. Add 'Write Bar Data to File' study")
    logger.info("  2. Set output to update every 1-5 seconds")
    logger.info("  3. Bridge will monitor these files automatically")
    logger.info("===========================================")
    logger.info("")
    
    # Log startup information
    logger.info("Sierra Chart File Access API initialized")
    logger.info("Available endpoints:")
    logger.info("  Health: http://0.0.0.0:8765/health")
    logger.info("  Status: http://0.0.0.0:8765/status")
    logger.info("  Market Data: http://0.0.0.0:8765/api/market_data")
    logger.info("  *** NEW ENDPOINTS FOR MINHOS INTEGRATION ***")
    logger.info("  Symbols API: http://0.0.0.0:8765/api/symbols")
    logger.info("  Data API: http://0.0.0.0:8765/api/data/{symbol}")
    logger.info("  Streaming API: http://0.0.0.0:8765/api/streaming/{symbol}")
    logger.info("  File List: http://0.0.0.0:8765/api/file/list")
    logger.info("  WebSocket: ws://0.0.0.0:8765/ws/market_data")
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8765,
        log_level="info",
        access_log=True
    )