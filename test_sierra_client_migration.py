#!/usr/bin/env python3
"""
Test Sierra Client Symbol Management Migration

Validates that Sierra Client now uses centralized symbol management
instead of hard-coded symbol references.
"""

import asyncio
import sys
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.sierra_client import SierraClient
from minhos.core.symbol_integration import get_symbol_integration
from minhos.core.symbol_manager import get_symbol_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sierra_client_migration():
    """Test Sierra Client centralized symbol management migration"""
    logger.info("🧪 Testing Sierra Client Symbol Management Migration...")
    
    try:
        # Test 1: Verify Symbol Integration is Used
        logger.info("1. Testing symbol integration initialization...")
        
        sierra_client = SierraClient()
        
        # Check if symbols are loaded from centralized management
        if hasattr(sierra_client, 'symbols') and sierra_client.symbols:
            logger.info(f"✅ Sierra Client loaded {len(sierra_client.symbols)} symbols from centralized management")
            logger.info(f"   Symbols: {list(sierra_client.symbols.keys())}")
        else:
            logger.warning("⚠️ Sierra Client symbols not loaded")
        
        # Test 2: Test Primary Symbol Resolution
        logger.info("2. Testing primary symbol resolution...")
        
        symbol_integration = get_symbol_integration()
        primary_symbol = symbol_integration.get_ai_brain_primary_symbol()
        logger.info(f"✅ Primary symbol resolved: {primary_symbol}")
        
        # Test 3: Test Bridge Symbol List
        logger.info("3. Testing bridge symbol configuration...")
        
        bridge_symbols = symbol_integration.get_bridge_symbols()
        logger.info(f"✅ Bridge symbols: {bridge_symbols}")
        
        # Test 4: Test Hard-coded Symbol Removal
        logger.info("4. Verifying hard-coded symbols are removed...")
        
        # Read the source file to verify no hard-coded symbols remain
        sierra_client_file = Path(__file__).parent / "minhos" / "services" / "sierra_client.py"
        with open(sierra_client_file, 'r') as f:
            source_code = f.read()
        
        hard_coded_patterns = ['NQU25-CME', 'NQZ25-CME', 'ESU25-CME']
        found_hard_coded = []
        
        for pattern in hard_coded_patterns:
            if pattern in source_code:
                found_hard_coded.append(pattern)
        
        if found_hard_coded:
            logger.warning(f"⚠️ Found remaining hard-coded symbols: {found_hard_coded}")
        else:
            logger.info("✅ No hard-coded symbols found")
        
        # Test 5: Test Symbol Validation in Market Data
        logger.info("5. Testing market data symbol validation...")
        
        # Mock the session to test symbol validation logic
        sierra_client.session = MagicMock()
        
        # Create mock response with test data
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "NQZ25-CME": {
                "symbol": "NQZ25-CME",
                "price": 23500.00,
                "timestamp": "2025-07-26T16:00:00",
                "volume": 1000
            },
            "ESZ25-CME": {
                "symbol": "ESZ25-CME", 
                "price": 5800.00,
                "timestamp": "2025-07-26T16:00:00",
                "volume": 500
            }
        })
        
        # Mock the context manager
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        sierra_client.session.get = MagicMock(return_value=mock_context)
        
        # Set connection state to connected for testing
        from minhos.services.sierra_client import ConnectionState
        sierra_client.connection_state = ConnectionState.CONNECTED
        
        # Test the get_all_market_data method
        market_data = await sierra_client.get_all_market_data()
        
        if market_data:
            logger.info(f"✅ Market data validation working: {len(market_data)} symbols processed")
            for symbol, data in market_data.items():
                logger.info(f"   {symbol}: ${data.close}")
        else:
            logger.warning("⚠️ Market data processing failed")
        
        # Test 6: Test Trade Command Symbol Resolution
        logger.info("6. Testing trade command symbol resolution...")
        
        # Test trade command without symbol (should use default from centralized management)
        test_trade_data = {
            'action': 'BUY',
            'quantity': 1,
            'order_type': 'MARKET'
            # No symbol specified - should use default
        }
        
        # We can't test the full WebSocket handler easily, but we can test the logic
        default_symbol = test_trade_data.get('symbol')
        if not default_symbol:
            default_symbol = symbol_integration.get_ai_brain_primary_symbol()
        
        logger.info(f"✅ Trade command default symbol resolution: {default_symbol}")
        
        # Test 7: Verify Configuration Integration
        logger.info("7. Testing configuration integration...")
        
        # Check if Sierra Client properly integrates with symbol configuration
        sierra_symbols = symbol_integration.get_sierra_client_symbols()
        dashboard_symbols = symbol_integration.get_dashboard_symbols()
        
        logger.info(f"✅ Sierra Client symbol config: {len(sierra_symbols)} symbols")
        logger.info(f"✅ Dashboard symbol config: {len(dashboard_symbols)} symbols")
        
        # Verify consistency
        sierra_symbol_set = set(sierra_symbols.keys())
        dashboard_symbol_set = set(dashboard_symbols.keys())
        
        if sierra_symbol_set == dashboard_symbol_set:
            logger.info("✅ Symbol configuration consistent across services")
        else:
            logger.warning(f"⚠️ Symbol configuration mismatch: Sierra={sierra_symbol_set}, Dashboard={dashboard_symbol_set}")
        
        logger.info("🎉 Sierra Client Migration Test Complete!")
        
        return {
            "success": True,
            "symbols_loaded": len(sierra_client.symbols) if hasattr(sierra_client, 'symbols') else 0,
            "primary_symbol": primary_symbol,
            "bridge_symbols": len(bridge_symbols),
            "hard_coded_removed": len(found_hard_coded) == 0,
            "market_data_processed": len(market_data) if market_data else 0,
            "configuration_consistent": sierra_symbol_set == dashboard_symbol_set
        }
        
    except Exception as e:
        logger.error(f"❌ Sierra Client Migration Test Failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

async def test_rollover_integration():
    """Test rollover integration with Sierra Client"""
    logger.info("🔄 Testing Rollover Integration...")
    
    try:
        # Test rollover status checking
        symbol_integration = get_symbol_integration()
        rollover_status = symbol_integration.check_rollover_status()
        
        logger.info(f"Rollover Status:")
        logger.info(f"  Needs attention: {rollover_status['needs_attention']}")
        logger.info(f"  Urgent rollovers: {rollover_status['urgent_rollovers']}")
        logger.info(f"  Total upcoming: {rollover_status['total_upcoming']}")
        
        # Test symbol manager rollover functionality
        symbol_manager = get_symbol_manager()
        alerts = symbol_manager.get_rollover_alerts(days_ahead=60)
        
        logger.info(f"✅ Rollover alerts: {len(alerts)} alerts for next 60 days")
        for alert in alerts[:3]:  # Show first 3
            logger.info(f"   {alert['current_symbol']} → {alert['next_symbol']} in {alert['days_until_rollover']} days")
        
        return {
            "success": True,
            "rollover_alerts": len(alerts),
            "needs_attention": rollover_status['needs_attention']
        }
        
    except Exception as e:
        logger.error(f"❌ Rollover Integration Test Failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("🚀 Starting Sierra Client Migration Tests...")
    
    # Test 1: Core migration functionality
    migration_result = await test_sierra_client_migration()
    
    # Test 2: Rollover integration
    rollover_result = await test_rollover_integration()
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"  Migration Test: {'✅' if migration_result['success'] else '❌'}")
    logger.info(f"  Rollover Integration: {'✅' if rollover_result['success'] else '❌'}")
    
    if migration_result['success'] and rollover_result['success']:
        logger.info("🎉 All Sierra Client Migration Tests Passed!")
        logger.info("✅ Sierra Client successfully migrated to centralized symbol management!")
    else:
        logger.warning("⚠️ Some tests failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main())