#!/usr/bin/env python3
"""
MinhOS v3 Trading Engine
                side=side,
                quantity=position_size,
                order_type=execution_strategy,
                price=signal.target_price,
                stop_price=signal.stop_loss,
                reason=f"AI Signal: {signal.reasoning}"
            )
            
            return order
            
        except Exception as e:
            logger.error(f"❌ Trade order creation error: {e}")
            return None
    
    async def _calculate_position_size(self, signal: TradingSignal, current_price: float) -> int:
        """Calculate position size using ML-Enhanced Kelly Criterion"""
        try:
            # Check if ML-enhanced sizing is enabled
            use_ml_sizing = self.config.get("use_ml_position_sizing", True)
            
            if use_ml_sizing:
                # Use ML-Enhanced Kelly Criterion
                try:
                    from .position_sizing_service import get_position_sizing_service
                    sizing_service = get_position_sizing_service()
                    
                    # Get optimal position size from Kelly Criterion
                    kelly_position = await sizing_service.calculate_optimal_position(
                        symbol=self.primary_symbol,
                        current_price=current_price,
                        market_data=signal.context  # Pass signal context as market data
                    )
                    
                    position_size = kelly_position.risk_adjusted_size
                    
                    logger.info(f"📏 ML-Enhanced Position Size (Kelly Criterion):")
                    logger.info(f"    Win Probability: {kelly_position.win_probability:.2%}")
                    logger.info(f"    Kelly Fraction: {kelly_position.kelly_fraction:.3f}")
                    logger.info(f"    Confidence Score: {kelly_position.confidence_score:.2f}")
                    logger.info(f"    Recommended Size: {position_size}")
                    
                    # Store Kelly details in signal context for later reference
                    signal.context['kelly_position'] = {
                        'win_probability': kelly_position.win_probability,
                        'kelly_fraction': kelly_position.kelly_fraction,
                        'confidence_score': kelly_position.confidence_score
                    }
                    
                    return max(1, position_size)
                    
                except Exception as e:
                    logger.warning(f"ML sizing failed, falling back to simple sizing: {e}")
                    # Fall back to simple sizing
            
            # Simple position sizing (fallback)
            base_size = 1  # Base position size
            
            # Adjust size based on confidence
            confidence_multiplier = signal.confidence
            
            # Apply risk management constraints
            if self.risk_manager:
                # This would use risk manager to calculate appropriate size
                # For now, use simple logic
                max_size = 3  # Maximum contracts
                calculated_size = int(base_size * confidence_multiplier * 2)
                position_size = min(calculated_size, max_size)
            else:
                position_size = base_size
            
            logger.info(f"📏 Simple Position Size Calculation:")
            logger.info(f"    Base Size: {base_size}")
            logger.info(f"    Confidence Multiplier: {confidence_multiplier:.2f}")
            logger.info(f"    Final Size: {position_size}")
            
            return max(1, position_size)  # Minimum 1 contract
            
        except Exception as e:
            logger.error(f"❌ Position size calculation error: {e}")
            return 1
    
    async def _validate_trade_with_risk_manager(self, order: TradeOrder, signal: TradingSignal) -> bool:
        """Validate trade with risk manager"""
        try:
            if not self.risk_manager:
                return False
            
            # TODO: Implement actual risk validation
            # For now, always approve if confidence is high enough
            approved = signal.confidence >= 0.75
            
            logger.info(f"🛡️ Risk Validation:")
            logger.info(f"    Order: {order.side} {order.quantity} {order.symbol}")
            logger.info(f"    Signal Confidence: {signal.confidence:.1%}")
            logger.info(f"    Risk Approved: {'✅ YES' if approved else '❌ NO'}")
            
            return approved
            
        except Exception as e:
            logger.error(f"❌ Risk validation error: {e}")
            return False
    
    async def _execute_autonomous_trade(self, order: TradeOrder, signal: TradingSignal) -> bool:
        """Execute trade autonomously without human intervention"""
        try:
            logger.info("🚀 AUTONOMOUS TRADE EXECUTION INITIATED")
            logger.info(f"📋 Order Details: {order.side} {order.quantity} {order.symbol}")
            logger.info(f"🎯 Strategy: {order.order_type.value}")
            
            # Execute based on strategy
            if order.order_type == ExecutionStrategy.MARKET:
                success = await self._execute_market_order(order)
            elif order.order_type == ExecutionStrategy.LIMIT:
                success = await self._execute_limit_order(order)
            elif order.order_type == ExecutionStrategy.ADAPTIVE:
                success = await self._execute_adaptive_order(order)
            else:
                logger.error(f"❌ Unknown execution strategy: {order.order_type}")
                return False
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Autonomous execution error: {e}")
            return False
    
    async def _save_ai_decision_log(self, signal: TradingSignal, current_price: float):
        """Save AI decision to log file for analysis"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "signal": signal.signal.value,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning,
                "current_price": current_price,
                "target_price": signal.target_price,
                "stop_loss": signal.stop_loss,
                "analysis_type": signal.analysis_type.value
            }
            
            # TODO: Save to structured log file or database
            # For now, just log as JSON
            logger.info(f"💾 AI Decision Log: {json.dumps(log_entry, indent=2)}")
            
        except Exception as e:
            logger.error(f"❌ AI decision logging error: {e}")
    
    async def _log_trade_rejection(self, signal: TradingSignal, order: TradeOrder, reason: str):
        """Log when a trade is rejected"""
        logger.warning("🚫 TRADE REJECTED")
        logger.warning(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.warning(f"📋 Order: {order.side} {order.quantity} {order.symbol}")
        logger.warning(f"❌ Reason: {reason}")
    
    async def _log_trade_execution(self, signal: TradingSignal, order: TradeOrder, execution_type: str):
        """Log successful trade execution"""
        logger.info("✅ TRADE EXECUTED")
        logger.info(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.info(f"📋 Order: {order.side} {order.quantity} {order.symbol}")
        logger.info(f"🚀 Execution Type: {execution_type}")
    
    async def _log_trade_failure(self, signal: TradingSignal, order: TradeOrder, reason: str):
        """Log failed trade execution"""
        logger.error("❌ TRADE EXECUTION FAILED")
        logger.error(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.error(f"📋 Order: {order.side} {order.quantity} {order.symbol}")
        logger.error(f"💥 Reason: {reason}")
    
    async def _log_signal_below_threshold(self, signal: TradingSignal, current_price: float):
        """Log when signal is below execution threshold"""
        logger.info("📊 SIGNAL BELOW EXECUTION THRESHOLD")
        logger.info(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.info(f"💰 Current Price: ${current_price:.2f}")
        logger.info(f"⚖️ Threshold: 75% (current: {signal.confidence:.1%})")
        logger.info(f"📝 Reasoning: {signal.reasoning}")
    
    async def _log_processing_error(self, signal: Optional[TradingSignal], error: str):
        """Log processing errors"""
        logger.error("💥 AI SIGNAL PROCESSING ERROR")
        if signal:
            logger.error(f"📋 Signal: {signal.signal.value} (confidence: {signal.confidence:.1%})")
        logger.error(f"❌ Error: {error}")
    
    async def _evaluate_decision_quality(self, signal: TradingSignal, 
                                        trade_order: Optional[TradeOrder], 
                                        current_price: float, 
                                        execution_success: Optional[bool]):
        """
        Evaluate the quality of our decision-making process independent of outcome.
        This is the core of our philosophy - measuring decision quality, not just results.
        """
        try:
            from ..core.decision_quality import get_decision_quality_framework
            
            # Generate unique decision ID
            decision_id = f"decision_{int(datetime.now().timestamp())}"
            
            # Prepare AI signal data for evaluation
            ai_signal_data = {
                'signal': signal.signal.value,
                'confidence': signal.confidence,
                'reasoning': signal.reasoning,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'analysis_type': signal.analysis_type.value
            }
            
            # Add decision quality context if available
            if hasattr(signal, 'decision_quality_context'):
                ai_signal_data.update(signal.decision_quality_context)
            
            # Prepare market data snapshot
            market_data_snapshot = {
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'market_session': getattr(signal, 'decision_quality_context', {}).get('market_session', 'unknown')
            }
            
            # Prepare risk metrics
            risk_metrics = {
                'position_size_calculated': trade_order is not None,
                'risk_reward_ratio': self._calculate_risk_reward_ratio(signal, current_price) if signal.target_price and signal.stop_loss else None,
                'portfolio_impact_assessed': True  # We always consider portfolio impact
            }
            
            # Prepare execution details
            execution_details = {}
            if trade_order:
                execution_details = {
                    'side': trade_order.side,
                    'quantity': trade_order.quantity,
                    'order_type': trade_order.order_type.value,
                    'signal_price': current_price,
                    'execution_price': current_price,  # Simplified - would be actual execution price
                    'execution_delay_seconds': 0,  # AI execution is immediate
                    'execution_success': execution_success
                }
            else:
                execution_details = {
                    'side': None,
                    'quantity': 0,
                    'signal_price': current_price,
                    'execution_success': None,  # Not executed
                    'reason_not_executed': 'Below confidence threshold'
                }
            
            # Get decision quality framework and evaluate
            quality_framework = get_decision_quality_framework()
            quality_score = quality_framework.evaluate_decision(
                decision_id=decision_id,
                ai_signal=ai_signal_data,
                market_data=market_data_snapshot,
                risk_metrics=risk_metrics,
                execution_details=execution_details
            )
            
            # Store the quality score for dashboard display
            if not hasattr(self, 'recent_quality_scores'):
                self.recent_quality_scores = []
            
            self.recent_quality_scores.append(quality_score)
            
            # Keep only last 20 scores for dashboard
            if len(self.recent_quality_scores) > 20:
                self.recent_quality_scores = self.recent_quality_scores[-20:]
            
            # Update stats with decision quality metrics
            self.stats["decision_quality_evaluations"] = self.stats.get("decision_quality_evaluations", 0) + 1
            self.stats["avg_decision_quality"] = sum(s.overall_score for s in self.recent_quality_scores) / len(self.recent_quality_scores)
            
            logger.info(f"📋 Decision Quality Evaluated: {quality_score.overall_score:.2f} ({quality_framework._get_quality_label(quality_score.overall_score)})")
            
        except Exception as e:
            logger.error(f"❌ Decision quality evaluation error: {e}")
    
    def _calculate_risk_reward_ratio(self, signal: TradingSignal, current_price: float) -> Optional[float]:
        """Calculate risk/reward ratio for a signal"""
        try:
            if not signal.target_price or not signal.stop_loss:
                return None
            
            if signal.signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                reward = signal.target_price - current_price
                risk = current_price - signal.stop_loss
            else:  # SELL signals
                reward = current_price - signal.target_price
                risk = signal.stop_loss - current_price
            
            if risk <= 0:
                return None
            
            return reward / risk
            
        except Exception as e:
            logger.error(f"❌ Risk/reward calculation error: {e}")
            return None
    
    # ============================================================================
    # END AI TRANSPARENCY METHODS
    # ============================================================================
    
    async def _check_decision_points(self):
        """Check for time-based and condition-based decision points"""
        try:
            now = datetime.now()
            
            # Pre-market analysis (9:00 AM ET)
            if now.time() == time(9, 0) and now.weekday() < 5:
                await self._create_decision(
                    "Pre-Market Analysis",
                    "Market opening soon. Review overnight developments and set trading plan.",
                    DecisionPriority.MEDIUM,
                    ["Aggressive strategy", "Normal strategy", "Defensive strategy", "Stay flat"],
                    {
                        'market_insights': self.market_insights.copy(),
                        'current_regime': self.current_regime.value
                    }
                )
            
            # End of day review (3:45 PM ET)
            if now.time() == time(15, 45) and now.weekday() < 5:
                await self._create_decision(
                    "End of Day Review",
                    "Market closing soon. Review positions and prepare for overnight.",
                    DecisionPriority.MEDIUM,
                    ["Close all positions", "Hold positions", "Adjust stops", "Add hedges"],
                    {
                        'performance': self.performance_metrics.copy(),
                        'positions': len(self.state_manager.get_positions()) if self.state_manager else 0
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Decision points check error: {e}")
    
    async def _decision_management_loop(self):
        """Manage pending decisions and auto-resolution"""
        while self.running:
            try:
                now = datetime.now()
                
                for decision in self.pending_decisions[:]:  # Copy to avoid modification during iteration
                    if decision.resolved:
                        continue
                    
                    # Check for timeout
                    age_seconds = (now - decision.created_at).total_seconds()
                    timeout = self.config["decision_timeout_seconds"].get(decision.priority, 3600)
                    
                    if age_seconds > timeout:
                        if decision.auto_action:
                            await self._resolve_decision(decision.id, decision.auto_action, auto_resolved=True)
                        else:
                            await self._resolve_decision(decision.id, "timeout", auto_resolved=True)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Decision management error: {e}")
                await asyncio.sleep(60)
    
    async def _order_management_loop(self):
        """Manage pending orders and execution"""
        while self.running:
            try:
                # Process pending orders
                for order in self.pending_orders[:]:
                    await self._process_order(order)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Order management error: {e}")
                await asyncio.sleep(5)
    
    async def _performance_tracking_loop(self):
        """Track and update performance metrics"""
        while self.running:
            try:
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Check for performance alerts
                if self.performance_metrics["trades_today"] > 10 and self.performance_metrics["win_rate"] < 0.3:
                    await self._create_decision(
                        "Performance Alert",
                        f"Win rate today: {self.performance_metrics['win_rate']:.1%} from {self.performance_metrics['trades_today']} trades",
                        DecisionPriority.HIGH,
                        ["Stop trading", "Reduce size", "Change strategy", "Continue"],
                        self.performance_metrics.copy(),
                        "Reduce size"
                    )
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Performance tracking error: {e}")
                await asyncio.sleep(300)
    
    async def _regime_detection_loop(self):
        """Dedicated loop for market regime detection"""
        while self.running:
            try:
                if len(self.market_data_buffer) >= 50:
                    new_regime = await self._detect_market_regime()
                    if new_regime != self.current_regime:
                        await self._on_regime_change(new_regime)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Regime detection loop error: {e}")
                await asyncio.sleep(60)
    
    # Decision management methods
    async def _create_decision(self, title: str, description: str, priority: DecisionPriority,
                             options: List[str], context: Dict[str, Any], auto_action: Optional[str] = None):
        """Create a new trading decision"""
        try:
            # Check for duplicate decisions
            for existing in self.pending_decisions:
                if existing.title == title and not existing.resolved:
                    return  # Don't create duplicate
            
            decision = TradingDecision(
                id="",  # Will be set in __post_init__
                title=title,
                description=description,
                priority=priority,
                options=options,
                context=context,
                auto_action=auto_action
            )
            
            self.pending_decisions.append(decision)
            self.stats["decisions_created"] += 1
            
            logger.info(f"📋 Decision created: {title} (Priority: {priority.value})")
            
            # Execute auto handler if available
            handler_key = f"{priority.value}_{title.lower().replace(' ', '_')}"
            if handler_key in self.auto_decision_handlers:
                await self.auto_decision_handlers[handler_key](decision)
            
        except Exception as e:
            logger.error(f"❌ Decision creation error: {e}")
    
    async def _resolve_decision(self, decision_id: str, resolution: str, auto_resolved: bool = False):
        """Resolve a pending decision"""
        try:
            for decision in self.pending_decisions:
                if decision.id == decision_id:
                    decision.resolved = True
                    decision.resolution = resolution
                    decision.resolved_at = datetime.now()
                    
                    self.decision_history.append(decision)
                    self.pending_decisions.remove(decision)
                    self.stats["decisions_resolved"] += 1
                    
                    resolution_type = "Auto" if auto_resolved else "Manual"
                    logger.info(f"✅ Decision resolved ({resolution_type}): {decision.title} → {resolution}")
                    
                    # Execute resolution action
                    await self._execute_decision_resolution(decision, resolution)
                    break
            
        except Exception as e:
            logger.error(f"❌ Decision resolution error: {e}")
    
    async def _execute_decision_resolution(self, decision: TradingDecision, resolution: str):
        """Execute the action based on decision resolution"""
        try:
            # This would contain the logic to execute the decided action
            # For now, just log
            logger.info(f"🎯 Executing decision: {resolution} for {decision.title}")
            
        except Exception as e:
            logger.error(f"❌ Decision execution error: {e}")
    
    # Order management methods
    async def _process_order(self, order: TradeOrder):
        """Process a pending order"""
        try:
            # This would contain actual order execution logic
            # For now, simulate order processing
            logger.info(f"📊 Processing order: {order.symbol} {order.side} {order.quantity}")
            
            # Remove from pending orders
            self.pending_orders.remove(order)
            self.order_history.append(order)
            self.stats["orders_executed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Order processing error: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        try:
            # This would calculate actual performance metrics
            # For now, placeholder
            pass
            
        except Exception as e:
            logger.error(f"❌ Performance update error: {e}")
    
    def _setup_execution_strategies(self):
        """Setup different execution strategies"""
        self.execution_strategies = {
            ExecutionStrategy.MARKET.value: self._execute_market_order,
            ExecutionStrategy.LIMIT.value: self._execute_limit_order,
            ExecutionStrategy.ADAPTIVE.value: self._execute_adaptive_order
        }
    
    def _setup_auto_decision_handlers(self):
        """Setup handlers for automatic decision resolution"""
        self.auto_decision_handlers = {
            "high_market_volatility_spike": self._handle_volatility_spike,
            "high_position_risk_alert": self._handle_position_risk
        }
    
    async def _execute_market_order(self, order: TradeOrder):
        """Execute market order"""
        try:
            logger.info(f"📈 Executing market order: {order.side} {order.quantity} {order.symbol} at market")
            
            # TODO: Implement actual Sierra Chart execution
            # For now, simulate execution
            success = True  # Placeholder - replace with actual execution
            
            if success:
                logger.info(f"✅ Market order executed successfully")
                return True
            else:
                logger.error(f"❌ Market order execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Market order execution error: {e}")
            return False
    
    async def _execute_limit_order(self, order: TradeOrder):
        """Execute limit order"""
        try:
            logger.info(f"📈 Executing limit order: {order.side} {order.quantity} {order.symbol} at {order.price}")
            
            # TODO: Implement actual Sierra Chart execution
            # For now, simulate execution
            success = True  # Placeholder - replace with actual execution
            
            if success:
                logger.info(f"✅ Limit order placed successfully")
                return True
            else:
                logger.error(f"❌ Limit order execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Limit order execution error: {e}")
            return False
    
    async def _execute_adaptive_order(self, order: TradeOrder):
        """Execute adaptive order with intelligent timing"""
        try:
            logger.info(f"📈 Executing adaptive order: {order.side} {order.quantity} {order.symbol}")
            
            # For high-confidence signals, use market orders for speed
            # For medium confidence, use limit orders for better prices
            if hasattr(order, 'confidence') and order.confidence > 0.85:
                return await self._execute_market_order(order)
            else:
                return await self._execute_limit_order(order)
                
        except Exception as e:
            logger.error(f"❌ Adaptive order execution error: {e}")
            return False
    
    async def _handle_volatility_spike(self, decision: TradingDecision):
        """Auto handler for volatility spike decisions"""
        try:
            # Automatically reduce position sizes
            logger.info("🔄 Auto-handling volatility spike: reducing position sizes")
            await self._resolve_decision(decision.id, "Reduce position sizes", auto_resolved=True)
            
        except Exception as e:
            logger.error(f"❌ Volatility spike handler error: {e}")
    
    async def _handle_position_risk(self, decision: TradingDecision):
        """Auto handler for position risk alerts"""
        try:
            # Automatically add stop loss
            logger.info("🛡️ Auto-handling position risk: adding stop loss")
            await self._resolve_decision(decision.id, "Add stop loss", auto_resolved=True)
            
        except Exception as e:
            logger.error(f"❌ Position risk handler error: {e}")
    
    # Public API methods
    def get_pending_decisions(self) -> List[TradingDecision]:
        """Get all pending decisions"""
        return [d for d in self.pending_decisions if not d.resolved]
    
    def get_market_regime(self) -> MarketRegime:
        """Get current market regime"""
        return self.current_regime
    
    def get_market_insights(self) -> Dict[str, Any]:
        """Get current market insights"""
        return self.market_insights.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current trading positions"""
        if not self.state_manager:
            return []
        
        try:
            positions = self.state_manager.get_positions()
            # Convert Position objects to dictionaries
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "entry_time": pos.entry_time.isoformat() if pos.entry_time else None,
                    "side": "long" if pos.quantity > 0 else "short" if pos.quantity < 0 else "flat"
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    def check_symbol_rollover(self) -> Dict[str, Any]:
        """Check if any trading symbols need rollover attention"""
        try:
            rollover_status = self.symbol_integration.check_rollover_status()
            
            # If rollover is needed, create trading decision
            if rollover_status['needs_attention']:
                for alert in rollover_status['alerts']:
                    if alert['action_required']:
                        decision = TradingDecision(
                            id=f"rollover_{alert['current_symbol']}",
                            title=f"Contract Rollover Required: {alert['current_symbol']}",
                            description=f"Contract {alert['current_symbol']} expires in {alert['days_until_rollover']} days. Consider rolling to {alert['next_symbol']}.",
                            priority=DecisionPriority.HIGH if alert['days_until_rollover'] <= 5 else DecisionPriority.MEDIUM,
                            options=["Roll positions now", "Roll closer to expiry", "Close positions"],
                            context={
                                'symbol_rollover': True,
                                'current_symbol': alert['current_symbol'],
                                'next_symbol': alert['next_symbol'],
                                'days_until_rollover': alert['days_until_rollover'],
                                'expiry_date': alert['expiry_date']
                            },
                            auto_action="Roll closer to expiry" if alert['days_until_rollover'] > 5 else None
                        )
                        
                        # Add to pending decisions if not already there
                        if not any(d.id == decision.id for d in self.pending_decisions):
                            self.pending_decisions.append(decision)
                            logger.info(f"📅 Created rollover decision: {decision.title}")
            
            return rollover_status
            
        except Exception as e:
            logger.error(f"Error checking symbol rollover: {e}")
            return {'error': str(e)}

    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        return {
            "running": self.running,
            "current_regime": self.current_regime.value,
            "pending_decisions": len(self.get_pending_decisions()),
            "pending_orders": len(self.pending_orders),
            "market_data_points": len(self.market_data_buffer),
            "performance": self.performance_metrics.copy(),
            "market_insights": self.market_insights.copy(),
            "stats": self.stats.copy(),
            "tradeable_symbols": self.tradeable_symbols,
            "primary_symbol": self.primary_symbol,
            "timestamp": datetime.now().isoformat()
        }

# Global trading engine instance
_trading_engine: Optional[TradingEngine] = None

def get_trading_engine() -> TradingEngine:
    """Get global trading engine instance"""
    # First try to get running instance from live trading integration
    try:
        from .live_trading_integration import get_running_service
        running_instance = get_running_service('trading_engine')
        if running_instance:
            return running_instance
    except ImportError:
        pass
    
    # Fallback to singleton pattern
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = TradingEngine()
    return _trading_engine

async def main():
    """Test the Trading Engine"""
    engine = TradingEngine()
    
    try:
        await engine.start()
        logger.info("Trading Engine running. Press Ctrl+C to stop...")
        
        # Keep running
        while engine.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())