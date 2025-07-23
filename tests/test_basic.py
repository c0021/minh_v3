"""
Basic validation tests for MinhOS v3
"""

import pytest
import sys
from pathlib import Path


def test_python_version():
    """Test that Python version is 3.9+"""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version_info}"


def test_project_structure():
    """Test that basic project structure exists"""
    project_root = Path(__file__).parent.parent
    
    required_dirs = [
        "minhos",
        "minhos/core", 
        "minhos/services",
        "bridge_windows",
        "tests",
        "data",
        "logs"
    ]
    
    for dir_path in required_dirs:
        assert (project_root / dir_path).exists(), f"Missing directory: {dir_path}"


def test_configuration_import():
    """Test that configuration can be imported"""
    from minhos.core.config import Config, config
    
    assert isinstance(config, Config)
    assert config.environment in ["dev", "test", "prod"]


def test_sierra_client_import():
    """Test that Sierra client can be imported"""
    from minhos.core.sierra_client import SierraClient
    
    client = SierraClient()
    assert client.host
    assert client.port > 0


@pytest.mark.asyncio
async def test_sierra_client_mock(mock_sierra_client):
    """Test Sierra client with mocking"""
    assert await mock_sierra_client.connect()
    
    market_data = await mock_sierra_client.get_market_data()
    assert market_data["price"] > 0
    
    trade_result = await mock_sierra_client.execute_trade("BUY", "NQ", 1)
    assert trade_result["status"] == "submitted"


def test_bridge_files_exist():
    """Test that Windows bridge files exist"""
    project_root = Path(__file__).parent.parent
    bridge_dir = project_root / "bridge_windows"
    
    required_files = [
        "bridge.py",
        "requirements.txt", 
        "install.ps1"
    ]
    
    for file_path in required_files:
        assert (bridge_dir / file_path).exists(), f"Missing bridge file: {file_path}"


def test_makefile_exists():
    """Test that Makefile exists and has key targets"""
    project_root = Path(__file__).parent.parent
    makefile = project_root / "Makefile"
    
    assert makefile.exists(), "Makefile not found"
    
    content = makefile.read_text()
    required_targets = ["install", "test", "run", "bridge-test", "clean"]
    
    for target in required_targets:
        assert f"{target}:" in content, f"Missing Makefile target: {target}"


def test_docker_compose_exists():
    """Test that docker-compose.yml exists"""
    project_root = Path(__file__).parent.parent
    docker_compose = project_root / "docker-compose.yml"
    
    assert docker_compose.exists(), "docker-compose.yml not found"


def test_sample_data(sample_market_data, sample_trade_data):
    """Test sample data fixtures"""
    # Test market data structure
    assert "symbol" in sample_market_data
    assert "price" in sample_market_data
    assert sample_market_data["price"] > 0
    
    # Test trade data structure  
    assert "action" in sample_trade_data
    assert sample_trade_data["action"] in ["BUY", "SELL"]
    assert "symbol" in sample_trade_data
    assert sample_trade_data["quantity"] > 0