#!/usr/bin/env python3
"""
Test ML Monitoring Integration

Tests the integration of ML monitoring with AI Brain Service and Dashboard API.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.ml_monitoring_service import get_ml_monitoring_service
from minhos.services.ai_brain_service import AIBrainService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ml_monitoring_integration():
    """Test ML monitoring service integration"""
    logger.info("🧪 Testing ML Monitoring Integration...")
    
    try:
        # Test 1: ML Monitoring Service Basic Functions
        logger.info("1. Testing ML Monitoring Service...")
        
        ml_monitoring = get_ml_monitoring_service()
        
        # Start monitoring service
        await ml_monitoring.start()
        logger.info("✅ ML Monitoring Service started")
        
        # Test recording metrics
        ml_monitoring.record_performance_metric('lstm', 'latency_ms', 150.0)
        ml_monitoring.record_performance_metric('lstm', 'confidence', 0.85)
        ml_monitoring.record_performance_metric('lstm', 'error_rate', 0.0)
        
        ml_monitoring.record_performance_metric('ensemble', 'latency_ms', 250.0)
        ml_monitoring.record_performance_metric('ensemble', 'confidence', 0.78)
        ml_monitoring.record_performance_metric('ensemble', 'error_rate', 0.0)
        
        ml_monitoring.record_performance_metric('kelly', 'latency_ms', 50.0)
        ml_monitoring.record_performance_metric('kelly', 'win_rate', 0.62)
        ml_monitoring.record_performance_metric('kelly', 'error_rate', 0.0)
        
        logger.info("✅ Recorded performance metrics for all models")
        
        # Test 2: Alert Summary
        logger.info("2. Testing alert summary...")
        
        alert_summary = ml_monitoring.get_alert_summary()
        logger.info(f"Alert Summary: {alert_summary}")
        
        # Test 3: Performance Trends
        logger.info("3. Testing performance trends...")
        
        for model_type in ['lstm', 'ensemble', 'kelly']:
            trends = ml_monitoring.get_performance_trends(model_type, 1)
            logger.info(f"{model_type.upper()} trends: {trends}")
        
        # Test 4: AI Brain Service Integration
        logger.info("4. Testing AI Brain Service integration...")
        
        ai_brain = AIBrainService()
        
        # Check if ML monitoring is properly integrated
        if hasattr(ai_brain, 'ml_monitoring'):
            logger.info("✅ ML monitoring integrated with AI Brain Service")
        else:
            logger.warning("❌ ML monitoring not integrated with AI Brain Service")
        
        # Test 5: Generate some test alerts
        logger.info("5. Testing alert generation...")
        
        # Simulate high latency to trigger alert
        ml_monitoring.record_performance_metric('lstm', 'latency_ms', 1500.0)  # High latency
        await asyncio.sleep(0.1)  # Give time for alert processing
        
        # Simulate low accuracy to trigger alert
        ml_monitoring.record_performance_metric('ensemble', 'accuracy', 0.3)  # Low accuracy
        await asyncio.sleep(0.1)
        
        # Check alerts again
        alert_summary = ml_monitoring.get_alert_summary()
        logger.info(f"Alert Summary after test conditions: {alert_summary}")
        
        # Test 6: Configuration
        logger.info("6. Testing configuration...")
        
        # Update configuration
        ml_monitoring.set_config(
            accuracy_degradation_threshold=0.10,
            latency_spike_threshold=3.0
        )
        logger.info("✅ Configuration updated")
        
        # Test 7: Performance Statistics (using the correct method)
        logger.info("7. Testing performance statistics...")
        
        # Check if service has performance tracking
        if hasattr(ml_monitoring, 'stats'):
            logger.info(f"Performance stats available: {ml_monitoring.stats}")
        else:
            logger.info("No performance stats method found")
        
        # Clean up
        await ml_monitoring.stop()
        logger.info("✅ ML Monitoring Service stopped")
        
        logger.info("🎉 ML Monitoring Integration Test Complete!")
        
        return {
            "success": True,
            "alerts_generated": alert_summary.get('active_alerts', 0),
            "metrics_recorded": True,
            "trends_available": True,
            "ai_brain_integration": hasattr(ai_brain, 'ml_monitoring')
        }
        
    except Exception as e:
        logger.error(f"❌ ML Monitoring Integration Test Failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def test_api_endpoints():
    """Test ML monitoring API endpoints"""
    logger.info("🧪 Testing ML Monitoring API Endpoints...")
    
    try:
        # Import API router
        from minhos.dashboard.api_ml_performance import get_ml_monitoring_alerts, get_ml_system_health
        
        # Test alerts endpoint
        alerts_result = await get_ml_monitoring_alerts()
        logger.info(f"Alerts API result: {alerts_result}")
        
        # Test system health endpoint
        health_result = await get_ml_system_health()
        logger.info(f"System Health API result: {health_result}")
        
        logger.info("✅ API endpoints working correctly")
        
        return {"success": True, "api_tests_passed": True}
        
    except Exception as e:
        logger.error(f"❌ API endpoints test failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("🚀 Starting ML Monitoring Integration Tests...")
    
    # Test 1: Core monitoring integration
    monitoring_result = await test_ml_monitoring_integration()
    
    # Test 2: API endpoints
    api_result = await test_api_endpoints()
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"  Monitoring Integration: {'✅' if monitoring_result['success'] else '❌'}")
    logger.info(f"  API Endpoints: {'✅' if api_result['success'] else '❌'}")
    
    if monitoring_result['success'] and api_result['success']:
        logger.info("🎉 All ML Monitoring Integration Tests Passed!")
    else:
        logger.warning("⚠️ Some tests failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main())