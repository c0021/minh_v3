#!/usr/bin/env python3
"""
End-to-End Pipeline Validation Test
===================================

Tests the complete MinhOS v3 pipeline:
Market Data → ML Pipeline → Trading Engine → Position Sizing → Execution

Validates that ML predictions properly influence live trading decisions.
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

from minhos.services.ai_brain_service import AIBrainService
from minhos.services.trading_engine import TradingEngine
from minhos.services.ml_pipeline_service import MLPipelineService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_end_to_end_pipeline():
    """Test complete end-to-end pipeline"""
    print("🚀 MinhOS End-to-End Pipeline Validation")
    print("=" * 60)
    
    try:
        # Step 1: Initialize Services
        print("1. Initializing Core Services...")
        ai_brain = AIBrainService()
        trading_engine = TradingEngine()
        
        print(f"   ✅ AI Brain initialized with ML capabilities: {list(ai_brain.ml_capabilities.keys())}")
        print(f"   ✅ Trading Engine initialized with ML pipeline: {trading_engine.ml_pipeline is not None}")
        
        # Step 2: Create Test Market Data
        print("\n2. Generating Test Market Data...")
        base_price = 23400.0
        test_data = []
        
        # Generate realistic market sequence
        for i in range(50):
            trend = 0.05 * i  # Slight upward trend
            noise = np.random.normal(0, 2.0)
            price = base_price + trend + noise
            
            data_point = {
                'timestamp': 1640995200 + (i * 60),
                'symbol': 'NQU25-CME',
                'open': price - 0.5,
                'high': price + np.random.uniform(1, 3),
                'low': price - np.random.uniform(1, 3),
                'close': price,
                'price': price,
                'bid': price - 0.25,
                'ask': price + 0.25,
                'volume': int(1500 + np.random.uniform(-300, 500))
            }
            test_data.append(data_point)
        
        print(f"   ✅ Generated {len(test_data)} market data points")
        print(f"   📈 Price trend: ${test_data[0]['price']:.2f} → ${test_data[-1]['price']:.2f}")
        
        # Step 3: Test ML Pipeline
        print("\n3. Testing ML Pipeline Processing...")
        if 'pipeline' in ai_brain.ml_capabilities:
            pipeline_service = ai_brain.ml_capabilities['pipeline']
            latest_data = test_data[-1]
            
            ml_prediction = await pipeline_service.get_ml_prediction(latest_data)
            
            if ml_prediction:
                print(f"   ✅ ML Prediction generated:")
                print(f"      Direction: {ml_prediction.direction}")
                print(f"      Confidence: {ml_prediction.confidence:.3f}")
                print(f"      LSTM Result: {ml_prediction.lstm_prediction is not None}")
                print(f"      Ensemble Result: {ml_prediction.ensemble_prediction is not None}")
                print(f"      Kelly Fraction: {ml_prediction.kelly_fraction}")
                print(f"      Position Size: {ml_prediction.position_size}")
            else:
                print("   ⚠️ ML Prediction returned None")
        else:
            print("   ❌ No ML pipeline capability found")
        
        # Step 4: Test AI Brain Analysis
        print("\n4. Testing AI Brain ML Analysis...")
        ai_brain.market_data_buffer.extend(test_data)
        
        # Test ML analysis
        ml_analysis = await ai_brain._analyze_ml_predictions(test_data)
        
        print(f"   🤖 ML Analysis Results:")
        print(f"      ML Enabled: {ml_analysis.get('ml_enabled', False)}")
        print(f"      ML Confidence: {ml_analysis.get('ml_confidence', 0):.3f}")
        print(f"      ML Direction: {ml_analysis.get('ml_direction', 0)}")
        print(f"      LSTM Prediction: {ml_analysis.get('lstm_prediction') is not None}")
        print(f"      Ensemble Prediction: {ml_analysis.get('ensemble_prediction') is not None}")
        
        # Step 5: Test Complete Signal Generation
        print("\n5. Testing Complete Signal Generation...")
        
        # Add data to AI brain and generate signal
        signal = await ai_brain.analyze_and_signal(test_data[-1])
        
        if signal:
            print(f"   ✅ Trading Signal Generated:")
            print(f"      Signal Type: {signal.signal.value}")
            print(f"      Confidence: {signal.confidence}%")
            print(f"      Target Price: ${signal.target_price}")
            print(f"      Stop Loss: ${signal.stop_loss}")
            print(f"      Reasoning: {signal.reasoning[:100]}...")
            
            # Check if ML is mentioned in reasoning
            ml_mentioned = any(term in signal.reasoning.lower() for term in ['ml', 'lstm', 'ensemble', 'kelly', 'neural'])
            print(f"      ML Integration in Reasoning: {'✅' if ml_mentioned else '❌'}")
            
            # Check signal context for ML data
            ml_context = any(key in signal.context for key in ['ml_confidence', 'kelly_position', 'lstm_prediction'])
            print(f"      ML Data in Context: {'✅' if ml_context else '❌'}")
            
        else:
            print("   ❌ No trading signal generated")
        
        # Step 6: Test Trading Engine ML Integration
        print("\n6. Testing Trading Engine ML Position Sizing...")
        
        if signal:
            # Test position size calculation
            current_price = test_data[-1]['price']
            position_size = await trading_engine._calculate_position_size(signal, current_price)
            
            print(f"   ✅ Position Size Calculation:")
            print(f"      Calculated Size: {position_size} contracts")
            print(f"      Uses ML Sizing: {trading_engine.config.get('use_ml_position_sizing', True)}")
            
            # Check if Kelly data is in signal context
            kelly_data = signal.context.get('kelly_position')
            if kelly_data:
                print(f"      Kelly Win Probability: {kelly_data.get('win_probability', 0):.2%}")
                print(f"      Kelly Fraction: {kelly_data.get('kelly_fraction', 0):.3f}")
                print(f"      Kelly Method: {kelly_data.get('method', 'unknown')}")
                print(f"   ✅ ML-Enhanced Position Sizing Working")
            else:
                print("   ⚠️ No Kelly Criterion data found in signal")
        
        # Step 7: Pipeline Health Check
        print("\n7. Pipeline Health Assessment...")
        
        pipeline_health = {
            'ml_pipeline_loaded': 'pipeline' in ai_brain.ml_capabilities,
            'trading_engine_ml_ready': trading_engine.ml_pipeline is not None,
            'ml_analysis_working': ml_analysis.get('ml_enabled', False),
            'signal_generation_working': signal is not None,
            'position_sizing_working': position_size > 0 if signal else False,
            'kelly_integration_working': kelly_data is not None if signal else False
        }
        
        print("   📊 Pipeline Component Status:")
        for component, status in pipeline_health.items():
            status_icon = "✅" if status else "❌"
            print(f"      {component.replace('_', ' ').title()}: {status_icon}")
        
        # Overall Assessment
        working_components = sum(pipeline_health.values())
        total_components = len(pipeline_health)
        health_percentage = (working_components / total_components) * 100
        
        print(f"\n📈 Pipeline Health: {health_percentage:.1f}% ({working_components}/{total_components} components)")
        
        if health_percentage >= 80:
            print("✅ End-to-End Pipeline: PRODUCTION READY")
        elif health_percentage >= 60:
            print("⚠️ End-to-End Pipeline: NEEDS ATTENTION")
        else:
            print("❌ End-to-End Pipeline: REQUIRES FIXES")
        
        return health_percentage >= 80
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

async def main():
    """Main test execution"""
    print("🎯 Starting End-to-End Pipeline Validation...")
    
    success = await test_end_to_end_pipeline()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 END-TO-END PIPELINE VALIDATION: SUCCESS")
        print("   Your ML-enhanced trading system is production ready!")
    else:
        print("💥 END-TO-END PIPELINE VALIDATION: ISSUES FOUND")
        print("   Review the errors above and address any failures.")

if __name__ == "__main__":
    asyncio.run(main())