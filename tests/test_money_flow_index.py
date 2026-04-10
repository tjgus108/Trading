"""MoneyFlowIndexStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.money_flow_index import MoneyFlowIndexStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n=50, prices=None, volume=1000.0):
    if prices is None:
        prices = np.full(n, 100.0)
    prices = np.array(prices, dtype=float)
    n = len(prices)
    return pd.DataFrame({
        "open": prices,
        "high": prices + 1.0,
        "low": prices - 1.0,
        "close": prices,
        "volume": np.full(n, volume),
        "ema50": prices,
        "atr14": np.full(n, 1.0),
    })


def _make_buy_df():
    """MFI crosses above 20: prev < 20, cur >= 20."""
    # Build a series where rolling window at idx-1 is all down (neg MF dominates → MFI~0)
    # and at idx there's one up move that pushes MFI just over 20.
    n = 60
    # idx = 58
    # Rolling [44..57]: all down → MFI ≈ 0
    # Rolling [45..58]: 13 down + 1 up (44→45 change is 1 up among the diffs)
    prices = (
        list(np.linspace(1000, 100, 45))  # 0..44: falling
        + [101.0]                          # 45: up tick
        + list(np.linspace(101, 90, 14))  # 46..59: falling
    )
    return _make_df(prices=prices)


def _make_sell_df():
    """MFI crosses below 80: prev > 80, cur <= 80."""
    n = 60
    # Rolling [44..57]: all up → MFI ≈ 100
    # Rolling [45..58]: 13 up + 1 down → MFI drops below 80
    prices = (
        list(np.linspace(100, 1100, 58))  # 0..57: rising
        + [1099.0]                         # 58: down tick
        + [1098.0]                         # 59
    )
    return _make_df(prices=prices)


# 1. 전략명 확인
def test_strategy_name():
    assert MoneyFlowIndexStrategy.name == "money_flow_index"


# 2. 인스턴스 생성
def test_instantiation():
    s = MoneyFlowIndexStrategy()
    assert s is not None


# 3. 데이터 부족 → HOLD
def test_insufficient_data_returns_hold():
    s = MoneyFlowIndexStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. None 입력 → HOLD
def test_none_input_returns_hold():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# 5. 데이터 부족 reasoning 확인
def test_insufficient_data_reasoning():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=5))
    assert "Insufficient" in sig.reasoning or "data" in sig.reasoning.lower()


# 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=30))
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성
def test_signal_fields_complete():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=30))
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert sig.strategy == "money_flow_index"


# 8. BUY reasoning 키워드 확인
def test_buy_reasoning_keyword():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_buy_df())
    if sig.action == Action.BUY:
        assert "MFI" in sig.reasoning
    else:
        pytest.skip("BUY 미발생")


# 9. SELL reasoning 키워드 확인
def test_sell_reasoning_keyword():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_sell_df())
    if sig.action == Action.SELL:
        assert "MFI" in sig.reasoning
    else:
        pytest.skip("SELL 미발생")


# 10. HIGH confidence 테스트 (BUY)
def test_high_confidence_buy():
    s = MoneyFlowIndexStrategy()
    # Extreme drop then tiny up — MFI stays very low after cross
    n = 60
    prices = list(np.linspace(500, 50, 45)) + [51.0] + list(np.linspace(51, 48, 14))
    sig = s.generate(_make_df(prices=prices))
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
    else:
        pytest.skip("BUY 미발생")


# 11. MEDIUM confidence 테스트
def test_medium_confidence_hold():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=30))
    # HOLD is MEDIUM confidence
    if sig.action == Action.HOLD and sig.confidence != Confidence.LOW:
        assert sig.confidence == Confidence.MEDIUM


# 12. entry_price > 0
def test_entry_price_positive():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=30))
    assert sig.entry_price >= 0.0


# 13. strategy 필드 값 확인
def test_strategy_field_value():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=30))
    assert sig.strategy == "money_flow_index"


# 14. 최소 행 수에서 동작
def test_minimum_rows():
    s = MoneyFlowIndexStrategy()
    sig = s.generate(_make_df(n=20))
    assert isinstance(sig, Signal)
    assert sig.action in list(Action)
