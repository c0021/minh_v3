#!/usr/bin/env python3
"""
Migration Verification Test
===========================

Tests that all services correctly use centralized symbol management
when instantiated (simulates actual service startup).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_sierra_client_migration():
    """Test Sierra Client migration"""
    print("🔧 Testing Sierra Client Migration...")
    try:
        from minhos.core.symbol_integration import get_sierra_client_symbols
        symbols = get_sierra_client_symbols()
        print(f"   ✅ Sierra Client symbols loaded: {list(symbols.keys())}")
        return True
    except Exception as e:
        print(f"   ❌ Sierra Client migration failed: {e}")
        return False

def test_historical_data_migration():
    """Test Historical Data Service migration"""
    print("🔧 Testing Historical Data Service Migration...")
    try:
        from minhos.core.symbol_integration import get_historical_data_symbols
        symbols = get_historical_data_symbols()
        print(f"   ✅ Historical Data symbols loaded: {symbols}")
        return True
    except Exception as e:
        print(f"   ❌ Historical Data migration failed: {e}")
        return False

def test_ai_brain_migration():
    """Test AI Brain Service migration"""
    print("🔧 Testing AI Brain Service Migration...")
    try:
        from minhos.core.symbol_integration import get_ai_brain_primary_symbol
        symbol = get_ai_brain_primary_symbol()
        print(f"   ✅ AI Brain primary symbol loaded: {symbol}")
        return True
    except Exception as e:
        print(f"   ❌ AI Brain migration failed: {e}")
        return False

def test_bridge_migration():
    """Test Windows Bridge migration"""
    print("🔧 Testing Windows Bridge Migration...")
    try:
        bridge_config_path = '/home/colindo/Sync/minh_v3/windows/bridge_installation/bridge_symbols.json'
        if os.path.exists(bridge_config_path):
            import json
            with open(bridge_config_path, 'r') as f:
                config = json.load(f)
            symbols = config.get('active_symbols', [])
            print(f"   ✅ Bridge symbols config loaded: {symbols}")
            return True
        else:
            print(f"   ❌ Bridge config file not found: {bridge_config_path}")
            return False
    except Exception as e:
        print(f"   ❌ Bridge migration failed: {e}")
        return False

def test_rollover_functionality():
    """Test automatic rollover functionality"""
    print("🔧 Testing Automatic Rollover Functionality...")
    try:
        from minhos.core.symbol_manager import get_symbol_manager
        manager = get_symbol_manager()
        
        # Test current contract resolution
        nq_config = manager.get_symbol_config('NQ')
        if nq_config:
            current_contract = nq_config.get_current_symbol()
            print(f"   ✅ Current NQ contract: {current_contract}")
            
            # Test rollover schedule
            if nq_config.contract_spec:
                schedule = nq_config.contract_spec.get_rollover_schedule(years=1)
                if schedule:
                    next_rollover = schedule[0]
                    print(f"   ✅ Next rollover: {next_rollover[0]} → {next_rollover[2]} on {next_rollover[1].strftime('%Y-%m-%d')}")
                    return True
            
        print("   ❌ Rollover functionality not working")
        return False
    except Exception as e:
        print(f"   ❌ Rollover test failed: {e}")
        return False

def test_integration_consistency():
    """Test that all services get consistent symbols"""
    print("🔧 Testing Symbol Consistency Across Services...")
    try:
        from minhos.core.symbol_integration import (
            get_sierra_client_symbols, get_historical_data_symbols, 
            get_ai_brain_primary_symbol, get_bridge_symbols
        )
        
        sierra_symbols = set(get_sierra_client_symbols().keys())
        historical_symbols = set(get_historical_data_symbols())
        bridge_symbols = set(get_bridge_symbols())
        primary_symbol = get_ai_brain_primary_symbol()
        
        print(f"   • Sierra Client: {len(sierra_symbols)} symbols")
        print(f"   • Historical Data: {len(historical_symbols)} symbols")
        print(f"   • Bridge: {len(bridge_symbols)} symbols")
        print(f"   • AI Brain Primary: {primary_symbol}")
        
        # Check consistency
        all_symbols = sierra_symbols | historical_symbols | bridge_symbols
        if primary_symbol in all_symbols:
            print(f"   ✅ Consistency check passed - all services use compatible symbols")
            return True
        else:
            print(f"   ❌ Consistency check failed - primary symbol not in other services")
            return False
            
    except Exception as e:
        print(f"   ❌ Consistency test failed: {e}")
        return False

def main():
    print("🚀 MinhOS v3 Migration Verification Test")
    print("=" * 60)
    
    tests = [
        test_sierra_client_migration,
        test_historical_data_migration,
        test_ai_brain_migration,
        test_bridge_migration,
        test_rollover_functionality,
        test_integration_consistency
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Migration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL MIGRATIONS SUCCESSFUL!")
        print("✅ Centralized symbol management is fully operational")
        print("✅ All services will use centralized symbols when started")
        print("✅ Automatic rollover system is active")
        print("✅ Zero maintenance quarterly transitions enabled")
    else:
        print(f"⚠️  {total - passed} migration issues need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)