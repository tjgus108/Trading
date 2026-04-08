"""VWAPReversionStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vwap_reversion import VWAPReversionStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 60, close_val: float = 100.0, vwap_val: float = 100.0,
             rsi_val: float = 50.0) -> pd.DataFrame:
    """테스트용 DataFrame 생성. 마지막 -2 행이 신호 판단 기준."""
    close = np.full(n, close_val)
    vwap = np.full(n, vwap_val)
    rsi14 = np.full(n, rsi_val)
    return pd.DataFrame({
        "open": close - 0.5,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": np.ones(n) * 1000,
        "vwap": vwap,
        "rsi14": rsi14,
    })


# 1. 전략 이름 확인
def test_strategy_name():
    s = VWAPReversionStrategy()
    assert s.name == "vwap_reversion"


# 2. BUY 신호: close < vwap*0.995 AND rsi < 35
def test_buy_signal_medium():
    """RSI 30 (oversold but not extreme) → BUY MEDIUM."""
    s = VWAPReversionStrategy()
    # close=99.0, vwap=100.0 → 99.0 < 99.5: True; rsi=30 < 35: True
    df = _make_df(n=60, close_val=99.0, vwap_val=100.0, rsi_val=30.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# 3. BUY 신호: RSI < 25 → HIGH confidence
def test_buy_signal_high_confidence():
    """RSI 20 (extreme oversold) → BUY HIGH."""
    s = VWAPReversionStrategy()
    df = _make_df(n=60, close_val=98.0, vwap_val=100.0, rsi_val=20.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# 4. SELL 신호: close > vwap*1.005 AND rsi > 65
def test_sell_signal_medium():
    """RSI 70 (overbought but not extreme) → SELL MEDIUM."""
    s = VWAPReversionStrategy()
    # close=101.0, vwap=100.0 → 101.0 > 100.5: True; rsi=70 > 65: True
    df = _make_df(n=60, close_val=101.0, vwap_val=100.0, rsi_val=70.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# 5. SELL 신호: RSI > 75 → HIGH confidence
def test_sell_signal_high_confidence():
    """RSI 80 (extreme overbought) → SELL HIGH."""
    s = VWAPReversionStrategy()
    df = _make_df(n=60, close_val=102.0, vwap_val=100.0, rsi_val=80.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# 6. HOLD: 조건 미충족
def test_hold_signal_no_condition():
    """close≈vwap, rsi=50 → HOLD."""
    s = VWAPReversionStrategy()
    df = _make_df(n=60, close_val=100.0, vwap_val=100.0, rsi_val=50.0)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 7. HOLD: close 하방이탈이지만 RSI가 충분히 낮지 않음
def test_hold_vwap_below_rsi_not_oversold():
    """close < vwap*0.995 but rsi=40 (not < 35) → HOLD."""
    s = VWAPReversionStrategy()
    df = _make_df(n=60, close_val=99.0, vwap_val=100.0, rsi_val=40.0)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 8. 데이터 부족 시 HOLD
def test_hold_insufficient_data():
    """50행 미만 → HOLD."""
    s = VWAPReversionStrategy()
    df = _make_df(n=30, close_val=99.0, vwap_val=100.0, rsi_val=20.0)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 9. Signal 필드 검증
def test_signal_fields_present():
    """Signal 객체에 필수 필드가 모두 있는지 확인."""
    s = VWAPReversionStrategy()
    df = _make_df(n=60, close_val=99.0, vwap_val=100.0, rsi_val=30.0)
    sig = s.generate(df)
    assert sig.strategy == "vwap_reversion"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
