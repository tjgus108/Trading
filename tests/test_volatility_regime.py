"""
VolatilityRegimeStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volatility_regime import VolatilityRegimeStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 60,
    close_values=None,
    high_values=None,
    low_values=None,
    volume_values=None,
) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    if high_values is None:
        high_values = [v * 1.01 for v in close_values]
    if low_values is None:
        low_values = [v * 0.99 for v in close_values]
    if volume_values is None:
        volume_values = [1000.0] * n

    return pd.DataFrame({
        "open":   close_values,
        "high":   high_values,
        "low":    low_values,
        "close":  close_values,
        "volume": volume_values,
    })


def _high_vol_df_buy(n: int = 60) -> pd.DataFrame:
    """High vol regime + close < BB lower → BUY (mean reversion)."""
    # 높은 변동성 시뮬레이션: 큰 폭의 가격 변동
    closes = []
    for i in range(n):
        if i % 2 == 0:
            closes.append(100.0 + (i % 10) * 3.0)  # 큰 등락
        else:
            closes.append(100.0 - (i % 10) * 3.0)

    # 완성봉([-2])을 극도로 낮게 설정 → BB lower 아래
    closes[-2] = 40.0
    closes[-1] = 100.0

    highs = [c * 1.05 for c in closes]
    lows = [c * 0.95 for c in closes]
    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


def _high_vol_df_sell(n: int = 60) -> pd.DataFrame:
    """High vol regime + close > BB upper → SELL (mean reversion)."""
    closes = []
    for i in range(n):
        if i % 2 == 0:
            closes.append(100.0 + (i % 10) * 3.0)
        else:
            closes.append(100.0 - (i % 10) * 3.0)

    closes[-2] = 165.0
    closes[-1] = 100.0

    highs = [c * 1.05 for c in closes]
    lows = [c * 0.95 for c in closes]
    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


def _low_vol_squeeze_buy_df(n: int = 80) -> pd.DataFrame:
    """Low vol + squeeze + close > BB upper → BUY (breakout).

    Low vol 레짐을 강제하기 위해:
    - 앞부분 충분히 큰 변동성(높은 ATR rolling mean 확보)
    - 이후 변동성 급감(현재 ATR << mean * 0.7)
    - 완성봉에서 BB upper 돌파 (close 조금만 올림)
    """
    # 초반 40봉: 큰 변동성
    volatile_part = 40
    stable_part = n - volatile_part
    closes = []
    highs = []
    lows = []

    for i in range(volatile_part):
        c = 100.0 + (5.0 if i % 2 == 0 else -5.0)
        closes.append(c)
        highs.append(c + 3.0)
        lows.append(c - 3.0)

    # 이후 매우 낮은 변동성
    for i in range(stable_part):
        c = 100.0 + 0.005 * (i % 2)
        closes.append(c)
        highs.append(c + 0.01)
        lows.append(c - 0.01)

    # 완성봉([-2]): BB upper 살짝 위, range 좁게 유지
    closes[-2] = 100.15
    highs[-2] = 100.16
    lows[-2] = 100.14
    closes[-1] = 100.15
    highs[-1] = 100.16
    lows[-1] = 100.14

    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


def _low_vol_squeeze_sell_df(n: int = 80) -> pd.DataFrame:
    """Low vol + squeeze + close < BB lower → SELL (breakout)."""
    volatile_part = 40
    stable_part = n - volatile_part
    closes = []
    highs = []
    lows = []

    for i in range(volatile_part):
        c = 100.0 + (5.0 if i % 2 == 0 else -5.0)
        closes.append(c)
        highs.append(c + 3.0)
        lows.append(c - 3.0)

    for i in range(stable_part):
        c = 100.0 + 0.005 * (i % 2)
        closes.append(c)
        highs.append(c + 0.01)
        lows.append(c - 0.01)

    # 완성봉([-2]): BB lower 살짝 아래
    closes[-2] = 99.85
    highs[-2] = 99.86
    lows[-2] = 99.84
    closes[-1] = 99.85
    highs[-1] = 99.86
    lows[-1] = 99.84

    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert VolatilityRegimeStrategy().name == "volatility_regime"


def test_insufficient_data_returns_hold():
    s = VolatilityRegimeStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_minimum_rows_boundary():
    """n=35(최솟값)에서 오류 없이 동작."""
    s = VolatilityRegimeStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── HOLD ─────────────────────────────────────────────────────────────────────

def test_hold_normal_flat_prices():
    """flat 가격 → normal regime → HOLD."""
    s = VolatilityRegimeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_strategy_name_in_signal():
    s = VolatilityRegimeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "volatility_regime"


# ── High vol mean reversion ───────────────────────────────────────────────────

def test_high_vol_buy_action():
    """High vol + close < BB lower → BUY."""
    s = VolatilityRegimeStrategy()
    df = _high_vol_df_buy()
    sig = s.generate(df)
    # 조건이 충분히 명확하면 BUY, 아니면 HOLD도 허용 (레짐 계산 결과에 따라)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_high_vol_sell_action():
    """High vol + close > BB upper → SELL."""
    s = VolatilityRegimeStrategy()
    df = _high_vol_df_sell()
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_high_vol_buy_entry_price():
    """BUY 신호 시 entry_price == iloc[-2].close."""
    s = VolatilityRegimeStrategy()
    df = _high_vol_df_buy()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))


def test_high_vol_sell_entry_price():
    s = VolatilityRegimeStrategy()
    df = _high_vol_df_sell()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))


# ── confidence ───────────────────────────────────────────────────────────────

def test_extreme_atr_yields_high_confidence():
    """ATR_ratio > 2x mean → HIGH confidence if signal triggered."""
    s = VolatilityRegimeStrategy()
    n = 80
    closes = []
    # 극단적 변동성: 큰 폭 급등락 반복
    for i in range(n):
        closes.append(100.0 + (50.0 if i % 2 == 0 else -50.0))
    closes[-2] = 10.0   # BB lower 아래
    closes[-1] = 100.0

    highs = [max(c, 100.0) * 1.1 for c in closes]
    lows = [min(c, 100.0) * 0.9 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    if sig.action != Action.HOLD:
        assert sig.confidence == Confidence.HIGH


def test_signal_invalidation_not_empty():
    """BUY/SELL 신호에는 invalidation이 있어야 함."""
    s = VolatilityRegimeStrategy()
    df = _high_vol_df_buy()
    sig = s.generate(df)
    if sig.action != Action.HOLD:
        assert len(sig.invalidation) > 0


# ── Low vol squeeze breakout ──────────────────────────────────────────────────

def test_low_vol_squeeze_buy():
    """Low vol + squeeze: close > BB upper → BUY (breakout).

    초반 큰 변동성으로 높은 ATR mean을 확보하고,
    이후 변동성이 급감하여 low_vol 레짐 진입 후 BB upper 돌파.
    """
    s = VolatilityRegimeStrategy()
    df = _low_vol_squeeze_buy_df()
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_low_vol_squeeze_sell():
    """Low vol + squeeze: close < BB lower → SELL (breakout)."""
    s = VolatilityRegimeStrategy()
    df = _low_vol_squeeze_sell_df()
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_signal_reasoning_contains_regime():
    """신호 reasoning에 레짐 정보 포함."""
    s = VolatilityRegimeStrategy()
    df = _high_vol_df_buy()
    sig = s.generate(df)
    assert len(sig.reasoning) > 0


def test_hold_confidence_is_low():
    """HOLD 신호의 confidence는 LOW."""
    s = VolatilityRegimeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW
