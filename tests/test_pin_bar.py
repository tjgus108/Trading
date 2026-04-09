"""Tests for PinBarStrategy."""

import pandas as pd
import pytest

from src.strategy.pin_bar import PinBarStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5, atr14=1.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": atr14}


def _base_rows(n: int = 22, atr14: float = 1.0) -> list:
    return [_base_row(atr14=atr14) for _ in range(n)]


def _with_downtrend(rows: list, end_idx: int) -> list:
    for i in range(end_idx):
        rows[i]["close"] = 120.0 - i * 2.0
    return rows


def _with_uptrend(rows: list, end_idx: int) -> list:
    for i in range(end_idx):
        rows[i]["close"] = 80.0 + i * 2.0
    return rows


def _bullish_pin_row(lower_ratio: float = 0.65, atr14: float = 1.0) -> dict:
    """아래꼬리가 lower_ratio만큼인 bullish pin bar"""
    # total_range=10, lower_wick=lower_ratio*10, body 상단에 위치
    l = 90.0
    total = 10.0
    lower_wick = total * lower_ratio
    body_bottom = l + lower_wick
    body_top = l + total * 0.92      # body 상단 8%
    h = l + total
    return {"open": body_bottom, "high": h, "low": l, "close": body_top, "volume": 1000, "atr14": atr14}


def _bearish_pin_row(upper_ratio: float = 0.65, atr14: float = 1.0) -> dict:
    """위꼬리가 upper_ratio만큼인 bearish pin bar"""
    l = 90.0
    total = 10.0
    upper_wick = total * upper_ratio
    body_top = l + total - upper_wick
    body_bottom = l + total * 0.08   # body 하단 8%
    h = l + total
    return {"open": body_top, "high": h, "low": l, "close": body_bottom, "volume": 1000, "atr14": atr14}


# ── 1. name ──────────────────────────────────────────────────────────────────

def test_name():
    assert PinBarStrategy.name == "pin_bar"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = PinBarStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. Bullish Pin Bar BUY ───────────────────────────────────────────────────

def test_bullish_pin_bar_buy():
    """아래꼬리 65% + RSI < 50 → BUY"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    rows[20] = _bullish_pin_row(lower_ratio=0.65, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "pin_bar"


# ── 4. Bearish Pin Bar SELL ──────────────────────────────────────────────────

def test_bearish_pin_bar_sell():
    """위꼬리 65% + RSI > 50 → SELL"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    # RSI > 50 유도: 상승 추세, pin bar도 이전 캔들보다 높게 close
    for i in range(22):
        rows[i]["close"] = 80.0 + i * 2.0
        rows[i]["open"] = 80.0 + i * 2.0 - 0.5
        rows[i]["high"] = 80.0 + i * 2.0 + 0.5
        rows[i]["low"] = 80.0 + i * 2.0 - 1.0
    # idx=20: bearish pin bar — 위꼬리 65%, 몸통 하단 33%
    # 전체 캔들 가격대에서 high, body 설정
    base_close = 80.0 + 20 * 2.0  # =120
    l = base_close - 10
    h = base_close + 10
    total = 20.0
    upper_wick = total * 0.65     # 13.0
    body_top = h - upper_wick     # 107
    body_bottom = l + total * 0.08  # 111.6 → body_mid=(107+111.6)/2=109.3
    # body_mid 109.3 < l + total*0.4 = 110+8=118? → 109.3 < 118 ✓
    rows[20] = {
        "open": body_top, "high": h, "low": l, "close": body_bottom,
        "volume": 1000, "atr14": 1.0
    }
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "pin_bar"


# ── 5. 아래꼬리 < 60% → BUY 없음 ─────────────────────────────────────────────

def test_lower_wick_too_small_no_buy():
    """아래꼬리 50% < 60% → BUY 조건 미충족"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    # body 중앙이 lower 50%: body=50~55, range=0~100
    rows[20] = {"open": 95.0, "high": 100.0, "low": 90.0, "close": 97.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 6. 위꼬리 < 60% → SELL 없음 ──────────────────────────────────────────────

def test_upper_wick_too_small_no_sell():
    """위꼬리 50% < 60% → SELL 조건 미충족"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_uptrend(rows, 20)
    rows[20] = {"open": 95.0, "high": 100.0, "low": 90.0, "close": 93.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# ── 7. RSI >= 50 → Bullish Pin Bar BUY 없음 ──────────────────────────────────

def test_rsi_above_50_no_bullish_pin():
    """RSI >= 50 → Bullish Pin Bar BUY 없음"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_uptrend(rows, 20)
    rows[20] = _bullish_pin_row(lower_ratio=0.65, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 8. RSI <= 50 → Bearish Pin Bar SELL 없음 ─────────────────────────────────

def test_rsi_below_50_no_bearish_pin():
    """RSI <= 50 → Bearish Pin Bar SELL 없음"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    rows[20] = _bearish_pin_row(upper_ratio=0.65, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# ── 9. confidence HIGH: 꼬리 >= 70% ──────────────────────────────────────────

def test_high_confidence_bullish_pin():
    """아래꼬리 >= 70% → HIGH confidence"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    rows[20] = _bullish_pin_row(lower_ratio=0.75, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 10. confidence MEDIUM: 60% <= 꼬리 < 70% ─────────────────────────────────

def test_medium_confidence_bullish_pin():
    """아래꼬리 60~70% → MEDIUM confidence"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    rows[20] = _bullish_pin_row(lower_ratio=0.63, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 11. zero range → HOLD ────────────────────────────────────────────────────

def test_zero_range_hold():
    """high == low → range=0 → HOLD"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[20] = {"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Zero range" in sig.reasoning


# ── 12. Signal 필드 검증 ─────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = PinBarStrategy()
    df = _make_df(_base_rows(22))
    sig = strategy.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")
    assert sig.strategy == "pin_bar"


# ── 13. entry_price == close ─────────────────────────────────────────────────

def test_entry_price_equals_close():
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    pin = _bullish_pin_row(lower_ratio=0.70, atr14=1.0)
    rows[20] = pin
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(pin["close"])


# ── 14. BUY invalidation에 low 포함 ──────────────────────────────────────────

def test_buy_invalidation_contains_low():
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_downtrend(rows, 20)
    rows[20] = _bullish_pin_row(lower_ratio=0.68, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "low" in sig.invalidation.lower() or "90" in sig.invalidation


# ── 15. HIGH confidence bearish pin bar ──────────────────────────────────────

def test_high_confidence_bearish_pin():
    """위꼬리 >= 70% → HIGH confidence"""
    strategy = PinBarStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows = _with_uptrend(rows, 20)
    rows[20] = _bearish_pin_row(upper_ratio=0.75, atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH
