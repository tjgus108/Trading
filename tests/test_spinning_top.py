"""Tests for SpinningTopStrategy.

idx = len(df) - 2 = 13 (for 15-row df)
  curr = df.iloc[13]  ← breakout 봉
  prev = df.iloc[12]  ← spinning top 후보
df.iloc[14] is the open (in-progress) candle, ignored by strategy.
"""

import pandas as pd
import pytest

from src.strategy.spinning_top import SpinningTopStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5, atr14=1.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": atr14}


def _base_rows(n: int = 15, atr14: float = 1.0) -> list:
    return [_base_row(atr14=atr14) for _ in range(n)]


def _spinning_top_row(atr14: float = 1.0) -> dict:
    """
    open=100, close=100.1 → body=0.1
    high=101, low=99 → range=2, body/range=0.05 < 0.25
    upper_wick = 101 - 100.1 = 0.9 > body*0.5=0.05
    lower_wick = 100.0 - 99 = 1.0 > body*0.5=0.05
    """
    return {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.1, "volume": 1000, "atr14": atr14}


# ── 1. name ──────────────────────────────────────────────────────────────────

def test_name():
    assert SpinningTopStrategy.name == "spinning_top"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = SpinningTopStrategy()
    df = _make_df(_base_rows(5))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. BUY: Spinning Top 이후 양봉 돌파 + RSI < 55 ──────────────────────────

def test_buy_after_spinning_top_breakout():
    """prev=spinning top, curr=close > spinning top high, RSI < 55"""
    strategy = SpinningTopStrategy()
    # 30행: RSI 계산에 충분한 데이터 (14-period rolling)
    rows = _base_rows(30, atr14=1.0)
    # 하락 추세로 RSI < 55 유도 (rows[0]~rows[27])
    for i in range(28):
        rows[i]["close"] = 130.0 - i * 1.5
    # rows[28]: spinning top (prev, idx-1 when idx=29... no)
    # idx = len(df)-2 = 28, curr=rows[28], prev=rows[27]
    # So prev=rows[27] should be spinning top, curr=rows[28] is breakout
    for i in range(27):
        rows[i]["close"] = 130.0 - i * 1.5
    rows[27] = _spinning_top_row(atr14=1.0)  # high=101, low=99
    rows[28] = {"open": 101.0, "high": 102.5, "low": 100.5, "close": 102.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "spinning_top"


# ── 4. SELL: Spinning Top 이후 음봉 돌파 + RSI > 45 ─────────────────────────

def test_sell_after_spinning_top_breakdown():
    """prev=spinning top, curr=close < spinning top low, RSI > 45"""
    strategy = SpinningTopStrategy()
    # 30행: RSI 계산에 충분한 데이터
    rows = _base_rows(30, atr14=1.0)
    # 상승 추세로 RSI > 45 유도
    # idx = len(df)-2 = 28, curr=rows[28], prev=rows[27]
    for i in range(27):
        rows[i]["close"] = 70.0 + i * 1.5
    rows[27] = _spinning_top_row(atr14=1.0)  # high=101, low=99
    # curr: breakdown below prev_low(99)
    rows[28] = {"open": 99.0, "high": 99.5, "low": 97.5, "close": 98.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "spinning_top"


# ── 5. 이전봉이 Spinning Top 아니면 HOLD ──────────────────────────────────────

def test_not_spinning_top_hold():
    """prev(rows[12]) body >= range*0.25 → spinning top 아님 → HOLD"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    # body=1.5, range=2 → 0.75 ≥ 0.25
    rows[12] = {"open": 99.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000, "atr14": 1.0}
    rows[13] = {"open": 101.0, "high": 102.5, "low": 100.5, "close": 102.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. 돌파 없으면 HOLD ───────────────────────────────────────────────────────

def test_no_breakout_hold():
    """Spinning Top 있어도 curr close가 high/low 사이 → HOLD"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    rows[12] = _spinning_top_row(atr14=1.0)  # high=101, low=99
    # curr close=100.5: between 99 and 101, no breakout
    rows[13] = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. confidence HIGH: 돌파폭 > ATR*0.3 (BUY) ───────────────────────────────

def test_high_confidence_buy():
    """breakout_up = curr_close - prev_high = 102.5-101=1.5 > atr*0.3=0.3 → HIGH"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    for i in range(12):
        rows[i]["close"] = 105.0 - i * 1.5
    rows[12] = _spinning_top_row(atr14=1.0)  # high=101
    rows[13] = {"open": 101.0, "high": 103.0, "low": 100.5, "close": 102.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 8. confidence MEDIUM: 돌파폭 <= ATR*0.3 (BUY) ────────────────────────────

def test_medium_confidence_buy():
    """breakout_up = 101.1-101=0.1 < atr*0.3=0.3 → MEDIUM"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    for i in range(12):
        rows[i]["close"] = 105.0 - i * 1.5
    rows[12] = _spinning_top_row(atr14=1.0)  # high=101
    rows[13] = {"open": 101.0, "high": 101.5, "low": 100.8, "close": 101.1, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 9. confidence HIGH: 돌파폭 > ATR*0.3 (SELL) ──────────────────────────────

def test_high_confidence_sell():
    """breakout_down = prev_low - curr_close = 99-97.5=1.5 > atr*0.3=0.3 → HIGH"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    for i in range(12):
        rows[i]["close"] = 95.0 + i * 1.5
    rows[12] = _spinning_top_row(atr14=1.0)  # low=99
    rows[13] = {"open": 99.0, "high": 99.5, "low": 97.0, "close": 97.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


# ── 10. Signal 필드 검증 ──────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = SpinningTopStrategy()
    df = _make_df(_base_rows(15))
    sig = strategy.generate(df)
    for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation", "bull_case", "bear_case"):
        assert hasattr(sig, field)
    assert sig.strategy == "spinning_top"


# ── 11. entry_price == close ──────────────────────────────────────────────────

def test_entry_price_equals_close():
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    for i in range(12):
        rows[i]["close"] = 105.0 - i * 1.5
    rows[12] = _spinning_top_row(atr14=1.0)  # high=101
    rows[13] = {"open": 101.0, "high": 103.0, "low": 100.5, "close": 102.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(102.5)


# ── 12. Spinning Top: 한쪽 꼬리 없으면 조건 미충족 → HOLD ────────────────────

def test_one_sided_wick_not_spinning_top():
    """lower_wick < body*0.5 → spinning top 아님 → HOLD"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    # body=0.1, upper_wick=1.0, lower_wick=0.01 < 0.05 → not spinning top
    rows[12] = {"open": 100.0, "high": 101.1, "low": 99.99, "close": 100.1, "volume": 1000, "atr14": 1.0}
    rows[13] = {"open": 101.0, "high": 102.5, "low": 100.5, "close": 102.0, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 13. RSI 조건 미충족 → BUY 없음 ───────────────────────────────────────────

def test_buy_rsi_too_high_hold():
    """curr_close > prev_high but RSI >= 55 → BUY 없음"""
    strategy = SpinningTopStrategy()
    rows = _base_rows(15, atr14=1.0)
    # 강한 상승 추세로 RSI >= 55
    for i in range(12):
        rows[i]["close"] = 90.0 + i * 3.0
    rows[12] = _spinning_top_row(atr14=1.0)  # high=101
    rows[13] = {"open": 101.0, "high": 103.0, "low": 100.5, "close": 102.5, "volume": 1000, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY
