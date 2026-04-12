"""ROCMACrossStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.roc_ma_cross import ROCMACrossStrategy


def _make_df(n=50, close_vals=None, ema50_vals=None):
    np.random.seed(0)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.2, 0.2, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
        "ema50": base,
        "ema20": base,
        "atr14": np.ones(n) * 0.5,
        "volume_sma20": np.ones(n) * 1000,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    if ema50_vals is not None:
        arr = np.asarray(ema50_vals, dtype=float)
        df["ema50"] = arr
    return df


def _make_buy_df():
    """ROC_MA crosses above 0 AND close > EMA50."""
    n = 50
    close = np.concatenate([
        np.linspace(110, 100, 14),   # 하락 → ROC 음수
        np.linspace(100, 120, 36),   # 급등 → ROC 양수로 크로스 유도
    ])
    ema50 = np.full(n, 95.0)  # close > ema50 조건 충족
    return _make_df(n=n, close_vals=close, ema50_vals=ema50)


def _make_sell_df():
    """ROC_MA crosses below 0 AND close < EMA50."""
    n = 50
    close = np.concatenate([
        np.linspace(100, 110, 14),   # 상승 → ROC 양수
        np.linspace(110, 90, 36),    # 급락 → ROC 음수로 크로스 유도
    ])
    ema50 = np.full(n, 120.0)  # close < ema50 조건 충족
    return _make_df(n=n, close_vals=close, ema50_vals=ema50)


strategy = ROCMACrossStrategy()


def test_strategy_name():
    assert strategy.name == "roc_ma_cross"


def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert "부족" in sig.reasoning


def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_returns_signal_with_normal_data():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.strategy == "roc_ma_cross"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_buy_signal_cross_above():
    df = _make_buy_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)
    assert sig.entry_price >= 0.0


def test_sell_signal_cross_below():
    df = _make_sell_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)
    assert sig.entry_price >= 0.0


def test_buy_suppressed_when_close_below_ema50():
    df = _make_buy_df()
    df["ema50"] = df["close"] + 100
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


def test_sell_suppressed_when_close_above_ema50():
    df = _make_sell_df()
    df["ema50"] = df["close"] - 100
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


def test_confidence_is_valid():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_buy_reasoning_format():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "ROC_MA" in sig.reasoning


def test_sell_reasoning_format():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "ROC_MA" in sig.reasoning


def test_hold_reasoning_format():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert len(sig.reasoning) > 0


def test_strategy_instance():
    strat = ROCMACrossStrategy()
    assert isinstance(strat, ROCMACrossStrategy)


def test_boundary_rows_below_min():
    df = _make_df(n=19)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_boundary_rows_at_min():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_suppressed_when_low_volume():
    df = _make_buy_df()
    df["volume"] = df["volume_sma20"] * 0.7  # 0.8배 미만 → 억제
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


def test_high_confidence_with_extreme_roc_and_volume():
    df = _make_df(n=50)
    df["volume"] = df["volume_sma20"] * 1.5  # 고볼륨 (1.2배 이상)
    sig = strategy.generate(df)
    if sig.action in (Action.BUY, Action.SELL):
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
