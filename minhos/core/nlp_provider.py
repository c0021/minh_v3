"""
API-agnostic NLP provider system for chat interface.
Supports swappable providers: Kimi K2, OpenAI, Anthropic, Local LLM.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParsedIntent:
    """Structured representation of parsed user intent."""
    intent: str  # query, analyze, explain, execute, alert
    symbol: Optional[str] = None
    indicator: Optional[str] = None
    parameters: Dict[str, Any] = None
    timeframe: Optional[str] = None
    confidence: float = 0.0
    raw_input: str = ""
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class NLPResponse:
    """Structured response from NLP provider."""
    content: str
    confidence: float = 0.0
    provider: str = ""
    processing_time: float = 0.0
    tokens_used: int = 0
    
class NLPProvider(ABC):
    """Abstract base class for all NLP providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"nlp.{name}")
    
    @abstractmethod
    async def parse_intent(self, user_input: str, context: Dict[str, Any] = None) -> ParsedIntent:
        """Parse user input into structured trading intent."""
        pass
    
    @abstractmethod
    async def generate_response(self, data: Dict[str, Any], context: str, user_input: str = "") -> NLPResponse:
        """Generate conversational response from technical data."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available and healthy."""
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health and performance metrics."""
        pass

class NoAvailableProviderError(Exception):
    """Raised when no NLP providers are available."""
    pass

class NLPProviderManager:
    """Manages multiple NLP providers with automatic fallback."""
    
    def __init__(self, primary_provider: str = "kimi_k2", fallback_providers: List[str] = None):
        self.providers: Dict[str, NLPProvider] = {}
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or ["openai", "local"]
        self.logger = logging.getLogger("nlp.manager")
        
        # Provider usage statistics
        self.provider_stats = {
            "requests_by_provider": {},
            "failures_by_provider": {},
            "response_times": {},
            "last_used": {}
        }
    
    def register_provider(self, name: str, provider: NLPProvider):
        """Register a new NLP provider."""
        self.providers[name] = provider
        self.provider_stats["requests_by_provider"][name] = 0
        self.provider_stats["failures_by_provider"][name] = 0
        self.provider_stats["response_times"][name] = []
        self.logger.info(f"Registered NLP provider: {name}")
    
    async def get_available_provider(self) -> NLPProvider:
        """Get the first available provider from priority list."""
        provider_order = [self.primary_provider] + self.fallback_providers
        
        for provider_name in provider_order:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                try:
                    if await provider.is_available():
                        self.logger.debug(f"Using provider: {provider_name}")
                        return provider
                except Exception as e:
                    self.logger.warning(f"Provider {provider_name} availability check failed: {e}")
                    self.provider_stats["failures_by_provider"][provider_name] += 1
        
        raise NoAvailableProviderError("No NLP providers are currently available")
    
    async def parse_intent(self, user_input: str, context: Dict[str, Any] = None) -> ParsedIntent:
        """Parse intent using the first available provider."""
        provider = await self.get_available_provider()
        
        try:
            start_time = datetime.utcnow()
            result = await provider.parse_intent(user_input, context)
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_provider_stats(provider.name, processing_time, success=True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Intent parsing failed with provider {provider.name}: {e}")
            self._update_provider_stats(provider.name, 0, success=False)
            
            # Try fallback providers
            return await self._try_fallback_intent_parsing(user_input, context, exclude=[provider.name])
    
    async def generate_response(self, data: Dict[str, Any], context: str, user_input: str = "") -> NLPResponse:
        """Generate response using the first available provider."""
        provider = await self.get_available_provider()
        
        try:
            start_time = datetime.utcnow()
            result = await provider.generate_response(data, context, user_input)
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_provider_stats(provider.name, processing_time, success=True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Response generation failed with provider {provider.name}: {e}")
            self._update_provider_stats(provider.name, 0, success=False)
            
            # Try fallback providers
            return await self._try_fallback_response_generation(data, context, user_input, exclude=[provider.name])
    
    async def _try_fallback_intent_parsing(self, user_input: str, context: Dict[str, Any], exclude: List[str]) -> ParsedIntent:
        """Try fallback providers for intent parsing."""
        available_providers = [name for name in self.fallback_providers if name not in exclude and name in self.providers]
        
        for provider_name in available_providers:
            provider = self.providers[provider_name]
            try:
                if await provider.is_available():
                    self.logger.info(f"Trying fallback provider for intent parsing: {provider_name}")
                    return await provider.parse_intent(user_input, context)
            except Exception as e:
                self.logger.warning(f"Fallback provider {provider_name} failed: {e}")
        
        # Return basic parsed intent as last resort
        return ParsedIntent(
            intent="query",
            raw_input=user_input,
            confidence=0.1
        )
    
    async def _try_fallback_response_generation(self, data: Dict[str, Any], context: str, user_input: str, exclude: List[str]) -> NLPResponse:
        """Try fallback providers for response generation."""
        available_providers = [name for name in self.fallback_providers if name not in exclude and name in self.providers]
        
        for provider_name in available_providers:
            provider = self.providers[provider_name]
            try:
                if await provider.is_available():
                    self.logger.info(f"Trying fallback provider for response generation: {provider_name}")
                    return await provider.generate_response(data, context, user_input)
            except Exception as e:
                self.logger.warning(f"Fallback provider {provider_name} failed: {e}")
        
        # Return basic response as last resort
        return NLPResponse(
            content=f"Technical data: {json.dumps(data, indent=2)}",
            confidence=0.1,
            provider="fallback"
        )
    
    def _update_provider_stats(self, provider_name: str, processing_time: float, success: bool):
        """Update provider usage statistics."""
        self.provider_stats["requests_by_provider"][provider_name] += 1
        self.provider_stats["last_used"][provider_name] = datetime.utcnow().isoformat()
        
        if success:
            self.provider_stats["response_times"][provider_name].append(processing_time)
            # Keep only last 100 response times
            if len(self.provider_stats["response_times"][provider_name]) > 100:
                self.provider_stats["response_times"][provider_name] = self.provider_stats["response_times"][provider_name][-100:]
        else:
            self.provider_stats["failures_by_provider"][provider_name] += 1
    
    async def get_provider_statistics(self) -> Dict[str, Any]:
        """Get comprehensive provider statistics."""
        stats = {}
        
        for provider_name, provider in self.providers.items():
            health_status = await provider.get_health_status()
            
            # Calculate average response time
            response_times = self.provider_stats["response_times"][provider_name]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            # Calculate success rate
            total_requests = self.provider_stats["requests_by_provider"][provider_name]
            failures = self.provider_stats["failures_by_provider"][provider_name]
            success_rate = ((total_requests - failures) / total_requests * 100) if total_requests > 0 else 0.0
            
            stats[provider_name] = {
                "health_status": health_status,
                "total_requests": total_requests,
                "failures": failures,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "last_used": self.provider_stats["last_used"].get(provider_name),
                "is_primary": provider_name == self.primary_provider
            }
        
        return stats

# Singleton instance for global access
_nlp_manager: Optional[NLPProviderManager] = None

def get_nlp_manager() -> NLPProviderManager:
    """Get global NLP provider manager instance."""
    global _nlp_manager
    if _nlp_manager is None:
        _nlp_manager = NLPProviderManager()
    return _nlp_manager

def initialize_nlp_providers(config):
    """Initialize NLP providers based on configuration."""
    manager = get_nlp_manager()
    
    # Import and register providers based on available configurations
    if hasattr(config, 'kimi_k2_api_key') and config.kimi_k2_api_key:
        from .providers.kimi_k2_provider import KimiK2Provider
        manager.register_provider("kimi_k2", KimiK2Provider(config))
    
    if hasattr(config, 'openai_api_key') and config.openai_api_key:
        from .providers.openai_provider import OpenAIProvider
        manager.register_provider("openai", OpenAIProvider(config))
    
    if hasattr(config, 'anthropic_api_key') and config.anthropic_api_key:
        from .providers.anthropic_provider import AnthropicProvider
        manager.register_provider("anthropic", AnthropicProvider(config))
    
    # Always register local LLM as final fallback
    from .providers.local_llm_provider import LocalLLMProvider
    manager.register_provider("local", LocalLLMProvider(config))
    
    logger.info(f"Initialized NLP providers: {list(manager.providers.keys())}")