"""
HighLowReversalStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.high_low_reversal import HighLowReversalStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 30,
    close_values=None,
    high_values=None,
    low_values=None,
) -> pd.DataFrame:
    """Mock DataFrame. _last() = iloc[-2]."""
    close = close_values if close_values is not None else [100.0] * n
    high = high_values if high_values is not None else [105.0] * n
    low = low_values if low_values is not None else [95.0] * n
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   high,
        "low":    low,
        "close":  close,
        "volume": [1000.0] * n,
    })


def _buy_df(n: int = 25, pos_val: float = 0.05) -> pd.DataFrame:
    """
    position[-2] = pos_val (< 0.2) AND pos_val > pos_ma.
    pos_ma will be low because all prior positions are ~0.
    We set close[-2] near low to achieve pos_val.
    """
    high = [105.0] * n
    low  = [95.0]  * n
    # position = (close - low) / (high - low) = pos_val → close = low + pos_val*(high-low)
    target_close = 95.0 + pos_val * 10.0
    close = [100.0] * n
    close[-2] = target_close
    # Make prior positions also low so pos_ma is low
    for i in range(n - 2):
        close[i] = 95.0 + 0.01 * 10.0  # position ~0.01
    return _make_df(n=n, close_values=close, high_values=high, low_values=low)


def _sell_df(n: int = 25, pos_val: float = 0.95) -> pd.DataFrame:
    """
    position[-2] = pos_val (> 0.8) AND pos_val < pos_ma.
    Prior positions are high so pos_ma is high.
    """
    high = [105.0] * n
    low  = [95.0]  * n
    target_close = 95.0 + pos_val * 10.0
    close = [100.0] * n
    # Prior positions very high → pos_ma high
    for i in range(n - 2):
        close[i] = 95.0 + 0.99 * 10.0  # position ~0.99
    close[-2] = target_close
    return _make_df(n=n, close_values=close, high_values=high, low_values=low)


# ── 기본 ──────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert HighLowReversalStrategy().name == "high_low_reversal"


def test_insufficient_data_returns_hold():
    s = HighLowReversalStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_insufficient_data_boundary():
    """n=19 < 20 → HOLD, n=20 → not HOLD (at least runs)"""
    s = HighLowReversalStrategy()
    sig = s.generate(_make_df(n=19))
    assert sig.action == Action.HOLD
    sig2 = s.generate(_make_df(n=20))
    assert sig2.strategy == "high_low_reversal"


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_medium_confidence():
    """position in (0.1, 0.2) AND position > pos_ma → BUY MEDIUM"""
    s = HighLowReversalStrategy()
    df = _buy_df(pos_val=0.15)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_buy_high_confidence():
    """position < 0.1 AND position > pos_ma → BUY HIGH"""
    s = HighLowReversalStrategy()
    df = _buy_df(pos_val=0.05)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_signal_has_correct_strategy():
    s = HighLowReversalStrategy()
    sig = s.generate(_buy_df(pos_val=0.05))
    assert sig.strategy == "high_low_reversal"


def test_buy_entry_price_is_close():
    s = HighLowReversalStrategy()
    df = _buy_df(pos_val=0.05)
    sig = s.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert abs(sig.entry_price - expected_close) < 1e-6


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_medium_confidence():
    """position in (0.8, 0.9) AND position < pos_ma → SELL MEDIUM"""
    s = HighLowReversalStrategy()
    df = _sell_df(pos_val=0.85)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


def test_sell_high_confidence():
    """position > 0.9 AND position < pos_ma → SELL HIGH"""
    s = HighLowReversalStrategy()
    df = _sell_df(pos_val=0.95)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_signal_has_correct_strategy():
    s = HighLowReversalStrategy()
    sig = s.generate(_sell_df(pos_val=0.95))
    assert sig.strategy == "high_low_reversal"


def test_sell_entry_price_is_close():
    s = HighLowReversalStrategy()
    df = _sell_df(pos_val=0.95)
    sig = s.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert abs(sig.entry_price - expected_close) < 1e-6


# ── HOLD 시그널 ───────────────────────────────────────────────────────────────

def test_hold_when_middle_position():
    """position around 0.5 → HOLD"""
    s = HighLowReversalStrategy()
    df = _make_df(n=25)  # close=100, high=105, low=95 → position=0.5
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_buy_condition_not_met_position_below_pma():
    """position < 0.2 but position < pos_ma → no BUY"""
    s = HighLowReversalStrategy()
    n = 25
    high = [105.0] * n
    low  = [95.0]  * n
    # Prior: position low (so pos_ma also low), then current even lower - but pos_ma
    # must be higher than current for BUY. Let's make all positions=0.15 so pos_ma=0.15
    # and current pos = 0.12 < pos_ma=0.15 → condition pos > pos_ma fails
    close = [95.0 + 0.15 * 10.0] * n  # all position=0.15
    close[-2] = 95.0 + 0.12 * 10.0    # position=0.12 < pos_ma~0.15 → no BUY
    df = _make_df(n=n, close_values=close, high_values=high, low_values=low)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_sell_condition_not_met_position_above_pma():
    """position > 0.8 but position > pos_ma → no SELL"""
    s = HighLowReversalStrategy()
    n = 25
    high = [105.0] * n
    low  = [95.0]  * n
    # All positions = 0.85, current = 0.88 > pos_ma~0.85 → no SELL
    close = [95.0 + 0.85 * 10.0] * n
    close[-2] = 95.0 + 0.88 * 10.0
    df = _make_df(n=n, close_values=close, high_values=high, low_values=low)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_returns_low_confidence():
    s = HighLowReversalStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW
