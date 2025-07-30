#!/usr/bin/env python3
"""
LSTM Model Training Script

Trains LSTM neural network using Sierra Chart historical data.
Integrates with MinhOS consolidated architecture.
"""

import asyncio
import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capabilities.prediction.lstm import LSTMPredictor
from capabilities.prediction.lstm.trainer import LSTMTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'logs' / 'lstm_training.log')
    ]
)
logger = logging.getLogger(__name__)

async def train_lstm_model(symbol: str = 'NQ', 
                          days_back: int = 30, 
                          epochs: int = 50,
                          verbose: bool = True) -> bool:
    """
    Train LSTM model with historical data
    
    Args:
        symbol: Trading symbol (e.g., 'NQ')
        days_back: Days of historical data to use
        epochs: Number of training epochs
        verbose: Enable verbose output
        
    Returns:
        Success status
    """
    try:
        print("🧠 MinhOS LSTM Training Pipeline")
        print("=" * 60)
        print(f"📊 Symbol: {symbol}")
        print(f"📅 Historical Data: {days_back} days")
        print(f"🔄 Training Epochs: {epochs}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Initialize LSTM Predictor
        print("1. Initializing LSTM Predictor...")
        model_path = project_root / "ml_models" / "lstm_model"
        model_path.parent.mkdir(exist_ok=True)
        
        lstm_predictor = LSTMPredictor(
            sequence_length=20,
            features=8,
            model_path=str(model_path)
        )
        
        print(f"   ✅ LSTM Predictor initialized")
        print(f"   📁 Model path: {model_path}")
        
        # Step 2: Initialize Trainer
        print("2. Initializing LSTM Trainer...")
        trainer = LSTMTrainer(predictor=lstm_predictor)
        
        # Update training configuration
        trainer.update_training_config(
            epochs=epochs,
            min_data_points=200,  # Lower requirement for testing
            early_stopping_patience=10
        )
        
        print(f"   ✅ Trainer initialized")
        print(f"   📋 Config: {trainer.get_training_config()}")
        print()
        
        # Step 3: Start Training
        print("3. Starting LSTM Training...")
        print("   (This may take several minutes depending on data size and epochs)")
        print()
        
        training_results = await trainer.train_lstm_model(
            symbol=symbol,
            days_back=days_back,
            save_model=True
        )
        
        # Step 4: Display Results
        print("4. Training Results:")
        print("=" * 60)
        
        if training_results['success']:
            print("   ✅ Training SUCCESSFUL!")
            print()
            print("   📊 Training Metrics:")
            print(f"      - Data Points Used: {training_results.get('data_points_used', 'N/A')}")
            print(f"      - Training Samples: {training_results.get('training_samples', 'N/A')}")
            print(f"      - Validation Samples: {training_results.get('validation_samples', 'N/A')}")
            print(f"      - Epochs Completed: {training_results.get('epochs_completed', 'N/A')}")
            print()
            print("   🎯 Performance Metrics:")
            print(f"      - Direction Accuracy: {training_results.get('direction_accuracy', 0):.1%}")
            print(f"      - Final Loss: {training_results.get('final_loss', 0):.6f}")
            print(f"      - Validation Loss: {training_results.get('final_val_loss', 0):.6f}")
            print(f"      - Best Val Loss: {training_results.get('best_val_loss', 0):.6f}")
            print()
            
            if training_results.get('model_saved'):
                print("   💾 Model Persistence:")
                print(f"      - Model Saved: ✅ {training_results.get('model_path', 'N/A')}")
                print(f"      - Metadata: ✅ {training_results.get('metadata_path', 'N/A')}")
            
            print()
            print("   🚀 LSTM Model Ready for Production!")
            
        else:
            print("   ❌ Training FAILED!")
            print(f"      Error: {training_results.get('message', 'Unknown error')}")
            return False
        
        # Step 5: Test Trained Model
        print()
        print("5. Testing Trained Model...")
        
        # Test prediction capability
        sample_data = {
            'price': 23442.50,
            'close': 23442.50,
            'volume': 1500,
            'high': 23445.00,
            'low': 23440.00,
            'open': 23441.00,
            'timestamp': datetime.now().timestamp()
        }
        
        prediction = await lstm_predictor.predict_direction(sample_data)
        print(f"   🎯 Sample Prediction: {prediction}")
        
        if prediction.get('source') == 'lstm_neural_network':
            print("   ✅ Model predictions working correctly!")
        else:
            print(f"   ⚠️ Model prediction issue: {prediction.get('message', 'Unknown')}")
        
        print()
        print("=" * 60)
        print("🎉 LSTM Training Pipeline Complete!")
        print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        logger.error(f"Training error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function with command line argument handling"""
    parser = argparse.ArgumentParser(description='Train LSTM Model for MinhOS')
    parser.add_argument('--symbol', default='NQ', help='Trading symbol (default: NQ)')
    parser.add_argument('--days', type=int, default=30, help='Days of historical data (default: 30)')
    parser.add_argument('--epochs', type=int, default=50, help='Training epochs (default: 50)')
    parser.add_argument('--quick', action='store_true', help='Quick training (10 epochs, 7 days)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Quick training mode
    if args.quick:
        args.epochs = 10
        args.days = 7
        print("🚀 Quick training mode: 10 epochs, 7 days of data")
    
    # Ensure logs directory exists
    (project_root / 'logs').mkdir(exist_ok=True)
    
    # Run training
    success = await train_lstm_model(
        symbol=args.symbol,
        days_back=args.days,
        epochs=args.epochs,
        verbose=args.verbose
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)