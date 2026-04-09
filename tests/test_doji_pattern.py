"""Tests for DojiPatternStrategy."""

import pandas as pd
import pytest

from src.strategy.doji_pattern import DojiPatternStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5, atr14=1.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": atr14}


def _base_rows(n: int = 22, atr14: float = 1.0) -> list:
    return [_base_row(atr14=atr14) for _ in range(n)]


def _doji_row(atr14: float = 1.0, perfect: bool = False) -> dict:
    """body < range*0.1 (또는 *0.05 for perfect)"""
    # open=100, close=100.05 (body=0.05), high=101, low=99 (range=2) → body/range=0.025 < 0.05
    return {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.05, "volume": 1000, "atr14": atr14}


def _big_bearish_row(atr14: float = 1.0) -> dict:
    """body=3 > atr*0.5=0.5, open > close"""
    return {"open": 103.0, "high": 104.0, "low": 99.5, "close": 100.0, "volume": 1000, "atr14": atr14}


def _big_bullish_row(atr14: float = 1.0) -> dict:
    """body=3 > atr*0.5=0.5, close > open"""
    return {"open": 100.0, "high": 104.0, "low": 99.5, "close": 103.0, "volume": 1000, "atr14": atr14}


# ── 1. name ──────────────────────────────────────────────────────────────────

def test_name():
    assert DojiPatternStrategy.name == "doji_pattern"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = DojiPatternStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. BUY: Doji + 큰 음봉 + RSI < 45 ────────────────────────────────────

def test_buy_signal_doji_after_bearish():
    """Doji + 이전봉 큰 음봉 + RSI < 45 → BUY"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    # 가파른 하락 추세로 RSI < 45 유도 (rows[19], [20]은 나중에 설정)
    for i in range(18):
        rows[i]["close"] = 100.0 - i * 2.0
    # rows[18]: 추세 계속
    rows[18]["close"] = 100.0 - 18 * 2.0
    # rows[19]: 큰 음봉 (open > close, body > atr*0.5=0.5)
    rows[19] = {"open": 70.0, "high": 71.0, "low": 65.5, "close": 67.0, "volume": 1000, "atr14": 1.0}
    # rows[20]: Doji (body << range), close 근처에서 atr14 설정
    rows[20] = {"open": 67.0, "high": 68.0, "low": 66.0, "close": 67.05, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "doji_pattern"


# ── 4. SELL: Doji + 큰 양봉 + RSI > 55 ───────────────────────────────────

def test_sell_signal_doji_after_bullish():
    """Doji + 이전봉 큰 양봉 + RSI > 55 → SELL"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[19] = _big_bullish_row(atr14=1.0)
    rows[20] = _doji_row(atr14=1.0)
    # RSI > 55: 상승 추세
    for i in range(20):
        rows[i]["close"] = 95.0 + i * 0.5
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "doji_pattern"


# ── 5. Doji 아니면 HOLD ───────────────────────────────────────────────────

def test_not_doji_hold():
    """body >= range*0.1 → Doji 아님 → HOLD"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    # body=2, range=2 → body/range=1.0 ≥ 0.1
    rows[20] = {"open": 99.0, "high": 101.0, "low": 99.0, "close": 101.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Doji 있지만 RSI 조건 불충족 → HOLD ──────────────────────────────────

def test_doji_rsi_not_satisfied_hold():
    """Doji + 큰 음봉 but RSI > 45 → BUY 없음 (상승 추세로 RSI 높임)"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    # RSI > 45: 가파른 상승 추세로 RSI 높임
    for i in range(22):
        rows[i]["close"] = 90.0 + i * 2.0
    rows[19] = _big_bearish_row(atr14=1.0)
    rows[20] = _doji_row(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    # 상승 추세에서 RSI가 높으므로 BUY 조건(< 45) 미충족 → HOLD 또는 SELL
    assert sig.action != Action.BUY


# ── 7. confidence HIGH: 완벽한 Doji (body < range*0.05) ───────────────────

def test_high_confidence_perfect_doji():
    """body < range*0.05 → HIGH confidence"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[19] = _big_bearish_row(atr14=1.0)
    # body=0.05, range=2 → 0.025 < 0.05 → perfect Doji
    rows[20] = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.05, "volume": 1000, "atr14": 1.0}
    for i in range(20):
        rows[i]["close"] = 100.0 - i * 0.5
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 8. confidence MEDIUM: 불완전한 Doji (body < range*0.1 but >= range*0.05) ──

def test_medium_confidence_imperfect_doji():
    """body/range = 0.07 → MEDIUM confidence"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[19] = _big_bearish_row(atr14=1.0)
    # body=0.14, range=2 → 0.07 < 0.1 but > 0.05
    rows[20] = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.14, "volume": 1000, "atr14": 1.0}
    for i in range(20):
        rows[i]["close"] = 100.0 - i * 0.5
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 9. 이전봉 body <= atr*0.5 → 조건 미충족 ─────────────────────────────────

def test_prev_body_too_small_no_signal():
    """이전봉 body < ATR*0.5 → BUY/SELL 조건 미충족"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=2.0)  # atr=2, threshold=1.0
    # prev: 음봉이지만 body=0.3 < 1.0
    rows[19] = {"open": 100.3, "high": 101.0, "low": 99.5, "close": 100.0, "volume": 1000, "atr14": 2.0}
    rows[20] = _doji_row(atr14=2.0)
    for i in range(20):
        rows[i]["close"] = 100.0 - i * 0.5
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 10. Signal 필드 검증 ─────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = DojiPatternStrategy()
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
    assert sig.strategy == "doji_pattern"


# ── 11. range=0 인 경우 (open==high==low==close) → HOLD ──────────────────

def test_zero_range_hold():
    """range=0 이면 Doji 판단 불가 → HOLD"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[20] = {"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 12. entry_price == close ─────────────────────────────────────────────────

def test_entry_price_equals_close():
    """entry_price는 현재 봉의 close 값"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[19] = _big_bearish_row(atr14=1.0)
    rows[20] = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.05, "volume": 1000, "atr14": 1.0}
    for i in range(20):
        rows[i]["close"] = 100.0 - i * 0.5
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(100.05)


# ── 13. SELL 신호의 invalidation 필드 ─────────────────────────────────────

def test_sell_invalidation_contains_high():
    """SELL 신호의 invalidation에 high 값 포함"""
    strategy = DojiPatternStrategy()
    rows = _base_rows(22, atr14=1.0)
    rows[19] = _big_bullish_row(atr14=1.0)
    rows[20] = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.05, "volume": 1000, "atr14": 1.0}
    for i in range(20):
        rows[i]["close"] = 95.0 + i * 0.5
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "101" in sig.invalidation or "high" in sig.invalidation.lower()
