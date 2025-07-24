"""
Local LLM provider implementation using Ollama.
Final fallback when all other providers are unavailable.
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import re

from ..nlp_provider import NLPProvider, ParsedIntent, NLPResponse

logger = logging.getLogger(__name__)

class LocalLLMProvider(NLPProvider):
    """Local LLM provider using Ollama for offline capability."""
    
    def __init__(self, config):
        super().__init__("local")
        self.base_url = getattr(config, 'local_llm_url', 'http://localhost:11434')
        self.model = getattr(config, 'local_llm_model', 'llama2')
        self.timeout = getattr(config, 'request_timeout', 60.0)
        
        # Health tracking
        self.last_health_check = None
        self.is_healthy = False
        self.consecutive_failures = 0
    
    async def parse_intent(self, user_input: str, context: Dict[str, Any] = None) -> ParsedIntent:
        """Parse user input using local LLM or fallback to basic parsing."""
        if await self.is_available():
            try:
                prompt = f"""Parse this trading command and extract information:

Command: "{user_input}"

Extract:
- Intent: query, analyze, explain, execute, or alert
- Symbol: stock ticker if mentioned (like AAPL, NVDA, SPY)
- Indicator: RSI, SMA, EMA, MACD, volume, pattern, volatility if mentioned
- Threshold: any numbers mentioned
- Timeframe: 1m, 5m, 1h, 1d if mentioned

Respond with: intent=X, symbol=Y, indicator=Z, confidence=0.8"""

                response = await self._make_ollama_request(prompt)
                return self._parse_llm_response(response, user_input)
                
            except Exception as e:
                self.logger.error(f"Local LLM intent parsing failed: {e}")
                self.consecutive_failures += 1
        
        # Fallback to rule-based parsing
        return self._rule_based_intent_parsing(user_input)
    
    async def generate_response(self, data: Dict[str, Any], context: str, user_input: str = "") -> NLPResponse:
        """Generate response using local LLM or simple formatting."""
        if await self.is_available():
            try:
                prompt = f"""Convert this technical trading data into a clear response:

User asked: "{user_input}"
Technical data: {json.dumps(data, indent=2)}

Explain the key information in 2-3 sentences. Be specific about numbers and actionable insights."""

                start_time = datetime.utcnow()
                response = await self._make_ollama_request(prompt)
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return NLPResponse(
                    content=response,
                    confidence=0.6,
                    provider=self.name,
                    processing_time=processing_time
                )
                
            except Exception as e:
                self.logger.error(f"Local LLM response generation failed: {e}")
                self.consecutive_failures += 1
        
        # Fallback to simple formatting
        return NLPResponse(
            content=self._format_simple_response(data, user_input),
            confidence=0.4,
            provider=f"{self.name}_fallback"
        )
    
    async def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        # Check health periodically
        now = datetime.utcnow()
        if (self.last_health_check is None or 
            (now - self.last_health_check).total_seconds() > 300):  # 5 minutes
            await self._perform_health_check()
        
        return self.is_healthy and self.consecutive_failures < 3
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of local LLM."""
        await self._perform_health_check()
        
        return {
            "is_healthy": self.is_healthy,
            "consecutive_failures": self.consecutive_failures,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "ollama_url": self.base_url,
            "model": self.model
        }
    
    async def _make_ollama_request(self, prompt: str) -> str:
        """Make request to local Ollama instance."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 200
            }
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    self.consecutive_failures = 0
                    return result.get('response', '').strip()
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama error {response.status}: {error_text}")
    
    async def _perform_health_check(self):
        """Check if Ollama is responsive."""
        try:
            response = await self._make_ollama_request("Say 'ok' if you're working.")
            self.is_healthy = len(response) > 0
            self.last_health_check = datetime.utcnow()
            
            if self.is_healthy:
                self.consecutive_failures = 0
                
        except Exception as e:
            self.logger.debug(f"Local LLM health check failed: {e}")
            self.is_healthy = False
            self.consecutive_failures += 1
            self.last_health_check = datetime.utcnow()
    
    def _parse_llm_response(self, response: str, user_input: str) -> ParsedIntent:
        """Parse LLM response into structured intent."""
        try:
            # Extract values using regex
            intent_match = re.search(r'intent=(\w+)', response, re.IGNORECASE)
            symbol_match = re.search(r'symbol=([A-Z]+|null)', response, re.IGNORECASE)
            indicator_match = re.search(r'indicator=(\w+|null)', response, re.IGNORECASE)
            confidence_match = re.search(r'confidence=([\d.]+)', response)
            
            intent = intent_match.group(1) if intent_match else "query"
            symbol = symbol_match.group(1) if symbol_match and symbol_match.group(1) != "null" else None
            indicator = indicator_match.group(1) if indicator_match and indicator_match.group(1) != "null" else None
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            return ParsedIntent(
                intent=intent.lower(),
                symbol=symbol,
                indicator=indicator,
                confidence=confidence,
                raw_input=user_input
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse LLM response: {e}")
            return self._rule_based_intent_parsing(user_input)
    
    def _rule_based_intent_parsing(self, user_input: str) -> ParsedIntent:
        """Basic rule-based intent parsing as final fallback."""
        user_lower = user_input.lower()
        
        # Determine intent
        intent = "query"
        if any(word in user_lower for word in ["explain", "why", "how", "what"]):
            intent = "explain"
        elif any(word in user_lower for word in ["analyze", "analysis", "look at"]):
            intent = "analyze"
        elif any(word in user_lower for word in ["alert", "notify", "when", "if"]):
            intent = "alert"
        
        # Extract symbol (look for 1-5 capital letters)
        symbol_match = re.search(r'\b([A-Z]{1,5})\b', user_input.upper())
        symbol = symbol_match.group(1) if symbol_match else None
        
        # Extract indicator
        indicator = None
        indicators = ["RSI", "SMA", "EMA", "MACD", "volume", "volatility", "pattern"]
        for ind in indicators:
            if ind.lower() in user_lower:
                indicator = ind
                break
        
        # Extract numbers for parameters
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', user_input)
        parameters = {}
        if numbers:
            parameters["threshold"] = float(numbers[0])
        
        return ParsedIntent(
            intent=intent,
            symbol=symbol,
            indicator=indicator,
            parameters=parameters,
            confidence=0.4,  # Low confidence for rule-based parsing
            raw_input=user_input
        )
    
    def _format_simple_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format a simple response when LLM is unavailable."""
        if not data:
            return "No data available to display."
        
        # Try to create a relevant response based on user input
        user_lower = user_input.lower()
        
        response_parts = []
        
        # Add relevant data points
        for key, value in data.items():
            if isinstance(value, (int, float)):
                response_parts.append(f"{key}: {value:.2f}")
            elif isinstance(value, str) and len(value) < 50:
                response_parts.append(f"{key}: {value}")
        
        if not response_parts:
            return f"Technical data available: {len(data)} indicators"
        
        # Limit response length
        response = " | ".join(response_parts[:4])
        
        # Add context based on user query
        if "rsi" in user_lower and any("rsi" in key.lower() for key in data.keys()):
            response = f"RSI Analysis: {response}"
        elif "volume" in user_lower:
            response = f"Volume Analysis: {response}"
        elif "price" in user_lower or "current" in user_lower:
            response = f"Market Data: {response}"
        
        return response