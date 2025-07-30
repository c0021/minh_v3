#!/usr/bin/env python3
"""
MinhOS v3 Configuration System
==============================

Tailscale-aware configuration management for MinhOS v3.
Handles both development and production environments with
automatic detection and fallback mechanisms.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json
import yaml

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
        except Exception as e:
            print(f"Warning: Failed to load .env file: {e}")

# Load .env file when module is imported
load_env_file()


@dataclass
class SierraConfig:
    """Sierra Chart bridge configuration"""
    host: str = "trading-pc"  # Tailscale hostname
    port: int = 8765
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    health_check_interval: int = 60
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    @property
    def ws_url(self) -> str:
        return f"ws://{self.host}:{self.port}"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///./data/minhos.db"
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 40
    
    # SQLite specific optimizations
    sqlite_wal_mode: bool = True
    sqlite_foreign_keys: bool = True
    sqlite_journal_mode: str = "WAL"
    sqlite_synchronous: str = "NORMAL"


@dataclass
class RedisConfig:
    """Redis configuration for caching and pub/sub"""
    url: str = "redis://localhost:6379/0"
    decode_responses: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class APIConfig:
    """REST API configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    cors_origins: List[str] = None
    rate_limit: str = "1000/minute"
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass  
class WebSocketConfig:
    """WebSocket configuration"""
    host: str = "0.0.0.0"
    port: int = 9001
    max_connections: int = 100
    heartbeat_interval: int = 30
    message_queue_size: int = 1000


@dataclass
class TradingConfig:
    """Trading engine configuration"""
    max_position_size: float = 100000.0
    max_daily_loss: float = 5000.0
    max_drawdown: float = 10000.0
    position_sizing_method: str = "fixed"  # fixed, percent, volatility
    risk_free_rate: float = 0.02
    enable_paper_trading: bool = False  # REAL TRADING ONLY - Configure paper trading in Sierra Chart if needed
    default_symbol: str = "NQ"
    autonomous_threshold: float = 0.75  # Minimum confidence for autonomous trades
    
@dataclass
class TimingConfig:
    """Timing and interval configuration"""
    market_analysis: int = 5000  # milliseconds
    decision_check: int = 30000  # milliseconds
    service_status_update: int = 10000  # milliseconds
    ai_transparency_update: int = 2000  # milliseconds

@dataclass
class ServicesConfig:
    """Services enablement configuration"""
    dashboard: dict = None
    
    def __post_init__(self):
        if self.dashboard is None:
            self.dashboard = {"enabled": True}


@dataclass
class AIConfig:
    """AI and ML configuration"""
    model_update_interval: int = 3600  # seconds
    prediction_horizon: int = 300  # seconds  
    confidence_threshold: float = 0.7
    max_features: int = 100
    enable_online_learning: bool = True
    pattern_memory_size: int = 10000


@dataclass  
class NLPConfig:
    """Natural Language Processing configuration for chat interface"""
    # Provider selection
    primary_provider: str = "kimi_k2"
    fallback_providers: List[str] = None
    
    # Kimi K2 settings
    kimi_k2_api_key: str = ""
    kimi_k2_base_url: str = "https://api.moonshot.cn/v1"
    kimi_k2_model: str = "moonshot-v1-8k"
    
    # OpenAI settings  
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # Anthropic settings
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_model: str = "claude-3-haiku-20240307"
    
    # Local LLM settings (Ollama)
    local_llm_url: str = "http://localhost:11434"
    local_llm_model: str = "llama2"
    
    # General settings
    enable_chat_interface: bool = True
    max_requests_per_minute: int = 50
    request_timeout: float = 30.0
    max_conversation_history: int = 50
    
    def __post_init__(self):
        if self.fallback_providers is None:
            self.fallback_providers = ["openai", "local"]


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "./logs/minhos.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


class Config:
    """
    Main configuration class for MinhOS v3
    
    Loads configuration from multiple sources in priority order:
    1. Environment variables  
    2. Configuration files (YAML/JSON)
    3. Default values
    
    Supports both development and production environments.
    """
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None, env: str = None):
        """
        Initialize configuration
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
            env: Environment name ('dev', 'prod', 'test')
        """
        
        # Detect environment
        self.environment = env or os.getenv("MINHOS_ENV", "dev")
        
        # Base directory setup
        self.base_dir = Path(__file__).parent.parent.parent
        self.ensure_directories()
        
        # Load configuration
        self._load_config(config_file)
        
        # Initialize component configs
        self.sierra = SierraConfig(**self._get_config_section("sierra", {}))
        self.database = DatabaseConfig(**self._get_config_section("database", {}))
        self.redis = RedisConfig(**self._get_config_section("redis", {}))
        self.api = APIConfig(**self._get_config_section("api", {}))
        self.websocket = WebSocketConfig(**self._get_config_section("websocket", {}))
        self.trading = TradingConfig(**self._get_config_section("trading", {}))
        self.timing = TimingConfig(**self._get_config_section("timing", {}))
        self.services = ServicesConfig(**self._get_config_section("services", {}))
        self.ai = AIConfig(**self._get_config_section("ai", {}))
        self.nlp = NLPConfig(**self._get_config_section("nlp", {}))
        self.logging = LoggingConfig(**self._get_config_section("logging", {}))
        
        # Override with environment variables
        self._apply_env_overrides()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        dirs_to_create = [
            self.base_dir / "data",
            self.base_dir / "logs", 
            self.base_dir / "ml_models",
            self.base_dir / "notebooks",
            self.base_dir / "scripts"
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_file: Optional[Union[str, Path]]):
        """Load configuration from file"""
        self._config_data = {}
        
        if config_file:
            config_path = Path(config_file)
        else:
            # Look for config files in order of preference
            config_files = [
                self.base_dir / f"config.{self.environment}.yaml",
                self.base_dir / f"config.{self.environment}.yml", 
                self.base_dir / f"config.{self.environment}.json",
                self.base_dir / "config.yaml",
                self.base_dir / "config.yml",
                self.base_dir / "config.json",
            ]
            
            config_path = None
            for path in config_files:
                if path.exists():
                    config_path = path
                    break
        
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    if config_path.suffix.lower() in ['.yaml', '.yml']:
                        self._config_data = yaml.safe_load(f) or {}
                    elif config_path.suffix.lower() == '.json':
                        self._config_data = json.load(f) or {}
            except Exception as e:
                print(f"Warning: Failed to load config file {config_path}: {e}")
                self._config_data = {}
    
    def _get_config_section(self, section: str, default: dict) -> dict:
        """Get configuration section with environment override"""
        base_config = self._config_data.get(section, {})
        env_config = self._config_data.get("environments", {}).get(self.environment, {}).get(section, {})
        
        # Merge base and environment-specific config
        result = {**default, **base_config, **env_config}
        return result
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            # Sierra Chart
            "SIERRA_HOST": ("sierra", "host"),
            "SIERRA_PORT": ("sierra", "port", int),
            "SIERRA_TIMEOUT": ("sierra", "timeout", int),
            
            # Database
            "DATABASE_URL": ("database", "url"),
            "DATABASE_ECHO": ("database", "echo", lambda x: x.lower() in ['true', '1', 'yes']),
            
            # Redis
            "REDIS_URL": ("redis", "url"),
            
            # API
            "API_HOST": ("api", "host"),
            "API_PORT": ("api", "port", int),
            "API_DEBUG": ("api", "debug", lambda x: x.lower() in ['true', '1', 'yes']),
            
            # WebSocket
            "WS_HOST": ("websocket", "host"),
            "WS_PORT": ("websocket", "port", int),
            
            # Trading
            "MAX_POSITION_SIZE": ("trading", "max_position_size", float),
            "MAX_DAILY_LOSS": ("trading", "max_daily_loss", float),
            "ENABLE_PAPER_TRADING": ("trading", "enable_paper_trading", lambda x: x.lower() in ['true', '1', 'yes']),
            
            # NLP Chat Interface
            "KIMI_K2_API_KEY": ("nlp", "kimi_k2_api_key"),
            "OPENAI_API_KEY": ("nlp", "openai_api_key"),
            "ANTHROPIC_API_KEY": ("nlp", "anthropic_api_key"),
            "PRIMARY_NLP_PROVIDER": ("nlp", "primary_provider"),
            "ENABLE_CHAT_INTERFACE": ("nlp", "enable_chat_interface", lambda x: x.lower() in ['true', '1', 'yes']),
            
            # Logging
            "LOG_LEVEL": ("logging", "level"),
            "LOG_FILE": ("logging", "file_path"),
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                section, key = config_path[:2]
                converter = config_path[2] if len(config_path) > 2 else str
                
                try:
                    converted_value = converter(env_value)
                    setattr(getattr(self, section), key, converted_value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Failed to convert environment variable {env_var}={env_value}: {e}")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "dev"
    
    @property
    def is_production(self) -> bool:  
        """Check if running in production mode"""
        return self.environment == "prod"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment == "test"
    
    def get_data_dir(self) -> Path:
        """Get data directory path"""
        return self.base_dir / "data"
    
    def get_log_dir(self) -> Path:
        """Get logs directory path"""
        return self.base_dir / "logs"
    
    def get_ml_models_dir(self) -> Path:
        """Get ML models directory path"""
        return self.base_dir / "ml_models"
    
    def get(self, key: str, default=None):
        """
        Get configuration value using dot notation
        For compatibility with legacy code expecting config.get()
        
        Example: config.get("trading.autonomous_threshold", 0.75)
        """
        try:
            # Split the key by dots
            parts = key.split(".")
            
            if len(parts) != 2:
                # If not in section.key format, return default
                return default
            
            section, attr = parts
            
            # Get the section object
            if hasattr(self, section):
                section_obj = getattr(self, section)
                # Get the attribute from the section
                if hasattr(section_obj, attr):
                    return getattr(section_obj, attr)
            
            return default
            
        except Exception:
            return default
    
    def to_dict(self) -> Dict:
        """Export configuration to dictionary"""
        return {
            "environment": self.environment,
            "sierra": self.sierra.__dict__,
            "database": self.database.__dict__, 
            "redis": self.redis.__dict__,
            "api": self.api.__dict__,
            "websocket": self.websocket.__dict__,
            "trading": self.trading.__dict__,
            "timing": self.timing.__dict__,
            "services": self.services.__dict__,
            "ai": self.ai.__dict__,
            "nlp": self.nlp.__dict__,
            "logging": self.logging.__dict__,
        }
    
    def save_config(self, file_path: Union[str, Path], format: str = "yaml"):
        """Save current configuration to file"""
        file_path = Path(file_path)
        config_dict = self.to_dict()
        
        with open(file_path, 'w') as f:
            if format.lower() in ['yaml', 'yml']:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")


# Global configuration instance
config = Config()

# Convenience function
def get_config() -> Config:
    """Get the global configuration instance."""
    return config

# Convenience exports
sierra_config = config.sierra
database_config = config.database
redis_config = config.redis
api_config = config.api
websocket_config = config.websocket
trading_config = config.trading
ai_config = config.ai
nlp_config = config.nlp
logging_config = config.logging