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

# Consolidated market data service
from .market_data_service import (
    MarketDataService, 
    SierraChartRecord,
    MultiChartData,
    get_market_data_service,
    get_sierra_client,  # Legacy compatibility
    get_sierra_historical_service  # Legacy compatibility
)
from ..models.market import MarketData
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
    DetectedPattern,
    PatternType,
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
# Pattern analyzer functionality now integrated into ai_brain_service
# from .pattern_analyzer import (
#     PatternAnalyzer,
#     PatternType,
#     DetectedPattern,
#     get_pattern_analyzer
# )

# Legacy compatibility for pattern analyzer
def get_pattern_analyzer():
    """Legacy compatibility - pattern analysis now part of AI brain service"""
    return get_ai_brain_service()
from .risk_manager import (
    RiskManager,
    RiskLevel,
    TradeRequest,
    RiskViolation,
    get_risk_manager
)
# Sierra historical data now part of market_data_service
# from .sierra_historical_data import (
#     SierraHistoricalDataService,
#     SierraChartRecord,
#     get_sierra_historical_service
# )

# Version information
__version__ = "3.0.0"
__author__ = "MinhOS Team"
__description__ = "Linux-native trading system services"

# Service registry for easy access
SERVICES = {
    'market_data': get_market_data_service,  # Consolidated service
    'sierra_client': get_sierra_client,  # Legacy compatibility -> market_data
    'sierra_historical': get_sierra_historical_service,  # Legacy -> market_data
    'web_api': get_web_api_service,
    'state_manager': get_state_manager,
    'ai_brain': get_ai_brain_service,
    'trading_engine': get_trading_engine,
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
    'MarketDataService', 'WebAPIService', 'StateManager',
    'AIBrainService', 'TradingEngine', 'RiskManager',
    
    # Service getters
    'get_market_data_service', 'get_sierra_client', 'get_sierra_historical_service',
    'get_web_api_service', 'get_state_manager', 'get_ai_brain_service', 
    'get_trading_engine', 'get_risk_manager', 'get_pattern_analyzer',
    
    # Data classes and enums
    'MarketData', 'SierraChartRecord', 'MultiChartData',
    'TradingState', 'SystemState', 'Position', 'RiskParameters',
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