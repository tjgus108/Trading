"""
APOStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.apo import APOStrategy, _calc_apo
from src.strategy.base import Action, Confidence, Signal

_COLS = ["open", "close", "high", "low", "volume", "ema50", "atr14"]


def _make_df(n: int = 35, close: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame (EMA10 ≈ EMA20 → APO ≈ 0)."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 2.0] * n,
        "low": [close - 2.0] * n,
        "volume": [1000.0] * n,
        "ema50": [close] * n,
        "atr14": [2.0] * n,
    })


def _make_bullish_cross_df(n: int = 60) -> pd.DataFrame:
    """
    초반 하락 후 상승 전환 — APO > 0 + 상향 크로스 유도.
    처음엔 하락, 나중엔 강한 상승.
    """
    closes = []
    for i in range(n):
        if i < n // 2:
            closes.append(100.0 - i * 0.2)
        else:
            closes.append(closes[-1] + (i - n // 2) * 0.8)
    return pd.DataFrame({
        "open": [c - 0.1 for c in closes],
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] - 5 for i in range(n)],
        "atr14": [2.0] * n,
    })


def _make_bearish_cross_df(n: int = 60) -> pd.DataFrame:
    """
    초반 상승 후 하락 전환 — APO < 0 + 하향 크로스 유도.
    """
    closes = []
    for i in range(n):
        if i < n // 2:
            closes.append(100.0 + i * 0.2)
        else:
            closes.append(closes[-1] - (i - n // 2) * 0.8)
    return pd.DataFrame({
        "open": [c + 0.1 for c in closes],
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] + 5 for i in range(n)],
        "atr14": [2.0] * n,
    })


def _make_strong_apo_df(n: int = 60) -> pd.DataFrame:
    """APO/close > 0.5% — HIGH confidence 유도."""
    closes = [100.0 + i * 2.0 for i in range(n)]
    return pd.DataFrame({
        "open": [c - 0.5 for c in closes],
        "close": closes,
        "high": [c + 2.0 for c in closes],
        "low": [c - 2.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] - 15 for i in range(n)],
        "atr14": [3.0] * n,
    })


# ── 기본 인터페이스 테스트 ──────────────────────────────────────────────────


def test_returns_signal_instance():
    df = _make_df()
    sig = APOStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_strategy_name():
    assert APOStrategy.name == "apo"


def test_signal_has_required_fields():
    df = _make_df()
    sig = APOStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_strategy_name_in_signal():
    df = _make_df()
    sig = APOStrategy().generate(df)
    assert sig.strategy == "apo"


# ── 데이터 부족 테스트 ─────────────────────────────────────────────────────


def test_insufficient_data_returns_hold():
    df = _make_df(n=15)
    sig = APOStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_exactly_min_rows():
    """30행 정확히 — 유효한 Action 반환."""
    df = _make_df(n=30)
    sig = APOStrategy().generate(df)
    assert sig.action in list(Action)


def test_29_rows_returns_hold():
    df = _make_df(n=29)
    sig = APOStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── _calc_apo 내부 함수 테스트 ────────────────────────────────────────────


def test_calc_apo_returns_four_floats():
    df = _make_df(n=35)
    apo_now, apo_prev, signal_now, signal_prev = _calc_apo(df)
    assert isinstance(apo_now, float)
    assert isinstance(apo_prev, float)
    assert isinstance(signal_now, float)
    assert isinstance(signal_prev, float)


def test_calc_apo_flat_near_zero():
    """flat 데이터 → APO ≈ 0."""
    df = _make_df(n=35)
    apo_now, _, _, _ = _calc_apo(df)
    assert abs(apo_now) < 1e-6


def test_calc_apo_rising_positive():
    """꾸준히 상승 → APO > 0 (EMA10 > EMA20)."""
    closes = [100.0 + i * 1.0 for i in range(50)]
    df = pd.DataFrame({
        "open": [c - 0.1 for c in closes],
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * 50,
        "ema50": [80.0] * 50,
        "atr14": [2.0] * 50,
    })
    apo_now, _, _, _ = _calc_apo(df)
    assert apo_now > 0


def test_calc_apo_falling_negative():
    """꾸준히 하락 → APO < 0 (EMA10 < EMA20)."""
    closes = [100.0 - i * 1.0 for i in range(50)]
    df = pd.DataFrame({
        "open": [c + 0.1 for c in closes],
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * 50,
        "ema50": [120.0] * 50,
        "atr14": [2.0] * 50,
    })
    apo_now, _, _, _ = _calc_apo(df)
    assert apo_now < 0


# ── BUY/SELL/HOLD 신호 테스트 ─────────────────────────────────────────────


def test_flat_df_returns_hold():
    df = _make_df(n=35)
    sig = APOStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_buy_entry_price_is_close():
    df = _make_bullish_cross_df()
    sig = APOStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_sell_entry_price_is_close():
    df = _make_bearish_cross_df()
    sig = APOStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


# ── Confidence 레벨 테스트 ────────────────────────────────────────────────


def test_non_hold_confidence_valid():
    """BUY/SELL 신호는 MEDIUM 또는 HIGH."""
    for df in [_make_bullish_cross_df(), _make_bearish_cross_df(), _make_strong_apo_df()]:
        sig = APOStrategy().generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_hold_confidence_low():
    df = _make_df(n=35)
    sig = APOStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── bull_case / bear_case 테스트 ──────────────────────────────────────────


def test_buy_signal_has_bull_case():
    df = _make_bullish_cross_df()
    sig = APOStrategy().generate(df)
    if sig.action == Action.BUY:
        assert len(sig.bull_case) > 0


def test_sell_signal_has_bear_case():
    df = _make_bearish_cross_df()
    sig = APOStrategy().generate(df)
    if sig.action == Action.SELL:
        assert len(sig.bear_case) > 0


# ── 엣지 케이스 ────────────────────────────────────────────────────────────


def test_large_dataframe():
    df = _make_df(n=500)
    sig = APOStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_zero_close_no_crash():
    """close가 0에 가까운 경우 — ZeroDivision 없어야 함."""
    df = _make_df(n=35, close=0.0001)
    sig = APOStrategy().generate(df)
    assert isinstance(sig, Signal)
