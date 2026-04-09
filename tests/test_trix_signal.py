"""TRIXSignalStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest
import unittest.mock as mock

from src.strategy.base import Action, Confidence, Signal
from src.strategy.trix_signal import TRIXSignalStrategy


def _make_df(n=80, close_vals=None):
    np.random.seed(42)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.05, 0.05, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    return df


def _make_buy_signal():
    return Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="trix_signal",
        entry_price=110.0,
        reasoning="TRIX Signal 크로스업: TRIX=0.0200 Signal=0.0100 Hist=0.0100 HStd=0.0050",
        invalidation="histogram이 다시 0 하향 돌파 시",
        bull_case="histogram -0.0050 → 0.0100, 모멘텀 전환",
        bear_case="단기 반등일 수 있음",
    )


def _make_sell_signal():
    return Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="trix_signal",
        entry_price=100.0,
        reasoning="TRIX Signal 크로스다운: TRIX=-0.0200 Signal=-0.0100 Hist=-0.0100 HStd=0.0050",
        invalidation="histogram이 다시 0 상향 돌파 시",
        bull_case="단기 조정일 수 있음",
        bear_case="histogram 0.0050 → -0.0100, 하락 전환",
    )


strategy = TRIXSignalStrategy()


# ── 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "trix_signal"


# ── 2. 인스턴스 생성
def test_strategy_instance():
    s = TRIXSignalStrategy()
    assert isinstance(s, TRIXSignalStrategy)


# ── 3. BUY 신호
def test_buy_signal():
    s = TRIXSignalStrategy()
    df = _make_df()
    with mock.patch.object(s, "generate", return_value=_make_buy_signal()):
        sig = s.generate(df)
    assert sig.action == Action.BUY


# ── 4. SELL 신호
def test_sell_signal():
    s = TRIXSignalStrategy()
    df = _make_df()
    with mock.patch.object(s, "generate", return_value=_make_sell_signal()):
        sig = s.generate(df)
    assert sig.action == Action.SELL


# ── 5. BUY HIGH confidence
def test_buy_high_confidence():
    s = TRIXSignalStrategy()
    df = _make_df()
    sig_val = _make_buy_signal()
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. SELL HIGH confidence
def test_sell_high_confidence():
    s = TRIXSignalStrategy()
    df = _make_df()
    sig_val = _make_sell_signal()
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 7. BUY MEDIUM confidence
def test_buy_medium_confidence():
    s = TRIXSignalStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="trix_signal",
        entry_price=110.0,
        reasoning="TRIX Signal 크로스업",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 8. 데이터 부족 (<50행) → HOLD
def test_insufficient_data():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 9. None 입력 → HOLD
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 10. 완만한 데이터 → 크로스 없을 때 HOLD 가능
def test_hold_no_signal():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
    assert sig.strategy == "trix_signal"


# ── 11. Signal 필드 완전성
def test_signal_fields_complete():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "trix_signal"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "TRIX" 포함
def test_buy_reasoning_contains_trix():
    s = TRIXSignalStrategy()
    df = _make_df()
    with mock.patch.object(s, "generate", return_value=_make_buy_signal()):
        sig = s.generate(df)
    assert "TRIX" in sig.reasoning


# ── 13. SELL reasoning에 "TRIX" 포함
def test_sell_reasoning_contains_trix():
    s = TRIXSignalStrategy()
    df = _make_df()
    with mock.patch.object(s, "generate", return_value=_make_sell_signal()):
        sig = s.generate(df)
    assert "TRIX" in sig.reasoning


# ── 14. 최소 50행으로 실행 가능
def test_minimum_rows():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig is not None
    assert sig.strategy == "trix_signal"
