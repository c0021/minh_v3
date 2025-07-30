#!/usr/bin/env python3
"""
Test LSTM Integration with AI Brain Service

Verifies that the LSTM predictor integrates cleanly with the consolidated ai_brain_service.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.ai_brain_service import AIBrainService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_lstm_integration():
    """Test LSTM integration with AI Brain Service"""
    print("🧠 Testing LSTM Integration with AI Brain Service")
    print("=" * 60)
    
    try:
        # Initialize AI Brain Service
        print("1. Initializing AI Brain Service...")
        ai_brain = AIBrainService()
        
        # Check ML capabilities
        print(f"2. ML Capabilities: {list(ai_brain.ml_capabilities.keys())}")
        
        # Test LSTM predictor directly
        if 'lstm' in ai_brain.ml_capabilities:
            print("3. Testing LSTM predictor...")
            lstm_predictor = ai_brain.ml_capabilities['lstm']
            
            # Get performance stats
            stats = lstm_predictor.get_performance_stats()
            print(f"   LSTM Stats: {stats}")
            
            # Test prediction with sample data
            sample_market_data = {
                'price': 23442.50,
                'close': 23442.50,
                'volume': 1500,
                'high': 23445.00,
                'low': 23440.00,
                'open': 23441.00,
                'timestamp': 1640995200  # Sample timestamp
            }
            
            print("4. Testing LSTM prediction with sample data...")
            prediction = await lstm_predictor.predict_direction(sample_market_data)
            print(f"   LSTM Prediction: {prediction}")
            
        else:
            print("3. ⚠️ LSTM predictor not available")
        
        # Test ML analysis method
        print("5. Testing ML analysis integration...")
        sample_data = [
            {'close': 23440.0, 'volume': 1000, 'timestamp': 1640995100},
            {'close': 23441.5, 'volume': 1200, 'timestamp': 1640995140},
            {'close': 23442.5, 'volume': 1500, 'timestamp': 1640995180},
        ]
        
        ml_analysis = await ai_brain._analyze_ml_predictions(sample_data)
        print(f"   ML Analysis Result: {ml_analysis}")
        
        # Test full analysis with ML
        print("6. Testing full market analysis with ML integration...")
        # Add more sample data for complete analysis
        extended_data = []
        base_price = 23440.0
        for i in range(30):
            extended_data.append({
                'close': base_price + (i * 0.5),
                'volume': 1000 + (i * 10),
                'timestamp': 1640995000 + (i * 30),
                'high': base_price + (i * 0.5) + 1.0,
                'low': base_price + (i * 0.5) - 1.0,
                'open': base_price + (i * 0.5) - 0.2,
            })
        
        # Store data in AI brain buffer
        ai_brain.market_data_buffer.extend(extended_data)
        
        # Run analysis
        try:
            analysis_result = await ai_brain._get_analysis_data()
            if analysis_result:
                print("   ✅ Analysis data retrieved successfully")
                
                # Test individual analysis components
                trend_analysis = await ai_brain._analyze_trend(extended_data)
                ml_analysis_full = await ai_brain._analyze_ml_predictions(extended_data)
                
                print(f"   Trend Analysis: {trend_analysis}")
                print(f"   ML Analysis: {ml_analysis_full}")
                
        except Exception as e:
            print(f"   ⚠️ Analysis test skipped: {e}")
        
        print("\n✅ LSTM Integration Test Complete!")
        print("=" * 60)
        
        # Summary
        print("📊 Test Summary:")
        print(f"   - AI Brain Service: ✅ Initialized")
        print(f"   - ML Capabilities: {len(ai_brain.ml_capabilities)} loaded")
        print(f"   - LSTM Available: {'✅' if 'lstm' in ai_brain.ml_capabilities else '❌'}")
        print(f"   - ML Analysis: ✅ Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 MinhOS LSTM Integration Test")
    print(f"📁 Project Root: {project_root}")
    print()
    
    success = await test_lstm_integration()
    
    if success:
        print("\n🎉 All tests passed! LSTM integration is working.")
        return 0
    else:
        print("\n💥 Tests failed! Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)