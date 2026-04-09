"""ATRChannelStrategy 단위 테스트."""

from typing import Optional

import numpy as np
import pandas as pd
import pytest

from src.strategy.atr_channel import ATRChannelStrategy
from src.strategy.base import Action, Confidence


def _make_df(
    n: int = 40,
    close: Optional[np.ndarray] = None,
    atr: float = 2.0,
    include_atr_col: bool = True,
) -> pd.DataFrame:
    if close is None:
        close = np.linspace(100.0, 110.0, n)
    n = len(close)
    data = {
        "open": close - 0.5,
        "high": close + 1.5,
        "low": close - 1.5,
        "close": close,
        "volume": np.ones(n) * 1000,
    }
    if include_atr_col:
        data["atr14"] = np.ones(n) * atr
    return pd.DataFrame(data)


def _make_breakout_up_df(atr: float = 2.0) -> pd.DataFrame:
    """SMA20 ≈ 100, upper = 100 + 2*2 = 104. iloc[-2] close=115 → 상방 돌파."""
    n = 40
    close = np.full(n, 100.0, dtype=float)
    close[-2] = 115.0  # 상방 돌파
    close[-1] = 115.5
    return _make_df(n=n, close=close, atr=atr)


def _make_breakout_down_df(atr: float = 2.0) -> pd.DataFrame:
    """SMA20 ≈ 100, lower = 100 - 2*2 = 96. iloc[-2] close=85 → 하방 돌파."""
    n = 40
    close = np.full(n, 100.0, dtype=float)
    close[-2] = 85.0  # 하방 돌파
    close[-1] = 84.5
    return _make_df(n=n, close=close, atr=atr)


# --- 기본 ---

def test_strategy_name():
    assert ATRChannelStrategy().name == "atr_channel"


def test_hold_on_insufficient_data():
    """25행 미만 → HOLD LOW."""
    st = ATRChannelStrategy()
    df = _make_df(n=15)
    sig = st.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_on_exactly_minimum_rows():
    """정확히 25행 → 최소 요건 충족."""
    st = ATRChannelStrategy()
    df = _make_df(n=25)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# --- BUY 신호 ---

def test_buy_signal_on_upper_breakout():
    """상방 채널 돌파 시 BUY 신호."""
    st = ATRChannelStrategy()
    df = _make_breakout_up_df(atr=2.0)
    sig = st.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_high_large_breakout():
    """돌파폭 > ATR * 0.5 시 HIGH confidence."""
    st = ATRChannelStrategy()
    # atr=2, upper≈104, close=115 → 돌파폭=11 > 2*0.5=1 → HIGH
    df = _make_breakout_up_df(atr=2.0)
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_buy_confidence_medium_small_breakout():
    """돌파폭 <= ATR * 0.5 시 MEDIUM confidence."""
    st = ATRChannelStrategy()
    n = 40
    close = np.full(n, 100.0, dtype=float)
    atr_val = 10.0
    # upper = 100 + 2*10 = 120, close[-2]=121 → 돌파폭=1 < 10*0.5=5 → MEDIUM
    close[-2] = 121.0
    close[-1] = 121.5
    df = _make_df(n=n, close=close, atr=atr_val)
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


def test_buy_entry_price_equals_last_close():
    """entry_price == df['close'].iloc[-2]."""
    st = ATRChannelStrategy()
    df = _make_breakout_up_df()
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(df["close"].iloc[-2], rel=1e-6)


# --- SELL 신호 ---

def test_sell_signal_on_lower_breakout():
    """하방 채널 돌파 시 SELL 신호."""
    st = ATRChannelStrategy()
    df = _make_breakout_down_df(atr=2.0)
    sig = st.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_high_large_breakout():
    """돌파폭 > ATR * 0.5 시 HIGH confidence."""
    st = ATRChannelStrategy()
    # atr=2, lower≈96, close=85 → 돌파폭=11 > 1 → HIGH
    df = _make_breakout_down_df(atr=2.0)
    sig = st.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


# --- HOLD ---

def test_hold_inside_channel():
    """채널 내부 close → HOLD."""
    st = ATRChannelStrategy()
    # SMA20=100, atr=2, upper=104, lower=96, close[-2]=100 (채널 내)
    close = np.full(40, 100.0)
    df = _make_df(close=close, atr=2.0)
    sig = st.generate(df)
    assert sig.action == Action.HOLD


# --- Signal 필드 유효성 ---

def test_signal_fields_valid():
    st = ATRChannelStrategy()
    df = _make_df(n=40)
    sig = st.generate(df)
    assert sig.strategy == "atr_channel"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# --- atr14 컬럼 없을 때 자체 계산 폴백 ---

def test_no_atr_col_fallback():
    """atr14 컬럼 없어도 자체 계산으로 동작해야 함."""
    st = ATRChannelStrategy()
    df = _make_df(n=40, include_atr_col=False)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_multiplier_param():
    """multiplier=1.0이면 채널이 좁아져 더 쉽게 돌파."""
    st = ATRChannelStrategy(multiplier=1.0)
    # atr=2, mid≈100, upper=102. close[-2]=103 → 돌파
    n = 40
    close = np.full(n, 100.0, dtype=float)
    close[-2] = 103.0
    close[-1] = 103.5
    df = _make_df(n=n, close=close, atr=2.0)
    sig = st.generate(df)
    assert sig.action == Action.BUY
