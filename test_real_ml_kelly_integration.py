#!/usr/bin/env python3
"""
Test Real ML Kelly Integration
=============================

Tests the complete integration with REAL trained models and proper method calls.
This should finally get predictions from the trained models.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, '/home/colindo/Sync/minh_v4')
sys.path.append(str(Path(__file__).parent / 'implementation' / 'ml_kelly_criterion_week5'))

async def test_real_ml_kelly_integration():
    """Test the real ML Kelly integration with proper method calls"""
    
    print("🔧 Testing Real ML Kelly Integration")
    print("=" * 50)
    
    # Test 1: Direct LSTM prediction
    try:
        from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
        lstm = LSTMPredictor()
        print(f"✅ LSTM: enabled={lstm.is_enabled}, trained={lstm.is_trained}")
        
        if lstm.is_trained:
            # Test with real market data
            market_data = {
                'timestamp': '2025-07-28T13:30:00',
                'symbol': 'NQU25-CME',
                'last_price': 20000.0,
                'volume': 100,
                'high': 20010.0,
                'low': 19990.0,
                'open': 20005.0,
                'bid': 19999.0,
                'ask': 20001.0
            }
            
            # Feed data to LSTM buffer (needs sequence)
            for i in range(25):
                prediction = await lstm.predict_direction(market_data)
                if i >= 20:  # After buffer is full
                    print(f"🧠 LSTM Step {i}: {prediction}")
                    if prediction.get('source') == 'lstm_neural_network':
                        print("🎉 SUCCESS: LSTM generating neural network predictions!")
                        break
        
    except Exception as e:
        print(f"❌ LSTM test failed: {e}")
    
    # Test 2: Direct Ensemble prediction  
    try:
        from capabilities.ensemble.ensemble_manager import EnsembleManager
        ensemble = EnsembleManager()
        print(f"✅ Ensemble: enabled={ensemble.is_enabled}, trained={ensemble.is_trained}")
        
        if ensemble.is_trained:
            # Test with market data list
            market_data_list = [market_data] * 10
            prediction = await ensemble.predict_ensemble(market_data_list)
            print(f"🎯 Ensemble prediction: {prediction}")
            if prediction.get('source') == 'ensemble_ml_models':
                print("🎉 SUCCESS: Ensemble generating ML predictions!")
        
    except Exception as e:
        print(f"❌ Ensemble test failed: {e}")
    
    # Test 3: ML Service Connector with fixed methods
    try:
        from implementation.ml_kelly_criterion_week5.services.ml_service_connector import MLServiceConnector
        
        connector = MLServiceConnector()
        await connector.initialize_services()
        print("✅ ML Service Connector initialized")
        
        # Test LSTM prediction through connector
        lstm_result = await connector.get_lstm_prediction('NQU25-CME', market_data)
        print(f"🧠 Connector LSTM: {lstm_result}")
        
        # Test Ensemble prediction through connector  
        ensemble_result = await connector.get_ensemble_prediction('NQU25-CME', market_data)
        print(f"🎯 Connector Ensemble: {ensemble_result}")
        
        # Test unified prediction
        unified_result = await connector.get_unified_ml_recommendation(
            'NQU25-CME', market_data, [], 100000.0
        )
        print(f"🌉 Unified ML: {unified_result}")
        
        if unified_result.get('status') != 'no_predictions':
            print("🎉 SUCCESS: ML Service Connector generating predictions!")
        
    except Exception as e:
        print(f"❌ ML Service Connector test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Full Kelly integration
    try:
        from implementation.ml_kelly_criterion_week5.services.kelly_service import KellyService
        
        kelly = KellyService()
        await kelly.start()
        print("✅ Kelly Service started")
        
        # Get recommendation with market data
        recommendation = await kelly.get_kelly_recommendation('NQU25-CME', market_data)
        print(f"💰 Kelly recommendation: {recommendation}")
        
        if hasattr(recommendation, 'status'):
            status = recommendation.status
        else:
            status = recommendation.get('status')
            
        if status != 'no_predictions':
            print("🎉 FINAL SUCCESS: Kelly service generating ML-powered recommendations!")
        else:
            print("⚠️ Still no predictions - need to debug further")
        
        await kelly.stop()
        
    except Exception as e:
        print(f"❌ Kelly service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_ml_kelly_integration())