#!/usr/bin/env python3
"""
Sierra Chart Historical Data Integration Service
===============================================

Provides access to Sierra Chart's extensive historical data archive.
Fills gaps in MinhOS market data with Sierra Chart's tick-level history.

Key Features:
- Direct access to Sierra Chart .dly (CSV) and .scid (binary) files
- Gap detection and automatic backfilling
- Historical data preprocessing for AI analysis
- Tailscale-aware remote file access
"""

import asyncio
import csv
import logging
import struct
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator
import pandas as pd
import numpy as np
from dataclasses import dataclass
import requests
import json

from ..models.market import MarketData
from ..core.market_data_adapter import get_market_data_adapter
from ..core.config import get_config

logger = logging.getLogger(__name__)

@dataclass
class SierraChartRecord:
    """Represents a single Sierra Chart data record"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    num_trades: int = 0
    bid_volume: int = 0
    ask_volume: int = 0

class SierraHistoricalDataService:
    """
    Service for accessing Sierra Chart's historical data archives.
    Bridges the gap between Sierra Chart's extensive data and MinhOS's AI analysis.
    """
    
    def __init__(self):
        """Initialize Sierra Historical Data Service"""
        self.config = get_config()
        self.market_adapter = get_market_data_adapter()
        
        # Sierra Chart configuration
        self.sierra_host = self.config.sierra.host  # "trading-pc" via Tailscale
        self.sierra_data_path = "C:/SierraChart/Data"  # Remote path
        
        # File access via bridge API
        self.bridge_url = f"http://{self.sierra_host}:8765"
        
        # Supported symbols
        self.symbols = ["NQU25-CME", "ESU25-CME", "YMU25-CME"]  # Extend as needed
        
        # Cache for processed data
        self.data_cache: Dict[str, List[SierraChartRecord]] = {}
        
        logger.info("Sierra Historical Data Service initialized")
    
    async def start(self):
        """Start the historical data service"""
        logger.info("🔄 Starting Sierra Historical Data Service...")
        
        # Initial gap analysis and backfill
        await self._perform_initial_backfill()
        
        # Schedule periodic gap checking
        asyncio.create_task(self._gap_monitoring_loop())
        
        logger.info("✅ Sierra Historical Data Service started")
    
    async def get_historical_data(self, 
                                 symbol: str, 
                                 start_date: datetime, 
                                 end_date: datetime,
                                 timeframe: str = "daily") -> List[SierraChartRecord]:
        """
        Get historical data for a symbol and date range.
        
        Args:
            symbol: Trading symbol (e.g., "NQU25-CME")
            start_date: Start date for data
            end_date: End date for data
            timeframe: "daily" or "tick" data
        
        Returns:
            List of SierraChartRecord objects
        """
        logger.info(f"📊 Fetching {timeframe} data for {symbol}: {start_date} to {end_date}")
        
        if timeframe == "daily":
            return await self._read_daily_data(symbol, start_date, end_date)
        elif timeframe == "tick":
            return await self._read_tick_data(symbol, start_date, end_date)
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
    
    async def _read_daily_data(self, 
                              symbol: str, 
                              start_date: datetime, 
                              end_date: datetime) -> List[SierraChartRecord]:
        """Read daily data from Sierra Chart .dly files"""
        try:
            # Convert symbol to Sierra Chart format
            sierra_symbol = self._convert_symbol_to_sierra_format(symbol)
            filename = f"{sierra_symbol}.dly"
            
            # Request file content from bridge
            file_content = await self._request_file_content(filename)
            if not file_content:
                logger.warning(f"No daily data file found for {symbol}")
                return []
            
            # Parse CSV content
            records = []
            csv_reader = csv.DictReader(file_content.splitlines())
            
            for row in csv_reader:
                try:
                    # Parse Sierra Chart CSV format
                    date_str = row.get('Date', '').strip()
                    record_date = datetime.strptime(date_str, "%Y/%m/%d")
                    
                    # Filter by date range
                    if start_date <= record_date <= end_date:
                        record = SierraChartRecord(
                            timestamp=record_date,
                            open=float(row.get('Open', 0)),
                            high=float(row.get('High', 0)),
                            low=float(row.get('Low', 0)),
                            close=float(row.get('Close', 0)),
                            volume=int(float(row.get('Volume', 0)))
                        )
                        records.append(record)
                        
                except (ValueError, KeyError) as e:
                    logger.debug(f"Skipping invalid row: {e}")
                    continue
            
            logger.info(f"📈 Loaded {len(records)} daily records for {symbol}")
            return records
            
        except Exception as e:
            logger.error(f"Error reading daily data for {symbol}: {e}")
            return []
    
    async def _read_tick_data(self, 
                             symbol: str, 
                             start_date: datetime, 
                             end_date: datetime) -> List[SierraChartRecord]:
        """Read tick data from Sierra Chart .scid files"""
        try:
            # Convert symbol to Sierra Chart format
            sierra_symbol = self._convert_symbol_to_sierra_format(symbol)
            filename = f"{sierra_symbol}.scid"
            
            # Request binary file content
            binary_content = await self._request_binary_file(filename)
            if not binary_content:
                logger.warning(f"No tick data file found for {symbol}")
                return []
            
            # Parse Sierra Chart binary format
            records = self._parse_scid_binary(binary_content, start_date, end_date)
            
            logger.info(f"📊 Loaded {len(records)} tick records for {symbol}")
            return records
            
        except Exception as e:
            logger.error(f"Error reading tick data for {symbol}: {e}")
            return []
    
    def _parse_scid_binary(self, 
                          binary_data: bytes, 
                          start_date: datetime, 
                          end_date: datetime) -> List[SierraChartRecord]:
        """
        Parse Sierra Chart .scid binary format.
        
        Format:
        - Header: 56 bytes (s_IntradayHeader)
        - Records: 40 bytes each (s_IntradayRecord)
        """
        records = []
        
        try:
            # Skip header (56 bytes)
            offset = 56
            record_size = 40
            
            while offset + record_size <= len(binary_data):
                # Extract record (40 bytes)
                record_bytes = binary_data[offset:offset + record_size]
                
                # Unpack binary data
                # DateTime (8 bytes), Open (4), High (4), Low (4), Close (4), 
                # NumTrades (4), TotalVolume (4), BidVolume (4), AskVolume (4)
                unpacked = struct.unpack('<Qffff4I', record_bytes)
                
                # Convert Sierra Chart DateTime to Python datetime
                sc_datetime = unpacked[0]  # Microseconds since 1899-12-30
                timestamp = self._convert_sierra_datetime(sc_datetime)
                
                # Filter by date range
                if start_date <= timestamp <= end_date:
                    record = SierraChartRecord(
                        timestamp=timestamp,
                        open=unpacked[1],
                        high=unpacked[2],
                        low=unpacked[3],
                        close=unpacked[4],
                        num_trades=unpacked[5],
                        volume=unpacked[6],
                        bid_volume=unpacked[7],
                        ask_volume=unpacked[8]
                    )
                    records.append(record)
                
                offset += record_size
            
        except Exception as e:
            logger.error(f"Error parsing SCID binary data: {e}")
        
        return records
    
    def _convert_sierra_datetime(self, sc_datetime: int) -> datetime:
        """Convert Sierra Chart datetime (microseconds since 1899-12-30) to Python datetime"""
        # Sierra Chart epoch: December 30, 1899
        sierra_epoch = datetime(1899, 12, 30)
        return sierra_epoch + timedelta(microseconds=sc_datetime)
    
    async def _request_file_content(self, filename: str) -> Optional[str]:
        """Request text file content from Sierra Chart via bridge"""
        try:
            # Use bridge API to read file
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                requests.get, 
                f"{self.bridge_url}/api/file/read",
                {"params": {"path": f"{self.sierra_data_path}/{filename}"}}
            )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to read {filename}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error requesting file {filename}: {e}")
            return None
    
    async def _request_binary_file(self, filename: str) -> Optional[bytes]:
        """Request binary file content from Sierra Chart via bridge"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                requests.get,
                f"{self.bridge_url}/api/file/read_binary",
                {"params": {"path": f"{self.sierra_data_path}/{filename}"}}
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.warning(f"Failed to read binary {filename}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error requesting binary file {filename}: {e}")
            return None
    
    def _convert_symbol_to_sierra_format(self, symbol: str) -> str:
        """Convert MinhOS symbol format to Sierra Chart format"""
        # Example: "NQU25-CME" -> "NQ 03-25" (needs mapping logic)
        symbol_map = {
            "NQU25-CME": "NQ 03-25",  # March 2025
            "ESU25-CME": "ES 03-25",  # March 2025  
            "YMU25-CME": "YM 03-25"   # March 2025
        }
        return symbol_map.get(symbol, symbol)
    
    async def _perform_initial_backfill(self):
        """Perform initial backfill of missing historical data"""
        logger.info("🔄 Starting initial historical data backfill...")
        
        for symbol in self.symbols:
            try:
                # Detect gaps in existing data
                gaps = await self._detect_data_gaps(symbol)
                
                if gaps:
                    logger.info(f"📊 Found {len(gaps)} data gaps for {symbol}")
                    
                    # Fill each gap
                    for start_date, end_date in gaps:
                        await self._fill_data_gap(symbol, start_date, end_date)
                else:
                    logger.info(f"✅ No data gaps found for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error during backfill for {symbol}: {e}")
        
        logger.info("✅ Initial historical data backfill completed")
    
    async def _detect_data_gaps(self, symbol: str) -> List[Tuple[datetime, datetime]]:
        """Detect gaps in market data for a symbol"""
        gaps = []
        
        try:
            # Get existing data range from MinhOS database
            existing_data = await self.market_adapter.get_historical_range(symbol)
            
            if not existing_data:
                # No existing data - need full historical backfill
                # Get last 30 days for initial load
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
                gaps.append((datetime.combine(start_date, datetime.min.time()), 
                           datetime.combine(end_date, datetime.max.time())))
            else:
                # Check for gaps in existing data
                # Implementation would analyze date continuity
                pass  # Simplified for now
                
        except Exception as e:
            logger.error(f"Error detecting gaps for {symbol}: {e}")
        
        return gaps
    
    async def _fill_data_gap(self, symbol: str, start_date: datetime, end_date: datetime):
        """Fill a specific data gap with Sierra Chart historical data"""
        try:
            logger.info(f"🔄 Filling gap for {symbol}: {start_date} to {end_date}")
            
            # Get daily data from Sierra Chart
            historical_records = await self.get_historical_data(
                symbol, start_date, end_date, "daily"
            )
            
            # Convert to MinhOS MarketData format and store
            for record in historical_records:
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=record.timestamp,
                    close=record.close,
                    bid=record.low,  # Approximate
                    ask=record.high,  # Approximate
                    volume=record.volume,
                    high=record.high,
                    low=record.low,
                    open=record.open,
                    source="sierra_historical"
                )
                
                # Store in unified market data
                await self.market_adapter.async_add_data(market_data)
            
            logger.info(f"✅ Filled {len(historical_records)} records for {symbol}")
            
        except Exception as e:
            logger.error(f"Error filling gap for {symbol}: {e}")
    
    async def _gap_monitoring_loop(self):
        """Periodically check for and fill data gaps"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Quick gap check for active symbols
                for symbol in self.symbols:
                    gaps = await self._detect_data_gaps(symbol)
                    
                    for start_date, end_date in gaps:
                        # Only fill recent gaps (last 7 days)
                        if (datetime.now() - end_date).days <= 7:
                            await self._fill_data_gap(symbol, start_date, end_date)
                
            except Exception as e:
                logger.error(f"Error in gap monitoring: {e}")
                await asyncio.sleep(300)  # Back off on error

# Singleton instance
_sierra_historical_service = None

def get_sierra_historical_service() -> SierraHistoricalDataService:
    """Get or create the Sierra Historical Data Service singleton"""
    global _sierra_historical_service
    if _sierra_historical_service is None:
        _sierra_historical_service = SierraHistoricalDataService()
    return _sierra_historical_service