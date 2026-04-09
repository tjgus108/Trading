"""Tests for ThreeCandlesStrategy."""

import pandas as pd
import pytest

from src.strategy.three_candles import ThreeCandlesStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": 1.0}


def _base_rows(n: int = 12) -> list:
    return [_base_row() for _ in range(n)]


def _bullish(open_, close, margin=0.5):
    return {"open": open_, "high": close + margin, "low": open_ - margin, "close": close, "volume": 1000, "atr14": 1.0}


def _bearish(open_, close, margin=0.5):
    return {"open": open_, "high": open_ + margin, "low": close - margin, "close": close, "volume": 1000, "atr14": 1.0}


def _tws_rows() -> list:
    """Three White Soldiers: c1(idx-2), c2(idx-1), c3(idx)"""
    rows = _base_rows(12)
    idx = len(rows) - 2  # 10
    # c1: open=100, close=102, body=2
    rows[idx - 2] = {"open": 100.0, "high": 102.3, "low": 99.5, "close": 102.0, "volume": 1000, "atr14": 1.0}
    # c2: open=101 (100 < 101 < 102), close=104
    rows[idx - 1] = {"open": 101.0, "high": 104.3, "low": 100.5, "close": 104.0, "volume": 1000, "atr14": 1.0}
    # c3: open=103 (101 < 103 < 104), close=106
    rows[idx]     = {"open": 103.0, "high": 106.3, "low": 102.5, "close": 106.0, "volume": 1000, "atr14": 1.0}
    return rows


def _tbc_rows() -> list:
    """Three Black Crows: 역방향"""
    rows = _base_rows(12)
    idx = len(rows) - 2  # 10
    # c1: open=106, close=104
    rows[idx - 2] = {"open": 106.0, "high": 106.5, "low": 103.7, "close": 104.0, "volume": 1000, "atr14": 1.0}
    # c2: open=105 (104 < 105 < 106), close=102
    rows[idx - 1] = {"open": 105.0, "high": 105.5, "low": 101.7, "close": 102.0, "volume": 1000, "atr14": 1.0}
    # c3: open=103 (102 < 103 < 104... wait: c2 close=102, c2 open=105 → open in (102, 105))
    # c3 open=103: 102 < 103 < 105 ✓, close=100
    rows[idx]     = {"open": 103.0, "high": 103.5, "low": 99.7, "close": 100.0, "volume": 1000, "atr14": 1.0}
    return rows


# ── 1. name ───────────────────────────────────────────────────────────────────

def test_name():
    assert ThreeCandlesStrategy.name == "three_candles"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = ThreeCandlesStrategy()
    df = _make_df(_base_rows(5))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. Three White Soldiers → BUY ────────────────────────────────────────────

def test_three_white_soldiers_buy():
    strategy = ThreeCandlesStrategy()
    df = _make_df(_tws_rows())
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "Three White Soldiers" in sig.reasoning


# ── 4. Three Black Crows → SELL ──────────────────────────────────────────────

def test_three_black_crows_sell():
    strategy = ThreeCandlesStrategy()
    df = _make_df(_tbc_rows())
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "Three Black Crows" in sig.reasoning


# ── 5. HIGH confidence: 위꼬리 작음 ─────────────────────────────────────────

def test_tws_high_confidence_small_wicks():
    """위꼬리 < body*0.3 → HIGH"""
    strategy = ThreeCandlesStrategy()
    rows = _tws_rows()
    idx = len(rows) - 2
    # 위꼬리 = high - close. body=2, wick < 0.6
    rows[idx - 2]["high"] = 102.2   # wick=0.2 < 0.6 ✓
    rows[idx - 1]["high"] = 104.2   # wick=0.2 ✓
    rows[idx]["high"]     = 106.2   # wick=0.2 ✓
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 6. MEDIUM confidence: 위꼬리 큰 경우 ─────────────────────────────────────

def test_tws_medium_confidence_large_wick():
    """위꼬리 >= body*0.3 하나라도 → MEDIUM"""
    strategy = ThreeCandlesStrategy()
    rows = _tws_rows()
    idx = len(rows) - 2
    # c3 body=3, wick=2 > 0.9 → MEDIUM
    rows[idx]["high"] = 108.0  # wick = 108 - 106 = 2 > 3*0.3=0.9
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 7. 패턴 없으면 HOLD ───────────────────────────────────────────────────────

def test_no_pattern_hold():
    strategy = ThreeCandlesStrategy()
    df = _make_df(_base_rows(12))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 8. close 순서 틀리면 패턴 불성립 ────────────────────────────────────────

def test_tws_close_not_ascending_hold():
    """c3 close < c2 close → 패턴 불성립"""
    strategy = ThreeCandlesStrategy()
    rows = _tws_rows()
    idx = len(rows) - 2
    rows[idx]["close"] = 103.0  # c2 close=104 > c3 close=103 → 불성립
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. open이 이전 body 밖이면 불성립 ────────────────────────────────────────

def test_tws_open_outside_body_hold():
    """c2 open > c1 close → open이 이전 body 밖"""
    strategy = ThreeCandlesStrategy()
    rows = _tws_rows()
    idx = len(rows) - 2
    rows[idx - 1]["open"] = 103.0  # c1 close=102 < c2 open=103 → 불성립
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 10. Signal 필드 검증 ──────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = ThreeCandlesStrategy()
    df = _make_df(_tws_rows())
    sig = strategy.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")
    assert sig.strategy == "three_candles"


# ── 11. entry_price == c3 close ──────────────────────────────────────────────

def test_entry_price_equals_c3_close():
    strategy = ThreeCandlesStrategy()
    rows = _tws_rows()
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.entry_price == pytest.approx(106.0)


# ── 12. TBC HIGH confidence: 아래꼬리 작음 ────────────────────────────────────

def test_tbc_high_confidence_small_wicks():
    """아래꼬리 < body*0.3 → HIGH"""
    strategy = ThreeCandlesStrategy()
    rows = _tbc_rows()
    idx = len(rows) - 2
    # lower_wick = open - low. c1 body=2, wick < 0.6
    rows[idx - 2]["low"] = 103.8   # wick = 106 - 103.8 = 2.2... body=2 → wick < 0.6 → low=105.5
    rows[idx - 2]["low"] = 105.6   # wick=0.4 < 0.6 ✓
    rows[idx - 1]["low"] = 104.6   # wick=0.4 ✓
    rows[idx]["low"]     = 102.6   # wick=0.4 ✓
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 13. 음봉이 아닌 경우 TBC 불성립 ─────────────────────────────────────────

def test_tbc_not_bearish_hold():
    """c1이 양봉이면 TBC 불성립"""
    strategy = ThreeCandlesStrategy()
    rows = _tbc_rows()
    idx = len(rows) - 2
    # c1을 양봉으로 변경
    rows[idx - 2]["close"] = 107.0  # open=106 < close=107 → 양봉
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
