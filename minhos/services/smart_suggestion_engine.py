#!/usr/bin/env python3
"""
Smart Command Suggestion Engine
==============================

Context-aware command suggestion system for MinhOS chat interface.
Provides intelligent autocomplete based on market state, ML analysis, and trading context.

Features:
- Market state analysis for contextual suggestions
- ML integration for probability-based recommendations  
- Historical command pattern learning
- Real-time suggestion ranking
- Adaptive suggestion weighting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict, Counter
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class SuggestionType(Enum):
    """Types of command suggestions"""
    TRADING_ACTION = "trading_action"      # Buy, sell, close position
    MARKET_ANALYSIS = "market_analysis"    # Get price, analyze trend  
    RISK_MANAGEMENT = "risk_management"    # Check exposure, set stops
    SYSTEM_STATUS = "system_status"        # System health, ML status
    ML_INSIGHT = "ml_insight"             # LSTM prediction, Kelly sizing
    POSITION_QUERY = "position_query"      # Current positions, P&L


@dataclass
class SuggestionContext:
    """Current context for generating suggestions"""
    market_price: float
    price_change: float
    volume_trend: str
    volatility_level: str
    ml_signal: Optional[str] = None
    ml_confidence: float = 0.0
    current_positions: int = 0
    account_exposure: float = 0.0
    recent_commands: List[str] = None
    session_duration: int = 0  # minutes
    
    def __post_init__(self):
        if self.recent_commands is None:
            self.recent_commands = []


@dataclass 
class CommandSuggestion:
    """A single command suggestion"""
    command: str
    description: str
    suggestion_type: SuggestionType
    relevance_score: float
    context_match: Dict[str, Any]
    example_usage: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "description": self.description,
            "type": self.suggestion_type.value,
            "relevance": self.relevance_score,
            "context": self.context_match,
            "example": self.example_usage
        }


class SmartSuggestionEngine:
    """
    Intelligent command suggestion engine with ML integration
    
    Analyzes current market state, trading context, and ML signals to provide
    contextually relevant command suggestions for the chat interface.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "/home/colindo/Sync/minh_v4/data/suggestions.db"
        
        # Command patterns and templates
        self.command_templates = self._initialize_command_templates()
        self.contextual_triggers = self._initialize_contextual_triggers()
        
        # Learning and adaptation
        self.command_usage_history = defaultdict(int)
        self.success_patterns = defaultdict(list)
        self.user_preferences = {}
        
        # Initialize database
        self._init_database()
        
        logger.info("Smart Suggestion Engine initialized")
    
    def _init_database(self):
        """Initialize suggestion database for learning and persistence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Command usage tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context_data TEXT,
                    success_rating INTEGER DEFAULT 0,
                    user_session TEXT
                )
            """)
            
            # Suggestion effectiveness tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestion_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggested_command TEXT NOT NULL,
                    was_used BOOLEAN DEFAULT FALSE,
                    context_match_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_feedback INTEGER DEFAULT 0
                )
            """)
            
            # User preference learning
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    preference_key TEXT PRIMARY KEY,
                    preference_value TEXT,
                    confidence_score REAL DEFAULT 0.5,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Suggestion database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize suggestion database: {e}")
    
    def _initialize_command_templates(self) -> Dict[SuggestionType, List[Dict]]:
        """Initialize command templates for different suggestion types"""
        return {
            SuggestionType.TRADING_ACTION: [
                {
                    "pattern": "buy {symbol}",
                    "description": "Open a long position on {symbol}",
                    "triggers": ["price_breakout", "bullish_signal", "support_bounce"],
                    "example": "buy NQU25-CME at market price"
                },
                {
                    "pattern": "sell {symbol}",
                    "description": "Open a short position on {symbol}",  
                    "triggers": ["price_breakdown", "bearish_signal", "resistance_rejection"],
                    "example": "sell NQU25-CME at current levels"
                },
                {
                    "pattern": "close position {symbol}",
                    "description": "Close existing position in {symbol}",
                    "triggers": ["profit_target", "stop_loss", "reversal_signal"],
                    "example": "close position NQU25-CME"
                },
                {
                    "pattern": "set stop loss {price}",
                    "description": "Set protective stop loss at {price}",
                    "triggers": ["new_position", "risk_management"],
                    "example": "set stop loss 23450"
                }
            ],
            
            SuggestionType.MARKET_ANALYSIS: [
                {
                    "pattern": "analyze {symbol}",
                    "description": "Get comprehensive market analysis for {symbol}",
                    "triggers": ["market_open", "volatility_spike", "news_event"],
                    "example": "analyze NQU25-CME current trend"
                },
                {
                    "pattern": "get price {symbol}",
                    "description": "Get current price and bid/ask for {symbol}",
                    "triggers": ["price_check", "order_preparation"],
                    "example": "get price NQU25-CME"
                },
                {
                    "pattern": "trend analysis",
                    "description": "Analyze current market trend direction",
                    "triggers": ["directional_uncertainty", "strategy_planning"],
                    "example": "trend analysis for current market"
                },
                {
                    "pattern": "volume analysis",
                    "description": "Analyze current volume patterns",
                    "triggers": ["volume_spike", "confirmation_needed"],
                    "example": "volume analysis for recent price move"
                }
            ],
            
            SuggestionType.ML_INSIGHT: [
                {
                    "pattern": "lstm prediction",
                    "description": "Get LSTM neural network price prediction",
                    "triggers": ["ml_analysis", "direction_uncertainty"],
                    "example": "lstm prediction for next 30 minutes"
                },
                {
                    "pattern": "ensemble forecast",
                    "description": "Get ensemble model market forecast",
                    "triggers": ["comprehensive_analysis", "model_consensus"],
                    "example": "ensemble forecast for market direction"
                },
                {
                    "pattern": "kelly position size",
                    "description": "Calculate optimal position size using Kelly Criterion",
                    "triggers": ["position_sizing", "risk_optimization"],
                    "example": "kelly position size for 65% confidence signal"
                },
                {
                    "pattern": "ml confidence check",
                    "description": "Check current ML model confidence levels",
                    "triggers": ["model_validation", "signal_quality"],
                    "example": "ml confidence check for current signals"
                }
            ],
            
            SuggestionType.RISK_MANAGEMENT: [
                {
                    "pattern": "check exposure",
                    "description": "Review current market exposure and risk",
                    "triggers": ["risk_review", "position_audit"],
                    "example": "check exposure across all positions"
                },
                {
                    "pattern": "risk assessment",
                    "description": "Comprehensive risk analysis of current positions",
                    "triggers": ["volatility_increase", "market_stress"],
                    "example": "risk assessment for current portfolio"
                },
                {
                    "pattern": "position limits",
                    "description": "Check position size limits and utilization",
                    "triggers": ["limit_monitoring", "capacity_planning"],
                    "example": "position limits for NQU25-CME"
                }
            ],
            
            SuggestionType.SYSTEM_STATUS: [
                {
                    "pattern": "system status",
                    "description": "Check overall system health and connectivity",
                    "triggers": ["health_check", "troubleshooting"],
                    "example": "system status and service health"
                },
                {
                    "pattern": "ml status",
                    "description": "Check ML model status and performance",
                    "triggers": ["ml_health", "model_monitoring"],
                    "example": "ml status for all models"
                },
                {
                    "pattern": "data feed status",
                    "description": "Check market data feed connectivity",
                    "triggers": ["data_issues", "connectivity_check"],
                    "example": "data feed status for Sierra Chart"
                }
            ],
            
            SuggestionType.POSITION_QUERY: [
                {
                    "pattern": "show positions",
                    "description": "Display all current trading positions",
                    "triggers": ["portfolio_review", "status_check"],
                    "example": "show positions with P&L"
                },
                {
                    "pattern": "pnl summary",
                    "description": "Show profit and loss summary",
                    "triggers": ["performance_review", "accounting"],
                    "example": "pnl summary for today"
                }
            ]
        }
    
    def _initialize_contextual_triggers(self) -> Dict[str, List[str]]:
        """Initialize contextual triggers that suggest specific command types"""
        return {
            # Market condition triggers
            "high_volatility": ["risk_assessment", "position_limits", "ml_confidence_check"],
            "price_breakout": ["buy", "trend_analysis", "volume_analysis"],
            "price_breakdown": ["sell", "trend_analysis", "stop_loss"],
            "volume_spike": ["volume_analysis", "analyze", "ml_insight"],
            
            # ML signal triggers  
            "high_ml_confidence": ["lstm_prediction", "kelly_position_size", "trading_action"],
            "low_ml_confidence": ["ml_status", "ensemble_forecast", "risk_assessment"],
            "ml_agreement": ["kelly_position_size", "trading_action"],
            "ml_disagreement": ["ml_confidence_check", "trend_analysis"],
            
            # Position triggers
            "new_session": ["system_status", "show_positions", "market_analysis"],
            "large_position": ["risk_assessment", "check_exposure", "set_stop_loss"],
            "no_positions": ["analyze", "lstm_prediction", "market_opportunities"],
            
            # Time-based triggers
            "market_open": ["system_status", "trend_analysis", "volume_analysis"],
            "market_close": ["pnl_summary", "risk_assessment", "position_review"],
            "session_start": ["system_status", "show_positions", "ml_status"]
        }
    
    async def get_smart_suggestions(self, 
                                  partial_command: str,
                                  context: SuggestionContext,
                                  max_suggestions: int = 5) -> List[CommandSuggestion]:
        """
        Generate smart command suggestions based on context and partial input
        
        Args:
            partial_command: Partially typed command from user
            context: Current market and trading context
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of ranked command suggestions
        """
        try:
            # Generate base suggestions
            suggestions = []
            
            # 1. Pattern matching for partial commands
            pattern_suggestions = await self._get_pattern_based_suggestions(partial_command)
            suggestions.extend(pattern_suggestions)
            
            # 2. Context-driven suggestions  
            context_suggestions = await self._get_context_driven_suggestions(context)
            suggestions.extend(context_suggestions)
            
            # 3. ML-enhanced suggestions
            ml_suggestions = await self._get_ml_enhanced_suggestions(context)
            suggestions.extend(ml_suggestions)
            
            # 4. Historical pattern suggestions
            history_suggestions = await self._get_historical_suggestions(context)
            suggestions.extend(history_suggestions)
            
            # Rank and filter suggestions
            ranked_suggestions = await self._rank_suggestions(suggestions, partial_command, context)
            
            # Remove duplicates and limit results
            unique_suggestions = self._deduplicate_suggestions(ranked_suggestions)
            
            return unique_suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating smart suggestions: {e}")
            return []
    
    async def _get_pattern_based_suggestions(self, partial_command: str) -> List[CommandSuggestion]:
        """Generate suggestions based on command pattern matching"""
        suggestions = []
        partial_lower = partial_command.lower().strip()
        
        if not partial_lower:
            return suggestions
            
        # Search through all command templates
        for suggestion_type, templates in self.command_templates.items():
            for template in templates:
                pattern = template["pattern"].lower()
                
                # Check if partial command matches beginning of pattern
                if pattern.startswith(partial_lower) or partial_lower in pattern:
                    # Calculate relevance based on match quality
                    if pattern.startswith(partial_lower):
                        relevance = 0.9  # High relevance for prefix match
                    else:
                        relevance = 0.6  # Medium relevance for substring match
                    
                    # Fill template variables
                    filled_command = self._fill_template_variables(template["pattern"])
                    
                    suggestion = CommandSuggestion(
                        command=filled_command,
                        description=template["description"].format(symbol="NQU25-CME"),
                        suggestion_type=suggestion_type,
                        relevance_score=relevance,
                        context_match={"match_type": "pattern", "triggers": template["triggers"]},
                        example_usage=template["example"]
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    async def _get_context_driven_suggestions(self, context: SuggestionContext) -> List[CommandSuggestion]:
        """Generate suggestions based on current market context"""
        suggestions = []
        
        # Analyze context and determine relevant triggers
        active_triggers = []
        
        # Market condition analysis
        if abs(context.price_change) > 0.5:  # Significant price movement
            if context.price_change > 0:
                active_triggers.append("price_breakout")
            else:
                active_triggers.append("price_breakdown")
        
        if context.volatility_level == "high":
            active_triggers.append("high_volatility")
            
        if context.volume_trend == "spike":
            active_triggers.append("volume_spike")
        
        # ML signal analysis
        if context.ml_confidence > 0.7:
            active_triggers.append("high_ml_confidence")
        elif context.ml_confidence < 0.4:
            active_triggers.append("low_ml_confidence")
        
        # Position analysis
        if context.current_positions == 0:
            active_triggers.append("no_positions")
        elif context.account_exposure > 0.7:
            active_triggers.append("large_position")
        
        # Session analysis
        if context.session_duration < 5:  # New session
            active_triggers.append("new_session")
        
        # Generate suggestions for active triggers
        for trigger in active_triggers:
            if trigger in self.contextual_triggers:
                trigger_commands = self.contextual_triggers[trigger]
                for command_hint in trigger_commands:
                    suggestion = await self._create_contextual_suggestion(command_hint, context, trigger)
                    if suggestion:
                        suggestions.append(suggestion)
        
        return suggestions
    
    async def _get_ml_enhanced_suggestions(self, context: SuggestionContext) -> List[CommandSuggestion]:
        """Generate ML-enhanced suggestions based on model insights"""
        suggestions = []
        
        try:
            # Import ML services for real-time insights
            from . import get_ai_brain_service
            ai_brain = get_ai_brain_service()
            
            if not ai_brain or not hasattr(ai_brain, 'ml_capabilities'):
                return suggestions
            
            ml_caps = ai_brain.ml_capabilities
            
            # LSTM-based suggestions
            if 'lstm' in ml_caps or 'pipeline' in ml_caps:
                lstm_suggestion = CommandSuggestion(
                    command="lstm prediction",
                    description="Get neural network price prediction with current confidence",
                    suggestion_type=SuggestionType.ML_INSIGHT,
                    relevance_score=0.8,
                    context_match={"ml_available": True, "confidence": context.ml_confidence},
                    example_usage="lstm prediction for next 15-30 minutes"
                )
                suggestions.append(lstm_suggestion)
            
            # Kelly Criterion suggestions for position sizing
            if 'kelly' in ml_caps or 'pipeline' in ml_caps:
                if context.ml_confidence > 0.6:  # Only suggest when we have decent confidence
                    kelly_suggestion = CommandSuggestion(
                        command="kelly position size",
                        description=f"Calculate optimal position size for {context.ml_confidence:.1%} confidence signal",
                        suggestion_type=SuggestionType.ML_INSIGHT,
                        relevance_score=0.7 + (context.ml_confidence * 0.3),
                        context_match={"kelly_applicable": True, "signal_confidence": context.ml_confidence},
                        example_usage=f"kelly position size for {context.ml_confidence:.0%} win probability"
                    )
                    suggestions.append(kelly_suggestion)
            
            # Ensemble model suggestions
            if 'ensemble' in ml_caps or 'pipeline' in ml_caps:
                ensemble_suggestion = CommandSuggestion(
                    command="ensemble forecast",
                    description="Get consensus forecast from multiple ML models",
                    suggestion_type=SuggestionType.ML_INSIGHT,
                    relevance_score=0.75,
                    context_match={"ensemble_available": True},
                    example_usage="ensemble forecast with model agreement analysis"
                )
                suggestions.append(ensemble_suggestion)
                
        except Exception as e:
            logger.warning(f"Error generating ML-enhanced suggestions: {e}")
        
        return suggestions
    
    async def _get_historical_suggestions(self, context: SuggestionContext) -> List[CommandSuggestion]:
        """Generate suggestions based on historical usage patterns"""
        suggestions = []
        
        try:
            # Query recent successful commands from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get frequently used commands in similar context
            cursor.execute("""
                SELECT command, COUNT(*) as usage_count, AVG(success_rating) as avg_rating
                FROM command_usage 
                WHERE timestamp > datetime('now', '-7 days')
                AND success_rating >= 3
                GROUP BY command
                ORDER BY usage_count DESC, avg_rating DESC
                LIMIT 5
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            for command, usage_count, avg_rating in results:
                # Calculate relevance based on usage frequency and success rate
                relevance = min(0.6 + (usage_count * 0.05) + (avg_rating * 0.1), 1.0)
                
                suggestion = CommandSuggestion(
                    command=command,
                    description=f"Frequently used command (success rate: {avg_rating:.1f}/5)",
                    suggestion_type=SuggestionType.TRADING_ACTION,  # Default type
                    relevance_score=relevance,
                    context_match={"historical_success": True, "usage_count": usage_count},
                    example_usage=command
                )
                suggestions.append(suggestion)
                
        except Exception as e:
            logger.warning(f"Error getting historical suggestions: {e}")
        
        return suggestions
    
    async def _rank_suggestions(self, 
                              suggestions: List[CommandSuggestion],
                              partial_command: str,
                              context: SuggestionContext) -> List[CommandSuggestion]:
        """Rank suggestions by relevance and context match"""
        
        for suggestion in suggestions:
            # Base relevance score
            score = suggestion.relevance_score
            
            # Boost for exact partial matches
            if partial_command and suggestion.command.lower().startswith(partial_command.lower()):
                score += 0.3
            
            # Boost for ML-related suggestions when ML confidence is high
            if suggestion.suggestion_type == SuggestionType.ML_INSIGHT and context.ml_confidence > 0.6:
                score += 0.2
            
            # Boost for trading actions when there's a clear signal
            if suggestion.suggestion_type == SuggestionType.TRADING_ACTION and context.ml_signal:
                score += 0.15
            
            # Boost for risk management during high volatility
            if (suggestion.suggestion_type == SuggestionType.RISK_MANAGEMENT and 
                context.volatility_level == "high"):
                score += 0.1
            
            # Update the relevance score
            suggestion.relevance_score = min(score, 1.0)
        
        # Sort by relevance score (descending)
        return sorted(suggestions, key=lambda s: s.relevance_score, reverse=True)
    
    def _deduplicate_suggestions(self, suggestions: List[CommandSuggestion]) -> List[CommandSuggestion]:
        """Remove duplicate suggestions based on command text"""
        seen_commands = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            command_key = suggestion.command.lower().strip()
            if command_key not in seen_commands:
                seen_commands.add(command_key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _fill_template_variables(self, template: str) -> str:
        """Fill template variables with contextually appropriate values"""
        # Replace common variables
        filled = template.replace("{symbol}", "NQU25-CME")
        filled = filled.replace("{price}", "23500")
        return filled
    
    async def _create_contextual_suggestion(self, 
                                          command_hint: str,
                                          context: SuggestionContext,
                                          trigger: str) -> Optional[CommandSuggestion]:
        """Create a contextual suggestion from a command hint"""
        
        # Map command hints to actual commands
        hint_to_command = {
            "buy": "buy NQU25-CME",
            "sell": "sell NQU25-CME", 
            "risk_assessment": "risk assessment",
            "position_limits": "check position limits",
            "ml_confidence_check": "ml confidence check",
            "trend_analysis": "trend analysis",
            "volume_analysis": "volume analysis",
            "lstm_prediction": "lstm prediction",
            "kelly_position_size": "kelly position size",
            "system_status": "system status",
            "show_positions": "show positions",
            "pnl_summary": "pnl summary"
        }
        
        if command_hint not in hint_to_command:
            return None
        
        command = hint_to_command[command_hint]
        
        # Determine suggestion type and description
        if "buy" in command or "sell" in command:
            suggestion_type = SuggestionType.TRADING_ACTION
            description = f"Execute {command_hint} based on {trigger}"
        elif "risk" in command or "position" in command:
            suggestion_type = SuggestionType.RISK_MANAGEMENT
            description = f"Check risk metrics due to {trigger}"
        elif "ml" in command or "lstm" in command or "kelly" in command:
            suggestion_type = SuggestionType.ML_INSIGHT
            description = f"Get ML insight triggered by {trigger}"
        elif "status" in command or "show" in command or "pnl" in command:
            suggestion_type = SuggestionType.SYSTEM_STATUS
            description = f"Check system status due to {trigger}"
        else:
            suggestion_type = SuggestionType.MARKET_ANALYSIS
            description = f"Analyze market conditions due to {trigger}"
        
        return CommandSuggestion(
            command=command,
            description=description,
            suggestion_type=suggestion_type,
            relevance_score=0.7,  # Context-driven suggestions get good relevance
            context_match={"trigger": trigger, "contextual": True},
            example_usage=command
        )
    
    async def record_command_usage(self, 
                                 command: str,
                                 context: SuggestionContext,
                                 success_rating: int = 3,
                                 user_session: str = "default"):
        """Record command usage for learning and improvement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            context_data = json.dumps({
                "market_price": context.market_price,
                "price_change": context.price_change,
                "ml_confidence": context.ml_confidence,
                "positions": context.current_positions,
                "volatility": context.volatility_level
            })
            
            cursor.execute("""
                INSERT INTO command_usage (command, context_data, success_rating, user_session)
                VALUES (?, ?, ?, ?)
            """, (command, context_data, success_rating, user_session))
            
            conn.commit()
            conn.close()
            
            # Update in-memory usage counter
            self.command_usage_history[command] += 1
            
        except Exception as e:
            logger.error(f"Error recording command usage: {e}")
    
    async def record_suggestion_feedback(self, 
                                       suggested_command: str,
                                       was_used: bool,
                                       context_match_score: float,
                                       user_feedback: int = 0):
        """Record feedback on suggestion effectiveness"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO suggestion_feedback 
                (suggested_command, was_used, context_match_score, user_feedback)
                VALUES (?, ?, ?, ?)
            """, (suggested_command, was_used, context_match_score, user_feedback))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording suggestion feedback: {e}")


# Singleton instance
_suggestion_engine = None

def get_smart_suggestion_engine() -> SmartSuggestionEngine:
    """Get the singleton smart suggestion engine instance"""
    global _suggestion_engine
    if _suggestion_engine is None:
        _suggestion_engine = SmartSuggestionEngine()
    return _suggestion_engine