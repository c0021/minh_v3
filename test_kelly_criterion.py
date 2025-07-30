#!/usr/bin/env python3
"""
Test Kelly Criterion Implementation

Comprehensive test of the ML-Enhanced Kelly Criterion system.
Tests probability estimation, Kelly calculation, and full integration.
"""

import asyncio
import sys
import os
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add project root to path
sys.path.append('/home/colindo/Sync/minh_v4')

from capabilities.position_sizing.api import PositionSizingAPI
from capabilities.position_sizing.kelly.kelly_manager import KellyManager
from capabilities.position_sizing.kelly.probability_estimator import ProbabilityEstimator
from capabilities.position_sizing.kelly.kelly_calculator import KellyCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class KellyCriterionTester:
    """Comprehensive tester for Kelly Criterion implementation"""
    
    def __init__(self):
        self.logger = logger
        
    def generate_mock_market_data(self, num_points: int = 100) -> List[Dict[str, Any]]:
        """Generate realistic mock market data for testing"""
        data = []
        base_price = 23000
        
        for i in range(num_points):
            # Simulate realistic price movement
            change_pct = np.random.normal(0, 0.01)  # 1% daily volatility
            base_price *= (1 + change_pct)
            
            # Generate OHLCV data
            high = base_price * (1 + abs(np.random.normal(0, 0.005)))
            low = base_price * (1 - abs(np.random.normal(0, 0.005)))
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'timestamp': (datetime.now() - timedelta(hours=num_points-i)).timestamp(),
                'price': base_price,
                'close': base_price,
                'open': base_price * (1 + np.random.normal(0, 0.002)),
                'high': high,
                'low': low,
                'volume': volume
            })
        
        return data
    
    def generate_mock_training_data(self, num_trades: int = 150) -> List[Dict[str, Any]]:
        """Generate mock historical trade data for training"""
        training_data = []
        
        for i in range(num_trades):
            # Generate market data for this trade
            market_data = self.generate_mock_market_data(50)
            
            # Generate trading signal
            signal_confidence = np.random.uniform(0.5, 0.9)
            signal_direction = np.random.choice([-1, 1])
            
            signal = {
                'direction': signal_direction,
                'confidence': signal_confidence,
                'source': 'mock_signal'
            }
            
            # Simulate trade outcome (higher confidence = higher win probability)
            win_probability = 0.45 + (signal_confidence - 0.5) * 0.4
            outcome = 1 if np.random.random() < win_probability else 0
            
            # Simulate PnL
            if outcome:
                pnl = np.random.uniform(50, 300)  # Win
            else:
                pnl = -np.random.uniform(40, 250)  # Loss
            
            training_data.append({
                'market_data': market_data,
                'signal': signal,
                'outcome': outcome,
                'pnl': pnl,
                'timestamp': datetime.now() - timedelta(days=num_trades-i)
            })
        
        return training_data
    
    async def test_probability_estimator(self):
        """Test probability estimator component"""
        self.logger.info("Testing Probability Estimator...")
        
        try:
            estimator = ProbabilityEstimator()
            
            # Test feature engineering
            market_data = self.generate_mock_market_data(30)
            signal = {'direction': 1, 'confidence': 0.7}
            
            features = estimator.engineer_features(market_data, signal)
            self.logger.info(f"✓ Feature engineering: {len(features) if features is not None else 0} features")
            
            # Test prediction (should work even without training using fallback)
            prob_result = await estimator.estimate_win_probability(market_data, signal)
            self.logger.info(f"✓ Probability estimation: {prob_result['win_probability']:.1%} "
                           f"(source: {prob_result['source']})")
            
            # Test training
            training_data = self.generate_mock_training_data(120)
            train_result = await estimator.train_probability_estimator(training_data)
            
            if train_result['success']:
                self.logger.info(f"✓ Training successful: {train_result['test_accuracy']:.1%} accuracy")
                
                # Test trained prediction
                prob_result_trained = await estimator.estimate_win_probability(market_data, signal)
                self.logger.info(f"✓ Trained prediction: {prob_result_trained['win_probability']:.1%} "
                               f"(calibrated: {prob_result_trained['calibrated']})")
            else:
                self.logger.warning(f"Training failed: {train_result['message']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Probability estimator test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_kelly_calculator(self):
        """Test Kelly calculator component"""
        self.logger.info("Testing Kelly Calculator...")
        
        try:
            calculator = KellyCalculator()
            
            # Test basic calculation
            signal = {'direction': 1, 'confidence': 0.75}
            win_probability = 0.65
            capital = 100000
            market_data = self.generate_mock_market_data(30)
            
            kelly_result = await calculator.calculate_optimal_position_size(
                signal, win_probability, capital, market_data
            )
            
            self.logger.info(f"✓ Kelly calculation: ${kelly_result['position_size']:.0f} "
                           f"({kelly_result['position_pct']:.1%} of capital)")
            self.logger.info(f"  Kelly fraction: {kelly_result['kelly_fraction']:.3f}, "
                           f"Win prob: {kelly_result['win_probability']:.1%}")
            
            # Test with different scenarios
            scenarios = [
                {'win_prob': 0.51, 'confidence': 0.55, 'description': 'Low edge'},
                {'win_prob': 0.70, 'confidence': 0.85, 'description': 'High edge'},
                {'win_prob': 0.45, 'confidence': 0.60, 'description': 'No edge'},
            ]
            
            for scenario in scenarios:
                signal_test = {'direction': 1, 'confidence': scenario['confidence']}
                result = await calculator.calculate_optimal_position_size(
                    signal_test, scenario['win_prob'], capital, market_data
                )
                self.logger.info(f"  {scenario['description']}: "
                               f"{result['position_pct']:.1%} position")
            
            # Test trade outcome updates
            for i in range(10):
                pnl = np.random.uniform(-100, 150)
                calculator.update_trade_outcome(pnl, pnl > 0)
            
            stats = calculator.get_performance_stats()
            self.logger.info(f"✓ Performance tracking: {stats['total_trades']} trades, "
                           f"{stats['win_rate']:.1%} win rate")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Kelly calculator test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_kelly_manager(self):
        """Test Kelly manager integration"""
        self.logger.info("Testing Kelly Manager...")
        
        try:
            manager = KellyManager()
            
            # Test without training
            signal = {'direction': 1, 'confidence': 0.75}
            capital = 100000
            market_data = self.generate_mock_market_data(30)
            
            result = await manager.calculate_position_size(signal, capital, market_data)
            self.logger.info(f"✓ Untrained calculation: {result['position_pct']:.1%} "
                           f"(method: {result['method']})")
            
            # Test training
            training_data = self.generate_mock_training_data(120)
            train_result = await manager.train_kelly_system(training_data)
            
            if train_result['success']:
                self.logger.info(f"✓ Training successful")
                
                # Test trained calculation
                result_trained = await manager.calculate_position_size(signal, capital, market_data)
                self.logger.info(f"✓ Trained calculation: {result_trained['position_pct']:.1%} "
                               f"(Win prob: {result_trained['win_probability']:.1%})")
            else:
                self.logger.warning(f"Training failed: {train_result['message']}")
            
            # Test performance summary
            performance = manager.get_performance_summary()
            self.logger.info(f"✓ Performance summary: Ready={performance['system_ready']}, "
                           f"Predictions={performance['total_predictions']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Kelly manager test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_position_sizing_api(self):
        """Test unified position sizing API"""
        self.logger.info("Testing Position Sizing API...")
        
        try:
            api = PositionSizingAPI()
            
            signal = {'direction': 1, 'confidence': 0.75}
            capital = 100000
            market_data = self.generate_mock_market_data(30)
            
            # Test different methods
            methods = ['fixed', 'kelly']
            
            for method in methods:
                result = await api.calculate_position_size(signal, capital, market_data, method)
                self.logger.info(f"✓ {method.upper()} method: {result['position_pct']:.1%} "
                               f"(${result['position_size']:.0f})")
            
            # Test recommendation system
            recommendation = api.get_sizing_recommendation(signal, capital, market_data)
            self.logger.info(f"✓ Recommendation: {recommendation['recommended']['method']} method, "
                           f"{recommendation['recommended']['position_pct']:.1%}")
            
            # Test system status
            status = api.get_system_status()
            self.logger.info(f"✓ System status: {len(status['methods_available'])} methods available")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Position sizing API test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_comprehensive_test(self):
        """Run all Kelly Criterion tests"""
        self.logger.info("🚀 Starting Kelly Criterion Comprehensive Test")
        self.logger.info("=" * 60)
        
        test_results = []
        
        # Run individual component tests
        tests = [
            ("Probability Estimator", self.test_probability_estimator),
            ("Kelly Calculator", self.test_kelly_calculator),
            ("Kelly Manager", self.test_kelly_manager),
            ("Position Sizing API", self.test_position_sizing_api),
        ]
        
        for test_name, test_func in tests:
            self.logger.info(f"\n📊 Testing {test_name}...")
            try:
                result = await test_func()
                test_results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                self.logger.info(f"{status}: {test_name}")
            except Exception as e:
                test_results.append((test_name, False))
                self.logger.error(f"❌ FAILED: {test_name} - {e}")
        
        # Summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📈 KELLY CRITERION TEST SUMMARY")
        self.logger.info("=" * 60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            self.logger.info(f"{status}: {test_name}")
        
        self.logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        
        if passed == total:
            self.logger.info("🎉 All Kelly Criterion tests PASSED! Ready for integration.")
        else:
            self.logger.warning(f"⚠️  {total-passed} test(s) failed. Review implementation.")
        
        return passed == total

async def main():
    """Main test execution"""
    tester = KellyCriterionTester()
    success = await tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())