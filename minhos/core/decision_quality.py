#!/usr/bin/env python3
"""
Decision Quality Framework for MinhOS v3
========================================

This module implements the Decision Quality scoring system that evaluates
trading decisions independent of their outcomes. This is the "HOW" that
leads to profitable trading through continuous improvement.

Philosophy: We measure the quality of our decision-making process, not just
the results. Good decisions can have bad outcomes due to market randomness,
but consistently high-quality decisions lead to long-term success.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class DecisionQualityCategory(Enum):
    """Categories for evaluating decision quality"""
    INFORMATION_ANALYSIS = "information_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    EXECUTION_DISCIPLINE = "execution_discipline"
    PATTERN_RECOGNITION = "pattern_recognition"
    MARKET_CONTEXT = "market_context"
    TIMING_QUALITY = "timing_quality"


@dataclass
class DecisionQualityScore:
    """Represents a decision quality evaluation"""
    decision_id: str
    timestamp: datetime
    
    # Category scores (0.0 to 1.0)
    information_analysis: float = 0.0  # How thoroughly was available info analyzed?
    risk_assessment: float = 0.0       # How well was risk evaluated?
    execution_discipline: float = 0.0  # Did we follow our plan without emotion?
    pattern_recognition: float = 0.0   # Quality of pattern identification
    market_context: float = 0.0        # Understanding of market conditions
    timing_quality: float = 0.0        # Entry/exit timing assessment
    
    # Overall quality score (weighted average)
    overall_score: float = 0.0
    
    # Detailed reasoning for each score
    reasoning: Dict[str, str] = field(default_factory=dict)
    
    # What we learned from this decision
    lessons_learned: List[str] = field(default_factory=list)
    
    # Decision details for context
    decision_details: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_overall_score(self):
        """Calculate weighted overall score"""
        # Equal weighting for now, can be adjusted based on importance
        weights = {
            'information_analysis': 0.20,
            'risk_assessment': 0.20,
            'execution_discipline': 0.20,
            'pattern_recognition': 0.15,
            'market_context': 0.15,
            'timing_quality': 0.10
        }
        
        self.overall_score = (
            self.information_analysis * weights['information_analysis'] +
            self.risk_assessment * weights['risk_assessment'] +
            self.execution_discipline * weights['execution_discipline'] +
            self.pattern_recognition * weights['pattern_recognition'] +
            self.market_context * weights['market_context'] +
            self.timing_quality * weights['timing_quality']
        )
        
        return self.overall_score


class DecisionQualityFramework:
    """
    Framework for evaluating and tracking decision quality independent of outcomes.
    This is the core of our process-focused trading philosophy.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize the Decision Quality Framework"""
        if db_path is None:
            # Use permanent location in data directory
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "decision_quality.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize SQLite database
        self._init_database()
        
        # Load existing decisions from database
        self.decision_history: List[DecisionQualityScore] = self._load_decisions_from_db()
        
        self.quality_thresholds = {
            'excellent': 0.85,
            'good': 0.70,
            'acceptable': 0.50,
            'poor': 0.0
        }
        
        # Track improvement over time (rebuilt from database)
        self.quality_trends = self._rebuild_trends_from_history()
        
        logger.info(f"Decision Quality Framework initialized with {len(self.decision_history)} historical decisions")
    
    def evaluate_decision(self,
                         decision_id: str,
                         ai_signal: Dict[str, Any],
                         market_data: Dict[str, Any],
                         risk_metrics: Dict[str, Any],
                         execution_details: Dict[str, Any]) -> DecisionQualityScore:
        """
        Evaluate the quality of a trading decision independent of outcome.
        
        This is the core method that implements our philosophy of measuring
        decision quality rather than just results.
        """
        logger.info(f"Evaluating decision quality for: {decision_id}")
        
        score = DecisionQualityScore(
            decision_id=decision_id,
            timestamp=datetime.now()
        )
        
        # 1. Information Analysis Quality
        score.information_analysis = self._evaluate_information_analysis(
            ai_signal, market_data
        )
        
        # 2. Risk Assessment Quality
        score.risk_assessment = self._evaluate_risk_assessment(
            risk_metrics, ai_signal
        )
        
        # 3. Execution Discipline
        score.execution_discipline = self._evaluate_execution_discipline(
            execution_details, ai_signal
        )
        
        # 4. Pattern Recognition Quality
        score.pattern_recognition = self._evaluate_pattern_recognition(
            ai_signal, market_data
        )
        
        # 5. Market Context Understanding
        score.market_context = self._evaluate_market_context(
            ai_signal, market_data
        )
        
        # 6. Timing Quality
        score.timing_quality = self._evaluate_timing(
            execution_details, market_data
        )
        
        # Calculate overall score
        score.calculate_overall_score()
        
        # Store decision details for learning
        score.decision_details = {
            'signal': ai_signal,
            'market_snapshot': market_data,
            'risk_snapshot': risk_metrics,
            'execution': execution_details
        }
        
        # Extract lessons learned
        score.lessons_learned = self._extract_lessons(score)
        
        # Track the decision
        self.decision_history.append(score)
        self._update_quality_trends(score)
        
        # Save to database
        self._save_decision_to_db(score)
        
        # Log the evaluation
        self._log_decision_quality(score)
        
        return score
    
    def _evaluate_information_analysis(self, 
                                     ai_signal: Dict[str, Any],
                                     market_data: Dict[str, Any]) -> float:
        """Evaluate how thoroughly available information was analyzed"""
        score = 0.0
        reasoning = []
        
        # Check if multiple timeframes were considered
        if ai_signal.get('timeframes_analyzed', 0) >= 3:
            score += 0.25
            reasoning.append("Multiple timeframes analyzed")
        
        # Check if volume was considered
        if ai_signal.get('volume_analysis') is not None:
            score += 0.20
            reasoning.append("Volume analysis included")
        
        # Check if technical indicators were used
        indicators_used = ai_signal.get('indicators_used', [])
        if len(indicators_used) >= 3:
            score += 0.25
            reasoning.append(f"Used {len(indicators_used)} technical indicators")
        
        # Check if market regime was identified
        if ai_signal.get('market_regime') is not None:
            score += 0.15
            reasoning.append("Market regime identified")
        
        # Check if confidence calculation was thorough
        if ai_signal.get('confidence_breakdown') is not None:
            score += 0.15
            reasoning.append("Detailed confidence breakdown provided")
        
        return min(1.0, score)
    
    def _evaluate_risk_assessment(self,
                                risk_metrics: Dict[str, Any],
                                ai_signal: Dict[str, Any]) -> float:
        """Evaluate the quality of risk assessment"""
        score = 0.0
        
        # Check if position sizing was calculated
        if risk_metrics.get('position_size_calculated', False):
            score += 0.25
        
        # Check if stop loss was defined
        if ai_signal.get('stop_loss') is not None:
            score += 0.25
        
        # Check if risk/reward ratio was calculated
        if risk_metrics.get('risk_reward_ratio') is not None:
            score += 0.25
        
        # Check if portfolio impact was considered
        if risk_metrics.get('portfolio_impact_assessed', False):
            score += 0.25
        
        return score
    
    def _evaluate_execution_discipline(self,
                                     execution_details: Dict[str, Any],
                                     ai_signal: Dict[str, Any]) -> float:
        """Evaluate if we followed our plan without emotional deviation"""
        score = 1.0  # Start with perfect score, deduct for deviations
        
        # Check if execution matched the plan
        planned_side = ai_signal.get('signal')
        executed_side = execution_details.get('side')
        if planned_side != executed_side:
            score -= 0.5
        
        # Check if position size matched plan
        planned_size = ai_signal.get('position_size')
        executed_size = execution_details.get('quantity')
        if planned_size and executed_size:
            size_deviation = abs(planned_size - executed_size) / planned_size
            if size_deviation > 0.1:  # More than 10% deviation
                score -= 0.25
        
        # Check if timing was disciplined (no hesitation)
        if execution_details.get('execution_delay_seconds', 0) > 60:
            score -= 0.25
        
        return max(0.0, score)
    
    def _evaluate_pattern_recognition(self,
                                    ai_signal: Dict[str, Any],
                                    market_data: Dict[str, Any]) -> float:
        """Evaluate the quality of pattern identification"""
        score = 0.0
        
        # Check if patterns were identified
        patterns = ai_signal.get('patterns_identified', [])
        if len(patterns) > 0:
            score += 0.40
        
        # Check pattern confidence levels
        if any(p.get('confidence', 0) > 0.8 for p in patterns):
            score += 0.30
        
        # Check if pattern context was considered
        if ai_signal.get('pattern_context') is not None:
            score += 0.30
        
        return score
    
    def _evaluate_market_context(self,
                               ai_signal: Dict[str, Any],
                               market_data: Dict[str, Any]) -> float:
        """Evaluate understanding of market conditions"""
        score = 0.0
        
        # Check if market session was considered
        if ai_signal.get('market_session') is not None:
            score += 0.25
        
        # Check if volatility was assessed
        if ai_signal.get('volatility_assessment') is not None:
            score += 0.25
        
        # Check if correlated markets were considered
        if ai_signal.get('correlated_markets_checked', False):
            score += 0.25
        
        # Check if news/events were considered
        if ai_signal.get('event_risk_considered', False):
            score += 0.25
        
        return score
    
    def _evaluate_timing(self,
                        execution_details: Dict[str, Any],
                        market_data: Dict[str, Any]) -> float:
        """Evaluate entry/exit timing quality"""
        # This is simplified - in reality would check against price action
        score = 0.5  # Default neutral score
        
        # Check if execution was near signal price
        signal_price = execution_details.get('signal_price')
        execution_price = execution_details.get('execution_price')
        
        if signal_price and execution_price:
            price_diff_pct = abs(signal_price - execution_price) / signal_price
            if price_diff_pct < 0.001:  # Within 0.1%
                score = 0.9
            elif price_diff_pct < 0.005:  # Within 0.5%
                score = 0.7
            elif price_diff_pct > 0.01:  # More than 1%
                score = 0.3
        
        return score
    
    def _extract_lessons(self, score: DecisionQualityScore) -> List[str]:
        """Extract lessons learned from this decision"""
        lessons = []
        
        # Identify weakest areas
        scores = {
            'Information Analysis': score.information_analysis,
            'Risk Assessment': score.risk_assessment,
            'Execution Discipline': score.execution_discipline,
            'Pattern Recognition': score.pattern_recognition,
            'Market Context': score.market_context,
            'Timing': score.timing_quality
        }
        
        weakest = min(scores.items(), key=lambda x: x[1])
        if weakest[1] < 0.5:
            lessons.append(f"Improve {weakest[0]} (scored {weakest[1]:.2f})")
        
        # Identify strengths
        strongest = max(scores.items(), key=lambda x: x[1])
        if strongest[1] > 0.8:
            lessons.append(f"Strong {strongest[0]} (scored {strongest[1]:.2f})")
        
        # Overall assessment
        if score.overall_score < 0.6:
            lessons.append("Focus on improving decision process before next trade")
        elif score.overall_score > 0.8:
            lessons.append("Excellent decision process - maintain these standards")
        
        return lessons
    
    def _update_quality_trends(self, score: DecisionQualityScore):
        """Track quality trends over time"""
        self.quality_trends['information_analysis'].append(score.information_analysis)
        self.quality_trends['risk_assessment'].append(score.risk_assessment)
        self.quality_trends['execution_discipline'].append(score.execution_discipline)
        self.quality_trends['pattern_recognition'].append(score.pattern_recognition)
        self.quality_trends['market_context'].append(score.market_context)
        self.quality_trends['timing_quality'].append(score.timing_quality)
        self.quality_trends['overall'].append(score.overall_score)
        
        # Keep only last 100 decisions for trend analysis
        for key in self.quality_trends:
            if len(self.quality_trends[key]) > 100:
                self.quality_trends[key] = self.quality_trends[key][-100:]
    
    def _log_decision_quality(self, score: DecisionQualityScore):
        """Log decision quality evaluation"""
        logger.info("=" * 60)
        logger.info("DECISION QUALITY EVALUATION")
        logger.info("=" * 60)
        logger.info(f"Decision ID: {score.decision_id}")
        logger.info(f"Overall Score: {score.overall_score:.2f} ({self._get_quality_label(score.overall_score)})")
        logger.info("-" * 60)
        logger.info(f"Information Analysis: {score.information_analysis:.2f}")
        logger.info(f"Risk Assessment: {score.risk_assessment:.2f}")
        logger.info(f"Execution Discipline: {score.execution_discipline:.2f}")
        logger.info(f"Pattern Recognition: {score.pattern_recognition:.2f}")
        logger.info(f"Market Context: {score.market_context:.2f}")
        logger.info(f"Timing Quality: {score.timing_quality:.2f}")
        logger.info("-" * 60)
        logger.info("Lessons Learned:")
        for lesson in score.lessons_learned:
            logger.info(f"  - {lesson}")
        logger.info("=" * 60)
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label for a score"""
        if score >= self.quality_thresholds['excellent']:
            return "EXCELLENT"
        elif score >= self.quality_thresholds['good']:
            return "GOOD"
        elif score >= self.quality_thresholds['acceptable']:
            return "ACCEPTABLE"
        else:
            return "POOR"
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get summary of decision quality over time"""
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'average_quality': 0.0,
                'quality_distribution': {},
                'improving_areas': [],
                'declining_areas': [],
                'strongest_area': None,
                'weakest_area': None
            }
        
        # Calculate averages
        recent_decisions = self.decision_history[-20:]  # Last 20 decisions
        
        avg_scores = {}
        for category in DecisionQualityCategory:
            key = category.value
            recent_scores = [getattr(d, key) for d in recent_decisions]
            avg_scores[key] = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        # Quality distribution
        quality_distribution = {
            'excellent': 0,
            'good': 0,
            'acceptable': 0,
            'poor': 0
        }
        
        for decision in self.decision_history:
            label = self._get_quality_label(decision.overall_score).lower()
            quality_distribution[label] += 1
        
        # Identify improving/declining areas
        improving_areas = []
        declining_areas = []
        
        for key, trend in self.quality_trends.items():
            if len(trend) >= 10:
                recent_avg = sum(trend[-5:]) / 5
                older_avg = sum(trend[-10:-5]) / 5
                improvement = recent_avg - older_avg
                
                if improvement > 0.1:
                    improving_areas.append((key, improvement))
                elif improvement < -0.1:
                    declining_areas.append((key, improvement))
        
        # Find strongest and weakest areas
        strongest = max(avg_scores.items(), key=lambda x: x[1]) if avg_scores else (None, 0)
        weakest = min(avg_scores.items(), key=lambda x: x[1]) if avg_scores else (None, 0)
        
        return {
            'total_decisions': len(self.decision_history),
            'average_quality': sum(d.overall_score for d in recent_decisions) / len(recent_decisions),
            'quality_distribution': quality_distribution,
            'improving_areas': improving_areas,
            'declining_areas': declining_areas,
            'strongest_area': strongest[0],
            'weakest_area': weakest[0],
            'category_averages': avg_scores,
            'recent_trend': 'improving' if len(improving_areas) > len(declining_areas) else 'declining'
        }
    
    def get_decision_by_id(self, decision_id: str) -> Optional[DecisionQualityScore]:
        """Retrieve a specific decision quality evaluation"""
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def export_quality_history(self, filepath: str):
        """Export decision quality history for analysis"""
        export_data = {
            'summary': self.get_quality_summary(),
            'decisions': [asdict(d) for d in self.decision_history],
            'trends': self.quality_trends,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Decision quality history exported to {filepath}")
    
    def _init_database(self):
        """Initialize SQLite database for decision quality persistence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_quality (
                    decision_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    information_analysis REAL NOT NULL,
                    risk_assessment REAL NOT NULL,
                    execution_discipline REAL NOT NULL,
                    pattern_recognition REAL NOT NULL,
                    market_context REAL NOT NULL,
                    timing_quality REAL NOT NULL,
                    overall_score REAL NOT NULL,
                    reasoning TEXT,
                    lessons_learned TEXT,
                    decision_details TEXT
                )
            """)
            
            # Create index for faster queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON decision_quality(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_overall_score ON decision_quality(overall_score)")
            conn.commit()
    
    def _save_decision_to_db(self, score: DecisionQualityScore):
        """Save decision quality score to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO decision_quality VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    score.decision_id,
                    score.timestamp.isoformat(),
                    score.information_analysis,
                    score.risk_assessment,
                    score.execution_discipline,
                    score.pattern_recognition,
                    score.market_context,
                    score.timing_quality,
                    score.overall_score,
                    json.dumps(score.reasoning),
                    json.dumps(score.lessons_learned),
                    json.dumps(score.decision_details, default=str)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving decision to database: {e}")
    
    def _load_decisions_from_db(self) -> List[DecisionQualityScore]:
        """Load existing decisions from database"""
        decisions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM decision_quality ORDER BY timestamp DESC LIMIT 100
                """)
                for row in cursor.fetchall():
                    score = DecisionQualityScore(
                        decision_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        information_analysis=row[2],
                        risk_assessment=row[3],
                        execution_discipline=row[4],
                        pattern_recognition=row[5],
                        market_context=row[6],
                        timing_quality=row[7],
                        overall_score=row[8],
                        reasoning=json.loads(row[9]) if row[9] else {},
                        lessons_learned=json.loads(row[10]) if row[10] else [],
                        decision_details=json.loads(row[11]) if row[11] else {}
                    )
                    decisions.append(score)
        except Exception as e:
            logger.error(f"Error loading decisions from database: {e}")
        
        return decisions
    
    def _rebuild_trends_from_history(self) -> Dict[str, List[float]]:
        """Rebuild quality trends from historical data"""
        trends = {
            'information_analysis': [],
            'risk_assessment': [],
            'execution_discipline': [],
            'pattern_recognition': [],
            'market_context': [],
            'timing_quality': [],
            'overall': []
        }
        
        # Get last 100 decisions for trends
        for decision in self.decision_history[-100:]:
            trends['information_analysis'].append(decision.information_analysis)
            trends['risk_assessment'].append(decision.risk_assessment)
            trends['execution_discipline'].append(decision.execution_discipline)
            trends['pattern_recognition'].append(decision.pattern_recognition)
            trends['market_context'].append(decision.market_context)
            trends['timing_quality'].append(decision.timing_quality)
            trends['overall'].append(decision.overall_score)
        
        return trends


# Singleton instance
_decision_quality_framework = None

def get_decision_quality_framework() -> DecisionQualityFramework:
    """Get or create the Decision Quality Framework singleton"""
    global _decision_quality_framework
    if _decision_quality_framework is None:
        _decision_quality_framework = DecisionQualityFramework()
    return _decision_quality_framework