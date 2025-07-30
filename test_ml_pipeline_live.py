#!/usr/bin/env python3
"""
Test ML Pipeline with Live Market Data
=====================================

This script validates the complete ML pipeline with live market data:
1. LSTM predictions
2. Ensemble predictions
3. Kelly Criterion position sizing
4. End-to-end trading workflow
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

from minhos.services.ai_brain_service import get_ai_brain_service
from minhos.services.ml_trading_workflow import MLTradingWorkflow
from minhos.services.trading_engine import get_trading_engine
from minhos.services.risk_manager import get_risk_manager
from minhos.services.state_manager import get_state_manager
from minhos.services.sierra_client import get_sierra_client
from minhos.services.ml_performance_monitor import MLPerformanceMonitor
from minhos.core.market_data_adapter import get_market_data_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLPipelineLiveValidator:
    """Validates ML pipeline with live market data"""
    
    def __init__(self):
        self.workflow = None
        self.monitor = None
        self.ai_brain = None
        self.trading_engine = None
        self.risk_manager = None
        self.state_manager = None
        self.sierra_client = None
        self.market_data_adapter = None
        
    async def setup(self):
        """Initialize all services"""
        logger.info("🚀 Initializing services for ML pipeline validation...")
        
        # Initialize core services
        self.market_data_adapter = get_market_data_adapter()
        self.state_manager = get_state_manager()
        self.risk_manager = get_risk_manager()
        self.sierra_client = get_sierra_client()
        self.ai_brain = get_ai_brain_service()
        self.trading_engine = get_trading_engine()
        
        # Initialize ML components
        self.workflow = MLTradingWorkflow()
        self.monitor = MLPerformanceMonitor()
        
        # Start services
        await self.state_manager.start()
        await self.risk_manager.start()
        await self.sierra_client.start()
        await self.ai_brain.start()
        await self.trading_engine.start()
        
        logger.info("✅ All services initialized")
        
    async def get_live_market_data(self):
        """Get current live market data"""
        try:
            # Get from market data adapter
            market_data = self.market_data_adapter.get_market_data("NQU25-CME")
            
            if not market_data:
                logger.warning("No live market data available, fetching from Sierra...")
                # Fallback to direct fetch
                market_data = await self.sierra_client.get_market_data("NQU25-CME")
                
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
            
    async def test_ml_predictions(self):
        """Test ML predictions with live data"""
        logger.info("\n" + "="*60)
        logger.info("🧠 Testing ML Predictions with Live Data")
        logger.info("="*60)
        
        # Get live market data
        market_data = await self.get_live_market_data()
        if not market_data:
            logger.error("❌ No market data available")
            return False
            
        logger.info(f"📊 Live Market Data: {market_data.symbol} @ ${market_data.price:.2f}")
        
        # Test through manual decision to get individual ML predictions
        logger.info("\n📊 Running ML predictions through workflow...")
        
        # Execute a manual decision which will run all ML components
        decision = await self.workflow.execute_manual_decision()
        
        if decision:
            logger.info("✅ ML Predictions successful:")
            logger.info(f"   Symbol: {decision.symbol}")
            logger.info(f"   Signal: {decision.signal.value}")
            logger.info(f"   Confidence: {decision.confidence:.2%}")
            logger.info(f"   Recommended size: {decision.recommended_size} contracts")
            
            # Show LSTM details if available
            if decision.lstm_prediction:
                logger.info("\n📈 LSTM Prediction:")
                logger.info(f"   Prediction: {decision.lstm_prediction.get('prediction', 'N/A')}")
                logger.info(f"   Direction: {decision.lstm_prediction.get('direction', 'N/A')}")
                logger.info(f"   Confidence: {decision.lstm_prediction.get('confidence', 0):.2%}")
                
            # Show Ensemble details if available
            if decision.ensemble_prediction:
                logger.info("\n🎯 Ensemble Prediction:")
                logger.info(f"   Prediction: {decision.ensemble_prediction.get('prediction', 'N/A')}")
                logger.info(f"   Direction: {decision.ensemble_prediction.get('direction', 'N/A')}")
                logger.info(f"   Agreement: {decision.ensemble_prediction.get('models_agreement', 0):.2%}")
                
            # Show timing
            logger.info(f"\n⏱️ Total inference time: {decision.total_latency_ms:.1f}ms")
            
            return True
        else:
            logger.error("❌ ML prediction workflow failed")
            return False
        
    async def test_kelly_sizing(self):
        """Test Kelly Criterion position sizing"""
        logger.info("\n" + "="*60)
        logger.info("💰 Testing Kelly Criterion Position Sizing")
        logger.info("="*60)
        
        # Get current market data
        market_data = await self.get_live_market_data()
        if not market_data:
            logger.error("❌ No market data available")
            return False
            
        # Generate a test trading signal
        signal = {
            'symbol': market_data.symbol,
            'direction': 'LONG',
            'confidence': 0.75,
            'stop_loss_pct': 0.02,  # 2% stop loss
            'take_profit_pct': 0.04  # 4% take profit
        }
        
        logger.info(f"📊 Test Signal: {signal['direction']} {signal['symbol']} @ {signal['confidence']:.2%} confidence")
        
        # Test Kelly through position sizing service
        from minhos.services.position_sizing_service import get_position_sizing_service
        position_service = get_position_sizing_service()
        
        kelly_result = await position_service.calculate_ml_position_size(
            symbol=signal['symbol'],
            signal_direction=signal['direction'],
            confidence=signal['confidence'],
            current_price=market_data.price,
            stop_loss_price=market_data.price * (1 - signal['stop_loss_pct']),
            capital=100000  # $100k capital
        )
        
        if kelly_result and kelly_result.get('position_size', 0) > 0:
            logger.info(f"✅ Kelly Position Size: {kelly_result['position_size']} contracts")
            logger.info(f"   Kelly fraction: {kelly_result['kelly_fraction']:.4f}")
            logger.info(f"   Win probability: {kelly_result['win_probability']:.2%}")
            logger.info(f"   Risk amount: ${kelly_result['risk_amount']:,.2f}")
            logger.info(f"   Expected value: ${kelly_result.get('expected_value', 0):,.2f}")
            return True
        else:
            logger.error("❌ Kelly calculation failed or returned zero position")
            return False
            
    async def test_trading_workflow(self):
        """Test complete trading workflow"""
        logger.info("\n" + "="*60)
        logger.info("🔄 Testing End-to-End Trading Workflow")
        logger.info("="*60)
        
        # Get market data
        market_data = await self.get_live_market_data()
        if not market_data:
            logger.error("❌ No market data available")
            return False
            
        # Execute complete workflow through manual decision
        logger.info("📊 Executing ML trading workflow...")
        decision = await self.workflow.execute_manual_decision()
        
        if decision:
            logger.info(f"✅ Trading Decision Generated:")
            logger.info(f"   Signal: {decision.signal.value}")
            logger.info(f"   Symbol: {decision.symbol}")
            logger.info(f"   Confidence: {decision.confidence:.2%}")
            logger.info(f"   Position size: {decision.recommended_size} contracts")
            if decision.kelly_position:
                logger.info(f"   Kelly fraction: {decision.kelly_position.kelly_fraction:.4f}")
                logger.info(f"   Risk amount: ${decision.kelly_position.risk_amount:,.2f}")
            logger.info(f"   Total inference time: {decision.total_latency_ms:.1f}ms")
            
            # Check if trade would be executed
            if decision.confidence >= 0.65:
                logger.info("   ✅ Confidence threshold met - trade would execute")
            else:
                logger.info("   ⚠️ Confidence below threshold - no trade")
                
            return True
        else:
            logger.error("❌ Trading workflow failed")
            return False
            
    async def test_performance_monitoring(self):
        """Test ML performance monitoring"""
        logger.info("\n" + "="*60)
        logger.info("📊 Testing ML Performance Monitoring")
        logger.info("="*60)
        
        # Get current health status
        health = self.monitor.get_health_status()
        logger.info(f"✅ ML Health Score: {health['health_score']}/100")
        logger.info(f"   Status: {health['status']}")
        
        # Check individual components
        for component, status in health['components'].items():
            logger.info(f"   {component}: {status}")
            
        # Get performance metrics
        metrics = self.monitor.get_performance_summary()
        logger.info("\n📈 Performance Metrics:")
        for model, model_metrics in metrics.items():
            if model_metrics:
                logger.info(f"\n   {model.upper()}:")
                for metric, value in model_metrics.items():
                    if isinstance(value, float):
                        logger.info(f"     {metric}: {value:.4f}")
                    else:
                        logger.info(f"     {metric}: {value}")
                        
        return health['health_score'] > 0
        
    async def run_validation(self):
        """Run complete ML pipeline validation"""
        try:
            await self.setup()
            
            # Wait for some market data
            logger.info("\n⏳ Waiting for market data to populate...")
            await asyncio.sleep(5)
            
            # Run tests
            results = {
                'ml_predictions': await self.test_ml_predictions(),
                'kelly_sizing': await self.test_kelly_sizing(),
                'trading_workflow': await self.test_trading_workflow(),
                'performance_monitoring': await self.test_performance_monitoring()
            }
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("📊 ML Pipeline Validation Summary")
            logger.info("="*60)
            
            passed = sum(1 for v in results.values() if v)
            total = len(results)
            
            for test, result in results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"{test}: {status}")
                
            logger.info(f"\nOverall: {passed}/{total} tests passed")
            
            if passed == total:
                logger.info("\n🎉 ML Pipeline is FULLY OPERATIONAL!")
            else:
                logger.warning("\n⚠️ Some components need attention")
                
            return passed == total
            
        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return False
        finally:
            # Cleanup
            if self.sierra_client:
                await self.sierra_client.stop()
            if self.ai_brain:
                await self.ai_brain.stop()
            if self.trading_engine:
                await self.trading_engine.stop()
            if self.risk_manager:
                await self.risk_manager.stop()
            if self.state_manager:
                await self.state_manager.stop()

async def main():
    """Main entry point"""
    validator = MLPipelineLiveValidator()
    success = await validator.run_validation()
    
    # Update todo list
    if success:
        logger.info("\n✅ ML pipeline validation with live market data COMPLETE")
    else:
        logger.error("\n❌ ML pipeline validation failed")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))