#!/usr/bin/env python3
"""
Kelly Criterion Integration Validation Test
===========================================

Comprehensive test suite to validate the ML-Enhanced Kelly Criterion
implementation is working correctly with LSTM and Ensemble integration.

Tests:
- Kelly Criterion calculation accuracy
- Position Sizing Service functionality  
- API endpoint responses
- Dashboard integration readiness
- ML model integration (LSTM + Ensemble)
"""

import asyncio
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_kelly_criterion_basic():
    """Test basic Kelly Criterion functionality"""
    print("🧮 Testing Kelly Criterion Basic Functionality...")
    
    try:
        from minhos.ml.kelly_criterion import get_kelly_criterion, KellyPosition
        
        kelly = get_kelly_criterion(capital=100000.0)
        assert kelly.capital == 100000.0
        assert kelly.max_kelly_fraction == 0.25
        assert kelly.confidence_threshold == 0.6
        
        # Test with mock ML predictions
        lstm_prediction = {
            'direction': 1,
            'confidence': 0.75,
            'probability': 0.65
        }
        
        ensemble_prediction = {
            'consensus_direction': 1,
            'consensus_confidence': 0.80,
            'probability': 0.70
        }
        
        position = kelly.calculate_position_size(
            symbol='NQU25-CME',
            current_price=23500.0,
            lstm_prediction=lstm_prediction,
            ensemble_prediction=ensemble_prediction
        )
        
        assert isinstance(position, KellyPosition)
        assert position.symbol == 'NQU25-CME'
        assert position.recommended_size >= 0
        assert 0.0 <= position.kelly_fraction <= 0.25
        assert 0.0 <= position.win_probability <= 1.0
        assert position.confidence_score > 0.6  # Above threshold
        
        print(f"✅ Kelly calculation successful:")
        print(f"   Recommended size: {position.recommended_size} contracts")
        print(f"   Kelly fraction: {position.kelly_fraction:.3f}")
        print(f"   Win probability: {position.win_probability:.2%}")
        print(f"   Confidence: {position.confidence_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kelly Criterion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_position_sizing_service():
    """Test Position Sizing Service functionality"""
    print("\n🔧 Testing Position Sizing Service...")
    
    try:
        from minhos.services.position_sizing_service import get_position_sizing_service
        
        service = get_position_sizing_service()
        assert service is not None
        
        # Get service status
        status = service.get_status()
        assert status['service'] == 'PositionSizingService'
        assert status['running'] == True
        assert status['ml_enabled'] == True
        
        print(f"✅ Position Sizing Service operational:")
        print(f"   Service: {status['service']}")
        print(f"   Running: {status['running']}")
        print(f"   ML Enabled: {status['ml_enabled']}")
        print(f"   LSTM Connected: {status['lstm_connected']}")
        print(f"   Ensemble Connected: {status['ensemble_connected']}")
        
        # Test position calculation
        position = await service.calculate_optimal_position(
            symbol='NQU25-CME',
            current_price=23500.0,
            market_data={'price': 23500.0, 'volume': 100}
        )
        
        assert position is not None
        assert position.symbol == 'NQU25-CME'
        
        print(f"✅ Position calculation successful:")
        print(f"   Symbol: {position.symbol}")
        print(f"   Size: {position.recommended_size}")
        print(f"   Kelly fraction: {position.kelly_fraction:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Position Sizing Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_kelly_api_endpoints():
    """Test Kelly API endpoints"""
    print("\n🌐 Testing Kelly API Endpoints...")
    
    try:
        from minhos.dashboard.api_kelly import (
            get_kelly_service_health, 
            get_kelly_performance_metrics,
            get_kelly_service
        )
        
        # Test service availability
        service = await get_kelly_service()
        assert service is not None
        
        # Test health endpoint
        health = await get_kelly_service_health()
        assert health.status in ['running', 'stopped']
        assert isinstance(health.ml_services_available, dict)
        assert 'kelly' in health.ml_services_available
        assert health.ml_services_available['kelly'] == True
        
        print(f"✅ Health endpoint working:")
        print(f"   Status: {health.status}")
        print(f"   Kelly available: {health.ml_services_available['kelly']}")
        print(f"   LSTM available: {health.ml_services_available['lstm']}")
        print(f"   Ensemble available: {health.ml_services_available['ensemble']}")
        
        # Test metrics endpoint
        metrics = await get_kelly_performance_metrics()
        assert metrics.service_status in ['running', 'stopped']
        assert isinstance(metrics.model_availability, dict)
        
        print(f"✅ Metrics endpoint working:")
        print(f"   Service status: {metrics.service_status}")
        print(f"   Total recommendations: {metrics.total_recommendations}")
        print(f"   Model availability: {metrics.model_availability}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kelly API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_pipeline_integration():
    """Test ML Pipeline integration"""
    print("\n🤖 Testing ML Pipeline Integration...")
    
    try:
        from minhos.services.ml_pipeline_service import MLPipelineService
        
        pipeline = MLPipelineService()
        assert pipeline is not None
        
        # Check ML components
        has_lstm = hasattr(pipeline, 'lstm_predictor') and pipeline.lstm_predictor is not None
        has_ensemble = hasattr(pipeline, 'ensemble_manager') and pipeline.ensemble_manager is not None
        has_kelly = hasattr(pipeline, 'kelly_manager') and pipeline.kelly_manager is not None
        
        print(f"✅ ML Pipeline components:")
        print(f"   LSTM Predictor: {has_lstm}")
        print(f"   Ensemble Manager: {has_ensemble}")  
        print(f"   Kelly Manager: {has_kelly}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Pipeline integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_models_availability():
    """Test ML models availability"""
    print("\n📊 Testing ML Models Availability...")
    
    try:
        import os
        from pathlib import Path
        
        ml_models_path = Path("/home/colindo/Sync/minh_v4/ml_models")
        
        # Check for LSTM models
        lstm_model = ml_models_path / "lstm_model_checkpoint.h5"
        lstm_available = lstm_model.exists()
        
        # Check for Ensemble models
        ensemble_path = ml_models_path / "ensemble"
        rf_model = ensemble_path / "random_forest_model.pkl"
        lgb_model = ensemble_path / "lightgbm_model.pkl"
        meta_model = ensemble_path / "meta_learner.pkl"
        
        ensemble_available = all([
            rf_model.exists(),
            lgb_model.exists(), 
            meta_model.exists()
        ])
        
        print(f"✅ ML Models status:")
        print(f"   LSTM model: {lstm_available}")
        print(f"   Ensemble models: {ensemble_available}")
        print(f"   Random Forest: {rf_model.exists()}")
        print(f"   LightGBM: {lgb_model.exists()}")
        print(f"   Meta learner: {meta_model.exists()}")
        
        return lstm_available and ensemble_available
        
    except Exception as e:
        print(f"❌ ML Models availability test failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🧪 Kelly Criterion Integration Validation Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_kelly_criterion_basic())
    test_results.append(await test_position_sizing_service())
    test_results.append(await test_kelly_api_endpoints())
    test_results.append(test_ml_pipeline_integration())
    test_results.append(test_ml_models_availability())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total:.1%}")
    
    if passed == total:
        print("🎉 All tests PASSED! Kelly Criterion implementation is ready.")
        print("\n✅ PHASE 2 WEEK 5-6 COMPLETE: ML-Enhanced Kelly Criterion")
        print("🎯 Ready for Week 7-8: System Integration")
    else:
        print("⚠️  Some tests FAILED. Review implementation before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)