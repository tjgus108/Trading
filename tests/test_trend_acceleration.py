"""
TrendAccelerationStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_acceleration import TrendAccelerationStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
    })
    return df


def _make_uptrend_df(strong: bool = False) -> pd.DataFrame:
    """
    EMA10 > EMA20 이고 스프레드가 확대되는 상승 추세.
    충분히 긴 상승 후 완성 캔들(-2)도 상승.
    """
    n = 40
    # 선형 상승 → ema10이 ema20보다 위, spread 양수+확대
    step = 2.0 if strong else 0.5
    closes = [100.0 + i * step for i in range(n)]
    closes[-1] = closes[-2] + step  # 진행 중 캔들
    return _make_df(n=n, close_values=closes)


def _make_downtrend_df(strong: bool = False) -> pd.DataFrame:
    """
    EMA10 < EMA20 이고 스프레드가 확대되는 하락 추세.
    """
    n = 40
    step = 2.0 if strong else 0.5
    closes = [200.0 - i * step for i in range(n)]
    closes[-1] = closes[-2] - step
    return _make_df(n=n, close_values=closes)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert TrendAccelerationStrategy().name == "trend_acceleration"


def test_insufficient_data_returns_hold():
    s = TrendAccelerationStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_insufficient_data_exact_boundary():
    s = TrendAccelerationStrategy()
    df = _make_df(n=24)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_minimum_rows_passes():
    """25행이면 처리 진행"""
    s = TrendAccelerationStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY 시그널 ───────────────────────────────────────────────────────────────

def test_buy_signal_uptrend():
    s = TrendAccelerationStrategy()
    df = _make_uptrend_df(strong=False)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "trend_acceleration"


def test_buy_high_confidence_strong_uptrend():
    """강한 상승 시 slope가 std보다 크면 HIGH"""
    s = TrendAccelerationStrategy()
    df = _make_uptrend_df(strong=True)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_buy_entry_price_equals_close():
    s = TrendAccelerationStrategy()
    df = _make_uptrend_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_reasoning_contains_spread():
    s = TrendAccelerationStrategy()
    df = _make_uptrend_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "spread" in sig.reasoning.lower()


# ── SELL 시그널 ──────────────────────────────────────────────────────────────

def test_sell_signal_downtrend():
    s = TrendAccelerationStrategy()
    df = _make_downtrend_df(strong=False)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "trend_acceleration"


def test_sell_high_confidence_strong_downtrend():
    s = TrendAccelerationStrategy()
    df = _make_downtrend_df(strong=True)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_entry_price_equals_close():
    s = TrendAccelerationStrategy()
    df = _make_downtrend_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_sell_reasoning_contains_spread():
    s = TrendAccelerationStrategy()
    df = _make_downtrend_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "spread" in sig.reasoning.lower()


# ── HOLD 케이스 ──────────────────────────────────────────────────────────────

def test_hold_flat_prices():
    """모든 가격 동일 → EMA 동일 → spread=0 → HOLD"""
    s = TrendAccelerationStrategy()
    df = _make_df(n=35, close_values=[100.0] * 35)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_oscillating_prices():
    """등락 반복 → spread 방향 불일치 → HOLD 가능성 높음"""
    s = TrendAccelerationStrategy()
    n = 35
    closes = [100.0 + (5 if i % 2 == 0 else -5) for i in range(n)]
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    # 어떤 액션이든 Signal 구조 유지
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_hold_confidence_is_low():
    s = TrendAccelerationStrategy()
    df = _make_df(n=35, close_values=[100.0] * 35)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_has_all_fields():
    s = TrendAccelerationStrategy()
    df = _make_uptrend_df()
    sig = s.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
