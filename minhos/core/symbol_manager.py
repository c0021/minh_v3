#!/usr/bin/env python3
"""
MinhOS v3 Centralized Symbol Management System
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class AssetType(Enum):
    FUTURES = "futures"
    FOREX = "forex"
    INDEX = "index"

@dataclass
class SymbolConfig:
    symbol: str
    contract_spec: Optional[str]
    asset_type: AssetType
    primary: bool
    timeframes: List[str]
    subscription_priority: int
    enabled: bool = True
    
    def get_current_symbol(self) -> str:
        """Get the current symbol (with rollover logic for futures)"""
        if self.asset_type == AssetType.FUTURES and self.contract_spec:
            # For futures, return the current contract (e.g., NQU25-CME)
            return f"{self.symbol}-{self.contract_spec}"
        else:
            # For non-futures, return the symbol as-is
            return self.symbol

class SymbolManager:
    def __init__(self):
        self.symbols = {
            'NQ': SymbolConfig(
                symbol='NQU25',
                contract_spec='CME',
                asset_type=AssetType.FUTURES,
                primary=True,
                timeframes=['1min', '30min', 'daily'],
                subscription_priority=1,
                enabled=True
            ),
            'ES': SymbolConfig(
                symbol='ESU25',
                contract_spec='CME',
                asset_type=AssetType.FUTURES,
                primary=False,
                timeframes=['1min'],
                subscription_priority=2,
                enabled=True
            ),
            'EURUSD': SymbolConfig(
                symbol='EURUSD',
                contract_spec=None,
                asset_type=AssetType.FOREX,
                primary=False,
                timeframes=['1min'],
                subscription_priority=3,
                enabled=False  # DISABLED for 3-symbol focus
            ),
            'XAUUSD': SymbolConfig(
                symbol='XAUUSD',
                contract_spec=None,
                asset_type=AssetType.FOREX,
                primary=False,
                timeframes=['1min'],
                subscription_priority=4,
                enabled=False  # DISABLED for 3-symbol focus
            ),
            'VIX': SymbolConfig(
                symbol='VIX_CGI',
                contract_spec=None,
                asset_type=AssetType.INDEX,
                primary=False,
                timeframes=['1min'],
                subscription_priority=5,
                enabled=True
            )
        }
    
    def get_active_symbols(self, primary_only: bool = False) -> List[str]:
        """Get list of currently active symbols (with rollover)"""
        active = []
        for key, config in self.symbols.items():
            if not config.enabled:
                continue
            if primary_only and not config.primary:
                continue
                
            active.append(config.get_current_symbol())
        
        return sorted(active, key=lambda s: self.symbols[self._get_base_key(s)].subscription_priority)
    
    def get_symbol_config(self, symbol_key: str) -> Optional[SymbolConfig]:
        """Get symbol configuration by key"""
        return self.symbols.get(symbol_key)
    
    def get_rollover_alerts(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming rollover alerts"""
        alerts = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        for key, config in self.symbols.items():
            if not config.contract_spec or not config.enabled:
                continue
                
            schedule = config.contract_spec.get_rollover_schedule(years=1)
            for current, rollover_date, next_symbol in schedule:
                if rollover_date <= cutoff_date:
                    alerts.append({
                        'symbol_key': key,
                        'current_contract': current,
                        'next_contract': next_symbol,
                        'rollover_date': rollover_date,
                        'days_until_rollover': (rollover_date - datetime.now()).days,
                        'action_required': rollover_date <= datetime.now() + timedelta(days=10)
                    })
        
        return sorted(alerts, key=lambda x: x['rollover_date'])
    
    def get_socket_subscriptions(self) -> Dict[str, Dict[str, Any]]:
        """Get socket subscription configuration for all services"""
        subscriptions = {}
        
        for key, config in self.symbols.items():
            if not config.enabled:
                continue
                
            current_symbol = config.get_current_symbol()
            subscriptions[current_symbol] = {
                'symbol_key': key,
                'timeframes': config.timeframes,
                'priority': config.subscription_priority,
                'primary': config.primary,
                'asset_type': config.asset_type.value
            }
        
        return subscriptions
    
    def _get_base_key(self, full_symbol: str) -> str:
        """Extract base key from full symbol (NQU25-CME -> NQ)"""
        for key, config in self.symbols.items():
            if config.get_current_symbol() == full_symbol:
                return key
        return full_symbol
    
    async def subscribe_to_changes(self) -> asyncio.Queue:
        """Subscribe to symbol configuration changes"""
        queue = asyncio.Queue(maxsize=100)
        self.subscribers.add(queue)
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from changes"""
        self.subscribers.discard(queue)
    
    async def _notify_subscribers(self, event_type: str, data: Dict[str, Any]):
        """Notify all subscribers of changes"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        dead_queues = set()
        for queue in self.subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(f"Subscriber queue full, dropping event: {event_type}")
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
                dead_queues.add(queue)
        
        # Clean up dead subscribers
        for queue in dead_queues:
            self.subscribers.discard(queue)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            'total_symbols': len(self.symbols),
            'active_symbols': len(self.get_active_symbols()),
            'primary_symbols': len(self.get_active_symbols(primary_only=True)),
            'futures_contracts': len([s for s in self.symbols.values() if s.is_futures()]),
            'upcoming_rollovers': len(self.get_rollover_alerts(days_ahead=30)),
            'subscribers': len(self.subscribers),
            'last_updated': datetime.now().isoformat()
        }

# Global instance
_symbol_manager = None

def get_symbol_manager() -> SymbolManager:
    """Get global symbol manager instance"""
    global _symbol_manager
    if _symbol_manager is None:
        _symbol_manager = SymbolManager()
    return _symbol_manager

def get_active_symbols(primary_only: bool = False) -> List[str]:
    """Convenience function to get active symbols"""
    return get_symbol_manager().get_active_symbols(primary_only)

def get_socket_subscriptions() -> Dict[str, Dict[str, Any]]:
    """Convenience function to get socket subscriptions"""
    return get_symbol_manager().get_socket_subscriptions()