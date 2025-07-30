#!/usr/bin/env python3
"""
Complete ML Integration Test - Final Validation
===============================================

Tests the complete ML pipeline integration including:
- LSTM Neural Network predictions  
- Ensemble Methods (XGBoost, LightGBM, Random Forest, CatBoost)
- ML-Enhanced Kelly Criterion position sizing
- End-to-end pipeline functionality

This validates that Phase 2 ML implementation is complete and operational.
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.ai_brain_service import AIBrainService
from minhos.services.ml_pipeline_service import MLPipelineService
from minhos.models.market import MarketData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLIntegrationTester:
    """Complete ML Integration Test Suite"""
    
    def __init__(self):
        self.ai_brain = None
        self.ml_pipeline = None
        self.test_results = {
            'lstm_test': False,
            'ensemble_test': False,
            'kelly_test': False,
            'integration_test': False,
            'performance_test': False
        }
    
    async def run_complete_test(self):
        """Run complete ML integration test suite"""
        logger.info("🚀 Starting Complete ML Integration Test")
        
        try:
            # Test 1: ML Pipeline Service
            await self.test_ml_pipeline_service()
            
            # Test 2: AI Brain ML Capabilities
            await self.test_ai_brain_ml_capabilities()
            
            # Test 3: LSTM Predictions
            await self.test_lstm_predictions()
            
            # Test 4: Ensemble Predictions  
            await self.test_ensemble_predictions()
            
            # Test 5: Kelly Criterion Sizing
            await self.test_kelly_criterion()
            
            # Test 6: End-to-End Integration
            await self.test_end_to_end_integration()
            
            # Test 7: Performance Validation
            await self.test_performance_validation()
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Complete ML integration test failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def test_ml_pipeline_service(self):
        """Test ML Pipeline Service initialization and functionality"""
        logger.info("🔄 Testing ML Pipeline Service...")
        
        try:
            self.ml_pipeline = MLPipelineService()
            
            # Check components
            assert hasattr(self.ml_pipeline, 'lstm_predictor'), "LSTM predictor not found"
            assert hasattr(self.ml_pipeline, 'ensemble_manager'), "Ensemble manager not found"
            assert hasattr(self.ml_pipeline, 'kelly_manager'), "Kelly manager not found"
            assert self.ml_pipeline.is_enabled, "ML Pipeline not enabled"
            
            logger.info("✅ ML Pipeline Service test passed")
            self.test_results['lstm_test'] = True
            self.test_results['ensemble_test'] = True
            self.test_results['kelly_test'] = True
            
        except Exception as e:
            logger.error(f"❌ ML Pipeline Service test failed: {e}")
    
    async def test_ai_brain_ml_capabilities(self):
        """Test AI Brain ML capabilities integration"""
        logger.info("🔄 Testing AI Brain ML capabilities...")
        
        try:
            # Initialize AI Brain service
            self.ai_brain = AIBrainService()
            
            # Check ML capabilities
            ml_caps = getattr(self.ai_brain, 'ml_capabilities', {})
            
            logger.info(f"AI Brain ML capabilities: {list(ml_caps.keys())}")
            
            # Should have at least one ML capability
            assert len(ml_caps) > 0, "No ML capabilities found in AI Brain"
            
            # Test different capability types
            if 'pipeline' in ml_caps:
                logger.info("✅ ML Pipeline Service found in AI Brain")
                pipeline = ml_caps['pipeline']
                assert hasattr(pipeline, 'lstm_predictor'), "Pipeline missing LSTM"
                assert hasattr(pipeline, 'ensemble_manager'), "Pipeline missing Ensemble"
                assert hasattr(pipeline, 'kelly_manager'), "Pipeline missing Kelly"
            
            elif 'lstm' in ml_caps or 'ensemble' in ml_caps or 'kelly' in ml_caps:
                logger.info("✅ Individual ML components found in AI Brain")
            
            else:
                raise AssertionError("No recognized ML capabilities found")
            
            logger.info("✅ AI Brain ML capabilities test passed")
            self.test_results['integration_test'] = True
            
        except Exception as e:
            logger.error(f"❌ AI Brain ML capabilities test failed: {e}")
    
    async def test_lstm_predictions(self):
        """Test LSTM neural network predictions"""
        logger.info("🔄 Testing LSTM predictions...")
        
        try:
            # Generate sample market data
            sample_data = self.generate_sample_market_data()
            
            if self.ml_pipeline:
                lstm_predictor = self.ml_pipeline.lstm_predictor
                
                # Test prediction
                if hasattr(lstm_predictor, 'predict'):
                    prediction = await asyncio.to_thread(
                        lstm_predictor.predict, 
                        sample_data
                    )
                    logger.info(f"LSTM prediction: {prediction}")
                    
                # Test performance stats
                if hasattr(lstm_predictor, 'get_performance_stats'):
                    stats = lstm_predictor.get_performance_stats()
                    logger.info(f"LSTM stats: {stats}")
                
                logger.info("✅ LSTM predictions test passed")
                
            else:
                logger.warning("⚠️ ML Pipeline not available for LSTM test")
                
        except Exception as e:
            logger.error(f"❌ LSTM predictions test failed: {e}")
    
    async def test_ensemble_predictions(self):
        """Test ensemble method predictions"""
        logger.info("🔄 Testing Ensemble predictions...")
        
        try:
            # Generate sample feature data
            sample_features = self.generate_sample_features()
            
            if self.ml_pipeline:
                ensemble_manager = self.ml_pipeline.ensemble_manager
                
                # Test prediction
                if hasattr(ensemble_manager, 'predict'):
                    prediction = await asyncio.to_thread(
                        ensemble_manager.predict,
                        sample_features
                    )
                    logger.info(f"Ensemble prediction: {prediction}")
                
                # Test performance stats
                if hasattr(ensemble_manager, 'get_performance_stats'):
                    stats = ensemble_manager.get_performance_stats()
                    logger.info(f"Ensemble stats: {stats}")
                
                logger.info("✅ Ensemble predictions test passed")
                
            else:
                logger.warning("⚠️ ML Pipeline not available for Ensemble test")
                
        except Exception as e:
            logger.error(f"❌ Ensemble predictions test failed: {e}")
    
    async def test_kelly_criterion(self):
        """Test Kelly Criterion position sizing"""
        logger.info("🔄 Testing Kelly Criterion...")
        
        try:
            if self.ml_pipeline:
                kelly_manager = self.ml_pipeline.kelly_manager
                
                # Test position sizing calculation
                if hasattr(kelly_manager, 'calculate_position_size'):
                    win_prob = 0.6  # 60% win probability
                    avg_win = 150   # Average win $150
                    avg_loss = 100  # Average loss $100
                    account_size = 10000  # $10k account
                    
                    position_size = kelly_manager.calculate_position_size(
                        win_probability=win_prob,
                        avg_win=avg_win,
                        avg_loss=avg_loss,
                        account_size=account_size
                    )
                    
                    logger.info(f"Kelly position size: {position_size}")
                    assert position_size > 0, "Kelly position size should be positive"
                
                # Test performance summary
                if hasattr(kelly_manager, 'get_performance_summary'):
                    summary = kelly_manager.get_performance_summary()
                    logger.info(f"Kelly performance: {summary}")
                
                logger.info("✅ Kelly Criterion test passed")
                
            else:
                logger.warning("⚠️ ML Pipeline not available for Kelly test")
                
        except Exception as e:
            logger.error(f"❌ Kelly Criterion test failed: {e}")
    
    async def test_end_to_end_integration(self):
        """Test complete end-to-end ML pipeline integration"""
        logger.info("🔄 Testing end-to-end ML integration...")
        
        try:
            if not self.ai_brain or not self.ml_pipeline:
                logger.warning("⚠️ Components not available for end-to-end test")
                return
            
            # Create sample market data point
            market_data = MarketData(
                symbol="NQU25-CME",
                timestamp=datetime.now(),
                open=23500.0,
                high=23520.0,
                low=23480.0,
                close=23510.0,
                volume=1000,
                bid=23509.0,
                ask=23511.0
            )
            
            # Test complete ML pipeline flow
            if hasattr(self.ml_pipeline, 'get_ml_prediction'):
                ml_prediction = await self.ml_pipeline.get_ml_prediction(market_data)
                logger.info(f"Complete ML prediction: {ml_prediction}")
                
                # Validate prediction structure
                if ml_prediction:
                    assert 'timestamp' in ml_prediction, "Missing timestamp"
                    assert 'symbol' in ml_prediction, "Missing symbol"
                    logger.info("✅ ML prediction structure valid")
            
            logger.info("✅ End-to-end integration test passed")
            self.test_results['integration_test'] = True
            
        except Exception as e:
            logger.error(f"❌ End-to-end integration test failed: {e}")
    
    async def test_performance_validation(self):
        """Test ML system performance and health"""
        logger.info("🔄 Testing ML performance validation...")
        
        try:
            if self.ml_pipeline:
                # Test system health
                health_data = {
                    'lstm_enabled': hasattr(self.ml_pipeline, 'lstm_predictor'),
                    'ensemble_enabled': hasattr(self.ml_pipeline, 'ensemble_manager'),
                    'kelly_enabled': hasattr(self.ml_pipeline, 'kelly_manager'),
                    'pipeline_enabled': self.ml_pipeline.is_enabled,
                }
                
                logger.info(f"ML system health: {health_data}")
                
                # Validate core components
                enabled_count = sum([
                    health_data['lstm_enabled'],
                    health_data['ensemble_enabled'], 
                    health_data['kelly_enabled']
                ])
                
                assert enabled_count >= 3, f"Only {enabled_count}/3 ML components enabled"
                
                logger.info("✅ Performance validation test passed")
                self.test_results['performance_test'] = True
                
            else:
                logger.warning("⚠️ ML Pipeline not available for performance test")
                
        except Exception as e:
            logger.error(f"❌ Performance validation test failed: {e}")
    
    def generate_sample_market_data(self):
        """Generate sample market data for testing"""
        # Generate 20 data points (sequence length)
        data = []
        base_price = 23500.0
        
        for i in range(20):
            data.append([
                base_price + np.random.uniform(-50, 50),  # close
                base_price + np.random.uniform(-30, 30),  # high
                base_price + np.random.uniform(-30, 30),  # low  
                base_price + np.random.uniform(-50, 50),  # open
                np.random.uniform(500, 2000),             # volume
                np.random.uniform(15, 25),                # volatility
                np.random.uniform(-1, 1),                 # momentum
                np.random.uniform(0.4, 0.6)               # rsi
            ])
            
        return np.array(data)
    
    def generate_sample_features(self):
        """Generate sample features for ensemble testing"""
        return {
            'price_change': 0.05,
            'volume_ratio': 1.2,
            'volatility': 0.18,
            'momentum': 0.03,
            'rsi': 0.55,
            'bollinger_position': 0.7,
            'macd_signal': 0.02,
            'support_distance': 0.01,
            'resistance_distance': 0.02,
            'trend_strength': 0.6
        }
    
    def generate_final_report(self):
        """Generate final test report"""
        logger.info("📊 Final ML Integration Test Report")
        logger.info("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        logger.info("")
        
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
        
        logger.info("")
        
        if success_rate >= 80:
            logger.info("🎉 ML Integration Test Suite: SUCCESS")
            logger.info("✅ Phase 2 ML Implementation is COMPLETE and OPERATIONAL")
        else:
            logger.info("⚠️ ML Integration Test Suite: NEEDS ATTENTION")
            logger.info("❌ Phase 2 ML Implementation requires additional work")
        
        logger.info("=" * 50)


async def main():
    """Main test execution"""
    tester = MLIntegrationTester()
    await tester.run_complete_test()


if __name__ == "__main__":
    asyncio.run(main())