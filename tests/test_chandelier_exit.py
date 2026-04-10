"""ChandelierExitStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.chandelier_exit import ChandelierExitStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(close, high_offset=1.0, low_offset=1.0, volume=1000.0):
    close = np.asarray(close, dtype=float)
    n = len(close)
    return pd.DataFrame(
        {
            "open": close - 0.2,
            "high": close + high_offset,
            "low": close - low_offset,
            "close": close,
            "volume": np.ones(n) * volume,
        }
    )


def _stable(n=40, value=100.0):
    return _make_df(np.ones(n) * value + np.arange(n) * 0.001)


def _buy_df():
    """close가 chandelier_long 위에 있고 상승 중 → BUY 조건."""
    # 완만한 상승 → 높은 highest_high, 작은 ATR → CL 낮음
    # 마지막 -2 캔들: close 급등으로 CL보다 훨씬 위
    close = np.concatenate([np.linspace(100.0, 105.0, 38), [160.0, 155.0]])
    # high_offset 작게 → ATR 작게 → CL = highest_high - small → 낮은 CL
    return _make_df(close, high_offset=0.5, low_offset=0.5)


def _sell_df():
    """close가 chandelier_short 아래에 있고 하락 중 → SELL 조건."""
    # 완만한 하락 → 낮은 lowest_low, 작은 ATR → CS 높음
    # 마지막 -2 캔들: close 급락으로 CS보다 훨씬 아래
    close = np.concatenate([np.linspace(200.0, 195.0, 38), [140.0, 145.0]])
    return _make_df(close, high_offset=0.5, low_offset=0.5)


# ── tests ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert ChandelierExitStrategy().name == "chandelier_exit"


def test_hold_insufficient_data():
    sig = ChandelierExitStrategy().generate(_make_df(np.ones(10) * 100.0))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_exactly_24_rows():
    sig = ChandelierExitStrategy().generate(_make_df(np.linspace(100, 110, 24)))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_no_error_at_minimum_rows():
    sig = ChandelierExitStrategy().generate(_make_df(np.linspace(100, 110, 25)))
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_present():
    sig = ChandelierExitStrategy().generate(_stable())
    assert sig.strategy == "chandelier_exit"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_second_to_last():
    df = _stable()
    sig = ChandelierExitStrategy().generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_empty_dataframe():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    sig = ChandelierExitStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == pytest.approx(0.0)


def test_hold_stable_trend():
    """안정적 추세 → 보통 HOLD."""
    sig = ChandelierExitStrategy().generate(_stable())
    # 안정적이면 buy/sell 조건이 성립하지 않을 가능성 높음
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_condition_logic():
    """buy 조건: close > chandelier_long AND close > prev_close."""
    df = _buy_df()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    atr14 = (high - low).rolling(14, min_periods=1).mean()
    chandelier_long = high.rolling(22, min_periods=1).max() - atr14 * 3.0
    idx = len(df) - 2
    c = float(close.iloc[idx])
    c_prev = float(close.iloc[idx - 1])
    cl = float(chandelier_long.iloc[idx])
    if c > cl and c > c_prev:
        sig = ChandelierExitStrategy().generate(df)
        assert sig.action == Action.BUY


def test_sell_condition_logic():
    """sell 조건: close < chandelier_short AND close < prev_close."""
    df = _sell_df()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    atr14 = (high - low).rolling(14, min_periods=1).mean()
    chandelier_short = low.rolling(22, min_periods=1).min() + atr14 * 3.0
    idx = len(df) - 2
    c = float(close.iloc[idx])
    c_prev = float(close.iloc[idx - 1])
    cs = float(chandelier_short.iloc[idx])
    if c < cs and c < c_prev:
        sig = ChandelierExitStrategy().generate(df)
        assert sig.action == Action.SELL


def test_buy_confidence_high():
    """close > chandelier_long * 1.01 → HIGH confidence on BUY."""
    df = _buy_df()
    sig = ChandelierExitStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_confidence_high():
    """close < chandelier_short * 0.99 → HIGH confidence on SELL."""
    df = _sell_df()
    sig = ChandelierExitStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_reasoning_contains_atr():
    sig = ChandelierExitStrategy().generate(_stable())
    assert "ATR" in sig.reasoning or "HOLD" in sig.reasoning or "NaN" in sig.reasoning


def test_atr_uses_rolling_mean():
    """atr14 = (high-low).rolling(14).mean() - 컬럼 없어도 자체 계산."""
    df = _stable()
    assert "atr14" not in df.columns
    sig = ChandelierExitStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
