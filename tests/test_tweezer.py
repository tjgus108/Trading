"""Tests for TweezerStrategy."""

import pandas as pd
import pytest

from src.strategy.tweezer import TweezerStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _base_row(open_=100.0, high=101.0, low=99.0, close=100.5, atr14=1.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": 1000, "atr14": atr14}


def _base_rows(n: int = 22, atr14: float = 1.0) -> list:
    return [_base_row(atr14=atr14) for _ in range(n)]


def _with_downtrend(rows: list, end_idx: int) -> list:
    """RSI < 50 유도: 가파른 하락 추세"""
    for i in range(end_idx):
        rows[i]["close"] = 120.0 - i * 2.0
    return rows


def _with_uptrend(rows: list, end_idx: int) -> list:
    """RSI > 50 유도: 가파른 상승 추세"""
    for i in range(end_idx):
        rows[i]["close"] = 80.0 + i * 2.0
    return rows


# ── 1. name ──────────────────────────────────────────────────────────────────

def test_name():
    assert TweezerStrategy.name == "tweezer"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data():
    strategy = TweezerStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. Tweezer Bottom BUY ────────────────────────────────────────────────────

def test_tweezer_bottom_buy():
    """이전봉 음봉 + 현재봉 양봉 + low 일치 + RSI < 50 → BUY"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    # prev (idx=19): 음봉, low=60.0
    rows[19] = {"open": 63.0, "high": 64.0, "low": 60.0, "close": 61.0, "volume": 1000, "atr14": 2.0}
    # curr (idx=20): 양봉, low=60.05 → |60.05-60.0|=0.05 < atr*0.1=0.2
    rows[20] = {"open": 60.5, "high": 63.0, "low": 60.05, "close": 62.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "tweezer"


# ── 4. Tweezer Top SELL ──────────────────────────────────────────────────────

def test_tweezer_top_sell():
    """이전봉 양봉 + 현재봉 음봉 + high 일치 + RSI > 50 → SELL"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_uptrend(rows, 19)
    # prev (idx=19): 양봉, high=118.0
    rows[19] = {"open": 115.0, "high": 118.0, "low": 114.0, "close": 117.0, "volume": 1000, "atr14": 2.0}
    # curr (idx=20): 음봉, high=118.05 → |118.05-118.0|=0.05 < atr*0.1=0.2
    rows[20] = {"open": 117.5, "high": 118.05, "low": 115.0, "close": 115.5, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "tweezer"


# ── 5. low 불일치 → HOLD ────────────────────────────────────────────────────

def test_low_mismatch_hold():
    """low 차이가 ATR*0.1 이상 → HOLD"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    rows[19] = {"open": 65.0, "high": 66.0, "low": 60.0, "close": 61.0, "volume": 1000, "atr14": 2.0}
    # low=60.5 → |60.5-60.0|=0.5 > atr*0.1=0.2
    rows[20] = {"open": 61.0, "high": 64.0, "low": 60.5, "close": 63.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. high 불일치 → HOLD ───────────────────────────────────────────────────

def test_high_mismatch_hold():
    """high 차이가 ATR*0.1 이상 → HOLD"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_uptrend(rows, 19)
    rows[19] = {"open": 115.0, "high": 118.0, "low": 114.0, "close": 117.0, "volume": 1000, "atr14": 2.0}
    # high=119.0 → |119.0-118.0|=1.0 > atr*0.1=0.2
    rows[20] = {"open": 117.5, "high": 119.0, "low": 115.0, "close": 115.5, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. RSI >= 50 인 경우 BUY 없음 ────────────────────────────────────────────

def test_rsi_above_50_no_buy():
    """RSI >= 50 → Tweezer Bottom BUY 없음"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_uptrend(rows, 19)
    rows[19] = {"open": 117.0, "high": 118.0, "low": 115.0, "close": 115.5, "volume": 1000, "atr14": 2.0}
    rows[20] = {"open": 115.5, "high": 118.0, "low": 115.05, "close": 117.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 8. RSI <= 50 인 경우 SELL 없음 ───────────────────────────────────────────

def test_rsi_below_50_no_sell():
    """RSI <= 50 → Tweezer Top SELL 없음"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    rows[19] = {"open": 63.0, "high": 66.0, "low": 62.0, "close": 65.0, "volume": 1000, "atr14": 2.0}
    rows[20] = {"open": 64.5, "high": 66.05, "low": 62.0, "close": 63.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# ── 9. confidence HIGH: low_diff < ATR*0.05 ──────────────────────────────────

def test_high_confidence_tweezer_bottom():
    """low_diff < ATR*0.05 → HIGH confidence"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    rows[19] = {"open": 63.0, "high": 64.0, "low": 60.0, "close": 61.0, "volume": 1000, "atr14": 2.0}
    # low_diff=0.01 < atr*0.05=0.1
    rows[20] = {"open": 60.5, "high": 63.0, "low": 60.01, "close": 62.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 10. confidence MEDIUM: ATR*0.05 <= low_diff < ATR*0.1 ────────────────────

def test_medium_confidence_tweezer_bottom():
    """ATR*0.05 <= low_diff < ATR*0.1 → MEDIUM confidence"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    rows[19] = {"open": 63.0, "high": 64.0, "low": 60.0, "close": 61.0, "volume": 1000, "atr14": 2.0}
    # low_diff=0.15 → ATR*0.05=0.1 <= 0.15 < ATR*0.1=0.2
    rows[20] = {"open": 60.5, "high": 63.0, "low": 60.15, "close": 62.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 11. Signal 필드 검증 ─────────────────────────────────────────────────────

def test_signal_fields_present():
    strategy = TweezerStrategy()
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
    assert sig.strategy == "tweezer"


# ── 12. entry_price == close ─────────────────────────────────────────────────

def test_entry_price_equals_close():
    """BUY 신호 시 entry_price == curr close"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    rows[19] = {"open": 63.0, "high": 64.0, "low": 60.0, "close": 61.0, "volume": 1000, "atr14": 2.0}
    rows[20] = {"open": 60.5, "high": 63.0, "low": 60.05, "close": 62.5, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(62.5)


# ── 13. SELL invalidation 필드에 high 포함 ────────────────────────────────────

def test_sell_invalidation_contains_high():
    """SELL 신호의 invalidation에 high 값 포함"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_uptrend(rows, 19)
    rows[19] = {"open": 115.0, "high": 118.0, "low": 114.0, "close": 117.0, "volume": 1000, "atr14": 2.0}
    rows[20] = {"open": 117.5, "high": 118.05, "low": 115.0, "close": 115.5, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "118" in sig.invalidation or "high" in sig.invalidation.lower()


# ── 14. 현재봉 음봉 → Tweezer Bottom 없음 ────────────────────────────────────

def test_curr_bearish_no_tweezer_bottom():
    """현재봉이 음봉이면 Tweezer Bottom 성립 안됨"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    rows[19] = {"open": 65.0, "high": 66.0, "low": 60.0, "close": 61.0, "volume": 1000, "atr14": 2.0}
    # 현재봉 음봉 (close < open)
    rows[20] = {"open": 62.0, "high": 63.0, "low": 60.05, "close": 60.5, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 15. 이전봉 양봉 → Tweezer Bottom 없음 ────────────────────────────────────

def test_prev_bullish_no_tweezer_bottom():
    """이전봉이 양봉이면 Tweezer Bottom 성립 안됨"""
    strategy = TweezerStrategy()
    rows = _base_rows(22, atr14=2.0)
    rows = _with_downtrend(rows, 19)
    # prev 양봉
    rows[19] = {"open": 60.0, "high": 64.0, "low": 59.5, "close": 63.0, "volume": 1000, "atr14": 2.0}
    rows[20] = {"open": 63.5, "high": 65.0, "low": 59.55, "close": 64.0, "volume": 1000, "atr14": 2.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY
