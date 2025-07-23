#!/usr/bin/env python3
"""
MinhOS v3 Services Module
=========================
Linux-native trading system services with no Windows dependencies.

This module provides all the core services for MinhOS v3:
- Sierra Chart data interface via Tailscale bridge
- Real-time market data streaming
- Web API endpoints
- Centralized state management
- AI-powered market analysis
- Intelligent trading engine
- Pattern recognition and learning
- Comprehensive risk management

All services are designed to work together seamlessly in a Linux environment
with proper error handling, logging, and performance monitoring.
"""

from .sierra_client import SierraClient, get_sierra_client
from ..models.market import MarketData
from .market_data import MarketDataService, get_market_data_service
from .web_api import WebAPIService, get_web_api_service
from .state_manager import (
    StateManager, 
    TradingState, 
    SystemState, 
    Position, 
    RiskParameters, 
    SystemConfig,
    get_state_manager
)
from .ai_brain_service import (
    AIBrainService, 
    TradingSignal, 
    SignalType, 
    MarketAnalysis,
    get_ai_brain_service,
    get_ai_status  # Legacy compatibility
)
from .trading_engine import (
    TradingEngine,
    DecisionPriority,
    MarketRegime,
    TradingDecision,
    get_trading_engine
)
from .pattern_analyzer import (
    PatternAnalyzer,
    PatternType,
    DetectedPattern,
    get_pattern_analyzer
)
from .risk_manager import (
    RiskManager,
    RiskLevel,
    TradeRequest,
    RiskViolation,
    get_risk_manager
)

# Version information
__version__ = "3.0.0"
__author__ = "MinhOS Team"
__description__ = "Linux-native trading system services"

# Service registry for easy access
SERVICES = {
    'sierra_client': get_sierra_client,
    'market_data': get_market_data_service,
    'web_api': get_web_api_service,
    'state_manager': get_state_manager,
    'ai_brain': get_ai_brain_service,
    'trading_engine': get_trading_engine,
    'pattern_analyzer': get_pattern_analyzer,
    'risk_manager': get_risk_manager
}

def get_service(service_name: str):
    """Get a service instance by name"""
    if service_name in SERVICES:
        return SERVICES[service_name]()
    else:
        raise ValueError(f"Unknown service: {service_name}. Available: {list(SERVICES.keys())}")

def list_services():
    """List all available services"""
    return list(SERVICES.keys())

# Export all public components
__all__ = [
    # Core services
    'SierraClient', 'MarketDataService', 'WebAPIService', 'StateManager',
    'AIBrainService', 'TradingEngine', 'PatternAnalyzer', 'RiskManager',
    
    # Service getters
    'get_sierra_client', 'get_market_data_service', 'get_web_api_service',
    'get_state_manager', 'get_ai_brain_service', 'get_trading_engine',
    'get_pattern_analyzer', 'get_risk_manager',
    
    # Data classes and enums
    'MarketData', 'TradingState', 'SystemState', 'Position', 'RiskParameters',
    'SystemConfig', 'TradingSignal', 'SignalType', 'MarketAnalysis',
    'DecisionPriority', 'MarketRegime', 'TradingDecision', 'PatternType',
    'DetectedPattern', 'RiskLevel', 'TradeRequest', 'RiskViolation',
    
    # Legacy compatibility
    'get_ai_status',
    
    # Utility functions
    'get_service', 'list_services',
    
    # Version info
    '__version__', '__author__', '__description__'
]