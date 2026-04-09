"""
AccelerationBandStrategy 단위 테스트
"""

import pandas as pd
import pytest

from src.strategy.acceleration_band import AccelerationBandStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, close_values=None,
             high_values=None, low_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    if high_values is None:
        high_values = [c * 1.01 for c in close_values]
    if low_values is None:
        low_values  = [c * 0.99 for c in close_values]
    df = pd.DataFrame({
        "open":   close_values,
        "high":   high_values,
        "low":    low_values,
        "close":  close_values,
        "volume": [1000.0] * n,
    })
    return df


def _make_buy_crossover_df(n: int = 40) -> pd.DataFrame:
    """
    iloc[-2]에서 upper 밴드를 상향 돌파하는 DataFrame.
    SMA20이 ~100이고 밴드폭이 작으므로 upper ≈ 100 + ε.
    [-3]: close=100 (upper 아래 또는 동일)
    [-2]: close=120 (upper 위)
    """
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0]  * n
    # [-3]: upper 이하
    closes[-3] = 100.0
    # [-2]: upper 크게 돌파
    closes[-2] = 120.0
    highs[-2]  = 121.0
    lows[-2]   = 119.0
    closes[-1] = 100.0
    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


def _make_sell_crossover_df(n: int = 40) -> pd.DataFrame:
    """
    iloc[-2]에서 lower 밴드를 하향 돌파하는 DataFrame.
    [-3]: close=100 (lower 위)
    [-2]: close=80 (lower 아래)
    """
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0]  * n
    closes[-3] = 100.0
    closes[-2] = 80.0
    highs[-2]  = 81.0
    lows[-2]   = 79.0
    closes[-1] = 100.0
    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


# ── 인스턴스 / 이름 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert AccelerationBandStrategy().name == "acceleration_band"


def test_strategy_instantiable():
    assert AccelerationBandStrategy() is not None


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = AccelerationBandStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_crash():
    s = AccelerationBandStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_crossover_signal():
    s = AccelerationBandStrategy()
    df = _make_buy_crossover_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_not_low():
    s = AccelerationBandStrategy()
    df = _make_buy_crossover_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_high_confidence_when_far_above():
    """1% 이상 돌파 → HIGH"""
    s = AccelerationBandStrategy()
    df = _make_buy_crossover_df()  # close[-2]=120, upper≈102 → 충분히 위
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_crossover_signal():
    s = AccelerationBandStrategy()
    df = _make_sell_crossover_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_not_low():
    s = AccelerationBandStrategy()
    df = _make_sell_crossover_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_high_confidence_when_far_below():
    """1% 이상 하향 돌파 → HIGH"""
    s = AccelerationBandStrategy()
    df = _make_sell_crossover_df()  # close[-2]=80, lower≈98 → 충분히 아래
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── HOLD ──────────────────────────────────────────────────────────────────────

def test_hold_when_no_crossover():
    s = AccelerationBandStrategy()
    df = _make_df(n=35)  # 모든 봉이 같아 크로스오버 없음
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = AccelerationBandStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ──────────────────────────────────────────────────────────

def test_entry_price_equals_last_close():
    s = AccelerationBandStrategy()
    df = _make_buy_crossover_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_signal_strategy_field():
    s = AccelerationBandStrategy()
    df = _make_sell_crossover_df()
    sig = s.generate(df)
    assert sig.strategy == "acceleration_band"


def test_reasoning_contains_band_info():
    s = AccelerationBandStrategy()
    df = _make_buy_crossover_df()
    sig = s.generate(df)
    assert "upper" in sig.reasoning or "lower" in sig.reasoning
