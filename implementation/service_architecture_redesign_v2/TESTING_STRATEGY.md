# Testing Strategy - Service Architecture Redesign

**Document Version**: 1.0  
**Created**: 2025-07-25  
**Last Updated**: 2025-07-25

## Overview

This document outlines the comprehensive testing strategy for the MinhOS service architecture redesign. The goal is to ensure zero downtime, no feature regression, and improved system reliability while migrating from tightly-coupled services to an event-driven architecture.

## Testing Philosophy

### Core Principles
1. **Test-First Migration**: Write tests before implementing changes
2. **Continuous Validation**: Test at every stage of migration
3. **Real-World Scenarios**: Tests reflect actual trading conditions
4. **Performance Focus**: Ensure no degradation in system performance
5. **Fault Tolerance**: Validate that failures don't cascade

### Testing Pyramid

```
                    ┌─────────────────┐
                    │   End-to-End    │  ← Few, critical path tests
                    │   Integration   │
                    │     Tests       │
                    └─────────────────┘
                  ┌───────────────────────┐
                  │    Integration        │  ← Service interaction tests
                  │      Tests            │
                  └───────────────────────┘
              ┌───────────────────────────────┐
              │        Unit Tests             │  ← Many, fast, isolated tests
              └───────────────────────────────┘
```

## Test Categories

## 1. Unit Tests

### 1.1 Core Infrastructure Tests

**Service Contracts Tests**
```python
# tests/core/test_service_contracts.py
import pytest
from datetime import datetime
from minhos.core.service_contracts import IService, ServiceHealth, HealthStatus

class MockCompliantService(IService):
    async def start(self): pass
    async def stop(self): pass
    async def health_check(self): 
        return ServiceHealth(
            service_name="mock",
            status=HealthStatus.HEALTHY,
            dependencies=[],
            last_heartbeat=datetime.now(),
            errors=[]
        )
    def get_dependencies(self): return []
    def get_service_name(self): return "mock"

class MockNonCompliantService:
    pass

def test_service_health_creation():
    """Test ServiceHealth object creation and validation"""
    health = ServiceHealth(
        service_name="test_service",
        status=HealthStatus.HEALTHY,
        dependencies=["dependency1", "dependency2"],
        last_heartbeat=datetime.now(),
        errors=[]
    )
    
    assert health.service_name == "test_service"
    assert health.status == HealthStatus.HEALTHY
    assert len(health.dependencies) == 2
    assert health.metadata == {}

def test_service_contract_compliance():
    """Test that services properly implement IService contract"""
    compliant_service = MockCompliantService()
    assert isinstance(compliant_service, IService)
    
    non_compliant_service = MockNonCompliantService()
    assert not isinstance(non_compliant_service, IService)

@pytest.mark.asyncio
async def test_service_lifecycle():
    """Test service start/stop lifecycle"""
    service = MockCompliantService()
    
    # Test start
    await service.start()  # Should not raise
    
    # Test health check
    health = await service.health_check()
    assert isinstance(health, ServiceHealth)
    assert health.service_name == "mock"
    
    # Test stop
    await service.stop()  # Should not raise
```

**Event Bus Tests**
```python
# tests/core/test_event_bus.py
import pytest
import asyncio
from datetime import datetime
from minhos.core.event_bus import EventBus, Event, EventHandler

@pytest.mark.asyncio
async def test_event_publishing_and_subscription():
    """Test basic pub/sub functionality"""
    event_bus = EventBus()
    received_events = []
    
    def event_handler(event: Event):
        received_events.append(event)
    
    # Subscribe
    event_bus.subscribe("test.event", event_handler, "test_service")
    
    # Publish
    test_event = Event(
        type="test.event",
        data={"message": "hello world"},
        source_service="test_publisher"
    )
    
    await event_bus.publish(test_event)
    
    # Verify
    assert len(received_events) == 1
    assert received_events[0].type == "test.event"
    assert received_events[0].data["message"] == "hello world"

@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test event delivery to multiple subscribers"""
    event_bus = EventBus()
    received_by_service1 = []
    received_by_service2 = []
    
    event_bus.subscribe("broadcast.event", 
                       lambda e: received_by_service1.append(e), 
                       "service1")
    event_bus.subscribe("broadcast.event", 
                       lambda e: received_by_service2.append(e), 
                       "service2")
    
    test_event = Event(
        type="broadcast.event",
        data={"broadcast": True},
        source_service="broadcaster"
    )
    
    await event_bus.publish(test_event)
    
    assert len(received_by_service1) == 1
    assert len(received_by_service2) == 1
    assert received_by_service1[0].data["broadcast"] is True
    assert received_by_service2[0].data["broadcast"] is True

@pytest.mark.asyncio
async def test_event_handler_error_handling():
    """Test that handler errors don't break event delivery"""
    event_bus = EventBus()
    successful_deliveries = []
    
    def failing_handler(event: Event):
        raise Exception("Handler error")
    
    def successful_handler(event: Event):
        successful_deliveries.append(event)
    
    event_bus.subscribe("error.test", failing_handler, "failing_service")
    event_bus.subscribe("error.test", successful_handler, "successful_service")
    
    test_event = Event(
        type="error.test",
        data={"test": "error handling"},
        source_service="test"
    )
    
    # Should not raise exception
    await event_bus.publish(test_event)
    
    # Successful handler should still receive event
    assert len(successful_deliveries) == 1
    
    # Check stats show delivery failure
    stats = event_bus.get_stats()
    assert stats["delivery_failures"] > 0

@pytest.mark.asyncio
async def test_async_event_handlers():
    """Test async event handler support"""
    event_bus = EventBus()
    received_events = []
    
    async def async_handler(event: Event):
        await asyncio.sleep(0.01)  # Simulate async work
        received_events.append(event)
    
    event_bus.subscribe("async.event", async_handler, "async_service")
    
    test_event = Event(
        type="async.event",
        data={"async": True},
        source_service="test"
    )
    
    await event_bus.publish(test_event)
    
    assert len(received_events) == 1
    assert received_events[0].data["async"] is True

@pytest.mark.asyncio
async def test_event_retry_mechanism():
    """Test event delivery retry logic"""
    event_bus = EventBus()
    attempt_count = 0
    
    def flaky_handler(event: Event):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:  # Fail first 2 attempts
            raise Exception(f"Attempt {attempt_count} failed")
        # Succeed on 3rd attempt
    
    event_bus.subscribe("retry.test", flaky_handler, "flaky_service")
    
    test_event = Event(
        type="retry.test",
        data={"test": "retry"},
        source_service="test"
    )
    
    await event_bus.publish(test_event)
    
    # Should have attempted 3 times
    assert attempt_count == 3

def test_event_history():
    """Test event history tracking"""
    event_bus = EventBus(max_history=5)
    
    # Publish events
    for i in range(10):
        event = Event(
            type="history.test",
            data={"id": i},
            source_service="test"
        )
        asyncio.run(event_bus.publish(event))
    
    # Should only keep last 5 events
    recent_events = event_bus.get_recent_events(limit=10)
    assert len(recent_events) == 5
    
    # Should be most recent events (5-9)
    event_ids = [e.data["id"] for e in recent_events]
    assert event_ids == [5, 6, 7, 8, 9]
```

**Service Registry Tests**
```python
# tests/core/test_service_registry.py
import pytest
import asyncio
from minhos.core.service_registry import ServiceRegistry, ContractViolationError, ServiceUnavailableError
from minhos.core.service_contracts import IService, ServiceHealth, HealthStatus
from minhos.core.event_bus import EventBus

class MockService(IService):
    def __init__(self, name: str, dependencies: list = None):
        self.name = name
        self.dependencies = dependencies or []
        self.started = False
        self.health_status = HealthStatus.STOPPED
    
    async def start(self):
        self.started = True
        self.health_status = HealthStatus.HEALTHY
    
    async def stop(self):
        self.started = False
        self.health_status = HealthStatus.STOPPED
    
    async def health_check(self):
        return ServiceHealth(
            service_name=self.name,
            status=self.health_status,
            dependencies=self.dependencies,
            last_heartbeat=datetime.now(),
            errors=[]
        )
    
    def get_dependencies(self):
        return self.dependencies
    
    def get_service_name(self):
        return self.name

class InvalidService:
    """Service that doesn't implement IService"""
    pass

def test_service_registration():
    """Test basic service registration"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    service = MockService("test_service")
    registry.register("test_service", service, IService)
    
    retrieved_service = registry.get_service("test_service")
    assert retrieved_service == service

def test_contract_violation_detection():
    """Test that invalid services are rejected"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    invalid_service = InvalidService()
    
    with pytest.raises(ContractViolationError):
        registry.register("invalid", invalid_service, IService)

def test_service_name_mismatch_detection():
    """Test that service name mismatches are detected"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    service = MockService("actual_name")
    
    with pytest.raises(ServiceRegistryError):
        registry.register("different_name", service, IService)

@pytest.mark.asyncio
async def test_dependency_ordering():
    """Test that services start in correct dependency order"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create services with dependencies: C -> B -> A
    service_a = MockService("service_a")
    service_b = MockService("service_b", ["service_a"])
    service_c = MockService("service_c", ["service_b"])
    
    # Register in random order
    registry.register("service_c", service_c, IService)
    registry.register("service_a", service_a, IService)
    registry.register("service_b", service_b, IService)
    
    # Start all services
    await registry.start_all_services()
    
    # All should be started
    assert service_a.started
    assert service_b.started
    assert service_c.started

@pytest.mark.asyncio
async def test_circular_dependency_detection():
    """Test detection of circular dependencies"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create circular dependency: A -> B -> A
    service_a = MockService("service_a", ["service_b"])
    service_b = MockService("service_b", ["service_a"])
    
    registry.register("service_a", service_a, IService)
    
    with pytest.raises(ServiceRegistryError, match="Circular dependency"):
        registry.register("service_b", service_b, IService)

@pytest.mark.asyncio
async def test_missing_dependency_detection():
    """Test detection of missing dependencies"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Service depends on non-existent service
    service = MockService("service", ["non_existent_service"])
    
    with pytest.raises(ServiceRegistryError, match="unregistered service"):
        registry.register("service", service, IService)

@pytest.mark.asyncio
async def test_service_lifecycle_events():
    """Test that service lifecycle events are published"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    received_events = []
    event_bus.subscribe("service.started", 
                       lambda e: received_events.append(e), 
                       "test")
    
    service = MockService("test_service")
    registry.register("test_service", service, IService)
    
    await registry.start_service("test_service")
    
    # Should have received service started event
    assert len(received_events) == 1
    assert received_events[0].data["service_name"] == "test_service"
```

### 1.2 Service Migration Tests

**Market Data Service Tests**
```python
# tests/services/test_market_data_migration.py
import pytest
from minhos.services.market_data import MarketDataService
from minhos.core.service_contracts import IMarketDataProvider
from minhos.core.event_bus import EventBus, Event

@pytest.mark.asyncio
async def test_market_data_service_contract_compliance():
    """Test that MarketDataService implements IMarketDataProvider"""
    event_bus = EventBus()
    service = MarketDataService(event_bus)
    
    assert isinstance(service, IMarketDataProvider)
    assert hasattr(service, 'get_market_data')
    assert hasattr(service, 'get_all_market_data')

@pytest.mark.asyncio
async def test_market_data_event_publishing():
    """Test that market data updates are published as events"""
    event_bus = EventBus()
    service = MarketDataService(event_bus)
    
    received_events = []
    event_bus.subscribe("market_data.updated", 
                       lambda e: received_events.append(e), 
                       "test")
    
    # Simulate Sierra client data
    sierra_event = Event(
        type="sierra.market_data",
        data=MockMarketData("NQU25", 23500.0),
        source_service="sierra_client"
    )
    
    await service._on_sierra_data(sierra_event)
    
    # Should publish market data update
    assert len(received_events) == 1
    assert received_events[0].type == "market_data.updated"
    assert received_events[0].data.symbol == "NQU25"

@pytest.mark.asyncio
async def test_market_data_health_check():
    """Test market data service health monitoring"""
    event_bus = EventBus()
    service = MarketDataService(event_bus)
    
    # Initially should be healthy but with no data
    health = await service.health_check()
    assert health.service_name == "market_data"
    assert health.status == HealthStatus.DEGRADED  # No data
    assert "No market data received" in health.errors
    
    # Add some data
    service.latest_data["NQU25"] = MockMarketData("NQU25", 23500.0)
    
    health = await service.health_check()
    assert health.status == HealthStatus.HEALTHY
    assert len(health.errors) == 0
```

## 2. Integration Tests

### 2.1 Service Interaction Tests

**Event Flow Integration**
```python
# tests/integration/test_service_communication.py
import pytest
import asyncio
from minhos.core.service_registry import ServiceRegistry
from minhos.core.event_bus import EventBus
from minhos.services.market_data import MarketDataService
from minhos.services.ai_brain_service import AIBrainService
from minhos.services.trading_engine import TradingEngine

@pytest.mark.asyncio
async def test_market_data_to_ai_brain_flow():
    """Test event flow from market data to AI brain"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create and register services
    market_service = MarketDataService(event_bus)
    ai_service = AIBrainService(event_bus)
    
    registry.register("market_data", market_service, IMarketDataProvider)
    registry.register("ai_brain", ai_service, IAIBrainService)
    
    # Start services
    await registry.start_all_services()
    
    # Simulate market data update
    market_data = MockMarketData("NQU25", 23500.0)
    await event_bus.publish(Event(
        type="market_data.updated",
        data=market_data,
        source_service="market_data"
    ))
    
    # Give AI brain time to process
    await asyncio.sleep(0.1)
    
    # Verify AI brain received and processed data
    assert ai_service.last_market_data == market_data
    assert ai_service.analysis_count > 0
    
    await registry.stop_all_services()

@pytest.mark.asyncio
async def test_complete_trading_pipeline():
    """Test complete flow: Market Data -> AI -> Trading -> Risk"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create all services
    market_service = MarketDataService(event_bus)
    ai_service = AIBrainService(event_bus)
    trading_engine = TradingEngine(event_bus)
    risk_manager = RiskManager(event_bus)
    
    # Register services
    registry.register("market_data", market_service, IMarketDataProvider)
    registry.register("ai_brain", ai_service, IAIBrainService)
    registry.register("trading_engine", trading_engine, ITradingEngine)
    registry.register("risk_manager", risk_manager, IRiskManager)
    
    # Start system
    await registry.start_all_services()
    
    # Simulate market data
    market_data = MockMarketData("NQU25", 23500.0)
    await event_bus.publish(Event(
        type="market_data.updated",
        data=market_data,
        source_service="market_data"
    ))
    
    # Wait for processing pipeline
    await asyncio.sleep(0.5)
    
    # Verify complete flow
    assert ai_service.last_market_data == market_data
    if ai_service.generated_signal:
        assert trading_engine.received_signals > 0
        assert risk_manager.risk_checks_performed > 0
    
    await registry.stop_all_services()
```

### 2.2 Health Monitoring Integration

```python
# tests/integration/test_health_monitoring.py
import pytest
import asyncio
from minhos.core.health_monitor import HealthMonitor
from minhos.core.event_bus import EventBus

@pytest.mark.asyncio
async def test_health_monitoring_integration():
    """Test health monitoring with multiple services"""
    event_bus = EventBus()
    health_monitor = HealthMonitor(event_bus, check_interval=1)
    
    # Create services with different health states
    healthy_service = MockService("healthy", health_status=HealthStatus.HEALTHY)
    unhealthy_service = MockService("unhealthy", health_status=HealthStatus.UNHEALTHY)
    
    health_monitor.add_service(healthy_service)
    health_monitor.add_service(unhealthy_service)
    
    # Track health events
    health_events = []
    event_bus.subscribe("service.health_changed", 
                       lambda e: health_events.append(e), 
                       "test")
    
    # Start monitoring
    await health_monitor.start_monitoring()
    
    # Wait for health checks
    await asyncio.sleep(2)
    
    # Should have received health change events
    assert len(health_events) >= 2
    
    # Verify health status tracking
    healthy_status = health_monitor.get_service_health("healthy")
    unhealthy_status = health_monitor.get_service_health("unhealthy")
    
    assert healthy_status.status == HealthStatus.HEALTHY
    assert unhealthy_status.status == HealthStatus.UNHEALTHY
    
    await health_monitor.stop_monitoring()
```

### 2.3 Fault Tolerance Tests

```python
# tests/integration/test_fault_tolerance.py
import pytest
import asyncio
from minhos.core.service_registry import ServiceRegistry
from minhos.core.event_bus import EventBus

@pytest.mark.asyncio
async def test_service_failure_isolation():
    """Test that one service failure doesn't affect others"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create services
    stable_service = MockService("stable")
    failing_service = FailingMockService("failing")
    
    registry.register("stable", stable_service, IService)
    registry.register("failing", failing_service, IService)
    
    await registry.start_all_services()
    
    # Cause failing service to fail
    failing_service.cause_failure()
    
    # Stable service should still be operational
    await asyncio.sleep(0.1)
    
    stable_health = await stable_service.health_check()
    assert stable_health.status == HealthStatus.HEALTHY
    
    await registry.stop_all_services()

@pytest.mark.asyncio
async def test_event_delivery_resilience():
    """Test event delivery continues despite handler failures"""
    event_bus = EventBus()
    
    successful_deliveries = []
    
    def failing_handler(event):
        raise Exception("Handler failure")
    
    def successful_handler(event):
        successful_deliveries.append(event)
    
    event_bus.subscribe("test.event", failing_handler, "failing_handler")
    event_bus.subscribe("test.event", successful_handler, "successful_handler")
    
    # Publish event
    test_event = Event(
        type="test.event",
        data={"test": True},
        source_service="test"
    )
    
    await event_bus.publish(test_event)
    
    # Successful handler should still receive event
    assert len(successful_deliveries) == 1
    
    # Event bus should track the failure
    stats = event_bus.get_stats()
    assert stats["delivery_failures"] > 0
    assert stats["events_delivered"] > 0
```

## 3. Performance Tests

### 3.1 Event Bus Performance

```python
# tests/performance/test_event_bus_performance.py
import pytest
import asyncio
import time
from minhos.core.event_bus import EventBus, Event

@pytest.mark.asyncio
async def test_event_throughput():
    """Test event processing throughput"""
    event_bus = EventBus()
    processed_count = 0
    
    def fast_handler(event):
        nonlocal processed_count
        processed_count += 1
    
    event_bus.subscribe("perf.test", fast_handler, "perf_handler")
    
    # Measure throughput
    event_count = 1000
    start_time = time.time()
    
    for i in range(event_count):
        await event_bus.publish(Event(
            type="perf.test",
            data={"id": i},
            source_service="perf_test"
        ))
    
    end_time = time.time()
    
    throughput = event_count / (end_time - start_time)
    
    # Should handle at least 500 events/second
    assert throughput > 500
    assert processed_count == event_count

@pytest.mark.asyncio
async def test_concurrent_event_processing():
    """Test concurrent event processing performance"""
    event_bus = EventBus()
    processed_events = []
    
    async def async_handler(event):
        await asyncio.sleep(0.01)  # Simulate work
        processed_events.append(event)
    
    event_bus.subscribe("concurrent.test", async_handler, "async_handler")
    
    # Publish events concurrently
    event_count = 100
    start_time = time.time()
    
    tasks = []
    for i in range(event_count):
        event = Event(
            type="concurrent.test",
            data={"id": i},
            source_service="concurrent_test"
        )
        tasks.append(event_bus.publish(event))
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Should complete within reasonable time (concurrent processing)
    assert processing_time < 2.0  # Should be much faster than 100 * 0.01 = 1s
    assert len(processed_events) == event_count
```

### 3.2 Service Registry Performance

```python
# tests/performance/test_service_registry_performance.py
import pytest
import asyncio
import time
from minhos.core.service_registry import ServiceRegistry
from minhos.core.event_bus import EventBus

@pytest.mark.asyncio
async def test_service_startup_performance():
    """Test service startup time with many services"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create many services
    service_count = 50
    for i in range(service_count):
        service = MockService(f"service_{i}")
        registry.register(f"service_{i}", service, IService)
    
    # Measure startup time
    start_time = time.time()
    await registry.start_all_services()
    end_time = time.time()
    
    startup_time = end_time - start_time
    
    # Should start all services quickly
    assert startup_time < 5.0  # 5 seconds for 50 services
    
    # Verify all services started
    for i in range(service_count):
        service = registry.get_service(f"service_{i}")
        assert service.started

@pytest.mark.asyncio
async def test_service_lookup_performance():
    """Test service lookup performance"""
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Register many services
    service_count = 1000
    for i in range(service_count):
        service = MockService(f"service_{i}")
        registry.register(f"service_{i}", service, IService)
    
    # Measure lookup time
    start_time = time.time()
    
    for i in range(service_count):
        service = registry.get_service(f"service_{i}")
        assert service is not None
    
    end_time = time.time()
    lookup_time = end_time - start_time
    
    # Should be fast lookups
    assert lookup_time < 0.1  # 100ms for 1000 lookups
```

## 4. End-to-End Tests

### 4.1 Complete System Tests

```python
# tests/e2e/test_complete_system.py
import pytest
import asyncio
from minhos.main import initialize_complete_system

@pytest.mark.asyncio
async def test_full_system_startup():
    """Test complete system startup and shutdown"""
    # Initialize complete system
    registry, health_monitor, event_bus = await initialize_complete_system()
    
    # Verify all services are registered
    services = registry.list_services()
    expected_services = [
        "market_data", "state_manager", "sierra_client",
        "risk_manager", "ai_brain", "trading_engine"
    ]
    
    for service_name in expected_services:
        assert service_name in services
        assert services[service_name]["running"] is True
    
    # Verify health monitoring is active
    health_status = health_monitor.get_all_health_status()
    assert len(health_status) == len(expected_services)
    
    # Simulate market data flow
    market_data = MockMarketData("NQU25", 23500.0)
    await event_bus.publish(Event(
        type="market_data.updated",
        data=market_data,
        source_service="e2e_test"
    ))
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Verify system processed data
    ai_service = registry.get_service("ai_brain")
    trading_engine = registry.get_service("trading_engine")
    
    assert ai_service.last_analysis is not None
    assert trading_engine.last_market_update is not None
    
    # Clean shutdown
    await health_monitor.stop_monitoring()
    await registry.stop_all_services()

@pytest.mark.asyncio
async def test_real_trading_scenario():
    """Test realistic trading scenario end-to-end"""
    registry, health_monitor, event_bus = await initialize_complete_system()
    
    # Subscribe to trading events
    executed_trades = []
    event_bus.subscribe("trade.executed", 
                       lambda e: executed_trades.append(e), 
                       "test")
    
    # Simulate series of market updates that should trigger trading
    market_prices = [23500.0, 23510.0, 23520.0, 23530.0, 23540.0]
    
    for price in market_prices:
        market_data = MockMarketData("NQU25", price)
        await event_bus.publish(Event(
            type="market_data.updated",
            data=market_data,
            source_service="e2e_test"
        ))
        await asyncio.sleep(0.2)  # Allow processing between updates
    
    # Wait for final processing
    await asyncio.sleep(2)
    
    # Verify trading occurred (if conditions were met)
    ai_service = registry.get_service("ai_brain")
    if ai_service.generated_signals > 0:
        assert len(executed_trades) > 0
    
    # Clean shutdown
    await health_monitor.stop_monitoring()
    await registry.stop_all_services()
```

### 4.2 Backwards Compatibility Tests

```python
# tests/e2e/test_backwards_compatibility.py
import pytest
from minhos.legacy import get_market_data_service, get_trading_engine

def test_legacy_service_access():
    """Test that legacy service access still works"""
    # Legacy code should still work during transition
    market_service = get_market_data_service()
    trading_engine = get_trading_engine()
    
    assert market_service is not None
    assert trading_engine is not None
    
    # Legacy methods should still exist
    assert hasattr(market_service, 'get_market_data')
    assert hasattr(trading_engine, 'get_positions')

@pytest.mark.asyncio
async def test_mixed_legacy_and_new_architecture():
    """Test that legacy and new services can coexist"""
    # This test ensures smooth migration by allowing both approaches
    
    # Legacy service access
    legacy_market_service = get_market_data_service()
    
    # New architecture
    event_bus = EventBus()
    new_market_service = MarketDataService(event_bus)
    
    # Both should work
    legacy_data = await legacy_market_service.get_market_data("NQU25")
    new_data = await new_market_service.get_market_data("NQU25")
    
    # Data should be equivalent
    if legacy_data and new_data:
        assert legacy_data.symbol == new_data.symbol
        assert abs(legacy_data.price - new_data.price) < 0.01
```

## 5. Chaos Testing

### 5.1 Failure Simulation Tests

```python
# tests/chaos/test_failure_scenarios.py
import pytest
import asyncio
import random

@pytest.mark.asyncio
async def test_random_service_failures():
    """Test system resilience with random service failures"""
    registry, health_monitor, event_bus = await initialize_complete_system()
    
    # Run system for a period with random failures
    services = list(registry._services.keys())
    failure_count = 0
    
    async def cause_random_failures():
        nonlocal failure_count
        for _ in range(10):  # 10 failure events
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Pick random service to fail
            service_name = random.choice(services)
            if service_name != "state_manager":  # Don't fail critical services
                service = registry.get_service(service_name)
                if hasattr(service, 'cause_temporary_failure'):
                    await service.cause_temporary_failure()
                    failure_count += 1
    
    # Run system with failures
    failure_task = asyncio.create_task(cause_random_failures())
    
    # Continue processing market data during failures
    for i in range(20):
        market_data = MockMarketData("NQU25", 23500.0 + i)
        await event_bus.publish(Event(
            type="market_data.updated",
            data=market_data,
            source_service="chaos_test"
        ))
        await asyncio.sleep(0.5)
    
    await failure_task
    
    # System should still be operational
    health_status = health_monitor.get_all_health_status()
    healthy_services = sum(1 for h in health_status.values() 
                          if h.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED])
    
    # At least 70% of services should be healthy
    assert healthy_services >= len(services) * 0.7
    
    await health_monitor.stop_monitoring()
    await registry.stop_all_services()

@pytest.mark.asyncio
async def test_network_partition_simulation():
    """Test behavior during simulated network partitions"""
    # Simulate network issues by adding delays to event delivery
    
    event_bus = EventBus()
    original_publish = event_bus.publish
    
    async def delayed_publish(event):
        # Random delay to simulate network issues
        await asyncio.sleep(random.uniform(0.1, 1.0))
        return await original_publish(event)
    
    event_bus.publish = delayed_publish
    
    # Continue with normal system test
    registry = ServiceRegistry(event_bus)
    # ... setup services ...
    
    # Test should pass even with network delays
    # Services should handle delayed/out-of-order events gracefully
```

## 6. Migration Validation Tests

### 6.1 Pre-Migration Tests

```python
# tests/migration/test_pre_migration_baseline.py
import pytest
import time
from minhos.legacy_system import LegacySystem

class TestPreMigrationBaseline:
    """Establish performance and functionality baseline before migration"""
    
    @pytest.mark.asyncio
    async def test_legacy_system_performance(self):
        """Measure legacy system performance as baseline"""
        legacy_system = LegacySystem()
        await legacy_system.start()
        
        # Measure market data processing time
        start_time = time.time()
        
        for i in range(100):
            market_data = MockMarketData("NQU25", 23500.0 + i)
            await legacy_system.process_market_data(market_data)
        
        end_time = time.time()
        legacy_processing_time = end_time - start_time
        
        # Store baseline for comparison
        with open("baseline_performance.json", "w") as f:
            json.dump({
                "market_data_processing_time": legacy_processing_time,
                "timestamp": datetime.now().isoformat()
            }, f)
        
        await legacy_system.stop()
        
        # Baseline should be reasonable
        assert legacy_processing_time < 10.0
    
    def test_legacy_system_functionality(self):
        """Document all legacy system functionality"""
        legacy_system = LegacySystem()
        
        # Test all public methods exist
        expected_methods = [
            "get_market_data", "get_positions", "execute_trade",
            "get_performance_metrics", "check_risk_limits"
        ]
        
        for method_name in expected_methods:
            assert hasattr(legacy_system, method_name)
```

### 6.2 Post-Migration Validation

```python
# tests/migration/test_post_migration_validation.py
import pytest
import json
import time

class TestPostMigrationValidation:
    """Validate that new system meets or exceeds legacy performance"""
    
    @pytest.mark.asyncio
    async def test_new_system_performance_comparison(self):
        """Compare new system performance to baseline"""
        # Load baseline performance
        with open("baseline_performance.json", "r") as f:
            baseline = json.load(f)
        
        legacy_time = baseline["market_data_processing_time"]
        
        # Test new system performance
        registry, health_monitor, event_bus = await initialize_complete_system()
        
        start_time = time.time()
        
        for i in range(100):
            market_data = MockMarketData("NQU25", 23500.0 + i)
            await event_bus.publish(Event(
                type="market_data.updated",
                data=market_data,
                source_service="perf_test"
            ))
        
        # Wait for all processing to complete
        await asyncio.sleep(2)
        
        end_time = time.time()
        new_processing_time = end_time - start_time
        
        # New system should be at least as fast as legacy
        # Allow 20% performance degradation during initial migration
        assert new_processing_time <= legacy_time * 1.2
        
        await health_monitor.stop_monitoring()
        await registry.stop_all_services()
    
    @pytest.mark.asyncio
    async def test_feature_parity_validation(self):
        """Validate all legacy features work in new system"""
        registry, health_monitor, event_bus = await initialize_complete_system()
        
        # Test all major features
        market_service = registry.get_service("market_data")
        trading_engine = registry.get_service("trading_engine")
        risk_manager = registry.get_service("risk_manager")
        
        # Market data functionality
        market_data = await market_service.get_market_data("NQU25")
        assert market_data is not None
        
        all_data = await market_service.get_all_market_data()
        assert len(all_data) > 0
        
        # Trading functionality
        positions = await trading_engine.get_positions()
        assert isinstance(positions, list)
        
        metrics = await trading_engine.get_performance_metrics()
        assert isinstance(metrics, dict)
        
        # Risk management functionality
        risk_metrics = await risk_manager.get_risk_metrics()
        assert isinstance(risk_metrics, dict)
        
        await health_monitor.stop_monitoring()
        await registry.stop_all_services()
```

## Test Execution Strategy

### Continuous Integration Pipeline

```yaml
# .github/workflows/architecture_migration_tests.yml
name: Architecture Migration Tests

on:
  push:
    branches: [ feature/service-architecture-redesign ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run unit tests
        run: |
          pytest tests/core/ tests/services/ -v --cov=minhos --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      - name: Run integration tests
        run: |
          pytest tests/integration/ -v --tb=short

  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-benchmark
      - name: Run performance tests
        run: |
          pytest tests/performance/ -v --benchmark-only

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      - name: Run end-to-end tests
        run: |
          pytest tests/e2e/ -v --tb=short
```

### Local Testing Commands

```bash
# Run all unit tests
pytest tests/core/ tests/services/ -v

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v --benchmark-only

# Run end-to-end tests
pytest tests/e2e/ -v

# Run migration validation tests
pytest tests/migration/ -v

# Run chaos tests (optional, for robustness validation)
pytest tests/chaos/ -v

# Generate coverage report
pytest --cov=minhos --cov-report=html --cov-report=term

# Run specific test categories
pytest -m "not chaos" -v  # Run all except chaos tests
pytest -m "performance" -v  # Run only performance tests
```

## Test Data Management

### Mock Data Generation

```python
# tests/fixtures/mock_data.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import random

@dataclass
class MockMarketData:
    symbol: str
    price: Decimal
    volume: int = 0
    bid: Decimal = None
    ask: Decimal = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.bid is None:
            self.bid = self.price - Decimal('0.25')
        if self.ask is None:
            self.ask = self.price + Decimal('0.25')

class MarketDataGenerator:
    def __init__(self, symbol: str, base_price: float):
        self.symbol = symbol
        self.base_price = base_price
        self.current_price = base_price
    
    def generate_realistic_sequence(self, count: int):
        """Generate realistic market data sequence"""
        data_points = []
        
        for i in range(count):
            # Random walk with mean reversion
            change = random.gauss(0, 0.5)  # Small random changes
            self.current_price += change
            
            # Mean reversion
            if abs(self.current_price - self.base_price) > 10:
                self.current_price += (self.base_price - self.current_price) * 0.1
            
            data_point = MockMarketData(
                symbol=self.symbol,
                price=Decimal(str(round(self.current_price, 2))),
                volume=random.randint(1, 100),
                timestamp=datetime.now() + timedelta(seconds=i)
            )
            
            data_points.append(data_point)
        
        return data_points
```

## Success Criteria

### Test Coverage Requirements
- **Unit Tests**: >90% code coverage
- **Integration Tests**: All service interactions covered
- **Performance Tests**: No regression >20% from baseline
- **End-to-End Tests**: All critical user journeys covered
- **Migration Tests**: Feature parity with legacy system

### Quality Gates
1. All unit tests must pass
2. Integration tests demonstrate proper service communication
3. Performance tests show acceptable overhead (<20% degradation)
4. End-to-end tests validate complete system functionality
5. Migration tests confirm feature parity

### Monitoring and Alerting
- Automated test execution on every commit
- Performance regression alerts
- Test failure notifications
- Coverage decrease alerts

This comprehensive testing strategy ensures that the service architecture redesign maintains system reliability while delivering improved maintainability and scalability.