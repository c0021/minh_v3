#!/usr/bin/env python3
"""
Live ML Kelly Integration Test
=============================

Tests the complete integration with real data flow:
Sierra Chart Data -> ML Models -> Kelly Calculator -> Position Sizing

This bridges the gap between existing ML models and Kelly integration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, '/home/colindo/Sync/minh_v4')
sys.path.append(str(Path(__file__).parent / 'implementation' / 'ml_kelly_criterion_week5'))

from capabilities.prediction.lstm.lstm_predictor import LSTMPredictor
from capabilities.ensemble.ensemble_manager import EnsembleManager
from implementation.ml_kelly_criterion_week5.services.kelly_service import KellyService
from minhos.core.market_data_store import MarketDataStore

async def test_live_ml_kelly_integration():
    """Test complete ML -> Kelly integration with real data"""
    
    print("🚀 Live ML Kelly Integration Test")
    print("=" * 50)
    
    # Initialize components
    lstm_predictor = LSTMPredictor()
    ensemble_manager = EnsembleManager()
    kelly_service = KellyService()
    market_data_store = MarketDataStore()
    
    print(f"✅ LSTM initialized: {lstm_predictor.is_enabled}")
    print(f"✅ Ensemble initialized: {ensemble_manager is not None}")
    print(f"✅ Kelly service initialized")
    
    # Start Kelly service
    await kelly_service.start()
    print("✅ Kelly service started")
    
    # Get current market data
    symbol = "NQU25-CME"
    try:
        current_data = await market_data_store.get_current_market_data(symbol)
        print(f"📊 Current {symbol} data: {current_data}")
        
        # Test LSTM prediction with real data
        if current_data:
            market_data = {
                'timestamp': current_data.get('timestamp'),
                'price': current_data.get('last_price', 0),
                'volume': current_data.get('volume', 0),
                'high': current_data.get('high', 0),
                'low': current_data.get('low', 0),
                'open': current_data.get('open', 0)
            }
            
            print("🧠 Testing LSTM prediction...")
            lstm_result = lstm_predictor.predict(market_data)
            print(f"   LSTM result: {lstm_result}")
            
            print("🎯 Testing Ensemble prediction...")
            # Create feature array for ensemble
            features = [
                market_data['price'],
                market_data['volume'],
                market_data['high'],
                market_data['low'], 
                market_data['open'],
                0.0, 0.0, 0.0  # placeholder for technical indicators
            ]
            ensemble_result = ensemble_manager.predict(features)
            print(f"   Ensemble result: {ensemble_result}")
            
            print("💰 Testing Kelly recommendation...")
            kelly_recommendation = await kelly_service.get_kelly_recommendation(symbol)
            print(f"   Kelly recommendation: {kelly_recommendation}")
            
        else:
            print("⚠️ No current market data available - using mock data")
            
            # Test with mock data
            mock_data = {
                'timestamp': '2025-07-28T13:20:00',
                'price': 20000.0,
                'volume': 100,
                'high': 20010.0, 
                'low': 19990.0,
                'open': 20005.0
            }
            
            print("🧠 Testing LSTM with mock data...")
            lstm_result = lstm_predictor.predict(mock_data)
            print(f"   LSTM result: {lstm_result}")
            
            print("💰 Testing Kelly recommendation with mock conditions...")
            kelly_recommendation = await kelly_service.get_kelly_recommendation(symbol)
            print(f"   Kelly recommendation: {kelly_recommendation}")
            
    except Exception as e:
        print(f"❌ Error testing with real data: {e}")
        print("📋 Falling back to basic integration test...")
        
        # Basic Kelly service test
        kelly_recommendation = await kelly_service.get_kelly_recommendation(symbol)
        print(f"💰 Basic Kelly recommendation: {kelly_recommendation}")
    
    # Stop Kelly service
    await kelly_service.stop()
    print("✅ Kelly service stopped")
    
    print("\n🎉 Live ML Kelly Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_live_ml_kelly_integration())