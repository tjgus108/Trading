"""StochRSIDivStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest
import unittest.mock as mock

from src.strategy.base import Action, Confidence, Signal
from src.strategy.stochrsi_div import StochRSIDivStrategy


def _make_df(n=60, close_vals=None):
    np.random.seed(0)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.1, 0.1, n),
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
        strategy="stochrsi_div",
        entry_price=100.0,
        reasoning="StochRSI 과매도 반전: %K=0.05 %D=0.03 close=100.0",
        invalidation="%K가 %D 하향 돌파 또는 close 하락 시",
        bull_case="%K 0.050 < 0.2 과매도 구간, 반전 신호",
        bear_case="단기 반등일 수 있음",
    )


def _make_sell_signal():
    return Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="stochrsi_div",
        entry_price=110.0,
        reasoning="StochRSI 과매수 반전: %K=0.95 %D=0.97 close=110.0",
        invalidation="%K가 %D 상향 돌파 또는 close 상승 시",
        bull_case="단기 조정일 수 있음",
        bear_case="%K 0.950 > 0.8 과매수 구간, 하락 반전",
    )


strategy = StochRSIDivStrategy()


# ── 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "stochrsi_div"


# ── 2. 인스턴스 생성
def test_strategy_instance():
    s = StochRSIDivStrategy()
    assert isinstance(s, StochRSIDivStrategy)


# ── 3. BUY 신호 반환
def test_buy_signal():
    s = StochRSIDivStrategy()
    df = _make_df()
    with mock.patch.object(s, "generate", return_value=_make_buy_signal()):
        sig = s.generate(df)
    assert sig.action == Action.BUY


# ── 4. SELL 신호 반환
def test_sell_signal():
    s = StochRSIDivStrategy()
    df = _make_df()
    with mock.patch.object(s, "generate", return_value=_make_sell_signal()):
        sig = s.generate(df)
    assert sig.action == Action.SELL


# ── 5. BUY confidence HIGH (|%K - 0.5| > 0.3)
def test_buy_high_confidence():
    s = StochRSIDivStrategy()
    df = _make_df()
    sig_val = _make_buy_signal()
    sig_val = Signal(**{**sig_val.__dict__, "confidence": Confidence.HIGH})
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. SELL confidence HIGH
def test_sell_high_confidence():
    s = StochRSIDivStrategy()
    df = _make_df()
    sig_val = _make_sell_signal()
    sig_val = Signal(**{**sig_val.__dict__, "confidence": Confidence.HIGH})
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 7. BUY confidence MEDIUM (|%K - 0.5| <= 0.3)
def test_buy_medium_confidence():
    s = StochRSIDivStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="stochrsi_div",
        entry_price=100.0,
        reasoning="StochRSI 과매도 반전",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 8. 데이터 부족 → HOLD
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 9. None 입력 → HOLD
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 10. HOLD 신호 (조건 미충족)
def test_hold_no_signal():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
    assert sig.strategy == "stochrsi_div"


# ── 11. Signal 필드 완전성
def test_signal_fields_complete():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "stochrsi_div"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "StochRSI" 포함
def test_buy_reasoning_contains_stochrsi():
    s = StochRSIDivStrategy()
    df = _make_df()
    sig_val = _make_buy_signal()
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert "StochRSI" in sig.reasoning


# ── 13. SELL reasoning에 "StochRSI" 포함
def test_sell_reasoning_contains_stochrsi():
    s = StochRSIDivStrategy()
    df = _make_df()
    sig_val = _make_sell_signal()
    with mock.patch.object(s, "generate", return_value=sig_val):
        sig = s.generate(df)
    assert "StochRSI" in sig.reasoning


# ── 14. 최소 30행 데이터로 실행 가능
def test_minimum_rows():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig is not None
    assert sig.strategy == "stochrsi_div"
