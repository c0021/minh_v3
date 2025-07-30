# Kelly Criterion - Mathematical Foundation

## 🧮 The Kelly Criterion Formula

The Kelly Criterion determines the optimal fraction of capital to wager based on the expected value of a bet with known probabilities and payoffs.

### Basic Formula
```
f* = (bp - q) / b
```

Where:
- **f*** = Optimal fraction of capital to bet
- **b** = Odds received on the wager (reward/risk ratio)
- **p** = Probability of winning
- **q** = Probability of losing = (1 - p)

### Trading Context Translation
```python
def kelly_fraction_for_trading(win_probability: float, avg_win: float, avg_loss: float) -> float:
    """
    Kelly Criterion adapted for trading
    
    Args:
        win_probability: P(profitable trade) [0, 1]
        avg_win: Average winning trade profit
        avg_loss: Average losing trade loss (positive number)
        
    Returns:
        Optimal fraction of capital to risk [0, 1]
    """
    if win_probability <= 0 or avg_win <= 0 or avg_loss <= 0:
        return 0.0
    
    # In trading: b = avg_win / avg_loss (reward/risk ratio)
    reward_risk_ratio = avg_win / avg_loss
    
    # Kelly formula
    edge = (reward_risk_ratio * win_probability) - (1 - win_probability)
    kelly_fraction = edge / reward_risk_ratio
    
    return max(0.0, kelly_fraction)  # Never bet negative amounts
```

---

## 📊 Mathematical Properties

### Expected Growth Rate
The Kelly Criterion maximizes the expected logarithmic growth rate of capital:

```
E[log(1 + f*R)] = p * log(1 + f*b) + q * log(1 - f)
```

Where R is the random return of the investment.

### Optimal Growth
Kelly maximizes long-term wealth growth while minimizing the probability of ruin (losing all capital).

```python
def expected_growth_rate(f: float, p: float, b: float) -> float:
    """
    Calculate expected logarithmic growth rate for given Kelly fraction
    
    Args:
        f: Fraction of capital bet
        p: Win probability  
        b: Reward/risk ratio
        
    Returns:
        Expected growth rate per period
    """
    if f <= 0:
        return 0.0
    
    q = 1 - p  # Loss probability
    
    # Expected log growth
    win_growth = p * math.log(1 + f * b)
    loss_growth = q * math.log(1 - f) if f < 1 else float('-inf')
    
    return win_growth + loss_growth
```

### Risk of Ruin
Kelly Criterion minimizes the probability of losing all capital:

```python
def probability_of_ruin(f: float, p: float, b: float, initial_capital: float, ruin_level: float) -> float:
    """
    Calculate probability of capital falling below ruin level
    
    This is a simplified approximation - exact calculation requires complex mathematics
    """
    if f >= 1.0:
        return 1.0  # Certain ruin if betting entire capital
    
    if f <= 0:
        return 0.0  # No risk if not betting
    
    # Approximation using negative exponential
    edge = (b * p) - (1 - p)
    if edge <= 0:
        return 1.0  # Negative edge leads to certain ruin
    
    ruin_ratio = ruin_level / initial_capital
    
    # Simplified approximation
    return math.exp(-2 * edge * math.log(initial_capital / ruin_level))
```

---

## 🎯 ML Integration Mathematics

### Converting ML Confidence to Win Probability

ML models output confidence scores that need calibration to actual probabilities:

```python
def calibrate_ml_confidence_to_probability(confidence: float, historical_accuracy: float) -> float:
    """
    Convert ML model confidence to calibrated win probability
    
    Args:
        confidence: Raw ML confidence score [0, 1]
        historical_accuracy: Historical accuracy of ML model [0, 1]
        
    Returns:
        Calibrated probability for Kelly calculation
    """
    # Simple calibration using historical accuracy
    # More sophisticated: Platt scaling or isotonic regression
    
    if confidence < 0.5:
        # Model predicts loss - invert for opposite direction
        return (1 - confidence) * historical_accuracy + (1 - historical_accuracy) * 0.5
    else:
        # Model predicts win
        return confidence * historical_accuracy + (1 - historical_accuracy) * 0.5

def aggregate_model_probabilities(predictions: List[Dict]) -> float:
    """
    Aggregate multiple ML model predictions into single probability
    
    Args:
        predictions: List of {'confidence': float, 'accuracy': float, 'weight': float}
        
    Returns:
        Weighted probability estimate
    """
    if not predictions:
        return 0.5  # Neutral if no predictions
    
    total_weight = sum(pred['weight'] for pred in predictions)
    if total_weight == 0:
        return 0.5
    
    weighted_prob = 0.0
    for pred in predictions:
        calibrated_prob = calibrate_ml_confidence_to_probability(
            pred['confidence'], pred['accuracy']
        )
        weighted_prob += calibrated_prob * (pred['weight'] / total_weight)
    
    return weighted_prob
```

### Dynamic Win/Loss Ratio Calculation

```python
def calculate_dynamic_win_loss_ratio(trade_history: List[Dict], lookback_days: int = 30) -> float:
    """
    Calculate win/loss ratio from recent trading history
    
    Args:
        trade_history: List of trade records with 'pnl' and 'timestamp'
        lookback_days: Number of days to look back
        
    Returns:
        Average win / Average loss ratio
    """
    cutoff_date = datetime.now() - timedelta(days=lookback_days)
    
    # Filter recent trades
    recent_trades = [
        trade for trade in trade_history 
        if datetime.fromisoformat(trade['timestamp']) > cutoff_date
    ]
    
    if not recent_trades:
        return 1.0  # Default neutral ratio
    
    # Separate wins and losses
    wins = [trade['pnl'] for trade in recent_trades if trade['pnl'] > 0]
    losses = [abs(trade['pnl']) for trade in recent_trades if trade['pnl'] < 0]
    
    if not wins or not losses:
        return 1.0  # Need both wins and losses for ratio
    
    avg_win = sum(wins) / len(wins)
    avg_loss = sum(losses) / len(losses)
    
    return avg_win / avg_loss if avg_loss > 0 else 1.0
```

---

## ⚖️ Risk-Adjusted Kelly Variants

### Fractional Kelly
Reduce Kelly bet size to manage risk:

```python
def fractional_kelly(kelly_fraction: float, fraction: float = 0.5) -> float:
    """
    Apply fractional Kelly to reduce risk
    
    Args:
        kelly_fraction: Full Kelly recommendation
        fraction: Fraction of Kelly to use (e.g., 0.5 for half-Kelly)
        
    Returns:
        Risk-adjusted Kelly fraction
    """
    return kelly_fraction * fraction

def adaptive_fractional_kelly(kelly_fraction: float, recent_performance: float) -> float:
    """
    Dynamically adjust Kelly fraction based on recent performance
    
    Args:
        kelly_fraction: Full Kelly recommendation
        recent_performance: Recent strategy performance [-1, 1]
        
    Returns:
        Adaptively adjusted Kelly fraction
    """
    # Reduce Kelly fraction if recent performance is poor
    if recent_performance < -0.1:  # Poor performance
        return kelly_fraction * 0.25  # Quarter Kelly
    elif recent_performance < 0:    # Slightly negative
        return kelly_fraction * 0.5   # Half Kelly  
    elif recent_performance > 0.1:  # Good performance
        return kelly_fraction * 0.8   # 80% Kelly
    else:                           # Neutral performance
        return kelly_fraction * 0.6   # 60% Kelly
```

### Portfolio Kelly
Adjust for multiple simultaneous positions:

```python
def portfolio_adjusted_kelly(individual_kellys: List[float], correlations: np.ndarray) -> List[float]:
    """
    Adjust individual Kelly fractions for portfolio correlations
    
    Args:
        individual_kellys: Kelly fractions for each position
        correlations: Correlation matrix between positions
        
    Returns:
        Portfolio-adjusted Kelly fractions
    """
    n_positions = len(individual_kellys)
    
    if n_positions <= 1:
        return individual_kellys
    
    # Simple correlation adjustment - reduce Kelly fractions for correlated positions
    adjusted_kellys = []
    
    for i, kelly in enumerate(individual_kellys):
        # Calculate average correlation with other positions
        avg_correlation = np.mean([abs(correlations[i][j]) for j in range(n_positions) if i != j])
        
        # Reduce Kelly fraction based on correlation
        correlation_factor = 1.0 - (avg_correlation * 0.5)  # Max 50% reduction
        adjusted_kelly = kelly * correlation_factor
        
        adjusted_kellys.append(adjusted_kelly)
    
    return adjusted_kellys
```

---

## 🎲 Uncertainty and Model Risk

### Kelly with Parameter Uncertainty

```python
def robust_kelly_with_uncertainty(win_prob_estimate: float, 
                                win_prob_std: float,
                                win_loss_ratio_estimate: float,
                                win_loss_ratio_std: float,
                                confidence_level: float = 0.95) -> float:
    """
    Calculate conservative Kelly fraction accounting for parameter uncertainty
    
    Args:
        win_prob_estimate: Estimated win probability
        win_prob_std: Standard deviation of win probability estimate
        win_loss_ratio_estimate: Estimated win/loss ratio
        win_loss_ratio_std: Standard deviation of win/loss ratio estimate
        confidence_level: Confidence level for conservative estimate
        
    Returns:
        Conservative Kelly fraction
    """
    # Use lower confidence bound for conservative estimation
    z_score = 1.96 if confidence_level == 0.95 else 1.645  # 95% or 90% confidence
    
    # Conservative parameter estimates
    conservative_win_prob = max(0.01, win_prob_estimate - z_score * win_prob_std)
    conservative_win_loss_ratio = max(0.1, win_loss_ratio_estimate - z_score * win_loss_ratio_std)
    
    # Calculate Kelly with conservative parameters
    edge = (conservative_win_loss_ratio * conservative_win_prob) - (1 - conservative_win_prob)
    
    if edge <= 0:
        return 0.0  # No positive edge with conservative estimates
    
    conservative_kelly = edge / conservative_win_loss_ratio
    
    return max(0.0, conservative_kelly)
```

### Model Ensemble Kelly

```python
def ensemble_kelly_calculation(model_predictions: List[Dict]) -> Dict:
    """
    Calculate Kelly fraction using ensemble of model predictions
    
    Args:
        model_predictions: List of model predictions with uncertainty
        
    Returns:
        Ensemble Kelly calculation with confidence bounds
    """
    if not model_predictions:
        return {'kelly_fraction': 0.0, 'confidence': 0.0}
    
    # Calculate Kelly for each model
    individual_kellys = []
    model_weights = []
    
    for pred in model_predictions:
        win_prob = pred['win_probability']
        win_loss_ratio = pred['win_loss_ratio']
        model_accuracy = pred.get('historical_accuracy', 0.6)
        
        # Individual Kelly calculation
        kelly = kelly_fraction_for_trading(win_prob, win_loss_ratio * 100, 100)
        
        individual_kellys.append(kelly)
        model_weights.append(model_accuracy)  # Weight by historical accuracy
    
    # Weighted average Kelly
    total_weight = sum(model_weights)
    if total_weight == 0:
        return {'kelly_fraction': 0.0, 'confidence': 0.0}
    
    ensemble_kelly = sum(k * w for k, w in zip(individual_kellys, model_weights)) / total_weight
    
    # Calculate ensemble confidence (inverse of prediction variance)
    kelly_variance = sum(w * (k - ensemble_kelly)**2 for k, w in zip(individual_kellys, model_weights)) / total_weight
    ensemble_confidence = 1.0 / (1.0 + kelly_variance)
    
    return {
        'kelly_fraction': ensemble_kelly,
        'confidence': ensemble_confidence,
        'individual_kellys': individual_kellys,
        'model_weights': model_weights,
        'variance': kelly_variance
    }
```

---

## 📈 Performance Metrics

### Kelly Performance Evaluation

```python
def evaluate_kelly_performance(trades: List[Dict], kelly_fractions: List[float]) -> Dict:
    """
    Evaluate Kelly Criterion performance vs fixed position sizing
    
    Args:
        trades: Historical trades with PnL
        kelly_fractions: Kelly fractions used for each trade
        
    Returns:
        Performance comparison metrics
    """
    if len(trades) != len(kelly_fractions):
        raise ValueError("Trades and Kelly fractions must have same length")
    
    # Calculate Kelly returns
    kelly_returns = []
    fixed_returns = []  # Compare to fixed 10% position sizing
    fixed_fraction = 0.10
    
    for trade, kelly_f in zip(trades, kelly_fractions):
        pnl_fraction = trade['pnl'] / trade.get('capital_at_risk', 1000)
        
        kelly_return = kelly_f * pnl_fraction
        fixed_return = fixed_fraction * pnl_fraction
        
        kelly_returns.append(kelly_return)
        fixed_returns.append(fixed_return)
    
    # Performance metrics
    kelly_total_return = sum(kelly_returns)
    fixed_total_return = sum(fixed_returns)
    
    kelly_volatility = np.std(kelly_returns) if len(kelly_returns) > 1 else 0
    fixed_volatility = np.std(fixed_returns) if len(fixed_returns) > 1 else 0
    
    # Sharpe ratio approximation (assuming risk-free rate = 0)
    kelly_sharpe = (np.mean(kelly_returns) / kelly_volatility) if kelly_volatility > 0 else 0
    fixed_sharpe = (np.mean(fixed_returns) / fixed_volatility) if fixed_volatility > 0 else 0
    
    return {
        'kelly_total_return': kelly_total_return,
        'fixed_total_return': fixed_total_return,
        'kelly_outperformance': kelly_total_return - fixed_total_return,
        'kelly_sharpe_ratio': kelly_sharpe,
        'fixed_sharpe_ratio': fixed_sharpe,
        'kelly_volatility': kelly_volatility,
        'fixed_volatility': fixed_volatility,
        'number_of_trades': len(trades)
    }
```

This mathematical foundation provides the theoretical basis for implementing Kelly Criterion in your ML-enhanced trading system, ensuring optimal position sizing based on rigorous mathematical principles.