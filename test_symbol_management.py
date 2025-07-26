#!/usr/bin/env python3
"""
Test Script: Centralized Symbol Management System
=================================================

Demonstrates the new centralized symbol management system and its benefits.
Run this to see how symbol management would work across all services.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from minhos.core.symbol_manager import get_symbol_manager, get_active_symbols
from minhos.core.symbol_integration import get_symbol_integration
from datetime import datetime
import json

def main():
    print("🔄 MinhOS v3 Centralized Symbol Management Test")
    print("=" * 60)
    
    # Initialize symbol manager
    symbol_manager = get_symbol_manager()
    integration = get_symbol_integration()
    
    # Test 1: Current Active Symbols
    print("\n📊 Current Active Symbols:")
    active_symbols = get_active_symbols()
    for i, symbol in enumerate(active_symbols, 1):
        config = symbol_manager.get_symbol_config(symbol_manager._get_base_key(symbol))
        print(f"  {i}. {symbol} ({'PRIMARY' if config.primary else 'secondary'})")
    
    # Test 2: Service-Specific Symbol Lists
    print("\n🔧 Service-Specific Symbol Configuration:")
    
    print("\n  Sierra Client Symbols:")
    sierra_symbols = integration.get_sierra_client_symbols()
    for symbol, config in sierra_symbols.items():
        print(f"    • {symbol}: {config['timeframes']} ({'primary' if config['primary'] else 'secondary'})")
    
    print("\n  Historical Data Symbols:")
    historical_symbols = integration.get_historical_data_symbols()
    for symbol in historical_symbols:
        print(f"    • {symbol}")
    
    print("\n  AI Brain Primary Symbol:")
    ai_symbol = integration.get_ai_brain_primary_symbol()
    print(f"    • {ai_symbol}")
    
    print("\n  Bridge Symbols:")
    bridge_symbols = integration.get_bridge_symbols()
    for symbol in bridge_symbols:
        print(f"    • {symbol}")
    
    # Test 3: Contract Rollover Information
    print("\n📅 Contract Rollover Schedule:")
    alerts = symbol_manager.get_rollover_alerts(days_ahead=180)
    
    if alerts:
        for alert in alerts[:3]:  # Show first 3 upcoming rollovers
            days_until = alert['days_until_rollover']
            status = "🚨 URGENT" if alert['action_required'] else "📋 Scheduled"
            print(f"    {status}: {alert['current_contract']} → {alert['next_contract']}")
            print(f"      Rollover Date: {alert['rollover_date'].strftime('%Y-%m-%d')} ({days_until} days)")
    else:
        print("    No upcoming rollovers in next 180 days")
    
    # Test 4: Socket Subscription Configuration
    print("\n🔌 Socket Subscription Configuration:")
    subscriptions = symbol_manager.get_socket_subscriptions()
    for symbol, config in subscriptions.items():
        priority = "★" * config['priority']
        print(f"    • {symbol}: Priority {priority} | {config['asset_type'].upper()} | {', '.join(config['timeframes'])}")
    
    # Test 5: System Status
    print("\n📊 System Status:")
    status = symbol_manager.get_system_status()
    print(f"    Total Symbols: {status['total_symbols']}")
    print(f"    Active Symbols: {status['active_symbols']}")
    print(f"    Primary Symbols: {status['primary_symbols']}")
    print(f"    Futures Contracts: {status['futures_contracts']}")
    print(f"    Upcoming Rollovers: {status['upcoming_rollovers']}")
    
    # Test 6: Migration Status
    print("\n🔄 Service Migration Status:")
    migration_status = integration.get_migration_status()
    print(f"    Migration Progress: {migration_status['migrated_services']}/{migration_status['total_services']} services")
    
    for service, info in migration_status['services'].items():
        status_icon = "✅" if info['migrated'] else "⏳"
        print(f"    {status_icon} {service}: {info['status']}")
    
    # Test 7: Rollover Alert Check
    print("\n⚠️  Rollover Status Check:")
    rollover_status = integration.check_rollover_status()
    if rollover_status['needs_attention']:
        print(f"    🚨 ATTENTION NEEDED: {rollover_status['urgent_rollovers']} urgent, {rollover_status['total_upcoming']} total")
        for alert in rollover_status['alerts'][:2]:
            print(f"      • {alert['current_contract']} expires in {alert['days_until_rollover']} days")
    else:
        print("    ✅ No immediate rollover attention needed")
    
    print("\n" + "=" * 60)
    print("🎯 Benefits of Centralized Symbol Management:")
    print("   ✅ Single source of truth for all symbols")
    print("   ✅ Automatic quarterly contract rollover")
    print("   ✅ No more hard-coded symbols in services")
    print("   ✅ Rollover alerts prevent trading disruptions")
    print("   ✅ Environment-specific symbol configuration")
    print("   ✅ Unified socket subscription management")
    print("   ✅ Easy addition of new instruments")

if __name__ == "__main__":
    main()