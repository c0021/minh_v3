"""
Emergency fallback NLP provider that works without any external dependencies.
This provider uses rule-based parsing and templates to provide basic chat functionality
when all other providers are unavailable.
"""

import re
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..nlp_provider import NLPProvider, ParsedIntent, NLPResponse

logger = logging.getLogger(__name__)

class EmergencyFallbackProvider(NLPProvider):
    """
    Emergency fallback provider that always works without external dependencies.
    Uses rule-based parsing and response templates.
    """
    
    def __init__(self):
        super().__init__("emergency_fallback")
        self.logger.info("Emergency fallback provider initialized")
    
    async def parse_intent(self, user_input: str, context: Dict[str, Any] = None) -> ParsedIntent:
        """Parse user input using comprehensive rule-based analysis."""
        user_lower = user_input.lower().strip()
        
        # Determine intent based on keywords and patterns
        intent = self._classify_intent(user_lower)
        
        # Extract symbol
        symbol = self._extract_symbol(user_input)
        
        # Extract indicator
        indicator = self._extract_indicator(user_lower)
        
        # Extract parameters
        parameters = self._extract_parameters(user_input, user_lower)
        
        # Calculate confidence based on how many elements we found
        confidence = self._calculate_confidence(intent, symbol, indicator, parameters)
        
        return ParsedIntent(
            intent=intent,
            symbol=symbol,
            indicator=indicator,
            parameters=parameters,
            timeframe=parameters.get('timeframe'),
            confidence=confidence,
            raw_input=user_input
        )
    
    async def generate_response(self, data: Dict[str, Any], context: str, user_input: str = "") -> NLPResponse:
        """Generate response using templates and data formatting."""
        start_time = datetime.utcnow()
        
        # Choose appropriate response template based on data type
        response = self._generate_contextual_response(data, user_input, context)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return NLPResponse(
            content=response,
            confidence=0.7,  # Good confidence for rule-based responses
            provider=self.name,
            processing_time=processing_time,
            tokens_used=0
        )
    
    async def is_available(self) -> bool:
        """Emergency fallback is always available."""
        return True
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Emergency fallback is always healthy."""
        return {
            "is_healthy": True,
            "provider_type": "emergency_fallback",
            "external_dependencies": False,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def _classify_intent(self, user_lower: str) -> str:
        """Classify user intent based on keywords and patterns."""
        
        # Question patterns for explain intent
        if any(pattern in user_lower for pattern in [
            "what", "why", "how", "explain", "tell me about", "describe",
            "what's", "how's", "why is", "what does", "how does"
        ]):
            return "explain"
        
        # Analysis patterns
        if any(pattern in user_lower for pattern in [
            "analyze", "analysis", "look at", "examine", "study", 
            "check", "review", "assess", "evaluate"
        ]):
            return "analyze"
        
        # Alert/notification patterns
        if any(pattern in user_lower for pattern in [
            "alert", "notify", "when", "if", "trigger", "warn",
            "let me know", "tell me when"
        ]):
            return "alert"
        
        # Execute/action patterns
        if any(pattern in user_lower for pattern in [
            "buy", "sell", "trade", "execute", "place", "order",
            "position", "close", "open"
        ]):
            return "execute"
        
        # Default to query
        return "query"
    
    def _extract_symbol(self, user_input: str) -> Optional[str]:
        """Extract trading symbol from user input."""
        # Common symbol patterns - try specific patterns first
        specific_patterns = [
            r'\b(NQ|ES|YM|RTY)\d*\b',  # Futures symbols
            r'\b(SPY|QQQ|IWM|GLD|SLV|TLT|VIX|DIA|XLF|XLE|XLI|XLK|XLU|XLV|XLY|XLP|XLB|XLRE)\b',  # Common ETFs
            r'\b(AAPL|NVDA|MSFT|GOOGL|GOOGL|AMZN|TSLA|META|NFLX|AMD|INTC|CRM|ORCL|ADBE|PYPL|DIS|V|MA|JPM|BAC|WFC|KO|PFE|JNJ|UNH|HD|WMT|PG)\b'  # Common stocks  
        ]
        
        # Try specific patterns first
        for pattern in specific_patterns:
            match = re.search(pattern, user_input.upper())
            if match:
                return match.group(1)
        
        # General pattern with extensive filtering
        general_match = re.search(r'\b([A-Z]{2,5})\b', user_input.upper())
        if general_match:
            symbol = general_match.group(1)
            # Extensive filter for common false positives
            false_positives = {
                'THE', 'AND', 'FOR', 'YOU', 'ARE', 'HOW', 'WHY', 'WHAT', 'WHERE', 'WHEN',
                'THIS', 'THAT', 'WITH', 'FROM', 'THEY', 'HAVE', 'BEEN', 'WILL', 'WERE',
                'SHOW', 'TELL', 'GIVE', 'TAKE', 'MAKE', 'COME', 'WANT', 'NEED', 'KNOW',
                'THINK', 'FIND', 'WORK', 'LOOK', 'SEEM', 'FEEL', 'TRY', 'LEAVE', 'CALL',
                'BUY', 'SELL', 'GET', 'PUT', 'SET', 'LET', 'SAY', 'MAY', 'WAY', 'DAY',
                'NEW', 'OLD', 'GOOD', 'BAD', 'HIGH', 'LOW', 'BIG', 'SMALL', 'LONG', 'SHORT',
                'CURRENT', 'MARKET', 'PRICE', 'DATA', 'TIME', 'NOW', 'TODAY', 'SYSTEM'
            }
            
            if symbol not in false_positives and len(symbol) >= 2:
                return symbol
        
        return None
    
    def _extract_indicator(self, user_lower: str) -> Optional[str]:
        """Extract technical indicator from user input."""
        indicators = {
            'rsi': ['rsi', 'relative strength'],
            'sma': ['sma', 'simple moving average', 'moving average'],
            'ema': ['ema', 'exponential moving average'],
            'macd': ['macd', 'moving average convergence'],
            'volume': ['volume', 'vol'],
            'volatility': ['volatility', 'vol', 'vix'],
            'pattern': ['pattern', 'formation', 'setup'],
            'support': ['support', 'floor'],
            'resistance': ['resistance', 'ceiling'],
            'trend': ['trend', 'direction']
        }
        
        for indicator, keywords in indicators.items():
            if any(keyword in user_lower for keyword in keywords):
                return indicator.upper()
        
        return None
    
    def _extract_parameters(self, user_input: str, user_lower: str) -> Dict[str, Any]:
        """Extract parameters like numbers, timeframes, conditions."""
        parameters = {}
        
        # Extract numbers
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', user_input)
        if numbers:
            parameters['threshold'] = float(numbers[0])
        
        # Extract timeframes
        timeframes = {
            '1m': ['1m', '1 minute', 'one minute'],
            '5m': ['5m', '5 minute', 'five minute'],  
            '15m': ['15m', '15 minute', 'fifteen minute'],
            '1h': ['1h', '1 hour', 'one hour', 'hourly'],
            '4h': ['4h', '4 hour', 'four hour'],
            '1d': ['1d', '1 day', 'daily', 'day']
        }
        
        for tf, keywords in timeframes.items():
            if any(keyword in user_lower for keyword in keywords):
                parameters['timeframe'] = tf
                break
        
        # Extract conditions
        if any(word in user_lower for word in ['above', 'over', 'higher than']):
            parameters['condition'] = 'above'
        elif any(word in user_lower for word in ['below', 'under', 'lower than']):
            parameters['condition'] = 'below'
        elif any(word in user_lower for word in ['crosses', 'cross']):
            parameters['condition'] = 'crosses'
        elif any(word in user_lower for word in ['breaks', 'break']):
            parameters['condition'] = 'breaks'
        
        return parameters
    
    def _calculate_confidence(self, intent: str, symbol: Optional[str], 
                            indicator: Optional[str], parameters: Dict[str, Any]) -> float:
        """Calculate confidence based on extracted elements."""
        base_confidence = 0.5
        
        # Boost confidence for each element found
        if intent != "query":  # Non-default intent
            base_confidence += 0.1
        if symbol:
            base_confidence += 0.2
        if indicator:
            base_confidence += 0.2
        if parameters:
            base_confidence += 0.1 * len(parameters)
        
        return min(base_confidence, 0.9)  # Cap at 0.9
    
    def _generate_contextual_response(self, data: Dict[str, Any], user_input: str, context: str) -> str:
        """Generate contextual response based on data and user query."""
        user_lower = user_input.lower()
        
        # Handle empty or error data
        if not data:
            return self._get_no_data_response(user_input)
        
        if 'error' in data:
            return f"I encountered an error: {data['error']}. Please try rephrasing your question or check if the system is running properly."
        
        # Market data response
        if 'market_snapshot' in data or 'symbol_data' in data:
            return self._format_market_data_response(data, user_input)
        
        # AI analysis response
        if 'ai_analysis' in data or 'current_signal' in data:
            return self._format_ai_analysis_response(data, user_input)
        
        # System status response
        if 'system_status' in data or 'active_sessions' in data:
            return self._format_system_status_response(data, user_input)
        
        # Decision quality response
        if 'decision_quality' in data or 'recent_decisions' in data:
            return self._format_decision_quality_response(data, user_input)
        
        # Pattern analysis response
        if 'current_patterns' in data or 'pattern_performance' in data:
            return self._format_pattern_response(data, user_input)
        
        # Default response for unrecognized data
        return self._format_generic_response(data, user_input)
    
    def _get_no_data_response(self, user_input: str) -> str:
        """Handle cases where no data is available."""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['market', 'price', 'current']):
            return "I don't have current market data available. Please check that the Sierra Chart connection is active and data is flowing."
        elif any(word in user_lower for word in ['ai', 'signal', 'analysis']):
            return "AI analysis data is not currently available. Please ensure the AI Brain service is running and processing market data."
        elif any(word in user_lower for word in ['system', 'status', 'health']):
            return "System status information is not available. Please check that all MinhOS services are running properly."
        else:
            return "I don't have the requested information available right now. Please ensure all MinhOS services are running and try again."
    
    def _format_market_data_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format market data into readable response."""
        response_parts = ["**Market Overview:**"]
        
        # Handle market_snapshot data
        if 'market_snapshot' in data and data['market_snapshot']:
            snapshot = data['market_snapshot']
            if 'price' in snapshot:
                response_parts.append(f"Current price: ${snapshot['price']:.2f}")
            if 'volume' in snapshot:
                response_parts.append(f"Volume: {snapshot['volume']:,}")
            if 'connected' in snapshot:
                status = "Connected" if snapshot['connected'] else "Disconnected"
                response_parts.append(f"Status: {status}")
        
        # Handle symbol_data
        if 'symbol_data' in data and data['symbol_data']:
            symbol_data = data['symbol_data']
            if 'symbol' in symbol_data:
                response_parts.append(f"Symbol: {symbol_data['symbol']}")
            if 'last_update' in symbol_data:
                response_parts.append(f"Last updated: {symbol_data['last_update']}")
        
        if len(response_parts) == 1:
            return "Market data is available but contains no displayable information."
        
        return " | ".join(response_parts)
    
    def _format_ai_analysis_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format AI analysis into readable response.""" 
        response_parts = ["**AI Analysis:**"]
        
        if 'ai_analysis' in data and data['ai_analysis']:
            analysis = data['ai_analysis']
            if 'signal' in analysis and analysis['signal']:
                signal = analysis['signal']
                response_parts.append(f"Signal: {signal.get('signal', 'Unknown')}")
                if 'confidence' in signal:
                    response_parts.append(f"Confidence: {signal['confidence']:.1%}")
                if 'reasoning' in signal:
                    response_parts.append(f"Reasoning: {signal['reasoning'][:100]}...")
        
        if 'current_signal' in data and data['current_signal']:
            signal = data['current_signal']
            if 'signal' in signal:
                response_parts.append(f"Current signal: {signal['signal']}")
            if 'confidence' in signal:
                response_parts.append(f"Confidence: {signal['confidence']:.1%}")
        
        if len(response_parts) == 1:
            return "AI analysis is active but no specific signals are currently available."
        
        return " | ".join(response_parts)
    
    def _format_system_status_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format system status into readable response."""
        response_parts = ["**System Status:**"]
        
        if 'system_status' in data:
            status = data['system_status']
            if 'chat_service' in status:
                response_parts.append(f"Chat: {status['chat_service']}")
            if 'active_sessions' in status:
                response_parts.append(f"Active sessions: {status['active_sessions']}")
            if 'success_rate' in status:
                response_parts.append(f"Success rate: {status['success_rate']:.1f}%")
        
        if 'active_sessions' in data:
            response_parts.append(f"Chat sessions: {data['active_sessions']}")
        
        if len(response_parts) == 1:
            return "System is running. All core services appear to be operational."
        
        return " | ".join(response_parts)
    
    def _format_decision_quality_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format decision quality metrics into readable response."""
        response_parts = ["**Decision Quality:**"]
        
        if 'decision_quality' in data and data['decision_quality']:
            quality = data['decision_quality']
            if 'average_quality' in quality:
                avg = quality['average_quality']
                response_parts.append(f"Average quality: {avg:.2f}")
            if 'total_decisions' in quality:
                response_parts.append(f"Total decisions: {quality['total_decisions']}")
            if 'strongest_area' in quality:
                response_parts.append(f"Strongest: {quality['strongest_area']}")
            if 'weakest_area' in quality:
                response_parts.append(f"Weakest: {quality['weakest_area']}")
        
        if len(response_parts) == 1:
            return "Decision quality tracking is active but no metrics are currently available."
        
        return " | ".join(response_parts)
    
    def _format_pattern_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format pattern analysis into readable response."""
        response_parts = ["**Pattern Analysis:**"]
        
        if 'current_patterns' in data:
            patterns = data['current_patterns']
            if isinstance(patterns, list):
                response_parts.append(f"Patterns detected: {len(patterns)}")
            elif isinstance(patterns, dict):
                response_parts.append(f"Pattern types: {len(patterns)}")
        
        if 'pattern_performance' in data:
            performance = data['pattern_performance']
            if isinstance(performance, dict) and performance:
                avg_performance = sum(performance.values()) / len(performance)
                response_parts.append(f"Average success rate: {avg_performance:.1%}")
        
        if len(response_parts) == 1:
            return "Pattern analysis is running but no patterns are currently detected."
        
        return " | ".join(response_parts)
    
    def _format_generic_response(self, data: Dict[str, Any], user_input: str) -> str:
        """Format generic data response."""
        if not data:
            return "No information is currently available."
        
        # Count available data points
        data_points = len([k for k, v in data.items() if v is not None])
        
        if data_points == 0:
            return "Data is available but contains no usable information at the moment."
        
        # Try to extract key-value pairs for display
        display_items = []
        for key, value in list(data.items())[:5]:  # Limit to first 5 items
            if isinstance(value, (int, float)):
                display_items.append(f"{key}: {value:.2f}")
            elif isinstance(value, str) and len(value) < 30:
                display_items.append(f"{key}: {value}")
            elif isinstance(value, bool):
                display_items.append(f"{key}: {'Yes' if value else 'No'}")
        
        if display_items:
            return f"Available data: {' | '.join(display_items)}"
        else:
            return f"I have {data_points} data points available, but they're too complex to summarize briefly. Please ask a more specific question."