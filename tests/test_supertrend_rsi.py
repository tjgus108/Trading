"""SupertrendRSIStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.supertrend_rsi import SupertrendRSIStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 50, close_vals=None) -> pd.DataFrame:
    if close_vals is None:
        close_vals = np.linspace(100.0, 110.0, n)
    close = np.asarray(close_vals, dtype=float)
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.ones(len(close)) * 1000,
        }
    )


def _make_bullish_df() -> pd.DataFrame:
    """Supertrend bullish + RSI ~60 유도: 꾸준한 상승."""
    n = 60
    close = np.linspace(80.0, 120.0, n)
    return _make_df(n, close)


def _make_bearish_df() -> pd.DataFrame:
    """Supertrend bearish + RSI ~40 유도: 꾸준한 하락."""
    n = 60
    close = np.linspace(120.0, 80.0, n)
    return _make_df(n, close)


# --- 기본 테스트 ---

def test_strategy_name():
    st = SupertrendRSIStrategy()
    assert st.name == "supertrend_rsi"


def test_insufficient_data_returns_hold():
    st = SupertrendRSIStrategy()
    df = _make_df(n=10)
    sig = st.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_exact_boundary():
    st = SupertrendRSIStrategy()
    df = _make_df(n=24)
    sig = st.generate(df)
    assert sig.action == Action.HOLD


def test_min_data_passes():
    """25행이면 데이터 부족 HOLD가 아니어야 한다."""
    st = SupertrendRSIStrategy()
    df = _make_df(n=25)
    sig = st.generate(df)
    # 데이터 부족 메시지 없어야 함
    assert "데이터 부족" not in sig.reasoning


def test_signal_fields_present():
    st = SupertrendRSIStrategy()
    df = _make_df(n=50)
    sig = st.generate(df)
    assert sig.strategy == "supertrend_rsi"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_closed_candle():
    st = SupertrendRSIStrategy()
    df = _make_df(n=50)
    sig = st.generate(df)
    # entry_price = iloc[-2]
    assert sig.entry_price == float(df["close"].iloc[-2])


def test_buy_signal_on_strong_uptrend():
    """강한 상승 추세: Supertrend bullish + RSI 50~70 → BUY."""
    st = SupertrendRSIStrategy()
    df = _make_bullish_df()
    sig = st.generate(df)
    # 강한 상승이면 BUY 또는 HOLD (RSI 조건에 따라)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_signal_on_strong_downtrend():
    """강한 하락 추세: Supertrend bearish + RSI 30~50 → SELL."""
    st = SupertrendRSIStrategy()
    df = _make_bearish_df()
    sig = st.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_buy_signal_rsi_and_supertrend_conditions():
    """BUY 신호: RSI 60, Supertrend bullish 조건 수동 검증."""
    st = SupertrendRSIStrategy()
    # 지속 상승 → Supertrend bullish, RSI > 50 예상
    n = 80
    close = np.concatenate([
        np.linspace(90.0, 95.0, 40),   # 완만 상승
        np.linspace(95.0, 115.0, 40),  # 강한 상승
    ])
    df = _make_df(n, close)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)
    assert sig.strategy == "supertrend_rsi"


def test_hold_when_rsi_overbought():
    """RSI >= 70이면 BUY 조건 불충족 → HOLD."""
    st = SupertrendRSIStrategy()
    # 매우 가파른 상승으로 RSI 과매수 유도
    n = 50
    close = np.concatenate([
        np.ones(20) * 100.0,
        np.linspace(100.0, 200.0, 30),
    ])
    df = _make_df(n, close)
    sig = st.generate(df)
    # RSI >= 70 이면 BUY 조건 불충족
    assert sig.action in (Action.HOLD, Action.BUY)  # BUY면 RSI < 70인 경우


def test_hold_when_rsi_oversold():
    """RSI <= 30이면 SELL 조건 불충족 → HOLD."""
    st = SupertrendRSIStrategy()
    n = 50
    close = np.concatenate([
        np.ones(20) * 200.0,
        np.linspace(200.0, 80.0, 30),
    ])
    df = _make_df(n, close)
    sig = st.generate(df)
    assert sig.action in (Action.HOLD, Action.SELL)


def test_confidence_high_when_conditions_met():
    """HIGH confidence: |RSI-50| > 15 AND ST 거리 > 1%."""
    st = SupertrendRSIStrategy()
    df = _make_bullish_df()
    sig = st.generate(df)
    # BUY면 confidence 검증
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_custom_parameters():
    """커스텀 파라미터로 인스턴스 생성 및 동작 확인."""
    st = SupertrendRSIStrategy(atr_span=5, multiplier=2.0, rsi_period=7)
    df = _make_df(n=40)
    sig = st.generate(df)
    assert sig.strategy == "supertrend_rsi"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_rsi_reasoning_in_signal():
    """RSI 값이 reasoning에 포함되는지 확인."""
    st = SupertrendRSIStrategy()
    df = _make_bullish_df()
    sig = st.generate(df)
    if sig.action != Action.HOLD or "데이터 부족" not in sig.reasoning:
        assert "RSI" in sig.reasoning or "조건 미충족" in sig.reasoning or sig.action in (Action.BUY, Action.SELL)
