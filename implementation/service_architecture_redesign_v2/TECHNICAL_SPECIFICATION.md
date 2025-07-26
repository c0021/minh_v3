# Technical Specification - Service Architecture Redesign

**Document Version**: 1.0  
**Created**: 2025-07-25  
**Last Updated**: 2025-07-25

## Architecture Overview

### Current State Problems
The current MinhOS architecture suffers from several critical issues that led to the recent operational problems:

1. **Implicit Contracts**: The `TradingEngine.get_positions()` method didn't exist, causing 500 errors every 5 seconds
2. **Data Format Mismatches**: Bridge returns `Dict[str, MarketData]` but services expected single `MarketData` objects
3. **Tight Coupling**: Services call methods directly without checking if they exist
4. **No Fault Isolation**: One service failure cascades to others
5. **Scattered Service Discovery**: Each service finds others differently

### Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Service Mesh Architecture                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Trading   │    │  AI Brain   │    │ Risk Mgmt   │     │
│  │   Engine    │    │   Service   │    │  Service    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│          │                   │                   │          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Event Bus (Pub/Sub)                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│          │                   │                   │          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Market    │    │    State    │    │   Sierra    │     │
│  │    Data     │    │   Manager   │    │   Client    │     │
│  │   Service   │    │             │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                  Service Registry                           │
│              (Contract Validation)                          │
├─────────────────────────────────────────────────────────────┤
│                  Health Monitor                             │
│            (Dependency Management)                          │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Service Registry

**Purpose**: Centralized service discovery with contract validation

**Key Features**:
- Contract enforcement at registration time
- Dependency tracking and resolution
- Service lifecycle management
- Health status aggregation

**Implementation**:
```python
class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, IService] = {}
        self._contracts: Dict[str, Type] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._health_monitor = HealthMonitor()
        self._event_bus = EventBus()
    
    def register(self, name: str, service: IService, contract: Type):
        # Validate service implements contract
        if not isinstance(service, contract):
            raise ContractViolationError(f"{service} must implement {contract}")
        
        self._services[name] = service
        self._contracts[name] = contract
        self._dependencies[name] = service.get_dependencies()
        
        logger.info(f"Registered {name} with contract {contract.__name__}")
    
    async def start_service(self, name: str):
        # Start dependencies first
        for dep in self._dependencies.get(name, []):
            if not self._is_service_healthy(dep):
                await self.start_service(dep)
        
        # Start the requested service
        service = self._services[name]
        await service.start()
        
        # Begin health monitoring
        self._health_monitor.monitor_service(name, service)
```

### 2. Event Bus

**Purpose**: Decouple services through pub/sub messaging

**Key Features**:
- Asynchronous event delivery
- Event history for debugging
- Error handling and retry logic
- Event schema validation

**Event Types**:
- `market_data.updated` - New market data available
- `trade.executed` - Trade completed
- `risk.threshold_exceeded` - Risk limits breached
- `ai.signal_generated` - New trading signal
- `service.health_changed` - Service status update

**Implementation**:
```python
@dataclass
class Event:
    type: str
    data: Any
    metadata: Dict[str, Any]
    timestamp: datetime
    id: str
    source_service: str

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._event_history: deque = deque(maxlen=10000)
        self._schema_validator = EventSchemaValidator()
    
    async def publish(self, event: Event):
        # Validate event schema
        self._schema_validator.validate(event)
        
        # Store in history
        self._event_history.append(event)
        
        # Deliver to subscribers
        handlers = self._subscribers.get(event.type, [])
        tasks = [self._deliver_event(handler, event) for handler in handlers]
        
        # Execute with error handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log delivery failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Event delivery failed: {result}")
    
    async def _deliver_event(self, handler: EventHandler, event: Event):
        try:
            await handler.handle(event)
        except Exception as e:
            # Implement retry logic
            await self._retry_delivery(handler, event, e)
```

### 3. Service Contracts

**Purpose**: Define explicit interfaces that services must implement

**Base Service Interface**:
```python
class IService(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Start the service"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the service gracefully"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ServiceHealth:
        """Return current health status"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of required service dependencies"""
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Return unique service identifier"""
        pass
```

**Trading Engine Contract**:
```python
class ITradingEngine(IService):
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current trading positions"""
        pass
    
    @abstractmethod
    async def execute_trade(self, signal: TradingSignal) -> TradeResult:
        """Execute a trading signal"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get trading performance data"""
        pass
    
    @abstractmethod
    async def set_risk_limits(self, limits: RiskLimits) -> None:
        """Update risk management limits"""
        pass
```

**Market Data Contract**:
```python
class IMarketDataProvider(IService):
    @abstractmethod
    async def get_market_data(self, symbol: str = None) -> Optional[MarketData]:
        """Get current market data for symbol"""
        pass
    
    @abstractmethod
    async def get_all_market_data(self) -> Dict[str, MarketData]:
        """Get market data for all symbols"""
        pass
    
    @abstractmethod
    async def subscribe_to_symbol(self, symbol: str, callback: Callable) -> str:
        """Subscribe to real-time updates for symbol"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """Cancel subscription"""
        pass
```

### 4. Health Monitor

**Purpose**: Track service health and manage dependencies

**Health States**:
- `STARTING` - Service is initializing
- `HEALTHY` - Service is operational
- `DEGRADED` - Service has issues but still functional
- `UNHEALTHY` - Service is not functioning properly
- `STOPPING` - Service is shutting down
- `STOPPED` - Service is not running

**Implementation**:
```python
@dataclass
class ServiceHealth:
    service_name: str
    status: HealthStatus
    dependencies: List[str]
    last_heartbeat: datetime
    errors: List[str]
    metadata: Dict[str, Any]

class HealthMonitor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.health_status: Dict[str, ServiceHealth] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    async def monitor_service(self, service_name: str, service: IService):
        """Start monitoring a service"""
        task = asyncio.create_task(self._monitor_loop(service_name, service))
        self.monitoring_tasks[service_name] = task
    
    async def _monitor_loop(self, service_name: str, service: IService):
        """Continuous health monitoring loop"""
        while True:
            try:
                health = await service.health_check()
                previous_health = self.health_status.get(service_name)
                
                self.health_status[service_name] = health
                
                # Publish health change events
                if not previous_health or previous_health.status != health.status:
                    await self.event_bus.publish(Event(
                        type="service.health_changed",
                        data=health,
                        source_service="health_monitor"
                    ))
                
                # Handle unhealthy services
                if health.status == HealthStatus.UNHEALTHY:
                    await self._handle_unhealthy_service(service_name, health)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                await asyncio.sleep(5)
```

### 5. Data Models

**Standardized Event Schemas**:
```python
@dataclass
class MarketDataEvent:
    symbol: str
    price: Decimal
    volume: int
    bid: Decimal
    ask: Decimal
    timestamp: datetime
    source: str

@dataclass
class TradingSignalEvent:
    signal_id: str
    symbol: str
    action: TradeAction  # BUY, SELL, HOLD
    confidence: float
    target_price: Optional[Decimal]
    stop_loss: Optional[Decimal]
    reasoning: str
    generated_at: datetime

@dataclass
class TradeExecutedEvent:
    trade_id: str
    symbol: str
    action: TradeAction
    quantity: int
    fill_price: Decimal
    commission: Decimal
    executed_at: datetime
    order_type: str
```

## Migration Implementation

### Phase 1: Core Infrastructure

**Step 1.1: Create Base Service Interface**
```python
# File: minhos/core/service_contracts.py
class IService(ABC):
    # Base interface implementation
    pass

class ServiceContractError(Exception):
    """Raised when service doesn't meet contract requirements"""
    pass
```

**Step 1.2: Implement Service Registry**
```python
# File: minhos/core/service_registry.py
class ServiceRegistry:
    # Registry implementation with contract validation
    pass
```

**Step 1.3: Build Event Bus**
```python
# File: minhos/core/event_bus.py
class EventBus:
    # Pub/sub messaging implementation
    pass
```

**Step 1.4: Create Health Monitor**
```python
# File: minhos/core/health_monitor.py
class HealthMonitor:
    # Service health tracking implementation
    pass
```

### Phase 2: Service Migration

**Migration Pattern for Each Service**:

1. **Define Contract**: Create interface specific to service
2. **Implement Contract**: Add interface to existing service class
3. **Add Health Checks**: Implement `health_check()` method
4. **Event Integration**: Subscribe to relevant events, publish updates
5. **Register Service**: Add to service registry with contract
6. **Replace Direct Calls**: Use event bus instead of method calls
7. **Add Tests**: Unit and integration tests for migration

**Example: Market Data Service Migration**
```python
# Before (direct coupling)
class TradingEngine:
    def __init__(self):
        self.market_data_service = get_market_data_service()
    
    async def analyze_market(self):
        data = await self.market_data_service.get_market_data()
        # Process data...

# After (event-driven)
class TradingEngine(ITradingEngine):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("market_data.updated", self._on_market_data)
    
    async def _on_market_data(self, event: Event):
        market_data = event.data
        # Process data...
        
        # Publish analysis result
        await self.event_bus.publish(Event(
            type="market.analysis_completed",
            data=analysis_result,
            source_service="trading_engine"
        ))
```

### Phase 3: Integration Testing

**Test Categories**:

1. **Contract Compliance Tests**: Verify services implement required interfaces
2. **Event Flow Tests**: Validate pub/sub message delivery
3. **Dependency Resolution Tests**: Ensure services start in correct order
4. **Health Monitoring Tests**: Verify health status tracking
5. **Fault Tolerance Tests**: Service failures don't cascade
6. **Performance Tests**: No degradation from new architecture

**Sample Integration Test**:
```python
async def test_market_data_flow():
    # Setup
    registry = ServiceRegistry()
    event_bus = EventBus()
    
    # Register services
    market_service = MarketDataService()
    trading_engine = TradingEngine(event_bus)
    
    registry.register("market_data", market_service, IMarketDataProvider)
    registry.register("trading_engine", trading_engine, ITradingEngine)
    
    # Start services
    await registry.start_all_services()
    
    # Simulate market data update
    market_data = MarketData(symbol="NQU25", price=23500.0)
    await event_bus.publish(Event(
        type="market_data.updated",
        data=market_data,
        source_service="market_data"
    ))
    
    # Verify trading engine received and processed data
    await asyncio.sleep(0.1)  # Allow event processing
    assert trading_engine.last_market_data == market_data
```

## Performance Considerations

### Event Bus Optimization
- **Async Event Delivery**: Non-blocking message publishing
- **Event Batching**: Group related events for efficiency
- **Subscription Filtering**: Reduce unnecessary message delivery
- **Event History Limits**: Prevent memory leaks from event storage

### Service Registry Efficiency
- **Dependency Caching**: Cache dependency resolution results
- **Health Check Batching**: Group health checks to reduce overhead
- **Lazy Service Loading**: Start services only when needed

### Memory Management
- **Event Cleanup**: Automatically clean old events from history
- **Service Isolation**: Each service runs in separate memory space
- **Resource Monitoring**: Track memory and CPU usage per service

## Error Handling Strategy

### Service Failure Handling
1. **Graceful Degradation**: Continue operating with reduced functionality
2. **Automatic Retry**: Retry failed operations with exponential backoff
3. **Circuit Breaker**: Prevent cascading failures by isolating problems
4. **Fallback Mechanisms**: Use cached data when services unavailable

### Event Delivery Failures
1. **Dead Letter Queue**: Store undeliverable events for later processing
2. **Retry Logic**: Attempt redelivery with increasing delays
3. **Event Versioning**: Handle schema changes gracefully
4. **Monitoring Alerts**: Notify operators of persistent failures

## Security Considerations

### Service Communication
- **Authentication**: Services must authenticate with registry
- **Authorization**: Role-based access to events and services
- **Encryption**: Secure communication between services
- **Audit Logging**: Track all service interactions

### Event Security
- **Event Signing**: Verify event authenticity
- **Access Control**: Restrict event publishing/subscribing by service
- **Data Sanitization**: Validate and clean event payloads
- **Privacy Protection**: Mask sensitive data in events

This technical specification provides the detailed blueprint for transforming MinhOS into a robust, maintainable service architecture that eliminates the current coupling issues and provides a foundation for future growth.