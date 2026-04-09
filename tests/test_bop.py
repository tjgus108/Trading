"""
BOPStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bop import BOPStrategy, _calc_bop
from src.strategy.base import Action, Confidence, Signal

_COLS = ["open", "close", "high", "low", "volume", "ema50", "atr14"]


def _make_df(n: int = 30, close: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame (close == open → BOP ≈ 0)."""
    data = {
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 2.0] * n,
        "low": [close - 2.0] * n,
        "volume": [1000.0] * n,
        "ema50": [close] * n,
        "atr14": [2.0] * n,
    }
    return pd.DataFrame(data)


def _make_bullish_df(n: int = 30, close: float = 110.0, ema50: float = 100.0) -> pd.DataFrame:
    """close > open + 고폭 좁음 → BOP > 0.1, close > ema50."""
    data = {
        "open": [100.0] * n,
        "close": [close] * n,
        "high": [close + 1.0] * n,
        "low": [99.0] * n,
        "volume": [1000.0] * n,
        "ema50": [ema50] * n,
        "atr14": [2.0] * n,
    }
    return pd.DataFrame(data)


def _make_bearish_df(n: int = 30, close: float = 90.0, ema50: float = 100.0) -> pd.DataFrame:
    """close < open + 고폭 좁음 → BOP < -0.1, close < ema50."""
    data = {
        "open": [100.0] * n,
        "close": [close] * n,
        "high": [101.0] * n,
        "low": [close - 1.0] * n,
        "volume": [1000.0] * n,
        "ema50": [ema50] * n,
        "atr14": [2.0] * n,
    }
    return pd.DataFrame(data)


def _make_rising_bop_df(n: int = 40) -> pd.DataFrame:
    """BOP가 점점 상승하는 데이터 — 상향 중 조건 유도."""
    opens = [100.0] * n
    closes = [100.0 + i * 0.3 for i in range(n)]
    highs = [c + 0.5 for c in closes]
    lows = [99.5] * n
    ema50 = [c - 5 for c in closes]
    data = {
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "ema50": ema50,
        "atr14": [1.0] * n,
    }
    return pd.DataFrame(data)


def _make_falling_bop_df(n: int = 40) -> pd.DataFrame:
    """BOP가 점점 하락하는 데이터 — 하향 중 조건 유도."""
    opens = [100.0] * n
    closes = [100.0 - i * 0.3 for i in range(n)]
    highs = [100.5] * n
    lows = [c - 0.5 for c in closes]
    ema50 = [c + 5 for c in closes]
    data = {
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "ema50": ema50,
        "atr14": [1.0] * n,
    }
    return pd.DataFrame(data)


# ── 기본 인터페이스 테스트 ──────────────────────────────────────────────────


def test_returns_signal_instance():
    df = _make_df()
    sig = BOPStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_strategy_name():
    assert BOPStrategy.name == "bop"


def test_signal_has_required_fields():
    df = _make_df()
    sig = BOPStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_strategy_name_in_signal():
    df = _make_df()
    sig = BOPStrategy().generate(df)
    assert sig.strategy == "bop"


# ── 데이터 부족 테스트 ─────────────────────────────────────────────────────


def test_insufficient_data_returns_hold():
    df = _make_df(n=10)
    sig = BOPStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_exactly_min_rows():
    """20행 정확히 — 유효한 Action 반환."""
    df = _make_df(n=20)
    sig = BOPStrategy().generate(df)
    assert sig.action in list(Action)


def test_19_rows_returns_hold():
    df = _make_df(n=19)
    sig = BOPStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── _calc_bop 내부 함수 테스트 ────────────────────────────────────────────


def test_calc_bop_returns_two_floats():
    df = _make_df(n=30)
    bop_now, bop_prev = _calc_bop(df)
    assert isinstance(bop_now, float)
    assert isinstance(bop_prev, float)


def test_calc_bop_bullish_positive():
    """매수 우위 데이터 → BOP > 0."""
    df = _make_bullish_df()
    bop_now, _ = _calc_bop(df)
    assert bop_now > 0


def test_calc_bop_bearish_negative():
    """매도 우위 데이터 → BOP < 0."""
    df = _make_bearish_df()
    bop_now, _ = _calc_bop(df)
    assert bop_now < 0


# ── HOLD 조건 테스트 ───────────────────────────────────────────────────────


def test_flat_market_holds():
    """close == open (BOP=0) → HOLD."""
    df = _make_df(n=30)
    sig = BOPStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_hold_action_has_low_confidence():
    df = _make_df(n=30)
    sig = BOPStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── BUY/SELL 신호 테스트 ──────────────────────────────────────────────────


def test_buy_entry_price_is_close():
    """BUY 신호 진입가 = 신호 봉 close."""
    df = _make_rising_bop_df()
    sig = BOPStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_sell_entry_price_is_close():
    df = _make_falling_bop_df()
    sig = BOPStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_buy_signal_has_bull_case():
    df = _make_rising_bop_df()
    sig = BOPStrategy().generate(df)
    if sig.action == Action.BUY:
        assert len(sig.bull_case) > 0


def test_sell_signal_has_bear_case():
    df = _make_falling_bop_df()
    sig = BOPStrategy().generate(df)
    if sig.action == Action.SELL:
        assert len(sig.bear_case) > 0


# ── Confidence 레벨 테스트 ────────────────────────────────────────────────


def test_non_hold_confidence():
    """BUY/SELL 신호는 MEDIUM 또는 HIGH."""
    for df in [_make_rising_bop_df(), _make_falling_bop_df(),
               _make_bullish_df(), _make_bearish_df()]:
        sig = BOPStrategy().generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── 엣지 케이스 ────────────────────────────────────────────────────────────


def test_zero_range_no_crash():
    """high == low (range=0) — 1e-10 보호로 ZeroDivision 없어야 함."""
    df = _make_df(n=30)
    df["high"] = df["close"]
    df["low"] = df["close"]
    sig = BOPStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_large_dataframe():
    df = _make_df(n=500)
    sig = BOPStrategy().generate(df)
    assert isinstance(sig, Signal)
