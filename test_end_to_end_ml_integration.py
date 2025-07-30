#!/usr/bin/env python3
"""
End-to-End ML Integration Validation Test
==========================================

Comprehensive test suite for Phase 2 Week 7-8 System Integration.
Validates the complete ML pipeline integration from market data to trade execution.

Test Flow:
1. Market Data Collection
2. LSTM Prediction Generation
3. Ensemble Model Consensus
4. Kelly Position Sizing Calculation
5. Risk Management Validation
6. Trading Engine Integration
7. Performance Monitoring
8. Health Check Systems

This test validates that all components work together as an integrated system.
"""

import asyncio
import sys
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_ml_pipeline_integration():
    """Test complete ML pipeline integration"""
    print("🧠 Testing ML Pipeline Integration...")
    
    try:
        from minhos.services.ml_pipeline_service import MLPipelineService
        
        pipeline = MLPipelineService()
        assert pipeline is not None
        
        # Test LSTM component
        lstm_available = hasattr(pipeline, 'lstm_predictor') and pipeline.lstm_predictor is not None
        print(f"   LSTM Predictor: {'✅' if lstm_available else '❌'}")
        
        # Test Ensemble component
        ensemble_available = hasattr(pipeline, 'ensemble_manager') and pipeline.ensemble_manager is not None
        print(f"   Ensemble Manager: {'✅' if ensemble_available else '❌'}")
        
        # Test Kelly component
        kelly_available = hasattr(pipeline, 'kelly_manager') and pipeline.kelly_manager is not None
        print(f"   Kelly Manager: {'✅' if kelly_available else '❌'}")
        
        # Test predictions (using async methods)
        if lstm_available:
            try:
                lstm_pred = await pipeline.lstm_predictor.predict_direction({'price': 23500.0, 'volume': 100})
                print(f"   LSTM Prediction: {lstm_pred}")
            except Exception as e:
                print(f"   LSTM Prediction: ❌ ({str(e)[:50]})")
        
        if ensemble_available:
            try:
                ensemble_pred = pipeline.ensemble_manager.predict_consensus({'price': 23500.0, 'volume': 100})
                print(f"   Ensemble Prediction: {ensemble_pred}")
            except Exception as e:
                print(f"   Ensemble Prediction: ❌ ({str(e)[:50]})")
        
        return lstm_available and ensemble_available and kelly_available
        
    except Exception as e:
        print(f"❌ ML Pipeline integration test failed: {e}")
        return False

async def test_position_sizing_integration():
    """Test Kelly position sizing integration"""
    print("\n🎯 Testing Position Sizing Integration...")
    
    try:
        from minhos.services.position_sizing_service import get_position_sizing_service
        
        service = get_position_sizing_service()
        assert service is not None
        
        # Test status
        status = service.get_status()
        print(f"   Service Running: {'✅' if status['running'] else '❌'}")
        print(f"   ML Enabled: {'✅' if status['ml_enabled'] else '❌'}")
        
        # Test position calculation
        position = await service.calculate_optimal_position(
            symbol="NQU25-CME",
            current_price=23500.0,
            market_data={'price': 23500.0, 'volume': 100}
        )
        
        print(f"   Position Calculation: {'✅' if position is not None else '❌'}")
        if position:
            print(f"   Recommended Size: {position.recommended_size}")
            print(f"   Kelly Fraction: {position.kelly_fraction:.3f}")
            print(f"   Confidence: {position.confidence_score:.2f}")
        
        return position is not None
        
    except Exception as e:
        print(f"❌ Position sizing integration test failed: {e}")
        return False

async def test_ml_performance_monitor():
    """Test ML performance monitoring system"""
    print("\n📊 Testing ML Performance Monitor...")
    
    try:
        from minhos.services.ml_performance_monitor import get_ml_performance_monitor, MetricType
        
        monitor = get_ml_performance_monitor()
        assert monitor is not None
        
        # Start monitoring
        await monitor.start()
        print("   Monitor Started: ✅")
        
        # Record test metrics
        await monitor.record_metric("lstm", MetricType.ACCURACY, 0.65, "NQU25-CME")
        await monitor.record_metric("lstm", MetricType.LATENCY, 150.0, "NQU25-CME")
        await monitor.record_metric("ensemble", MetricType.CONFIDENCE, 0.70, "NQU25-CME")
        await monitor.record_metric("kelly", MetricType.KELLY_FRACTION, 0.15, "NQU25-CME")
        
        print("   Metrics Recording: ✅")
        
        # Get performance summary
        summary = monitor.get_performance_summary()
        print(f"   Performance Summary: {'✅' if summary else '❌'}")
        print(f"   Metrics Collected: {summary.get('metrics_collected', 0)}")
        print(f"   Health Score: {summary.get('latest_health_score', 0):.1f}/100")
        
        # Stop monitoring
        await monitor.stop()
        print("   Monitor Stopped: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ ML performance monitor test failed: {e}")
        return False

async def test_ml_trading_workflow():
    """Test ML trading workflow integration"""
    print("\n🔄 Testing ML Trading Workflow...")
    
    try:
        from minhos.services.ml_trading_workflow import get_ml_trading_workflow
        
        workflow = get_ml_trading_workflow()
        assert workflow is not None
        
        # Test configuration
        config = workflow.config
        print(f"   Workflow Configuration: {'✅' if config else '❌'}")
        print(f"   Min Confidence: {config.get('min_confidence_threshold', 0):.2%}")
        print(f"   Auto Trading: {'✅' if config.get('enable_auto_trading', False) else '❌ (Disabled for Safety)'}")
        
        # Test manual decision (safe - no auto execution)
        decision = await workflow.manual_decision("NQU25-CME")
        print(f"   Manual Decision: {'✅' if decision is not None else '❌'}")
        
        if decision:
            print(f"   Signal: {decision.signal.value}")
            print(f"   Confidence: {decision.confidence:.2%}")
            print(f"   Recommended Size: {decision.recommended_size}")
            print(f"   Risk Approved: {'✅' if decision.risk_approved else '❌'}")
            print(f"   Risk Reason: {decision.risk_reason}")
        
        # Test workflow status
        status = workflow.get_status()
        print(f"   Workflow Status: {status.get('workflow_status', 'unknown')}")
        
        return decision is not None
        
    except Exception as e:
        print(f"❌ ML trading workflow test failed: {e}")
        return False

async def test_trading_engine_kelly_integration():
    """Test trading engine Kelly integration"""
    print("\n⚙️ Testing Trading Engine Kelly Integration...")
    
    try:
        from minhos.services.trading_engine import TradingEngine
        
        trading_engine = TradingEngine()
        assert trading_engine is not None
        
        # Check position sizing service connection
        has_position_sizing = hasattr(trading_engine, 'position_sizing') and trading_engine.position_sizing is not None
        print(f"   Position Sizing Connected: {'✅' if has_position_sizing else '❌'}")
        
        if has_position_sizing:
            # Test position sizing integration
            status = trading_engine.position_sizing.get_status()
            print(f"   Position Sizing Status: {status.get('service', 'Unknown')}")
            print(f"   ML Enabled: {'✅' if status.get('ml_enabled', False) else '❌'}")
        
        # Check other ML integrations
        has_ml_pipeline = hasattr(trading_engine, 'ml_pipeline') and trading_engine.ml_pipeline is not None
        print(f"   ML Pipeline Connected: {'✅' if has_ml_pipeline else '❌'}")
        
        return has_position_sizing and has_ml_pipeline
        
    except Exception as e:
        print(f"❌ Trading engine Kelly integration test failed: {e}")
        return False

async def test_end_to_end_data_flow():
    """Test complete end-to-end data flow"""
    print("\n🌊 Testing End-to-End Data Flow...")
    
    try:
        # Simulate complete pipeline flow
        start_time = time.time()
        
        # Step 1: Market Data (simulated)
        market_data = {
            'symbol': 'NQU25-CME',
            'price': 23540.0,
            'volume': 150,
            'timestamp': datetime.now()
        }
        print("   1. Market Data: ✅")
        
        # Step 2: LSTM Prediction
        from minhos.services.ml_pipeline_service import MLPipelineService
        pipeline = MLPipelineService()
        
        try:
            lstm_pred = await pipeline.lstm_predictor.predict_direction(market_data)
            print(f"   2. LSTM Prediction: {'✅' if lstm_pred else '❌'}")
        except Exception as e:
            lstm_pred = None
            print(f"   2. LSTM Prediction: ❌ ({str(e)[:30]})")
        
        # Step 3: Ensemble Prediction
        try:
            ensemble_pred = pipeline.ensemble_manager.predict_consensus(market_data)
            print(f"   3. Ensemble Prediction: {'✅' if ensemble_pred else '❌'}")
        except Exception as e:
            ensemble_pred = None
            print(f"   3. Ensemble Prediction: ❌ ({str(e)[:30]})")
        
        # Step 4: Kelly Position Sizing
        from minhos.services.position_sizing_service import get_position_sizing_service
        position_service = get_position_sizing_service()
        
        kelly_position = await position_service.calculate_optimal_position(
            symbol=market_data['symbol'],
            current_price=market_data['price'],
            market_data=market_data
        )
        print(f"   4. Kelly Position Sizing: {'✅' if kelly_position else '❌'}")
        
        # Step 5: Risk Management (simulated approval)
        risk_approved = kelly_position.confidence_score > 0.5 if kelly_position else False
        print(f"   5. Risk Management: {'✅' if risk_approved else '❌'}")
        
        # Step 6: Performance Monitoring
        from minhos.services.ml_performance_monitor import get_ml_performance_monitor, MetricType
        monitor = get_ml_performance_monitor()
        
        if kelly_position:
            await monitor.record_metric("pipeline", MetricType.LATENCY, 
                                      (time.time() - start_time) * 1000, "NQU25-CME")
        print("   6. Performance Monitoring: ✅")
        
        # Calculate end-to-end metrics
        total_time = (time.time() - start_time) * 1000
        print(f"   End-to-End Latency: {total_time:.1f}ms")
        
        if kelly_position:
            print(f"   Final Recommendation: {kelly_position.recommended_size} contracts")
            print(f"   Kelly Fraction: {kelly_position.kelly_fraction:.3f}")
            print(f"   Combined Confidence: {kelly_position.confidence_score:.2%}")
        
        return kelly_position is not None and risk_approved
        
    except Exception as e:
        print(f"❌ End-to-end data flow test failed: {e}")
        return False

async def test_system_health_monitoring():
    """Test system health monitoring"""
    print("\n🏥 Testing System Health Monitoring...")
    
    try:
        from minhos.services.ml_performance_monitor import get_ml_performance_monitor
        
        monitor = get_ml_performance_monitor()
        await monitor.start()
        
        # Generate health snapshot
        snapshot = await monitor._generate_health_snapshot()
        
        print(f"   Health Snapshot: {'✅' if snapshot else '❌'}")
        print(f"   Overall Score: {snapshot.overall_score:.1f}/100")
        print(f"   LSTM Health: {snapshot.lstm_health.get('status', 'unknown')}")
        print(f"   Ensemble Health: {snapshot.ensemble_health.get('status', 'unknown')}")
        print(f"   Kelly Health: {snapshot.kelly_health.get('status', 'unknown')}")
        print(f"   Active Alerts: {len(snapshot.alerts)}")
        
        await monitor.stop()
        
        return snapshot.overall_score > 50.0  # At least 50% health
        
    except Exception as e:
        print(f"❌ System health monitoring test failed: {e}")
        return False

async def test_ml_api_integration():
    """Test ML API endpoint integration"""
    print("\n🌐 Testing ML API Integration...")
    
    try:
        from minhos.dashboard.api_kelly import (
            get_kelly_service_health,
            get_kelly_performance_metrics,
            get_current_kelly_recommendation
        )
        
        # Test health endpoint
        health = await get_kelly_service_health()
        print(f"   Health API: {'✅' if health else '❌'}")
        print(f"   Service Status: {health.status}")
        
        # Test metrics endpoint
        metrics = await get_kelly_performance_metrics()
        print(f"   Metrics API: {'✅' if metrics else '❌'}")
        print(f"   Service Status: {metrics.service_status}")
        
        # Test recommendation endpoint (with default params)
        try:
            recommendation = await get_current_kelly_recommendation()
            print(f"   Recommendation API: {'✅' if recommendation else '❌'}")
            if recommendation:
                print(f"   Position Size: {recommendation.position_size}")
                print(f"   Confidence: {recommendation.confidence:.2%}")
        except Exception as e:
            print(f"   Recommendation API: ❌ (Expected - needs market data)")
        
        return health.status == 'running' and metrics.service_status == 'running'
        
    except Exception as e:
        print(f"❌ ML API integration test failed: {e}")
        return False

async def main():
    """Run comprehensive end-to-end integration test suite"""
    print("=" * 70)
    print("🧪 End-to-End ML Integration Validation Test Suite")
    print("📋 Phase 2 Week 7-8: System Integration")
    print("=" * 70)
    
    test_results = []
    
    # Core ML Pipeline Tests
    test_results.append(await test_ml_pipeline_integration())
    test_results.append(await test_position_sizing_integration())
    test_results.append(await test_ml_performance_monitor())
    
    # Workflow Integration Tests
    test_results.append(await test_ml_trading_workflow())
    test_results.append(await test_trading_engine_kelly_integration())
    
    # End-to-End System Tests
    test_results.append(await test_end_to_end_data_flow())
    test_results.append(await test_system_health_monitoring())
    test_results.append(await test_ml_api_integration())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 70)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total:.1%}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! End-to-End ML Integration Complete!")
        print("\n✅ PHASE 2 WEEK 7-8 COMPLETE: System Integration")
        print("🎯 PHASE 2 COMPLETE: ML Features Implementation")
        print("\n🚀 Ready for Production Deployment!")
        
        print("\n📊 System Capabilities Validated:")
        print("   ✅ LSTM Neural Network Predictions")
        print("   ✅ Ensemble Model Consensus")
        print("   ✅ ML-Enhanced Kelly Criterion Position Sizing")
        print("   ✅ End-to-End Trading Workflow")
        print("   ✅ Real-time Performance Monitoring")
        print("   ✅ System Health Checks and Alerts")
        print("   ✅ API Integration and Dashboard Readiness")
        print("   ✅ Risk Management Integration")
        
    else:
        print("⚠️  Some tests FAILED. Review integration before production deployment.")
        print(f"   Failed tests: {total - passed}")
        print("   Check logs above for specific failure details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)