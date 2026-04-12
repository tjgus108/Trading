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


def test_all_signals_identical():
    """All signals are identical (perfect +1.0 correlation)."""
    tracker = SignalCorrelationTracker(["s1", "s2", "s3"])
    actions = [Action.BUY, Action.HOLD, Action.SELL, Action.BUY, Action.HOLD] * 5
    for a in actions:
        tracker.record_many({"s1": a, "s2": a, "s3": a})
    
    corr = tracker.correlation_matrix()
    assert corr is not None
    # All diagonal should be 1.0
    assert abs(corr.loc["s1", "s1"] - 1.0) < 0.001
    # All off-diagonal should be 1.0 (identical signals)
    assert abs(corr.loc["s1", "s2"] - 1.0) < 0.001
    assert abs(corr.loc["s2", "s3"] - 1.0) < 0.001
    
    pairs = tracker.high_correlation_pairs(threshold=0.99)
    assert len(pairs) == 3  # All pairs correlated


def test_perfect_negative_correlation():
    """Two signals with perfect negative correlation (-1.0)."""
    tracker = SignalCorrelationTracker(["buy_bias", "sell_bias"])
    # Alternate: buy_bias = BUY, sell_bias = SELL; then reversed
    for i in range(10):
        if i % 2 == 0:
            tracker.record("buy_bias", Action.BUY)
            tracker.record("sell_bias", Action.SELL)
        else:
            tracker.record("buy_bias", Action.SELL)
            tracker.record("sell_bias", Action.BUY)
    
    corr = tracker.correlation_matrix()
    assert corr is not None
    # Perfect negative correlation
    assert abs(corr.loc["buy_bias", "sell_bias"] + 1.0) < 0.001
    
    high_neg = tracker.high_correlation_pairs(threshold=0.5)
    assert any(a == "buy_bias" and b == "sell_bias" and r < -0.99 
               for a, b, r in high_neg)


def test_mixed_signals_with_one_negatively_correlated():
    """Three signals: s1 & s2 aligned, s3 opposite to them."""
    tracker = SignalCorrelationTracker(["aligned1", "aligned2", "contrarian"])
    
    # aligned1 & aligned2 move together; contrarian moves opposite
    for i in range(10):
        if i % 2 == 0:
            tracker.record_many({"aligned1": Action.BUY, "aligned2": Action.BUY, 
                               "contrarian": Action.SELL})
        else:
            tracker.record_many({"aligned1": Action.SELL, "aligned2": Action.SELL, 
                               "contrarian": Action.BUY})
    
    corr = tracker.correlation_matrix()
    assert corr is not None
    
    # aligned1 & aligned2 should be highly positively correlated
    assert corr.loc["aligned1", "aligned2"] > 0.8
    
    # aligned1 & contrarian should be negatively correlated
    assert corr.loc["aligned1", "contrarian"] < -0.5
    
    high_pairs = tracker.high_correlation_pairs(threshold=0.5)
    assert len(high_pairs) >= 1  # At least one pair over threshold
