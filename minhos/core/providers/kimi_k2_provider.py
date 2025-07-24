"""
Kimi K2 (Moonshot AI) provider implementation.
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..nlp_provider import NLPProvider, ParsedIntent, NLPResponse

logger = logging.getLogger(__name__)

class KimiK2Provider(NLPProvider):
    """Kimi K2 API provider for natural language processing."""
    
    def __init__(self, config):
        super().__init__("kimi_k2")
        self.api_key = config.kimi_k2_api_key
        self.base_url = config.kimi_k2_base_url
        self.model = getattr(config, 'kimi_k2_model', 'moonshot-v1-8k')
        self.timeout = getattr(config, 'request_timeout', 30.0)
        self.max_retries = 3
        
        # Rate limiting
        self.max_requests_per_minute = getattr(config, 'max_requests_per_minute', 50)
        self.request_timestamps = []
        
        # Health tracking
        self.last_health_check = None
        self.consecutive_failures = 0
        self.is_healthy = True
    
    async def parse_intent(self, user_input: str, context: Dict[str, Any] = None) -> ParsedIntent:
        """Parse user input into structured trading intent using Kimi K2."""
        system_prompt = """You are a trading system command parser. Extract trading intent from natural language.

Return JSON with this exact structure:
{
    "intent": "query|analyze|explain|execute|alert",
    "symbol": "STOCK_TICKER or null",
    "indicator": "RSI|SMA|EMA|MACD|volume|pattern|volatility or null", 
    "parameters": {
        "threshold": number_if_mentioned,
        "timeframe": "1m|5m|15m|1h|4h|1d if mentioned",
        "condition": "above|below|crosses|breaks if mentioned"
    },
    "confidence": 0.0-1.0
}

Examples:
"Show me NVDA RSI" -> {"intent": "query", "symbol": "NVDA", "indicator": "RSI", "confidence": 0.9}
"Alert when SPY breaks 450" -> {"intent": "alert", "symbol": "SPY", "parameters": {"threshold": 450, "condition": "breaks"}, "confidence": 0.85}
"Explain why AI is bullish" -> {"intent": "explain", "confidence": 0.8}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse this trading command: '{user_input}'"}
        ]
        
        try:
            response = await self._make_api_request(messages)
            response_content = response.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            # Parse JSON response
            try:
                parsed_data = json.loads(response_content)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                parsed_data = self._fallback_intent_parsing(user_input)
            
            return ParsedIntent(
                intent=parsed_data.get('intent', 'query'),
                symbol=parsed_data.get('symbol'),
                indicator=parsed_data.get('indicator'),
                parameters=parsed_data.get('parameters', {}),
                timeframe=parsed_data.get('parameters', {}).get('timeframe'),
                confidence=parsed_data.get('confidence', 0.5),
                raw_input=user_input
            )
            
        except Exception as e:
            self.logger.error(f"Intent parsing failed: {e}")
            self.consecutive_failures += 1
            return self._fallback_intent_parsing(user_input)
    
    async def generate_response(self, data: Dict[str, Any], context: str, user_input: str = "") -> NLPResponse:
        """Generate conversational response from technical data using Kimi K2."""
        system_prompt = """You are a professional trading assistant. Convert technical analysis data into clear, conversational responses.

Guidelines:
- Be precise and actionable
- Include specific numbers and confidence levels when available
- Explain technical terms briefly
- Maintain professional trading context
- Keep responses concise but informative
- Always include reasoning when making assessments
"""
        
        user_prompt = f"""
Technical Data: {json.dumps(data, indent=2)}
User Query: "{user_input}"
Context: {context}

Convert this technical data into a natural, informative response that directly addresses the user's query. Include specific values, confidence levels, and actionable insights.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            start_time = datetime.utcnow()
            response = await self._make_api_request(messages)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
            
            return NLPResponse(
                content=content,
                confidence=0.8,  # High confidence for successful API response
                provider=self.name,
                processing_time=processing_time,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            self.consecutive_failures += 1
            
            # Fallback response
            return NLPResponse(
                content=f"Technical Analysis Summary: {self._format_fallback_response(data)}",
                confidence=0.3,
                provider=f"{self.name}_fallback",
                processing_time=0.0
            )
    
    async def is_available(self) -> bool:
        """Check if Kimi K2 API is available and healthy."""
        # Check rate limiting
        now = datetime.utcnow()
        self.request_timestamps = [ts for ts in self.request_timestamps if (now - ts).total_seconds() < 60]
        
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            return False
        
        # Quick health check if we haven't checked recently
        if (self.last_health_check is None or 
            (now - self.last_health_check).total_seconds() > 300):  # 5 minutes
            await self._perform_health_check()
        
        return self.is_healthy and self.consecutive_failures < 5
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health and performance metrics."""
        await self._perform_health_check()
        
        return {
            "is_healthy": self.is_healthy,
            "consecutive_failures": self.consecutive_failures,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "rate_limit_remaining": max(0, self.max_requests_per_minute - len(self.request_timestamps)),
            "max_requests_per_minute": self.max_requests_per_minute,
            "api_endpoint": self.base_url
        }
    
    async def _make_api_request(self, messages: list) -> Dict[str, Any]:
        """Make authenticated request to Kimi K2 API."""
        # Rate limiting check
        now = datetime.utcnow()
        self.request_timestamps.append(now)
        self.request_timestamps = [ts for ts in self.request_timestamps if (now - ts).total_seconds() < 60]
        
        if len(self.request_timestamps) > self.max_requests_per_minute:
            raise Exception("Rate limit exceeded")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,  # Lower temperature for more consistent responses
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.post(f"{self.base_url}/chat/completions", 
                                          headers=headers, 
                                          json=payload) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            self.consecutive_failures = 0  # Reset failure count on success
                            return result
                        elif response.status == 429:  # Rate limited
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            else:
                                raise Exception("Rate limited after retries")
                        else:
                            error_text = await response.text()
                            raise Exception(f"API error {response.status}: {error_text}")
                
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    else:
                        raise Exception("Request timeout after retries")
    
    async def _perform_health_check(self):
        """Perform a lightweight health check of the API."""
        try:
            test_messages = [
                {"role": "user", "content": "Respond with 'healthy' if you're working correctly."}
            ]
            
            response = await self._make_api_request(test_messages)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '').lower()
            
            self.is_healthy = 'healthy' in content or len(content) > 0
            self.last_health_check = datetime.utcnow()
            
            if self.is_healthy:
                self.consecutive_failures = 0
                
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            self.is_healthy = False
            self.consecutive_failures += 1
            self.last_health_check = datetime.utcnow()
    
    def _fallback_intent_parsing(self, user_input: str) -> ParsedIntent:
        """Basic intent parsing when API is unavailable."""
        user_lower = user_input.lower()
        
        # Simple keyword-based parsing
        intent = "query"
        if any(word in user_lower for word in ["explain", "why", "how"]):
            intent = "explain"
        elif any(word in user_lower for word in ["analyze", "analysis"]):
            intent = "analyze"
        elif any(word in user_lower for word in ["alert", "notify", "when"]):
            intent = "alert"
        
        # Extract symbol (very basic)
        import re
        symbol_match = re.search(r'\b([A-Z]{1,5})\b', user_input.upper())
        symbol = symbol_match.group(1) if symbol_match else None
        
        # Extract indicator
        indicator = None
        for ind in ["RSI", "SMA", "EMA", "MACD", "volume", "volatility"]:
            if ind.lower() in user_lower:
                indicator = ind
                break
        
        return ParsedIntent(
            intent=intent,
            symbol=symbol,
            indicator=indicator,
            confidence=0.3,  # Low confidence for fallback parsing
            raw_input=user_input
        )
    
    def _format_fallback_response(self, data: Dict[str, Any]) -> str:
        """Format basic response when API is unavailable."""
        if not data:
            return "No technical data available."
        
        parts = []
        
        # Basic data formatting
        for key, value in data.items():
            if isinstance(value, (int, float)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, str):
                parts.append(f"{key}: {value}")
        
        return " | ".join(parts[:5])  # Limit to first 5 items