"""
Trade History Loader for Kelly Criterion

Loads historical trade data from SQLite database for probability estimation.
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

class TradeHistoryLoader:
    """
    Loader for historical trade data from SQLite database.
    
    Provides trade history data to the Kelly Criterion probability estimator
    for calculating win/loss ratios and probability estimates.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "/home/colindo/Sync/minh_v4/data/trade_history.db"
        self.logger = logging.getLogger(__name__)
        
        # Ensure database exists
        if not Path(self.db_path).exists():
            self.logger.warning(f"Trade history database not found: {self.db_path}")
            self.db_available = False
        else:
            self.db_available = True
            self.logger.info(f"Trade history database loaded: {self.db_path}")
    
    def get_trade_history(self, 
                         symbol: Optional[str] = None,
                         lookback_days: Optional[int] = 30,
                         limit: Optional[int] = None) -> List[Dict]:
        """
        Load trade history from database
        
        Args:
            symbol: Filter for specific symbol (None for all)
            lookback_days: Days to look back (None for all)
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        if not self.db_available:
            self.logger.warning("Trade history database not available")
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM trades WHERE 1=1"
            params = []
            
            # Symbol filter
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            # Date filter
            if lookback_days:
                cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
                query += " AND timestamp >= ?"
                params.append(cutoff_date)
            
            # Order by timestamp (most recent first)
            query += " ORDER BY timestamp DESC"
            
            # Limit
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            trades = []
            for row in rows:
                trade = {
                    'id': row['id'],
                    'symbol': row['symbol'],
                    'timestamp': row['timestamp'],
                    'entry_price': row['entry_price'],
                    'exit_price': row['exit_price'],
                    'quantity': row['quantity'],
                    'pnl': row['pnl'],
                    'side': row['side'],
                    'strategy': row['strategy'],
                    'confidence': row['confidence'],
                    'holding_period': row['holding_period'],
                    'commission': row['commission'],
                    'net_pnl': row['net_pnl']
                }
                trades.append(trade)
            
            conn.close()
            
            self.logger.info(f"Loaded {len(trades)} trades from database")
            return trades
            
        except Exception as e:
            self.logger.error(f"Error loading trade history: {e}")
            return []
    
    def get_trade_statistics(self, symbol: Optional[str] = None) -> Dict:
        """
        Get trade statistics for analysis
        
        Args:
            symbol: Filter for specific symbol
            
        Returns:
            Dictionary with trade statistics
        """
        trades = self.get_trade_history(symbol=symbol)
        
        if not trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'win_loss_ratio': 1.0,
                'total_pnl': 0.0
            }
        
        # Calculate statistics
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] < 0]
        
        win_pnls = [t['pnl'] for t in wins]
        loss_pnls = [abs(t['pnl']) for t in losses]
        
        avg_win = sum(win_pnls) / len(win_pnls) if win_pnls else 0
        avg_loss = sum(loss_pnls) / len(loss_pnls) if loss_pnls else 0
        
        stats = {
            'total_trades': len(trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(trades) if trades else 0,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': avg_win / avg_loss if avg_loss > 0 else 1.0,
            'total_pnl': sum(t['pnl'] for t in trades)
        }
        
        return stats
    
    def verify_data_availability(self, min_trades: int = 10) -> bool:
        """
        Verify sufficient trade data is available
        
        Args:
            min_trades: Minimum number of trades required
            
        Returns:
            True if sufficient data available
        """
        if not self.db_available:
            return False
        
        trades = self.get_trade_history(limit=min_trades + 5)  # Get a few extra
        
        result = len(trades) >= min_trades
        
        if result:
            self.logger.info(f"✅ Trade data verification passed: {len(trades)} trades available")
        else:
            self.logger.warning(f"❌ Insufficient trade data: {len(trades)} < {min_trades}")
        
        return result

# Global instance for easy access
trade_history_loader = TradeHistoryLoader()