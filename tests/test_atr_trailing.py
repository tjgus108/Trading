"""ATRTrailingStrategy 단위 테스트 (12개+)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.atr_trailing import ATRTrailingStrategy

strategy = ATRTrailingStrategy()


def _make_df(n=30, scenario="hold"):
    """
    scenario:
      "buy_medium"  → EMA50 상승 + close > EMA50 + trail rising, close < EMA50*1.01 → MEDIUM
      "buy_high"    → EMA50 상승 + close > EMA50*1.01 + trail rising → HIGH
      "sell_medium" → EMA50 하락 + close < EMA50 + trail falling, close > EMA50*0.99 → MEDIUM
      "sell_high"   → EMA50 하락 + close < EMA50*0.99 + trail falling → HIGH
      "no_trend"    → EMA50 flat → HOLD
      "hold"        → HOLD (close 반대쪽)
    """
    base = 100.0
    atr_val = 1.0

    closes = np.full(n, base, dtype=float)
    ema50 = np.full(n, base, dtype=float)
    atr14 = np.full(n, atr_val, dtype=float)

    idx = n - 2

    if scenario == "buy_medium":
        # EMA50 상승: prev5 < now
        ema50[idx - 5] = base - 0.5
        ema50[idx] = base            # now > prev5
        # close > EMA50, but < EMA50*1.01 → MEDIUM
        closes[idx] = base + 0.5    # 0.5% above, not 1%
        # trail_bull = close - atr*2 → rising: need close[idx] - atr > close[idx-1] - atr
        closes[idx - 1] = base + 0.3  # trail_bull[idx-1] = 100.3 - 2 = 98.3
        # trail_bull[idx] = 100.5 - 2 = 98.5 > 98.3 → rising

    elif scenario == "buy_high":
        ema50[idx - 5] = base - 1.0
        ema50[idx] = base
        closes[idx] = base + 1.5    # > EMA50 * 1.01 = 101.0 → HIGH
        closes[idx - 1] = base + 0.5

    elif scenario == "sell_medium":
        ema50[idx - 5] = base + 0.5
        ema50[idx] = base            # now < prev5
        closes[idx] = base - 0.5    # < EMA50, but > EMA50*0.99 → MEDIUM
        closes[idx - 1] = base - 0.3
        # trail_bear = close + atr*2
        # trail_bear[idx] = 99.5 + 2 = 101.5
        # trail_bear[idx-1] = 99.7 + 2 = 101.7
        # 101.5 < 101.7 → falling ✓

    elif scenario == "sell_high":
        ema50[idx - 5] = base + 1.0
        ema50[idx] = base
        closes[idx] = base - 1.5    # < EMA50 * 0.99 = 99.0 → HIGH
        closes[idx - 1] = base - 0.5

    elif scenario == "no_trend":
        # EMA50 flat (no slope) → no signal
        ema50[:] = base
        closes[idx] = base + 2.0

    elif scenario == "hold":
        # EMA50 상승이지만 close < EMA50 → no BUY
        ema50[idx - 5] = base - 1.0
        ema50[idx] = base
        closes[idx] = base - 0.5

    volumes = np.ones(n) * 1000.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": volumes,
        "ema50": ema50,
        "atr14": atr14,
    })
    return df


# ── BUY 케이스 ────────────────────────────────────────────────

def test_buy_medium_action():
    sig = strategy.generate(_make_df(scenario="buy_medium"))
    assert sig.action == Action.BUY


def test_buy_medium_confidence():
    sig = strategy.generate(_make_df(scenario="buy_medium"))
    assert sig.confidence == Confidence.MEDIUM


def test_buy_high_action():
    sig = strategy.generate(_make_df(scenario="buy_high"))
    assert sig.action == Action.BUY


def test_buy_high_confidence():
    sig = strategy.generate(_make_df(scenario="buy_high"))
    assert sig.confidence == Confidence.HIGH


# ── SELL 케이스 ────────────────────────────────────────────────

def test_sell_medium_action():
    sig = strategy.generate(_make_df(scenario="sell_medium"))
    assert sig.action == Action.SELL


def test_sell_medium_confidence():
    sig = strategy.generate(_make_df(scenario="sell_medium"))
    assert sig.confidence == Confidence.MEDIUM


def test_sell_high_action():
    sig = strategy.generate(_make_df(scenario="sell_high"))
    assert sig.action == Action.SELL


def test_sell_high_confidence():
    sig = strategy.generate(_make_df(scenario="sell_high"))
    assert sig.confidence == Confidence.HIGH


# ── HOLD 케이스 ────────────────────────────────────────────────

def test_no_trend_hold():
    sig = strategy.generate(_make_df(scenario="no_trend"))
    assert sig.action == Action.HOLD


def test_hold_scenario():
    sig = strategy.generate(_make_df(scenario="hold"))
    assert sig.action == Action.HOLD


# ── 데이터 부족 ────────────────────────────────────────────────

def test_insufficient_data_hold():
    """20행 미만 → HOLD."""
    df = _make_df(n=15, scenario="hold")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_low_confidence():
    df = _make_df(n=10, scenario="hold")
    sig = strategy.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ────────────────────────────────────────────

def test_signal_strategy_name():
    sig = strategy.generate(_make_df(scenario="hold"))
    assert sig.strategy == "atr_trailing"


def test_buy_reasoning_mentions_ema50():
    sig = strategy.generate(_make_df(scenario="buy_high"))
    assert "EMA50" in sig.reasoning


def test_sell_reasoning_mentions_trail_bear():
    sig = strategy.generate(_make_df(scenario="sell_high"))
    assert "trail_bear" in sig.reasoning


def test_buy_invalidation_mentions_trail_stop():
    sig = strategy.generate(_make_df(scenario="buy_medium"))
    assert "trailing stop" in sig.invalidation
