#!/usr/bin/env python3
"""
MinhOS v3 Risk Manager
=====================
Linux-native comprehensive risk management and validation system.
Provides critical risk controls, position monitoring, and trading safety.

Replaces the original risk_manager.py with enhanced safety features
and clean Linux architecture.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json
import sqlite3

# Import other services
from minhos.core.base_service import BaseService
from .state_manager import get_state_manager, TradingState, SystemState, Position, RiskParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk_manager")

def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

@dataclass
class TradeRequest:
    """Represents a trade request for validation"""
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    timestamp: datetime
    reason: str = ""
    strategy: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

@dataclass
class RiskViolation:
    """Represents a risk rule violation"""
    level: RiskLevel
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    rule_type: str
    recommendation: str = ""

@dataclass
class RiskLimits:
    """Current risk limits and thresholds"""
    max_position_size: int
    max_daily_loss: float
    max_drawdown_percent: float
    position_size_percent: float
    stop_loss_points: float
    take_profit_points: float
    max_orders_per_minute: int
    volatility_multiplier: float = 1.0

class RiskManager(BaseService):
    """
    Comprehensive risk management system for MinhOS v3
    All trades must pass through this system for validation
    """
    
    def __init__(self, db_path: str = None):
        """Initialize Risk Manager"""
        super().__init__("RiskManager")
        if db_path is None:
            # Move to permanent location in data directory
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "risk.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.running = False
        
        # Service references
        self.state_manager = None
        
        # Centralized symbol management integration
        from ..core.symbol_integration import get_symbol_integration
        self.symbol_integration = get_symbol_integration()
        
        # Mark service as migrated to centralized symbol management
        self.symbol_integration.mark_service_migrated('risk_manager')
        
        # Risk state
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = ""
        self.circuit_breaker_time = None
        self.emergency_mode = False
        
        # Violation tracking
        self.violations: List[RiskViolation] = []
        self.violation_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0, "EMERGENCY": 0}
        
        # Order rate limiting
        self.order_timestamps: List[datetime] = []
        self.order_history: List[TradeRequest] = []
        
        # Risk calculations
        self.current_exposure = 0.0
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.risk_budget_used = 0.0
        
        # Performance tracking
        self.risk_metrics = {
            "orders_validated": 0,
            "orders_blocked": 0,
            "violations_recorded": 0,
            "circuit_breaker_triggers": 0,
            "emergency_stops": 0,
            "risk_checks_passed": 0,
            "risk_checks_failed": 0
        }
        
        # Risk configuration
        self.risk_config = {
            "strict_mode": True,
            "auto_stop_loss": True,
            "position_monitoring": True,
            "drawdown_protection": True,
            "volatility_adjustment": True,
            "correlation_limits": True
        }
        
        # Real-time monitoring
        self.position_alerts = []
        self.risk_warnings = []
        
        # Initialize database
        self._init_database()
        
        logger.info("🛡️ Risk Manager initialized (Linux-native)")
    
    def _init_database(self):
        """Initialize risk management database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Enable WAL mode for better concurrent access
                cursor.execute("PRAGMA journal_mode=WAL")
                
                # Risk violations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS risk_violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        level TEXT,
                        message TEXT,
                        details TEXT,
                        rule_type TEXT,
                        recommendation TEXT
                    )
                ''')
                
                # Trade validations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trade_validations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        symbol TEXT,
                        order_type TEXT,
                        quantity INTEGER,
                        price REAL,
                        approved BOOLEAN,
                        rejection_reasons TEXT,
                        risk_score REAL
                    )
                ''')
                
                # Risk limits history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS risk_limits_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        limits TEXT,
                        reason TEXT
                    )
                ''')
                
                # Daily risk summary table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_risk_summary (
                        date TEXT PRIMARY KEY,
                        max_exposure REAL,
                        max_drawdown REAL,
                        total_violations INTEGER,
                        trades_blocked INTEGER,
                        risk_score REAL,
                        summary TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Risk database initialized")
                
        except Exception as e:
            logger.error(f"❌ Risk database initialization failed: {e}")
            raise
    
    async def start(self):
        """Start the Risk Manager"""
        logger.info("🚀 Starting Risk Manager...")
        self.running = True
        
        # Initialize service references
        self.state_manager = get_state_manager()
        
        # Start monitoring loops
        asyncio.create_task(self._position_monitoring_loop())
        asyncio.create_task(self._risk_calculation_loop())
        asyncio.create_task(self._violation_cleanup_loop())
        asyncio.create_task(self._daily_summary_loop())
        
        logger.info("✅ Risk Manager started")
    
    async def stop(self):
        """Stop the Risk Manager"""
        logger.info("🛑 Stopping Risk Manager...")
        self.running = False
        
        # Save current state
        await self._save_daily_summary()
        
        logger.info("Risk Manager stopped")
    
    async def validate_trade_request(self, trade_request: TradeRequest) -> Tuple[bool, List[str]]:
        """
        CRITICAL: Validate trade request against all risk parameters
        Returns: (is_allowed, list_of_reasons_if_blocked)
        """
        try:
            self.risk_metrics["orders_validated"] += 1
            violations = []
            risk_score = 0.0
            
            # Validate symbol against centralized management
            symbol_violations = await self._validate_symbol(trade_request.symbol)
            violations.extend(symbol_violations)
            
            # CRITICAL: Check if risk management is properly configured
            if not await self._validate_risk_configuration():
                violations.append("CRITICAL: Risk parameters not configured or invalid")
                await self._record_violation(RiskLevel.CRITICAL, "Risk configuration invalid", {
                    "request": asdict(trade_request)
                }, "risk_config")
                return False, violations
            
            # Check emergency states
            if self.emergency_mode:
                violations.append("EMERGENCY: System in emergency mode - all trading blocked")
                return False, violations
            
            if self.circuit_breaker_active:
                violations.append(f"BLOCKED: Circuit breaker active - {self.circuit_breaker_reason}")
                return False, violations
            
            # System state validation
            if self.state_manager:
                system_state = self.state_manager.system_state
                if system_state != SystemState.ONLINE:
                    violations.append(f"BLOCKED: System state is {system_state.value}")
                    return False, violations
                
                system_config = self.state_manager.system_config
                if not system_config.trading_enabled:
                    violations.append("BLOCKED: Trading not enabled in system config")
                    return False, violations
            
            # Rate limiting validation
            rate_violations = await self._validate_order_rate()
            violations.extend(rate_violations)
            risk_score += len(rate_violations) * 0.1
            
            # Position size validation
            size_violations, size_risk = await self._validate_position_size(trade_request)
            violations.extend(size_violations)
            risk_score += size_risk
            
            # Daily loss limit validation
            loss_violations, loss_risk = await self._validate_daily_loss()
            violations.extend(loss_violations)
            risk_score += loss_risk
            
            # Market conditions validation
            market_violations, market_risk = await self._validate_market_conditions(trade_request)
            violations.extend(market_violations)
            risk_score += market_risk
            
            # Drawdown validation
            drawdown_violations, drawdown_risk = await self._validate_drawdown()
            violations.extend(drawdown_violations)
            risk_score += drawdown_risk
            
            # Volatility-adjusted limits
            volatility_violations, vol_risk = await self._validate_volatility_adjustments(trade_request)
            violations.extend(volatility_violations)
            risk_score += vol_risk
            
            # Correlation limits (if multiple positions)
            correlation_violations, corr_risk = await self._validate_correlation_limits(trade_request)
            violations.extend(correlation_violations)
            risk_score += corr_risk
            
            # Record validation in database
            await self._record_trade_validation(trade_request, len(violations) == 0, violations, risk_score)
            
            # Determine final result
            if violations:
                self.risk_metrics["orders_blocked"] += 1
                self.risk_metrics["risk_checks_failed"] += 1
                
                # Create violation record
                await self._record_violation(
                    RiskLevel.HIGH,
                    f"Trade request blocked: {trade_request.symbol} {trade_request.order_type.value}",
                    {
                        "request": asdict(trade_request),
                        "violations": violations,
                        "risk_score": risk_score
                    },
                    "trade_validation",
                    "Review risk parameters and market conditions"
                )
                
                return False, violations
            
            # Trade approved
            self.risk_metrics["risk_checks_passed"] += 1
            self.order_history.append(trade_request)
            self._update_order_rate_tracking()
            
            logger.info(f"✅ Trade approved: {trade_request.symbol} {trade_request.order_type.value} {trade_request.quantity}")
            return True, []
            
        except Exception as e:
            logger.error(f"❌ Risk validation error: {e}")
            violations.append(f"SYSTEM ERROR: Risk validation failed - {str(e)}")
            self.risk_metrics["orders_blocked"] += 1
            return False, violations
    
    async def validate_trade(self, order, signal=None) -> bool:
        """
        Validate trade order (compatibility method for TradingService)
        
        Args:
            order: TradeOrder object from trading service
            signal: Optional TradingSignal object
            
        Returns:
            bool: True if trade is approved, False if rejected
        """
        try:
            # Convert TradeOrder to TradeRequest for internal validation
            trade_request = TradeRequest(
                symbol=order.symbol,
                order_type=OrderType(order.side),  # BUY, SELL, CLOSE
                quantity=order.quantity,
                price=order.price or 0.0,
                stop_loss=order.stop_price,
                take_profit=None,  # Not provided in TradeOrder
                reason=order.reason or "Trading service order"
            )
            
            # Use existing comprehensive validation
            is_approved, violations = await self.validate_trade_request(trade_request)
            
            if not is_approved:
                logger.warning(f"Trade rejected by risk manager: {', '.join(violations)}")
            
            return is_approved
            
        except Exception as e:
            logger.error(f"Trade validation error: {e}")
            return False
    
    async def _validate_risk_configuration(self) -> bool:
        """Validate that risk parameters are properly configured"""
        try:
            if not self.state_manager:
                logger.error("State manager not available for risk validation")
                return False
            
            risk_params = self.state_manager.risk_params
            
            # Check if risk management is enabled
            if not risk_params.enabled:
                logger.error("Risk parameters not enabled")
                return False
            
            # Validate critical parameters
            if (risk_params.max_position_size <= 0 or
                risk_params.max_daily_loss <= 0 or
                risk_params.position_size_percent <= 0):
                
                logger.error(f"Invalid risk parameters: pos_size={risk_params.max_position_size}, "
                           f"daily_loss={risk_params.max_daily_loss}, "
                           f"size_pct={risk_params.position_size_percent}")
                return False
            
            # Validate stop loss configuration
            if risk_params.stop_loss_points <= 0:
                logger.warning("Stop loss not configured - trading allowed but risky")
            
            return True
            
        except Exception as e:
            logger.error(f"Risk configuration validation error: {e}")
            return False
    
    async def _validate_order_rate(self) -> List[str]:
        """Validate order rate limits"""
        violations = []
        
        try:
            if not self.state_manager:
                return violations
            
            max_orders = self.state_manager.system_config.max_orders_per_minute
            
            # Count orders in the last minute
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            recent_orders = [ts for ts in self.order_timestamps if ts > one_minute_ago]
            
            if len(recent_orders) >= max_orders:
                violations.append(f"Order rate limit exceeded: {len(recent_orders)}/{max_orders} orders per minute")
                
                await self._record_violation(
                    RiskLevel.MEDIUM,
                    "Order rate limit exceeded",
                    {"recent_orders": len(recent_orders), "limit": max_orders},
                    "rate_limit"
                )
            
        except Exception as e:
            logger.error(f"Order rate validation error: {e}")
            violations.append(f"Cannot validate order rate: {str(e)}")
        
        return violations
    
    async def _validate_position_size(self, trade_request: TradeRequest) -> Tuple[List[str], float]:
        """Validate position size against limits"""
        violations = []
        risk_score = 0.0
        
        try:
            if not self.state_manager:
                return violations, risk_score
            
            risk_params = self.state_manager.risk_params
            current_positions = self.state_manager.get_positions()
            
            # Get current position for this symbol
            current_position = current_positions.get(trade_request.symbol)
            current_quantity = current_position.quantity if current_position else 0
            
            # Calculate new position size
            if trade_request.order_type == OrderType.BUY:
                new_quantity = current_quantity + trade_request.quantity
            elif trade_request.order_type == OrderType.SELL:
                new_quantity = current_quantity - trade_request.quantity
            elif trade_request.order_type == OrderType.CLOSE:
                new_quantity = 0
            else:
                new_quantity = current_quantity  # For stop/limit orders
            
            # Check maximum position size
            if abs(new_quantity) > risk_params.max_position_size:
                violations.append(f"Position size {abs(new_quantity)} exceeds maximum {risk_params.max_position_size}")
                risk_score += 0.3
            
            # Check position as percentage of account (simplified calculation)
            estimated_exposure = abs(new_quantity) * trade_request.price
            max_exposure = 100000 * (risk_params.position_size_percent / 100)  # Assuming $100k account
            
            if estimated_exposure > max_exposure:
                violations.append(f"Position exposure ${estimated_exposure:,.0f} exceeds limit ${max_exposure:,.0f}")
                risk_score += 0.4
            
            # Check total number of positions
            if len(current_positions) >= risk_params.max_positions and trade_request.symbol not in current_positions:
                violations.append(f"Maximum number of positions ({risk_params.max_positions}) already held")
                risk_score += 0.2
            
        except Exception as e:
            logger.error(f"Position size validation error: {e}")
            violations.append(f"Cannot validate position size: {str(e)}")
            risk_score += 0.5
        
        return violations, risk_score
    
    async def _validate_daily_loss(self) -> Tuple[List[str], float]:
        """Validate against daily loss limits"""
        violations = []
        risk_score = 0.0
        
        try:
            if not self.state_manager:
                return violations, risk_score
            
            risk_params = self.state_manager.risk_params
            current_pnl = self.state_manager.pnl.get("today", 0.0)
            max_daily_loss = abs(risk_params.max_daily_loss)
            
            # Check current daily P&L
            if current_pnl < -max_daily_loss:
                violations.append(f"Daily loss ${abs(current_pnl):,.2f} exceeds limit ${max_daily_loss:,.2f}")
                risk_score += 0.5
                
                # Trigger circuit breaker for severe losses
                if current_pnl < -max_daily_loss * 1.2:
                    await self._trigger_circuit_breaker("Daily loss limit severely exceeded")
            
            # Warning for approaching limit
            elif current_pnl < -max_daily_loss * 0.8:
                risk_score += 0.2
                await self._record_violation(
                    RiskLevel.MEDIUM,
                    f"Approaching daily loss limit: ${abs(current_pnl):,.2f} / ${max_daily_loss:,.2f}",
                    {"current_pnl": current_pnl, "limit": max_daily_loss},
                    "daily_loss_warning"
                )
            
        except Exception as e:
            logger.error(f"Daily loss validation error: {e}")
            violations.append(f"Cannot validate daily loss: {str(e)}")
            risk_score += 0.3
        
        return violations, risk_score
    
    async def _validate_market_conditions(self, trade_request: TradeRequest) -> Tuple[List[str], float]:
        """Validate market conditions for trading"""
        violations = []
        risk_score = 0.0
        
        try:
            if not self.state_manager:
                return violations, risk_score
            
            # Check market data freshness
            if self.state_manager.last_market_update:
                data_age = (datetime.now() - self.state_manager.last_market_update).total_seconds()
                
                if data_age > 60:  # 1 minute threshold
                    violations.append(f"Market data is stale: {data_age:.0f} seconds old")
                    risk_score += 0.4
                elif data_age > 30:
                    risk_score += 0.1  # Minor risk for moderately stale data
            else:
                violations.append("No market data available")
                risk_score += 0.5
            
            # Validate trade price
            if trade_request.price <= 0:
                violations.append("Invalid trade price")
                risk_score += 0.3
            
            # Check trading hours (simplified - could be enhanced)
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 17:  # Outside typical futures hours
                risk_score += 0.1
                logger.warning("Trading outside typical market hours")
            
        except Exception as e:
            logger.error(f"Market conditions validation error: {e}")
            violations.append(f"Cannot validate market conditions: {str(e)}")
            risk_score += 0.3
        
        return violations, risk_score
    
    async def _validate_drawdown(self) -> Tuple[List[str], float]:
        """Validate against maximum drawdown limits"""
        violations = []
        risk_score = 0.0
        
        try:
            if not self.state_manager:
                return violations, risk_score
            
            risk_params = self.state_manager.risk_params
            positions = self.state_manager.get_positions()
            
            # Calculate total unrealized P&L
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions.values())
            
            if total_unrealized_pnl < 0:
                # Simplified drawdown calculation (would be more sophisticated in production)
                account_value = 100000  # Assumed account value
                drawdown_pct = abs(total_unrealized_pnl) / account_value * 100
                max_drawdown = risk_params.max_drawdown_percent
                
                if drawdown_pct > max_drawdown:
                    violations.append(f"Drawdown {drawdown_pct:.1f}% exceeds limit {max_drawdown:.1f}%")
                    risk_score += 0.5
                    
                    await self._trigger_circuit_breaker(f"Maximum drawdown exceeded: {drawdown_pct:.1f}%")
                
                elif drawdown_pct > max_drawdown * 0.8:
                    risk_score += 0.2
                    await self._record_violation(
                        RiskLevel.MEDIUM,
                        f"Approaching drawdown limit: {drawdown_pct:.1f}% / {max_drawdown:.1f}%",
                        {"current_drawdown": drawdown_pct, "limit": max_drawdown},
                        "drawdown_warning"
                    )
            
        except Exception as e:
            logger.error(f"Drawdown validation error: {e}")
            violations.append(f"Cannot validate drawdown: {str(e)}")
            risk_score += 0.3
        
        return violations, risk_score
    
    async def _validate_volatility_adjustments(self, trade_request: TradeRequest) -> Tuple[List[str], float]:
        """Validate trades against volatility-adjusted limits"""
        violations = []
        risk_score = 0.0
        
        try:
            # This would implement volatility-based position sizing adjustments
            # For now, placeholder implementation
            
            if self.risk_config.get("volatility_adjustment", True):
                # Would calculate current market volatility and adjust position sizes
                # High volatility = smaller positions
                pass
            
        except Exception as e:
            logger.error(f"Volatility adjustment validation error: {e}")
            risk_score += 0.1
        
        return violations, risk_score
    
    async def _validate_symbol(self, symbol: str) -> List[str]:
        """Validate symbol against centralized management"""
        violations = []
        
        try:
            # Check if symbol is in tradeable symbols list
            tradeable_symbols = self.symbol_integration.get_trading_engine_symbols()
            if symbol not in tradeable_symbols:
                violations.append(f"Symbol {symbol} not in approved tradeable symbols list")
                
                await self._record_violation(
                    RiskLevel.HIGH,
                    f"Invalid symbol for trading: {symbol}",
                    {"symbol": symbol, "tradeable_symbols": tradeable_symbols},
                    "symbol_validation",
                    "Use only symbols from centralized management system"
                )
            
            # Check if symbol requires rollover attention
            rollover_status = self.symbol_integration.check_rollover_status()
            if rollover_status.get('needs_attention', False):
                urgent_rollovers = rollover_status.get('urgent_rollovers', [])
                if symbol in [alert['current_symbol'] for alert in urgent_rollovers]:
                    violations.append(f"Symbol {symbol} requires rollover attention - trading may be risky")
                    
                    await self._record_violation(
                        RiskLevel.MEDIUM,
                        f"Symbol rollover warning: {symbol}",
                        {"symbol": symbol, "rollover_status": rollover_status},
                        "rollover_warning",
                        "Consider rolling to next contract before trading"
                    )
            
        except Exception as e:
            logger.error(f"Symbol validation error: {e}")
            violations.append(f"Cannot validate symbol {symbol}: {str(e)}")
        
        return violations
    
    async def _validate_correlation_limits(self, trade_request: TradeRequest) -> Tuple[List[str], float]:
        """Validate correlation limits between positions"""
        violations = []
        risk_score = 0.0
        
        try:
            # This would implement correlation analysis between positions
            # Prevent over-concentration in correlated instruments
            
            if self.risk_config.get("correlation_limits", True):
                # Would analyze correlations between symbols
                pass
            
        except Exception as e:
            logger.error(f"Correlation validation error: {e}")
            risk_score += 0.1
        
        return violations, risk_score
    
    def _update_order_rate_tracking(self):
        """Update order rate tracking"""
        try:
            now = datetime.now()
            self.order_timestamps.append(now)
            
            # Keep only last hour of timestamps
            one_hour_ago = now - timedelta(hours=1)
            self.order_timestamps = [ts for ts in self.order_timestamps if ts > one_hour_ago]
            
        except Exception as e:
            logger.error(f"Order rate tracking update error: {e}")
    
    async def _record_violation(self, level: RiskLevel, message: str, details: Dict[str, Any], 
                               rule_type: str, recommendation: str = ""):
        """Record a risk violation"""
        try:
            violation = RiskViolation(
                level=level,
                message=message,
                details=details,
                timestamp=datetime.now(),
                rule_type=rule_type,
                recommendation=recommendation
            )
            
            self.violations.append(violation)
            self.violation_counts[level.value] += 1
            self.risk_metrics["violations_recorded"] += 1
            
            # Save to database
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO risk_violations 
                    (timestamp, level, message, details, rule_type, recommendation)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    violation.timestamp.isoformat(),
                    level.value,
                    message,
                    json.dumps(details, default=json_serializer),
                    rule_type,
                    recommendation
                ))
                conn.commit()
            
            # Log based on severity
            if level == RiskLevel.CRITICAL or level == RiskLevel.EMERGENCY:
                logger.error(f"🚨 {level.value} VIOLATION: {message}")
            elif level == RiskLevel.HIGH:
                logger.warning(f"⚠️ {level.value} RISK: {message}")
            else:
                logger.info(f"📊 {level.value} Note: {message}")
            
            # Keep only recent violations in memory
            if len(self.violations) > 1000:
                self.violations = self.violations[-1000:]
                
        except Exception as e:
            logger.error(f"Violation recording error: {e}")
    
    async def _record_trade_validation(self, trade_request: TradeRequest, approved: bool, 
                                     rejection_reasons: List[str], risk_score: float):
        """Record trade validation in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trade_validations 
                    (timestamp, symbol, order_type, quantity, price, approved, rejection_reasons, risk_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_request.timestamp.isoformat(),
                    trade_request.symbol,
                    trade_request.order_type.value,
                    trade_request.quantity,
                    trade_request.price,
                    approved,
                    json.dumps(rejection_reasons),
                    risk_score
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Trade validation recording error: {e}")
    
    async def _trigger_circuit_breaker(self, reason: str):
        """Trigger emergency circuit breaker"""
        try:
            if not self.circuit_breaker_active:
                self.circuit_breaker_active = True
                self.circuit_breaker_reason = reason
                self.circuit_breaker_time = datetime.now()
                self.risk_metrics["circuit_breaker_triggers"] += 1
                
                logger.error(f"🛑 CIRCUIT BREAKER TRIGGERED: {reason}")
                
                # Disable auto-trading
                if self.state_manager:
                    await self.state_manager.update_system_config(auto_trade_enabled=False)
                    await self.state_manager.emergency_stop(f"Risk circuit breaker: {reason}")
                
                # Record critical violation
                await self._record_violation(
                    RiskLevel.EMERGENCY,
                    f"Circuit breaker triggered: {reason}",
                    {"reason": reason, "time": self.circuit_breaker_time.isoformat()},
                    "circuit_breaker",
                    "Immediate manual intervention required"
                )
                
        except Exception as e:
            logger.critical(f"CRITICAL: Circuit breaker trigger failed: {e}")
    
    async def reset_circuit_breaker(self, admin_override: bool = False, reason: str = "") -> bool:
        """Reset circuit breaker (requires admin action)"""
        try:
            if not admin_override:
                logger.warning("Circuit breaker reset requires admin_override=True")
                return False
            
            self.circuit_breaker_active = False
            self.circuit_breaker_reason = ""
            self.circuit_breaker_time = None
            
            logger.info(f"✅ Circuit breaker reset: {reason}")
            
            await self._record_violation(
                RiskLevel.HIGH,
                f"Circuit breaker reset by admin: {reason}",
                {"reset_reason": reason, "reset_time": datetime.now().isoformat()},
                "circuit_breaker_reset"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Circuit breaker reset error: {e}")
            return False
    
    async def calculate_position_size(self, symbol: str, entry_price: float, 
                                    confidence: float = 0.5) -> Tuple[int, Dict[str, Any]]:
        """Calculate appropriate position size based on risk parameters"""
        try:
            if not self.state_manager:
                return 1, {"error": "State manager not available"}
            
            risk_params = self.state_manager.risk_params
            
            if not risk_params.enabled:
                return 1, {"warning": "Risk parameters not enabled"}
            
            # Base position sizing
            account_value = 100000  # Simplified - would come from actual account data
            risk_per_trade = risk_params.position_size_percent / 100
            
            # Adjust for confidence
            confidence_multiplier = min(1.0, max(0.1, confidence))
            adjusted_risk = risk_per_trade * confidence_multiplier
            
            # Calculate based on stop loss
            if risk_params.stop_loss_points > 0:
                risk_amount = account_value * adjusted_risk
                position_size = int(risk_amount / risk_params.stop_loss_points)
            else:
                position_size = 1
            
            # Apply maximum limits
            position_size = min(position_size, risk_params.max_position_size)
            position_size = max(1, position_size)  # Minimum 1 contract
            
            calculation_details = {
                "account_value": account_value,
                "risk_per_trade": risk_per_trade,
                "confidence_multiplier": confidence_multiplier,
                "adjusted_risk": adjusted_risk,
                "stop_loss_points": risk_params.stop_loss_points,
                "max_position_size": risk_params.max_position_size,
                "calculated_size": position_size
            }
            
            return position_size, calculation_details
            
        except Exception as e:
            logger.error(f"Position size calculation error: {e}")
            return 1, {"error": str(e)}
    
    # Monitoring loops
    async def _position_monitoring_loop(self):
        """Monitor positions for risk issues"""
        while self.running:
            try:
                if self.state_manager:
                    positions = self.state_manager.get_positions()
                    
                    for symbol, position in positions.items():
                        await self._monitor_position(position)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Position monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_position(self, position: Position):
        """Monitor individual position for risk issues"""
        try:
            # Check for excessive losses
            if position.unrealized_pnl < -500:  # $500 loss threshold
                await self._record_violation(
                    RiskLevel.HIGH,
                    f"Position loss alert: {position.symbol} showing ${position.unrealized_pnl:.2f} loss",
                    {"position": asdict(position)},
                    "position_loss",
                    "Consider adding stop loss or closing position"
                )
            
            # Check for stale positions
            hours_since_update = (datetime.now() - position.last_update).total_seconds() / 3600
            if hours_since_update > 24:
                await self._record_violation(
                    RiskLevel.MEDIUM,
                    f"Stale position: {position.symbol} not updated for {hours_since_update:.1f} hours",
                    {"position": asdict(position), "hours_stale": hours_since_update},
                    "stale_position",
                    "Verify position is still valid"
                )
            
        except Exception as e:
            logger.error(f"Position monitoring error: {e}")
    
    async def _risk_calculation_loop(self):
        """Calculate and update risk metrics"""
        while self.running:
            try:
                await self._update_risk_metrics()
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Risk calculation error: {e}")
                await asyncio.sleep(60)
    
    async def _update_risk_metrics(self):
        """Update real-time risk metrics"""
        try:
            if not self.state_manager:
                return
            
            positions = self.state_manager.get_positions()
            
            # Calculate total exposure
            total_exposure = sum(abs(pos.quantity * pos.current_price) for pos in positions.values())
            self.current_exposure = total_exposure
            
            # Calculate current P&L
            total_unrealized = sum(pos.unrealized_pnl for pos in positions.values())
            self.daily_pnl = self.state_manager.pnl.get("today", 0.0) + total_unrealized
            
            # Update risk budget used
            if self.state_manager.risk_params.max_daily_loss > 0:
                self.risk_budget_used = abs(self.daily_pnl) / self.state_manager.risk_params.max_daily_loss
            
        except Exception as e:
            logger.error(f"Risk metrics update error: {e}")
    
    async def _violation_cleanup_loop(self):
        """Clean up old violations"""
        while self.running:
            try:
                # Remove old violations from memory
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.violations = [v for v in self.violations if v.timestamp > cutoff_time]
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                logger.error(f"Violation cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _daily_summary_loop(self):
        """Generate daily risk summaries"""
        while self.running:
            try:
                # Check if we need to generate daily summary (at market close)
                now = datetime.now()
                if now.hour == 16 and now.minute == 0:  # 4 PM
                    await self._save_daily_summary()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Daily summary error: {e}")
                await asyncio.sleep(60)
    
    async def _save_daily_summary(self):
        """Save daily risk summary"""
        try:
            today = datetime.now().date().isoformat()
            
            summary = {
                "date": today,
                "max_exposure": self.current_exposure,
                "max_drawdown": self.max_drawdown,
                "total_violations": sum(self.violation_counts.values()),
                "trades_blocked": self.risk_metrics["orders_blocked"],
                "circuit_breakers": self.risk_metrics["circuit_breaker_triggers"],
                "risk_metrics": self.risk_metrics.copy()
            }
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_risk_summary 
                    (date, max_exposure, max_drawdown, total_violations, trades_blocked, risk_score, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    today,
                    self.current_exposure,
                    self.max_drawdown,
                    sum(self.violation_counts.values()),
                    self.risk_metrics["orders_blocked"],
                    self.risk_budget_used,
                    json.dumps(summary)
                ))
                conn.commit()
            
            logger.info(f"📊 Daily risk summary saved for {today}")
            
        except Exception as e:
            logger.error(f"Daily summary save error: {e}")
    
    # Public API methods
    def get_risk_status(self) -> Dict[str, Any]:
        """Get comprehensive risk status"""
        try:
            return {
                "circuit_breaker_active": self.circuit_breaker_active,
                "circuit_breaker_reason": self.circuit_breaker_reason,
                "emergency_mode": self.emergency_mode,
                "current_exposure": self.current_exposure,
                "daily_pnl": self.daily_pnl,
                "risk_budget_used": self.risk_budget_used,
                "violations_last_24h": len([v for v in self.violations 
                                          if (datetime.now() - v.timestamp).total_seconds() < 86400]),
                "violation_counts": self.violation_counts.copy(),
                "risk_metrics": self.risk_metrics.copy(),
                "risk_config": self.risk_config.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk status error: {e}")
            return {
                "error": str(e),
                "circuit_breaker_active": True,  # Safe default
                "timestamp": datetime.now().isoformat()
            }
    
    def get_recent_violations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent risk violations"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_violations = [v for v in self.violations if v.timestamp > cutoff_time]
            
            return [asdict(v) for v in recent_violations]
            
        except Exception as e:
            logger.error(f"Recent violations error: {e}")
            return []
    
    def validate_system_safety(self) -> Tuple[bool, List[str]]:
        """Comprehensive system safety validation"""
        issues = []
        
        try:
            # Check circuit breaker
            if self.circuit_breaker_active:
                issues.append(f"Circuit breaker active: {self.circuit_breaker_reason}")
            
            # Check emergency mode
            if self.emergency_mode:
                issues.append("System in emergency mode")
            
            # Check risk configuration
            if not self._validate_risk_configuration():
                issues.append("Risk parameters not properly configured")
            
            # Check for critical violations
            recent_critical = len([v for v in self.violations 
                                 if v.level in [RiskLevel.CRITICAL, RiskLevel.EMERGENCY] and
                                 (datetime.now() - v.timestamp).total_seconds() < 300])
            
            if recent_critical > 0:
                issues.append(f"{recent_critical} critical violations in last 5 minutes")
            
            # Check system state
            if self.state_manager and self.state_manager.system_state != SystemState.ONLINE:
                issues.append(f"System not online: {self.state_manager.system_state.value}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            logger.error(f"System safety validation error: {e}")
            issues.append(f"Safety validation failed: {str(e)}")
            return False, issues

    async def health_check(self) -> bool:
        """
        Health check method for TradingService compatibility
        
        Returns:
            bool: True if risk manager is healthy, False otherwise
        """
        try:
            # Check if service is running
            if not getattr(self, '_running', False):
                return False
            
            # Check if database is accessible
            if self.db_path and not self.db_path.exists():
                return False
            
            # Check if state manager is available
            if not self.state_manager:
                return False
            
            # Check for emergency conditions
            if self.emergency_mode or self.circuit_breaker_active:
                return False
            
            # Check for excessive recent violations
            recent_critical = len([v for v in self.violations 
                                 if v.level in [RiskLevel.CRITICAL, RiskLevel.EMERGENCY] and
                                 (datetime.now() - v.timestamp).total_seconds() < 300])
            
            if recent_critical > 5:  # More than 5 critical violations in 5 minutes
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False

    # Abstract method implementations for BaseService
    async def _initialize(self):
        """Initialize service-specific components"""
        # Get state manager reference
        self.state_manager = get_state_manager()
        
        # Initialize database
        self.db_path.parent.mkdir(exist_ok=True)
        await self._setup_database()
        
        logger.info("Risk Manager initialized")
    
    async def _start_service(self):
        """Start service-specific functionality"""
        # Start monitoring loops
        if self.running:
            asyncio.create_task(self._position_monitoring_loop())
            asyncio.create_task(self._risk_calculation_loop()) 
            asyncio.create_task(self._violation_cleanup_loop())
            asyncio.create_task(self._daily_summary_loop())
        
        logger.info("Risk Manager service started")
    
    async def _stop_service(self):
        """Stop service-specific functionality"""
        self.running = False
        logger.info("Risk Manager service stopped")
    
    async def _cleanup(self):
        """Cleanup service resources"""
        # Clear violations and reset state
        self.violations.clear()
        self.order_history.clear()
        self.order_timestamps.clear()
        
        logger.info("Risk Manager cleanup completed")

    async def _setup_database(self):
        """Setup risk management database"""
        try:
            # Create database connection and tables
            # This is a simplified setup - full implementation would create proper tables
            if not self.db_path.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                self.db_path.touch()
            
            logger.info(f"Risk database setup at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")

# Global risk manager instance
_risk_manager: Optional[RiskManager] = None

def get_risk_manager() -> RiskManager:
    """Get global risk manager instance"""
    # First try to get running instance from live trading integration
    try:
        from .live_trading_integration import get_running_service
        running_instance = get_running_service('risk_manager')
        if running_instance:
            return running_instance
    except ImportError:
        pass
    
    # Fallback to singleton pattern
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager()
    return _risk_manager

async def main():
    """Test the Risk Manager"""
    risk_mgr = RiskManager()
    
    try:
        await risk_mgr.start()
        
        # Test trade validation with dynamic symbol from centralized management
        from ..core.symbol_integration import get_symbol_integration
        symbol_integration = get_symbol_integration()
        primary_symbol = symbol_integration.get_ai_brain_primary_symbol()
        
        test_trade = TradeRequest(
            symbol=primary_symbol,
            order_type=OrderType.BUY,
            quantity=2,
            price=21850.0,
            timestamp=datetime.now(),
            reason="Test trade"
        )
        
        is_allowed, reasons = await risk_mgr.validate_trade_request(test_trade)
        print(f"Trade allowed: {is_allowed}")
        if not is_allowed:
            print("Rejection reasons:")
            for reason in reasons:
                print(f"  - {reason}")
        
        # Test safety validation
        is_safe, issues = risk_mgr.validate_system_safety()
        print(f"\nSystem safe: {is_safe}")
        if not is_safe:
            print("Safety issues:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Show risk status
        print("\nRisk Status:")
        status = risk_mgr.get_risk_status()
        for key, value in status.items():
            if key not in ["risk_metrics", "risk_config"]:
                print(f"  {key}: {value}")
        
        # Keep running for testing
        await asyncio.sleep(10)
        
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await risk_mgr.stop()

if __name__ == "__main__":
    asyncio.run(main())