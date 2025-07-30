#!/usr/bin/env python3
"""
Simple ML Components Test
========================

Tests individual ML components directly without full workflow.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys
import numpy as np

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Direct imports of ML capabilities
from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
from capabilities.ensemble.ensemble_manager import EnsembleManager
from capabilities.position_sizing.kelly.kelly_manager import KellyManager
from minhos.services.ml_performance_monitor import MLPerformanceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMLTester:
    """Simple tester for ML components"""
    
    def __init__(self):
        self.lstm = None
        self.ensemble = None
        self.kelly = None
        self.monitor = None
        
    def setup(self):
        """Initialize ML components"""
        logger.info("🚀 Initializing ML components...")
        
        # Initialize components
        self.lstm = LSTMPredictor()
        self.ensemble = EnsembleManager()
        self.kelly = KellyManager()
        self.monitor = MLPerformanceMonitor()
        
        logger.info("✅ ML components initialized")
        
    async def test_lstm(self):
        """Test LSTM prediction"""
        logger.info("\n" + "="*60)
        logger.info("🧠 Testing LSTM Neural Network")
        logger.info("="*60)
        
        try:
            # Create sample data (5 days of OHLCV)
            sample_data = {
                'timestamps': [datetime.now().timestamp() - i*86400 for i in range(5, 0, -1)],
                'open': [23500, 23520, 23480, 23550, 23540],
                'high': [23550, 23540, 23520, 23580, 23560],
                'low': [23480, 23490, 23460, 23530, 23520],
                'close': [23530, 23500, 23510, 23560, 23550],
                'volume': [10000, 11000, 9500, 12000, 10500]
            }
            
            # Get prediction
            result = self.lstm.predict("NQU25-CME", sample_data)
            
            if result:
                logger.info(f"✅ LSTM Prediction successful:")
                logger.info(f"   Next price prediction: ${result['prediction']:.2f}")
                logger.info(f"   Direction: {result['direction']}")
                logger.info(f"   Confidence: {result['confidence']:.2%}")
                logger.info(f"   Inference time: {result['inference_time_ms']:.1f}ms")
                logger.info(f"   Model version: {result.get('model_version', 'N/A')}")
                return True
            else:
                logger.error("❌ LSTM prediction failed")
                return False
                
        except Exception as e:
            logger.error(f"LSTM test error: {e}")
            return False
            
    async def test_ensemble(self):
        """Test Ensemble models"""
        logger.info("\n" + "="*60)
        logger.info("🎯 Testing Ensemble Methods")
        logger.info("="*60)
        
        try:
            # Create features for ensemble
            features = {
                'price': 23550,
                'volume': 10500,
                'rsi': 55.5,
                'macd': 0.5,
                'bb_position': 0.6,
                'volume_ratio': 1.1,
                'price_change': 0.002,
                'volatility': 0.015
            }
            
            # Get ensemble prediction
            result = self.ensemble.predict("NQU25-CME", features)
            
            if result:
                logger.info(f"✅ Ensemble Prediction successful:")
                logger.info(f"   Direction prediction: {result['direction']}")
                logger.info(f"   Confidence: {result['confidence']:.2%}")
                logger.info(f"   Models agreement: {result['models_agreement']:.2%}")
                logger.info(f"   Active models: {result['active_models']}")
                logger.info(f"   Inference time: {result['inference_time_ms']:.1f}ms")
                
                # Show individual model predictions
                if 'model_predictions' in result:
                    logger.info("\n   Individual model predictions:")
                    for model, pred in result['model_predictions'].items():
                        logger.info(f"     {model}: {pred}")
                        
                return True
            else:
                logger.error("❌ Ensemble prediction failed")
                return False
                
        except Exception as e:
            logger.error(f"Ensemble test error: {e}")
            return False
            
    async def test_kelly(self):
        """Test Kelly Criterion"""
        logger.info("\n" + "="*60)
        logger.info("💰 Testing Kelly Criterion Calculator")
        logger.info("="*60)
        
        try:
            # Test Kelly calculation
            kelly_result = self.kelly.calculate_position_size(
                symbol="NQU25-CME",
                signal_confidence=0.75,
                stop_loss_price=23400,
                take_profit_price=23700,
                current_price=23550,
                capital=100000
            )
            
            if kelly_result:
                logger.info(f"✅ Kelly Calculation successful:")
                logger.info(f"   Recommended contracts: {kelly_result['contracts']}")
                logger.info(f"   Kelly fraction: {kelly_result['kelly_fraction']:.4f}")
                logger.info(f"   Win probability: {kelly_result['win_probability']:.2%}")
                logger.info(f"   Loss probability: {kelly_result['loss_probability']:.2%}")
                logger.info(f"   Risk per contract: ${kelly_result['risk_per_contract']:,.2f}")
                logger.info(f"   Total risk: ${kelly_result['total_risk']:,.2f}")
                logger.info(f"   Expected value: ${kelly_result['expected_value']:,.2f}")
                return True
            else:
                logger.error("❌ Kelly calculation failed")
                return False
                
        except Exception as e:
            logger.error(f"Kelly test error: {e}")
            return False
            
    async def test_ml_health(self):
        """Test ML health monitoring"""
        logger.info("\n" + "="*60)
        logger.info("📊 Testing ML Health Monitoring")
        logger.info("="*60)
        
        try:
            # Get health status
            health = self.monitor.get_health_status()
            
            logger.info(f"✅ ML Health Check:")
            logger.info(f"   Overall health score: {health['health_score']}/100")
            logger.info(f"   Status: {health['status']}")
            logger.info(f"   Timestamp: {health['timestamp']}")
            
            # Check components
            logger.info("\n   Component Status:")
            for component, status in health['components'].items():
                logger.info(f"     {component}: {status}")
                
            # Get performance summary
            perf = self.monitor.get_performance_summary()
            if perf:
                logger.info("\n   Performance Metrics:")
                for model in ['lstm', 'ensemble', 'kelly']:
                    if model in perf and perf[model]:
                        logger.info(f"\n     {model.upper()}:")
                        for metric, value in perf[model].items():
                            if isinstance(value, (int, float)):
                                logger.info(f"       {metric}: {value:.4f}")
                            else:
                                logger.info(f"       {metric}: {value}")
                                
            return health['health_score'] > 0
            
        except Exception as e:
            logger.error(f"Health monitoring test error: {e}")
            return False
            
    async def run_tests(self):
        """Run all component tests"""
        try:
            self.setup()
            
            # Run individual tests
            results = {
                'lstm': await self.test_lstm(),
                'ensemble': await self.test_ensemble(),
                'kelly': await self.test_kelly(),
                'ml_health': await self.test_ml_health()
            }
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("📊 ML Components Test Summary")
            logger.info("="*60)
            
            passed = sum(1 for v in results.values() if v)
            total = len(results)
            
            for test, result in results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"{test}: {status}")
                
            logger.info(f"\nOverall: {passed}/{total} tests passed")
            
            if passed == total:
                logger.info("\n🎉 All ML Components are OPERATIONAL!")
                logger.info("✅ Phase 3 Production Deployment - ML Pipeline Validated")
            else:
                logger.warning(f"\n⚠️ {total - passed} components need attention")
                
            return passed == total
            
        except Exception as e:
            logger.error(f"Test execution error: {e}", exc_info=True)
            return False

async def main():
    """Main entry point"""
    tester = SimpleMLTester()
    success = await tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))