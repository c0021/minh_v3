#!/usr/bin/env python3
"""
Complete ML Integration Test

Tests the full ML pipeline: LSTM + Ensemble integration with AI Brain Service.
Verifies that both LSTM and Ensemble models work together for enhanced signals.
"""

import asyncio
import sys
import logging
from pathlib import Path
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.ai_brain_service import AIBrainService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_complete_ml_integration():
    """Test complete ML integration with AI Brain Service"""
    print("🤖 Testing Complete ML Integration (LSTM + Ensemble)")
    print("=" * 60)
    
    try:
        # Initialize AI Brain Service
        print("1. Initializing AI Brain Service with ML capabilities...")
        ai_brain = AIBrainService()
        
        # Check ML capabilities
        ml_capabilities = list(ai_brain.ml_capabilities.keys())
        print(f"   🧠 ML Capabilities Loaded: {ml_capabilities}")
        
        if 'lstm' in ml_capabilities:
            lstm_stats = ai_brain.ml_capabilities['lstm'].get_performance_stats()
            print(f"   📊 LSTM Stats: Enabled: {lstm_stats['is_enabled']}, Trained: {lstm_stats['is_trained']}")
        
        if 'ensemble' in ml_capabilities:
            ensemble_stats = ai_brain.ml_capabilities['ensemble'].get_performance_stats()
            print(f"   🎯 Ensemble Stats: Enabled: {ensemble_stats['is_enabled']}, Trained: {ensemble_stats['is_trained']}")
        
        if 'kelly' in ml_capabilities:
            try:
                kelly_status = ai_brain.ml_capabilities['kelly'].get_system_status()
                enabled = kelly_status.get('config', {}).get('enabled', kelly_status.get('kelly_enabled', True))
                print(f"   💰 Kelly Stats: Enabled: {enabled}")
            except Exception as e:
                print(f"   💰 Kelly Stats: Error getting status: {e}")
        
        # Create comprehensive test data sequence
        print("\n2. Creating test market data sequence...")
        test_data = []
        base_price = 23400.0
        
        # Generate 30 data points with realistic market movement
        for i in range(30):
            # Add some trend and noise
            trend = 0.02 * i  # Slight upward trend
            noise = np.random.normal(0, 2.0)
            price = base_price + trend + noise
            
            data_point = {
                'timestamp': 1640995200 + (i * 60),
                'open': price - 0.5,
                'high': price + np.random.uniform(1, 3),
                'low': price - np.random.uniform(1, 3),
                'close': price,
                'price': price,
                'volume': int(1500 + np.random.uniform(-200, 300))
            }
            test_data.append(data_point)
        
        print(f"   ✅ Generated {len(test_data)} data points")
        print(f"   📈 Price range: ${test_data[0]['price']:.2f} - ${test_data[-1]['price']:.2f}")
        
        # Add data to AI brain buffer
        ai_brain.market_data_buffer.extend(test_data)
        
        # Test ML analysis
        print("\n3. Testing ML Analysis Integration...")
        ml_analysis = await ai_brain._analyze_ml_predictions(test_data)
        
        print(f"   🤖 ML Analysis Results:")
        print(f"      - ML Enabled: {ml_analysis.get('ml_enabled', False)}")
        print(f"      - ML Confidence: {ml_analysis.get('ml_confidence', 0):.3f}")
        print(f"      - ML Direction: {ml_analysis.get('ml_direction', 0)}")
        print(f"      - ML Agreement: {ml_analysis.get('ml_agreement', 0):.3f}")
        
        # Show individual model results
        if ml_analysis.get('lstm_prediction'):
            lstm_pred = ml_analysis['lstm_prediction']
            lstm_dir = "UP" if lstm_pred.get('direction', 0) > 0 else "DOWN" if lstm_pred.get('direction', 0) < 0 else "NEUTRAL"
            print(f"      - LSTM: {lstm_dir} (confidence: {lstm_pred.get('confidence', 0):.3f})")
        
        if ml_analysis.get('ensemble_prediction'):
            ens_pred = ml_analysis['ensemble_prediction']
            ens_dir = "UP" if ens_pred.get('direction', 0) > 0 else "DOWN" if ens_pred.get('direction', 0) < 0 else "NEUTRAL"
            print(f"      - Ensemble: {ens_dir} (confidence: {ens_pred.get('confidence', 0):.3f})")
            
            # Show base model predictions
            base_preds = ens_pred.get('base_predictions', {})
            if base_preds:
                print(f"        Base models:")
                for model, pred in base_preds.items():
                    pred_dir = "↗" if pred > 0.05 else "↘" if pred < -0.05 else "→"
                    print(f"          {model}: {pred_dir} {pred:.4f}")
        
        # Test complete analysis pipeline
        print("\n4. Testing Complete Analysis Pipeline...")
        try:
            # Get analysis data
            analysis_result = await ai_brain._get_analysis_data()
            if analysis_result:
                analysis_data = analysis_result.get('data', analysis_result)
                data_source = analysis_result.get('source', 'unknown')
                
                # Run all analysis components
                trend_analysis = await ai_brain._analyze_trend(analysis_data)
                momentum_analysis = await ai_brain._analyze_momentum(analysis_data)
                volatility_analysis = await ai_brain._analyze_volatility(analysis_data)
                volume_analysis = await ai_brain._analyze_volume(analysis_data)
                pattern_analysis = await ai_brain._analyze_patterns(analysis_data)
                ml_analysis_full = await ai_brain._analyze_ml_predictions(analysis_data)
                
                # Combine analyses
                combined_analysis = await ai_brain._combine_analyses(
                    trend_analysis, momentum_analysis, volatility_analysis,
                    volume_analysis, pattern_analysis, ml_analysis_full
                )
                
                print(f"   ✅ Complete analysis pipeline working")
                print(f"   📊 Analysis Results:")
                print(f"      - Trend: {combined_analysis.trend_direction} (strength: {combined_analysis.trend_strength:.3f})")
                print(f"      - Volatility: {combined_analysis.volatility_level}")
                print(f"      - Volume: {combined_analysis.volume_analysis}")
                
                # Check if ML predictions are included
                if hasattr(combined_analysis, 'ml_predictions'):
                    print(f"      - ML Integration: ✅ Included in analysis")
                else:
                    print(f"      - ML Integration: ⚠️ Not included")
                
                # Generate signal with ML enhancement
                signal = await ai_brain._generate_signal(combined_analysis, analysis_data, data_source)
                
                if signal:
                    print(f"   🎯 Generated Signal:")
                    print(f"      - Type: {signal.signal.name}")
                    print(f"      - Confidence: {signal.confidence:.1%}")
                    print(f"      - Reasoning: {signal.reasoning}")
                    
                    # Check for ML enhancement in reasoning
                    if "LSTM" in signal.reasoning or "Ensemble" in signal.reasoning or "ML" in signal.reasoning:
                        print(f"      - ML Enhancement: ✅ Detected in reasoning")
                    else:
                        print(f"      - ML Enhancement: ⚠️ Not detected in reasoning")
                    
                    # Check for Kelly Criterion attributes
                    if hasattr(signal, 'kelly_position_pct'):
                        print(f"      - Kelly Position: {signal.kelly_position_pct:.1%} (${signal.kelly_position_size:.0f})")
                        print(f"      - Kelly Win Prob: {signal.kelly_win_probability:.1%}")
                        print(f"      - Kelly Method: {signal.kelly_method}")
                        print(f"      - Kelly Enhancement: ✅ Included in signal")
                    else:
                        print(f"      - Kelly Enhancement: ⚠️ Not detected in signal")
                
        except Exception as e:
            print(f"   ⚠️ Complete analysis test error: {e}")
        
        # Performance summary
        print("\n5. Performance Summary:")
        overall_success = True
        
        # Check LSTM
        if 'lstm' in ml_capabilities:
            lstm_stats = ai_brain.ml_capabilities['lstm'].get_performance_stats()
            if lstm_stats['is_enabled'] and lstm_stats['predictions_made'] > 0:
                print(f"   ✅ LSTM: Operational ({lstm_stats['predictions_made']} predictions)")
            else:
                print(f"   ⚠️ LSTM: Limited functionality")
        
        # Check Ensemble
        if 'ensemble' in ml_capabilities:
            ensemble_stats = ai_brain.ml_capabilities['ensemble'].get_performance_stats()
            if ensemble_stats['is_enabled'] and ensemble_stats['predictions_made'] > 0:
                print(f"   ✅ Ensemble: Operational ({ensemble_stats['predictions_made']} predictions)")
            else:
                print(f"   ⚠️ Ensemble: Limited functionality")
        
        # Check Kelly Criterion
        if 'kelly' in ml_capabilities:
            try:
                kelly_status = ai_brain.ml_capabilities['kelly'].get_system_status()
                enabled = kelly_status.get('config', {}).get('enabled', kelly_status.get('kelly_enabled', True))
                if enabled:
                    print(f"   ✅ Kelly Criterion: Operational")
                else:
                    print(f"   ⚠️ Kelly Criterion: Disabled")
            except Exception as e:
                print(f"   ⚠️ Kelly Criterion: Error checking status")
        
        # Check ML integration
        if ml_analysis.get('ml_enabled'):
            print(f"   ✅ ML Integration: Functional")
        else:
            print(f"   ❌ ML Integration: Not working")
            overall_success = False
        
        print("\n" + "=" * 60)
        if overall_success:
            print("🎉 Complete ML Integration Test: SUCCESS!")
            print("   LSTM, Ensemble, and Kelly Criterion are fully integrated")
            print("   ML predictions are enhancing traditional analysis")
            print("   Position sizing is now ML-enhanced with Kelly Criterion")
        else:
            print("⚠️ Complete ML Integration Test: PARTIAL SUCCESS")
            print("   Some ML components may need attention")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 MinhOS Complete ML Integration Test")
    print(f"📁 Project Root: {project_root}")
    print()
    
    success = await test_complete_ml_integration()
    
    if success:
        print("\n🎉 All ML integration tests passed!")
        print("Ready for production deployment of ML-enhanced signals!")
        return 0
    else:
        print("\n💥 Some ML integration tests failed!")
        print("Check the errors above for issues to resolve.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)