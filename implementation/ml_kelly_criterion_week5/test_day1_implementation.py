#!/usr/bin/env python3
"""
Day 1 Implementation Test
=========================

Quick validation of Day 1 Kelly Calculator and Probability Estimator implementation.
Tests core functionality without complex unit testing framework dependencies.

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import sys
from datetime import datetime, timedelta

# Import our implementations
from core.kelly_calculator import KellyCalculator, kelly_criterion_formula
from core.probability_estimator import MLProbabilityEstimator, ModelPrediction

def test_kelly_formula():
    """Test basic Kelly Criterion formula"""
    print("\n🧮 Testing Kelly Criterion Formula...")
    
    test_cases = [
        (0.6, 2.0, 0.4),     # Basic positive edge
        (0.5, 1.0, 0.0),     # No edge
        (0.7, 1.5, 0.5),     # Good edge
    ]
    
    passed = 0
    for win_prob, win_loss_ratio, expected in test_cases:
        result = kelly_criterion_formula(win_prob, win_loss_ratio)
        diff = abs(result - expected)
        
        if diff < 0.001:
            print(f"  ✅ P={win_prob}, W/L={win_loss_ratio} → Kelly={result:.3f} (expected {expected})")
            passed += 1
        else:
            print(f"  ❌ P={win_prob}, W/L={win_loss_ratio} → Kelly={result:.3f} (expected {expected}) - diff: {diff:.3f}")
    
    print(f"  Kelly Formula Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_kelly_calculator():
    """Test Kelly Calculator class"""
    print("\n⚙️ Testing Kelly Calculator Class...")
    
    calculator = KellyCalculator()
    
    # Test basic calculation
    try:
        result = calculator.calculate_position_recommendation(
            symbol='NQU25-CME',
            win_probability=0.65,
            win_loss_ratio=1.8,
            ml_confidence=0.75,
            account_capital=100000.0
        )
        
        print(f"  ✅ Position recommendation generated:")
        print(f"     Symbol: {result.symbol}")
        print(f"     Kelly Fraction: {result.kelly_fraction:.3f}")
        print(f"     Position Size: {result.position_size} contracts")
        print(f"     Capital Risk: {result.max_capital_risk:.3f}")
        print(f"     Reasoning: {result.reasoning}")
        
        # Basic validation
        assert result.kelly_fraction >= 0
        assert result.position_size >= 0
        assert result.confidence == 0.75
        assert result.symbol == 'NQU25-CME'
        
        print("  ✅ Kelly Calculator class working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Kelly Calculator failed: {e}")
        return False

def test_probability_estimator():
    """Test ML Probability Estimator"""
    print("\n🧠 Testing ML Probability Estimator...")
    
    estimator = MLProbabilityEstimator()
    
    # Test model predictions
    sample_predictions = [
        {
            'model_type': 'lstm',
            'confidence': 0.75,
            'direction': 'long',
            'historical_accuracy': 0.65
        },
        {
            'model_type': 'ensemble',
            'confidence': 0.70,
            'direction': 'long',
            'historical_accuracy': 0.70
        }
    ]
    
    # Test trade history
    sample_trades = [
        {'pnl': 150.0, 'timestamp': (datetime.now() - timedelta(days=5)).isoformat(), 'symbol': 'NQU25-CME'},
        {'pnl': -100.0, 'timestamp': (datetime.now() - timedelta(days=10)).isoformat(), 'symbol': 'NQU25-CME'},
        {'pnl': 200.0, 'timestamp': (datetime.now() - timedelta(days=15)).isoformat(), 'symbol': 'NQU25-CME'},
        {'pnl': -120.0, 'timestamp': (datetime.now() - timedelta(days=20)).isoformat(), 'symbol': 'NQU25-CME'},
    ]
    
    try:
        # Test probability estimation
        prob_estimate = estimator.estimate_trading_probability(
            sample_predictions, sample_trades, 'NQU25-CME'
        )
        
        print(f"  ✅ Probability estimation generated:")
        print(f"     Win Probability: {prob_estimate.win_probability:.3f}")
        print(f"     Win/Loss Ratio: {prob_estimate.win_loss_ratio:.3f}")
        print(f"     Confidence: {prob_estimate.confidence:.3f}")
        print(f"     Model Agreement: {prob_estimate.model_agreement}")
        print(f"     Reasoning: {prob_estimate.reasoning}")
        
        # Basic validation
        assert 0 <= prob_estimate.win_probability <= 1
        assert prob_estimate.win_loss_ratio >= 0
        assert 0 <= prob_estimate.confidence <= 1
        
        print("  ✅ Probability Estimator working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Probability Estimator failed: {e}")
        return False

def test_integration():
    """Test Kelly Calculator + Probability Estimator integration"""
    print("\n🔗 Testing Integration...")
    
    try:
        # Create components
        calculator = KellyCalculator()
        estimator = MLProbabilityEstimator()
        
        # Sample ML predictions
        ml_predictions = [
            {'model_type': 'lstm', 'confidence': 0.72, 'direction': 'long'},
            {'model_type': 'ensemble', 'confidence': 0.68, 'direction': 'long'}
        ]
        
        # Sample trade history
        trade_history = [
            {'pnl': 100, 'timestamp': datetime.now().isoformat(), 'symbol': 'NQU25-CME'}
            for _ in range(5)  # Small trade history
        ]
        
        # Step 1: Get probability estimate
        prob_estimate = estimator.estimate_trading_probability(
            ml_predictions, trade_history, 'NQU25-CME'
        )
        
        # Step 2: Calculate Kelly position
        kelly_result = calculator.calculate_position_recommendation(
            symbol='NQU25-CME',
            win_probability=prob_estimate.win_probability,
            win_loss_ratio=prob_estimate.win_loss_ratio,
            ml_confidence=prob_estimate.confidence,
            account_capital=100000.0
        )
        
        print(f"  ✅ Integration test successful:")
        print(f"     ML Models → Probability: {prob_estimate.win_probability:.3f}")
        print(f"     Probability → Kelly: {kelly_result.kelly_fraction:.3f}")
        print(f"     Kelly → Position: {kelly_result.position_size} contracts")
        print(f"     End-to-end reasoning: ML confidence → Kelly position sizing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False

def main():
    """Run all Day 1 implementation tests"""
    print("🚀 MinhOS v4 - Kelly Criterion Day 1 Implementation Test")
    print("=" * 60)
    
    tests = [
        ("Kelly Formula", test_kelly_formula),
        ("Kelly Calculator", test_kelly_calculator),
        ("Probability Estimator", test_probability_estimator),
        ("Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 Day 1 Implementation: ALL TESTS PASSED!")
        print("✅ Ready to proceed to Day 2: ML Integration")
    else:
        print(f"\n⚠️  Day 1 Implementation: {total-passed} tests failed")
        print("❌ Fix failing tests before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)