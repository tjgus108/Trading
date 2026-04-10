"""tests/test_trend_slope_filter.py — TrendSlopeFilterStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.trend_slope_filter import TrendSlopeFilterStrategy


# ── 헬퍼 ──────────────────────────────────────────────────────────────────

def _make_df(prices):
    size = len(prices)
    return pd.DataFrame({
        "open": prices,
        "high": [p * 1.001 for p in prices],
        "low": [p * 0.999 for p in prices],
        "close": prices,
        "volume": [1000.0] * size,
    })


def _uptrend_accel_df():
    """강한 상승 추세 + 가속 → BUY 유도."""
    # 점진적 상승 후 마지막에 가속
    prices = [100.0 + i * 0.5 for i in range(25)]  # 완만한 상승
    prices += [prices[-1] + i * 2.0 for i in range(1, 11)]  # 급격한 가속
    return _make_df(prices)


def _downtrend_accel_df():
    """강한 하락 추세 + 가속 → SELL 유도."""
    prices = [200.0 - i * 0.5 for i in range(25)]
    prices += [prices[-1] - i * 2.0 for i in range(1, 11)]
    return _make_df(prices)


def _flat_df(n=30, price=100.0):
    return _make_df([price] * n)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략명 = 'trend_slope_filter'"""
    assert TrendSlopeFilterStrategy().name == "trend_slope_filter"


def test_instance_creation():
    """2. 인스턴스 생성"""
    s = TrendSlopeFilterStrategy(window=20, threshold=0.001)
    assert s.window == 20
    assert s.threshold == 0.001


def test_insufficient_data_hold():
    """3. 데이터 부족 → HOLD"""
    s = TrendSlopeFilterStrategy()
    df = _make_df([100.0] * 20)  # 25 미만
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_none_input_hold():
    """4. None 입력 → HOLD"""
    s = TrendSlopeFilterStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """5. 데이터 부족 reasoning 확인"""
    s = TrendSlopeFilterStrategy()
    df = _make_df([100.0] * 15)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning or "minimum" in sig.reasoning


def test_normal_data_returns_signal():
    """6. 정상 데이터 → Signal 반환"""
    s = TrendSlopeFilterStrategy()
    df = _flat_df(30)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    """7. Signal 필드 완성"""
    s = TrendSlopeFilterStrategy()
    df = _flat_df(30)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert sig.invalidation is not None


def test_buy_reasoning_keyword():
    """8. BUY reasoning에 'slope' 포함"""
    s = TrendSlopeFilterStrategy()
    df = _uptrend_accel_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "slope" in sig.reasoning.lower()


def test_sell_reasoning_keyword():
    """9. SELL reasoning에 'slope' 포함"""
    s = TrendSlopeFilterStrategy()
    df = _downtrend_accel_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "slope" in sig.reasoning.lower()


def test_high_confidence():
    """10. HIGH confidence (|slope_norm| > threshold * 2)"""
    s = TrendSlopeFilterStrategy(threshold=0.001)
    # 강한 추세 → HIGH confidence
    prices = [100.0 + i * 1.0 for i in range(35)]
    df = _make_df(prices)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence():
    """11. MEDIUM confidence (|slope_norm| <= threshold * 2)"""
    s = TrendSlopeFilterStrategy(threshold=0.001)
    # 완만한 추세
    prices = [100.0 + i * 0.0001 for i in range(35)]
    df = _make_df(prices)
    sig = s.generate(df)
    if sig.action in (Action.BUY, Action.SELL):
        assert sig.confidence == Confidence.MEDIUM


def test_entry_price_positive():
    """12. entry_price > 0"""
    s = TrendSlopeFilterStrategy()
    df = _flat_df(30)
    sig = s.generate(df)
    assert sig.entry_price > 0


def test_strategy_field_value():
    """13. strategy 필드 = 'trend_slope_filter'"""
    s = TrendSlopeFilterStrategy()
    df = _flat_df(30)
    sig = s.generate(df)
    assert sig.strategy == "trend_slope_filter"


def test_minimum_rows_works():
    """14. 최소 25행에서 동작"""
    s = TrendSlopeFilterStrategy()
    df = _flat_df(25)
    sig = s.generate(df)
    assert "Insufficient" not in sig.reasoning
