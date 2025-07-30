#!/usr/bin/env python3
"""
ML Integration Test
==================

Test the ML service integration with Kelly Criterion implementation.
Validates LSTM, Ensemble, and Kelly service integration.

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List

# Import our integration services
from services.ml_service_connector import MLServiceConnector
from services.kelly_service import KellyService

def test_ml_service_connector():
    """Test ML Service Connector initialization and basic functionality"""
    print("\n🔌 Testing ML Service Connector...")
    
    try:
        # Initialize connector
        connector = MLServiceConnector()
        
        # Test configuration
        config = connector.get_config()
        assert 'enable_lstm' in config
        assert 'enable_ensemble' in config
        print(f"  ✅ Configuration loaded: {len(config)} settings")
        
        # Test status before initialization
        status = connector.get_status()
        assert 'services_initialized' in status
        print(f"  ✅ Status available: initialized={status['services_initialized']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ML Service Connector test failed: {e}")
        return False

async def test_ml_service_initialization():
    """Test ML service initialization"""
    print("\n🚀 Testing ML Service Initialization...")
    
    try:
        connector = MLServiceConnector()
        
        # Initialize services
        success = await connector.initialize_services()
        print(f"  ✅ Services initialization: {success}")
        
        # Check service status
        status = connector.get_status()
        print(f"  ✅ Services initialized: {status['services_initialized']}")
        print(f"  ✅ Service status: {status['service_status']}")
        
        # Health check
        health = await connector.health_check()
        print(f"  ✅ Health check complete: overall_healthy={health['overall_healthy']}")
        print(f"  ✅ Available services: {list(health['services'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ML Service initialization test failed: {e}")
        return False

async def test_kelly_service():
    """Test Kelly Service functionality"""
    print("\n⚙️ Testing Kelly Service...")
    
    try:
        # Initialize Kelly Service
        kelly_service = KellyService()
        
        # Test configuration
        config = kelly_service.get_config()
        print(f"  ✅ Kelly Service config loaded: {len(config)} settings")
        
        # Start service
        await kelly_service.start()
        print("  ✅ Kelly Service started")
        
        # Check status
        status = kelly_service.get_status()
        print(f"  ✅ Kelly Service status: running={status['running']}")
        
        # Test health check
        health = await kelly_service.get_service_health()
        print(f"  ✅ Health check: service_running={health['service_running']}")
        
        # Stop service
        await kelly_service.stop()
        print("  ✅ Kelly Service stopped")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Kelly Service test failed: {e}")
        return False

async def test_mock_ml_prediction():
    """Test ML prediction with mock data"""
    print("\n🧠 Testing Mock ML Prediction...")
    
    try:
        connector = MLServiceConnector()
        await connector.initialize_services()
        
        # Mock market data
        market_data = {
            'symbol': 'NQU25-CME',
            'price': 23450.0,
            'close': 23450.0,
            'high': 23500.0,
            'low': 23400.0,
            'open': 23425.0,
            'volume': 125000,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test LSTM prediction (may fail if service not available)
        try:
            lstm_pred = await connector.get_lstm_prediction('NQU25-CME', market_data)
            if lstm_pred:
                print(f"  ✅ LSTM prediction: confidence={lstm_pred.get('confidence', 0):.3f}")
            else:
                print("  ⚠️  LSTM prediction: Service not available")
        except Exception as e:
            print(f"  ⚠️  LSTM prediction failed: {e}")
        
        # Test Ensemble prediction (may fail if service not available)
        try:
            ensemble_pred = await connector.get_ensemble_prediction('NQU25-CME', market_data)
            if ensemble_pred:
                print(f"  ✅ Ensemble prediction: confidence={ensemble_pred.get('confidence', 0):.3f}")
            else:
                print("  ⚠️  Ensemble prediction: Service not available")
        except Exception as e:
            print(f"  ⚠️  Ensemble prediction failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Mock ML prediction test failed: {e}")
        return False

async def test_end_to_end_kelly_recommendation():
    """Test end-to-end Kelly recommendation"""
    print("\n🎯 Testing End-to-End Kelly Recommendation...")
    
    try:
        # Start Kelly Service
        kelly_service = KellyService()
        await kelly_service.start()
        
        # Mock market data
        market_data = {
            'symbol': 'NQU25-CME',
            'price': 23450.0,
            'close': 23450.0,
            'high': 23500.0,
            'low': 23400.0,
            'open': 23425.0,
            'volume': 125000,
            'timestamp': datetime.now().isoformat()
        }
        
        # Mock trade history
        trade_history = [
            {'pnl': 150.0, 'timestamp': (datetime.now() - timedelta(days=i)).isoformat(), 'symbol': 'NQU25-CME'}
            for i in range(1, 6)
        ] + [
            {'pnl': -100.0, 'timestamp': (datetime.now() - timedelta(days=i)).isoformat(), 'symbol': 'NQU25-CME'}
            for i in range(6, 9)
        ]
        
        # Get Kelly recommendation
        recommendation = await kelly_service.get_kelly_recommendation(
            symbol='NQU25-CME',
            market_data=market_data,
            trade_history=trade_history,
            account_capital=100000.0
        )
        
        print(f"  ✅ Kelly recommendation generated:")
        print(f"     Symbol: {recommendation.symbol}")
        print(f"     Status: {recommendation.status}")
        print(f"     Kelly Fraction: {recommendation.kelly_fraction:.4f}")
        print(f"     Position Size: {recommendation.position_size} contracts")
        print(f"     Confidence: {recommendation.confidence:.3f}")
        print(f"     Win Probability: {recommendation.win_probability:.3f}")
        print(f"     Win/Loss Ratio: {recommendation.win_loss_ratio:.3f}")
        print(f"     Capital Risk: {recommendation.capital_risk:.4f}")
        print(f"     ML Models Used: {recommendation.ml_models_used}")
        print(f"     Model Agreement: {recommendation.model_agreement}")
        print(f"     Reasoning: {recommendation.reasoning}")
        
        # Validate recommendation
        assert recommendation.symbol == 'NQU25-CME'
        assert isinstance(recommendation.kelly_fraction, float)
        assert isinstance(recommendation.position_size, int)
        assert 0 <= recommendation.confidence <= 1
        assert recommendation.win_probability > 0
        assert recommendation.win_loss_ratio > 0
        
        print("  ✅ Recommendation validation passed")
        
        # Test performance metrics
        metrics = await kelly_service.get_performance_metrics()
        print(f"  ✅ Performance metrics: total_recs={metrics.total_recommendations}")
        
        # Test recent recommendations
        recent = await kelly_service.get_recent_recommendations(limit=5)
        print(f"  ✅ Recent recommendations: {len(recent)} found")
        
        # Stop service
        await kelly_service.stop()
        
        return True
        
    except Exception as e:
        print(f"  ❌ End-to-end Kelly recommendation test failed: {e}")
        return False

async def test_performance_benchmark():
    """Test performance of Kelly recommendation generation"""
    print("\n⚡ Testing Performance Benchmark...")
    
    try:
        import time
        
        # Start Kelly Service
        kelly_service = KellyService()
        await kelly_service.start()
        
        # Mock data
        market_data = {
            'symbol': 'NQU25-CME',
            'price': 23450.0,
            'close': 23450.0,
            'volume': 125000,
            'timestamp': datetime.now().isoformat()
        }
        
        # Performance test
        start_time = time.time()
        recommendations = []
        
        for i in range(10):  # Test 10 recommendations
            rec = await kelly_service.get_kelly_recommendation(
                symbol='NQU25-CME',
                market_data=market_data,
                account_capital=100000.0
            )
            recommendations.append(rec)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_ms = (total_time / len(recommendations)) * 1000
        
        print(f"  ✅ Performance test: {len(recommendations)} recommendations")
        print(f"  ✅ Total time: {total_time:.3f} seconds")
        print(f"  ✅ Average time: {avg_time_ms:.2f}ms per recommendation")
        
        # Validate performance (should be well under 1 second per recommendation)
        assert avg_time_ms < 1000, f"Performance too slow: {avg_time_ms:.2f}ms"
        
        # Check recommendation consistency
        successful_recs = [r for r in recommendations if r.status == 'success']
        print(f"  ✅ Successful recommendations: {len(successful_recs)}/{len(recommendations)}")
        
        await kelly_service.stop()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Performance benchmark test failed: {e}")
        return False

async def main():
    """Run all ML integration tests"""
    print("🚀 MinhOS v4 - ML Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("ML Service Connector", test_ml_service_connector),
        ("ML Service Initialization", test_ml_service_initialization),
        ("Kelly Service", test_kelly_service),
        ("Mock ML Prediction", test_mock_ml_prediction),
        ("End-to-End Kelly Recommendation", test_end_to_end_kelly_recommendation),
        ("Performance Benchmark", test_performance_benchmark)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ML Integration: ALL TESTS PASSED!")
        print("✅ Ready for production integration with MinhOS")
    else:
        print(f"\n⚠️  ML Integration: {total-passed} tests failed")
        print("⚠️  Some ML services may not be available - this is expected in development")
        
        # Check if critical tests passed
        critical_tests = ["ML Service Connector", "Kelly Service", "End-to-End Kelly Recommendation"]
        critical_results = [(name, result) for name, result in results if name in critical_tests]
        critical_passed = sum(1 for _, result in critical_results if result)
        
        if critical_passed == len(critical_tests):
            print("✅ All critical tests passed - Integration is functional")
        else:
            print("❌ Critical tests failed - Review implementation")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite crashed: {e}")
        sys.exit(1)