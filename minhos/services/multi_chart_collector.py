#!/usr/bin/env python3
"""
MinhOS v3 Multi-Chart Data Collector (Migrated)
===============================================

MIGRATED: Now uses unified market data store instead of local storage.

Collects data from multiple Sierra Chart symbols and timeframes for comprehensive market analysis.

Your Setup:
- NQ 1min (primary trading chart)
- NQ Daily  
- NQ 30min
- ES 1min
- VIX 1min

This service aggregates data from all charts and provides a unified view for the AI brain
and trading strategies to make multi-timeframe and cross-asset decisions.

Key Features:
- Multi-symbol data collection (NQ, ES, VIX)
- Multi-timeframe analysis (1min, 30min, daily) 
- Correlation analysis between assets
- Market regime detection across timeframes
- Data synchronization and storage
- Real-time broadcasting to MinhOS services

Author: MinhOS v3 System
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

from minhos.core.base_service import BaseService
from minhos.services.sierra_client import SierraClient
from minhos.models.market import MarketData

# Import unified market data store
from ..core.market_data_adapter import get_market_data_adapter

logger = logging.getLogger(__name__)

@dataclass
class MultiChartData:
    """Comprehensive multi-chart market data"""
    timestamp: str
    primary_symbol: str = "NQU25-CME"
    
    # NQ Data (multiple timeframes)
    nq_1min: Optional[MarketData] = None
    nq_30min: Optional[MarketData] = None  
    nq_daily: Optional[MarketData] = None
    
    # ES Data
    es_1min: Optional[MarketData] = None
    
    # VIX Data  
    vix_1min: Optional[MarketData] = None
    
    # Derived Analytics
    nq_es_spread: Optional[float] = None
    vix_level: Optional[str] = None  # LOW, NORMAL, HIGH, EXTREME
    market_regime: Optional[str] = None  # TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE
    timeframe_alignment: Optional[str] = None  # BULLISH, BEARISH, MIXED, NEUTRAL

@dataclass  
class ChartConfiguration:
    """Configuration for each chart"""
    symbol: str
    timeframe: str
    primary: bool = False
    weight: float = 1.0
    enabled: bool = True

class MultiChartCollector(BaseService):
    """Collects and analyzes data from multiple Sierra Chart symbols/timeframes"""
    
    def __init__(self, sierra_client: SierraClient):
        super().__init__("multi_chart_collector", 9004)
        self.sierra_client = sierra_client
        
        # Chart configurations matching your Sierra Chart setup
        self.chart_configs = {
            'NQ_1MIN': ChartConfiguration('NQU25-CME', '1min', primary=True, weight=1.0),
            'NQ_30MIN': ChartConfiguration('NQU25-CME', '30min', weight=0.8),
            'NQ_DAILY': ChartConfiguration('NQU25-CME', 'daily', weight=0.6),
            'ES_1MIN': ChartConfiguration('ESU25-CME', '1min', weight=0.7),
            'VIX_1MIN': ChartConfiguration('VIX', '1min', weight=0.5)
        }
        
        # MIGRATED: Use unified market data store instead of local storage
        self.market_data_adapter = get_market_data_adapter()
        self.chart_data: Dict[str, Any] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.subscribers = set()
        self.running = False
        
        # Analytics
        self.last_analysis: Optional[MultiChartData] = None
        self.analysis_interval = 5.0  # Analyze every 5 seconds
        
        # Subscribers
        self.subscribers = set()
        
        logger.info("Multi-Chart Collector initialized")
    
    async def start(self):
        """Start the multi-chart collector"""
        await super().start()
        
        # Start data collection
        asyncio.create_task(self._data_collection_loop())
        
        # Start analysis
        asyncio.create_task(self._analysis_loop())
        
        logger.info("Multi-Chart Collector started")
    
    async def _data_collection_loop(self):
        """Main data collection loop"""
        while self.running:
            try:
                # Collect data from all configured charts
                await self._collect_all_data()
                
                # Wait before next collection
                await asyncio.sleep(1.0)  # Collect every second
                
            except Exception as e:
                logger.error(f"Data collection error: {e}")
                await asyncio.sleep(5.0)
    
    async def _collect_all_data(self):
        """MIGRATED: Collect data from unified store for all configured charts"""
        for chart_id, config in self.chart_configs.items():
            if not config.enabled:
                continue
                
            try:
                # MIGRATED: Get current market data from unified store
                market_data = self.market_data_adapter.get_market_data(config.symbol)
                if market_data:
                    self.chart_data[chart_id] = market_data
                    logger.debug(f"Updated {chart_id}: {market_data.symbol} @ ${market_data.close}")
                
            except Exception as e:
                logger.error(f"Failed to collect data for {chart_id}: {e}")
    
    async def _analysis_loop(self):
        """Analyze collected data and generate insights"""
        while self.running:
            try:
                # Perform multi-chart analysis
                analysis = await self._perform_analysis()
                
                if analysis:
                    self.last_analysis = analysis
                    await self._broadcast_analysis(analysis)
                
                await asyncio.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                await asyncio.sleep(10.0)
    
    async def _perform_analysis(self) -> Optional[MultiChartData]:
        """MIGRATED: Perform comprehensive multi-chart analysis using unified store"""
        if not self.chart_data:
            return None
        
        try:
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # MIGRATED: Extract data for each asset from chart_data
            nq_data = self.chart_data.get('NQ_1MIN')
            es_data = self.chart_data.get('ES_1MIN')  
            vix_data = self.chart_data.get('VIX_1MIN')
            
            if not nq_data:
                return None  # Need at least primary symbol
            
            # Calculate NQ/ES spread (approximate - would need actual ES data)
            nq_es_spread = None
            if es_data and nq_data:
                # Normalize spread (NQ is ~4x ES price typically)
                estimated_es_equivalent = nq_data.price / 4.0
                if es_data.price > 0:
                    nq_es_spread = estimated_es_equivalent - es_data.price
            
            # Analyze VIX level
            vix_level = self._analyze_vix_level(vix_data) if vix_data else None
            
            # Determine market regime
            market_regime = await self._determine_market_regime()
            
            # Analyze timeframe alignment
            timeframe_alignment = await self._analyze_timeframe_alignment()
            
            # Create comprehensive analysis
            analysis = MultiChartData(
                timestamp=timestamp,
                primary_symbol="NQU25-CME",
                nq_1min=nq_data,
                es_1min=es_data,
                vix_1min=vix_data,
                nq_es_spread=nq_es_spread,
                vix_level=vix_level,
                market_regime=market_regime,
                timeframe_alignment=timeframe_alignment
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis calculation error: {e}")
            return None
    
    def _analyze_vix_level(self, vix_data: MarketData) -> str:
        """Analyze VIX level and return categorization"""
        if not vix_data or vix_data.price <= 0:
            return "UNKNOWN"
        
        vix_price = vix_data.price
        
        if vix_price < 12:
            return "EXTREMELY_LOW"
        elif vix_price < 16:
            return "LOW"
        elif vix_price < 20:
            return "NORMAL"
        elif vix_price < 30:
            return "HIGH"
        else:
            return "EXTREME"
    
    async def _determine_market_regime(self) -> str:
        """Determine current market regime based on multi-chart data"""
        nq_data = self.chart_data.get('NQ_1MIN')
        if not nq_data:
            return "UNKNOWN"
        
        # Get recent price history from unified store
        nq_config = self.chart_configs.get('NQ_1MIN')
        if not nq_config:
            return "UNKNOWN"
            
        nq_history = self.market_data_adapter.get_historical_data(nq_config.symbol, limit=10)
        if len(nq_history) < 10:
            return "INSUFFICIENT_DATA"
        
        # Calculate trend
        recent_prices = [d.price for d in nq_history[-10:]]
        first_half_avg = statistics.mean(recent_prices[:5])
        second_half_avg = statistics.mean(recent_prices[5:])
        
        price_change_pct = (second_half_avg - first_half_avg) / first_half_avg * 100
        
        # Calculate volatility
        price_changes = [abs(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] * 100 
                        for i in range(1, len(recent_prices))]
        avg_volatility = statistics.mean(price_changes)
        
        # Determine regime
        if avg_volatility > 0.5:  # High volatility threshold
            return "VOLATILE"
        elif price_change_pct > 0.2:
            return "TRENDING_UP"
        elif price_change_pct < -0.2:
            return "TRENDING_DOWN"
        else:
            return "RANGING"
    
    async def _analyze_timeframe_alignment(self) -> str:
        """Analyze alignment across different timeframes"""
        # Placeholder for timeframe analysis
        # In real implementation, this would compare trends across 1min, 30min, daily
        # For now, return based on current trend
        
        market_regime = await self._determine_market_regime()
        
        if market_regime == "TRENDING_UP":
            return "BULLISH"
        elif market_regime == "TRENDING_DOWN":
            return "BEARISH"
        elif market_regime == "VOLATILE":
            return "MIXED"
        else:
            return "NEUTRAL"
    
    async def _broadcast_analysis(self, analysis: MultiChartData):
        """Broadcast analysis to subscribers"""
        if not self.subscribers:
            return
        
        message = {
            'type': 'multi_chart_analysis',
            'data': asdict(analysis)
        }
        
        # Convert MarketData objects to dicts for JSON serialization
        data = message['data']
        for key, value in data.items():
            if isinstance(value, MarketData):
                data[key] = asdict(value)
        
        # Broadcast to all subscribers
        disconnected = []
        for websocket in self.subscribers.copy():
            try:
                await websocket.send(json.dumps(message, default=str))
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected subscribers
        for websocket in disconnected:
            self.subscribers.discard(websocket)
        
        logger.debug(f"Broadcasted analysis to {len(self.subscribers)} subscribers")
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections"""
        self.subscribers.add(websocket)
        logger.info(f"New multi-chart subscriber: {websocket.remote_address}")
        
        try:
            # Send current analysis if available
            if self.last_analysis:
                await self._broadcast_analysis(self.last_analysis)
            
            # Keep connection alive
            async for message in websocket:
                try:
                    request = json.loads(message)
                    await self._handle_subscriber_request(websocket, request)
                except Exception as e:
                    logger.error(f"WebSocket message error: {e}")
        
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            self.subscribers.discard(websocket)
            logger.info("Multi-chart subscriber disconnected")
    
    async def _handle_subscriber_request(self, websocket, request: Dict):
        """Handle requests from subscribers"""
        req_type = request.get('type')
        
        if req_type == 'get_current_analysis':
            if self.last_analysis:
                await websocket.send(json.dumps({
                    'type': 'current_analysis',
                    'data': asdict(self.last_analysis)
                }, default=str))
        
        elif req_type == 'get_chart_data':
            chart_id = request.get('chart_id', 'NQ_1MIN')
            data = self.chart_data.get(chart_id)
            if data:
                await websocket.send(json.dumps({
                    'type': 'chart_data',
                    'chart_id': chart_id,
                    'data': asdict(data)
                }, default=str))
        
        elif req_type == 'get_historical_data':
            chart_id = request.get('chart_id', 'NQ_1MIN')
            limit = min(request.get('limit', 100), 1000)
            
            # Get historical data from unified store
            config = self.chart_configs.get(chart_id)
            if config:
                history = self.market_data_adapter.get_historical_data(config.symbol, limit=limit)
                await websocket.send(json.dumps({
                    'type': 'historical_data',
                    'chart_id': chart_id,
                    'data': [asdict(d) for d in history]
                }, default=str))
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Unknown chart_id: {chart_id}'
                }, default=str))
    
    def get_status(self) -> Dict:
        """Get current service status"""
        return {
            'service': 'multi_chart_collector',
            'charts_configured': len(self.chart_configs),
            'charts_active': len(self.chart_data),
            'total_data_points': sum(len(self.market_data_adapter.get_historical_data(config.symbol, limit=100)) for config in self.chart_configs.values()),
            'subscribers': len(self.subscribers),
            'last_analysis_time': self.last_analysis.timestamp if self.last_analysis else None,
            'current_symbols': list(self.chart_data.keys())
        }
    
    def get_current_analysis(self) -> Optional[MultiChartData]:
        """Get the latest multi-chart analysis"""
        return self.last_analysis
    
    def get_chart_data(self, chart_id: str) -> Optional[MarketData]:
        """MIGRATED: Get current data for specific chart from unified store"""
        config = self.chart_configs.get(chart_id)
        if config:
            return self.market_data_adapter.get_market_data(config.symbol)
        return None
    
    def get_historical_data(self, chart_id: str, limit: int = 100) -> List[MarketData]:
        """MIGRATED: Get historical data for specific chart from unified store"""
        config = self.chart_configs.get(chart_id)
        if config:
            return self.market_data_adapter.get_historical_data(config.symbol, limit=limit)
        return []
    
    # Abstract method implementations required by BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        # Chart configurations already set up in __init__
        pass
        
    async def _start_service(self):
        """Start service-specific functionality"""
        logger.info("Starting Multi-Chart Collector background tasks...")
        self.running = True
        
        # Start data collection tasks
        asyncio.create_task(self._data_collection_loop())
        asyncio.create_task(self._analysis_loop())
        
    async def _stop_service(self):
        """Stop service-specific functionality"""
        logger.info("Stopping Multi-Chart Collector...")
        self.running = False
        
    async def _cleanup(self):
        """Cleanup service resources"""
        self.chart_data.clear()
        self.analysis_results.clear()
        self.subscribers.clear()

# Service factory function
async def create_multi_chart_collector(sierra_client: SierraClient) -> MultiChartCollector:
    """Create and initialize Multi-Chart Collector"""
    collector = MultiChartCollector(sierra_client)
    await collector.start()
    return collector

if __name__ == "__main__":
    # Test mode
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        # Create mock sierra client for testing
        from unittest.mock import AsyncMock
        mock_sierra = AsyncMock()
        
        collector = await create_multi_chart_collector(mock_sierra)
        
        try:
            while True:
                status = collector.get_status()
                logger.info(f"Multi-Chart Status: {status}")
                await asyncio.sleep(30)
        except KeyboardInterrupt:
            logger.info("Shutting down collector...")
        finally:
            await collector.stop()
    
    asyncio.run(main())