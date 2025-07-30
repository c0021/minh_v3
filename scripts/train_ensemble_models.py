#!/usr/bin/env python3
"""
Ensemble Models Training Script

Trains ensemble of ML models (XGBoost, LightGBM, Random Forest, CatBoost) 
for multi-model trading signal fusion.
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

from capabilities.ensemble import EnsembleManager
from capabilities.prediction.lstm.trainer import LSTMTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'logs' / 'ensemble_training.log')
    ]
)
logger = logging.getLogger(__name__)

async def train_ensemble_models(symbol: str = 'NQ', 
                               days_back: int = 30, 
                               verbose: bool = True) -> bool:
    """
    Train ensemble models with historical data
    
    Args:
        symbol: Trading symbol (e.g., 'NQ')
        days_back: Days of historical data to use
        verbose: Enable verbose output
        
    Returns:
        Success status
    """
    try:
        print("🎯 MinhOS Ensemble Training Pipeline")
        print("=" * 60)
        print(f"📊 Symbol: {symbol}")
        print(f"📅 Historical Data: {days_back} days")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Initialize Ensemble Manager
        print("1. Initializing Ensemble Manager...")
        model_path = project_root / "ml_models" / "ensemble"
        model_path.mkdir(exist_ok=True)
        
        ensemble_manager = EnsembleManager(model_path=str(model_path))
        
        print(f"   ✅ Ensemble Manager initialized")
        print(f"   📁 Model path: {model_path}")
        print(f"   🔧 Config: {ensemble_manager.config}")
        print()
        
        # Step 2: Load Historical Data (reuse LSTM trainer's data loading)
        print("2. Loading Historical Data...")
        lstm_trainer = LSTMTrainer()  # Use LSTM trainer for data loading
        
        training_data = await lstm_trainer.load_training_data(symbol, days_back)
        
        if len(training_data) < 50:
            print(f"   ❌ Insufficient data: {len(training_data)} points (need at least 50)")
            return False
        
        print(f"   ✅ Loaded {len(training_data)} data points")
        print(f"   📈 Price range: ${training_data[0]['price']:.2f} - ${training_data[-1]['price']:.2f}")
        print()
        
        # Step 3: Train Ensemble Models
        print("3. Training Ensemble Models...")
        print("   🏗️ Base Models: XGBoost, LightGBM, Random Forest, CatBoost")
        print("   🧠 Meta-Learner: Linear Regression (Stacking)")
        print("   (This may take several minutes...)")
        print()
        
        training_results = await ensemble_manager.train_ensemble(
            training_data=training_data,
            validation_split=0.2
        )
        
        # Step 4: Display Results
        print("4. Training Results:")
        print("=" * 60)
        
        if training_results['success']:
            print("   ✅ Ensemble Training SUCCESSFUL!")
            print()
            print("   📊 Training Metrics:")
            print(f"      - Training Samples: {training_results.get('training_samples', 'N/A')}")
            print(f"      - Validation Samples: {training_results.get('validation_samples', 'N/A')}")
            print(f"      - Features Engineered: {training_results.get('features', 'N/A')}")
            print(f"      - Base Models: {training_results.get('base_models', 'N/A')}")
            print()
            
            print("   🎯 Model Performance:")
            for model_name, performance in training_results.get('model_performance', {}).items():
                accuracy = performance.get('direction_accuracy', 0)
                mse = performance.get('mse', 0)
                print(f"      - {model_name.upper()}: {accuracy:.1%} accuracy, MSE: {mse:.6f}")
            print()
            
            print("   ⚖️ Model Weights:")
            for model_name, weight in training_results.get('model_weights', {}).items():
                print(f"      - {model_name.upper()}: {weight:.3f}")
            print()
            
            print("   🔥 Top Features:")
            feature_names = training_results.get('feature_names', [])
            if feature_names:
                for i, feature in enumerate(feature_names[:10]):
                    print(f"      {i+1:2d}. {feature}")
            print()
            
            print("   🚀 Ensemble Models Ready for Production!")
            
        else:
            print("   ❌ Ensemble Training FAILED!")
            print(f"      Error: {training_results.get('message', 'Unknown error')}")
            return False
        
        # Step 5: Test Ensemble Predictions
        print()
        print("5. Testing Ensemble Predictions...")
        
        # Test prediction capability with recent data
        test_data = training_data[-25:]  # Use last 25 points for testing
        
        prediction = await ensemble_manager.predict_ensemble(test_data)
        print(f"   🎯 Sample Prediction: {prediction}")
        
        if prediction.get('source') == 'ensemble_ml_models':
            print("   ✅ Ensemble predictions working correctly!")
            
            # Show prediction details
            direction = "UP" if prediction['direction'] > 0 else "DOWN" if prediction['direction'] < 0 else "NEUTRAL"
            print(f"      - Direction: {direction}")
            print(f"      - Confidence: {prediction['confidence']:.1%}")
            print(f"      - Model Agreement: {prediction['model_agreement']:.1%}")
            print(f"      - Ensemble Method: {prediction.get('ensemble_method', 'N/A')}")
            
            # Show base model predictions
            base_preds = prediction.get('base_predictions', {})
            if base_preds:
                print("      - Base Predictions:")
                for model, pred in base_preds.items():
                    pred_dir = "↗" if pred > 0.05 else "↘" if pred < -0.05 else "→"
                    print(f"        {model.upper()}: {pred_dir} {pred:.4f}")
        else:
            print(f"   ⚠️ Ensemble prediction issue: {prediction.get('message', 'Unknown')}")
        
        # Show performance stats
        print()
        print("6. Ensemble Performance Stats:")
        stats = ensemble_manager.get_performance_stats()
        print(f"   📈 Models Enabled: {stats['is_enabled']}")
        print(f"   🎓 Models Trained: {stats['is_trained']}")
        print(f"   🔢 Predictions Made: {stats['predictions_made']}")
        print(f"   🏗️ Base Models: {', '.join(stats['base_models'])}")
        
        print()
        print("=" * 60)
        print("🎉 Ensemble Training Pipeline Complete!")
        print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ensemble training pipeline failed: {e}")
        logger.error(f"Training error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function with command line argument handling"""
    parser = argparse.ArgumentParser(description='Train Ensemble Models for MinhOS')
    parser.add_argument('--symbol', default='NQ', help='Trading symbol (default: NQ)')
    parser.add_argument('--days', type=int, default=30, help='Days of historical data (default: 30)')
    parser.add_argument('--quick', action='store_true', help='Quick training (7 days)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Quick training mode
    if args.quick:
        args.days = 7
        print("🚀 Quick training mode: 7 days of data")
    
    # Ensure logs directory exists
    (project_root / 'logs').mkdir(exist_ok=True)
    
    # Run training
    success = await train_ensemble_models(
        symbol=args.symbol,
        days_back=args.days,
        verbose=args.verbose
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)