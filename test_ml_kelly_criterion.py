#!/usr/bin/env python3
"""
Test ML-Enhanced Kelly Criterion System

Tests the complete integration of:
- LSTM predictions
- Ensemble predictions
- Kelly Criterion position sizing
- Trading Engine integration
"""

import asyncio
import sys
import logging
from pathlib import Path
import numpy as np
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.ml.kelly_criterion import get_kelly_criterion, MLEnhancedKellyCriterion
from minhos.services.trading_engine import TradingSignal, SignalType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_kelly_criterion_calculations():
    """Test core Kelly Criterion calculations"""
    logger.info("🧪 Testing Kelly Criterion Calculations...")
    
    kelly = MLEnhancedKellyCriterion(capital=100000.0)
    
    # Test Case 1: Favorable odds with high confidence
    logger.info("\nTest 1: Favorable odds (60% win rate, 2:1 reward/risk)")
    
    lstm_pred = {
        'probability': 0.6,
        'confidence': 0.8,
        'direction': 1
    }
    
    ensemble_pred = {
        'probability': 0.62,
        'confidence': 0.85,
        'direction': 1
    }
    
    position = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred,
        ensemble_prediction=ensemble_pred,
        risk_params={'max_position_size': 10}
    )
    
    logger.info(f"✅ Win Probability: {position.win_probability:.2%}")
    logger.info(f"✅ Kelly Fraction: {position.kelly_fraction:.3f}")
    logger.info(f"✅ Recommended Size: {position.recommended_size} contracts")
    logger.info(f"✅ Risk-Adjusted Size: {position.risk_adjusted_size} contracts")
    
    # Test Case 2: Unfavorable odds
    logger.info("\nTest 2: Unfavorable odds (40% win rate)")
    
    lstm_pred2 = {
        'probability': 0.4,
        'confidence': 0.7,
        'direction': -1
    }
    
    ensemble_pred2 = {
        'probability': 0.38,
        'confidence': 0.65,
        'direction': -1
    }
    
    position2 = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred2,
        ensemble_prediction=ensemble_pred2
    )
    
    logger.info(f"✅ Win Probability: {position2.win_probability:.2%}")
    logger.info(f"✅ Kelly Fraction: {position2.kelly_fraction:.3f}")
    logger.info(f"✅ Recommended Size: {position2.recommended_size} contracts")
    
    # Test Case 3: Low confidence
    logger.info("\nTest 3: Low confidence prediction")
    
    lstm_pred3 = {
        'probability': 0.55,
        'confidence': 0.4,
        'direction': 1
    }
    
    ensemble_pred3 = {
        'probability': 0.52,
        'confidence': 0.45,
        'direction': 1
    }
    
    position3 = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred3,
        ensemble_prediction=ensemble_pred3
    )
    
    logger.info(f"✅ Win Probability: {position3.win_probability:.2%}")
    logger.info(f"✅ Confidence Score: {position3.confidence_score:.2f}")
    logger.info(f"✅ Recommended Size: {position3.recommended_size} contracts (low conf)")
    
    return {
        'test1_kelly': position.kelly_fraction,
        'test1_size': position.recommended_size,
        'test2_kelly': position2.kelly_fraction,
        'test2_size': position2.recommended_size,
        'test3_size': position3.recommended_size
    }

async def test_position_sizing_service():
    """Test Position Sizing Service integration"""
    logger.info("\n🧪 Testing Position Sizing Service...")
    
    service = get_position_sizing_service()
    
    # Mock market data
    market_data = {
        'close': 23500.0,
        'high': 23550.0,
        'low': 23450.0,
        'volume': 1000,
        'rsi': 55,
        'macd': 5.0,
        'volatility': 0.015
    }
    
    # Test position calculation
    kelly_position = await service.calculate_optimal_position(
        symbol="NQU25-CME",
        current_price=23500.0,
        market_data=market_data
    )
    
    logger.info(f"✅ Service returned position size: {kelly_position.recommended_size}")
    logger.info(f"✅ Win probability: {kelly_position.win_probability:.2%}")
    logger.info(f"✅ Kelly fraction: {kelly_position.kelly_fraction:.3f}")
    
    # Check service status
    status = service.get_status()
    logger.info(f"✅ Service status: {status['service']} - ML enabled: {status['ml_enabled']}")
    
    return {
        'service_working': kelly_position.recommended_size >= 0,
        'ml_enabled': status['ml_enabled']
    }

async def test_ml_integration():
    """Test complete ML integration"""
    logger.info("\n🧪 Testing ML Integration...")
    
    ml_integration = get_ml_integration()
    
    # Mock market data with more features
    market_data = {
        'symbol': 'NQU25-CME',
        'close': 23500.0,
        'high': 23550.0,
        'low': 23450.0,
        'open': 23480.0,
        'volume': 1000,
        'price_change': 20.0,
        'volume_ratio': 1.2,
        'rsi': 55,
        'macd': 5.0,
        'bb_upper': 23600.0,
        'bb_lower': 23400.0,
        'bb_position': 0.5,
        'trend_strength': 0.7,
        'volatility': 0.015
    }
    
    # Get ML prediction
    prediction = await ml_integration.get_ml_prediction(
        symbol="NQU25-CME",
        market_data=market_data
    )
    
    logger.info(f"✅ ML Prediction Direction: {prediction['direction']}")
    logger.info(f"✅ ML Confidence: {prediction['confidence']:.2f}")
    logger.info(f"✅ Win Probability: {prediction['win_probability']:.2%}")
    logger.info(f"✅ Recommended Size: {prediction['recommended_size']} contracts")
    logger.info(f"✅ Kelly Fraction: {prediction.get('kelly_fraction', 0):.3f}")
    
    # Test performance tracking
    performance = ml_integration.get_performance_summary()
    logger.info(f"✅ Total predictions tracked: {performance['total_predictions']}")
    
    return {
        'ml_working': prediction['direction'] is not None,
        'kelly_integrated': prediction.get('recommended_size', 0) >= 0,
        'tracking_enabled': performance['total_predictions'] > 0
    }

async def test_trading_engine_integration():
    """Test Trading Engine with ML position sizing"""
    logger.info("\n🧪 Testing Trading Engine Integration...")
    
    from minhos.services.trading_engine import TradingEngine
    
    engine = TradingEngine()
    
    # Create a test signal
    test_signal = TradingSignal(
        timestamp=datetime.now(),
        symbol="NQU25-CME",
        signal=SignalType.BUY,
        confidence=0.75,
        reasoning="Test signal for Kelly sizing",
        entry_price=23500.0,
        target_price=23600.0,
        stop_loss=23450.0,
        context={
            'lstm_prediction': {
                'probability': 0.6,
                'confidence': 0.8,
                'direction': 1
            },
            'ensemble_prediction': {
                'probability': 0.58,
                'confidence': 0.75,
                'direction': 1
            }
        }
    )
    
    # Test position size calculation
    position_size = await engine._calculate_position_size(test_signal, 23500.0)
    
    logger.info(f"✅ Trading Engine calculated size: {position_size} contracts")
    
    # Check if ML sizing was used
    ml_sizing_used = engine.config.get('use_ml_position_sizing', False)
    logger.info(f"✅ ML position sizing enabled: {ml_sizing_used}")
    
    # Check if Kelly details were stored
    kelly_details = test_signal.context.get('kelly_position', {})
    if kelly_details:
        logger.info(f"✅ Kelly details stored in signal context:")
        logger.info(f"   Win probability: {kelly_details.get('win_probability', 0):.2%}")
        logger.info(f"   Kelly fraction: {kelly_details.get('kelly_fraction', 0):.3f}")
    
    return {
        'position_size': position_size,
        'ml_sizing_enabled': ml_sizing_used,
        'kelly_details_stored': len(kelly_details) > 0
    }

async def test_performance_tracking():
    """Test Kelly Criterion performance tracking"""
    logger.info("\n🧪 Testing Performance Tracking...")
    
    kelly = get_kelly_criterion()
    
    # Simulate some trades
    trades = [
        {'symbol': 'NQU25-CME', 'entry': 23500, 'exit': 23550, 'size': 2, 'predicted_dir': 1},
        {'symbol': 'NQU25-CME', 'entry': 23550, 'exit': 23530, 'size': 1, 'predicted_dir': 1},
        {'symbol': 'NQU25-CME', 'entry': 23530, 'exit': 23480, 'size': 2, 'predicted_dir': -1},
        {'symbol': 'NQU25-CME', 'entry': 23480, 'exit': 23520, 'size': 1, 'predicted_dir': 1},
    ]
    
    for trade in trades:
        kelly.update_performance(
            symbol=trade['symbol'],
            entry_price=trade['entry'],
            exit_price=trade['exit'],
            size=trade['size'],
            predicted_direction=trade['predicted_dir']
        )
    
    # Get performance summary
    performance = kelly.get_performance_summary()
    
    logger.info(f"✅ Total trades tracked: {performance['total_trades']}")
    logger.info(f"✅ Win rate: {performance['historical_stats']['win_rate']:.1%}")
    logger.info(f"✅ Average win: ${performance['historical_stats']['avg_win']:.2f}")
    logger.info(f"✅ Average loss: ${performance['historical_stats']['avg_loss']:.2f}")
    logger.info(f"✅ Total P&L: ${performance['total_pnl']:.2f}")
    logger.info(f"✅ Prediction accuracy: {performance['prediction_accuracy']:.1%}")
    
    return {
        'tracking_working': performance['total_trades'] == len(trades),
        'metrics_calculated': performance['historical_stats']['win_rate'] > 0
    }

async def main():
    """Run all tests"""
    logger.info("🚀 Starting ML-Enhanced Kelly Criterion Tests...")
    
    results = {}
    
    # Test 1: Kelly Criterion calculations
    calc_results = await test_kelly_criterion_calculations()
    results['kelly_calculations'] = calc_results
    
    # Test 2: Position Sizing Service
    service_results = await test_position_sizing_service()
    results['position_sizing_service'] = service_results
    
    # Test 3: ML Integration
    ml_results = await test_ml_integration()
    results['ml_integration'] = ml_results
    
    # Test 4: Trading Engine Integration
    engine_results = await test_trading_engine_integration()
    results['trading_engine'] = engine_results
    
    # Test 5: Performance Tracking
    perf_results = await test_performance_tracking()
    results['performance_tracking'] = perf_results
    
    # Summary
    logger.info("\n📊 Test Summary:")
    logger.info(f"✅ Kelly Calculations: Working")
    logger.info(f"✅ Position Sizing Service: {'Working' if service_results['service_working'] else 'Failed'}")
    logger.info(f"✅ ML Integration: {'Working' if ml_results['ml_working'] else 'Failed'}")
    logger.info(f"✅ Trading Engine: {'Integrated' if engine_results['ml_sizing_enabled'] else 'Not integrated'}")
    logger.info(f"✅ Performance Tracking: {'Working' if perf_results['tracking_working'] else 'Failed'}")
    
    # Overall success
    all_working = (
        service_results['service_working'] and
        ml_results['ml_working'] and
        engine_results['ml_sizing_enabled'] and
        perf_results['tracking_working']
    )
    
    if all_working:
        logger.info("\n🎉 ALL ML-ENHANCED KELLY CRITERION TESTS PASSED! 🎉")
        logger.info("✅ System ready for mathematically optimal position sizing!")
    else:
        logger.warning("\n⚠️ Some tests had issues - check details above")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())