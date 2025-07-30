# ML-Enhanced Kelly Criterion - Technical Specification

## 🎯 System Architecture

### Core Mathematical Foundation

The Kelly Criterion determines optimal position sizing based on edge and odds:

```python
def kelly_criterion(win_probability: float, win_loss_ratio: float) -> float:
    """
    Calculate optimal position size using Kelly Criterion
    
    Args:
        win_probability: P(win) from ML models [0, 1]
        win_loss_ratio: Average win / Average loss ratio
        
    Returns:
        Optimal fraction of capital to risk [0, 1]
    """
    if win_probability <= 0 or win_loss_ratio <= 0:
        return 0.0
    
    # Kelly formula: f* = (bp - q) / b
    # where b = win_loss_ratio, p = win_probability, q = 1 - win_probability
    edge = (win_loss_ratio * win_probability) - (1 - win_probability)
    kelly_fraction = edge / win_loss_ratio
    
    # Cap at maximum 25% of capital for safety
    return max(0.0, min(kelly_fraction, 0.25))
```

---

## 🧠 ML Model Integration

### Probability Estimation Framework

```python
class MLProbabilityEstimator:
    """Convert ML model outputs to Kelly-compatible probabilities"""
    
    def __init__(self):
        self.lstm_weight = 0.4      # LSTM historical accuracy weighting
        self.ensemble_weight = 0.6  # Ensemble historical accuracy weighting
        self.confidence_threshold = 0.6  # Minimum confidence for trading
    
    def estimate_win_probability(self, 
                               lstm_prediction: Dict,
                               ensemble_prediction: Dict) -> float:
        """
        Aggregate ML model predictions into single probability estimate
        
        Returns probability that trade will be profitable
        """
        # Extract confidence scores and directions
        lstm_conf = lstm_prediction.get('confidence', 0.5)
        lstm_direction = lstm_prediction.get('direction', 'neutral')
        
        ensemble_conf = ensemble_prediction.get('confidence', 0.5) 
        ensemble_direction = ensemble_prediction.get('direction', 'neutral')
        
        # Only proceed if models agree on direction
        if lstm_direction != ensemble_direction:
            return 0.5  # Neutral probability when models disagree
        
        # Weighted average of confidence scores
        combined_confidence = (
            self.lstm_weight * lstm_conf + 
            self.ensemble_weight * ensemble_conf
        )
        
        # Apply confidence threshold
        if combined_confidence < self.confidence_threshold:
            return 0.5  # Don't trade below confidence threshold
            
        return combined_confidence
    
    def estimate_win_loss_ratio(self, symbol: str, lookback_days: int = 30) -> float:
        """
        Calculate historical win/loss ratio for symbol
        Uses actual trading history from State Manager
        """
        # Implementation will query historical trades from database
        # and calculate average win size / average loss size
        pass
```

---

## 🔄 Service Architecture

### Kelly Calculator Service

```python
class KellyCalculatorService:
    """Core Kelly Criterion calculation service"""
    
    def __init__(self):
        self.probability_estimator = MLProbabilityEstimator()
        self.position_sizer = RiskAdjustedPositionSizer()
        self.min_kelly_fraction = 0.01  # Minimum 1% position
        self.max_kelly_fraction = 0.25  # Maximum 25% position
        
    async def calculate_optimal_position(self, 
                                       symbol: str,
                                       ml_predictions: Dict) -> Dict:
        """
        Main entry point for Kelly-based position sizing
        
        Returns:
        {
            'symbol': 'NQU25-CME',
            'kelly_fraction': 0.15,
            'position_size': 2,  # Number of contracts
            'confidence': 0.73,
            'win_probability': 0.68,
            'win_loss_ratio': 1.45,
            'risk_adjusted': True,
            'max_capital_risk': 0.15  # 15% of total capital
        }
        """
        # Extract ML predictions
        lstm_pred = ml_predictions.get('lstm', {})
        ensemble_pred = ml_predictions.get('ensemble', {})
        
        # Estimate win probability from ML models
        win_prob = self.probability_estimator.estimate_win_probability(
            lstm_pred, ensemble_pred
        )
        
        # Get historical win/loss ratio
        win_loss_ratio = await self.probability_estimator.estimate_win_loss_ratio(symbol)
        
        # Calculate Kelly fraction
        kelly_fraction = kelly_criterion(win_prob, win_loss_ratio)
        
        # Apply risk adjustments
        risk_adjusted_size = await self.position_sizer.apply_risk_constraints(
            symbol, kelly_fraction, win_prob
        )
        
        return {
            'symbol': symbol,
            'kelly_fraction': kelly_fraction,
            'position_size': risk_adjusted_size['contracts'],
            'confidence': max(lstm_pred.get('confidence', 0), ensemble_pred.get('confidence', 0)),
            'win_probability': win_prob,
            'win_loss_ratio': win_loss_ratio,
            'risk_adjusted': risk_adjusted_size['was_adjusted'],
            'max_capital_risk': risk_adjusted_size['capital_fraction'],
            'reasoning': f"Kelly: {kelly_fraction:.3f}, Risk-adj: {risk_adjusted_size['capital_fraction']:.3f}"
        }
```

### Risk-Adjusted Position Sizer

```python
class RiskAdjustedPositionSizer:
    """Apply additional risk constraints to Kelly-optimized positions"""
    
    def __init__(self):
        self.max_position_size = 5      # Max contracts per position
        self.max_portfolio_risk = 0.20  # Max 20% total capital at risk
        self.max_correlation_limit = 0.15  # Max 15% in correlated positions
        
    async def apply_risk_constraints(self, 
                                   symbol: str, 
                                   kelly_fraction: float,
                                   win_probability: float) -> Dict:
        """
        Apply portfolio-level risk constraints to Kelly calculation
        """
        # Get current portfolio state
        portfolio_state = await self.get_portfolio_state()
        
        # Calculate position size in contracts
        account_value = portfolio_state['total_capital']
        contract_value = await self.get_contract_value(symbol)
        
        # Kelly-suggested position size
        kelly_capital = kelly_fraction * account_value
        kelly_contracts = int(kelly_capital / contract_value)
        
        # Apply constraints
        final_contracts = min(kelly_contracts, self.max_position_size)
        
        # Check portfolio-level risk
        current_risk = portfolio_state['total_risk_fraction']
        position_risk = (final_contracts * contract_value) / account_value
        
        if current_risk + position_risk > self.max_portfolio_risk:
            # Reduce position to stay within portfolio risk limit
            max_additional_risk = self.max_portfolio_risk - current_risk
            max_contracts = int((max_additional_risk * account_value) / contract_value)
            final_contracts = min(final_contracts, max_contracts)
        
        # Check correlation limits (implementation depends on position correlation tracking)
        final_contracts = await self.apply_correlation_limits(symbol, final_contracts)
        
        return {
            'contracts': max(0, final_contracts),
            'capital_fraction': (final_contracts * contract_value) / account_value,
            'was_adjusted': final_contracts != kelly_contracts,
            'kelly_suggested': kelly_contracts,
            'risk_reason': self.get_adjustment_reason(kelly_contracts, final_contracts)
        }
    
    def get_adjustment_reason(self, kelly_contracts: int, final_contracts: int) -> str:
        """Explain why position was adjusted from Kelly suggestion"""
        if final_contracts == kelly_contracts:
            return "No adjustment needed"
        elif final_contracts < kelly_contracts:
            return "Reduced due to risk constraints"
        else:
            return "Increased due to minimum position requirements"
```

---

## 📊 Dashboard Integration

### API Endpoints

```python
# New API endpoints for Kelly Criterion dashboard integration
@router.get("/api/kelly/current-positions")
async def get_kelly_positions():
    """Get current Kelly-optimized position recommendations"""
    
@router.get("/api/kelly/performance-history") 
async def get_kelly_performance():
    """Historical Kelly Criterion performance vs fixed sizing"""
    
@router.get("/api/kelly/risk-metrics")
async def get_kelly_risk_metrics():
    """Current Kelly-based risk metrics and constraints"""
```

### Dashboard Widgets

```python
class KellyDashboardWidget:
    """Dashboard component for Kelly Criterion monitoring"""
    
    def render_kelly_metrics(self) -> str:
        """
        HTML template for Kelly metrics display:
        - Current Kelly fraction recommendations
        - Win probability estimates  
        - Risk-adjusted position sizes
        - Historical Kelly performance
        """
        return """
        <div class="kelly-metrics-panel">
            <h3>🎯 Kelly Position Sizing</h3>
            <div class="kelly-recommendation">
                <span class="symbol">NQU25-CME</span>
                <span class="kelly-fraction">15.3%</span>
                <span class="contracts">2 contracts</span>
                <span class="confidence">73% confidence</span>
            </div>
            <div class="risk-metrics">
                <span>Win Prob: 68%</span>
                <span>W/L Ratio: 1.45</span>
                <span>Port Risk: 15.3%</span>
            </div>
        </div>
        """
```

---

## 🔗 Integration Points

### Existing Services Integration

```python
class KellyIntegrationLayer:
    """Coordinates Kelly service with existing MinhOS architecture"""
    
    def __init__(self):
        self.ml_models = {
            'lstm': self.get_lstm_service(),
            'ensemble': self.get_ensemble_service()
        }
        self.risk_manager = get_risk_manager()
        self.trading_engine = get_trading_engine()
        self.state_manager = get_state_manager()
    
    async def get_ml_predictions(self, symbol: str) -> Dict:
        """Gather predictions from all ML models"""
        predictions = {}
        
        # Get LSTM prediction
        lstm_service = self.ml_models['lstm']
        predictions['lstm'] = await lstm_service.get_prediction(symbol)
        
        # Get Ensemble prediction  
        ensemble_service = self.ml_models['ensemble']
        predictions['ensemble'] = await ensemble_service.get_prediction(symbol)
        
        return predictions
    
    async def execute_kelly_trade(self, symbol: str) -> Dict:
        """Complete Kelly-based trading workflow"""
        
        # 1. Get ML predictions
        ml_predictions = await self.get_ml_predictions(symbol)
        
        # 2. Calculate Kelly position size
        kelly_calc = KellyCalculatorService()
        position_rec = await kelly_calc.calculate_optimal_position(symbol, ml_predictions)
        
        # 3. Validate with Risk Manager
        risk_approval = await self.risk_manager.validate_position(position_rec)
        
        if not risk_approval['approved']:
            return {'status': 'rejected', 'reason': risk_approval['reason']}
        
        # 4. Execute trade via Trading Engine
        trade_result = await self.trading_engine.execute_trade({
            'symbol': symbol,
            'size': position_rec['position_size'],
            'reasoning': f"Kelly-optimized: {position_rec['reasoning']}"
        })
        
        # 5. Log Kelly decision for performance tracking
        await self.state_manager.log_kelly_decision(position_rec, trade_result)
        
        return {
            'status': 'executed',
            'kelly_fraction': position_rec['kelly_fraction'],
            'position_size': position_rec['position_size'],
            'trade_id': trade_result['trade_id']
        }
```

---

## 🧪 Testing Framework

### Mathematical Validation Tests

```python
def test_kelly_formula_accuracy():
    """Test Kelly formula mathematical accuracy"""
    # Known Kelly results for validation
    test_cases = [
        {'win_prob': 0.6, 'win_loss_ratio': 2.0, 'expected': 0.1},   # 10% position
        {'win_prob': 0.7, 'win_loss_ratio': 1.5, 'expected': 0.133}, # 13.3% position  
        {'win_prob': 0.5, 'win_loss_ratio': 1.0, 'expected': 0.0},   # No edge = no position
    ]
    
    for case in test_cases:
        result = kelly_criterion(case['win_prob'], case['win_loss_ratio'])
        assert abs(result - case['expected']) < 0.001, f"Kelly calculation failed for {case}"

def test_probability_estimation():
    """Test ML model probability aggregation"""
    estimator = MLProbabilityEstimator()
    
    # Test model agreement
    lstm_pred = {'confidence': 0.8, 'direction': 'long'}
    ensemble_pred = {'confidence': 0.7, 'direction': 'long'}
    prob = estimator.estimate_win_probability(lstm_pred, ensemble_pred)
    assert 0.7 <= prob <= 0.8, "Probability should be weighted average"
    
    # Test model disagreement
    lstm_pred = {'confidence': 0.8, 'direction': 'long'}
    ensemble_pred = {'confidence': 0.7, 'direction': 'short'}
    prob = estimator.estimate_win_probability(lstm_pred, ensemble_pred)
    assert prob == 0.5, "Disagreeing models should return neutral probability"
```

---

## ⚠️ Implementation Considerations

### Performance Requirements
- **Latency**: Kelly calculations must complete within 50ms for real-time trading
- **Accuracy**: Mathematical calculations accurate to 6 decimal places  
- **Reliability**: 99.9% uptime during trading hours
- **Scalability**: Support for multiple symbols simultaneously

### Risk Management
- **Conservative Estimates**: Always err on side of smaller position sizes
- **Circuit Breakers**: Stop Kelly calculations if ML model confidence drops below threshold
- **Portfolio Limits**: Never exceed overall portfolio risk limits regardless of Kelly suggestion
- **Historical Validation**: Continuously validate Kelly performance vs fixed sizing

### Data Dependencies
- **ML Model Predictions**: Requires LSTM and Ensemble services operational
- **Historical Trade Data**: Needs access to past trade results for win/loss ratio calculations
- **Real-time Market Data**: Requires current prices for position size calculations
- **Account Information**: Needs current capital and position information

---

This technical specification provides the detailed framework for implementing ML-Enhanced Kelly Criterion as a core component of your trading system's position sizing optimization.