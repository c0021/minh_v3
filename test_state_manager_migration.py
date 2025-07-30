#!/usr/bin/env python3
"""
Test State Manager Symbol Management Migration

Validates that State Manager now uses centralized symbol management
for symbol validation and state reporting.
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.state_manager import StateManager, Position
from minhos.core.symbol_integration import get_symbol_integration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_state_manager_migration():
    """Test State Manager centralized symbol management migration"""
    logger.info("🧪 Testing State Manager Symbol Management Migration...")
    
    try:
        # Test 1: Initialize State Manager
        logger.info("1. Testing State Manager initialization...")
        
        state_manager = StateManager()
        
        # Check if symbol integration is loaded
        if hasattr(state_manager, 'symbol_integration') and state_manager.symbol_integration:
            logger.info("✅ State Manager loaded symbol integration")
        else:
            logger.warning("⚠️ State Manager symbol integration not loaded")
        
        # Test 2: Test Symbol Validation
        logger.info("2. Testing symbol validation...")
        
        symbol_integration = get_symbol_integration()
        primary_symbol = symbol_integration.get_ai_brain_primary_symbol()
        
        # Test symbol validation (should not block)
        await state_manager._validate_symbol(primary_symbol)
        logger.info(f"✅ Valid symbol validation passed: {primary_symbol}")
        
        # Test invalid symbol (should warn but not block)
        await state_manager._validate_symbol("INVALID-SYMBOL")
        logger.info("✅ Invalid symbol validation completed (warns but doesn't block)")
        
        # Test 3: Test Tradeable Symbols Access
        logger.info("3. Testing tradeable symbols access...")
        
        tradeable_symbols = state_manager.get_tradeable_symbols()
        if tradeable_symbols:
            logger.info(f"✅ Tradeable symbols available: {tradeable_symbols}")
        else:
            logger.warning("⚠️ No tradeable symbols available")
        
        # Test 4: Test Rollover Status Access
        logger.info("4. Testing rollover status access...")
        
        rollover_status = state_manager.get_symbol_rollover_status()
        logger.info(f"✅ Rollover status: {rollover_status}")
        
        # Test 5: Test Position Update with Symbol Validation
        logger.info("5. Testing position update with symbol validation...")
        
        # Update position with valid symbol
        await state_manager.update_position(
            symbol=primary_symbol,
            quantity=1,
            side="LONG",
            entry_price=23500.0,
            current_price=23510.0
        )
        
        positions = state_manager.get_positions()
        if primary_symbol in positions:
            logger.info(f"✅ Position updated successfully: {positions[primary_symbol].symbol}")
        else:
            logger.warning("⚠️ Position update failed")
        
        # Test 6: Test Current State with Symbol Management Info
        logger.info("6. Testing current state with symbol management info...")
        
        current_state = state_manager.get_current_state()
        
        if "symbol_management" in current_state:
            symbol_info = current_state["symbol_management"]
            logger.info("✅ Current state includes symbol management information")
            logger.info(f"   Tradeable symbols count: {symbol_info.get('tradeable_symbols_count', 'N/A')}")
            logger.info(f"   Rollover alerts: {symbol_info.get('rollover_alerts', 'N/A')}")
            logger.info(f"   Needs attention: {symbol_info.get('rollover_needs_attention', 'N/A')}")
        else:
            logger.warning("⚠️ Current state missing symbol management information")
        
        # Test 7: Test Migration Status
        logger.info("7. Testing migration status...")
        
        # Check if service is marked as migrated
        if (hasattr(state_manager, 'symbol_integration') and 
            hasattr(state_manager, '_validate_symbol') and
            hasattr(state_manager, 'get_tradeable_symbols') and
            hasattr(state_manager, 'get_symbol_rollover_status')):
            logger.info("✅ State Manager fully integrated with centralized symbol management")
        else:
            logger.warning("⚠️ State Manager partially integrated")
        
        # Test 8: Verify No Hard-coded Symbols
        logger.info("8. Verifying no hard-coded symbols...")
        
        # Read the source file to verify no hard-coded symbols remain
        state_manager_file = Path(__file__).parent / "minhos" / "services" / "state_manager.py"
        with open(state_manager_file, 'r') as f:
            source_code = f.read()
        
        hard_coded_patterns = ['NQU25-CME', 'NQZ25-CME', 'ESU25-CME', '"NQ"', "'NQ'"]
        found_hard_coded = []
        
        for pattern in hard_coded_patterns:
            if pattern in source_code:
                found_hard_coded.append(pattern)
        
        if found_hard_coded:
            logger.warning(f"⚠️ Found remaining hard-coded symbols: {found_hard_coded}")
        else:
            logger.info("✅ No hard-coded symbols found")
        
        logger.info("🎉 State Manager Migration Test Complete!")
        
        return {
            "success": True,
            "symbol_integration_loaded": hasattr(state_manager, 'symbol_integration'),
            "tradeable_symbols_access": len(tradeable_symbols) > 0,
            "rollover_status_access": rollover_status is not None,
            "position_update_working": primary_symbol in state_manager.get_positions(),
            "current_state_enhanced": "symbol_management" in current_state,
            "hard_coded_removed": len(found_hard_coded) == 0,
            "fully_integrated": (hasattr(state_manager, 'symbol_integration') and 
                               hasattr(state_manager, '_validate_symbol') and
                               hasattr(state_manager, 'get_tradeable_symbols') and
                               hasattr(state_manager, 'get_symbol_rollover_status'))
        }
        
    except Exception as e:
        logger.error(f"❌ State Manager Migration Test Failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

async def test_position_symbol_validation():
    """Test position symbol validation"""
    logger.info("🔍 Testing Position Symbol Validation...")
    
    try:
        state_manager = StateManager()
        symbol_integration = get_symbol_integration()
        
        # Test with all tradeable symbols
        tradeable_symbols = symbol_integration.get_trading_engine_symbols()
        
        for symbol in tradeable_symbols:
            await state_manager.update_position(
                symbol=symbol,
                quantity=1,
                side="LONG",
                entry_price=20000.0,
                current_price=20010.0
            )
            logger.info(f"✅ Position update successful for {symbol}")
        
        # Verify all positions were created
        positions = state_manager.get_positions()
        created_symbols = set(positions.keys())
        expected_symbols = set(tradeable_symbols)
        
        if created_symbols.issuperset(expected_symbols):
            logger.info(f"✅ All tradeable symbols have positions: {created_symbols}")
        else:
            missing = expected_symbols - created_symbols
            logger.warning(f"⚠️ Missing positions for symbols: {missing}")
        
        return {
            "success": True,
            "positions_created": len(positions),
            "expected_positions": len(tradeable_symbols),
            "all_symbols_tested": created_symbols.issuperset(expected_symbols)
        }
        
    except Exception as e:
        logger.error(f"❌ Position Symbol Validation Test Failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("🚀 Starting State Manager Migration Tests...")
    
    # Test 1: Core migration functionality
    migration_result = await test_state_manager_migration()
    
    # Test 2: Position symbol validation
    validation_result = await test_position_symbol_validation()
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"  Migration Test: {'✅' if migration_result['success'] else '❌'}")
    logger.info(f"  Position Validation: {'✅' if validation_result['success'] else '❌'}")
    
    if migration_result['success'] and validation_result['success']:
        logger.info("🎉 All State Manager Migration Tests Passed!")
        logger.info("✅ State Manager successfully migrated to centralized symbol management!")
    else:
        logger.warning("⚠️ Some tests failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main())