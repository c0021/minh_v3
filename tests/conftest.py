"""
MinhOS v3 Test Configuration
============================

Pytest configuration and fixtures for MinhOS v3 testing.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

# Test environment setup
os.environ["MINHOS_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Test database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def config():
    """Test configuration"""
    from minhos.core.config import Config
    
    # Create test config with temporary directories
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config()
        config.base_dir = Path(tmpdir)
        config.ensure_directories()
        yield config

@pytest.fixture
async def mock_sierra_client():
    """Mock Sierra Chart client"""
    client = MagicMock()
    client.is_connected = True
    client.connect = AsyncMock(return_value=True)
    client.disconnect = AsyncMock()
    client.get_market_data = AsyncMock(return_value={
        "timestamp": "2024-01-01T12:00:00",
        "symbol": "NQ",
        "price": 15000.0,
        "volume": 100,
        "bid": 14999.5,
        "ask": 15000.5
    })
    client.execute_trade = AsyncMock(return_value={"status": "submitted", "command_id": "test123"})
    client.get_stats = MagicMock(return_value={
        "status": "connected",
        "total_messages": 100,
        "failed_requests": 0,
        "latency_ms": 10.5
    })
    
    yield client

@pytest.fixture
def sample_market_data():
    """Sample market data for tests"""
    return {
        "timestamp": "2024-01-01T12:00:00",
        "symbol": "NQ",
        "price": 15000.0,
        "volume": 100,
        "bid": 14999.5,
        "ask": 15000.5
    }

@pytest.fixture
def sample_trade_data():
    """Sample trade data for tests"""
    return {
        "action": "BUY",
        "symbol": "NQ",
        "quantity": 1,
        "price": 15000.0,
        "order_type": "LIMIT"
    }