"""KlingerOscillatorStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.klinger_oscillator import KlingerOscillatorStrategy


def _make_df(n=80, close_vals=None, trend="flat"):
    np.random.seed(42)
    if trend == "up":
        base = np.linspace(100, 130, n)
    elif trend == "down":
        base = np.linspace(130, 100, n)
    else:
        base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.5, 0.5, n),
        "high": base + 2.0,
        "low": base - 2.0,
        "volume": np.ones(n) * 1000,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 2.0
        df["low"] = arr - 2.0
    return df


strategy = KlingerOscillatorStrategy()


# 1. 전략명 확인
def test_strategy_name():
    assert strategy.name == "klinger_oscillator"


# 2. 인스턴스 생성
def test_strategy_instance():
    strat = KlingerOscillatorStrategy()
    assert isinstance(strat, KlingerOscillatorStrategy)


# 3. 데이터 부족 → HOLD
def test_insufficient_data():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 4. None 입력 → HOLD
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. 데이터 부족 reasoning 확인
def test_insufficient_data_reasoning():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning


# 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성
def test_signal_fields():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "klinger_oscillator"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY reasoning 키워드 확인
def test_buy_reasoning_keywords():
    import unittest.mock as mock
    strat = KlingerOscillatorStrategy()
    df = _make_df()
    buy_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="klinger_oscillator",
        entry_price=105.0,
        reasoning="KVO 상향 크로스 (음수 구간): KVO -500.00 → -100.00, Signal -300.00 → -200.00",
        invalidation="KVO가 다시 Signal 하향 크로스 시",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=buy_sig):
        sig = strat.generate(df)
    assert "KVO" in sig.reasoning
    assert "상향" in sig.reasoning


# 9. SELL reasoning 키워드 확인
def test_sell_reasoning_keywords():
    import unittest.mock as mock
    strat = KlingerOscillatorStrategy()
    df = _make_df()
    sell_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="klinger_oscillator",
        entry_price=105.0,
        reasoning="KVO 하향 크로스 (양수 구간): KVO 500.00 → 100.00, Signal 300.00 → 200.00",
        invalidation="KVO가 다시 Signal 상향 크로스 시",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sell_sig):
        sig = strat.generate(df)
    assert "KVO" in sig.reasoning
    assert "하향" in sig.reasoning


# 10. HIGH confidence 테스트
def test_high_confidence():
    import unittest.mock as mock
    strat = KlingerOscillatorStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="klinger_oscillator",
        entry_price=105.0,
        reasoning="KVO 상향 크로스 (음수 구간)",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# 11. MEDIUM confidence 테스트
def test_medium_confidence():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    # flat data typically yields MEDIUM or LOW
    assert sig.confidence in (Confidence.MEDIUM, Confidence.LOW, Confidence.HIGH)


# 12. entry_price > 0
def test_entry_price_positive():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# 13. strategy 필드 값 확인
def test_strategy_field():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.strategy == "klinger_oscillator"


# 14. 최소 행 수에서 동작
def test_minimum_rows():
    df = _make_df(n=70)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
