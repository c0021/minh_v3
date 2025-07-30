#!/usr/bin/env python3
"""
Connect ML Models to Kelly Service
==================================

Direct integration script to connect trained LSTM and Ensemble models
to the Kelly Criterion service, bypassing complex initialization issues.

This addresses the core issue: Kelly service shows 'no_predictions' because
ML models aren't connected properly.
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, '/home/colindo/Sync/minh_v4')
sys.path.append(str(Path(__file__).parent / 'implementation' / 'ml_kelly_criterion_week5'))

def test_direct_ml_connection():
    """Test direct connection to ML models"""
    
    print("🔌 Testing Direct ML Model Connection")
    print("=" * 50)
    
    # Test 1: Load LSTM directly
    try:
        from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
        lstm = LSTMPredictor()
        print(f"✅ LSTM loaded: enabled={lstm.is_enabled}, trained={lstm.is_trained}")
        
        # Load the model
        if os.path.exists(lstm.model_path + '.h5'):
            try:
                lstm.load_model()
                print(f"✅ LSTM model loaded from {lstm.model_path}")
            except Exception as e:
                print(f"⚠️ LSTM model load warning: {e}")
                
        # Test prediction with sample data
        sample_data = {
            'timestamp': datetime.now().isoformat(),
            'price': 20000.0,
            'volume': 100,
            'high': 20010.0,
            'low': 19990.0,
            'open': 20005.0
        }
        
        # Add 20 data points for LSTM sequence requirement
        for i in range(20):
            prediction = lstm.predict(sample_data)
            if i == 19:  # Last prediction should work
                print(f"🧠 LSTM prediction: {prediction}")
                
    except Exception as e:
        print(f"❌ LSTM connection failed: {e}")
    
    # Test 2: Load Ensemble directly  
    try:
        from capabilities.ensemble.ensemble_manager import EnsembleManager
        ensemble = EnsembleManager()
        print(f"✅ Ensemble loaded: enabled={ensemble.is_enabled}")
        
        # Test prediction
        features = [20000.0, 100, 20010.0, 19990.0, 20005.0, 0.5, 0.3, 0.7]
        prediction = ensemble.predict(features)
        print(f"🎯 Ensemble prediction: {prediction}")
        
    except Exception as e:
        print(f"❌ Ensemble connection failed: {e}")
    
    # Test 3: Create simplified ML bridge
    try:
        print("\n🌉 Creating Direct ML Bridge")
        
        # Create a simplified bridge class
        class DirectMLBridge:
            def __init__(self):
                self.lstm = LSTMPredictor()
                self.ensemble = EnsembleManager() 
                self.data_buffer = []
                
            def get_ml_prediction(self, symbol, price_data=None):
                """Get unified ML prediction for Kelly service"""
                
                if not price_data:
                    price_data = {
                        'price': 20000.0,
                        'volume': 100,
                        'high': 20010.0,
                        'low': 19990.0,
                        'open': 20005.0
                    }
                
                predictions = {}
                
                # Get LSTM prediction
                try:
                    self.data_buffer.append(price_data)
                    if len(self.data_buffer) >= 20:
                        lstm_result = self.lstm.predict(price_data)
                        predictions['lstm'] = {
                            'direction': lstm_result.get('direction', 0),
                            'confidence': float(lstm_result.get('confidence', 0.0)),
                            'source': 'lstm_neural_network'
                        }
                except Exception as e:
                    predictions['lstm'] = {'error': str(e)}
                
                # Get Ensemble prediction
                try:
                    features = [
                        price_data['price'],
                        price_data['volume'], 
                        price_data['high'],
                        price_data['low'],
                        price_data['open'],
                        0.5, 0.3, 0.7  # placeholder technical indicators
                    ]
                    ensemble_result = self.ensemble.predict(features)
                    predictions['ensemble'] = {
                        'direction': ensemble_result.get('direction', 0),
                        'confidence': float(ensemble_result.get('confidence', 0.0)),
                        'source': 'ensemble_models'
                    }
                except Exception as e:
                    predictions['ensemble'] = {'error': str(e)}
                
                return predictions
        
        # Test the bridge
        bridge = DirectMLBridge()
        prediction = bridge.get_ml_prediction('NQU25-CME')
        print(f"🌉 ML Bridge prediction: {json.dumps(prediction, indent=2)}")
        
        # Now connect to Kelly service
        print("\n💰 Connecting to Kelly Service")
        
        from implementation.ml_kelly_criterion_week5.services.kelly_service import KellyService
        kelly = KellyService()
        
        # Monkey patch the ML connector to use our bridge
        if hasattr(kelly, 'ml_connector'):
            def mock_get_unified_ml_recommendation(symbol):
                bridge_result = bridge.get_ml_prediction(symbol)
                
                # Convert to expected format
                if 'lstm' in bridge_result and 'ensemble' in bridge_result:
                    return {
                        'status': 'active_predictions',
                        'models_used': ['lstm', 'ensemble'],
                        'lstm_prediction': bridge_result['lstm'],
                        'ensemble_prediction': bridge_result['ensemble'],
                        'unified_confidence': (
                            bridge_result['lstm'].get('confidence', 0) * 0.4 +
                            bridge_result['ensemble'].get('confidence', 0) * 0.6
                        ),
                        'model_agreement': abs(
                            bridge_result['lstm'].get('direction', 0) - 
                            bridge_result['ensemble'].get('direction', 0)
                        ) < 0.5
                    }
                else:
                    return {
                        'status': 'no_predictions',
                        'error': 'ML models not available'
                    }
            
            kelly.ml_connector.get_unified_ml_recommendation = mock_get_unified_ml_recommendation
            print("✅ Kelly service ML connector patched")
            
            # Test Kelly recommendation with live ML
            async def test_kelly_with_ml():
                await kelly.start()
                recommendation = await kelly.get_kelly_recommendation('NQU25-CME')
                print(f"💰 Kelly with ML: {json.dumps(recommendation, indent=2)}")
                await kelly.stop()
            
            asyncio.run(test_kelly_with_ml())
        
    except Exception as e:
        print(f"❌ ML Bridge creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_ml_connection()