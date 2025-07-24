"""
Chat service for natural language interaction with MinhOS trading system.
Provides WebSocket-based chat interface with API-agnostic NLP processing.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from fastapi import WebSocket, WebSocketDisconnect

from ..core.base_service import BaseService
from ..core.nlp_provider import get_nlp_manager, ParsedIntent, NLPResponse
from ..core.config import get_config

logger = logging.getLogger(__name__)

class ChatMessage:
    """Represents a chat message in the conversation."""
    
    def __init__(self, content: str, message_type: str, timestamp: datetime = None, 
                 metadata: Dict[str, Any] = None):
        self.content = content
        self.message_type = message_type  # 'user', 'ai', 'system', 'error'
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

class ConversationContext:
    """Manages conversation history and context for a chat session."""
    
    def __init__(self, max_history: int = 50):
        self.messages: List[ChatMessage] = []
        self.max_history = max_history
        self.session_start = datetime.utcnow()
        self.user_preferences = {}
        
    def add_message(self, message: ChatMessage):
        """Add a message to the conversation history."""
        self.messages.append(message)
        
        # Trim history if it gets too long
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_recent_context(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent messages for context."""
        recent = self.messages[-count:] if len(self.messages) >= count else self.messages
        return [msg.to_dict() for msg in recent]
    
    def get_trading_context(self) -> Dict[str, Any]:
        """Extract trading-relevant context from conversation."""
        context = {
            "session_duration": (datetime.utcnow() - self.session_start).total_seconds(),
            "message_count": len(self.messages),
            "recent_symbols": [],
            "recent_indicators": [],
            "common_intents": []
        }
        
        # Analyze recent messages for patterns
        recent_messages = self.messages[-10:]  # Last 10 messages
        for msg in recent_messages:
            if hasattr(msg, 'parsed_intent'):
                intent = msg.parsed_intent
                if intent.symbol:
                    context["recent_symbols"].append(intent.symbol)
                if intent.indicator:
                    context["recent_indicators"].append(intent.indicator)
                context["common_intents"].append(intent.intent)
        
        # Remove duplicates and get most common
        context["recent_symbols"] = list(set(context["recent_symbols"]))[-3:]
        context["recent_indicators"] = list(set(context["recent_indicators"]))[-3:]
        
        return context

class ChatService(BaseService):
    """Service for handling natural language chat interactions."""
    
    def __init__(self):
        super().__init__("chat_service")
        self.nlp_manager = get_nlp_manager()
        self.config = get_config()
        
        # Active WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
        # Service references (will be injected)
        self.ai_brain_service = None
        self.sierra_client = None
        self.decision_quality_framework = None
        self.trading_engine = None
        
        # Chat statistics
        self.stats = {
            "total_messages": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "active_sessions": 0,
            "avg_response_time": 0.0
        }
    
    def inject_dependencies(self, **services):
        """Inject service dependencies."""
        self.ai_brain_service = services.get('ai_brain_service')
        self.sierra_client = services.get('sierra_client')
        self.decision_quality_framework = services.get('decision_quality_framework')
        self.trading_engine = services.get('trading_engine')
        
        self.logger.info("Chat service dependencies injected")
    
    async def connect_websocket(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.conversation_contexts[client_id] = ConversationContext()
        self.stats["active_sessions"] = len(self.active_connections)
        
        self.logger.info(f"Chat client connected: {client_id}")
        
        # Send welcome message
        welcome_msg = ChatMessage(
            content="Welcome to MinhOS Chat! You can ask about market data, AI analysis, system status, or trading decisions. Try: 'Show me current market overview' or 'Explain the latest AI signal'",
            message_type="system"
        )
        await self._send_message(client_id, welcome_msg)
    
    async def disconnect_websocket(self, client_id: str):
        """Disconnect a WebSocket client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.conversation_contexts:
            del self.conversation_contexts[client_id]
        
        self.stats["active_sessions"] = len(self.active_connections)
        self.logger.info(f"Chat client disconnected: {client_id}")
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming chat message from client."""
        start_time = datetime.utcnow()
        
        try:
            self.stats["total_messages"] += 1
            
            # Add user message to context
            user_msg = ChatMessage(content=message, message_type="user")
            self.conversation_contexts[client_id].add_message(user_msg)
            
            # Parse intent using NLP manager
            context = self.conversation_contexts[client_id].get_trading_context()
            parsed_intent = await self.nlp_manager.parse_intent(message, context)
            user_msg.parsed_intent = parsed_intent
            
            # Route to appropriate handler based on intent
            response_data = await self._route_intent(parsed_intent, context)
            
            # Generate conversational response
            nlp_response = await self.nlp_manager.generate_response(
                response_data, 
                str(context), 
                message
            )
            
            # Create AI response message
            ai_msg = ChatMessage(
                content=nlp_response.content,
                message_type="ai",
                metadata={
                    "intent": parsed_intent.intent,
                    "symbol": parsed_intent.symbol,
                    "indicator": parsed_intent.indicator,
                    "confidence": parsed_intent.confidence,
                    "provider": nlp_response.provider,
                    "processing_time": nlp_response.processing_time
                }
            )
            
            # Add to context and send
            self.conversation_contexts[client_id].add_message(ai_msg)
            await self._send_message(client_id, ai_msg)
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.stats["successful_queries"] += 1
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["successful_queries"] - 1) + processing_time) /
                self.stats["successful_queries"]
            )
            
        except Exception as e:
            self.logger.error(f"Error handling chat message: {e}")
            self.stats["failed_queries"] += 1
            
            error_msg = ChatMessage(
                content="I encountered an error processing your request. Please try rephrasing or ask about something else.",
                message_type="error",
                metadata={"error": str(e)}
            )
            await self._send_message(client_id, error_msg)
    
    async def _route_intent(self, intent: ParsedIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route parsed intent to appropriate service handler."""
        
        if intent.intent == "query":
            return await self._handle_query(intent, context)
        elif intent.intent == "analyze":
            return await self._handle_analysis(intent, context)
        elif intent.intent == "explain":
            return await self._handle_explanation(intent, context)
        elif intent.intent == "alert":
            return await self._handle_alert(intent, context)
        else:
            return await self._handle_general_query(intent, context)
    
    async def _handle_query(self, intent: ParsedIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data query requests."""
        data = {}
        
        try:
            if intent.symbol and self.sierra_client:
                # Get symbol-specific data
                symbol_data = await self.sierra_client.get_symbol_data(intent.symbol)
                data["symbol_data"] = symbol_data
                data["symbol"] = intent.symbol
            
            if intent.indicator and self.ai_brain_service:
                # Get indicator analysis
                if intent.symbol:
                    indicator_data = await self.ai_brain_service.get_indicator_analysis(
                        intent.indicator, intent.symbol
                    )
                else:
                    indicator_data = await self.ai_brain_service.get_current_analysis()
                data["indicator_analysis"] = indicator_data
                data["indicator"] = intent.indicator
            
            if not intent.symbol and not intent.indicator:
                # General market overview
                if self.ai_brain_service:
                    data["ai_analysis"] = await self.ai_brain_service.get_current_analysis()
                if self.sierra_client:
                    data["market_snapshot"] = await self.sierra_client.get_market_snapshot()
        
        except Exception as e:
            self.logger.error(f"Query handling error: {e}")
            data["error"] = f"Unable to fetch requested data: {str(e)}"
        
        return data
    
    async def _handle_analysis(self, intent: ParsedIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis requests."""
        data = {}
        
        try:
            if self.ai_brain_service:
                # Get comprehensive AI analysis
                analysis = await self.ai_brain_service.analyze_conditions(
                    symbol=intent.symbol,
                    indicators=intent.indicator,
                    timeframe=intent.timeframe
                )
                data["ai_analysis"] = analysis
            
            if self.decision_quality_framework:
                # Include decision quality context
                quality_summary = await self.decision_quality_framework.get_current_summary()
                data["decision_quality"] = quality_summary
            
            if intent.symbol and self.sierra_client:
                # Add market context
                market_data = await self.sierra_client.get_symbol_data(intent.symbol)
                data["market_context"] = market_data
        
        except Exception as e:
            self.logger.error(f"Analysis handling error: {e}")
            data["error"] = f"Unable to perform analysis: {str(e)}"
        
        return data
    
    async def _handle_explanation(self, intent: ParsedIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle explanation requests."""
        data = {}
        
        try:
            if self.ai_brain_service:
                # Get latest AI reasoning
                current_analysis = await self.ai_brain_service.get_current_analysis()
                data["ai_reasoning"] = current_analysis
            
            if self.decision_quality_framework:
                # Get recent decision explanations
                recent_decisions = await self.decision_quality_framework.get_recent_decisions(5)
                data["recent_decisions"] = recent_decisions
            
            # Add context about what user might be asking about
            if intent.symbol:
                data["focus_symbol"] = intent.symbol
            if intent.indicator:
                data["focus_indicator"] = intent.indicator
        
        except Exception as e:
            self.logger.error(f"Explanation handling error: {e}")
            data["error"] = f"Unable to provide explanation: {str(e)}"
        
        return data
    
    async def _handle_alert(self, intent: ParsedIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle alert setup requests."""
        data = {
            "alert_request": {
                "symbol": intent.symbol,
                "indicator": intent.indicator,
                "parameters": intent.parameters,
                "status": "Alert functionality not yet implemented"
            }
        }
        
        # TODO: Implement alert system integration
        return data
    
    async def _handle_general_query(self, intent: ParsedIntent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries and system status requests."""
        data = {}
        
        try:
            # System status
            data["system_status"] = {
                "chat_service": "active",
                "active_sessions": self.stats["active_sessions"],
                "total_messages": self.stats["total_messages"],
                "success_rate": (
                    self.stats["successful_queries"] / max(1, self.stats["total_messages"]) * 100
                )
            }
            
            # Recent activity
            if hasattr(self, 'trading_engine') and self.trading_engine:
                data["recent_activity"] = await self.trading_engine.get_recent_activity()
        
        except Exception as e:
            self.logger.error(f"General query handling error: {e}")
            data["error"] = f"Unable to fetch system information: {str(e)}"
        
        return data
    
    async def _send_message(self, client_id: str, message: ChatMessage):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message.to_dict())
            except WebSocketDisconnect:
                await self.disconnect_websocket(client_id)
            except Exception as e:
                self.logger.error(f"Error sending message to {client_id}: {e}")
    
    async def broadcast_message(self, message: ChatMessage):
        """Broadcast message to all connected clients."""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message.to_dict())
            except WebSocketDisconnect:
                disconnected_clients.append(client_id)
            except Exception as e:
                self.logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect_websocket(client_id)
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status."""
        nlp_stats = await self.nlp_manager.get_provider_statistics()
        
        return {
            "service_name": self.service_name,
            "is_running": self.is_running,
            "stats": self.stats,
            "nlp_providers": nlp_stats,
            "active_sessions": len(self.active_connections),
            "conversation_contexts": len(self.conversation_contexts)
        }
    
    # Required abstract method implementations from BaseService
    
    async def _initialize(self):
        """Initialize service-specific components."""
        # Initialize NLP providers
        try:
            from ..core.nlp_provider import initialize_nlp_providers
            initialize_nlp_providers(self.config)
            self.logger.info("NLP providers initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP providers: {e}")
    
    async def _start_service(self):
        """Start service-specific functionality."""
        # Chat service starts when WebSocket connections are made
        # No additional startup required
        self.logger.info("Chat service ready to accept connections")
    
    async def _stop_service(self):
        """Stop service-specific functionality."""
        # Disconnect all active WebSocket connections
        disconnected_clients = list(self.active_connections.keys())
        for client_id in disconnected_clients:
            await self.disconnect_websocket(client_id)
        
        self.logger.info(f"Disconnected {len(disconnected_clients)} chat clients")
    
    async def _cleanup(self):
        """Cleanup service resources."""
        # Clear conversation contexts
        self.conversation_contexts.clear()
        
        # Reset statistics
        self.stats = {
            "total_messages": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "active_sessions": 0,
            "avg_response_time": 0.0
        }
        
        self.logger.info("Chat service cleanup completed")

# Singleton instance
_chat_service: Optional[ChatService] = None

def get_chat_service() -> ChatService:
    """Get global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service