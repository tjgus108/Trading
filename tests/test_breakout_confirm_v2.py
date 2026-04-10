"""tests/test_breakout_confirm_v2.py — BreakoutConfirmV2Strategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.breakout_confirm_v2 import BreakoutConfirmV2Strategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50, price: float = 100.0) -> pd.DataFrame:
    closes = np.full(n, price)
    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + 1.0,
        "low": closes - 1.0,
        "volume": np.ones(n) * 1000.0,
    })


def _make_buy_df(vol_multiplier: float = 1.5) -> pd.DataFrame:
    """
    BUY 조건: close > resistance, volume > vol_ma20*1.3, close > close.shift(3)
    resistance = high.rolling(20).max().shift(1)
    Base: closes=100, highs=101 → resistance at idx=48: max of highs[28:48]=101
    Set close[48]=102 (> 101), volume high, close[48]>close[45]

    For HIGH confidence: volume[48] > vol_ma20*2.0
    vol_ma20 at idx=48 = mean(volumes[29:49]).
    If volumes[0:48]=base and volumes[48]=X, then vol_ma20 ≈ mean(volumes[29:49])
    = (19*base + X) / 20. We need X > vol_ma20*2.0.
    Solve: X > ((19*base + X)/20)*2 → 20X > 2*(19*base + X) → 18X > 38*base
    → X > 38*base/18 ≈ 2.11*base.
    So for HIGH, vol_multiplier=2.5 ensures X=2500 > vol_ma20*2.0
    with vol_ma20=(19*1000+2500)/20=1075, threshold=2150 < 2500 ✓.
    For MEDIUM: vol_multiplier=1.5 → X=1500, vol_ma20=1025, threshold*2=2050 > 1500 ✓.
    """
    n = 50
    base_vol = 1000.0
    closes = np.full(n, 100.0)
    highs = closes + 1.0
    lows = closes - 1.0
    volumes = np.full(n, base_vol)

    closes[48] = 102.0
    closes[49] = 102.0
    highs[48] = 103.0
    lows[48] = 101.5
    volumes[48] = base_vol * vol_multiplier

    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


def _make_sell_df(vol_multiplier: float = 1.5) -> pd.DataFrame:
    """
    SELL 조건: close < support, volume > vol_ma20*1.3, close < close.shift(3)
    """
    n = 50
    base_vol = 1000.0
    closes = np.full(n, 100.0)
    highs = closes + 1.0
    lows = closes - 1.0
    volumes = np.full(n, base_vol)

    closes[48] = 98.0
    closes[49] = 98.0
    lows[48] = 97.5
    highs[48] = 98.5
    volumes[48] = base_vol * vol_multiplier

    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────
def test_strategy_name():
    assert BreakoutConfirmV2Strategy.name == "breakout_confirm_v2"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────
def test_instantiation():
    s = BreakoutConfirmV2Strategy()
    assert isinstance(s, BreakoutConfirmV2Strategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────
def test_insufficient_data_returns_hold():
    df = _make_df(n=20)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────
def test_none_input_returns_hold():
    sig = BreakoutConfirmV2Strategy().generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────
def test_insufficient_data_reasoning():
    df = _make_df(n=10)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────
def test_normal_data_returns_signal():
    df = _make_df(n=50)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────
def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.strategy == "breakout_confirm_v2"
    assert isinstance(sig.entry_price, float)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────
def test_buy_reasoning_keyword():
    df = _make_buy_df(vol_multiplier=1.5)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.action == Action.BUY
    assert "breakout" in sig.reasoning.lower()


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────
def test_sell_reasoning_keyword():
    df = _make_sell_df(vol_multiplier=1.5)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.action == Action.SELL
    assert "breakdown" in sig.reasoning.lower()


# ── 10. HIGH confidence 테스트 (volume > vol_ma20 * 2.0) ─────────────────
def test_high_confidence_high_volume():
    # vol_multiplier=2.5: volume[48]=2500, vol_ma20≈1075, threshold=2150 < 2500 → HIGH
    df = _make_buy_df(vol_multiplier=2.5)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 11. MEDIUM confidence 테스트 (volume 1.3~2.0x) ───────────────────────
def test_medium_confidence_moderate_volume():
    # vol_multiplier=1.5: volume[48]=1500, vol_ma20≈1025, threshold*2=2050 > 1500 → MEDIUM
    df = _make_buy_df(vol_multiplier=1.5)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 12. entry_price > 0 ───────────────────────────────────────────────────
def test_entry_price_positive():
    df = _make_buy_df(vol_multiplier=1.5)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────
def test_strategy_field_value():
    df = _make_df(n=50)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert sig.strategy == "breakout_confirm_v2"


# ── 14. 최소 행 수(25)에서 동작 ──────────────────────────────────────────
def test_minimum_rows_works():
    df = _make_df(n=25)
    sig = BreakoutConfirmV2Strategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
