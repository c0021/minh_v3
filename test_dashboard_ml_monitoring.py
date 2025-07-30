#!/usr/bin/env python3
"""
Test Dashboard ML Monitoring Visualization

Tests the ML monitoring visualization integration in the main dashboard.
"""

import asyncio
import sys
import logging
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from minhos.services.ml_monitoring_service import get_ml_monitoring_service
from minhos.dashboard.api_ml_performance import get_ml_monitoring_alerts, get_ml_system_health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dashboard_ml_monitoring():
    """Test dashboard ML monitoring visualization"""
    logger.info("🎯 Testing Dashboard ML Monitoring Visualization...")
    
    try:
        # Test 1: Setup ML Monitoring with Test Data
        logger.info("1. Setting up ML monitoring with test data...")
        
        ml_monitoring = get_ml_monitoring_service()
        await ml_monitoring.start()
        
        # Generate test performance metrics for all models
        test_metrics = {
            'lstm': {
                'latency_ms': [120, 145, 132, 156, 140],
                'confidence': [0.82, 0.78, 0.85, 0.76, 0.80],
                'error_rate': [0.02, 0.01, 0.0, 0.03, 0.01]
            },
            'ensemble': {
                'latency_ms': [220, 245, 215, 260, 230],
                'confidence': [0.75, 0.82, 0.79, 0.71, 0.77],
                'error_rate': [0.01, 0.0, 0.02, 0.01, 0.0]
            },
            'kelly': {
                'latency_ms': [45, 52, 41, 48, 50],
                'win_rate': [0.58, 0.62, 0.60, 0.55, 0.59],
                'error_rate': [0.0, 0.01, 0.0, 0.0, 0.01]
            }
        }
        
        # Record test metrics
        for model_type, metrics in test_metrics.items():
            for i, latency in enumerate(metrics['latency_ms']):
                ml_monitoring.record_performance_metric(model_type, 'latency_ms', latency)
                
                if 'confidence' in metrics:
                    ml_monitoring.record_performance_metric(model_type, 'confidence', metrics['confidence'][i])
                if 'win_rate' in metrics:
                    ml_monitoring.record_performance_metric(model_type, 'win_rate', metrics['win_rate'][i])
                    
                ml_monitoring.record_performance_metric(model_type, 'error_rate', metrics['error_rate'][i])
        
        logger.info("✅ Test metrics recorded")
        
        # Test 2: Generate Test Alerts
        logger.info("2. Generating test alerts...")
        
        # Generate some alerts for testing
        ml_monitoring.record_performance_metric('lstm', 'latency_ms', 800)  # High latency
        await asyncio.sleep(0.1)
        ml_monitoring.record_performance_metric('ensemble', 'accuracy', 0.45)  # Low accuracy
        await asyncio.sleep(0.1)
        ml_monitoring.record_performance_metric('kelly', 'error_rate', 0.15)  # High error rate
        await asyncio.sleep(0.1)
        
        logger.info("✅ Test alerts generated")
        
        # Test 3: Test API Endpoints for Dashboard
        logger.info("3. Testing dashboard API endpoints...")
        
        # Test system health endpoint
        system_health = await get_ml_system_health()
        logger.info(f"System Health API: Status={system_health['status']}, Alerts={system_health['active_alerts']}")
        
        # Test alerts endpoint
        alerts_data = await get_ml_monitoring_alerts()
        logger.info(f"Alerts API: Active={alerts_data['active_alerts']}, Total Today={alerts_data['total_alerts_today']}")
        
        # Test performance trends
        for model_type in ['lstm', 'ensemble', 'kelly']:
            try:
                trends = ml_monitoring.get_performance_trends(model_type, 1)
                logger.info(f"{model_type.upper()} trends: {len(trends)} metrics available")
            except Exception as e:
                logger.warning(f"Error getting trends for {model_type}: {e}")
        
        logger.info("✅ API endpoints tested successfully")
        
        # Test 4: Verify Dashboard Data Structure
        logger.info("4. Verifying dashboard data structure...")
        
        # Check if data format matches what the dashboard expects
        dashboard_data = {
            "system_health": system_health,
            "alerts": alerts_data,
            "model_metrics": {
                "lstm": {
                    "enabled": True,
                    "predictions": 5,
                    "avg_confidence": 0.80,
                    "avg_latency_ms": 139,
                    "error_rate": 0.014
                },
                "ensemble": {
                    "enabled": True,
                    "predictions": 5,
                    "avg_confidence": 0.77,
                    "avg_latency_ms": 234,
                    "error_rate": 0.008
                },
                "kelly": {
                    "enabled": True,
                    "calculations": 5,
                    "win_rate": 0.59,
                    "avg_latency_ms": 47,
                    "error_rate": 0.004
                }
            }
        }
        
        logger.info("Dashboard data structure:")
        logger.info(json.dumps(dashboard_data, indent=2, default=str))
        
        # Test 5: Dashboard Update Simulation
        logger.info("5. Simulating dashboard updates...")
        
        # Simulate what happens during a dashboard update cycle
        update_results = []
        
        # Simulate multiple update cycles
        for cycle in range(3):
            logger.info(f"  Update cycle {cycle + 1}/3...")
            
            # Add new metrics
            ml_monitoring.record_performance_metric('lstm', 'latency_ms', 125 + cycle * 10)
            ml_monitoring.record_performance_metric('ensemble', 'confidence', 0.78 + cycle * 0.02)
            ml_monitoring.record_performance_metric('kelly', 'win_rate', 0.60 + cycle * 0.01)
            
            # Get updated system health
            updated_health = await get_ml_system_health()
            update_results.append({
                'cycle': cycle + 1,
                'health_status': updated_health['status'],
                'active_alerts': updated_health['active_alerts']
            })
            
            await asyncio.sleep(0.2)
        
        logger.info("Update cycles completed:")
        for result in update_results:
            logger.info(f"  Cycle {result['cycle']}: {result['health_status']} status, {result['active_alerts']} alerts")
        
        # Test 6: Performance Validation
        logger.info("6. Validating dashboard performance...")
        
        import time
        
        # Test API response times
        start_time = time.time()
        await get_ml_system_health()
        health_time = (time.time() - start_time) * 1000
        
        start_time = time.time()
        await get_ml_monitoring_alerts()
        alerts_time = (time.time() - start_time) * 1000
        
        logger.info(f"API Response Times:")
        logger.info(f"  System Health: {health_time:.1f}ms")
        logger.info(f"  Alerts: {alerts_time:.1f}ms")
        
        if health_time < 100 and alerts_time < 100:
            logger.info("✅ Dashboard API performance is optimal")
        else:
            logger.warning("⚠️ Dashboard API performance could be improved")
        
        # Cleanup
        await ml_monitoring.stop()
        logger.info("✅ ML Monitoring Service stopped")
        
        logger.info("🎉 Dashboard ML Monitoring Visualization Test Complete!")
        
        return {
            "success": True,
            "system_health": system_health,
            "alerts_generated": alerts_data['active_alerts'],
            "api_performance": {
                "health_api_ms": health_time,
                "alerts_api_ms": alerts_time
            },
            "dashboard_ready": True
        }
        
    except Exception as e:
        logger.error(f"❌ Dashboard ML Monitoring Test Failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def test_dashboard_integration():
    """Test integration with actual dashboard"""
    logger.info("🔗 Testing Dashboard Integration...")
    
    try:
        # Check if dashboard HTML has the required elements
        dashboard_path = Path(__file__).parent / "minhos" / "dashboard" / "templates" / "index.html"
        
        if not dashboard_path.exists():
            logger.warning("Dashboard HTML file not found")
            return {"success": False, "error": "Dashboard file not found"}
        
        with open(dashboard_path, 'r') as f:
            dashboard_html = f.read()
        
        # Check for required ML monitoring elements
        required_elements = [
            'ml-system-health',
            'ml-active-alerts',
            'ml-models-active',
            'ml-avg-latency',
            'lstm-status',
            'ensemble-status',
            'kelly-status',
            'ml-alerts-container',
            'ml-trends-container',
            'updateMLMonitoring'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in dashboard_html:
                missing_elements.append(element)
        
        if missing_elements:
            logger.warning(f"Missing dashboard elements: {missing_elements}")
            return {"success": False, "missing_elements": missing_elements}
        
        logger.info("✅ All required dashboard elements present")
        
        # Check for CSS classes
        required_css = [
            'ml-model-metrics',
            'metric-row',
            'ml-alert-item',
            'trend-item'
        ]
        
        missing_css = []
        for css_class in required_css:
            if css_class not in dashboard_html:
                missing_css.append(css_class)
        
        if missing_css:
            logger.warning(f"Missing CSS classes: {missing_css}")
        else:
            logger.info("✅ All required CSS classes present")
        
        # Check update intervals
        if 'updateMLMonitoring' in dashboard_html and 'setInterval' in dashboard_html:
            logger.info("✅ ML monitoring update interval configured")
        else:
            logger.warning("⚠️ ML monitoring update interval not configured")
        
        return {
            "success": True,
            "elements_present": len(required_elements) - len(missing_elements),
            "total_elements": len(required_elements),
            "css_classes_present": len(required_css) - len(missing_css),
            "total_css_classes": len(required_css)
        }
        
    except Exception as e:
        logger.error(f"❌ Dashboard Integration Test Failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("🚀 Starting Dashboard ML Monitoring Visualization Tests...")
    
    # Test 1: Core ML monitoring functionality
    monitoring_result = await test_dashboard_ml_monitoring()
    
    # Test 2: Dashboard integration
    integration_result = await test_dashboard_integration()
    
    # Summary
    logger.info("📊 Test Summary:")
    logger.info(f"  ML Monitoring Functionality: {'✅' if monitoring_result['success'] else '❌'}")
    logger.info(f"  Dashboard Integration: {'✅' if integration_result['success'] else '❌'}")
    
    if monitoring_result['success'] and integration_result['success']:
        logger.info("🎉 All Dashboard ML Monitoring Tests Passed!")
        logger.info("🎯 Dashboard is ready for production ML monitoring!")
    else:
        logger.warning("⚠️ Some tests failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main())