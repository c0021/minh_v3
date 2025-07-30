"""
Position Sizing API

Unified API for all position sizing methods including fixed sizing and Kelly Criterion.
Provides clean integration point for trading services.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .kelly.kelly_manager import KellyManager

class PositionSizingAPI:
    """
    Unified API for position sizing capabilities.
    
    Supports:
    - Fixed position sizing (existing method)
    - ML-Enhanced Kelly Criterion (new method)
    - Automatic fallback and safety mechanisms
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Kelly system
        self.kelly_manager = KellyManager()
        
        # Configuration
        self.config = {
            'default_method': 'kelly',  # 'kelly' or 'fixed'
            'fixed_position_pct': 0.02,  # 2% for fixed sizing
            'enable_kelly': True,
            'kelly_training_required': True
        }
        
        self.logger.info("Position Sizing API initialized")
    
    async def calculate_position_size(self, 
                                    signal: Dict[str, Any],
                                    capital: float,
                                    market_data: List[Dict[str, Any]] = None,
                                    method: str = None) -> Dict[str, Any]:
        """
        Calculate optimal position size using specified or default method
        
        Args:
            signal: Trading signal with direction and confidence
            capital: Available trading capital
            market_data: Recent market data for analysis
            method: Sizing method ('kelly', 'fixed', or None for default)
            
        Returns:
            Position sizing recommendation
        """
        # Determine method
        if method is None:
            method = self.config['default_method']
        
        # Validate inputs
        if capital <= 0:
            return {
                'position_size': 0.0,
                'position_pct': 0.0,
                'method': method,
                'reason': 'No available capital',
                'source': 'position_sizing_api'
            }
        
        signal_direction = signal.get('direction', 0)
        if signal_direction == 0:
            return {
                'position_size': 0.0,
                'position_pct': 0.0,
                'method': method,
                'reason': 'No trading signal',
                'source': 'position_sizing_api'
            }
        
        try:
            if method == 'kelly' and self.config['enable_kelly']:
                # Use Kelly Criterion
                return await self.kelly_manager.calculate_position_size(
                    signal, capital, market_data
                )
            else:
                # Use fixed sizing
                return self._calculate_fixed_position_size(signal, capital, method)
                
        except Exception as e:
            self.logger.error(f"Position sizing error: {e}")
            # Fallback to fixed sizing
            return self._calculate_fixed_position_size(
                signal, capital, f"Error fallback: {str(e)}"
            )
    
    def _calculate_fixed_position_size(self, signal: Dict[str, Any], 
                                     capital: float, 
                                     reason: str = "Fixed sizing") -> Dict[str, Any]:
        """Calculate position size using fixed percentage method"""
        
        position_pct = self.config['fixed_position_pct']
        position_size = capital * position_pct
        
        return {
            'position_size': position_size,
            'position_pct': position_pct,
            'method': 'fixed',
            'kelly_fraction': 0.0,
            'win_probability': 0.5,
            'signal_confidence': signal.get('confidence', 0.5),
            'signal_direction': signal.get('direction', 0),
            'reason': reason,
            'source': 'position_sizing_api_fixed'
        }
    
    async def train_kelly_system(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the Kelly system on historical data
        
        Args:
            training_data: Historical trades with outcomes
            
        Returns:
            Training results
        """
        if not self.config['enable_kelly']:
            return {
                'success': False,
                'message': 'Kelly system disabled'
            }
        
        return await self.kelly_manager.train_kelly_system(training_data)
    
    def update_trade_outcome(self, trade_result: Dict[str, Any]):
        """
        Update position sizing system with trade outcome
        
        Args:
            trade_result: Trade outcome for learning
        """
        if self.config['enable_kelly']:
            self.kelly_manager.update_trade_outcome(trade_result)
    
    def get_sizing_recommendation(self, signal: Dict[str, Any], 
                                capital: float,
                                market_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get position sizing recommendation with method comparison
        
        Args:
            signal: Trading signal
            capital: Available capital
            market_data: Market data for analysis
            
        Returns:
            Comprehensive sizing analysis
        """
        try:
            # Get both Kelly and fixed recommendations
            results = {}
            
            # Fixed sizing (always available)
            results['fixed'] = self._calculate_fixed_position_size(signal, capital)
            
            # Kelly sizing (if enabled and trained)
            if self.config['enable_kelly']:
                # Run Kelly calculation synchronously for comparison
                import asyncio
                if asyncio.get_event_loop().is_running():
                    # We're in an async context, schedule the coroutine
                    task = asyncio.create_task(
                        self.kelly_manager.calculate_position_size(signal, capital, market_data)
                    )
                    # This is a synchronous method, so we can't await here
                    # Return a note that Kelly calculation is being processed
                    results['kelly'] = {
                        'position_size': 0.0,
                        'position_pct': 0.0,
                        'method': 'kelly_async_pending',
                        'reason': 'Kelly calculation in progress',
                        'source': 'position_sizing_api'
                    }
                else:
                    # Create new event loop for the Kelly calculation
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        kelly_result = loop.run_until_complete(
                            self.kelly_manager.calculate_position_size(signal, capital, market_data)
                        )
                        results['kelly'] = kelly_result
                    finally:
                        loop.close()
            
            # Determine recommended method
            recommended_method = self.config['default_method']
            recommended_result = results.get(recommended_method, results['fixed'])
            
            return {
                'recommended': recommended_result,
                'methods': results,
                'default_method': self.config['default_method'],
                'kelly_available': self.config['enable_kelly'],
                'kelly_trained': self.kelly_manager.is_ready if self.config['enable_kelly'] else False
            }
            
        except Exception as e:
            self.logger.error(f"Sizing recommendation error: {e}")
            return {
                'recommended': self._calculate_fixed_position_size(signal, capital, f"Error: {str(e)}"),
                'methods': {'fixed': self._calculate_fixed_position_size(signal, capital)},
                'default_method': 'fixed',
                'kelly_available': False,
                'kelly_trained': False
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive position sizing system status"""
        status = {
            'config': self.config,
            'methods_available': ['fixed']
        }
        
        if self.config['enable_kelly']:
            status['methods_available'].append('kelly')
            status['kelly_system'] = self.kelly_manager.get_system_status()
        
        return status
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for dashboard"""
        summary = {
            'default_method': self.config['default_method'],
            'kelly_enabled': self.config['enable_kelly']
        }
        
        if self.config['enable_kelly']:
            summary.update(self.kelly_manager.get_performance_summary())
        
        return summary
    
    def set_config(self, **kwargs):
        """Update position sizing configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated position sizing config: {key} = {value}")
        
        # Pass Kelly-specific configs
        if self.config['enable_kelly']:
            kelly_configs = {k.replace('kelly_', ''): v for k, v in kwargs.items() 
                           if k.startswith('kelly_')}
            if kelly_configs:
                self.kelly_manager.set_config(**kelly_configs)