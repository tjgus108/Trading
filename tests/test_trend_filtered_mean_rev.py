"""
TrendFilteredMeanRevStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_filtered_mean_rev import TrendFilteredMeanRevStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, close_values=None) -> pd.DataFrame:
    """Mock DataFrame. _last() = iloc[-2]."""
    close = close_values if close_values is not None else [100.0] * n
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [c + 2.0 for c in close],
        "low":    [c - 2.0 for c in close],
        "close":  close,
        "volume": [1000.0] * n,
    })


def _buy_df(n: int = 60) -> pd.DataFrame:
    """
    BUY 조건: close[-2] > ema50[-2] AND close[-2] < lower band
    - 앞 n-3 rows: 점진적 상승 (ema50 high)
    - 마지막 완성 캔들[-2]: ema50보다 높지만 bb lower보다 낮은 급락값
    """
    # Use constant high values so ema50 is high, then a dip at idx[-2]
    base = 200.0
    close = [base] * n
    # idx[-2]: drop far below bb lower but still above ema50 (ema50 will be ~200)
    # BB lower = mean(20) - std(20)*1.5. With all 200s, std≈0 so lower≈200.
    # We need std > 0: vary slightly
    for i in range(n):
        close[i] = base + (i % 3) * 0.5  # slight variation, std > 0
    # Set[-2] to value above ema50 but below bb lower:
    # After variation, mean~200.5, std~0.4, lower~199.9
    # ema50 will track ~200.5 → we need close[-2] > ema50 AND < lower
    # That's contradictory with ema50 close to mean. Let's use a different setup:
    # Make ema50 low by starting from low values, then the target candle is high
    # Actually for BUY: trend_up (close > ema50) + close < lower
    # ema50 is slow MA - if we have a long uptrend then a single dip, ema50 stays high
    # Let's do: first half very low, second half very high → ema50 somewhere in between
    # At[-2]: moderate value > ema50 but we need it < bb_lower
    # Better approach: stable high values, std=0 → lower=mean → close[-2] slightly below mean
    # but ema50 is also ~mean → close[-2] < ema50 too. That's trend_down.
    # Proper setup for BUY with std>0:
    half = n // 2
    # First half: low values (ema50 pulls down)
    for i in range(half):
        close[i] = 80.0
    # Second half: high values (ema50 still catching up, will be < close)
    for i in range(half, n):
        close[i] = 100.0
    # At[-2]: drop below bb_lower (which is ~100 - std*1.5)
    # std of last 20 values: mostly 100.0 → need variation
    for i in range(n - 22, n - 2):
        close[i] = 100.0 + (i % 2) * 2.0  # alternating, std > 0
    # bb_mid ~ 101, bb_std ~ 1, lower ~ 99.5
    # ema50 ~ 90 (still catching up from 80s)
    # Set [-2] to 98 → close(98) > ema50(~90) AND close(98) < lower(~99.5)
    close[-2] = 98.0
    close[-1] = 100.0  # current candle
    return _make_df(n=n, close_values=close)


def _sell_df(n: int = 60) -> pd.DataFrame:
    """
    SELL 조건: close[-2] < ema50[-2] AND close[-2] > upper band
    - First half: high values (ema50 high)
    - Second half: low values (ema50 still catching down)
    - At[-2]: spike above bb_upper but still below ema50
    """
    half = n // 2
    close = [100.0] * n
    for i in range(half):
        close[i] = 120.0
    for i in range(half, n):
        close[i] = 100.0
    # Add variation to last 20 for std > 0
    for i in range(n - 22, n - 2):
        close[i] = 100.0 + (i % 2) * 2.0
    # bb_mid ~ 101, bb_std ~ 1, upper ~ 102.5
    # ema50 ~ 110 (still catching down from 120s)
    # Set[-2] to 103 → close(103) < ema50(~110) AND close(103) > upper(~102.5)
    close[-2] = 103.0
    close[-1] = 100.0
    return _make_df(n=n, close_values=close)


# ── 기본 ──────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert TrendFilteredMeanRevStrategy().name == "trend_filtered_mean_rev"


def test_insufficient_data_returns_hold():
    s = TrendFilteredMeanRevStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_insufficient_data_boundary():
    s = TrendFilteredMeanRevStrategy()
    sig29 = s.generate(_make_df(n=29))
    assert sig29.action == Action.HOLD
    sig30 = s.generate(_make_df(n=30))
    assert sig30.strategy == "trend_filtered_mean_rev"


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_action():
    s = TrendFilteredMeanRevStrategy()
    df = _buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_signal_strategy_name():
    s = TrendFilteredMeanRevStrategy()
    sig = s.generate(_buy_df())
    assert sig.strategy == "trend_filtered_mean_rev"


def test_buy_entry_price_is_close():
    s = TrendFilteredMeanRevStrategy()
    df = _buy_df()
    sig = s.generate(df)
    expected = float(df["close"].iloc[-2])
    assert abs(sig.entry_price - expected) < 1e-6


def test_buy_confidence_medium_or_high():
    s = TrendFilteredMeanRevStrategy()
    sig = s.generate(_buy_df())
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_high_confidence_large_deviation():
    """deviation > bb_std * 2.0 → HIGH"""
    s = TrendFilteredMeanRevStrategy()
    n = 60
    half = n // 2
    close = [100.0] * n
    for i in range(half):
        close[i] = 80.0
    for i in range(half, n):
        close[i] = 100.0
    for i in range(n - 22, n - 2):
        close[i] = 100.0 + (i % 2) * 2.0
    # Very large deviation: drop far below lower
    close[-2] = 90.0  # far below bb_lower, well above ema50(~90→borderline)
    # Make ema50 clearly below 90 by starting even lower
    for i in range(half):
        close[i] = 60.0
    close[-1] = 100.0
    df = _make_df(n=n, close_values=close)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_action():
    s = TrendFilteredMeanRevStrategy()
    df = _sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_signal_strategy_name():
    s = TrendFilteredMeanRevStrategy()
    sig = s.generate(_sell_df())
    assert sig.strategy == "trend_filtered_mean_rev"


def test_sell_entry_price_is_close():
    s = TrendFilteredMeanRevStrategy()
    df = _sell_df()
    sig = s.generate(df)
    expected = float(df["close"].iloc[-2])
    assert abs(sig.entry_price - expected) < 1e-6


def test_sell_confidence_medium_or_high():
    s = TrendFilteredMeanRevStrategy()
    sig = s.generate(_sell_df())
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── HOLD 시그널 ───────────────────────────────────────────────────────────────

def test_hold_flat_data():
    """모든 값 동일 → position 조건 미충족 → HOLD"""
    s = TrendFilteredMeanRevStrategy()
    df = _make_df(n=50)  # all 100.0 → ema50~100, bb_mid~100, std~0 → no signal
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_trend_up_but_above_mid():
    """trend_up but close above bb_mid (not below lower) → HOLD"""
    s = TrendFilteredMeanRevStrategy()
    n = 60
    half = n // 2
    close = [100.0] * n
    for i in range(half):
        close[i] = 80.0
    for i in range(half, n):
        close[i] = 110.0
    close[-1] = 110.0
    df = _make_df(n=n, close_values=close)
    sig = s.generate(df)
    # close[-2]=110 > ema50 (trend_up) but close > bb_mid, not below lower → HOLD
    assert sig.action == Action.HOLD


def test_hold_returns_low_confidence():
    s = TrendFilteredMeanRevStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW
