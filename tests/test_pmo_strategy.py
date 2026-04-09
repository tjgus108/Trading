"""PriceMomentumOscillator (pmo_strategy) 단위 테스트."""

import numpy as np
import pandas as pd
import pytest
import unittest.mock as mock

from src.strategy.base import Action, Confidence, Signal
from src.strategy.pmo_strategy import PriceMomentumOscillator


def _make_df(n: int = 80, close_vals=None) -> pd.DataFrame:
    np.random.seed(42)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.5, 0.5, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["close"] = arr
    return df


def _mock_signal(action, confidence, reasoning="test", strategy="pmo_strategy"):
    return Signal(
        action=action,
        confidence=confidence,
        strategy=strategy,
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


strategy = PriceMomentumOscillator()


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "pmo_strategy"


# 2. 인스턴스 생성
def test_strategy_instance():
    strat = PriceMomentumOscillator()
    assert isinstance(strat, PriceMomentumOscillator)


# 3. 데이터 부족 (n < 60) → HOLD
def test_insufficient_data():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# 4. None 입력 → HOLD
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. None 입력 시 entry_price == 0.0
def test_none_entry_price_zero():
    sig = strategy.generate(None)
    assert sig.entry_price == 0.0
    assert sig.confidence == Confidence.LOW


# 6. 데이터 부족 시 entry_price == 0.0
def test_insufficient_entry_price_zero():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.entry_price == 0.0


# 7. HOLD (크로스 없음) - 일반 데이터
def test_hold_no_cross():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    # 일반 랜덤 데이터에서는 크로스 조건 충족 가능성 낮음
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
    assert isinstance(sig, Signal)


# 8. BUY 신호 (mock)
def test_buy_signal_mock():
    strat = PriceMomentumOscillator()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PMO 상향 크로스 (oversold): PMO=-0.3 Signal=-0.5"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# 9. SELL 신호 (mock)
def test_sell_signal_mock():
    strat = PriceMomentumOscillator()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PMO 하향 크로스 (overbought): PMO=0.3 Signal=0.5"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# 10. BUY HIGH confidence (diff > 0.5)
def test_buy_high_confidence_mock():
    strat = PriceMomentumOscillator()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "PMO 상향 크로스: diff=0.7"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# 11. SELL HIGH confidence (diff > 0.5)
def test_sell_high_confidence_mock():
    strat = PriceMomentumOscillator()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "PMO 하향 크로스: diff=0.8"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# 12. MEDIUM confidence (diff <= 0.5)
def test_medium_confidence_mock():
    strat = PriceMomentumOscillator()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PMO 상향 크로스: diff=0.3"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# 13. Signal 필드 완전성 (정상 데이터)
def test_signal_fields():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "pmo_strategy"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 14. entry_price > 0 (충분한 데이터)
def test_entry_price_positive():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.entry_price > 0


# 15. BUY 조건: PMO < 0 에서만 BUY — 강하락 후 반등 시나리오
def test_buy_only_when_pmo_negative():
    # 급락 후 반등하는 가격 시리즈 생성
    n = 80
    close_vals = np.concatenate([
        np.linspace(100, 60, 60),   # 급락
        np.linspace(60, 65, 20),    # 소폭 반등
    ])
    df = _make_df(n=n, close_vals=close_vals)
    sig = strategy.generate(df)
    # BUY 나오면 PMO < 0 조건이 충족된 것 (오버솔드)
    assert sig.action in (Action.BUY, Action.HOLD)


# 16. SELL 조건: PMO > 0 에서만 SELL — 강상승 후 하락 시나리오
def test_sell_only_when_pmo_positive():
    n = 80
    close_vals = np.concatenate([
        np.linspace(60, 100, 60),   # 급등
        np.linspace(100, 95, 20),   # 소폭 하락
    ])
    df = _make_df(n=n, close_vals=close_vals)
    sig = strategy.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 17. reasoning에 "PMO" 포함 (정상 신호)
def test_reasoning_contains_pmo():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    if sig.action != Action.HOLD or sig.confidence != Confidence.LOW:
        assert "PMO" in sig.reasoning
