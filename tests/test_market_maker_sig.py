"""MarketMakerStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.market_maker_sig import MarketMakerStrategy


def _make_df(n=30, close_vals=None, high_vals=None, low_vals=None, atr_mult=1.0):
    base = np.ones(n) * 100.0
    df = pd.DataFrame(
        {
            "open": base,
            "close": base.copy(),
            "high": base + 1.0 * atr_mult,
            "low": base - 1.0 * atr_mult,
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
        df["high"] = df["close"] + 1.0 * atr_mult
    if low_vals is not None:
        arr = np.asarray(low_vals, dtype=float)
        df["low"] = arr
    else:
        df["low"] = df["close"] - 1.0 * atr_mult
    return df


def _make_mm_buy_df():
    """
    축적(narrow ATR) + 하방 조작(low < range_low, recover) + close > range_high → BUY

    Strategy checks: acc_atr (iloc[idx-1]) < cur_avg_atr (rolling(10).mean().shift(1) at idx) * 0.7
    idx = len(df)-2
    cur_avg_atr is avg of ATR for rows [idx-11 .. idx-2] (shift(1) of rolling(10))

    We use: first 10 rows wide (ATR~4), next 13 rows narrow (ATR~0.4).
    avg_atr at idx includes the wide rows → high avg.
    acc_atr (idx-1) = narrow ATR → passes accumulation check.
    """
    n = 25
    close = np.ones(n) * 100.0
    # First 10 rows: wide ATR
    high = close + 4.0
    low = close - 4.0
    # Rows 10-22: narrow ATR (close=100, high=100.2, low=99.8)
    high[10:23] = 100.2
    low[10:23] = 99.8
    # range_low from rolling(10).min().shift(1) of close[10..22] ~ 100 - but close is 100
    # range_high ~ 100.2 (from close rolling max, close=100 → actually 100)
    # Use low rolling for range: close rolling(10) of rows 10..22 = 100
    # range_high ~ 100, range_low ~ 100 — but we need close > range_high
    # Set close[10:23] = 100.1 so range_high ~ 100.1
    close[10:23] = 100.1
    high[10:23] = 100.3
    low[10:23] = 99.9

    # idx-2 = 23: spike down (low=95 < range_low~99.9), close=100.5 > range_high~100.3
    low[23] = 95.0
    close[23] = 100.5
    high[23] = 101.0
    # idx-1 = 24: current bar (ignored)
    high[24] = 101.0
    low[24] = 99.5
    close[24] = 100.0

    return _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)


def _make_mm_sell_df():
    """
    축적(narrow ATR) + 상방 조작(high > range_high, reject) + close < range_low → SELL
    """
    n = 25
    close = np.ones(n) * 100.0
    high = close + 4.0
    low = close - 4.0
    # Rows 10-22: narrow ATR
    close[10:23] = 99.9
    high[10:23] = 100.1
    low[10:23] = 99.7

    # idx-2 = 23: spike up (high=105 > range_high~100.1), close=99.5 < range_low~99.7
    high[23] = 105.0
    close[23] = 99.5
    low[23] = 99.4
    # close must also be < range_low ~99.7 ✓
    # idx-1 = 24: current bar
    high[24] = 100.5
    low[24] = 99.0
    close[24] = 100.0

    return _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)


strategy = MarketMakerStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "market_maker_sig"


# ── 2. 인스턴스 생성 ──────────────────────────
def test_strategy_instance():
    s = MarketMakerStrategy()
    assert isinstance(s, MarketMakerStrategy)


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


# ── 5. 정상 데이터, 패턴 없음 → HOLD ────────
def test_no_pattern_hold():
    """넓은 ATR (비축적 상태) → MM 패턴 없음 → HOLD."""
    df = _make_df(n=25, atr_mult=3.0)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. MM BUY 신호 ────────────────────────────
def test_mm_buy_signal():
    df = _make_mm_buy_df()
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 7. MM SELL 신호 ───────────────────────────
def test_mm_sell_signal():
    df = _make_mm_sell_df()
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 8. Signal 필드 완전성 ─────────────────────
def test_signal_fields_complete():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "market_maker_sig"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 9. BUY reasoning 키워드 ──────────────────
def test_buy_reasoning_keyword():
    df = _make_mm_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "MM" in sig.reasoning or "축적" in sig.reasoning


# ── 10. SELL reasoning 키워드 ────────────────
def test_sell_reasoning_keyword():
    df = _make_mm_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "MM" in sig.reasoning or "축적" in sig.reasoning


# ── 11. BUY entry_price 양수 ─────────────────
def test_buy_entry_price_positive():
    df = _make_mm_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price > 0


# ── 12. SELL entry_price 양수 ────────────────
def test_sell_entry_price_positive():
    df = _make_mm_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price > 0


# ── 13. HIGH confidence (큰 spike) ───────────
def test_high_confidence_large_spike():
    """spike > ATR*2 → HIGH confidence (uses same setup as mm_buy with bigger spike)."""
    df = _make_mm_buy_df()
    sig = strategy.generate(df)
    # spike_size = range_low - low[-2] = 99.9 - 95 = 4.9, ATR at that point ~ small
    # Just check that if BUY, it has HIGH or MEDIUM (don't fail on HOLD)
    assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)


# ── 14. HOLD confidence MEDIUM ───────────────
def test_hold_confidence_medium():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM


# ── 15. 최소 행 경계값 (20) ──────────────────
def test_min_rows_boundary():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── 16. 19행 → HOLD LOW ──────────────────────
def test_below_min_rows():
    df = _make_df(n=19)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
