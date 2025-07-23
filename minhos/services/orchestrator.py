#!/usr/bin/env python3
"""
MinhOS v3 Service Orchestrator
==============================
Manages the lifecycle of all MinhOS services with dependency resolution,
health monitoring, and automatic recovery.

Key Features:
- Dependency-based startup ordering
- Health monitoring with configurable intervals
- Automatic service recovery with backoff
- Graceful shutdown handling
- Service state persistence
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
from pathlib import Path

from minhos.core.base_service import BaseService
from minhos.services import (
    get_sierra_client, get_market_data_service, get_web_api_service,
    get_state_manager, get_ai_brain_service, get_trading_engine,
    get_pattern_analyzer, get_risk_manager
)
from minhos.dashboard import DashboardServer

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service lifecycle states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    RECOVERING = "recovering"


class ServiceInfo:
    """Information about a managed service"""
    
    def __init__(self, name: str, factory, dependencies: List[str] = None):
        self.name = name
        self.factory = factory
        self.dependencies = dependencies or []
        self.instance: Optional[BaseService] = None
        self.status = ServiceStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        self.health_status = False
        self.restart_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None


class ServiceOrchestrator:
    """Orchestrates all MinhOS services"""
    
    def __init__(self, config):
        self.config = config
        self.services: Dict[str, ServiceInfo] = {}
        self.running = False
        self.health_check_interval = 10  # seconds
        self.max_restart_attempts = 3
        self.restart_delay = 5  # seconds
        
        # Define service dependencies
        self._define_services()
        
        # Tasks for background operations
        self._health_monitor_task = None
        
    def _define_services(self):
        """Define all services and their dependencies"""
        
        # Core infrastructure services
        self.services['state_manager'] = ServiceInfo(
            'state_manager',
            get_state_manager,
            dependencies=[]
        )
        
        self.services['sierra_client'] = ServiceInfo(
            'sierra_client',
            get_sierra_client,
            dependencies=['state_manager']
        )
        
        # Data services
        self.services['market_data'] = ServiceInfo(
            'market_data',
            get_market_data_service,
            dependencies=['sierra_client', 'state_manager']
        )
        
        # Analysis services
        self.services['pattern_analyzer'] = ServiceInfo(
            'pattern_analyzer',
            get_pattern_analyzer,
            dependencies=['market_data', 'state_manager']
        )
        
        self.services['ai_brain'] = ServiceInfo(
            'ai_brain',
            get_ai_brain_service,
            dependencies=['market_data', 'pattern_analyzer', 'state_manager']
        )
        
        # Trading services
        self.services['risk_manager'] = ServiceInfo(
            'risk_manager',
            get_risk_manager,
            dependencies=['state_manager', 'market_data']
        )
        
        self.services['trading_engine'] = ServiceInfo(
            'trading_engine',
            get_trading_engine,
            dependencies=['ai_brain', 'risk_manager', 'sierra_client', 'state_manager']
        )
        
        # API services
        self.services['web_api'] = ServiceInfo(
            'web_api',
            get_web_api_service,
            dependencies=['market_data', 'state_manager', 'trading_engine']
        )
        
        # Dashboard service
        self.services['dashboard'] = ServiceInfo(
            'dashboard',
            self._get_dashboard_service,
            dependencies=['web_api', 'market_data', 'state_manager']
        )
    
    def _get_dashboard_service(self):
        """Create dashboard service instance"""
        return DashboardServer(host="0.0.0.0", port=8888)
    
    def _get_startup_order(self) -> List[str]:
        """Determine service startup order based on dependencies"""
        visited = set()
        order = []
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            service = self.services.get(name)
            if service:
                for dep in service.dependencies:
                    visit(dep)
                order.append(name)
        
        for name in self.services:
            visit(name)
        
        return order
    
    async def start(self):
        """Start all services in dependency order"""
        self.running = True
        logger.info("Starting ServiceOrchestrator")
        
        # Get startup order
        startup_order = self._get_startup_order()
        logger.info(f"Service startup order: {startup_order}")
        
        # Start services
        for service_name in startup_order:
            if not self.running:
                break
                
            try:
                await self._start_service(service_name)
            except Exception as e:
                logger.error(f"Failed to start {service_name}: {e}")
                # Critical service failure - stop orchestrator
                await self.stop()
                raise
        
        # Start health monitoring
        if self.running:
            self._health_monitor_task = asyncio.create_task(self._health_monitor())
            logger.info("All services started successfully")
    
    async def _start_service(self, name: str):
        """Start a single service"""
        service_info = self.services[name]
        
        if service_info.status == ServiceStatus.RUNNING:
            logger.debug(f"Service {name} already running")
            return
        
        logger.info(f"Starting service: {name}")
        service_info.status = ServiceStatus.STARTING
        
        try:
            # Check dependencies
            for dep in service_info.dependencies:
                dep_info = self.services.get(dep)
                if not dep_info or dep_info.status != ServiceStatus.RUNNING:
                    raise RuntimeError(f"Dependency {dep} not running")
            
            # Create service instance
            service_info.instance = service_info.factory()
            
            # Start the service
            await service_info.instance.start()
            
            service_info.status = ServiceStatus.RUNNING
            service_info.start_time = datetime.now()
            service_info.restart_count = 0
            service_info.error_count = 0
            
            logger.info(f"Service {name} started successfully")
            
        except Exception as e:
            service_info.status = ServiceStatus.FAILED
            service_info.last_error = str(e)
            service_info.error_count += 1
            logger.error(f"Failed to start service {name}: {e}")
            raise
    
    async def stop(self):
        """Stop all services in reverse dependency order"""
        logger.info("Stopping ServiceOrchestrator")
        self.running = False
        
        # Cancel health monitoring
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Get shutdown order (reverse of startup)
        shutdown_order = list(reversed(self._get_startup_order()))
        
        # Stop services
        for service_name in shutdown_order:
            await self._stop_service(service_name)
        
        logger.info("All services stopped")
    
    async def _stop_service(self, name: str):
        """Stop a single service"""
        service_info = self.services.get(name)
        if not service_info or service_info.status != ServiceStatus.RUNNING:
            return
        
        logger.info(f"Stopping service: {name}")
        service_info.status = ServiceStatus.STOPPING
        
        try:
            if service_info.instance:
                await service_info.instance.stop()
                service_info.instance = None
            
            service_info.status = ServiceStatus.STOPPED
            service_info.start_time = None
            
            logger.info(f"Service {name} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping service {name}: {e}")
            service_info.status = ServiceStatus.FAILED
            service_info.last_error = str(e)
    
    async def _health_monitor(self):
        """Monitor service health and recover failed services"""
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for name, service_info in self.services.items():
                    if service_info.status == ServiceStatus.RUNNING:
                        await self._check_service_health(name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
    
    async def _check_service_health(self, name: str):
        """Check health of a single service"""
        service_info = self.services[name]
        
        try:
            if service_info.instance:
                health = await service_info.instance.health_check()
                service_info.health_status = health
                service_info.last_health_check = datetime.now()
                
                if not health:
                    logger.warning(f"Service {name} health check failed")
                    await self._handle_unhealthy_service(name)
                    
        except Exception as e:
            logger.error(f"Error checking health of {name}: {e}")
            service_info.health_status = False
            await self._handle_unhealthy_service(name)
    
    async def _handle_unhealthy_service(self, name: str):
        """Handle an unhealthy service"""
        service_info = self.services[name]
        
        if service_info.restart_count >= self.max_restart_attempts:
            logger.error(f"Service {name} exceeded max restart attempts")
            service_info.status = ServiceStatus.FAILED
            return
        
        logger.info(f"Attempting to restart service {name}")
        service_info.status = ServiceStatus.RECOVERING
        service_info.restart_count += 1
        
        # Stop the service
        await self._stop_service(name)
        
        # Wait before restart
        await asyncio.sleep(self.restart_delay)
        
        # Restart the service
        try:
            await self._start_service(name)
            
            # Restart dependent services
            await self._restart_dependent_services(name)
            
        except Exception as e:
            logger.error(f"Failed to restart service {name}: {e}")
    
    async def _restart_dependent_services(self, name: str):
        """Restart services that depend on the given service"""
        for service_name, service_info in self.services.items():
            if name in service_info.dependencies and service_info.status == ServiceStatus.RUNNING:
                logger.info(f"Restarting dependent service: {service_name}")
                await self._stop_service(service_name)
                await self._start_service(service_name)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        
        for name, info in self.services.items():
            status[name] = {
                'status': info.status.value,
                'health': info.health_status,
                'start_time': info.start_time.isoformat() if info.start_time else None,
                'uptime': str(datetime.now() - info.start_time) if info.start_time else None,
                'restart_count': info.restart_count,
                'error_count': info.error_count,
                'last_error': info.last_error,
                'last_health_check': info.last_health_check.isoformat() if info.last_health_check else None
            }
        
        return status
    
    async def restart_service(self, name: str):
        """Manually restart a service"""
        if name not in self.services:
            raise ValueError(f"Unknown service: {name}")
        
        logger.info(f"Manual restart requested for service: {name}")
        
        # Stop the service
        await self._stop_service(name)
        
        # Reset restart count for manual restart
        self.services[name].restart_count = 0
        
        # Start the service
        await self._start_service(name)
        
        # Restart dependent services
        await self._restart_dependent_services(name)