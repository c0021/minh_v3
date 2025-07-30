#!/usr/bin/env python3
"""
MinhOS v3 Centralized Symbol Management System
==============================================

Eliminates hard-coded symbols and provides intelligent contract rollover.
Single source of truth for all symbol configuration across the entire system.

Key Features:
- Automatic quarterly contract rollover (NQU25 → NQZ25 → NQH26)
- Centralized symbol configuration with expiration dates
- Socket subscription management
- Historical symbol mapping
- Environment-aware symbol sets (prod vs dev)

Author: MinhOS v3 System
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import calendar

logger = logging.getLogger(__name__)

class AssetType(Enum):
    FUTURES = "futures"
    FOREX = "forex"
    INDEX = "index"
    CRYPTO = "crypto"

class ContractStatus(Enum):
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    ROLLOVER = "rollover"

@dataclass
class ContractSpec:
    """Contract specification with rollover logic"""
    base_symbol: str  # NQ, ES, etc.
    exchange: str     # CME, CBOT, etc.
    asset_type: AssetType
    tick_size: float
    contract_size: int
    expiration_months: List[str] = field(default_factory=lambda: ['H', 'M', 'U', 'Z'])  # Mar, Jun, Sep, Dec
    days_before_rollover: int = 10  # Start rollover 10 days before expiration
    
    def get_current_contract(self, as_of_date: Optional[datetime] = None) -> str:
        """Get current active contract symbol"""
        if as_of_date is None:
            as_of_date = datetime.now()
            
        year = as_of_date.year
        current_quarter = (as_of_date.month - 1) // 3
        
        # Find next expiration month
        for i, month_code in enumerate(self.expiration_months):
            exp_month = ['H', 'M', 'U', 'Z'].index(month_code) * 3 + 3  # Mar=3, Jun=6, Sep=9, Dec=12
            exp_date = datetime(year, exp_month, self._get_third_friday(year, exp_month))
            
            # If we're within rollover window, use next contract
            rollover_date = exp_date - timedelta(days=self.days_before_rollover)
            
            if as_of_date < rollover_date:
                year_suffix = str(year)[-2:]  # 25, 26, etc.
                return f"{self.base_symbol}{month_code}{year_suffix}-{self.exchange}"
        
        # If we're past December, use next year's March contract
        year_suffix = str(year + 1)[-2:]
        return f"{self.base_symbol}H{year_suffix}-{self.exchange}"
    
    def get_rollover_schedule(self, years: int = 2) -> List[Tuple[str, datetime, str]]:
        """Get complete rollover schedule"""
        schedule = []
        current_date = datetime.now()
        
        for year_offset in range(years):
            year = current_date.year + year_offset
            for month_code in self.expiration_months:
                exp_month = ['H', 'M', 'U', 'Z'].index(month_code) * 3 + 3
                exp_date = datetime(year, exp_month, self._get_third_friday(year, exp_month))
                rollover_date = exp_date - timedelta(days=self.days_before_rollover)
                
                if rollover_date > current_date:
                    year_suffix = str(year)[-2:]
                    current_symbol = f"{self.base_symbol}{month_code}{year_suffix}-{self.exchange}"
                    
                    # Determine next contract
                    next_idx = (self.expiration_months.index(month_code) + 1) % len(self.expiration_months)
                    next_month_code = self.expiration_months[next_idx]
                    next_year = year if next_idx > 0 else year + 1
                    next_year_suffix = str(next_year)[-2:]
                    next_symbol = f"{self.base_symbol}{next_month_code}{next_year_suffix}-{self.exchange}"
                    
                    schedule.append((current_symbol, rollover_date, next_symbol))
        
        return sorted(schedule, key=lambda x: x[1])
    
    def _get_third_friday(self, year: int, month: int) -> int:
        """Get third Friday of the month (futures expiration)"""
        # Find first Friday
        first_day = datetime(year, month, 1)
        first_friday = 1 + (4 - first_day.weekday()) % 7
        
        # Third Friday is 14 days later
        return first_friday + 14

@dataclass
class SymbolConfig:
    """Complete symbol configuration"""
    symbol: str
    contract_spec: Optional[ContractSpec]
    asset_type: AssetType
    primary: bool = True
    timeframes: List[str] = field(default_factory=lambda: ['1min'])
    enabled: bool = True
    subscription_priority: int = 1  # 1=highest, 5=lowest
    
    def is_futures(self) -> bool:
        return self.asset_type == AssetType.FUTURES
    
    def get_current_symbol(self) -> str:
        """Get current active symbol (handles rollover for futures)"""
        if self.contract_spec:
            return self.contract_spec.get_current_contract()
        return self.symbol

class SymbolManager:
    """Centralized symbol management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.contracts: Dict[str, ContractSpec] = {}
        self.symbols: Dict[str, SymbolConfig] = {}
        self.subscribers: Set[asyncio.Queue] = set()
        self._initialize_default_contracts()
        self._initialize_default_symbols()
        
    def _initialize_default_contracts(self):
        """Initialize standard futures contracts"""
        self.contracts = {
            'NQ': ContractSpec(
                base_symbol='NQ',
                exchange='CME',
                asset_type=AssetType.FUTURES,
                tick_size=0.25,
                contract_size=20,
                expiration_months=['H', 'M', 'U', 'Z']
            ),
            'ES': ContractSpec(
                base_symbol='ES',
                exchange='CME',
                asset_type=AssetType.FUTURES,
                tick_size=0.25,
                contract_size=50,
                expiration_months=['H', 'M', 'U', 'Z']
            ),
            'YM': ContractSpec(
                base_symbol='YM',
                exchange='CBOT',
                asset_type=AssetType.FUTURES,
                tick_size=1.0,
                contract_size=5,
                expiration_months=['H', 'M', 'U', 'Z']
            )
        }
    
    def _initialize_default_symbols(self):
        """Initialize default symbol configuration"""
        self.symbols = {
            'NQ': SymbolConfig(
                symbol='NQ',
                contract_spec=self.contracts['NQ'],
                asset_type=AssetType.FUTURES,
                primary=True,
                timeframes=['1min', '30min', 'daily'],
                subscription_priority=1
            ),
            'ES': SymbolConfig(
                symbol='ES',
                contract_spec=self.contracts['ES'],
                asset_type=AssetType.FUTURES,
                primary=False,
                timeframes=['1min'],
                subscription_priority=2
            ),
            'EURUSD': SymbolConfig(
                symbol='EURUSD',
                contract_spec=None,
                asset_type=AssetType.FOREX,
                primary=False,
                timeframes=['1min'],
<<<<<<< HEAD
                subscription_priority=3,
                enabled=False  # DISABLED for 3-symbol focus
=======
                subscription_priority=3
>>>>>>> 25301bf6f2e931ccc6aab9ec2c45b5c7f4fddfa2
            ),
            'XAUUSD': SymbolConfig(
                symbol='XAUUSD',
                contract_spec=None,
                asset_type=AssetType.FOREX,
                primary=False,
                timeframes=['1min'],
<<<<<<< HEAD
                subscription_priority=4,
                enabled=False  # DISABLED for 3-symbol focus
=======
                subscription_priority=4
>>>>>>> 25301bf6f2e931ccc6aab9ec2c45b5c7f4fddfa2
            ),
            'VIX': SymbolConfig(
                symbol='VIX_CGI',
                contract_spec=None,
                asset_type=AssetType.INDEX,
                primary=False,
                timeframes=['1min'],
                subscription_priority=5
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