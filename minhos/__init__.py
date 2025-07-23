"""
MinhOS v3 - Linux-Native Trading Platform
=========================================

A sophisticated trading platform that connects to Sierra Chart via Tailscale bridge,
providing real-time market data, AI-powered analysis, and comprehensive trade management.

Architecture:
- Windows PC: Runs Sierra Chart + minimal bridge
- Linux System: Runs full MinhOS v3 platform
- Connection: Secure Tailscale mesh network

Key Components:
- Core: Configuration, utilities, base classes
- Services: Market data, AI analysis, risk management
- Dashboard: Web-based monitoring interface
- Analysis: Trading indicators and patterns
"""

__version__ = "3.0.0"
__author__ = "MinhOS Development Team"

# Core imports
from minhos.core.config import Config
from minhos.core.base_service import BaseService
# SierraClient is now in services module

# Simplified imports for CLI usage
__all__ = [
    "Config",
    "BaseService"
]