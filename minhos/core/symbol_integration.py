#!/usr/bin/env python3
"""
Symbol Manager Integration Layer
================================

Provides backwards compatibility and migration path for existing services.
Gradually replaces hard-coded symbols with centralized management.

Author: MinhOS v3 System
"""

import logging
from typing import Dict, List, Optional, Any
from .symbol_manager import get_symbol_manager, get_active_symbols, get_socket_subscriptions

logger = logging.getLogger(__name__)

class SymbolIntegration:
    """Integration layer for migrating services to centralized symbol management"""
    
    def __init__(self):
        self.symbol_manager = get_symbol_manager()
        self._service_migrations: Dict[str, bool] = {}
    
    def get_sierra_client_symbols(self) -> Dict[str, Dict[str, Any]]:
        """Get symbols for Sierra Client service in legacy format"""
        symbols = {}
        subscriptions = get_socket_subscriptions()
        
        for symbol, config in subscriptions.items():
            symbols[symbol] = {
                'timeframes': config['timeframes'],
                'primary': config['primary']
            }
        
        logger.info(f"Sierra Client symbols: {list(symbols.keys())}")
        return symbols
    
    def get_historical_data_symbols(self) -> List[str]:
        """Get symbols for Historical Data service"""
        # Include both futures and non-futures for historical analysis
        symbols = get_active_symbols()
        logger.info(f"Historical Data symbols: {symbols}")
        return symbols
    
    def get_bridge_symbols(self) -> List[str]:
        """Get symbols for Windows Bridge"""
        symbols = get_active_symbols()
        logger.info(f"Bridge symbols: {symbols}")
        return symbols
    
    def get_ai_brain_primary_symbol(self) -> str:
        """Get primary symbol for AI Brain analysis"""
        primary_symbols = get_active_symbols(primary_only=True)
        if primary_symbols:
            logger.info(f"AI Brain primary symbol: {primary_symbols[0]}")
            return primary_symbols[0]
        
        # Fallback to first available symbol
        all_symbols = get_active_symbols()
        if all_symbols:
            logger.warning(f"No primary symbol found, using fallback: {all_symbols[0]}")
            return all_symbols[0]
        
        logger.error("No symbols available for AI Brain")
        return "NQU25-CME"  # Emergency fallback
    
    def get_dashboard_symbols(self) -> Dict[str, Dict[str, Any]]:
        """Get symbols for Dashboard display"""
        symbols = {}
        subscriptions = get_socket_subscriptions()
        
        for symbol, config in subscriptions.items():
            symbols[symbol] = {
                'display_name': self._get_display_name(symbol),
                'primary': config['primary'],
                'asset_type': config['asset_type'],
                'priority': config['priority']
            }
        
        return symbols
    
    def get_trading_engine_symbols(self) -> List[str]:
        """Get tradeable symbols for Trading Engine"""
        # Only return primary symbols for trading
        symbols = get_active_symbols(primary_only=True)
        logger.info(f"Trading Engine symbols: {symbols}")
        return symbols
    
    def check_rollover_status(self) -> Dict[str, Any]:
        """Check if any symbols need rollover attention"""
        alerts = self.symbol_manager.get_rollover_alerts(days_ahead=15)
        
        status = {
            'needs_attention': len(alerts) > 0,
            'urgent_rollovers': len([a for a in alerts if a['action_required']]),
            'total_upcoming': len(alerts),
            'alerts': alerts
        }
        
        if status['needs_attention']:
            logger.warning(f"Symbol rollover attention needed: {status['urgent_rollovers']} urgent, {status['total_upcoming']} total")
        
        return status
    
    def _get_display_name(self, symbol: str) -> str:
        """Convert symbol to display name"""
        display_names = {
            'EURUSD': 'EUR/USD',
            'XAUUSD': 'Gold',
            'VIX_CGI': 'VIX'
        }
        
        # Handle futures contracts
        if symbol.startswith('NQ'):
            return f'NASDAQ {symbol[-3:]}'  # NQU25-CME -> NASDAQ U25
        elif symbol.startswith('ES'):
            return f'S&P 500 {symbol[-3:]}'  # ESU25-CME -> S&P 500 U25
        elif symbol.startswith('YM'):
            return f'Dow Jones {symbol[-3:]}'  # YMU25-CME -> Dow Jones U25
        
        return display_names.get(symbol, symbol)
    
    def get_pattern_analyzer_symbols(self) -> List[str]:
        """Get symbols for Pattern Analyzer service"""
        symbols = get_active_symbols()
        logger.info(f"Pattern Analyzer symbols: {symbols}")
        return symbols
    
    def get_web_api_symbols(self) -> List[str]:
        """Get symbols for Web API service"""
        symbols = get_active_symbols()
        logger.info(f"Web API symbols: {symbols}")
        return symbols
    
    def get_trading_engine_symbols(self) -> List[str]:
        """Get symbols for Trading Engine service"""
        # Trading engine focuses on primary tradeable symbol
        primary_symbols = get_active_symbols(primary_only=True)
        logger.info(f"Trading Engine symbols: {primary_symbols}")
        return primary_symbols
    
    def mark_service_migrated(self, service_name: str):
        """Mark a service as successfully migrated to centralized symbols"""
        self._service_migrations[service_name] = True
        logger.info(f"Service {service_name} successfully migrated to centralized symbol management")
    
    def is_service_migrated(self, service_name: str) -> bool:
        """Check if a service has been migrated to centralized symbol management"""
        return self._service_migrations.get(service_name, False)
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status of all services"""
        expected_services = [
            'sierra_client',
            'sierra_historical_data', 
            'windows_bridge',
            'ai_brain_service',
            'dashboard',
            'trading_engine'
        ]
        
        status = {
            'total_services': len(expected_services),
            'migrated_services': len(self._service_migrations),
            'migration_complete': len(self._service_migrations) == len(expected_services),
            'services': {}
        }
        
        for service in expected_services:
            status['services'][service] = {
                'migrated': self._service_migrations.get(service, False),
                'status': 'migrated' if self._service_migrations.get(service, False) else 'pending'
            }
        
        return status

# Global instance
_symbol_integration = None

def get_symbol_integration() -> SymbolIntegration:
    """Get global symbol integration instance"""
    global _symbol_integration
    if _symbol_integration is None:
        _symbol_integration = SymbolIntegration()
    return _symbol_integration

# Convenience functions for easy migration
def get_sierra_client_symbols() -> Dict[str, Dict[str, Any]]:
    """Convenience function for Sierra Client"""
    return get_symbol_integration().get_sierra_client_symbols()

def get_historical_data_symbols() -> List[str]:
    """Convenience function for Historical Data Service"""
    return get_symbol_integration().get_historical_data_symbols()

def get_bridge_symbols() -> List[str]:
    """Convenience function for Windows Bridge"""
    return get_symbol_integration().get_bridge_symbols()

def get_ai_brain_primary_symbol() -> str:
    """Convenience function for AI Brain"""
    return get_symbol_integration().get_ai_brain_primary_symbol()

def check_rollover_status() -> Dict[str, Any]:
    """Convenience function for rollover checking"""
    return get_symbol_integration().check_rollover_status()