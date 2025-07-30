#!/usr/bin/env python3
"""
Kelly Calculator Core
====================

Core Kelly Criterion calculations for ML-enhanced position sizing.
Implements mathematically optimal position sizing based on ML model predictions.

Features:
- Pure Kelly Criterion formula implementation
- ML confidence score integration
- Risk-adjusted position sizing
- Portfolio-level constraints
- Performance tracking and logging

Author: MinhOS v4 - ML Kelly Implementation
Date: 2025-07-28
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KellyResult:
    """Structured result from Kelly calculation"""
    symbol: str
    kelly_fraction: float
    position_size: int  # Number of contracts
    confidence: float
    win_probability: float
    win_loss_ratio: float
    risk_adjusted: bool
    max_capital_risk: float
    reasoning: str
    timestamp: datetime
    model_inputs: Dict
    constraints_applied: List[str]


class KellyCalculator:
    """
    Core Kelly Criterion calculator with ML integration
    
    Implements the Kelly formula: f* = (bp - q) / b
    Where:
        f* = Optimal fraction of capital to bet
        b = Odds (reward/risk ratio)
        p = Win probability
        q = Loss probability (1 - p)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Kelly Calculator with configuration
        
        Args:
            config: Configuration dictionary with Kelly parameters
        """
        self.config = config or self._default_config()
        
        # Kelly fraction constraints
        self.min_kelly_fraction = self.config.get('min_kelly_fraction', 0.01)  # 1% minimum
        self.max_kelly_fraction = self.config.get('max_kelly_fraction', 0.25)  # 25% maximum
        
        # Confidence thresholds
        self.min_confidence = self.config.get('confidence_threshold', 0.01)  # Temporarily lowered for testing
        
        # Risk management parameters
        self.max_portfolio_risk = self.config.get('max_portfolio_risk', 0.20)  # 20% max total risk
        self.max_single_position = self.config.get('max_position_size', 5)  # Max 5 contracts
        
        # Fractional Kelly settings (for risk reduction)
        self.kelly_fraction_multiplier = self.config.get('kelly_fraction_multiplier', 0.6)  # Use 60% of full Kelly
        
        logger.info(f"Kelly Calculator initialized with config: {self.config}")
    
    def _default_config(self) -> Dict:
        """Default Kelly Calculator configuration"""
        return {
            'min_kelly_fraction': 0.01,
            'max_kelly_fraction': 0.25,
            'confidence_threshold': 0.01,  # Temporarily lowered for testing
            'max_portfolio_risk': 0.20,
            'max_position_size': 5,
            'kelly_fraction_multiplier': 0.6,
            'enable_fractional_kelly': True,
            'enable_portfolio_constraints': True
        }
    
    def calculate_kelly_fraction(self, win_probability: float, win_loss_ratio: float) -> float:
        """
        Core Kelly Criterion formula implementation
        
        Args:
            win_probability: Probability of winning trade [0, 1]
            win_loss_ratio: Average win / Average loss ratio
            
        Returns:
            Optimal fraction of capital to risk [0, 1]
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if not (0 <= win_probability <= 1):
            raise ValueError(f"Win probability must be between 0 and 1, got {win_probability}")
        
        if win_loss_ratio <= 0:
            raise ValueError(f"Win/loss ratio must be positive, got {win_loss_ratio}")
        
        # Kelly formula: f* = (bp - q) / b
        # where b = win_loss_ratio, p = win_probability, q = 1 - win_probability
        edge = (win_loss_ratio * win_probability) - (1 - win_probability)
        
        if edge <= 0:
            # No positive expected value - don't trade
            logger.debug(f"No edge detected: edge={edge:.4f}, returning 0")
            return 0.0
        
        kelly_fraction = edge / win_loss_ratio
        
        # Apply bounds
        kelly_fraction = max(0.0, min(kelly_fraction, self.max_kelly_fraction))
        
        logger.debug(f"Kelly calculation: p={win_probability:.3f}, b={win_loss_ratio:.3f}, "
                    f"edge={edge:.4f}, kelly={kelly_fraction:.4f}")
        
        return kelly_fraction
    
    def apply_fractional_kelly(self, kelly_fraction: float, confidence: float = 0.5) -> float:
        """
        Apply fractional Kelly to reduce risk
        
        Args:
            kelly_fraction: Full Kelly recommendation
            confidence: Model confidence [0, 1]
            
        Returns:
            Risk-adjusted Kelly fraction
        """
        if not self.config.get('enable_fractional_kelly', True):
            return kelly_fraction
        
        # Base fractional Kelly
        fractional_kelly = kelly_fraction * self.kelly_fraction_multiplier
        
        # Additional confidence-based adjustment
        confidence_factor = min(1.0, confidence / 0.8)  # Scale confidence to [0, 1.25]
        adjusted_kelly = fractional_kelly * confidence_factor
        
        # Apply minimum threshold
        if adjusted_kelly < self.min_kelly_fraction:
            if kelly_fraction > self.min_kelly_fraction:
                adjusted_kelly = self.min_kelly_fraction
            else:
                adjusted_kelly = 0.0
        
        logger.debug(f"Fractional Kelly: original={kelly_fraction:.4f}, "
                    f"fractional={fractional_kelly:.4f}, confidence_adj={adjusted_kelly:.4f}")
        
        return adjusted_kelly
    
    def convert_kelly_to_position_size(self, 
                                     kelly_fraction: float, 
                                     symbol: str, 
                                     account_capital: float,
                                     contract_value: Optional[float] = None) -> Tuple[int, float]:
        """
        Convert Kelly fraction to actual position size in contracts
        
        Args:
            kelly_fraction: Kelly fraction [0, 1]
            symbol: Trading symbol
            account_capital: Total account capital
            contract_value: Value per contract (estimated if None)
            
        Returns:
            Tuple of (contracts, capital_fraction_used)
        """
        if kelly_fraction <= 0:
            return 0, 0.0
        
        # Estimate contract value if not provided
        if contract_value is None:
            contract_value = self._estimate_contract_value(symbol)
        
        # Calculate capital to risk
        capital_to_risk = kelly_fraction * account_capital
        
        # Convert to number of contracts
        contracts = int(capital_to_risk / contract_value)
        
        # Apply maximum position size constraint
        contracts = min(contracts, self.max_single_position)
        
        # Ensure minimum viable position
        if contracts == 0 and kelly_fraction >= self.min_kelly_fraction:
            contracts = 1  # Take minimum position if Kelly suggests trade
        
        # Calculate actual capital fraction used
        actual_capital_fraction = (contracts * contract_value) / account_capital
        
        logger.debug(f"Position sizing: kelly={kelly_fraction:.4f}, capital=${account_capital}, "
                    f"contract_value=${contract_value}, contracts={contracts}, "
                    f"actual_fraction={actual_capital_fraction:.4f}")
        
        return contracts, actual_capital_fraction
    
    def _estimate_contract_value(self, symbol: str) -> float:
        """
        Estimate contract value for position sizing
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Estimated value per contract
        """
        # Simple estimation based on symbol type
        # In production, this should get real-time contract specifications
        if 'NQ' in symbol:  # NASDAQ futures
            return 23000.0 * 20  # ~$23k * $20/point multiplier = $460k per contract
        elif 'ES' in symbol:  # S&P futures
            return 4600.0 * 50   # ~$4.6k * $50/point multiplier = $230k per contract
        elif 'YM' in symbol:  # Dow futures
            return 35000.0 * 5   # ~$35k * $5/point multiplier = $175k per contract
        else:
            return 100000.0  # Default estimate
    
    def apply_portfolio_constraints(self, 
                                  kelly_fraction: float, 
                                  symbol: str,
                                  current_portfolio_risk: float = 0.0) -> Tuple[float, List[str]]:
        """
        Apply portfolio-level risk constraints to Kelly fraction
        
        Args:
            kelly_fraction: Calculated Kelly fraction
            symbol: Trading symbol
            current_portfolio_risk: Current portfolio risk fraction
            
        Returns:
            Tuple of (adjusted_kelly_fraction, constraints_applied)
        """
        constraints_applied = []
        adjusted_kelly = kelly_fraction
        
        if not self.config.get('enable_portfolio_constraints', True):
            return adjusted_kelly, constraints_applied
        
        # Portfolio risk constraint
        available_risk = self.max_portfolio_risk - current_portfolio_risk
        if available_risk <= 0:
            logger.warning(f"Portfolio risk limit exceeded: current={current_portfolio_risk:.3f}, "
                          f"max={self.max_portfolio_risk:.3f}")
            return 0.0, ['portfolio_limit_exceeded']
        
        if adjusted_kelly > available_risk:
            adjusted_kelly = available_risk
            constraints_applied.append(f'portfolio_risk_limit_applied')
            logger.info(f"Kelly reduced due to portfolio constraint: "
                       f"{kelly_fraction:.4f} -> {adjusted_kelly:.4f}")
        
        # Minimum position constraint
        if 0 < adjusted_kelly < self.min_kelly_fraction:
            if kelly_fraction >= self.min_kelly_fraction:
                adjusted_kelly = self.min_kelly_fraction
                constraints_applied.append('minimum_position_applied')
            else:
                adjusted_kelly = 0.0
                constraints_applied.append('below_minimum_threshold')
        
        return adjusted_kelly, constraints_applied
    
    def calculate_position_recommendation(self,
                                        symbol: str,
                                        win_probability: float,
                                        win_loss_ratio: float,
                                        ml_confidence: float,
                                        account_capital: float = 100000.0,
                                        current_portfolio_risk: float = 0.0,
                                        model_inputs: Optional[Dict] = None) -> KellyResult:
        """
        Complete Kelly position recommendation pipeline
        
        Args:
            symbol: Trading symbol
            win_probability: ML-estimated win probability [0, 1]
            win_loss_ratio: Historical win/loss ratio
            ml_confidence: ML model confidence [0, 1]
            account_capital: Total account capital
            current_portfolio_risk: Current portfolio risk fraction
            model_inputs: ML model input data for logging
            
        Returns:
            KellyResult with complete recommendation
        """
        logger.info(f"Calculating Kelly position for {symbol}: "
                   f"win_prob={win_probability:.3f}, win_loss={win_loss_ratio:.3f}, "
                   f"confidence={ml_confidence:.3f}")
        
        # Step 1: Basic Kelly calculation
        kelly_fraction = self.calculate_kelly_fraction(win_probability, win_loss_ratio)
        
        # Step 2: Apply fractional Kelly for risk reduction
        risk_adjusted_kelly = self.apply_fractional_kelly(kelly_fraction, ml_confidence)
        
        # Step 3: Apply portfolio constraints
        final_kelly, constraints = self.apply_portfolio_constraints(
            risk_adjusted_kelly, symbol, current_portfolio_risk
        )
        
        # Step 4: Convert to position size
        position_size, actual_capital_fraction = self.convert_kelly_to_position_size(
            final_kelly, symbol, account_capital
        )
        
        # Step 5: Build reasoning string
        reasoning_parts = [
            f"Kelly: {kelly_fraction:.3f}",
            f"Risk-adj: {risk_adjusted_kelly:.3f}",
            f"Final: {final_kelly:.3f}"
        ]
        if constraints:
            reasoning_parts.append(f"Constraints: {', '.join(constraints)}")
        
        reasoning = " | ".join(reasoning_parts)
        
        # Create result
        result = KellyResult(
            symbol=symbol,
            kelly_fraction=final_kelly,
            position_size=position_size,
            confidence=ml_confidence,
            win_probability=win_probability,
            win_loss_ratio=win_loss_ratio,
            risk_adjusted=(risk_adjusted_kelly != kelly_fraction),
            max_capital_risk=actual_capital_fraction,
            reasoning=reasoning,
            timestamp=datetime.now(),
            model_inputs=model_inputs or {},
            constraints_applied=constraints
        )
        
        logger.info(f"Kelly recommendation for {symbol}: {position_size} contracts "
                   f"({final_kelly:.3f} fraction, {actual_capital_fraction:.3f} capital risk)")
        
        return result
    
    def validate_inputs(self, win_probability: float, win_loss_ratio: float, confidence: float) -> bool:
        """
        Validate inputs for Kelly calculation
        
        Args:
            win_probability: Win probability [0, 1]
            win_loss_ratio: Win/loss ratio (positive)
            confidence: Model confidence [0, 1]
            
        Returns:
            True if inputs are valid, False otherwise
        """
        if not (0 <= win_probability <= 1):
            logger.error(f"Invalid win probability: {win_probability}")
            return False
        
        if win_loss_ratio <= 0:
            logger.error(f"Invalid win/loss ratio: {win_loss_ratio}")
            return False
        
        if not (0 <= confidence <= 1):
            logger.error(f"Invalid confidence: {confidence}")
            return False
        
        if confidence < self.min_confidence:
            logger.warning(f"Confidence below threshold: {confidence} < {self.min_confidence}")
            return False
        
        return True
    
    def get_config(self) -> Dict:
        """Get current Kelly Calculator configuration"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict) -> None:
        """Update Kelly Calculator configuration"""
        self.config.update(new_config)
        logger.info(f"Kelly Calculator config updated: {new_config}")


# Utility functions for external use
def kelly_criterion_formula(win_probability: float, win_loss_ratio: float) -> float:
    """
    Pure Kelly Criterion formula implementation
    
    Args:
        win_probability: P(win) [0, 1]
        win_loss_ratio: Average win / Average loss
        
    Returns:
        Optimal fraction to bet [0, 1]
    """
    # Input validation
    if win_probability <= 0 or win_probability > 1.0 or win_loss_ratio <= 0:
        return 0.0
    
    # Kelly formula: f* = (bp - q) / b
    # where b = win_loss_ratio, p = win_probability, q = 1 - win_probability
    edge = (win_loss_ratio * win_probability) - (1 - win_probability)
    
    if edge <= 0:
        return 0.0
    
    return edge / win_loss_ratio


def expected_growth_rate(kelly_fraction: float, win_probability: float, win_loss_ratio: float) -> float:
    """
    Calculate expected logarithmic growth rate for Kelly fraction
    
    Args:
        kelly_fraction: Fraction of capital to bet
        win_probability: Win probability
        win_loss_ratio: Win/loss ratio
        
    Returns:
        Expected growth rate per period
    """
    if kelly_fraction <= 0:
        return 0.0
    
    p = win_probability
    q = 1 - p
    b = win_loss_ratio
    
    # Expected log growth: p * log(1 + f*b) + q * log(1 - f)
    win_growth = p * math.log(1 + kelly_fraction * b) if p > 0 else 0
    loss_growth = q * math.log(1 - kelly_fraction) if q > 0 and kelly_fraction < 1 else float('-inf')
    
    return win_growth + loss_growth