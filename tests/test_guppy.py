"""
GuppyStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.guppy import GuppyStrategy, _calc_guppy
from src.strategy.base import Action, Confidence, Signal

_COLS = ["open", "close", "high", "low", "volume", "ema50", "atr14"]


def _make_df(n: int = 70, close: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 2.0] * n,
        "low": [close - 2.0] * n,
        "volume": [1000.0] * n,
        "ema50": [close] * n,
        "atr14": [2.0] * n,
    })


def _make_bullish_df(n: int = 70) -> pd.DataFrame:
    """close 꾸준히 상승 → Short Avg > Long Avg, Short Avg 상승 중."""
    closes = [100.0 + i * 0.5 for i in range(n)]
    return pd.DataFrame({
        "open": [c - 0.3 for c in closes],
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] - 10 for i in range(n)],
        "atr14": [2.0] * n,
    })


def _make_bearish_df(n: int = 70) -> pd.DataFrame:
    """close 꾸준히 하락 → Short Avg < Long Avg, Short Avg 하락 중."""
    closes = [100.0 - i * 0.5 for i in range(n)]
    return pd.DataFrame({
        "open": [c + 0.3 for c in closes],
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] + 10 for i in range(n)],
        "atr14": [2.0] * n,
    })


def _make_strong_bullish_df(n: int = 80) -> pd.DataFrame:
    """강한 상승 — separation > 1% 유도."""
    closes = [100.0 + i * 1.5 for i in range(n)]
    return pd.DataFrame({
        "open": [c - 0.5 for c in closes],
        "close": closes,
        "high": [c + 1.5 for c in closes],
        "low": [c - 1.5 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] - 20 for i in range(n)],
        "atr14": [3.0] * n,
    })


def _make_strong_bearish_df(n: int = 80) -> pd.DataFrame:
    """강한 하락 — separation < -1% 유도."""
    closes = [200.0 - i * 1.5 for i in range(n)]
    return pd.DataFrame({
        "open": [c + 0.5 for c in closes],
        "close": closes,
        "high": [c + 1.5 for c in closes],
        "low": [c - 1.5 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] + 20 for i in range(n)],
        "atr14": [3.0] * n,
    })


# ── 기본 인터페이스 테스트 ──────────────────────────────────────────────────


def test_returns_signal_instance():
    df = _make_df()
    sig = GuppyStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_strategy_name():
    assert GuppyStrategy.name == "guppy"


def test_signal_has_required_fields():
    df = _make_df()
    sig = GuppyStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_strategy_name_in_signal():
    df = _make_df()
    sig = GuppyStrategy().generate(df)
    assert sig.strategy == "guppy"


# ── 데이터 부족 테스트 ─────────────────────────────────────────────────────


def test_insufficient_data_returns_hold():
    df = _make_df(n=30)
    sig = GuppyStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_exactly_min_rows():
    """65행 정확히 — 유효한 Action 반환."""
    df = _make_df(n=65)
    sig = GuppyStrategy().generate(df)
    assert sig.action in list(Action)


def test_64_rows_returns_hold():
    df = _make_df(n=64)
    sig = GuppyStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── _calc_guppy 내부 함수 테스트 ──────────────────────────────────────────


def test_calc_guppy_returns_three_floats():
    df = _make_df(n=70)
    sa_now, sa_prev, la_now = _calc_guppy(df)
    assert isinstance(sa_now, float)
    assert isinstance(sa_prev, float)
    assert isinstance(la_now, float)


def test_calc_guppy_bullish_short_above_long():
    """상승 데이터 → Short Avg > Long Avg."""
    df = _make_bullish_df()
    sa_now, _, la_now = _calc_guppy(df)
    assert sa_now > la_now


def test_calc_guppy_bearish_short_below_long():
    """하락 데이터 → Short Avg < Long Avg."""
    df = _make_bearish_df()
    sa_now, _, la_now = _calc_guppy(df)
    assert sa_now < la_now


# ── BUY/SELL/HOLD 신호 테스트 ─────────────────────────────────────────────


def test_bullish_df_returns_buy():
    df = _make_bullish_df()
    sig = GuppyStrategy().generate(df)
    assert sig.action == Action.BUY


def test_bearish_df_returns_sell():
    df = _make_bearish_df()
    sig = GuppyStrategy().generate(df)
    assert sig.action == Action.SELL


def test_flat_df_returns_hold():
    """flat 데이터 — Short Avg ≈ Long Avg, 방향 불확실 → HOLD."""
    df = _make_df(n=70)
    sig = GuppyStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_buy_entry_price_is_close():
    df = _make_bullish_df()
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_sell_entry_price_is_close():
    df = _make_bearish_df()
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


# ── Confidence 레벨 테스트 ────────────────────────────────────────────────


def test_strong_bullish_high_confidence():
    df = _make_strong_bullish_df()
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_strong_bearish_high_confidence():
    df = _make_strong_bearish_df()
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


def test_non_hold_confidence_valid():
    """BUY/SELL 신호는 MEDIUM 또는 HIGH."""
    for df in [_make_bullish_df(), _make_bearish_df()]:
        sig = GuppyStrategy().generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_hold_confidence_low():
    df = _make_df(n=70)
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── bull_case / bear_case 테스트 ──────────────────────────────────────────


def test_buy_signal_has_bull_case():
    df = _make_bullish_df()
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.BUY:
        assert len(sig.bull_case) > 0


def test_sell_signal_has_bear_case():
    df = _make_bearish_df()
    sig = GuppyStrategy().generate(df)
    if sig.action == Action.SELL:
        assert len(sig.bear_case) > 0


# ── 엣지 케이스 ────────────────────────────────────────────────────────────


def test_large_dataframe():
    df = _make_df(n=500)
    sig = GuppyStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_all_same_close_no_crash():
    """모든 close 동일 — ZeroDivision 없어야 함."""
    df = _make_df(n=70, close=50000.0)
    sig = GuppyStrategy().generate(df)
    assert isinstance(sig, Signal)
