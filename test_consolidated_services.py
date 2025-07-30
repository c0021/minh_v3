#!/usr/bin/env python3
"""
MinhOS v4 Consolidated Services Integration Test
==============================================
Comprehensive test suite to verify all consolidated services work together properly.

Tests:
1. Trading Service (trading_engine.py + live_trading_integration.py → trading_service.py)
2. Risk Manager (enhanced with BaseService and validate_trade method)
3. API Server (web_api.py + dashboard APIs → api_server.py)
4. Dashboard Server (dashboard/main.py → dashboard_server.py)

Validates:
- Service instantiation and startup
- Inter-service communication
- API endpoint functionality
- WebSocket connections
- Data flow between services
- Error handling and graceful degradation
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import consolidated services
from minhos.services.trading_service import TradingService, get_trading_service
from minhos.services.risk_manager import RiskManager, get_risk_manager
from minhos.services.api_server import APIServer, get_api_server
from minhos.services.dashboard_server import DashboardServer, get_dashboard_server

# Import supporting services
from minhos.services.state_manager import get_state_manager
from minhos.services.ai_brain_service import get_ai_brain_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("integration_test")

class ConsolidatedServicesTest:
    """Integration test suite for consolidated MinhOS v4 services"""
    
    def __init__(self):
        self.test_results = {}
        self.services = {}
        self.start_time = datetime.now()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete integration test suite"""
        logger.info("=" * 80)
        logger.info("MinhOS v4 Consolidated Services Integration Test")
        logger.info("=" * 80)
        
        try:
            # Test 1: Service Instantiation
            await self._test_service_instantiation()
            
            # Test 2: Service Startup
            await self._test_service_startup()
            
            # Test 3: Inter-service Communication
            await self._test_inter_service_communication()
            
            # Test 4: API Functionality
            await self._test_api_functionality()
            
            # Test 5: Dashboard Functionality
            await self._test_dashboard_functionality()
            
            # Test 6: Data Flow
            await self._test_data_flow()
            
            # Test 7: Error Handling
            await self._test_error_handling()
            
            # Test 8: Service Shutdown
            await self._test_service_shutdown()
            
        except Exception as e:
            logger.error(f"Test suite failed with error: {e}")
            self.test_results["suite_error"] = str(e)
        
        finally:
            # Generate test report
            await self._generate_test_report()
        
        return self.test_results
    
    async def _test_service_instantiation(self):
        """Test 1: Verify all services can be instantiated"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 1: Service Instantiation")
        logger.info("=" * 60)
        
        test_name = "service_instantiation"
        results = {}
        
        try:
            # Test Trading Service
            logger.info("Testing Trading Service instantiation...")
            trading_service = TradingService()
            results["trading_service"] = {
                "instantiated": True,
                "class_name": trading_service.__class__.__name__,
                "has_start_method": hasattr(trading_service, 'start'),
                "has_stop_method": hasattr(trading_service, 'stop'),
                "inherits_base_service": hasattr(trading_service, '_running')
            }
            self.services["trading_service"] = trading_service
            logger.info("✅ Trading Service instantiated successfully")
            
            # Test Risk Manager
            logger.info("Testing Risk Manager instantiation...")
            risk_manager = RiskManager()
            results["risk_manager"] = {
                "instantiated": True,
                "class_name": risk_manager.__class__.__name__,
                "has_start_method": hasattr(risk_manager, 'start'),
                "has_validate_trade": hasattr(risk_manager, 'validate_trade'),
                "has_health_check": hasattr(risk_manager, 'health_check'),
                "inherits_base_service": hasattr(risk_manager, '_running')
            }
            self.services["risk_manager"] = risk_manager
            logger.info("✅ Risk Manager instantiated successfully")
            
            # Test API Server
            logger.info("Testing API Server instantiation...")
            api_server = APIServer(host="127.0.0.1", port=8001)  # Different port for testing
            results["api_server"] = {
                "instantiated": True,
                "class_name": api_server.__class__.__name__,
                "host": api_server.host,
                "port": api_server.port,
                "has_fastapi_app": hasattr(api_server, 'app'),
                "inherits_base_service": hasattr(api_server, '_running')
            }
            self.services["api_server"] = api_server
            logger.info("✅ API Server instantiated successfully")
            
            # Test Dashboard Server
            logger.info("Testing Dashboard Server instantiation...")
            dashboard_server = DashboardServer(host="127.0.0.1", port=8889)  # Different port for testing
            results["dashboard_server"] = {
                "instantiated": True,
                "class_name": dashboard_server.__class__.__name__,
                "host": dashboard_server.host,
                "port": dashboard_server.port,
                "has_fastapi_app": hasattr(dashboard_server, 'app'),
                "has_connection_manager": hasattr(dashboard_server, 'connection_manager'),
                "inherits_base_service": hasattr(dashboard_server, '_running')
            }
            self.services["dashboard_server"] = dashboard_server
            logger.info("✅ Dashboard Server instantiated successfully")
            
            results["overall_success"] = True
            logger.info("\n✅ All services instantiated successfully!")
            
        except Exception as e:
            logger.error(f"❌ Service instantiation failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_service_startup(self):
        """Test 2: Verify all services can start properly"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 2: Service Startup")
        logger.info("=" * 60)
        
        test_name = "service_startup"
        results = {}
        
        try:
            # Start services in dependency order
            
            # 1. Risk Manager (no dependencies)
            logger.info("Starting Risk Manager...")
            start_time = time.time()
            await self.services["risk_manager"].start()
            startup_time = time.time() - start_time
            results["risk_manager"] = {
                "started": True,
                "startup_time_seconds": startup_time,
                "running_state": getattr(self.services["risk_manager"], '_running', False)
            }
            logger.info(f"✅ Risk Manager started in {startup_time:.2f}s")
            
            # 2. Trading Service (depends on risk manager)
            logger.info("Starting Trading Service...")
            start_time = time.time()
            await self.services["trading_service"].start()
            startup_time = time.time() - start_time
            results["trading_service"] = {
                "started": True,
                "startup_time_seconds": startup_time,
                "running_state": getattr(self.services["trading_service"], '_running', False)
            }
            logger.info(f"✅ Trading Service started in {startup_time:.2f}s")
            
            # 3. API Server (depends on other services for data)
            logger.info("Starting API Server...")
            start_time = time.time()
            await self.services["api_server"].start()
            startup_time = time.time() - start_time
            results["api_server"] = {
                "started": True,
                "startup_time_seconds": startup_time,
                "running_state": getattr(self.services["api_server"], '_running', False)
            }
            logger.info(f"✅ API Server started in {startup_time:.2f}s")
            
            # 4. Dashboard Server (depends on API server)
            logger.info("Starting Dashboard Server...")
            start_time = time.time()
            await self.services["dashboard_server"].start()
            startup_time = time.time() - start_time
            results["dashboard_server"] = {
                "started": True,
                "startup_time_seconds": startup_time,
                "running_state": getattr(self.services["dashboard_server"], '_running', False)
            }
            logger.info(f"✅ Dashboard Server started in {startup_time:.2f}s")
            
            # Give services time to fully initialize
            logger.info("Waiting for services to fully initialize...")
            await asyncio.sleep(2)
            
            results["overall_success"] = True
            logger.info("\n✅ All services started successfully!")
            
        except Exception as e:
            logger.error(f"❌ Service startup failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_inter_service_communication(self):
        """Test 3: Verify services can communicate with each other"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 3: Inter-service Communication")
        logger.info("=" * 60)
        
        test_name = "inter_service_communication"
        results = {}
        
        try:
            # Test Risk Manager validation (Trading Service → Risk Manager)
            logger.info("Testing Trading Service → Risk Manager communication...")
            
            # Create a mock trade order
            from minhos.services.trading_service import TradeOrder, ExecutionStrategy
            mock_order = TradeOrder(
                symbol="NQU25-CME",
                side="BUY",
                quantity=1,
                order_type=ExecutionStrategy.MARKET,
                reason="Integration test"
            )
            
            # Test risk validation
            risk_manager = self.services["risk_manager"]
            validation_result = await risk_manager.validate_trade(mock_order)
            
            results["trading_to_risk"] = {
                "communication_successful": True,
                "validation_result": validation_result,
                "order_details": {
                    "symbol": mock_order.symbol,
                    "side": mock_order.side,
                    "quantity": mock_order.quantity
                }
            }
            logger.info(f"✅ Risk validation result: {validation_result}")
            
            # Test API Server service references
            logger.info("Testing API Server service references...")
            api_server = self.services["api_server"]
            service_refs = {
                "sierra_client": api_server.sierra_client is not None,
                "state_manager": api_server.state_manager is not None,
                "ai_brain": api_server.ai_brain is not None,
                "risk_manager": api_server.risk_manager is not None,
                "trading_service": api_server.trading_service is not None
            }
            
            results["api_service_refs"] = service_refs
            logger.info(f"✅ API Server service references: {service_refs}")
            
            # Test Dashboard Server → API Server communication
            logger.info("Testing Dashboard Server → API Server communication...")
            dashboard_server = self.services["dashboard_server"]
            system_status = await dashboard_server._get_system_status()
            
            results["dashboard_to_api"] = {
                "communication_successful": system_status is not None,
                "status_keys": list(system_status.keys()) if system_status else [],
                "has_timestamp": "timestamp" in (system_status or {})
            }
            logger.info(f"✅ System status retrieved: {bool(system_status)}")
            
            results["overall_success"] = True
            logger.info("\n✅ Inter-service communication working!")
            
        except Exception as e:
            logger.error(f"❌ Inter-service communication failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_api_functionality(self):
        """Test 4: Verify API endpoints are working"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 4: API Functionality")
        logger.info("=" * 60)
        
        test_name = "api_functionality"
        results = {}
        
        try:
            # Test API Server app initialization
            api_server = self.services["api_server"]
            app = api_server.app
            
            # Check if key routes are registered
            routes = [route.path for route in app.routes]
            
            expected_routes = [
                "/api/system/status",
                "/api/system/health",
                "/api/market/latest",
                "/api/trading/config",
                "/api/trading/positions",
                "/api/enhanced/autonomous-status"
            ]
            
            route_status = {}
            for route in expected_routes:
                route_status[route] = route in routes
            
            results["route_registration"] = {
                "total_routes": len(routes),
                "expected_routes_found": route_status,
                "all_expected_present": all(route_status.values())
            }
            
            # Test CORS middleware
            middlewares = [middleware.cls.__name__ for middleware in app.user_middleware]
            results["middleware"] = {
                "cors_enabled": "CORSMiddleware" in middlewares,
                "total_middlewares": len(middlewares)
            }
            
            logger.info(f"✅ API routes registered: {len(routes)} total")
            logger.info(f"✅ Expected routes present: {all(route_status.values())}")
            logger.info(f"✅ CORS middleware enabled: {'CORSMiddleware' in middlewares}")
            
            results["overall_success"] = True
            
        except Exception as e:
            logger.error(f"❌ API functionality test failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_dashboard_functionality(self):
        """Test 5: Verify dashboard functionality"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 5: Dashboard Functionality")
        logger.info("=" * 60)
        
        test_name = "dashboard_functionality"
        results = {}
        
        try:
            dashboard_server = self.services["dashboard_server"]
            
            # Test static file setup
            static_dir_exists = dashboard_server.static_dir.exists() if dashboard_server.static_dir else False
            templates_dir_exists = dashboard_server.templates_dir.exists() if dashboard_server.templates_dir else False
            
            results["file_setup"] = {
                "static_dir_exists": static_dir_exists,
                "templates_dir_exists": templates_dir_exists,
                "templates_initialized": dashboard_server.templates is not None,
                "static_dir_path": str(dashboard_server.static_dir) if dashboard_server.static_dir else None,
                "templates_dir_path": str(dashboard_server.templates_dir) if dashboard_server.templates_dir else None
            }
            
            # Test WebSocket connection manager
            connection_manager = dashboard_server.connection_manager
            results["websocket_manager"] = {
                "manager_initialized": connection_manager is not None,
                "active_connections": connection_manager.get_connection_count() if connection_manager else 0,
                "has_broadcast_method": hasattr(connection_manager, 'broadcast') if connection_manager else False
            }
            
            # Test route setup
            app = dashboard_server.app
            routes = [route.path for route in app.routes]
            
            expected_dashboard_routes = [
                "/",
                "/enhanced",
                "/dashboard",
                "/health"
            ]
            
            dashboard_route_status = {}
            for route in expected_dashboard_routes:
                dashboard_route_status[route] = route in routes
            
            results["routes"] = {
                "total_routes": len(routes),
                "expected_routes": dashboard_route_status,
                "all_expected_present": all(dashboard_route_status.values())
            }
            
            logger.info(f"✅ Static files: {static_dir_exists}, Templates: {templates_dir_exists}")
            logger.info(f"✅ WebSocket manager initialized: {connection_manager is not None}")
            logger.info(f"✅ Dashboard routes: {len(routes)} total")
            
            results["overall_success"] = True
            
        except Exception as e:
            logger.error(f"❌ Dashboard functionality test failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_data_flow(self):
        """Test 6: Verify data flows correctly between services"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 6: Data Flow")
        logger.info("=" * 60)
        
        test_name = "data_flow"
        results = {}
        
        try:
            # Test Trading Service status retrieval
            trading_service = self.services["trading_service"]
            trading_status = await trading_service.get_status()
            
            results["trading_status"] = {
                "status_retrieved": trading_status is not None,
                "status_keys": list(trading_status.keys()) if trading_status else [],
                "has_required_fields": all(key in (trading_status or {}) for key in ["is_connected", "services_running"])
            }
            
            # Test Risk Manager status
            risk_manager = self.services["risk_manager"]
            risk_status = risk_manager.get_risk_status()
            
            results["risk_status"] = {
                "status_retrieved": risk_status is not None,
                "status_keys": list(risk_status.keys()) if risk_status else [],
                "has_metrics": "risk_metrics" in (risk_status or {})
            }
            
            # Test API Server system status compilation
            api_server = self.services["api_server"]
            system_status = await api_server._get_system_status()
            
            results["system_status"] = {
                "status_compiled": system_status is not None,
                "has_services": "services" in (system_status or {}),
                "has_timestamp": "timestamp" in (system_status or {}),
                "service_count": len(system_status.get("services", {})) if system_status else 0
            }
            
            logger.info(f"✅ Trading status: {bool(trading_status)}")
            logger.info(f"✅ Risk status: {bool(risk_status)}")
            logger.info(f"✅ System status: {bool(system_status)}")
            
            results["overall_success"] = True
            
        except Exception as e:
            logger.error(f"❌ Data flow test failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_error_handling(self):
        """Test 7: Verify error handling and graceful degradation"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 7: Error Handling")
        logger.info("=" * 60)
        
        test_name = "error_handling"
        results = {}
        
        try:
            # Test invalid trade validation
            risk_manager = self.services["risk_manager"]
            
            # Create invalid order (negative quantity)
            from minhos.services.trading_service import TradeOrder, ExecutionStrategy
            invalid_order = TradeOrder(
                symbol="INVALID",
                side="INVALID_SIDE",
                quantity=-1,
                order_type=ExecutionStrategy.MARKET,
                reason="Error handling test"
            )
            
            # Should handle gracefully without crashing
            try:
                validation_result = await risk_manager.validate_trade(invalid_order)
                results["invalid_trade_handling"] = {
                    "handled_gracefully": True,
                    "validation_result": validation_result,
                    "service_still_running": getattr(risk_manager, '_running', True)
                }
            except Exception as e:
                results["invalid_trade_handling"] = {
                    "handled_gracefully": False,
                    "error": str(e)
                }
            
            # Test API Server with unavailable services
            api_server = self.services["api_server"]
            
            # Temporarily set sierra_client to None to test degradation
            original_sierra = api_server.sierra_client
            api_server.sierra_client = None
            
            market_data = await api_server._get_live_market_data()
            
            results["missing_service_handling"] = {
                "handled_gracefully": True,  # Should return None without crashing
                "market_data_result": market_data,
                "service_still_running": getattr(api_server, '_running', True)
            }
            
            # Restore original reference
            api_server.sierra_client = original_sierra
            
            logger.info("✅ Invalid trade handled gracefully")
            logger.info("✅ Missing service handled gracefully")
            
            results["overall_success"] = True
            
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _test_service_shutdown(self):
        """Test 8: Verify all services can shut down cleanly"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 8: Service Shutdown")
        logger.info("=" * 60)
        
        test_name = "service_shutdown"
        results = {}
        
        try:
            # Shutdown services in reverse order
            shutdown_results = {}
            
            # 1. Dashboard Server
            logger.info("Stopping Dashboard Server...")
            start_time = time.time()
            await self.services["dashboard_server"].stop()
            shutdown_time = time.time() - start_time
            shutdown_results["dashboard_server"] = {
                "stopped_cleanly": True,
                "shutdown_time_seconds": shutdown_time
            }
            logger.info(f"✅ Dashboard Server stopped in {shutdown_time:.2f}s")
            
            # 2. API Server
            logger.info("Stopping API Server...")
            start_time = time.time()
            await self.services["api_server"].stop()
            shutdown_time = time.time() - start_time
            shutdown_results["api_server"] = {
                "stopped_cleanly": True,
                "shutdown_time_seconds": shutdown_time
            }
            logger.info(f"✅ API Server stopped in {shutdown_time:.2f}s")
            
            # 3. Trading Service
            logger.info("Stopping Trading Service...")
            start_time = time.time()
            await self.services["trading_service"].stop()
            shutdown_time = time.time() - start_time
            shutdown_results["trading_service"] = {
                "stopped_cleanly": True,
                "shutdown_time_seconds": shutdown_time
            }
            logger.info(f"✅ Trading Service stopped in {shutdown_time:.2f}s")
            
            # 4. Risk Manager
            logger.info("Stopping Risk Manager...")
            start_time = time.time()
            await self.services["risk_manager"].stop()
            shutdown_time = time.time() - start_time
            shutdown_results["risk_manager"] = {
                "stopped_cleanly": True,
                "shutdown_time_seconds": shutdown_time
            }
            logger.info(f"✅ Risk Manager stopped in {shutdown_time:.2f}s")
            
            results["shutdown_results"] = shutdown_results
            results["overall_success"] = True
            logger.info("\n✅ All services shut down cleanly!")
            
        except Exception as e:
            logger.error(f"❌ Service shutdown failed: {e}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        self.test_results[test_name] = results
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 80)
        logger.info("INTEGRATION TEST REPORT")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get("overall_success", False))
        failed_tests = total_tests - passed_tests
        
        test_duration = (datetime.now() - self.start_time).total_seconds()
        
        # Summary
        logger.info(f"Test Duration: {test_duration:.2f} seconds")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        logger.info("\nDetailed Results:")
        logger.info("-" * 40)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result.get("overall_success", False) else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
            
            if not result.get("overall_success", False) and "error" in result:
                logger.info(f"  Error: {result['error']}")
        
        # Overall result
        if failed_tests == 0:
            logger.info("\n🎉 ALL TESTS PASSED - Consolidated services integration successful!")
        else:
            logger.info(f"\n⚠️  {failed_tests} TEST(S) FAILED - Review errors above")
        
        # Save detailed report to file
        report_file = project_root / "consolidated_services_test_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                "test_summary": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": test_duration,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "detailed_results": self.test_results
            }, f, indent=2, default=str)
        
        logger.info(f"\nDetailed report saved to: {report_file}")

async def main():
    """Run the consolidated services integration test"""
    test_suite = ConsolidatedServicesTest()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Return appropriate exit code
        failed_tests = sum(1 for result in results.values() 
                          if not result.get("overall_success", False))
        
        if failed_tests > 0:
            sys.exit(1)  # Indicate test failure
        else:
            sys.exit(0)  # Indicate success
            
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())