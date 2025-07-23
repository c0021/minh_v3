#!/usr/bin/env python3
"""
MinhOS v3 Base Service Class
============================

Provides common functionality for all MinhOS services including:
- Async lifecycle management
- Health monitoring  
- Graceful shutdown handling
- Event publishing/subscribing
- Error handling and logging
- Performance monitoring
"""

import asyncio
import logging
import signal
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from minhos.core.config import config


class ServiceStatus(Enum):
    """Service status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    DEGRADED = "degraded"


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceEvent:
    """Service event for pub/sub system"""
    
    def __init__(self, event_type: str, data: Any, source: str, timestamp: datetime = None):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = timestamp or datetime.now()
        self.id = f"{self.source}_{self.event_type}_{int(self.timestamp.timestamp())}"


class BaseService(ABC):
    """
    Base class for all MinhOS services
    
    Provides common functionality including lifecycle management,
    health monitoring, event handling, and graceful shutdown.
    """
    
    def __init__(self, name: str, config_section: Optional[Dict] = None):
        """
        Initialize base service
        
        Args:
            name: Service name
            config_section: Service-specific configuration
        """
        self.name = name
        self.logger = logging.getLogger(f"minhos.{name}")
        self.config_section = config_section or {}
        
        # Service state
        self.status = ServiceStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None
        self.error_count = 0
        self.last_error: Optional[Exception] = None
        
        # Health monitoring
        self.last_health_check = datetime.now()
        self.health_status = HealthStatus.UNKNOWN
        self.health_details: Dict[str, Any] = {}
        
        # Event system
        self.event_subscribers: Dict[str, List[Callable]] = {}
        self.published_events: List[ServiceEvent] = []
        
        # Performance tracking
        self.metrics = {
            "requests_processed": 0,
            "errors_encountered": 0,
            "average_response_time": 0.0,
            "last_activity": datetime.now(),
        }
        
        # Shutdown handling
        self._shutdown_event = asyncio.Event()
        self._tasks: List[asyncio.Task] = []
        
        # Setup signal handlers (if running as main process)
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        except ValueError:
            # Not in main thread, skip signal handlers
            pass
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self._shutdown_event.set()
    
    async def start(self) -> bool:
        """
        Start the service
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.status == ServiceStatus.RUNNING:
            self.logger.warning("Service is already running")
            return True
        
        self.logger.info(f"Starting {self.name} service")
        self.status = ServiceStatus.STARTING
        self.start_time = datetime.now()
        
        try:
            # Initialize service
            await self._initialize()
            
            # Start background tasks
            self._tasks.append(asyncio.create_task(self._health_monitor()))
            self._tasks.append(asyncio.create_task(self._metrics_collector()))
            
            # Start service-specific tasks
            await self._start_service()
            
            self.status = ServiceStatus.RUNNING
            self.logger.info(f"{self.name} service started successfully")
            
            # Publish start event
            await self.publish_event("service_started", {"service": self.name})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start {self.name} service: {e}")
            self.status = ServiceStatus.ERROR
            self.last_error = e
            self.error_count += 1
            return False
    
    async def stop(self) -> bool:
        """
        Stop the service gracefully
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if self.status == ServiceStatus.STOPPED:
            self.logger.warning("Service is already stopped")
            return True
        
        self.logger.info(f"Stopping {self.name} service")
        self.status = ServiceStatus.STOPPING
        
        try:
            # Stop service-specific functionality
            await self._stop_service()
            
            # Cancel background tasks
            for task in self._tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Cleanup
            await self._cleanup()
            
            self.status = ServiceStatus.STOPPED
            self.stop_time = datetime.now()
            self.logger.info(f"{self.name} service stopped successfully")
            
            # Publish stop event
            await self.publish_event("service_stopped", {"service": self.name})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping {self.name} service: {e}")
            self.status = ServiceStatus.ERROR
            self.last_error = e
            self.error_count += 1
            return False
    
    async def restart(self) -> bool:
        """Restart the service"""
        self.logger.info(f"Restarting {self.name} service")
        
        if not await self.stop():
            return False
        
        # Brief pause before restart
        await asyncio.sleep(1)
        
        return await self.start()
    
    async def run_until_shutdown(self):
        """Run the service until shutdown signal received"""
        if not await self.start():
            raise RuntimeError(f"Failed to start {self.name} service")
        
        try:
            # Wait for shutdown signal
            await self._shutdown_event.wait()
        finally:
            await self.stop()
    
    async def get_health(self) -> Dict[str, Any]:
        """Get service health information"""
        uptime = None
        if self.start_time and self.status == ServiceStatus.RUNNING:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "service": self.name,
            "status": self.status.value,
            "health_status": self.health_status.value,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_health_check": self.last_health_check.isoformat(),
            "error_count": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None,
            "metrics": self.metrics.copy(),
            "health_details": self.health_details.copy(),
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return {
            "service": self.name,
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.copy(),
            "events_published": len(self.published_events),
            "subscribers": {event_type: len(subs) for event_type, subs in self.event_subscribers.items()},
        }
    
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to service events"""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
    
    def unsubscribe_from_event(self, event_type: str, callback: Callable):
        """Unsubscribe from service events"""
        if event_type in self.event_subscribers:
            try:
                self.event_subscribers[event_type].remove(callback)
            except ValueError:
                pass
    
    async def publish_event(self, event_type: str, data: Any):
        """Publish an event to subscribers"""
        event = ServiceEvent(event_type, data, self.name)
        self.published_events.append(event)
        
        # Keep only last 1000 events
        if len(self.published_events) > 1000:
            self.published_events = self.published_events[-1000:]
        
        # Notify subscribers
        if event_type in self.event_subscribers:
            for callback in self.event_subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event callback for {event_type}: {e}")
    
    async def _health_monitor(self):
        """Background health monitoring task"""
        while self.status == ServiceStatus.RUNNING:
            try:
                await self._check_health()
                await asyncio.sleep(config.sierra.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_collector(self):
        """Background metrics collection task"""
        while self.status == ServiceStatus.RUNNING:
            try:
                await self._collect_metrics()
                await asyncio.sleep(60)  # Collect every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(60)
    
    async def _check_health(self):
        """Perform health check"""
        try:
            # Update last health check time
            self.last_health_check = datetime.now()
            
            # Perform service-specific health check
            is_healthy = await self._service_health_check()
            
            if is_healthy:
                self.health_status = HealthStatus.HEALTHY
            else:
                self.health_status = HealthStatus.DEGRADED
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.health_status = HealthStatus.UNHEALTHY
            self.health_details["error"] = str(e)
    
    async def _collect_metrics(self):
        """Collect service metrics"""
        try:
            # Update activity timestamp
            self.metrics["last_activity"] = datetime.now()
            
            # Service-specific metrics collection
            await self._service_metrics_collection()
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
    
    # Abstract methods to be implemented by subclasses
    @abstractmethod
    async def _initialize(self):
        """Initialize service-specific components"""
        pass
    
    @abstractmethod 
    async def _start_service(self):
        """Start service-specific functionality"""
        pass
    
    @abstractmethod
    async def _stop_service(self):
        """Stop service-specific functionality"""
        pass
    
    @abstractmethod
    async def _cleanup(self):
        """Cleanup service resources"""
        pass
    
    async def _service_health_check(self) -> bool:
        """Service-specific health check (override in subclasses)"""
        return True
    
    async def _service_metrics_collection(self):
        """Service-specific metrics collection (override in subclasses)"""
        pass
    
    # Utility methods for subclasses
    def record_request(self, response_time: float = None):
        """Record a processed request"""
        self.metrics["requests_processed"] += 1
        self.metrics["last_activity"] = datetime.now()
        
        if response_time is not None:
            # Update average response time
            current_avg = self.metrics.get("average_response_time", 0.0)
            request_count = self.metrics["requests_processed"]
            self.metrics["average_response_time"] = (
                (current_avg * (request_count - 1) + response_time) / request_count
            )
    
    def record_error(self, error: Exception = None):
        """Record an error"""
        self.metrics["errors_encountered"] += 1
        self.error_count += 1
        if error:
            self.last_error = error
    
    def get_uptime(self) -> Optional[timedelta]:
        """Get service uptime"""
        if self.start_time and self.status == ServiceStatus.RUNNING:
            return datetime.now() - self.start_time
        return None