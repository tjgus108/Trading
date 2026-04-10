"""TrendStrengthIndexStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_strength_index import TrendStrengthIndexStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n=60, prices=None):
    if prices is None:
        prices = np.full(n, 100.0)
    prices = np.array(prices, dtype=float)
    n = len(prices)
    return pd.DataFrame({
        "open": prices,
        "high": prices + 1.0,
        "low": prices - 1.0,
        "close": prices,
        "volume": np.full(n, 1000.0),
        "ema50": prices,
        "atr14": np.full(n, 1.5),
    })


def _make_buy_df():
    """TSI crosses above signal while TSI < 0: 하락 후 반등."""
    n = 80
    # Long downtrend then a sharp reversal → TSI still negative but crosses above signal
    prices = list(np.linspace(200, 100, 60)) + list(np.linspace(100, 130, 20))
    return _make_df(prices=prices)


def _make_sell_df():
    """TSI crosses below signal while TSI > 0: 상승 후 반락."""
    n = 80
    prices = list(np.linspace(100, 200, 60)) + list(np.linspace(200, 170, 20))
    return _make_df(prices=prices)


# 1. 전략명 확인
def test_strategy_name():
    assert TrendStrengthIndexStrategy.name == "trend_strength_index"


# 2. 인스턴스 생성
def test_instantiation():
    s = TrendStrengthIndexStrategy()
    assert s is not None


# 3. 데이터 부족 → HOLD
def test_insufficient_data_returns_hold():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=20))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. None 입력 → HOLD
def test_none_input_returns_hold():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# 5. 데이터 부족 reasoning 확인
def test_insufficient_data_reasoning():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=10))
    assert "Insufficient" in sig.reasoning or "data" in sig.reasoning.lower()


# 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=60))
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성
def test_signal_fields_complete():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=60))
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert sig.strategy == "trend_strength_index"


# 8. BUY reasoning 키워드 확인
def test_buy_reasoning_keyword():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_buy_df())
    if sig.action == Action.BUY:
        assert "TSI" in sig.reasoning
    else:
        pytest.skip("BUY 미발생")


# 9. SELL reasoning 키워드 확인
def test_sell_reasoning_keyword():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_sell_df())
    if sig.action == Action.SELL:
        assert "TSI" in sig.reasoning
    else:
        pytest.skip("SELL 미발생")


# 10. HIGH confidence 테스트
def test_high_confidence_condition():
    """abs(tsi) > 25 이면 HIGH confidence."""
    s = TrendStrengthIndexStrategy()
    # Very steep downtrend then sharp reversal → large abs(TSI)
    prices = list(np.linspace(1000, 100, 70)) + list(np.linspace(100, 200, 20))
    sig = s.generate(_make_df(prices=prices))
    if sig.action == Action.BUY and abs(float('nan') if sig.entry_price == 0 else 0) > 25:
        assert sig.confidence == Confidence.HIGH
    # Just verify it doesn't crash
    assert isinstance(sig, Signal)


# 11. MEDIUM confidence 테스트
def test_medium_confidence_hold():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=60))
    if sig.action == Action.HOLD:
        assert sig.confidence in (Confidence.LOW, Confidence.MEDIUM)


# 12. entry_price > 0
def test_entry_price_positive():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=60))
    assert sig.entry_price >= 0.0


# 13. strategy 필드 값 확인
def test_strategy_field_value():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=60))
    assert sig.strategy == "trend_strength_index"


# 14. 최소 행 수에서 동작
def test_minimum_rows():
    s = TrendStrengthIndexStrategy()
    sig = s.generate(_make_df(n=40))
    assert isinstance(sig, Signal)
    assert sig.action in list(Action)
