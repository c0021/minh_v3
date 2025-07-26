"""
MinhOS v3 Test Configuration
============================

Pytest configuration and fixtures for MinhOS v3 testing.
"""

import asyncio
import os
import tempfile
from pathlib import Path
# Mock imports removed - MinhOS philosophy: NO FAKE DATA
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

# Mock fixtures removed - MinhOS philosophy: NO FAKE DATA
# Tests must use real Sierra Chart connections or be skipped

# Sample data fixtures removed - MinhOS philosophy: NO FAKE DATA
# Tests must use real market data from Sierra Chart or be skipped