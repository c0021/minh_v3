#!/usr/bin/env python3
"""
Market Data Store Adapter
========================

Provides compatibility layer for existing services to use the unified market data store.
"""

import asyncio
from typing import Dict, List, Optional, Callable
import logging
from datetime import datetime

from .market_data_store import get_market_data_store, MarketDataStore
from ..models.market import MarketData


logger = logging.getLogger(__name__)


class MarketDataAdapter:
    """
    Adapter to make the unified market data store compatible with existing service interfaces.
    Provides both synchronous and asynchronous APIs.
    """
    
    def __init__(self):
        self._store = get_market_data_store()
        self._callbacks: List[Callable] = []
        self._subscriber_task = None
        self._running = False
    
    @property
    def store(self) -> MarketDataStore:
        """Direct access to the underlying store"""
        return self._store
    
    # Synchronous API (for compatibility)
    
    def get_latest_data(self, symbol: Optional[str] = None) -> Dict[str, MarketData]:
        """Get latest market data (sync)"""
        return self._store.get_latest(symbol)
    
    def get_historical_data(self, symbol: str, limit: Optional[int] = 1000) -> List[MarketData]:
        """Get historical data (sync)"""
        return self._store.get_history(symbol, limit)
    
    def add_data(self, data: MarketData) -> None:
        """Add market data (sync wrapper)"""
        # Run async method in new event loop if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule as a task if loop is already running
                asyncio.create_task(self._store.add(data))
            else:
                # Run directly if no loop is running
                loop.run_until_complete(self._store.add(data))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(self._store.add(data))
    
    # Asynchronous API
    
    async def async_add_data(self, data: MarketData) -> None:
        """Add market data (async)"""
        await self._store.add(data)
    
    async def subscribe(self, callback: Callable[[MarketData], None]) -> None:
        """Subscribe to market data updates with a callback"""
        self._callbacks.append(callback)
        
        # Start subscriber task if not running
        if not self._running:
            self._running = True
            self._subscriber_task = asyncio.create_task(self._run_subscriber())
    
    def unsubscribe(self, callback: Callable[[MarketData], None]) -> None:
        """Unsubscribe from market data updates"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def _run_subscriber(self):
        """Run subscriber loop to distribute updates to callbacks"""
        queue = await self._store.subscribe()
        
        try:
            while self._running and self._callbacks:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    
                    # Call all callbacks
                    for callback in self._callbacks[:]:  # Copy to avoid modification during iteration
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(data)
                            else:
                                callback(data)
                        except Exception as e:
                            logger.error(f"Error in market data callback: {e}")
                            
                except asyncio.TimeoutError:
                    continue
                    
        except asyncio.CancelledError:
            pass
        finally:
            self._store.unsubscribe(queue)
            self._running = False
    
    async def start(self):
        """Start the adapter services"""
        await self._store.start_cleanup_task()
        logger.info("Market data adapter started")
    
    async def stop(self):
        """Stop the adapter services"""
        self._running = False
        
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
        
        await self._store.stop_cleanup_task()
        logger.info("Market data adapter stopped")
    
    # Compatibility methods for existing services
    
    @property
    def latest_data(self) -> Dict[str, MarketData]:
        """Property for backward compatibility"""
        return self._store.get_latest()
    
    def broadcast_market_data(self, data: MarketData) -> None:
        """Broadcast market data (backward compatibility)"""
        self.add_data(data)
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get latest data for a symbol (backward compatibility)"""
        return self._store.get_latest(symbol).get(symbol)
    
    def get_all_market_data(self) -> Dict[str, MarketData]:
        """Get all latest market data (backward compatibility)"""
        return self._store.get_latest()
    
    def get_symbols(self) -> List[str]:
        """Get all available symbols"""
        return self._store.get_symbols()
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        return self._store.get_stats()
    
    def get_historical_range(self, symbol: str) -> Optional[tuple]:
        """Get the historical data range for a symbol (start_date, end_date)"""
        try:
            # Get all historical data for the symbol to find range
            historical_data = self.get_historical_data(symbol, limit=None)
            
            if not historical_data:
                return None
                
            # Extract timestamps and find min/max
            timestamps = []
            for data in historical_data:
                try:
                    # Handle both string and float timestamps
                    if isinstance(data.timestamp, str):
                        # Skip string timestamps that can't be converted
                        continue
                    timestamps.append(float(data.timestamp))
                except (ValueError, TypeError):
                    continue
                    
            if timestamps:
                start_date = datetime.fromtimestamp(min(timestamps))
                end_date = datetime.fromtimestamp(max(timestamps))
                return (start_date, end_date)
            
            return None
        except Exception as e:
            logger.error(f"Error getting historical range for {symbol}: {e}")
            return None


# Global adapter instance
_adapter_instance: Optional[MarketDataAdapter] = None


def get_market_data_adapter() -> MarketDataAdapter:
    """Get or create the singleton market data adapter"""
    global _adapter_instance
    
    if _adapter_instance is None:
        _adapter_instance = MarketDataAdapter()
    
    return _adapter_instance