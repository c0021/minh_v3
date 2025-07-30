#!/usr/bin/env python3
"""
ML Performance Dashboard Test

Tests the ML Performance Dashboard API endpoints and functionality.
"""

import asyncio
import sys
import logging
import requests
import time
from typing import Dict, Any

# Add project root to path
sys.path.append('/home/colindo/Sync/minh_v4')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MLPerformanceDashboardTester:
    """Test ML Performance Dashboard functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_api_endpoint(self, endpoint: str, expected_keys: list = None) -> bool:
        """Test a single API endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in data]
                    if missing_keys:
                        logger.warning(f"Missing keys in {endpoint}: {missing_keys}")
                        return False
                
                logger.info(f"✅ {endpoint} - OK")
                return True
            else:
                logger.error(f"❌ {endpoint} - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {endpoint} - Error: {e}")
            return False
    
    def test_ml_status_endpoint(self) -> bool:
        """Test ML system status endpoint"""
        return self.test_api_endpoint(
            "/api/ml/status",
            expected_keys=['lstm_enabled', 'ensemble_enabled', 'kelly_enabled', 'system_health']
        )
    
    def test_current_performance_endpoint(self) -> bool:
        """Test current ML performance endpoint"""
        return self.test_api_endpoint(
            "/api/ml/performance/current",
            expected_keys=['timestamp', 'lstm', 'ensemble', 'kelly', 'system_metrics']
        )
    
    def test_model_accuracy_endpoint(self) -> bool:
        """Test model accuracy endpoint"""
        return self.test_api_endpoint(
            "/api/ml/models/accuracy",
            expected_keys=['timestamp', 'models']
        )
    
    def test_recent_predictions_endpoint(self) -> bool:
        """Test recent predictions endpoint"""
        return self.test_api_endpoint(
            "/api/ml/predictions/recent",
            expected_keys=['total_predictions', 'predictions', 'avg_confidence']
        )
    
    def test_performance_history_endpoint(self) -> bool:
        """Test performance history endpoint"""
        return self.test_api_endpoint(
            "/api/ml/performance/history?hours=24",
            expected_keys=['timeframe_hours', 'data_points', 'history']
        )
    
    def test_health_check_endpoint(self) -> bool:
        """Test ML health check endpoint"""
        return self.test_api_endpoint(
            "/api/ml/health",
            expected_keys=['timestamp', 'overall_status', 'components', 'healthy_components']
        )
    
    def test_dashboard_page(self) -> bool:
        """Test ML Performance Dashboard HTML page"""
        try:
            url = f"{self.base_url}/ml-performance"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Check for key elements in HTML
                required_elements = [
                    'ML Performance Dashboard',
                    'ml-performance-dashboard',
                    'ml-system-status',
                    'ml-current-performance',
                    'chart.js'
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in html_content:
                        missing_elements.append(element)
                
                if missing_elements:
                    logger.warning(f"Missing HTML elements: {missing_elements}")
                    return False
                
                logger.info("✅ ML Performance Dashboard page - OK")
                return True
            else:
                logger.error(f"❌ Dashboard page - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Dashboard page - Error: {e}")
            return False
    
    def test_detailed_api_responses(self) -> bool:
        """Test detailed API response content"""
        try:
            # Test ML status with detailed validation
            response = self.session.get(f"{self.base_url}/api/ml/status")
            if response.status_code == 200:
                data = response.json()
                
                # Validate data types and ranges
                if not isinstance(data.get('total_predictions'), int):
                    logger.error("total_predictions should be integer")
                    return False
                
                if not 0 <= data.get('avg_confidence', 0) <= 1:
                    logger.error("avg_confidence should be between 0 and 1")
                    return False
                
                if data.get('system_health') not in ['optimal', 'good', 'limited', 'disabled', 'critical']:
                    logger.error(f"Invalid system_health: {data.get('system_health')}")
                    return False
                
                logger.info("✅ Detailed API validation - OK")
                return True
            else:
                logger.error("Failed to get ML status for detailed validation")
                return False
                
        except Exception as e:
            logger.error(f"❌ Detailed API validation - Error: {e}")
            return False
    
    def run_performance_test(self) -> Dict[str, float]:
        """Run performance test on API endpoints"""
        endpoints = [
            "/api/ml/status",
            "/api/ml/performance/current",
            "/api/ml/models/accuracy",
            "/api/ml/predictions/recent",
            "/api/ml/health"
        ]
        
        performance_results = {}
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                performance_results[endpoint] = latency
                
                status = "✅" if response.status_code == 200 else "❌"
                logger.info(f"{status} {endpoint} - {latency:.1f}ms")
                
            except Exception as e:
                logger.error(f"❌ {endpoint} - Performance test failed: {e}")
                performance_results[endpoint] = -1
        
        return performance_results
    
    def run_comprehensive_test(self) -> bool:
        """Run comprehensive ML Performance Dashboard test"""
        logger.info("🚀 Starting ML Performance Dashboard Test")
        logger.info("=" * 60)
        
        test_results = []
        
        # Test individual endpoints
        tests = [
            ("ML Status Endpoint", self.test_ml_status_endpoint),
            ("Current Performance Endpoint", self.test_current_performance_endpoint),
            ("Model Accuracy Endpoint", self.test_model_accuracy_endpoint),
            ("Recent Predictions Endpoint", self.test_recent_predictions_endpoint),
            ("Performance History Endpoint", self.test_performance_history_endpoint),
            ("Health Check Endpoint", self.test_health_check_endpoint),
            ("Dashboard HTML Page", self.test_dashboard_page),
            ("Detailed API Validation", self.test_detailed_api_responses)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📊 Testing {test_name}...")
            try:
                result = test_func()
                test_results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"{status}: {test_name}")
            except Exception as e:
                test_results.append((test_name, False))
                logger.error(f"❌ FAILED: {test_name} - {e}")
        
        # Performance test
        logger.info(f"\n⚡ Running Performance Test...")
        performance_results = self.run_performance_test()
        
        avg_latency = sum(lat for lat in performance_results.values() if lat > 0) / len([lat for lat in performance_results.values() if lat > 0])
        logger.info(f"Average API latency: {avg_latency:.1f}ms")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📈 ML PERFORMANCE DASHBOARD TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        
        logger.info(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        logger.info(f"Performance: {avg_latency:.1f}ms average latency")
        
        if passed == total and avg_latency < 1000:  # All tests pass and latency < 1 second
            logger.info("🎉 ML Performance Dashboard: FULLY OPERATIONAL!")
            return True
        else:
            logger.warning("⚠️ Some tests failed or performance is slow")
            return False

def main():
    """Main test execution"""
    tester = MLPerformanceDashboardTester()
    
    # Check if dashboard is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code != 200:
            logger.error("❌ Dashboard not running on localhost:8001")
            logger.info("Please start the dashboard with: python -m minhos.dashboard.main")
            return 1
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to dashboard on localhost:8001")
        logger.info("Please start the dashboard with: python -m minhos.dashboard.main")
        return 1
    
    # Run tests
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)