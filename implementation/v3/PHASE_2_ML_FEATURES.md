# Phase 2: ML Feature Integration Plan (Weeks 1-8)

## 🎯 Goal: Add LSTM, Ensemble Methods, and ML-Enhanced Kelly Criterion

**Prerequisites**: Phase 1 consolidation must be complete with clean architecture

---

## 🏗️ ML Feature Architecture

### Design Principle: Capabilities, Not Layers
Each ML feature is a self-contained capability that integrates cleanly:

```
minhos/
├── capabilities/              # ML features as capabilities
│   ├── prediction/           # Price prediction capability
│   │   ├── traditional/      # Existing technical analysis
│   │   ├── lstm/            # LSTM neural network
│   │   └── api.py           # Unified prediction API
│   │
│   ├── ensemble/            # Ensemble trading capability  
│   │   ├── models/          # XGBoost, LightGBM, RF
│   │   ├── fusion/          # Signal fusion logic
│   │   └── api.py          # Ensemble API
│   │
│   └── position_sizing/     # Position sizing capability
│       ├── fixed/           # Current fixed sizing
│       ├── kelly/           # ML-enhanced Kelly
│       └── api.py          # Sizing API
```

---

## 📅 Week 1-2: LSTM Price Prediction

### Week 1: LSTM Implementation
**File**: `/capabilities/prediction/lstm/`

#### Core Components:
1. **lstm_model.py** - TensorFlow LSTM architecture
   ```python
   - 200 LSTM units → 100 units → Dense layers
   - Attention mechanism for temporal patterns
   - Dropout for regularization
   - 20-step sequence input, 8 features
   ```

2. **data_pipeline.py** - Feature engineering
   ```python
   - Price features: returns, log returns, ratios
   - Technical indicators: RSI, MACD, Bollinger
   - Volume features: volume ratio, volume MA
   - Market microstructure: bid-ask, order flow
   ```

3. **trainer.py** - Model training
   ```python
   - Historical data loading from Sierra Chart
   - Train/validation split (80/20)
   - Early stopping, learning rate scheduling
   - Model versioning and storage
   ```

### Week 2: LSTM Integration
1. **Integration with ai_brain_service.py**
   ```python
   # In consolidated ai_brain_service.py
   from capabilities.prediction.lstm import LSTMPredictor
   
   async def analyze_market(self, data):
       traditional = await self.technical_analysis(data)
       lstm_pred = await self.lstm_predictor.predict(data)
       return self.combine_signals(traditional, lstm_pred)
   ```

2. **Dashboard Widget**
   - Real-time LSTM predictions display
   - Confidence visualization
   - Direction indicators (UP/DOWN/NEUTRAL)

3. **Performance Monitoring**
   - Track prediction accuracy
   - Compare with traditional signals
   - A/B testing framework

---

## 📅 Week 3-4: Ensemble Methods

### Week 3: Ensemble Models
**File**: `/capabilities/ensemble/`

#### Base Models:
1. **Random Forest** - Robust to overfitting
2. **XGBoost** - High performance gradient boosting
3. **LightGBM** - Fast training and inference
4. **CatBoost** - Handles categorical features well

#### Meta-Learning:
- Stacking ensemble with linear meta-learner
- Dynamic weight adjustment based on regime
- Model agreement scoring

### Week 4: Ensemble Integration
1. **Signal Fusion Algorithm**
   ```python
   - Weighted combination of models
   - Market regime detection
   - Confidence calibration
   - Parallel inference for speed
   ```

2. **Dashboard Components**
   - Model agreement visualization
   - Individual model predictions
   - Ensemble confidence display

---

## 📅 Week 5-6: ML-Enhanced Kelly Criterion

### Week 5: Kelly Calculator
**File**: `/capabilities/position_sizing/kelly/`

#### Components:
1. **probability_estimator.py**
   ```python
   - XGBoost classifier for win probability
   - Isotonic regression calibration
   - Feature importance tracking
   ```

2. **kelly_calculator.py**
   ```python
   - Quarter Kelly (25%) for safety
   - Volatility scaling
   - Correlation adjustments
   - Maximum position constraints
   ```

3. **backtester.py**
   - Historical performance validation
   - Compare with fixed sizing
   - Risk metrics calculation

### Week 6: Kelly Integration
1. **Integration with risk_service.py**
   ```python
   from capabilities.position_sizing.kelly import KellyCalculator
   
   async def calculate_position_size(self, signal, capital):
       if self.use_kelly:
           return await self.kelly.calculate_optimal_size(signal, capital)
       return self.fixed_size_calculator(capital)
   ```

2. **Safety Mechanisms**
   - Gradual Kelly adoption (start 25%)
   - Maximum position limits
   - Drawdown protection
   - Circuit breakers

---

## 📅 Week 7-8: System Integration & Optimization

### Week 7: Full Integration
1. **Unified ML Pipeline**
   - LSTM → Ensemble → Kelly chain
   - Performance monitoring dashboard
   - Real-time inference optimization

2. **A/B Testing Framework**
   - Traditional vs ML comparison
   - Gradual rollout controls
   - Performance metrics tracking

### Week 8: Production Optimization
1. **Performance Tuning**
   - Model inference caching
   - Batch prediction optimization
   - GPU utilization (if available)

2. **Monitoring & Alerts**
   - Model degradation detection
   - Automatic fallback triggers
   - Performance dashboards

---

## 🎯 Success Criteria

### Technical Metrics:
- LSTM accuracy: >65% directional accuracy
- Ensemble agreement: >70% on high-confidence signals  
- Kelly performance: >15% improvement vs fixed sizing
- Inference latency: <100ms for all predictions

### Business Metrics:
- Win rate improvement: +10-15%
- Sharpe ratio improvement: +25-50%
- Maximum drawdown reduction: -30-40%
- Risk-adjusted returns: +15-25%

---

## 🚨 Risk Management

### Model Risks:
1. **Overfitting Protection**
   - Regular out-of-sample validation
   - Walk-forward analysis
   - Cross-validation on different market regimes

2. **Failure Handling**
   - Automatic fallback to traditional analysis
   - Model confidence thresholds
   - Human override capabilities

### Implementation Risks:
1. **Gradual Adoption**
   - Start with paper trading
   - 25% → 50% → 100% allocation
   - Continuous monitoring

2. **Circuit Breakers**
   - Accuracy threshold: <40% triggers shutdown
   - Drawdown limit: -10% triggers review
   - Volatility spike: Reduces position sizes

---

## 📊 Monitoring Dashboard

### Real-Time Metrics:
```
┌─────────────────────────────────────┐
│ ML Model Performance                │
├─────────────────────────────────────┤
│ LSTM Accuracy (7d):     67.3% ✓    │
│ Ensemble Agreement:     78.2% ✓    │
│ Kelly Win Rate:        58.4% ✓    │
│                                     │
│ Current Predictions:                │
│ LSTM:      ↗️ UP (72% conf)        │
│ Ensemble:  ↗️ UP (68% conf)        │
│ Position:  2.3% (Kelly-sized)      │
└─────────────────────────────────────┘
```

---

## 🔧 Technical Stack

### Required Libraries:
```python
# Deep Learning
tensorflow==2.15.0
torch==2.2.0  # Alternative to TF

# ML Models
xgboost==2.0.3
lightgbm==4.1.0
catboost==1.2.2
scikit-learn==1.3.2

# Data Processing
pandas==2.0.3
numpy==1.24.3
ta-lib==0.4.26

# Model Management
mlflow==2.9.2
optuna==3.5.0  # Hyperparameter tuning
```

---

## 📝 Implementation Checklist

### Pre-Implementation:
- [ ] Phase 1 consolidation complete
- [ ] GPU availability confirmed
- [ ] Historical data access verified
- [ ] Backup/rollback plan ready

### Week-by-Week:
- [ ] Week 1: LSTM model implementation
- [ ] Week 2: LSTM integration & testing
- [ ] Week 3: Ensemble models implementation
- [ ] Week 4: Ensemble integration & fusion
- [ ] Week 5: Kelly criterion implementation
- [ ] Week 6: Kelly integration & safety
- [ ] Week 7: Full system integration
- [ ] Week 8: Production optimization

### Post-Implementation:
- [ ] Performance validation
- [ ] Documentation complete
- [ ] Monitoring operational
- [ ] Team training done