"""LiquiditySweepStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.liquidity_sweep import LiquiditySweepStrategy


def _make_df(n=30, close_vals=None, high_vals=None, low_vals=None):
    np.random.seed(42)
    base = np.ones(n) * 100.0
    df = pd.DataFrame(
        {
            "open": base,
            "close": base.copy(),
            "high": base + 1.0,
            "low": base - 1.0,
            "volume": np.ones(n) * 1000,
        }
    )
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[: len(arr)].copy()
        df["close"] = arr
    if high_vals is not None:
        arr = np.asarray(high_vals, dtype=float)
        df["high"] = arr
    else:
        df["high"] = df["close"] + 1.0
    if low_vals is not None:
        arr = np.asarray(low_vals, dtype=float)
        df["low"] = arr
    else:
        df["low"] = df["close"] - 1.0
    return df


def _make_bullish_sweep_df():
    """
    마지막 완성봉: low < recent_low AND close > recent_low → BUY
    recent_low = low.rolling(10).min().shift(1)
    """
    n = 20
    close = np.ones(n) * 100.0
    high = close + 1.0
    low = close - 1.0  # recent_low ~ 99 (rolling min of low)

    # idx -2 (봉 18): low=96 < 99, close=100.5 > 99
    low[-2] = 96.0
    close[-2] = 100.5
    high[-2] = 101.5
    # idx -1: current bar (무시)
    return _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)


def _make_bearish_sweep_df():
    """
    마지막 완성봉: high > recent_high AND close < recent_high → SELL
    recent_high = high.rolling(10).max().shift(1)
    low must NOT also trigger bullish sweep.
    """
    n = 20
    close = np.ones(n) * 100.0
    high = close + 1.0  # recent_high ~ 101
    low = close - 1.0   # recent_low ~ 99

    # idx -2: high=104 > 101, close=99.5 < 101
    # low[-2] must stay >= recent_low(99) to avoid bullish sweep
    high[-2] = 104.0
    close[-2] = 99.5
    low[-2] = 99.2   # above recent_low=99, so bullish sweep won't fire
    return _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)


strategy = LiquiditySweepStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "liquidity_sweep"


# ── 2. 인스턴스 생성 ──────────────────────────
def test_strategy_instance():
    s = LiquiditySweepStrategy()
    assert isinstance(s, LiquiditySweepStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert "부족" in sig.reasoning


# ── 4. None 입력 → HOLD ──────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 5. 정상 데이터, sweep 없음 → HOLD ────────
def test_no_sweep_hold():
    """완전 평탄: 고/저점 돌파 없음 → HOLD."""
    n = 20
    close = np.ones(n) * 100.0
    high = close + 0.5   # recent_high ~ 100.5, high == recent_high
    low = close - 0.5    # recent_low ~ 99.5, low == recent_low
    df = _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Bullish sweep → BUY ────────────────────
def test_bullish_sweep_buy():
    df = _make_bullish_sweep_df()
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 7. Bearish sweep → SELL ───────────────────
def test_bearish_sweep_sell():
    df = _make_bearish_sweep_df()
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 8. Signal 필드 완전성 ─────────────────────
def test_signal_fields_complete():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "liquidity_sweep"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 9. BUY reasoning 키워드 ──────────────────
def test_buy_reasoning_keyword():
    df = _make_bullish_sweep_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "sweep" in sig.reasoning.lower() or "Bullish" in sig.reasoning


# ── 10. SELL reasoning 키워드 ────────────────
def test_sell_reasoning_keyword():
    df = _make_bearish_sweep_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "sweep" in sig.reasoning.lower() or "Bearish" in sig.reasoning


# ── 11. BUY entry_price 양수 ─────────────────
def test_buy_entry_price_positive():
    df = _make_bullish_sweep_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price > 0


# ── 12. SELL entry_price 양수 ────────────────
def test_sell_entry_price_positive():
    df = _make_bearish_sweep_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price > 0


# ── 13. HIGH confidence (큰 스윕) ────────────
def test_high_confidence_large_sweep():
    """스윕 크기 > ATR*0.5 → HIGH confidence."""
    n = 20
    close = np.ones(n) * 100.0
    high = close + 0.3
    low = close - 0.3  # ATR ~0.6, recent_low ~99.7

    # 큰 sweep: low=94 (sweep=5.7 > 0.6*0.5=0.3), close=100.5 > 99.7
    low[-2] = 94.0
    close[-2] = 100.5
    high[-2] = 101.0
    df = _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 14. HOLD confidence MEDIUM ───────────────
def test_hold_confidence_medium():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM


# ── 15. 최소 행 경계값 (15) ──────────────────
def test_min_rows_boundary():
    df = _make_df(n=15)
    sig = strategy.generate(df)
    # 15행이면 통과 (HOLD or signal), 크래시 없음
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── 16. 14행 → HOLD LOW ──────────────────────
def test_below_min_rows():
    df = _make_df(n=14)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
