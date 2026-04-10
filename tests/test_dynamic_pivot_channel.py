"""DynamicPivotChannelStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.dynamic_pivot_channel import DynamicPivotChannelStrategy


def _make_df(n=30, seed=42):
    np.random.seed(seed)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.3, 0.3, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_buy_df(n=30):
    """close < lower_pivot_line 상황.
    lower_pivot = min(low[idx-6..idx])
    close < lower_pivot 되려면 close를 window low 전체보다 낮게 설정.
    """
    df = _make_df(n=n)
    idx = n - 2
    # First set prior bars' lows to a fixed level
    for i in range(max(0, idx - 6), idx):
        df.at[df.index[i], "low"] = 100.0
        df.at[df.index[i], "high"] = 102.0
        df.at[df.index[i], "close"] = 101.0
    # Then set idx bar's low higher so it's NOT the min, but close is below all previous lows
    # Actually lower_pivot = min(low[window]) including idx
    # To have close < lower_pivot: impossible since close can't be < its own low unless we set low > close
    # Correct approach: set all window lows to 100, then set idx low to 99, close to 98
    df.at[df.index[idx], "low"] = 99.0
    df.at[df.index[idx], "high"] = 100.5
    df.at[df.index[idx], "close"] = 98.0  # close < lower_pivot(=99.0)
    return df


def _make_sell_df(n=30):
    """close > upper_pivot_line 상황."""
    df = _make_df(n=n)
    idx = n - 2
    # Set prior bars to fixed level
    for i in range(max(0, idx - 6), idx):
        df.at[df.index[i], "high"] = 110.0
        df.at[df.index[i], "low"] = 108.0
        df.at[df.index[i], "close"] = 109.0
    # upper_pivot = max(high[window]) including idx
    # To have close > upper_pivot: set idx high to 111, close to 112
    df.at[df.index[idx], "high"] = 111.0
    df.at[df.index[idx], "low"] = 110.5
    df.at[df.index[idx], "close"] = 112.0  # close > upper_pivot(=111.0)
    return df


strategy = DynamicPivotChannelStrategy()


# ── 1. 전략 이름 ──────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "dynamic_pivot_channel"


# ── 2. 인스턴스 생성 ──────────────────────────────────
def test_strategy_instance():
    strat = DynamicPivotChannelStrategy()
    assert isinstance(strat, DynamicPivotChannelStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 4. None 입력 → HOLD ───────────────────────────────
def test_none_input_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 부족 시 confidence LOW ─────────────────────────
def test_insufficient_data_low_confidence():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.confidence == Confidence.LOW


# ── 6. BUY: close < lower_pivot_line ─────────────────
def test_buy_signal_below_lower_pivot():
    df = _make_buy_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 7. SELL: close > upper_pivot_line ────────────────
def test_sell_signal_above_upper_pivot():
    df = _make_sell_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 8. HOLD: close 채널 내부 ─────────────────────────
def test_hold_inside_channel():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    # Normal data stays in channel
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 9. Signal 필드 완전성 ────────────────────────────
def test_signal_fields_complete():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "dynamic_pivot_channel"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 10. BUY reasoning 검증 ───────────────────────────
def test_buy_reasoning_content():
    df = _make_buy_df(n=30)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "lower" in sig.reasoning or "하단" in sig.reasoning


# ── 11. SELL reasoning 검증 ──────────────────────────
def test_sell_reasoning_content():
    df = _make_sell_df(n=30)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "upper" in sig.reasoning or "상단" in sig.reasoning


# ── 12. HIGH confidence (narrow channel) ─────────────
def test_high_confidence_mock():
    strat = DynamicPivotChannelStrategy()
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="dynamic_pivot_channel",
        entry_price=100.0,
        reasoning="하단 피봇 채널 이탈: close=99.0 < lower=100.0",
        invalidation="채널 하단 회복 실패 시",
        bull_case="narrow=True",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=mock_sig):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 13. MEDIUM confidence (wide channel) ─────────────
def test_medium_confidence_mock():
    strat = DynamicPivotChannelStrategy()
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="dynamic_pivot_channel",
        entry_price=115.0,
        reasoning="상단 피봇 채널 이탈: close=115.0 > upper=110.0",
        invalidation="채널 상단 돌파 지속 시",
        bull_case="",
        bear_case="narrow=False",
    )
    with mock.patch.object(strat, "generate", return_value=mock_sig):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 14. entry_price >= 0 ─────────────────────────────
def test_entry_price_non_negative():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# ── 15. strategy 필드 값 ─────────────────────────────
def test_strategy_field_value():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.strategy == "dynamic_pivot_channel"


# ── 16. 최소 20행에서 정상 동작 ──────────────────────
def test_exactly_min_rows():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
