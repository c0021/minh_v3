"""
LSTM Neural Network Prediction Capability

Self-contained LSTM implementation for price direction prediction.
Integrates cleanly with consolidated ai_brain_service.py.
"""

from .lstm_predictor import LSTMPredictor

__all__ = ['LSTMPredictor']