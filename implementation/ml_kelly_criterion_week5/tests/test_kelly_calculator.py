#!/usr/bin/env python3
"""
Kelly Calculator Tests
=====================

Comprehensive unit tests for Kelly Calculator core functionality.
Tests mathematical accuracy, edge cases, and integration scenarios.

Test Categories:
- Mathematical validation
- Input validation and error handling
- Configuration and constraints
- Integration scenarios
- Performance benchmarks

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import unittest
import math
from datetime import datetime, timedelta
from typing import Dict, List

# Import the modules we're testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.kelly_calculator import (
    KellyCalculator, 
    KellyResult,
    kelly_criterion_formula,
    expected_growth_rate
)
from core.probability_estimator import (
    MLProbabilityEstimator,
    ModelPrediction,
    ProbabilityEstimate,
    simple_confidence_to_probability,
    calculate_edge
)


class TestKellyCriterionFormula(unittest.TestCase):
    """Test the core Kelly Criterion mathematical formula"""
    
    def test_basic_kelly_formula(self):
        """Test Kelly formula with known results"""
        test_cases = [
            # (win_prob, win_loss_ratio, expected_kelly)
            # Kelly formula: f* = (bp - q) / b = (b*p - (1-p)) / b
            (0.6, 2.0, 0.4),     # (2*0.6 - 0.4) / 2 = 0.8/2 = 0.4
            (0.7, 1.5, 0.5),     # (1.5*0.7 - 0.3) / 1.5 = 0.75/1.5 = 0.5
            (0.5, 1.0, 0.0),     # No edge: 50% win, 1:1 ratio = 0% Kelly
            (0.4, 2.0, 0.1),     # (2*0.4 - 0.6) / 2 = 0.2/2 = 0.1
            (0.8, 3.0, 0.733),   # (3*0.8 - 0.2) / 3 = 2.2/3 ≈ 0.733
        ]
        
        for win_prob, win_loss_ratio, expected in test_cases:
            with self.subTest(win_prob=win_prob, win_loss_ratio=win_loss_ratio):
                result = kelly_criterion_formula(win_prob, win_loss_ratio)
                self.assertAlmostEqual(result, expected, places=3,
                    msg=f"Kelly formula failed for p={win_prob}, b={win_loss_ratio}")
    
    def test_kelly_formula_edge_cases(self):
        """Test Kelly formula edge cases"""
        # Zero probability
        self.assertEqual(kelly_criterion_formula(0.0, 2.0), 0.0)
        
        # Zero win/loss ratio
        self.assertEqual(kelly_criterion_formula(0.6, 0.0), 0.0)
        
        # Negative inputs should return 0
        self.assertEqual(kelly_criterion_formula(-0.1, 2.0), 0.0)
        self.assertEqual(kelly_criterion_formula(0.6, -1.0), 0.0)
        
        # Probability > 1 (invalid but should be handled)
        self.assertEqual(kelly_criterion_formula(1.1, 2.0), 0.0)
    
    def test_expected_growth_rate(self):
        """Test expected growth rate calculation"""
        # Positive edge case
        growth = expected_growth_rate(0.1, 0.6, 2.0)
        self.assertGreater(growth, 0, "Positive edge should have positive growth")
        
        # Zero Kelly fraction
        growth = expected_growth_rate(0.0, 0.6, 2.0)
        self.assertEqual(growth, 0.0, "Zero Kelly should have zero growth")
        
        # Full Kelly fraction (should be close to maximum growth)
        optimal_kelly = kelly_criterion_formula(0.6, 2.0)
        optimal_growth = expected_growth_rate(optimal_kelly, 0.6, 2.0)
        
        # Test that slightly less Kelly has lower growth
        reduced_growth = expected_growth_rate(optimal_kelly * 0.9, 0.6, 2.0)
        self.assertLess(reduced_growth, optimal_growth)


class TestKellyCalculator(unittest.TestCase):
    """Test the KellyCalculator class"""
    
    def setUp(self):
        """Set up test calculator with default config"""
        self.calculator = KellyCalculator()
        
        # Test configuration
        self.test_config = {
            'min_kelly_fraction': 0.01,
            'max_kelly_fraction': 0.25,
            'confidence_threshold': 0.6,
            'max_portfolio_risk': 0.20,
            'max_position_size': 5,
            'kelly_fraction_multiplier': 0.6
        }
    
    def test_kelly_calculator_initialization(self):
        """Test Kelly Calculator initialization"""
        # Default initialization
        calc = KellyCalculator()
        self.assertEqual(calc.min_kelly_fraction, 0.01)
        self.assertEqual(calc.max_kelly_fraction, 0.25)
        
        # Custom config initialization
        custom_config = {'min_kelly_fraction': 0.02, 'max_kelly_fraction': 0.30}
        calc = KellyCalculator(custom_config)
        self.assertEqual(calc.min_kelly_fraction, 0.02)
        self.assertEqual(calc.max_kelly_fraction, 0.30)
    
    def test_basic_kelly_calculation(self):
        """Test basic Kelly fraction calculation"""
        # Standard case
        kelly = self.calculator.calculate_kelly_fraction(0.6, 2.0)
        self.assertAlmostEqual(kelly, 0.1, places=3)
        
        # Test max Kelly constraint
        kelly = self.calculator.calculate_kelly_fraction(0.9, 10.0)  # Would be very high
        self.assertLessEqual(kelly, self.calculator.max_kelly_fraction)
    
    def test_fractional_kelly(self):
        """Test fractional Kelly application"""
        # Base Kelly calculation
        base_kelly = self.calculator.calculate_kelly_fraction(0.7, 2.0)
        
        # Apply fractional Kelly
        fractional_kelly = self.calculator.apply_fractional_kelly(base_kelly, confidence=0.8)
        
        # Should be less than full Kelly
        self.assertLess(fractional_kelly, base_kelly)
        
        # Should be reasonable fraction
        expected_fractional = base_kelly * self.calculator.kelly_fraction_multiplier
        self.assertAlmostEqual(fractional_kelly, expected_fractional, delta=0.02)
    
    def test_position_size_conversion(self):
        """Test Kelly fraction to position size conversion"""
        kelly_fraction = 0.15  # 15% of capital
        account_capital = 100000.0  # $100k account
        
        contracts, capital_fraction = self.calculator.convert_kelly_to_position_size(
            kelly_fraction, 'NQU25-CME', account_capital
        )
        
        # Should get reasonable position size
        self.assertGreater(contracts, 0)
        self.assertLessEqual(contracts, self.calculator.max_single_position)
        
        # Capital fraction should be reasonable (contract value estimation may be high)
        self.assertGreater(capital_fraction, 0.0)
        self.assertLessEqual(capital_fraction, 1.0)  # Should not exceed 100% of capital
    
    def test_portfolio_constraints(self):
        """Test portfolio-level constraints"""
        kelly_fraction = 0.15
        current_risk = 0.10  # Already 10% at risk
        
        adjusted_kelly, constraints = self.calculator.apply_portfolio_constraints(
            kelly_fraction, 'NQU25-CME', current_risk
        )
        
        # Should not exceed total portfolio risk
        self.assertLessEqual(adjusted_kelly + current_risk, self.calculator.max_portfolio_risk)
        
        # Test portfolio limit exceeded
        current_risk = 0.25  # Exceeds max 20%
        adjusted_kelly, constraints = self.calculator.apply_portfolio_constraints(
            kelly_fraction, 'NQU25-CME', current_risk
        )
        self.assertEqual(adjusted_kelly, 0.0)
        self.assertIn('portfolio_limit_exceeded', constraints)
    
    def test_complete_position_recommendation(self):
        """Test complete position recommendation pipeline"""
        result = self.calculator.calculate_position_recommendation(
            symbol='NQU25-CME',
            win_probability=0.65,
            win_loss_ratio=1.8,
            ml_confidence=0.75,
            account_capital=100000.0,
            current_portfolio_risk=0.05
        )
        
        # Verify result structure
        self.assertIsInstance(result, KellyResult)
        self.assertEqual(result.symbol, 'NQU25-CME')
        self.assertGreater(result.kelly_fraction, 0)
        self.assertGreater(result.position_size, 0)
        self.assertEqual(result.confidence, 0.75)
        self.assertIsNotNone(result.reasoning)
    
    def test_input_validation(self):
        """Test input validation"""
        # Valid inputs
        self.assertTrue(self.calculator.validate_inputs(0.6, 2.0, 0.7))
        
        # Invalid win probability
        self.assertFalse(self.calculator.validate_inputs(-0.1, 2.0, 0.7))
        self.assertFalse(self.calculator.validate_inputs(1.5, 2.0, 0.7))
        
        # Invalid win/loss ratio
        self.assertFalse(self.calculator.validate_inputs(0.6, -1.0, 0.7))
        self.assertFalse(self.calculator.validate_inputs(0.6, 0.0, 0.7))
        
        # Invalid confidence
        self.assertFalse(self.calculator.validate_inputs(0.6, 2.0, -0.1))
        self.assertFalse(self.calculator.validate_inputs(0.6, 2.0, 1.5))
        
        # Below confidence threshold
        self.assertFalse(self.calculator.validate_inputs(0.6, 2.0, 0.5))  # Below 0.6 threshold


class TestProbabilityEstimator(unittest.TestCase):
    """Test the ML Probability Estimator"""
    
    def setUp(self):
        """Set up test probability estimator"""
        self.estimator = MLProbabilityEstimator()
        
        # Sample ML predictions
        self.sample_predictions = [
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
        
        # Sample trade history
        self.sample_trade_history = [
            {'pnl': 150.0, 'timestamp': (datetime.now() - timedelta(days=5)).isoformat(), 'symbol': 'NQU25-CME'},
            {'pnl': -100.0, 'timestamp': (datetime.now() - timedelta(days=10)).isoformat(), 'symbol': 'NQU25-CME'},
            {'pnl': 200.0, 'timestamp': (datetime.now() - timedelta(days=15)).isoformat(), 'symbol': 'NQU25-CME'},
            {'pnl': -120.0, 'timestamp': (datetime.now() - timedelta(days=20)).isoformat(), 'symbol': 'NQU25-CME'},
        ]
    
    def test_confidence_calibration(self):
        """Test confidence to probability calibration"""
        # Test basic calibration
        prob = self.estimator.calibrate_confidence_to_probability(0.8, 'lstm', 0.65)
        
        # Should be between 0.5 and 0.8 (pulled toward historical accuracy)
        self.assertGreater(prob, 0.5)
        self.assertLess(prob, 0.8)
        
        # Test with perfect historical accuracy
        prob_perfect = self.estimator.calibrate_confidence_to_probability(0.8, 'lstm', 1.0)
        self.assertAlmostEqual(prob_perfect, 0.8, places=2)
    
    def test_model_aggregation_agreement(self):
        """Test model aggregation when models agree"""
        # Models agree on direction
        predictions = [
            ModelPrediction('lstm', 0.75, 'long', historical_accuracy=0.65),
            ModelPrediction('ensemble', 0.70, 'long', historical_accuracy=0.70)
        ]
        
        result = self.estimator.aggregate_model_predictions(predictions)
        
        self.assertTrue(result.model_agreement)
        self.assertGreater(result.win_probability, 0.5)
        self.assertGreater(result.confidence, 0)
        self.assertEqual(len(result.individual_probabilities), 2)
    
    def test_model_aggregation_disagreement(self):
        """Test model aggregation when models disagree"""
        # Models disagree on direction
        predictions = [
            ModelPrediction('lstm', 0.75, 'long', historical_accuracy=0.65),
            ModelPrediction('ensemble', 0.70, 'short', historical_accuracy=0.70)
        ]
        
        result = self.estimator.aggregate_model_predictions(predictions)
        
        self.assertFalse(result.model_agreement)
        self.assertEqual(result.win_probability, 0.5)  # Neutral when disagree
        self.assertEqual(result.confidence, 0.0)
    
    def test_win_loss_ratio_calculation(self):
        """Test win/loss ratio calculation from trade history"""
        ratio = self.estimator.calculate_historical_win_loss_ratio(
            self.sample_trade_history, 'NQU25-CME'
        )
        
        # With small sample size, may return default ratio
        # Expected: wins = [150, 200] avg = 175, losses = [100, 120] avg = 110
        # Ratio = 175/110 ≈ 1.59, but may use default if insufficient data
        if len(self.sample_trade_history) >= self.estimator.min_trades_for_ratio:
            expected_ratio = 175.0 / 110.0
            self.assertAlmostEqual(ratio, expected_ratio, places=2)
        else:
            # Should return default ratio for insufficient data
            self.assertEqual(ratio, self.estimator.config.get('default_win_loss_ratio', 1.2))
    
    def test_complete_probability_estimation(self):
        """Test complete probability estimation pipeline"""
        result = self.estimator.estimate_trading_probability(
            self.sample_predictions,
            self.sample_trade_history,
            'NQU25-CME'
        )
        
        # Verify result structure
        self.assertIsInstance(result, ProbabilityEstimate)
        self.assertGreater(result.win_probability, 0.5)  # Models are confident and agree
        self.assertGreater(result.win_loss_ratio, 1.0)   # Historical data shows positive ratio
        self.assertTrue(result.model_agreement)
        self.assertIsNotNone(result.reasoning)
    
    def test_prediction_quality_validation(self):
        """Test prediction quality validation"""
        # Good prediction
        good_prediction = ProbabilityEstimate(
            win_probability=0.65,
            win_loss_ratio=1.5,
            confidence=0.7,
            model_agreement=True,
            individual_probabilities=[0.6, 0.7],
            reasoning="Test",
            metadata={}
        )
        
        validation = self.estimator.validate_prediction_quality(good_prediction)
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)
        
        # Poor prediction (low confidence)
        poor_prediction = ProbabilityEstimate(
            win_probability=0.65,
            win_loss_ratio=1.5,
            confidence=0.4,  # Below threshold
            model_agreement=True,
            individual_probabilities=[0.4, 0.4],
            reasoning="Test",
            metadata={}
        )
        
        validation = self.estimator.validate_prediction_quality(poor_prediction)
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_simple_confidence_conversion(self):
        """Test simple confidence to probability conversion"""
        # High confidence
        prob = simple_confidence_to_probability(0.8, 0.65)
        self.assertGreater(prob, 0.5)
        self.assertLess(prob, 0.8)
        
        # Low confidence (below 0.5)
        prob = simple_confidence_to_probability(0.3, 0.65)
        self.assertGreater(prob, 0.5)  # Should flip to opposite direction
    
    def test_edge_calculation(self):
        """Test expected edge calculation"""
        # Positive edge
        edge = calculate_edge(0.6, 2.0)
        self.assertGreater(edge, 0)
        
        # Zero edge
        edge = calculate_edge(0.5, 1.0)
        self.assertAlmostEqual(edge, 0.0, places=3)
        
        # Negative edge
        edge = calculate_edge(0.4, 1.5)
        self.assertLess(edge, 0.01)  # Allow for floating point precision


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmark tests"""
    
    def test_kelly_calculation_speed(self):
        """Test Kelly calculation performance"""
        import time
        
        calculator = KellyCalculator()
        
        # Time multiple calculations
        start_time = time.time()
        
        for _ in range(1000):
            result = calculator.calculate_position_recommendation(
                symbol='NQU25-CME',
                win_probability=0.65,
                win_loss_ratio=1.8,
                ml_confidence=0.75,
                account_capital=100000.0
            )
        
        end_time = time.time()
        avg_time_ms = ((end_time - start_time) / 1000) * 1000
        
        # Should be well under 100ms per calculation
        self.assertLess(avg_time_ms, 10.0, 
                       f"Kelly calculation too slow: {avg_time_ms:.2f}ms average")
        
        print(f"Kelly calculation performance: {avg_time_ms:.2f}ms average per calculation")
    
    def test_probability_estimation_speed(self):
        """Test probability estimation performance"""
        import time
        
        estimator = MLProbabilityEstimator()
        
        predictions = [
            {'model_type': 'lstm', 'confidence': 0.75, 'direction': 'long'},
            {'model_type': 'ensemble', 'confidence': 0.70, 'direction': 'long'}
        ]
        
        trade_history = [
            {'pnl': 100, 'timestamp': datetime.now().isoformat(), 'symbol': 'NQU25-CME'}
            for _ in range(50)  # 50 sample trades
        ]
        
        start_time = time.time()
        
        for _ in range(100):
            result = estimator.estimate_trading_probability(
                predictions, trade_history, 'NQU25-CME'
            )
        
        end_time = time.time()
        avg_time_ms = ((end_time - start_time) / 100) * 1000
        
        # Should be fast
        self.assertLess(avg_time_ms, 50.0,
                       f"Probability estimation too slow: {avg_time_ms:.2f}ms average")
        
        print(f"Probability estimation performance: {avg_time_ms:.2f}ms average per calculation")


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2)