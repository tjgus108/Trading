"""Tests for MarubozuStrategy."""

import pandas as pd
import pytest

from src.strategy.marubozu import MarubozuStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5, atr14=1.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": atr14}


def _base_rows(n: int = 22, atr14: float = 1.0) -> list:
    return [_base_row(atr14=atr14) for _ in range(n)]


def _bullish_maru(atr14: float = 1.0, big: bool = False) -> dict:
    """
    body = 0.8 * atr14 (> 0.7), or 1.1 * atr14 (> 1.0 for HIGH)
    low = open - 0.03 * atr14 (< tol=0.05*atr14 → no lower wick)
    high = close + 0.03 * atr14 (< tol → no upper wick)
    """
    factor = 1.1 if big else 0.8
    body = factor * atr14
    o = 100.0
    c = o + body
    l = o - 0.03 * atr14
    h = c + 0.03 * atr14
    return {"open": o, "high": h, "low": l, "close": c, "volume": 1000, "atr14": atr14}


def _bearish_maru(atr14: float = 1.0, big: bool = False) -> dict:
    """
    body = 0.8 * atr14 (> 0.7), or 1.1 * atr14 (> 1.0 for HIGH)
    high = open + 0.03 * atr14 (< tol)
    low = close - 0.03 * atr14 (< tol)
    """
    factor = 1.1 if big else 0.8
    body = factor * atr14
    o = 100.0
    c = o - body
    h = o + 0.03 * atr14
    l = c - 0.03 * atr14
    return {"open": o, "high": h, "low": l, "close": c, "volume": 1000, "atr14": atr14}


# ── 1. name ──────────────────────────────────────────────────────────────────

def test_name():
    assert MarubozuStrategy.name == "marubozu"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = MarubozuStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. BUY: Bullish Marubozu ─────────────────────────────────────────────────

def test_buy_bullish_marubozu():
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bullish_maru(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "marubozu"


# ── 4. SELL: Bearish Marubozu ────────────────────────────────────────────────

def test_sell_bearish_marubozu():
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bearish_maru(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "marubozu"


# ── 5. body <= ATR*0.7 → HOLD ────────────────────────────────────────────────

def test_small_body_hold():
    """body < ATR*0.7 → Marubozu 아님 → HOLD"""
    strategy = MarubozuStrategy()
    rows = _base_rows(22, atr14=1.0)
    # body=0.5 < 0.7
    rows[20] = {"open": 100.0, "high": 100.6, "low": 99.9, "close": 100.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. 아래꼬리 너무 길면 Bullish Marubozu 아님 → HOLD ──────────────────────

def test_bullish_lower_wick_too_large_hold():
    """low가 너무 낮아서 아래꼬리 허용 초과 → HOLD"""
    strategy = MarubozuStrategy()
    rows = _base_rows(22, atr14=1.0)
    # body=1.0 > 0.7, tol=0.05
    # l = open - 0.1 > tol → lower wick 과다
    rows[20] = {"open": 100.0, "high": 101.03, "low": 99.8, "close": 101.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. 위꼬리 너무 길면 Bearish Marubozu 아님 → HOLD ────────────────────────

def test_bearish_upper_wick_too_large_hold():
    """high가 너무 높아서 위꼬리 허용 초과 → HOLD"""
    strategy = MarubozuStrategy()
    rows = _base_rows(22, atr14=1.0)
    # body=1.0, tol=0.05, high = open + 0.2 > tol → 위꼬리 과다
    rows[20] = {"open": 100.0, "high": 100.2, "low": 98.97, "close": 99.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 8. confidence HIGH: body > ATR*1.0 ──────────────────────────────────────

def test_high_confidence_bullish():
    """body > ATR*1.0 → HIGH"""
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bullish_maru(atr14=1.0, big=True)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 9. confidence MEDIUM: ATR*0.7 < body <= ATR*1.0 ────────────────────────

def test_medium_confidence_bullish():
    """body = 0.8 * atr → MEDIUM"""
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bullish_maru(atr14=1.0, big=False)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 10. confidence HIGH: body > ATR*1.0 (Bearish) ───────────────────────────

def test_high_confidence_bearish():
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bearish_maru(atr14=1.0, big=True)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 11. Signal 필드 검증 ─────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = MarubozuStrategy()
    df = _make_df(_base_rows(22))
    sig = strategy.generate(df)
    for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation", "bull_case", "bear_case"):
        assert hasattr(sig, field)
    assert sig.strategy == "marubozu"


# ── 12. entry_price == close ─────────────────────────────────────────────────

def test_entry_price_equals_close():
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    maru = _bullish_maru(atr14=1.0)
    rows[20] = maru
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.entry_price == pytest.approx(maru["close"])


# ── 13. invalidation 필드: BUY → low 포함 ────────────────────────────────────

def test_buy_invalidation_contains_low():
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bullish_maru(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "low" in sig.invalidation.lower() or str(round(rows[20]["low"], 2)) in sig.invalidation


# ── 14. invalidation 필드: SELL → high 포함 ──────────────────────────────────

def test_sell_invalidation_contains_high():
    strategy = MarubozuStrategy()
    rows = _base_rows(22)
    rows[20] = _bearish_maru(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "high" in sig.invalidation.lower() or str(round(rows[20]["high"], 2)) in sig.invalidation
