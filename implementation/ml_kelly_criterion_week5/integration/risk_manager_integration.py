#!/usr/bin/env python3
"""
Risk Manager Integration for Kelly Criterion
=============================================

Integrates Kelly position sizing with MinhOS Risk Manager for:
- Position size validation and constraints
- Portfolio risk limit enforcement
- Risk-adjusted Kelly calculations
- Emergency position reduction logic

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass

# Add MinhOS to path
minhos_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(minhos_path))

try:
    from minhos.services.risk_manager import RiskManager, TradeRequest, OrderType, RiskLevel
    from minhos.services import get_risk_manager
except ImportError as e:
    logging.warning(f"Could not import MinhOS Risk Manager: {e}")
    # Create stub classes for development
    class RiskManager:
        async def validate_trade_request(self, trade_request): return True, []
        async def get_portfolio_risk(self): return {"risk_level": "LOW", "max_position_size": 10}
    
    class TradeRequest:
        def __init__(self, **kwargs): pass
    
    class OrderType:
        BUY = "BUY"
        SELL = "SELL"
    
    class RiskLevel:
        LOW = "LOW"
        MEDIUM = "MEDIUM" 
        HIGH = "HIGH"

logger = logging.getLogger(__name__)

@dataclass
class RiskAdjustedKellyResult:
    """Risk-adjusted Kelly recommendation with constraints applied"""
    original_kelly_fraction: float
    adjusted_kelly_fraction: float
    original_position_size: int
    adjusted_position_size: int
    risk_constraints_applied: List[str]
    portfolio_risk_level: str
    max_allowed_position: int
    capital_at_risk: float
    risk_validation_passed: bool
    risk_manager_notes: List[str]

class KellyRiskManagerIntegration:
    """
    Integration layer between Kelly Criterion and MinhOS Risk Manager
    
    Provides:
    - Kelly position size validation
    - Risk-adjusted Kelly calculations
    - Portfolio constraint enforcement
    """
    
    def __init__(self, risk_manager: Optional[RiskManager] = None):
        self.risk_manager = risk_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Risk adjustment parameters
        self.risk_multipliers = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 0.8,
            RiskLevel.HIGH: 0.5,
            RiskLevel.CRITICAL: 0.25,
            RiskLevel.EMERGENCY: 0.0
        }
        
        self.logger.info("Kelly Risk Manager Integration initialized")
    
    async def initialize(self):
        """Initialize Risk Manager connection"""
        try:
            if not self.risk_manager:
                self.risk_manager = get_risk_manager()
            
            if self.risk_manager:
                self.logger.info("Risk Manager connection established")
                return True
            else:
                self.logger.warning("Risk Manager not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Risk Manager: {e}")
            return False
    
    async def validate_and_adjust_kelly_position(
        self,
        symbol: str,
        kelly_fraction: float,
        position_size: int,
        account_capital: float,
        current_price: float
    ) -> RiskAdjustedKellyResult:
        """
        Validate Kelly position with Risk Manager and apply constraints
        
        Args:
            symbol: Trading symbol
            kelly_fraction: Original Kelly fraction
            position_size: Original position size
            account_capital: Account capital
            current_price: Current market price
            
        Returns:
            RiskAdjustedKellyResult with validated and adjusted values
        """
        try:
            self.logger.info(f"Validating Kelly position for {symbol}: {position_size} contracts")
            
            constraints_applied = []
            risk_notes = []
            
            # Get current portfolio risk level
            portfolio_risk = await self._get_portfolio_risk()
            risk_level = portfolio_risk.get('risk_level', 'MEDIUM')
            max_portfolio_position = portfolio_risk.get('max_position_size', 10)
            
            # Apply risk-level adjustment to Kelly fraction
            risk_multiplier = self.risk_multipliers.get(
                getattr(RiskLevel, risk_level, RiskLevel.MEDIUM), 
                0.8
            )
            
            adjusted_kelly_fraction = kelly_fraction * risk_multiplier
            if adjusted_kelly_fraction != kelly_fraction:
                constraints_applied.append(f"Risk-level adjustment ({risk_level}): {risk_multiplier:.2f}x")
            
            # Calculate adjusted position size
            adjusted_position_size = int(abs(adjusted_kelly_fraction * account_capital / current_price))
            
            # Validate with Risk Manager
            validation_passed = True
            if self.risk_manager and position_size > 0:
                trade_request = TradeRequest(
                    symbol=symbol,
                    order_type=OrderType.BUY if position_size > 0 else OrderType.SELL,
                    quantity=abs(adjusted_position_size),
                    price=current_price,
                    timestamp=datetime.now()
                )
                
                validation_passed, violations = await self.risk_manager.validate_trade_request(trade_request)
                if violations:
                    risk_notes.extend(violations)
                
                if not validation_passed:
                    # Apply emergency reduction
                    adjusted_position_size = min(adjusted_position_size, max_portfolio_position // 2)
                    constraints_applied.append("Emergency position reduction due to risk violations")
            
            # Apply portfolio limits
            if adjusted_position_size > max_portfolio_position:
                adjusted_position_size = max_portfolio_position
                constraints_applied.append(f"Portfolio limit: max {max_portfolio_position} contracts")
            
            # Calculate capital at risk
            capital_at_risk = adjusted_position_size * current_price
            
            # Final validation - don't exceed 10% of capital
            max_risk_capital = account_capital * 0.10
            if capital_at_risk > max_risk_capital:
                adjusted_position_size = int(max_risk_capital / current_price)
                capital_at_risk = adjusted_position_size * current_price
                constraints_applied.append("10% capital risk limit applied")
            
            # Recalculate adjusted Kelly fraction based on final position
            if account_capital > 0 and current_price > 0:
                adjusted_kelly_fraction = (adjusted_position_size * current_price) / account_capital
            
            result = RiskAdjustedKellyResult(
                original_kelly_fraction=kelly_fraction,
                adjusted_kelly_fraction=adjusted_kelly_fraction,
                original_position_size=position_size,
                adjusted_position_size=adjusted_position_size,
                risk_constraints_applied=constraints_applied,
                portfolio_risk_level=risk_level,
                max_allowed_position=max_portfolio_position,
                capital_at_risk=capital_at_risk,
                risk_validation_passed=validation_passed,
                risk_manager_notes=risk_notes
            )
            
            self.logger.info(
                f"Risk adjustment complete: {kelly_fraction:.4f} -> {adjusted_kelly_fraction:.4f}, "
                f"{position_size} -> {adjusted_position_size} contracts"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in risk validation: {e}")
            # Return safe defaults
            return RiskAdjustedKellyResult(
                original_kelly_fraction=kelly_fraction,
                adjusted_kelly_fraction=0.0,
                original_position_size=position_size,
                adjusted_position_size=0,
                risk_constraints_applied=["Risk validation error - position blocked"],
                portfolio_risk_level="EMERGENCY",
                max_allowed_position=0,
                capital_at_risk=0.0,
                risk_validation_passed=False,
                risk_manager_notes=[f"Risk validation error: {str(e)}"]
            )
    
    async def _get_portfolio_risk(self) -> Dict[str, Any]:
        """Get current portfolio risk metrics from Risk Manager"""
        try:
            if self.risk_manager and hasattr(self.risk_manager, 'get_portfolio_risk'):
                return await self.risk_manager.get_portfolio_risk()
            else:
                # Default risk parameters
                return {
                    'risk_level': 'MEDIUM',
                    'max_position_size': 5,
                    'current_drawdown': 0.0,
                    'portfolio_value': 100000.0
                }
        except Exception as e:
            self.logger.error(f"Error getting portfolio risk: {e}")
            return {
                'risk_level': 'HIGH',
                'max_position_size': 2,
                'current_drawdown': 0.0,
                'portfolio_value': 100000.0
            }
    
    async def calculate_fractional_kelly(
        self,
        kelly_fraction: float,
        risk_level: str = "MEDIUM"
    ) -> Tuple[float, str]:
        """
        Calculate fractional Kelly based on risk tolerance
        
        Common fractional Kelly strategies:
        - Full Kelly: 1.0x (high risk)
        - Half Kelly: 0.5x (moderate risk) 
        - Quarter Kelly: 0.25x (conservative)
        - Eighth Kelly: 0.125x (very conservative)
        """
        try:
            risk_strategies = {
                "LOW": (1.0, "Full Kelly"),
                "MEDIUM": (0.5, "Half Kelly"), 
                "HIGH": (0.25, "Quarter Kelly"),
                "CRITICAL": (0.125, "Eighth Kelly"),
                "EMERGENCY": (0.0, "No Position")
            }
            
            multiplier, strategy_name = risk_strategies.get(risk_level, (0.5, "Half Kelly"))
            fractional_kelly = kelly_fraction * multiplier
            
            self.logger.debug(f"Fractional Kelly: {kelly_fraction:.4f} * {multiplier} = {fractional_kelly:.4f} ({strategy_name})")
            
            return fractional_kelly, strategy_name
            
        except Exception as e:
            self.logger.error(f"Error calculating fractional Kelly: {e}")
            return kelly_fraction * 0.25, "Quarter Kelly (Safe Default)"
    
    async def get_risk_integration_status(self) -> Dict[str, Any]:
        """Get integration status and health metrics"""
        try:
            status = {
                'risk_manager_available': self.risk_manager is not None,
                'integration_active': True,
                'last_validation_time': datetime.now(),
                'risk_multipliers': self.risk_multipliers,
                'validation_count': 0,
                'constraint_application_rate': 0.0
            }
            
            if self.risk_manager:
                # Get additional Risk Manager status if available
                if hasattr(self.risk_manager, 'get_system_status'):
                    rm_status = await self.risk_manager.get_system_status()
                    status.update({
                        'risk_manager_status': rm_status,
                        'system_risk_level': rm_status.get('current_risk_level', 'UNKNOWN')
                    })
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {
                'risk_manager_available': False,
                'integration_active': False,
                'error': str(e)
            }

# Factory function for easy import
async def create_kelly_risk_integration() -> KellyRiskManagerIntegration:
    """Create and initialize Kelly Risk Manager integration"""
    integration = KellyRiskManagerIntegration()
    await integration.initialize()
    return integration

if __name__ == "__main__":
    async def test_integration():
        """Test the Risk Manager integration"""
        print("🧪 Testing Kelly Risk Manager Integration")
        print("=" * 45)
        
        integration = await create_kelly_risk_integration()
        
        # Test risk adjustment
        result = await integration.validate_and_adjust_kelly_position(
            symbol="NQU25-CME",
            kelly_fraction=0.15,
            position_size=3,
            account_capital=100000.0,
            current_price=18500.0
        )
        
        print(f"Original Kelly: {result.original_kelly_fraction:.4f}")
        print(f"Adjusted Kelly: {result.adjusted_kelly_fraction:.4f}")
        print(f"Original Position: {result.original_position_size} contracts")
        print(f"Adjusted Position: {result.adjusted_position_size} contracts")
        print(f"Constraints Applied: {result.risk_constraints_applied}")
        print(f"Risk Level: {result.portfolio_risk_level}")
        print(f"Validation Passed: {result.risk_validation_passed}")
        
        # Test fractional Kelly
        frac_kelly, strategy = await integration.calculate_fractional_kelly(0.20, "HIGH")
        print(f"\nFractional Kelly (HIGH risk): {frac_kelly:.4f} ({strategy})")
        
        # Test status
        status = await integration.get_risk_integration_status()
        print(f"\nIntegration Status: {status}")
        
        print("\n✅ Risk Manager integration test complete!")
    
    asyncio.run(test_integration())