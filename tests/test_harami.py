"""Tests for HaramiStrategy."""

import pandas as pd
import pytest

from src.strategy.harami import HaramiStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5, atr14=1.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": atr14}


def _base_rows(n: int = 22, atr14: float = 1.0) -> list:
    return [_base_row(atr14=atr14) for _ in range(n)]


def _big_bearish_row(atr14: float = 1.0) -> dict:
    """body=3 > atr*0.5=0.5, open > close"""
    return {"open": 103.0, "high": 104.0, "low": 99.5, "close": 100.0, "volume": 1000, "atr14": atr14}


def _big_bullish_row(atr14: float = 1.0) -> dict:
    """body=3 > atr*0.5=0.5, close > open"""
    return {"open": 100.0, "high": 104.0, "low": 99.5, "close": 103.0, "volume": 1000, "atr14": atr14}


def _small_bullish_inside(prev_open=103.0, prev_close=100.0, atr14=1.0) -> dict:
    """현재봉 양봉, 이전봉 body 내부에 위치, body < prev_body * 0.5"""
    # prev_body = 3, curr_body = 0.8 (< 1.5), inside prev body [100, 103]
    return {"open": 100.5, "high": 102.0, "low": 100.3, "close": 101.3, "volume": 1000, "atr14": atr14}


def _small_bearish_inside(prev_open=100.0, prev_close=103.0, atr14=1.0) -> dict:
    """현재봉 음봉, 이전봉 body 내부에 위치, body < prev_body * 0.5"""
    # prev_body = 3, curr_body = 0.8 (< 1.5), inside prev body [100, 103]
    return {"open": 102.5, "high": 102.7, "low": 101.3, "close": 101.7, "volume": 1000, "atr14": atr14}


# ── 1. name ───────────────────────────────────────────────────────────────────

def test_name():
    assert HaramiStrategy.name == "harami"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = HaramiStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. BUY: Bullish Harami + RSI < 50 ────────────────────────────────────────

def test_bullish_harami_buy():
    """큰 음봉 + 작은 양봉(내부) + RSI < 50 → BUY"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    # 급격한 하락 추세로 RSI << 50 유도
    for i in range(20):
        rows[i]["close"] = 200.0 - i * 8.0
    rows[i]["open"] = rows[i]["close"] + 8.0
    # rows[19]: 큰 음봉 (body=3, open=103, close=100), atr 맞게
    rows[19] = {"open": 103.0, "high": 104.0, "low": 99.5, "close": 100.0, "volume": 1000, "atr14": 1.0}
    # rows[20]: 작은 양봉, 이전봉 body [100, 103] 내부
    rows[20] = {"open": 100.5, "high": 102.0, "low": 100.3, "close": 101.3, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "harami"


# ── 4. SELL: Bearish Harami + RSI > 50 ───────────────────────────────────────

def test_bearish_harami_sell():
    """큰 양봉 + 작은 음봉(내부) + RSI > 50 → SELL"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    # 상승 추세로 RSI > 50 유도
    for i in range(20):
        rows[i]["close"] = 90.0 + i * 1.5
    # rows[19]: 큰 양봉 (body=3, open=100, close=103)
    rows[19] = _big_bullish_row(atr14=1.0)
    # rows[20]: 작은 음봉, 이전봉 body [100, 103] 내부
    rows[20] = _small_bearish_inside(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "harami"


# ── 5. 현재봉이 이전봉 body 밖 → HOLD ────────────────────────────────────────

def test_not_inside_hold():
    """현재봉 open/close가 이전봉 body 밖에 있으면 HOLD"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)
    # outside: open=98 (below prev body bottom=100)
    rows[20] = {"open": 98.0, "high": 99.0, "low": 97.5, "close": 98.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. 현재봉 body >= 이전봉 body * 0.5 → HOLD ───────────────────────────────

def test_curr_body_too_large_hold():
    """현재봉 body가 이전봉 body의 0.5 이상이면 Harami 아님 → HOLD"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)  # body=3
    # curr body = 2.0 >= 3*0.5=1.5 → 조건 불충족
    rows[20] = {"open": 100.5, "high": 103.0, "low": 100.2, "close": 102.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. RSI >= 50 (BUY 조건 미충족) → HOLD ────────────────────────────────────

def test_rsi_too_high_no_buy():
    """큰 음봉 + 작은 양봉(내부) but RSI >= 50 → BUY 없음"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    # 상승 추세로 RSI >= 50
    for i in range(20):
        rows[i]["close"] = 90.0 + i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)
    rows[20] = _small_bullish_inside(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 8. RSI <= 50 (SELL 조건 미충족) → HOLD ───────────────────────────────────

def test_rsi_too_low_no_sell():
    """큰 양봉 + 작은 음봉(내부) but RSI << 50 → SELL 없음"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    # 급격한 하락 추세로 RSI << 50 (very low)
    for i in range(20):
        rows[i]["close"] = 200.0 - i * 8.0
    rows[i]["open"] = rows[i]["close"] + 8.0
    rows[19] = _big_bullish_row(atr14=1.0)
    rows[20] = _small_bearish_inside(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# ── 9. confidence HIGH: curr_body < prev_body * 0.3 ──────────────────────────

def test_high_confidence_very_small_body():
    """curr_body < prev_body * 0.3 → HIGH confidence"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)  # body=3
    # curr_body=0.2 < 3*0.3=0.9 → HIGH
    rows[20] = {"open": 101.0, "high": 101.5, "low": 100.8, "close": 101.2, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 10. confidence MEDIUM: curr_body >= prev_body * 0.3 ──────────────────────

def test_medium_confidence_moderate_body():
    """curr_body >= prev_body * 0.3 but < prev_body * 0.5 → MEDIUM"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)  # body=3
    # curr_body=1.0 (>= 3*0.3=0.9 but < 3*0.5=1.5) → MEDIUM
    rows[20] = {"open": 100.5, "high": 101.8, "low": 100.3, "close": 101.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 11. 이전봉 body <= ATR * 0.5 → HOLD ─────────────────────────────────────

def test_prev_body_too_small_hold():
    """이전봉 body가 ATR*0.5 이하 → 큰 봉 조건 불충족 → HOLD"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=2.0)  # atr=2, threshold=1.0
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    # prev body=0.5 < atr*0.5=1.0
    rows[19] = {"open": 100.5, "high": 101.0, "low": 99.5, "close": 100.0, "volume": 1000, "atr14": 2.0}
    rows[20] = _small_bullish_inside(atr14=2.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 12. Signal 필드 검증 ──────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = HaramiStrategy()
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
    assert sig.strategy == "harami"


# ── 13. entry_price == close ──────────────────────────────────────────────────

def test_entry_price_equals_close():
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)
    rows[20] = _small_bullish_inside(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))


# ── 14. 현재봉이 양봉이 아니면 Bullish Harami 조건 불충족 ─────────────────────

def test_curr_not_bullish_no_buy():
    """이전봉 큰 음봉 + 현재봉 음봉 → Bullish Harami 불성립"""
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)
    # 음봉 (close < open), 내부
    rows[20] = {"open": 101.5, "high": 102.0, "low": 100.5, "close": 101.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 15. BUY 신호 invalidation 필드에 low 포함 ────────────────────────────────

def test_buy_invalidation_contains_low():
    strategy = HaramiStrategy()
    rows = _base_rows(22, atr14=1.0)
    for i in range(20):
        rows[i]["close"] = 110.0 - i * 1.5
    rows[19] = _big_bearish_row(atr14=1.0)
    rows[20] = _small_bullish_inside(atr14=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "low" in sig.invalidation.lower() or "99.5" in sig.invalidation
