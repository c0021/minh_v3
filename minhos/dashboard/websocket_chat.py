"""
WebSocket endpoint for real-time chat interface.
"""

import asyncio
import json
import logging
from typing import Dict, Any
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from minhos.services.chat_service import get_chat_service
from minhos.core.nlp_provider import get_nlp_manager, initialize_nlp_providers
from minhos.core.config import get_config

logger = logging.getLogger(__name__)

# WebSocket router
websocket_router = APIRouter()

class ChatWebSocketManager:
    """Manages WebSocket connections for chat interface."""
    
    def __init__(self):
        self.chat_service = get_chat_service()
        self.logger = logging.getLogger("websocket.chat")
        
        # Initialize NLP providers
        try:
            config = get_config()
            initialize_nlp_providers(config)
            self.logger.info("NLP providers initialized for chat")
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP providers: {e}")
    
    async def handle_connection(self, websocket: WebSocket):
        """Handle a new WebSocket connection."""
        client_id = str(uuid.uuid4())
        
        try:
            # Connect to chat service
            await self.chat_service.connect_websocket(websocket, client_id)
            self.logger.info(f"Chat WebSocket connected: {client_id}")
            
            # Listen for messages
            while True:
                try:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Extract message content
                    message_type = message_data.get("type", "chat_message")
                    content = message_data.get("content", "").strip()
                    
                    if message_type == "chat_message" and content:
                        # Process chat message
                        await self.chat_service.handle_message(client_id, content)
                    
                    elif message_type == "ping":
                        # Respond to ping for connection health
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": "utcnow().isoformat()"
                        })
                    
                    elif message_type == "get_history":
                        # Send conversation history
                        if client_id in self.chat_service.conversation_contexts:
                            context = self.chat_service.conversation_contexts[client_id]
                            history = context.get_recent_context(20)
                            await websocket.send_json({
                                "type": "history",  
                                "messages": history
                            })
                    
                    elif message_type == "get_suggestions":
                        # Get smart command suggestions
                        partial_command = message_data.get("partial_command", "")
                        suggestions = await self.chat_service.get_smart_suggestions(client_id, partial_command)
                        await websocket.send_json({
                            "type": "suggestions",
                            "data": suggestions
                        })
                    
                except json.JSONDecodeError:
                    # Handle plain text messages (fallback)
                    if isinstance(data, str) and data.strip():
                        await self.chat_service.handle_message(client_id, data.strip())
                
                except WebSocketDisconnect:
                    break
                
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_id}: {e}")
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "content": "Error processing your message. Please try again.",
                            "timestamp": "utcnow().isoformat()"
                        })
                    except:
                        break  # Connection is broken
        
        except WebSocketDisconnect:
            self.logger.info(f"Chat WebSocket disconnected: {client_id}")
        
        except Exception as e:
            self.logger.error(f"Chat WebSocket error for {client_id}: {e}")
        
        finally:
            # Clean up connection
            await self.chat_service.disconnect_websocket(client_id)

# Global WebSocket manager instance
chat_ws_manager = ChatWebSocketManager()

@websocket_router.websocket("/ws/chat")
async def chat_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat interface."""
    await chat_ws_manager.handle_connection(websocket)

# Additional WebSocket endpoint for testing with client ID
@websocket_router.websocket("/ws/chat/{client_id}")
async def chat_websocket_with_id(websocket: WebSocket, client_id: str):
    """WebSocket endpoint with predefined client ID (for testing)."""
    chat_service = get_chat_service()
    
    try:
        await chat_service.connect_websocket(websocket, client_id)
        logger.info(f"Chat WebSocket connected with ID: {client_id}")
        
        while True:
            try:
                data = await websocket.receive_text()
                
                # Handle JSON messages
                try:
                    message_data = json.loads(data)
                    content = message_data.get("content", "").strip()
                    if content:
                        await chat_service.handle_message(client_id, content)
                except json.JSONDecodeError:
                    # Handle plain text
                    if data.strip():
                        await chat_service.handle_message(client_id, data.strip())
            
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in chat WebSocket {client_id}: {e}")
                break
    
    finally:
        await chat_service.disconnect_websocket(client_id)
        logger.info(f"Chat WebSocket {client_id} cleaned up")