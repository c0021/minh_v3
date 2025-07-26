# Migration Guide - Service Architecture Redesign

**Document Version**: 1.0  
**Created**: 2025-07-25  
**Estimated Duration**: 8 weeks  
**Risk Level**: Medium (with mitigation strategies)

## Pre-Migration Checklist

### Environment Preparation
- [ ] Create feature branch: `feature/service-architecture-redesign`
- [ ] Set up development environment with new dependencies
- [ ] Backup current production state and configuration
- [ ] Establish rollback procedures and testing protocols
- [ ] Document current service dependencies and data flows

### Testing Infrastructure
- [ ] Expand unit test coverage for existing services (target: 80%+)
- [ ] Create integration test harness for new architecture
- [ ] Set up performance benchmarking baseline
- [ ] Prepare monitoring and logging for migration process
- [ ] Create service compatibility matrix

## Migration Phases

## Phase 1: Foundation Infrastructure (Week 1-2)

### Goal
Establish core components without disrupting existing system.

### 1.1: Create Service Contracts (Days 1-2)

**Create: `minhos/core/service_contracts.py`**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    STOPPED = "stopped"

@dataclass
class ServiceHealth:
    service_name: str
    status: HealthStatus
    dependencies: List[str]
    last_heartbeat: datetime
    errors: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IService(ABC):
    """Base interface for all MinhOS services"""
    
    @abstractmethod
    async def start(self) -> None:
        """Start the service and initialize resources"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the service gracefully, cleanup resources"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ServiceHealth:
        """Return current health status"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of service names this service depends on"""
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Return unique service identifier"""
        pass

# Specific service contracts
class ITradingEngine(IService):
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def execute_trade(self, signal: Any) -> Any:
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        pass

class IMarketDataProvider(IService):
    @abstractmethod
    async def get_market_data(self, symbol: str = None) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def get_all_market_data(self) -> Dict[str, Any]:
        pass

class IRiskManager(IService):
    @abstractmethod
    async def check_risk_limits(self, trade: Any) -> bool:
        pass
    
    @abstractmethod
    async def get_risk_metrics(self) -> Dict[str, Any]:
        pass

class IAIBrainService(IService):
    @abstractmethod
    async def analyze_market(self, data: Any) -> Any:
        pass
    
    @abstractmethod
    async def generate_signal(self, analysis: Any) -> Any:
        pass

class IStateManager(IService):
    @abstractmethod
    async def get_state(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def update_state(self, state: Dict[str, Any]) -> None:
        pass
```

**Testing**: Create `tests/core/test_service_contracts.py`
```python
import pytest
from minhos.core.service_contracts import IService, ServiceHealth, HealthStatus

class MockService(IService):
    async def start(self): pass
    async def stop(self): pass
    async def health_check(self): return ServiceHealth(...)
    def get_dependencies(self): return []
    def get_service_name(self): return "mock"

def test_service_health_creation():
    health = ServiceHealth(
        service_name="test",
        status=HealthStatus.HEALTHY,
        dependencies=[],
        last_heartbeat=datetime.now(),
        errors=[]
    )
    assert health.service_name == "test"
    assert health.metadata == {}
```

### 1.2: Build Event Bus (Days 3-4)

**Create: `minhos/core/event_bus.py`**
```python
import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Callable, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

@dataclass
class Event:
    type: str
    data: Any
    source_service: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

class EventHandler:
    def __init__(self, handler: Callable, service_name: str):
        self.handler = handler
        self.service_name = service_name
    
    async def handle(self, event: Event):
        try:
            if asyncio.iscoroutinefunction(self.handler):
                await self.handler(event)
            else:
                self.handler(event)
        except Exception as e:
            logger.error(f"Event handler error in {self.service_name}: {e}")
            raise

class EventBus:
    def __init__(self, max_history: int = 10000):
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._event_history: deque = deque(maxlen=max_history)
        self._stats = {
            "events_published": 0,
            "events_delivered": 0,
            "delivery_failures": 0
        }
    
    async def publish(self, event: Event):
        """Publish event to all subscribers"""
        self._event_history.append(event)
        self._stats["events_published"] += 1
        
        subscribers = self._subscribers.get(event.type, [])
        if not subscribers:
            logger.debug(f"No subscribers for event type: {event.type}")
            return
        
        # Deliver to all subscribers concurrently
        tasks = []
        for handler in subscribers:
            tasks.append(self._deliver_with_retry(handler, event))
        
        # Wait for all deliveries
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        for result in results:
            if isinstance(result, Exception):
                self._stats["delivery_failures"] += 1
                logger.error(f"Event delivery failed: {result}")
            else:
                self._stats["events_delivered"] += 1
    
    def subscribe(self, event_type: str, handler: Callable, service_name: str = "unknown"):
        """Subscribe to event type"""
        event_handler = EventHandler(handler, service_name)
        self._subscribers[event_type].append(event_handler)
        logger.info(f"Service {service_name} subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type"""
        handlers = self._subscribers.get(event_type, [])
        self._subscribers[event_type] = [h for h in handlers if h.handler != handler]
    
    async def _deliver_with_retry(self, handler: EventHandler, event: Event, max_retries: int = 3):
        """Deliver event with retry logic"""
        for attempt in range(max_retries):
            try:
                await handler.handle(event)
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return self._stats.copy()
    
    def get_recent_events(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """Get recent events for debugging"""
        events = list(self._event_history)
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
```

**Testing**: Create comprehensive tests for event delivery, retry logic, and error handling.

### 1.3: Implement Service Registry (Days 5-6)

**Create: `minhos/core/service_registry.py`**
```python
import asyncio
import logging
from typing import Dict, List, Type, Any, Optional
from .service_contracts import IService, ServiceHealth, HealthStatus
from .event_bus import EventBus, Event

logger = logging.getLogger(__name__)

class ServiceRegistryError(Exception):
    pass

class ContractViolationError(ServiceRegistryError):
    pass

class ServiceUnavailableError(ServiceRegistryError):
    pass

class ServiceRegistry:
    def __init__(self, event_bus: EventBus):
        self._services: Dict[str, IService] = {}
        self._contracts: Dict[str, Type] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._startup_order: List[str] = []
        self._event_bus = event_bus
        self._running_services: set = set()
        
    def register(self, name: str, service: IService, contract: Type):
        """Register service with contract validation"""
        # Validate contract compliance
        if not isinstance(service, contract):
            raise ContractViolationError(
                f"Service {name} does not implement contract {contract.__name__}"
            )
        
        # Validate service name matches
        if service.get_service_name() != name:
            raise ServiceRegistryError(
                f"Service name mismatch: {name} vs {service.get_service_name()}"
            )
        
        self._services[name] = service
        self._contracts[name] = contract
        self._dependencies[name] = service.get_dependencies()
        
        # Recalculate startup order
        self._calculate_startup_order()
        
        logger.info(f"Registered service {name} with contract {contract.__name__}")
    
    def get_service(self, name: str, contract: Type = None) -> IService:
        """Get service with optional contract validation"""
        service = self._services.get(name)
        if not service:
            raise ServiceUnavailableError(f"Service {name} not found")
        
        if contract and not isinstance(service, contract):
            raise ContractViolationError(
                f"Service {name} does not implement {contract.__name__}"
            )
        
        return service
    
    async def start_all_services(self):
        """Start all services in dependency order"""
        for service_name in self._startup_order:
            await self.start_service(service_name)
    
    async def start_service(self, name: str):
        """Start a specific service and its dependencies"""
        if name in self._running_services:
            logger.debug(f"Service {name} already running")
            return
        
        # Start dependencies first
        for dep_name in self._dependencies.get(name, []):
            await self.start_service(dep_name)
        
        # Start the service
        service = self._services.get(name)
        if not service:
            raise ServiceUnavailableError(f"Service {name} not registered")
        
        try:
            logger.info(f"Starting service: {name}")
            await service.start()
            self._running_services.add(name)
            
            # Publish service started event
            await self._event_bus.publish(Event(
                type="service.started",
                data={"service_name": name},
                source_service="service_registry"
            ))
            
        except Exception as e:
            logger.error(f"Failed to start service {name}: {e}")
            raise
    
    async def stop_all_services(self):
        """Stop all services in reverse dependency order"""
        for service_name in reversed(self._startup_order):
            await self.stop_service(service_name)
    
    async def stop_service(self, name: str):
        """Stop a specific service"""
        if name not in self._running_services:
            return
        
        service = self._services.get(name)
        if service:
            try:
                logger.info(f"Stopping service: {name}")
                await service.stop()
                self._running_services.discard(name)
                
                # Publish service stopped event
                await self._event_bus.publish(Event(
                    type="service.stopped",
                    data={"service_name": name},
                    source_service="service_registry"
                ))
                
            except Exception as e:
                logger.error(f"Error stopping service {name}: {e}")
    
    def _calculate_startup_order(self):
        """Calculate service startup order using topological sort"""
        # Build dependency graph
        graph = {name: self._dependencies.get(name, []) 
                for name in self._services.keys()}
        
        # Topological sort
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(node):
            if node in temp_visited:
                raise ServiceRegistryError(f"Circular dependency detected involving {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            for dep in graph.get(node, []):
                if dep not in self._services:
                    raise ServiceRegistryError(f"Service {node} depends on unregistered service {dep}")
                visit(dep)
            
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        for service_name in self._services.keys():
            if service_name not in visited:
                visit(service_name)
        
        self._startup_order = result
        logger.debug(f"Service startup order: {self._startup_order}")
    
    def get_service_health(self, name: str) -> Optional[ServiceHealth]:
        """Get health status of a service"""
        service = self._services.get(name)
        if not service:
            return None
        
        try:
            # Note: This would be async in real implementation
            # For now, return a basic health status
            return ServiceHealth(
                service_name=name,
                status=HealthStatus.HEALTHY if name in self._running_services else HealthStatus.STOPPED,
                dependencies=self._dependencies.get(name, []),
                last_heartbeat=datetime.now(),
                errors=[]
            )
        except Exception as e:
            return ServiceHealth(
                service_name=name,
                status=HealthStatus.UNHEALTHY,
                dependencies=self._dependencies.get(name, []),
                last_heartbeat=datetime.now(),
                errors=[str(e)]
            )
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List all registered services with metadata"""
        return {
            name: {
                "contract": contract.__name__,
                "dependencies": self._dependencies.get(name, []),
                "running": name in self._running_services
            }
            for name, contract in self._contracts.items()
        }
```

### 1.4: Create Health Monitor (Days 7-8)

**Create: `minhos/core/health_monitor.py`**
```python
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .service_contracts import IService, ServiceHealth, HealthStatus
from .event_bus import EventBus, Event

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, event_bus: EventBus, check_interval: int = 10):
        self.event_bus = event_bus
        self.check_interval = check_interval
        self.monitored_services: Dict[str, IService] = {}
        self.health_history: Dict[str, List[ServiceHealth]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
    
    def add_service(self, service: IService):
        """Add service to monitoring"""
        service_name = service.get_service_name()
        self.monitored_services[service_name] = service
        self.health_history[service_name] = []
        
        if self.running:
            self._start_monitoring_service(service_name)
    
    def remove_service(self, service_name: str):
        """Remove service from monitoring"""
        if service_name in self.monitoring_tasks:
            self.monitoring_tasks[service_name].cancel()
            del self.monitoring_tasks[service_name]
        
        self.monitored_services.pop(service_name, None)
        self.health_history.pop(service_name, None)
    
    async def start_monitoring(self):
        """Start health monitoring for all services"""
        self.running = True
        
        for service_name in self.monitored_services:
            self._start_monitoring_service(service_name)
        
        logger.info(f"Started health monitoring for {len(self.monitored_services)} services")
    
    async def stop_monitoring(self):
        """Stop all health monitoring"""
        self.running = False
        
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to finish
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        
        self.monitoring_tasks.clear()
        logger.info("Stopped health monitoring")
    
    def _start_monitoring_service(self, service_name: str):
        """Start monitoring task for a specific service"""
        if service_name in self.monitoring_tasks:
            self.monitoring_tasks[service_name].cancel()
        
        task = asyncio.create_task(self._monitor_service_loop(service_name))
        self.monitoring_tasks[service_name] = task
    
    async def _monitor_service_loop(self, service_name: str):
        """Continuous monitoring loop for a service"""
        service = self.monitored_services[service_name]
        previous_status = None
        
        while self.running:
            try:
                # Get current health
                health = await service.health_check()
                
                # Store in history
                self.health_history[service_name].append(health)
                
                # Keep only last 100 health checks
                if len(self.health_history[service_name]) > 100:
                    self.health_history[service_name] = self.health_history[service_name][-100:]
                
                # Publish health change events
                if previous_status != health.status:
                    await self.event_bus.publish(Event(
                        type="service.health_changed",
                        data={
                            "service_name": service_name,
                            "previous_status": previous_status.value if previous_status else None,
                            "current_status": health.status.value,
                            "health": health
                        },
                        source_service="health_monitor"
                    ))
                    
                    previous_status = health.status
                
                # Handle critical health issues
                if health.status == HealthStatus.UNHEALTHY:
                    await self._handle_unhealthy_service(service_name, health)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error for {service_name}: {e}")
                
                # Create error health status
                error_health = ServiceHealth(
                    service_name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    dependencies=service.get_dependencies(),
                    last_heartbeat=datetime.now(),
                    errors=[f"Health check failed: {str(e)}"]
                )
                
                self.health_history[service_name].append(error_health)
                
                await asyncio.sleep(5)  # Shorter retry interval on errors
    
    async def _handle_unhealthy_service(self, service_name: str, health: ServiceHealth):
        """Handle unhealthy service detection"""
        logger.warning(f"Service {service_name} is unhealthy: {health.errors}")
        
        await self.event_bus.publish(Event(
            type="service.unhealthy",
            data={
                "service_name": service_name,
                "health": health,
                "suggested_actions": self._suggest_recovery_actions(service_name, health)
            },
            source_service="health_monitor"
        ))
    
    def _suggest_recovery_actions(self, service_name: str, health: ServiceHealth) -> List[str]:
        """Suggest recovery actions based on health status"""
        actions = []
        
        if "timeout" in str(health.errors):
            actions.append("Check network connectivity")
            actions.append("Verify service is responding")
        
        if "memory" in str(health.errors):
            actions.append("Check memory usage")
            actions.append("Consider restarting service")
        
        if "dependency" in str(health.errors):
            actions.append("Check dependent services")
            actions.append("Verify service dependencies are healthy")
        
        if not actions:
            actions.append("Restart service")
            actions.append("Check service logs for errors")
        
        return actions
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get current health for a service"""
        history = self.health_history.get(service_name, [])
        return history[-1] if history else None
    
    def get_all_health_status(self) -> Dict[str, ServiceHealth]:
        """Get current health for all monitored services"""
        return {
            name: self.get_service_health(name)
            for name in self.monitored_services
            if self.get_service_health(name) is not None
        }
    
    def get_health_trends(self, service_name: str, hours: int = 24) -> List[ServiceHealth]:
        """Get health trend for a service over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = self.health_history.get(service_name, [])
        
        return [h for h in history if h.last_heartbeat >= cutoff_time]
```

### 1.5: Phase 1 Testing and Validation

**Integration Test Example**:
```python
# tests/integration/test_phase1_infrastructure.py
import pytest
import asyncio
from minhos.core.service_contracts import IService, ServiceHealth, HealthStatus
from minhos.core.service_registry import ServiceRegistry
from minhos.core.event_bus import EventBus, Event
from minhos.core.health_monitor import HealthMonitor

class MockService(IService):
    def __init__(self, name: str, dependencies: List[str] = None):
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

@pytest.mark.asyncio
async def test_service_registry_dependency_order():
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Create services with dependencies
    service_a = MockService("service_a")
    service_b = MockService("service_b", ["service_a"])
    service_c = MockService("service_c", ["service_b"])
    
    # Register services
    registry.register("service_a", service_a, IService)
    registry.register("service_b", service_b, IService)
    registry.register("service_c", service_c, IService)
    
    # Start all services
    await registry.start_all_services()
    
    # Verify all services started
    assert service_a.started
    assert service_b.started
    assert service_c.started

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    event_bus = EventBus()
    received_events = []
    
    def event_handler(event: Event):
        received_events.append(event)
    
    # Subscribe to events
    event_bus.subscribe("test.event", event_handler, "test_service")
    
    # Publish event
    test_event = Event(
        type="test.event",
        data={"message": "hello"},
        source_service="test"
    )
    
    await event_bus.publish(test_event)
    
    # Verify event received
    assert len(received_events) == 1
    assert received_events[0].data["message"] == "hello"

@pytest.mark.asyncio
async def test_health_monitor():
    event_bus = EventBus()
    health_monitor = HealthMonitor(event_bus, check_interval=1)
    
    service = MockService("test_service")
    health_monitor.add_service(service)
    
    await health_monitor.start_monitoring()
    
    # Wait for health check
    await asyncio.sleep(1.5)
    
    health = health_monitor.get_service_health("test_service")
    assert health is not None
    assert health.service_name == "test_service"
    
    await health_monitor.stop_monitoring()
```

### Phase 1 Completion Criteria

- [ ] All core components implemented and tested
- [ ] Unit tests pass with >90% coverage
- [ ] Integration tests validate component interaction
- [ ] Performance benchmarks show acceptable overhead (<5%)
- [ ] Documentation complete for all new components
- [ ] Existing services remain fully operational

## Phase 2: Service Migration (Week 3-4)

### Migration Order and Rationale

1. **Market Data Service** - Fewest dependencies, easiest to migrate
2. **State Manager** - Core infrastructure used by other services  
3. **Sierra Client** - Data provider that other services depend on
4. **Risk Manager** - Business logic with moderate complexity
5. **AI Brain Service** - Complex logic but well-isolated
6. **Trading Engine** - Most dependencies, migrate last

### 2.1: Market Data Service Migration (Days 9-10)

**Step 1: Update Market Data Service Contract**
```python
# Update minhos/services/market_data.py

from minhos.core.service_contracts import IMarketDataProvider, ServiceHealth, HealthStatus
from minhos.core.event_bus import EventBus, Event

class MarketDataService(IMarketDataProvider):
    def __init__(self, event_bus: EventBus):
        # Existing initialization...
        self.event_bus = event_bus
        self.service_name = "market_data"
        self.dependencies = ["sierra_client"]  # Depends on Sierra client for data
        
        # Subscribe to Sierra client events
        self.event_bus.subscribe("sierra.market_data", self._on_sierra_data, self.service_name)
    
    async def _on_sierra_data(self, event: Event):
        """Handle market data from Sierra client"""
        market_data = event.data
        
        # Store the data
        self.latest_data[market_data.symbol] = market_data
        
        # Publish market data update event
        await self.event_bus.publish(Event(
            type="market_data.updated",
            data=market_data,
            source_service=self.service_name
        ))
    
    # Implement IMarketDataProvider methods
    async def get_market_data(self, symbol: str = None) -> Optional[MarketData]:
        # Existing implementation...
        pass
    
    async def get_all_market_data(self) -> Dict[str, MarketData]:
        # Existing implementation...
        pass
    
    # Implement IService methods
    async def start(self) -> None:
        # Existing start logic...
        await super().start()  # Call existing start method
    
    async def stop(self) -> None:
        # Existing stop logic...
        await super().stop()
    
    async def health_check(self) -> ServiceHealth:
        errors = []
        status = HealthStatus.HEALTHY
        
        # Check if receiving data
        if not self.latest_data:
            errors.append("No market data received")
            status = HealthStatus.DEGRADED
        
        # Check data freshness
        now = datetime.now()
        for symbol, data in self.latest_data.items():
            if now - data.timestamp > timedelta(minutes=5):
                errors.append(f"Stale data for {symbol}")
                status = HealthStatus.DEGRADED
        
        return ServiceHealth(
            service_name=self.service_name,
            status=status,
            dependencies=self.dependencies,
            last_heartbeat=now,
            errors=errors,
            metadata={
                "symbols_count": len(self.latest_data),
                "last_update": max(data.timestamp for data in self.latest_data.values()) if self.latest_data else None
            }
        )
    
    def get_dependencies(self) -> List[str]:
        return self.dependencies
    
    def get_service_name(self) -> str:
        return self.service_name
```

**Step 2: Update Service Instantiation**
```python
# Update minhos/main.py or service initialization

async def initialize_services():
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    health_monitor = HealthMonitor(event_bus)
    
    # Create and register market data service
    market_data_service = MarketDataService(event_bus)
    registry.register("market_data", market_data_service, IMarketDataProvider)
    health_monitor.add_service(market_data_service)
    
    # ... register other services
    
    return registry, health_monitor
```

### 2.2: State Manager Migration (Days 11-12)

Similar process but with IStateManager contract implementation.

### 2.3: Sierra Client Migration (Days 13-14) 

Focus on converting Sierra client to publish events instead of direct method calls.

### 2.4: Risk Manager Migration (Days 15-16)

Implement IRiskManager contract and event-driven risk checking.

### Phase 2 Completion Criteria

- [ ] All target services implement their contracts
- [ ] Services registered with service registry
- [ ] Event-driven communication established
- [ ] Health monitoring active for all services
- [ ] Backward compatibility maintained
- [ ] Integration tests pass

## Phase 3: Complete Integration (Week 5-6)

### 3.1: Replace Direct Service Calls

**Before (direct coupling)**:
```python
class TradingEngine:
    def __init__(self):
        self.market_data = get_market_data_service()
        self.risk_manager = get_risk_manager()
    
    async def process_signal(self, signal):
        # Direct method calls
        market_data = await self.market_data.get_market_data(signal.symbol)
        risk_check = await self.risk_manager.check_risk_limits(signal)
```

**After (event-driven)**:
```python
class TradingEngine(ITradingEngine):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Subscribe to relevant events
        self.event_bus.subscribe("market_data.updated", self._on_market_data)
        self.event_bus.subscribe("ai.signal_generated", self._on_trading_signal)
        self.event_bus.subscribe("risk.check_result", self._on_risk_result)
    
    async def _on_trading_signal(self, event: Event):
        signal = event.data
        
        # Request risk check via event
        await self.event_bus.publish(Event(
            type="risk.check_request",
            data={"signal": signal, "request_id": str(uuid4())},
            source_service="trading_engine"
        ))
```

### 3.2: Service Startup Integration

Update main application startup to use service registry:

```python
# minh.py updates

async def main():
    # Initialize core infrastructure
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    health_monitor = HealthMonitor(event_bus)
    
    # Register all services
    await register_all_services(registry, event_bus, health_monitor)
    
    # Start services in dependency order
    await registry.start_all_services()
    
    # Start health monitoring
    await health_monitor.start_monitoring()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await health_monitor.stop_monitoring()
        await registry.stop_all_services()

async def register_all_services(registry, event_bus, health_monitor):
    # Market Data Service
    market_data = MarketDataService(event_bus)
    registry.register("market_data", market_data, IMarketDataProvider)
    health_monitor.add_service(market_data)
    
    # State Manager
    state_manager = StateManager(event_bus)
    registry.register("state_manager", state_manager, IStateManager)
    health_monitor.add_service(state_manager)
    
    # Continue for all services...
```

## Phase 4: Validation and Deployment (Week 7-8)

### 4.1: Comprehensive Testing

**End-to-End Integration Test**:
```python
@pytest.mark.asyncio
async def test_full_system_integration():
    """Test complete event flow through the system"""
    
    # Setup
    event_bus = EventBus()
    registry = ServiceRegistry(event_bus)
    
    # Register all services
    await register_test_services(registry, event_bus)
    
    # Start system
    await registry.start_all_services()
    
    # Simulate market data update
    market_data = MarketData(symbol="NQU25", price=23500.0)
    await event_bus.publish(Event(
        type="market_data.updated",
        data=market_data,
        source_service="test"
    ))
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Verify AI analysis occurred
    ai_service = registry.get_service("ai_brain", IAIBrainService)
    assert ai_service.last_analysis is not None
    
    # Verify trading engine processed data
    trading_engine = registry.get_service("trading_engine", ITradingEngine)
    assert trading_engine.last_market_update == market_data
    
    # Cleanup
    await registry.stop_all_services()
```

### 4.2: Performance Validation

**Benchmark Tests**:
```python
import time
import statistics

async def benchmark_event_throughput():
    """Measure event processing throughput"""
    event_bus = EventBus()
    received_count = 0
    
    def counter_handler(event):
        nonlocal received_count
        received_count += 1
    
    event_bus.subscribe("benchmark.event", counter_handler)
    
    # Send 1000 events
    start_time = time.time()
    for i in range(1000):
        await event_bus.publish(Event(
            type="benchmark.event",
            data={"id": i},
            source_service="benchmark"
        ))
    
    end_time = time.time()
    
    throughput = 1000 / (end_time - start_time)
    assert throughput > 500  # Should handle 500+ events/sec
    assert received_count == 1000
```

### 4.3: Rollback Procedures

**Feature Flag Implementation**:
```python
# config.py
USE_NEW_ARCHITECTURE = os.getenv("USE_NEW_ARCHITECTURE", "false").lower() == "true"

# Service initialization
if USE_NEW_ARCHITECTURE:
    # Use new service registry approach
    await initialize_new_architecture()
else:
    # Use legacy direct service approach
    await initialize_legacy_services()
```

**Rollback Script**:
```bash
#!/bin/bash
# rollback_architecture.sh

echo "Rolling back to legacy architecture..."

# Set environment variable
export USE_NEW_ARCHITECTURE=false

# Restart services
python minh.py stop
sleep 5
python minh.py start

echo "Rollback complete"
```

## Risk Mitigation Strategies

### 1. Gradual Rollout
- Deploy to development environment first
- Limited production rollout with feature flags
- Monitor performance and error rates closely
- Full rollout only after validation period

### 2. Monitoring and Alerting
- Enhanced logging during migration period
- Performance monitoring dashboards
- Automated alerts for service health issues
- Event flow tracking and debugging tools

### 3. Testing Strategy
- Comprehensive unit tests for all new components
- Integration tests for service interactions
- Load testing to validate performance
- Chaos testing to validate fault tolerance

### 4. Documentation and Training
- Updated architecture documentation
- Service contract specifications
- Troubleshooting guides for operators
- Training sessions for development team

## Success Metrics

### Technical Metrics
- **Zero Downtime**: System remains operational during migration
- **Performance**: No degradation in response times or throughput
- **Reliability**: Reduced error rates and improved fault tolerance
- **Maintainability**: Easier to add new services and modify existing ones

### Operational Metrics
- **Faster Development**: New features can be added without touching multiple services
- **Better Testing**: Services can be tested in isolation
- **Improved Debugging**: Event flow provides clear audit trail
- **Reduced Coupling**: Service failures don't cascade to other services

This migration guide provides a systematic approach to transforming MinhOS into a robust, maintainable service architecture while minimizing risk and ensuring system stability throughout the process.