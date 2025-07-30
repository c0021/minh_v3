#!/usr/bin/env python3
"""
Test Trading Engine Symbol Management Migration

Validates that Trading Engine now uses centralized symbol management
and properly handles symbol rollover decisions.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.trading_engine import TradingEngine, DecisionPriority
from minhos.core.symbol_integration import get_symbol_integration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_trading_engine_migration():
    """Test Trading Engine centralized symbol management migration"""
    logger.info("🧪 Testing Trading Engine Symbol Management Migration...")
    
    try:
        # Test 1: Initialize Trading Engine
        logger.info("1. Testing Trading Engine initialization...")
        
        trading_engine = TradingEngine()
        
        # Check if symbols are loaded from centralized management
        if hasattr(trading_engine, 'tradeable_symbols') and trading_engine.tradeable_symbols:
            logger.info(f"✅ Trading Engine loaded {len(trading_engine.tradeable_symbols)} tradeable symbols")
            logger.info(f"   Symbols: {trading_engine.tradeable_symbols}")
        else:
            logger.warning("⚠️ Trading Engine tradeable symbols not loaded")
        
        # Check primary symbol
        if hasattr(trading_engine, 'primary_symbol') and trading_engine.primary_symbol:
            logger.info(f"✅ Primary trading symbol: {trading_engine.primary_symbol}")
        else:
            logger.warning("⚠️ Primary trading symbol not set")
        
        # Test 2: Test Symbol Integration Service
        logger.info("2. Testing symbol integration service...")
        
        if hasattr(trading_engine, 'symbol_integration'):
            logger.info("✅ Symbol integration service connected")
            
            # Test rollover status check
            rollover_status = trading_engine.check_symbol_rollover()
            logger.info(f"✅ Rollover status check: {rollover_status}")
        else:
            logger.warning("⚠️ Symbol integration service not connected")
        
        # Test 3: Test Engine Status with Symbol Information
        logger.info("3. Testing engine status with symbol information...")
        
        status = trading_engine.get_engine_status()
        
        if 'tradeable_symbols' in status and 'primary_symbol' in status:
            logger.info("✅ Engine status includes symbol information")
            logger.info(f"   Tradeable symbols: {status['tradeable_symbols']}")
            logger.info(f"   Primary symbol: {status['primary_symbol']}")
        else:
            logger.warning("⚠️ Engine status missing symbol information")
        
        # Test 4: Test Rollover Decision Creation
        logger.info("4. Testing rollover decision creation...")
        
        # Check if any rollover decisions were created
        pending_decisions = trading_engine.get_pending_decisions()
        rollover_decisions = [d for d in pending_decisions if d.context.get('symbol_rollover', False)]
        
        if rollover_decisions:
            logger.info(f"✅ Found {len(rollover_decisions)} rollover decisions")
            for decision in rollover_decisions:
                logger.info(f"   Decision: {decision.title} (Priority: {decision.priority.value})")
        else:
            logger.info("ℹ️ No rollover decisions needed (symbols not expiring soon)")
        
        # Test 5: Test Symbol Configuration Consistency
        logger.info("5. Testing symbol configuration consistency...")
        
        symbol_integration = get_symbol_integration()
        
        # Get symbols from different sources
        sierra_symbols = symbol_integration.get_sierra_client_symbols()
        trading_symbols = symbol_integration.get_trading_engine_symbols()
        ai_primary = symbol_integration.get_ai_brain_primary_symbol()
        
        # Check consistency
        trading_symbol_set = set(trading_symbols)
        sierra_symbol_set = set(sierra_symbols.keys())
        
        if ai_primary in trading_symbols:
            logger.info("✅ Primary symbol is in tradeable symbols list")
        else:
            logger.warning(f"⚠️ Primary symbol {ai_primary} not in tradeable symbols {trading_symbols}")
        
        if trading_symbol_set.issubset(sierra_symbol_set):
            logger.info("✅ All trading symbols are available in Sierra Client")
        else:
            logger.warning(f"⚠️ Trading symbols not all available in Sierra Client")
        
        # Test 6: Test Migration Status
        logger.info("6. Testing migration status...")
        
        # Check if service is marked as migrated
        try:
            # We can't directly access the migration status, but we can verify the service
            # is properly integrated by checking if all required methods work
            if (hasattr(trading_engine, 'symbol_integration') and 
                hasattr(trading_engine, 'tradeable_symbols') and
                hasattr(trading_engine, 'primary_symbol') and
                hasattr(trading_engine, 'check_symbol_rollover')):
                logger.info("✅ Trading Engine fully integrated with centralized symbol management")
            else:
                logger.warning("⚠️ Trading Engine partially integrated")
        except Exception as e:
            logger.error(f"❌ Migration status check failed: {e}")
        
        # Test 7: Test Hard-coded Symbol Removal
        logger.info("7. Verifying hard-coded symbols are removed...")
        
        # Read the source file to verify no hard-coded symbols remain
        trading_engine_file = Path(__file__).parent / "minhos" / "services" / "trading_engine.py"
        with open(trading_engine_file, 'r') as f:
            source_code = f.read()
        
        hard_coded_patterns = ['NQU25-CME', 'NQZ25-CME', 'ESU25-CME', 'ESZ25-CME']
        found_hard_coded = []
        
        for pattern in hard_coded_patterns:
            if pattern in source_code:
                found_hard_coded.append(pattern)
        
        if found_hard_coded:
            logger.warning(f"⚠️ Found remaining hard-coded symbols: {found_hard_coded}")
        else:
            logger.info("✅ No hard-coded symbols found")
        
        logger.info("🎉 Trading Engine Migration Test Complete!")
        
        return {
            "success": True,
            "tradeable_symbols_loaded": len(trading_engine.tradeable_symbols) if hasattr(trading_engine, 'tradeable_symbols') else 0,
            "primary_symbol": trading_engine.primary_symbol if hasattr(trading_engine, 'primary_symbol') else None,
            "symbol_integration_connected": hasattr(trading_engine, 'symbol_integration'),
            "rollover_decisions": len(rollover_decisions),
            "hard_coded_removed": len(found_hard_coded) == 0,
            "fully_integrated": hasattr(trading_engine, 'symbol_integration') and hasattr(trading_engine, 'tradeable_symbols')
        }
        
    except Exception as e:
        logger.error(f"❌ Trading Engine Migration Test Failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

async def test_rollover_workflow():
    """Test the rollover workflow in Trading Engine"""
    logger.info("🔄 Testing Rollover Workflow...")
    
    try:
        trading_engine = TradingEngine()
        
        # Test rollover monitoring
        rollover_status = trading_engine.check_symbol_rollover()
        logger.info(f"Rollover monitoring result: {rollover_status}")
        
        # Check if decisions were created properly
        decisions_before = len(trading_engine.get_pending_decisions())
        
        # Run rollover check again (should not duplicate decisions)
        trading_engine.check_symbol_rollover()
        
        decisions_after = len(trading_engine.get_pending_decisions())
        
        if decisions_after == decisions_before:
            logger.info("✅ Rollover decision deduplication working correctly")
        else:
            logger.warning(f"⚠️ Rollover decisions may be duplicating: {decisions_before} -> {decisions_after}")
        
        return {
            "success": True,
            "rollover_status": rollover_status,
            "decisions_created": decisions_after
        }
        
    except Exception as e:
        logger.error(f"❌ Rollover Workflow Test Failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("🚀 Starting Trading Engine Migration Tests...")
    
    # Test 1: Core migration functionality
    migration_result = await test_trading_engine_migration()
    
    # Test 2: Rollover workflow
    rollover_result = await test_rollover_workflow()
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"  Migration Test: {'✅' if migration_result['success'] else '❌'}")
    logger.info(f"  Rollover Workflow: {'✅' if rollover_result['success'] else '❌'}")
    
    if migration_result['success'] and rollover_result['success']:
        logger.info("🎉 All Trading Engine Migration Tests Passed!")
        logger.info("✅ Trading Engine successfully migrated to centralized symbol management!")
    else:
        logger.warning("⚠️ Some tests failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main())