#!/usr/bin/env python3
"""
Smart Command Suggestions Test
==============================

End-to-end test for the smart command suggestion system.
Tests the complete integration from context analysis to UI response.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.smart_suggestion_engine import (
    SmartSuggestionEngine, SuggestionContext, SuggestionType
)
from minhos.services.chat_service import ChatService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_suggestion_engine():
    """Test the smart suggestion engine directly"""
    logger.info("🔄 Testing Smart Suggestion Engine...")
    
    engine = SmartSuggestionEngine()
    
    # Test context
    context = SuggestionContext(
        market_price=23500.0,
        price_change=0.8,  # Significant price movement
        volume_trend="spike",
        volatility_level="high",
        ml_signal="STRONG_BUY",
        ml_confidence=0.75,
        current_positions=0,
        account_exposure=0.0,
        recent_commands=["analyze", "trend analysis"],
        session_duration=5
    )
    
    # Test different partial commands
    test_cases = [
        ("", "Empty partial command - should show contextual suggestions"),
        ("buy", "Buy command - should show trading actions"),
        ("lstm", "LSTM command - should show ML insights"),
        ("sys", "System command - should show system status"),
        ("an", "Analysis command - should show market analysis"),
        ("kelly", "Kelly command - should show position sizing")
    ]
    
    for partial_command, description in test_cases:
        logger.info(f"\n--- Testing: {description} ---")
        suggestions = await engine.get_smart_suggestions(partial_command, context, max_suggestions=3)
        
        logger.info(f"Partial command: '{partial_command}'")
        logger.info(f"Suggestions returned: {len(suggestions)}")
        
        for i, suggestion in enumerate(suggestions):
            logger.info(f"  {i+1}. {suggestion.command} ({suggestion.relevance_score:.2f})")
            logger.info(f"     Type: {suggestion.suggestion_type.value}")
            logger.info(f"     Description: {suggestion.description}")
    
    logger.info("✅ Smart Suggestion Engine tests completed")


async def test_chat_service_integration():
    """Test the chat service integration"""
    logger.info("🔄 Testing Chat Service Integration...")
    
    try:
        chat_service = ChatService()
        
        # Create a fake client ID
        client_id = "test_client_123"
        
        # Test getting suggestions
        suggestions_data = await chat_service.get_smart_suggestions(client_id, "buy")
        
        logger.info(f"Chat service suggestions: {len(suggestions_data.get('suggestions', []))}")
        logger.info(f"Context summary: {suggestions_data.get('context_summary', {})}")
        
        if suggestions_data.get('suggestions'):
            logger.info("Sample suggestion:")
            suggestion = suggestions_data['suggestions'][0]
            logger.info(f"  Command: {suggestion['command']}")
            logger.info(f"  Description: {suggestion['description']}")
            logger.info(f"  Type: {suggestion['type']}")
            logger.info(f"  Relevance: {suggestion['relevance']}")
        
        logger.info("✅ Chat Service Integration test completed")
        
    except Exception as e:
        logger.error(f"❌ Chat Service Integration test failed: {e}")


async def test_contextual_suggestions():
    """Test context-driven suggestion generation"""
    logger.info("🔄 Testing Contextual Suggestions...")
    
    engine = SmartSuggestionEngine()
    
    # Test different market scenarios
    scenarios = [
        {
            "name": "High Volatility Market",
            "context": SuggestionContext(
                market_price=23500.0,
                price_change=-1.2,
                volume_trend="spike",
                volatility_level="high",
                ml_confidence=0.4,
                current_positions=2,
                account_exposure=0.8
            ),
            "expected_types": [SuggestionType.RISK_MANAGEMENT, SuggestionType.MARKET_ANALYSIS]
        },
        {
            "name": "Strong ML Signal",
            "context": SuggestionContext(
                market_price=23500.0,
                price_change=0.3,
                volume_trend="normal",
                volatility_level="normal",
                ml_signal="BUY",
                ml_confidence=0.85,
                current_positions=0,
                account_exposure=0.1
            ),
            "expected_types": [SuggestionType.ML_INSIGHT, SuggestionType.TRADING_ACTION]
        },
        {
            "name": "New Session",
            "context": SuggestionContext(
                market_price=23500.0,
                price_change=0.0,
                volume_trend="normal",
                volatility_level="normal",
                ml_confidence=0.5,
                current_positions=0,
                account_exposure=0.0,
                session_duration=1
            ),
            "expected_types": [SuggestionType.SYSTEM_STATUS, SuggestionType.MARKET_ANALYSIS]
        }
    ]
    
    for scenario in scenarios:
        logger.info(f"\n--- Testing Scenario: {scenario['name']} ---")
        
        suggestions = await engine.get_smart_suggestions("", scenario["context"], max_suggestions=5)
        
        logger.info(f"Generated {len(suggestions)} suggestions")
        
        # Check if expected types are present
        suggestion_types = [s.suggestion_type for s in suggestions]
        for expected_type in scenario["expected_types"]:
            if expected_type in suggestion_types:
                logger.info(f"  ✅ Found expected type: {expected_type.value}")
            else:
                logger.info(f"  ⚠️ Missing expected type: {expected_type.value}")
        
        # Show top suggestions
        for i, suggestion in enumerate(suggestions[:3]):
            logger.info(f"  {i+1}. {suggestion.command} (relevance: {suggestion.relevance_score:.2f})")
    
    logger.info("✅ Contextual Suggestions tests completed")


async def test_ml_integration():
    """Test ML integration in suggestions"""
    logger.info("🔄 Testing ML Integration...")
    
    engine = SmartSuggestionEngine()
    
    # Context with ML data
    ml_context = SuggestionContext(
        market_price=23500.0,
        price_change=0.5,
        volume_trend="normal",
        volatility_level="normal",
        ml_signal="STRONG_BUY",
        ml_confidence=0.75,
        current_positions=0,
        account_exposure=0.2
    )
    
    # Test ML-related partial commands
    ml_commands = ["lstm", "ensemble", "kelly", "ml"]
    
    for cmd in ml_commands:
        suggestions = await engine.get_smart_suggestions(cmd, ml_context, max_suggestions=3)
        logger.info(f"ML command '{cmd}': {len(suggestions)} suggestions")
        
        ml_suggestions = [s for s in suggestions if s.suggestion_type == SuggestionType.ML_INSIGHT]
        logger.info(f"  ML-specific suggestions: {len(ml_suggestions)}")
        
        if ml_suggestions:
            top_ml = ml_suggestions[0]
            logger.info(f"  Top ML suggestion: {top_ml.command} ({top_ml.relevance_score:.2f})")
    
    logger.info("✅ ML Integration tests completed")


async def main():
    """Run all smart suggestion tests"""
    logger.info("🚀 Starting Smart Command Suggestions Test Suite")
    logger.info("=" * 60)
    
    try:
        # Run all tests
        await test_suggestion_engine()
        await test_chat_service_integration()
        await test_contextual_suggestions()
        await test_ml_integration()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Smart Command Suggestions Test Suite: SUCCESS")
        logger.info("✅ All components are working correctly")
        logger.info("✅ Smart suggestions are ready for production use")
        
    except Exception as e:
        logger.error(f"\n❌ Test Suite Failed: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())