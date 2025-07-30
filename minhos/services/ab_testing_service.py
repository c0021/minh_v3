#!/usr/bin/env python3
"""
A/B Testing Service

Provides framework for comparing ML-enhanced vs traditional trading signals.
Tracks performance metrics for both approaches to measure improvement.
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import json
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ABTestResult:
    """A/B test result data"""
    group: str  # 'traditional' or 'ml_enhanced'
    signal_type: str
    confidence: float
    timestamp: datetime
    entry_price: float
    exit_price: Optional[float] = None
    position_size: float = 0.0
    pnl: Optional[float] = None
    win: Optional[bool] = None
    duration_minutes: Optional[int] = None
    metadata: Dict[str, Any] = None

class ABTestingService:
    """
    A/B Testing service for comparing ML vs Traditional trading approaches
    
    Features:
    - Random assignment of signals to test groups
    - Performance tracking and comparison
    - Statistical significance testing
    - Real-time metrics calculation
    """
    
    def __init__(self, db_path: str = None, test_allocation: float = 0.5):
        """
        Initialize A/B testing service
        
        Args:
            db_path: Path to SQLite database for storing test results
            test_allocation: Fraction of signals allocated to ML group (0.0-1.0)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "ab_testing.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.test_allocation = test_allocation  # 0.5 = 50% ML, 50% Traditional
        
        # Performance tracking
        self.test_results = {
            'traditional': deque(maxlen=1000),
            'ml_enhanced': deque(maxlen=1000)
        }
        
        # Current test configuration
        self.config = {
            'enabled': True,
            'test_duration_days': 30,
            'min_sample_size': 50,
            'significance_level': 0.05,
            'allocation_method': 'random',  # 'random' or 'time_based'
            'force_group': None  # None, 'traditional', or 'ml_enhanced' for testing
        }
        
        # Metrics tracking
        self.current_metrics = {
            'traditional': self._init_metrics(),
            'ml_enhanced': self._init_metrics()
        }
        
        # Initialize database
        self._init_database()
        
        # Load existing results
        self._load_historical_results()
        
        logger.info(f"A/B Testing Service initialized with {test_allocation:.0%} ML allocation")
    
    def _init_metrics(self) -> Dict[str, Any]:
        """Initialize metrics structure"""
        return {
            'total_signals': 0,
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0.0,
            'avg_pnl_per_trade': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'avg_trade_duration': 0.0,
            'confidence_scores': [],
            'position_sizes': []
        }
    
    def _init_database(self):
        """Initialize SQLite database for storing A/B test results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ab_test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        exit_price REAL,
                        position_size REAL NOT NULL,
                        pnl REAL,
                        win INTEGER,
                        duration_minutes INTEGER,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_group_timestamp 
                    ON ab_test_results(group_name, timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON ab_test_results(timestamp)
                """)
                
                conn.commit()
                logger.info("A/B testing database initialized")
                
        except Exception as e:
            logger.error(f"Error initializing A/B testing database: {e}")
    
    def _load_historical_results(self):
        """Load historical A/B test results from database"""
        try:
            # Load last 30 days of results
            cutoff_date = datetime.now() - timedelta(days=30)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM ab_test_results 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_date.isoformat(),))
                
                results = cursor.fetchall()
                
                for row in results:
                    result = ABTestResult(
                        group=row[1],
                        signal_type=row[2],
                        confidence=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        entry_price=row[5],
                        exit_price=row[6],
                        position_size=row[7],
                        pnl=row[8],
                        win=bool(row[9]) if row[9] is not None else None,
                        duration_minutes=row[10],
                        metadata=json.loads(row[11]) if row[11] else {}
                    )
                    
                    self.test_results[result.group].append(result)
                
                logger.info(f"Loaded {len(results)} historical A/B test results")
                
                # Recalculate metrics
                self._recalculate_metrics()
                
        except Exception as e:
            logger.error(f"Error loading historical results: {e}")
    
    def assign_test_group(self, signal_data: Dict[str, Any]) -> str:
        """
        Assign a signal to either 'traditional' or 'ml_enhanced' test group
        
        Args:
            signal_data: Signal information for assignment decision
            
        Returns:
            Group name: 'traditional' or 'ml_enhanced'
        """
        if not self.config['enabled']:
            return 'ml_enhanced'  # Default to ML if A/B testing disabled
        
        # Check for forced group assignment (for testing)
        if self.config['force_group']:
            return self.config['force_group']
        
        # Random assignment based on allocation
        if self.config['allocation_method'] == 'random':
            import random
            return 'ml_enhanced' if random.random() < self.test_allocation else 'traditional'
        
        # Time-based assignment (alternating)
        elif self.config['allocation_method'] == 'time_based':
            total_signals = sum(self.current_metrics[group]['total_signals'] for group in self.current_metrics)
            return 'ml_enhanced' if total_signals % 2 == 0 else 'traditional'
        
        # Default to random
        import random
        return 'ml_enhanced' if random.random() < self.test_allocation else 'traditional'
    
    def record_signal(self, group: str, signal_data: Dict[str, Any]) -> str:
        """
        Record a signal assignment for A/B testing
        
        Args:
            group: Test group ('traditional' or 'ml_enhanced')
            signal_data: Signal information
            
        Returns:
            Test ID for tracking this signal
        """
        try:
            # Create test result record
            result = ABTestResult(
                group=group,
                signal_type=signal_data.get('signal_type', 'unknown'),
                confidence=signal_data.get('confidence', 0.5),
                timestamp=datetime.now(),
                entry_price=signal_data.get('current_price', 0.0),
                position_size=signal_data.get('position_size', 0.0),
                metadata=signal_data
            )
            
            # Store in memory
            self.test_results[group].append(result)
            
            # Update metrics
            self.current_metrics[group]['total_signals'] += 1
            self.current_metrics[group]['confidence_scores'].append(result.confidence)
            self.current_metrics[group]['position_sizes'].append(result.position_size)
            
            # Store in database
            self._save_result_to_db(result)
            
            logger.debug(f"Recorded {group} signal: {result.signal_type} "
                        f"(confidence: {result.confidence:.1%})")
            
            return f"{group}_{result.timestamp.isoformat()}"
            
        except Exception as e:
            logger.error(f"Error recording signal for group {group}: {e}")
            return ""
    
    def record_trade_outcome(self, test_id: str, outcome_data: Dict[str, Any]):
        """
        Record the outcome of a trade for A/B testing
        
        Args:
            test_id: Test ID from record_signal
            outcome_data: Trade outcome information
        """
        try:
            # Parse test ID to find the result
            if '_' not in test_id:
                logger.warning(f"Invalid test ID format: {test_id}")
                return
            
            group, timestamp_str = test_id.split('_', 1)
            timestamp = datetime.fromisoformat(timestamp_str)
            
            # Find the corresponding result
            for result in self.test_results[group]:
                if result.timestamp == timestamp:
                    # Update result with outcome
                    result.exit_price = outcome_data.get('exit_price')
                    result.pnl = outcome_data.get('pnl', 0.0)
                    result.win = outcome_data.get('pnl', 0.0) > 0
                    
                    # Calculate duration
                    if 'exit_timestamp' in outcome_data:
                        exit_time = datetime.fromisoformat(outcome_data['exit_timestamp'])
                        result.duration_minutes = int((exit_time - result.timestamp).total_seconds() / 60)
                    
                    # Update metrics
                    self._update_metrics_for_trade(group, result)
                    
                    # Update database
                    self._update_result_in_db(result)
                    
                    logger.debug(f"Recorded trade outcome for {group}: "
                               f"PnL=${result.pnl:.2f}, Win={result.win}")
                    break
            else:
                logger.warning(f"Could not find result for test ID: {test_id}")
                
        except Exception as e:
            logger.error(f"Error recording trade outcome: {e}")
    
    def _update_metrics_for_trade(self, group: str, result: ABTestResult):
        """Update metrics when a trade is completed"""
        metrics = self.current_metrics[group]
        
        metrics['total_trades'] += 1
        
        if result.win is not None:
            if result.win:
                metrics['wins'] += 1
            else:
                metrics['losses'] += 1
        
        if result.pnl is not None:
            metrics['total_pnl'] += result.pnl
            metrics['avg_pnl_per_trade'] = metrics['total_pnl'] / metrics['total_trades']
        
        if result.duration_minutes is not None:
            # Calculate average duration
            durations = [r.duration_minutes for r in self.test_results[group] 
                        if r.duration_minutes is not None]
            if durations:
                metrics['avg_trade_duration'] = statistics.mean(durations)
        
        # Calculate win rate
        if metrics['total_trades'] > 0:
            metrics['win_rate'] = metrics['wins'] / metrics['total_trades']
        
        # Calculate Sharpe ratio (simplified)
        pnls = [r.pnl for r in self.test_results[group] if r.pnl is not None]
        if len(pnls) > 1:
            avg_return = statistics.mean(pnls)
            return_std = statistics.stdev(pnls)
            metrics['sharpe_ratio'] = avg_return / return_std if return_std > 0 else 0.0
        
        # Calculate max drawdown (simplified)
        if pnls:
            cumulative = np.cumsum(pnls)
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = (cumulative - running_max) / np.maximum(running_max, 1)
            metrics['max_drawdown'] = abs(min(drawdowns)) if len(drawdowns) > 0 else 0.0
    
    def _recalculate_metrics(self):
        """Recalculate all metrics from scratch"""
        for group in ['traditional', 'ml_enhanced']:
            self.current_metrics[group] = self._init_metrics()
            
            for result in self.test_results[group]:
                self.current_metrics[group]['total_signals'] += 1
                self.current_metrics[group]['confidence_scores'].append(result.confidence)
                
                if result.position_size:
                    self.current_metrics[group]['position_sizes'].append(result.position_size)
                
                if result.pnl is not None:
                    self._update_metrics_for_trade(group, result)
    
    def get_current_results(self) -> Dict[str, Any]:
        """Get current A/B testing results"""
        return {
            'config': self.config,
            'metrics': self.current_metrics,
            'test_summary': {
                'total_signals': sum(m['total_signals'] for m in self.current_metrics.values()),
                'total_trades': sum(m['total_trades'] for m in self.current_metrics.values()),
                'ml_allocation': self.test_allocation,
                'test_duration_days': self.config['test_duration_days']
            },
            'comparison': self._calculate_comparison_metrics(),
            'statistical_significance': self._calculate_statistical_significance()
        }
    
    def _calculate_comparison_metrics(self) -> Dict[str, Any]:
        """Calculate comparison metrics between groups"""
        traditional = self.current_metrics['traditional']
        ml_enhanced = self.current_metrics['ml_enhanced']
        
        comparison = {}
        
        # Win rate improvement
        if traditional['total_trades'] > 0 and ml_enhanced['total_trades'] > 0:
            win_rate_diff = ml_enhanced['win_rate'] - traditional['win_rate']
            comparison['win_rate_improvement'] = win_rate_diff
            comparison['win_rate_improvement_pct'] = (win_rate_diff / traditional['win_rate'] * 100) if traditional['win_rate'] > 0 else 0
        
        # Sharpe ratio improvement
        if traditional['sharpe_ratio'] != 0 and ml_enhanced['sharpe_ratio'] != 0:
            sharpe_diff = ml_enhanced['sharpe_ratio'] - traditional['sharpe_ratio']
            comparison['sharpe_improvement'] = sharpe_diff
            comparison['sharpe_improvement_pct'] = (sharpe_diff / abs(traditional['sharpe_ratio']) * 100) if traditional['sharpe_ratio'] != 0 else 0
        
        # Drawdown improvement (lower is better)
        if traditional['max_drawdown'] > 0 and ml_enhanced['max_drawdown'] > 0:
            drawdown_diff = traditional['max_drawdown'] - ml_enhanced['max_drawdown']
            comparison['drawdown_improvement'] = drawdown_diff
            comparison['drawdown_improvement_pct'] = (drawdown_diff / traditional['max_drawdown'] * 100) if traditional['max_drawdown'] > 0 else 0
        
        # PnL improvement
        if traditional['total_trades'] > 0 and ml_enhanced['total_trades'] > 0:
            pnl_diff = ml_enhanced['avg_pnl_per_trade'] - traditional['avg_pnl_per_trade']
            comparison['pnl_improvement'] = pnl_diff
            comparison['pnl_improvement_pct'] = (pnl_diff / abs(traditional['avg_pnl_per_trade']) * 100) if traditional['avg_pnl_per_trade'] != 0 else 0
        
        return comparison
    
    def _calculate_statistical_significance(self) -> Dict[str, Any]:
        """Calculate statistical significance of results"""
        try:
            from scipy import stats
            HAS_SCIPY = True
        except ImportError:
            HAS_SCIPY = False
        
        significance = {'has_scipy': HAS_SCIPY}
        
        if not HAS_SCIPY:
            significance['message'] = 'Install scipy for statistical significance testing'
            return significance
        
        # Get PnL data for both groups
        traditional_pnls = [r.pnl for r in self.test_results['traditional'] if r.pnl is not None]
        ml_pnls = [r.pnl for r in self.test_results['ml_enhanced'] if r.pnl is not None]
        
        if len(traditional_pnls) < 10 or len(ml_pnls) < 10:
            significance['message'] = 'Insufficient data for significance testing'
            return significance
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(ml_pnls, traditional_pnls)
        
        significance.update({
            'sample_sizes': {
                'traditional': len(traditional_pnls),
                'ml_enhanced': len(ml_pnls)
            },
            't_statistic': t_stat,
            'p_value': p_value,
            'is_significant': p_value < self.config['significance_level'],
            'confidence_level': (1 - self.config['significance_level']) * 100
        })
        
        return significance
    
    def _save_result_to_db(self, result: ABTestResult):
        """Save A/B test result to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO ab_test_results 
                    (group_name, signal_type, confidence, timestamp, entry_price, 
                     exit_price, position_size, pnl, win, duration_minutes, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.group,
                    result.signal_type,
                    result.confidence,
                    result.timestamp.isoformat(),
                    result.entry_price,
                    result.exit_price,
                    result.position_size,
                    result.pnl,
                    result.win,
                    result.duration_minutes,
                    json.dumps(result.metadata) if result.metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving result to database: {e}")
    
    def _update_result_in_db(self, result: ABTestResult):
        """Update A/B test result in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE ab_test_results 
                    SET exit_price = ?, pnl = ?, win = ?, duration_minutes = ?
                    WHERE group_name = ? AND timestamp = ?
                """, (
                    result.exit_price,
                    result.pnl,
                    result.win,
                    result.duration_minutes,
                    result.group,
                    result.timestamp.isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating result in database: {e}")
    
    def set_config(self, **kwargs):
        """Update A/B testing configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated A/B testing config: {key} = {value}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for dashboard display"""
        results = self.get_current_results()
        
        return {
            'enabled': self.config['enabled'],
            'allocation': self.test_allocation,
            'total_signals': results['test_summary']['total_signals'],
            'total_trades': results['test_summary']['total_trades'],
            'traditional_metrics': self.current_metrics['traditional'],
            'ml_enhanced_metrics': self.current_metrics['ml_enhanced'],
            'comparison': results['comparison'],
            'statistical_significance': results['statistical_significance'],
            'last_update': datetime.now().isoformat()
        }

# Global A/B testing service instance
_ab_testing_service = None

def get_ab_testing_service() -> ABTestingService:
    """Get global A/B testing service instance"""
    global _ab_testing_service
    if _ab_testing_service is None:
        _ab_testing_service = ABTestingService()
    return _ab_testing_service