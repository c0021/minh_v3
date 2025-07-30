#!/usr/bin/env python3
"""
Test Trained LSTM Model

Verify that the trained LSTM model can make predictions.
"""

import asyncio
import sys
import logging
from pathlib import Path
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from capabilities.prediction.lstm import LSTMPredictor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_trained_model():
    """Test the trained LSTM model"""
    print("🧠 Testing Trained LSTM Model")
    print("=" * 50)
    
    try:
        # Initialize predictor
        model_path = project_root / "ml_models" / "lstm_model"
        lstm_predictor = LSTMPredictor(
            sequence_length=20,
            features=8,
            model_path=str(model_path)
        )
        
        print(f"📊 Initial Stats: {lstm_predictor.get_performance_stats()}")
        
        # Manually load the trained model
        print("📥 Loading trained model...")
        try:
            import tensorflow as tf
            lstm_predictor.model = tf.keras.models.load_model(f"{model_path}.h5", compile=False)
            lstm_predictor.is_trained = True
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
        
        # Test with sample data sequence
        print("🎯 Testing predictions with sample data...")
        
        # Generate a sequence of market data to build up the buffer
        sample_data_sequence = []
        base_price = 23400.0
        
        for i in range(25):  # More than sequence_length (20)
            price = base_price + (i * 0.5) + np.random.normal(0, 1.0)
            sample_data = {
                'price': price,
                'close': price,
                'volume': 1500 + (i * 10),
                'high': price + 2.0,
                'low': price - 2.0,
                'open': price - 0.5,
                'timestamp': 1640995200 + (i * 60)
            }
            sample_data_sequence.append(sample_data)
        
        # Feed data to predictor to build buffer
        predictions = []
        for i, data in enumerate(sample_data_sequence):
            prediction = await lstm_predictor.predict_direction(data)
            predictions.append(prediction)
            print(f"   Step {i+1}: {prediction}")
            
            # Once we have enough data, we should start getting real predictions
            if i >= 20 and prediction.get('source') == 'lstm_neural_network':
                print(f"✅ Successfully generating LSTM predictions after {i+1} steps!")
                break
        
        # Show final stats
        print(f"📈 Final Stats: {lstm_predictor.get_performance_stats()}")
        
        # Check if we got any real predictions
        real_predictions = [p for p in predictions if p.get('source') == 'lstm_neural_network']
        if real_predictions:
            print(f"🎉 SUCCESS: Generated {len(real_predictions)} real LSTM predictions!")
            print("📊 Sample predictions:")
            for i, pred in enumerate(real_predictions[:3]):
                direction = "UP" if pred['direction'] > 0 else "DOWN" if pred['direction'] < 0 else "NEUTRAL"
                print(f"   {i+1}. Direction: {direction}, Confidence: {pred['confidence']:.1%}")
            return True
        else:
            print("⚠️ No real LSTM predictions generated - model may need more training data")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_trained_model()
    
    if success:
        print("\n🎉 Trained LSTM model is working correctly!")
        return 0
    else:
        print("\n💥 Trained LSTM model test failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)