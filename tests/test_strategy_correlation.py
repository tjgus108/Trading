"""Edge case tests for SignalCorrelationTracker."""
import pytest
from src.analysis.strategy_correlation import SignalCorrelationTracker
from src.strategy.base import Action


def test_empty_history_returns_none():
    tracker = SignalCorrelationTracker(["a", "b"])
    assert tracker.correlation_matrix() is None
    assert tracker.high_correlation_pairs() == []
    assert "insufficient" in tracker.summary()


def test_single_strategy_returns_none():
    tracker = SignalCorrelationTracker(["only"])
    for _ in range(10):
        tracker.record("only", Action.BUY)
    # Only one strategy — need >=2 for a matrix
    assert tracker.correlation_matrix() is None
