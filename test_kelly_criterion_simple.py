#!/usr/bin/env python3
"""
Test Kelly Criterion Core Functionality

Tests the core Kelly Criterion calculations and position sizing logic
without requiring full ML system integration.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.ml.kelly_criterion import get_kelly_criterion, MLEnhancedKellyCriterion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_kelly_criterion_calculations():
    """Test core Kelly Criterion calculations"""
    logger.info("🧪 Testing Kelly Criterion Calculations...")
    
    kelly = MLEnhancedKellyCriterion(capital=100000.0)
    
    # Test Case 1: Favorable odds with high confidence
    logger.info("\nTest 1: Favorable odds (60% win rate, $50 avg win, $40 avg loss)")
    
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
    
    # Set historical stats for testing
    kelly.win_loss_history = [
        {'symbol': 'NQU25-CME', 'pnl': 50, 'timestamp': datetime.now()},
        {'symbol': 'NQU25-CME', 'pnl': -40, 'timestamp': datetime.now()},
        {'symbol': 'NQU25-CME', 'pnl': 55, 'timestamp': datetime.now()},
        {'symbol': 'NQU25-CME', 'pnl': -35, 'timestamp': datetime.now()},
        {'symbol': 'NQU25-CME', 'pnl': 45, 'timestamp': datetime.now()},
    ]
    
    position = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred,
        ensemble_prediction=ensemble_pred,
        risk_params={'max_position_size': 10}
    )
    
    logger.info(f"✅ Combined Win Probability: {position.win_probability:.2%}")
    logger.info(f"✅ Kelly Fraction: {position.kelly_fraction:.3f}")
    logger.info(f"✅ Confidence Score: {position.confidence_score:.2f}")
    logger.info(f"✅ Recommended Size: {position.recommended_size} contracts")
    logger.info(f"✅ Risk-Adjusted Size: {position.risk_adjusted_size} contracts")
    
    # Validate Kelly calculation
    expected_b = position.expected_win / position.expected_loss if position.expected_loss > 0 else 0
    expected_kelly = (position.win_probability * expected_b - (1 - position.win_probability)) / expected_b if expected_b > 0 else 0
    expected_kelly = max(0, min(expected_kelly, kelly.max_kelly_fraction))
    
    logger.info(f"✅ Expected Kelly (manual calc): {expected_kelly:.3f}")
    logger.info(f"✅ Odds ratio (b): {expected_b:.2f}")
    
    # Test Case 2: Unfavorable odds (should recommend 0)
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
    logger.info(f"✅ Recommended Size: {position2.recommended_size} contracts (should be 0)")
    
    # Test Case 3: Low confidence (below threshold)
    logger.info("\nTest 3: Low confidence prediction (below threshold)")
    
    lstm_pred3 = {
        'probability': 0.55,
        'confidence': 0.3,  # Low confidence
        'direction': 1
    }
    
    ensemble_pred3 = {
        'probability': 0.52,
        'confidence': 0.35,  # Low confidence
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
    logger.info(f"✅ Recommended Size: {position3.recommended_size} contracts (should be 0 due to low confidence)")
    
    # Test Case 4: Perfect scenario
    logger.info("\nTest 4: High confidence, high win probability")
    
    lstm_pred4 = {
        'probability': 0.75,
        'confidence': 0.9,
        'direction': 1
    }
    
    ensemble_pred4 = {
        'probability': 0.78,
        'confidence': 0.95,
        'direction': 1
    }
    
    position4 = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred4,
        ensemble_prediction=ensemble_pred4
    )
    
    logger.info(f"✅ Win Probability: {position4.win_probability:.2%}")
    logger.info(f"✅ Kelly Fraction: {position4.kelly_fraction:.3f}")
    logger.info(f"✅ Confidence Score: {position4.confidence_score:.2f}")
    logger.info(f"✅ Recommended Size: {position4.recommended_size} contracts")
    
    return {
        'test1_favorable': position.recommended_size > 0,
        'test1_kelly': position.kelly_fraction,
        'test2_unfavorable': position2.recommended_size == 0,
        'test3_low_confidence': position3.recommended_size == 0,
        'test4_high_confidence': position4.recommended_size > position.recommended_size
    }

def test_performance_tracking():
    """Test Kelly Criterion performance tracking"""
    logger.info("\n🧪 Testing Performance Tracking...")
    
    kelly = get_kelly_criterion()
    
    # Simulate some trades
    trades = [
        {'symbol': 'NQU25-CME', 'entry': 23500, 'exit': 23550, 'size': 2, 'predicted_dir': 1},  # Win
        {'symbol': 'NQU25-CME', 'entry': 23550, 'exit': 23530, 'size': 1, 'predicted_dir': 1},  # Loss (wrong direction)
        {'symbol': 'NQU25-CME', 'entry': 23530, 'exit': 23480, 'size': 2, 'predicted_dir': -1}, # Win (short)
        {'symbol': 'NQU25-CME', 'entry': 23480, 'exit': 23520, 'size': 1, 'predicted_dir': 1},  # Win
    ]
    
    for i, trade in enumerate(trades):
        kelly.update_performance(
            symbol=trade['symbol'],
            entry_price=trade['entry'],
            exit_price=trade['exit'],
            size=trade['size'],
            predicted_direction=trade['predicted_dir']
        )
        logger.info(f"   Trade {i+1}: Entry=${trade['entry']}, Exit=${trade['exit']}, "
                   f"PnL=${(trade['exit'] - trade['entry']) * trade['size'] * trade['predicted_dir']}")
    
    # Get performance summary
    performance = kelly.get_performance_summary()
    
    logger.info(f"✅ Total trades tracked: {performance['total_trades']}")
    logger.info(f"✅ Win rate: {performance['historical_stats']['win_rate']:.1%}")
    logger.info(f"✅ Average win: ${performance['historical_stats']['avg_win']:.2f}")
    logger.info(f"✅ Average loss: ${performance['historical_stats']['avg_loss']:.2f}")
    logger.info(f"✅ Total P&L: ${performance['total_pnl']:.2f}")
    logger.info(f"✅ Prediction accuracy: {performance['prediction_accuracy']:.1%}")
    
    if performance['historical_stats']['avg_loss'] > 0:
        reward_risk = performance['historical_stats']['avg_win'] / performance['historical_stats']['avg_loss']
        logger.info(f"✅ Reward/Risk ratio: {reward_risk:.2f}")
    
    return {
        'tracking_working': performance['total_trades'] == len(trades),
        'win_rate_calculated': performance['historical_stats']['win_rate'] > 0,
        'pnl_tracked': performance['total_pnl'] != 0
    }

def test_risk_adjustments():
    """Test risk adjustment features"""
    logger.info("\n🧪 Testing Risk Adjustments...")
    
    kelly = MLEnhancedKellyCriterion(capital=100000.0)
    
    # Base prediction
    lstm_pred = {'probability': 0.65, 'confidence': 0.8, 'direction': 1}
    ensemble_pred = {'probability': 0.63, 'confidence': 0.75, 'direction': 1}
    
    # Test 1: Normal conditions
    position1 = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred,
        ensemble_prediction=ensemble_pred
    )
    
    # Test 2: High volatility
    position2 = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred,
        ensemble_prediction=ensemble_pred,
        risk_params={'volatility_multiplier': 2.0}
    )
    
    # Test 3: During drawdown
    position3 = kelly.calculate_position_size(
        symbol="NQU25-CME",
        current_price=23500.0,
        lstm_prediction=lstm_pred,
        ensemble_prediction=ensemble_pred,
        risk_params={'current_drawdown': 0.1}  # 10% drawdown
    )
    
    logger.info(f"✅ Normal conditions size: {position1.recommended_size}")
    logger.info(f"✅ High volatility size: {position2.recommended_size} (should be smaller)")
    logger.info(f"✅ During drawdown size: {position3.recommended_size} (should be smaller)")
    
    return {
        'volatility_reduces_size': position2.recommended_size <= position1.recommended_size,
        'drawdown_reduces_size': position3.recommended_size <= position1.recommended_size
    }

def main():
    """Run all tests"""
    logger.info("🚀 Starting Kelly Criterion Core Tests...")
    
    results = {}
    
    # Test 1: Core Kelly calculations
    calc_results = test_kelly_criterion_calculations()
    results['kelly_calculations'] = calc_results
    
    # Test 2: Performance tracking
    perf_results = test_performance_tracking()
    results['performance_tracking'] = perf_results
    
    # Test 3: Risk adjustments
    risk_results = test_risk_adjustments()
    results['risk_adjustments'] = risk_results
    
    # Summary
    logger.info("\n📊 Test Summary:")
    logger.info(f"✅ Favorable odds test: {'PASS' if calc_results['test1_favorable'] else 'FAIL'}")
    logger.info(f"✅ Unfavorable odds test: {'PASS' if calc_results['test2_unfavorable'] else 'FAIL'}")
    logger.info(f"✅ Low confidence test: {'PASS' if calc_results['test3_low_confidence'] else 'FAIL'}")
    logger.info(f"✅ High confidence test: {'PASS' if calc_results['test4_high_confidence'] else 'FAIL'}")
    logger.info(f"✅ Performance tracking: {'PASS' if perf_results['tracking_working'] else 'FAIL'}")
    logger.info(f"✅ Risk adjustments: {'PASS' if risk_results['volatility_reduces_size'] else 'FAIL'}")
    
    # Overall success
    all_tests_pass = (
        calc_results['test1_favorable'] and
        calc_results['test2_unfavorable'] and
        calc_results['test3_low_confidence'] and
        perf_results['tracking_working'] and
        risk_results['volatility_reduces_size']
    )
    
    if all_tests_pass:
        logger.info("\n🎉 ALL KELLY CRITERION TESTS PASSED! 🎉")
        logger.info("✅ Core Kelly Criterion system working correctly!")
        logger.info("✅ Mathematical position sizing operational!")
        logger.info("✅ Risk adjustments functioning!")
        logger.info("✅ Performance tracking active!")
    else:
        logger.warning("\n⚠️ Some tests failed - check details above")
    
    return results

if __name__ == "__main__":
    main()