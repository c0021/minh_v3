#!/usr/bin/env python3
"""
Fix ML Kelly Integration
=======================

This script properly connects the existing trained ML models to the Kelly service
by using the correct API methods and data formats.

Goal: Change Kelly service status from 'no_predictions' to 'active_predictions'
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

async def fix_ml_kelly_integration():
    """Fix the ML to Kelly integration"""
    
    print("🔧 Fixing ML Kelly Integration")
    print("=" * 50)
    
    # Initialize ML models with correct APIs
    from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
    from capabilities.ensemble.ensemble_manager import EnsembleManager
    
    lstm = LSTMPredictor()
    ensemble = EnsembleManager()
    
    print(f"✅ LSTM initialized: enabled={lstm.is_enabled}, trained={lstm.is_trained}")
    print(f"✅ Ensemble initialized: enabled={ensemble.is_enabled}")
    
    # Create sample market data in the correct format
    market_data = {
        'timestamp': datetime.now().isoformat(),
        'symbol': 'NQU25-CME',
        'last_price': 20000.0,
        'volume': 100,
        'high': 20010.0,
        'low': 19990.0,
        'open': 20005.0,
        'bid': 19999.0,
        'ask': 20001.0
    }
    
    print("📊 Sample market data created")
    
    # Test LSTM prediction
    print("\n🧠 Testing LSTM Prediction")
    try:
        # Feed data to LSTM buffer first (it needs 20 data points)
        for i in range(25):
            lstm_prediction = await lstm.predict_direction(market_data)
            if i >= 20:  # After buffer is full
                print(f"   Attempt {i}: {lstm_prediction}")
                if lstm_prediction.get('source') == 'lstm_neural_network':
                    print("✅ LSTM generating neural network predictions!")
                    break
    except Exception as e:
        print(f"❌ LSTM prediction failed: {e}")
    
    # Test Ensemble prediction
    print("\n🎯 Testing Ensemble Prediction")  
    try:
        # Ensemble needs list of market data
        market_data_list = [market_data] * 10  # Provide some history
        ensemble_prediction = await ensemble.predict_ensemble(market_data_list)
        print(f"   Ensemble result: {ensemble_prediction}")
    except Exception as e:
        print(f"❌ Ensemble prediction failed: {e}")
    
    # Now fix the Kelly service ML connector
    print("\n🔧 Fixing Kelly Service ML Connector")
    
    try:
        from implementation.ml_kelly_criterion_week5.services.kelly_service import KellyService
        from implementation.ml_kelly_criterion_week5.services.ml_service_connector import MLServiceConnector
        
        # Create a working ML connector
        class WorkingMLConnector(MLServiceConnector):
            def __init__(self):
                super().__init__()
                self.lstm = LSTMPredictor()
                self.ensemble = EnsembleManager()
                self.data_history = []
                
            async def get_unified_ml_recommendation(self, symbol, market_data=None):
                """Get unified ML recommendation that actually works"""
                
                if not market_data:
                    market_data = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'last_price': 20000.0,
                        'volume': 100,
                        'high': 20010.0,
                        'low': 19990.0,
                        'open': 20005.0,
                        'bid': 19999.0,
                        'ask': 20001.0
                    }
                
                self.data_history.append(market_data)
                if len(self.data_history) > 50:
                    self.data_history = self.data_history[-50:]  # Keep last 50
                
                predictions = {}
                models_used = []
                
                # Get LSTM prediction
                try:
                    lstm_result = await self.lstm.predict_direction(market_data)
                    if lstm_result.get('source') == 'lstm_neural_network':
                        predictions['lstm'] = lstm_result
                        models_used.append('lstm')
                    else:
                        predictions['lstm'] = {'confidence': 0.0, 'direction': 0, 'source': 'lstm_insufficient_data'}
                except Exception as e:
                    predictions['lstm'] = {'error': str(e), 'confidence': 0.0, 'direction': 0}
                
                # Get Ensemble prediction
                try:
                    if len(self.data_history) >= 5:
                        ensemble_result = await self.ensemble.predict_ensemble(self.data_history[-10:])
                        predictions['ensemble'] = ensemble_result
                        models_used.append('ensemble')
                    else:
                        predictions['ensemble'] = {'confidence': 0.0, 'direction': 0, 'source': 'ensemble_insufficient_data'}
                except Exception as e:
                    predictions['ensemble'] = {'error': str(e), 'confidence': 0.0, 'direction': 0}
                
                # Calculate unified prediction
                lstm_conf = predictions.get('lstm', {}).get('confidence', 0.0)
                ensemble_conf = predictions.get('ensemble', {}).get('confidence', 0.0)
                
                if isinstance(lstm_conf, str):
                    lstm_conf = 0.0
                if isinstance(ensemble_conf, str):
                    ensemble_conf = 0.0
                    
                # Weighted average (LSTM 40%, Ensemble 60%)
                unified_confidence = float(lstm_conf) * 0.4 + float(ensemble_conf) * 0.6
                
                # Determine status
                if models_used:
                    status = 'active_predictions'
                else:
                    status = 'no_predictions'
                
                result = {
                    'status': status,
                    'symbol': symbol,
                    'models_used': models_used,
                    'lstm_prediction': predictions['lstm'],
                    'ensemble_prediction': predictions['ensemble'],
                    'unified_confidence': unified_confidence,
                    'model_agreement': len(models_used) >= 2,
                    'timestamp': datetime.now().isoformat()
                }
                
                return result
        
        # Create Kelly service with working connector
        kelly = KellyService()
        kelly.ml_connector = WorkingMLConnector()
        
        print("✅ Kelly service ML connector replaced with working version")
        
        # Test the integration
        print("\n💰 Testing Fixed Kelly Integration")
        
        await kelly.start()
        print("✅ Kelly service started")
        
        # Get recommendation with market data
        recommendation = await kelly.get_kelly_recommendation('NQU25-CME', market_data)
        print(f"📊 Kelly recommendation: {json.dumps(recommendation, indent=2)}")
        
        # Check if status changed from no_predictions
        if recommendation.get('status') != 'no_predictions':
            print("🎉 SUCCESS: Kelly service now has active predictions!")
        else:
            print("⚠️ Still showing no_predictions - need more data or model training")
        
        await kelly.stop()
        print("✅ Kelly service stopped")
        
    except Exception as e:
        print(f"❌ Kelly integration fix failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_ml_kelly_integration())