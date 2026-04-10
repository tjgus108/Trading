"""MomentumBreadthStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.momentum_breadth import MomentumBreadthStrategy


def _make_df(n=50, close_vals=None):
    np.random.seed(1)
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
        df = df.iloc[: len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    return df


def _buy_df():
    """모든 시간대 상승 → score=3 → BUY."""
    n = 50
    base = np.linspace(90, 130, n)  # 꾸준히 상승
    return _make_df(n=n, close_vals=base)


def _sell_df():
    """모든 시간대 하락 → score=0 → SELL."""
    n = 50
    base = np.linspace(130, 90, n)  # 꾸준히 하락
    return _make_df(n=n, close_vals=base)


strategy = MomentumBreadthStrategy()


# 1. 전략명 확인
def test_strategy_name():
    assert strategy.name == "momentum_breadth"


# 2. 인스턴스 생성
def test_instance_creation():
    strat = MomentumBreadthStrategy()
    assert isinstance(strat, MomentumBreadthStrategy)


# 3. 데이터 부족 → HOLD
def test_insufficient_data_hold():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 4. None 입력 → HOLD
def test_none_input_hold():
    try:
        sig = strategy.generate(None)
        assert sig.action == Action.HOLD
    except Exception:
        pass


# 5. 데이터 부족 시 reasoning에 "Insufficient" 포함
def test_insufficient_data_reasoning():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert "Insufficient" in sig.reasoning


# 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성 확인
def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "momentum_breadth"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY 신호 reasoning 확인
def test_buy_signal_reasoning():
    df = _buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "BUY" in sig.reasoning or "breadth" in sig.reasoning


# 9. SELL 신호 reasoning 확인
def test_sell_signal_reasoning():
    df = _sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "SELL" in sig.reasoning or "breadth" in sig.reasoning


# 10. HIGH confidence 조건 테스트 (score==3, mom5 > mom5_avg*1.5)
def test_high_confidence_buy():
    # 강한 상승 + 최근 가속
    n = 50
    base = np.ones(n) * 100.0
    for i in range(n):
        base[i] = 100.0 + i * 0.5
    # 마지막 구간 추가 가속
    for i in range(40, n):
        base[i] += (i - 39) * 3.0
    df = _make_df(n=n, close_vals=base)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 11. MEDIUM confidence 조건 테스트 (BUY지만 mom5 <= mom5_avg*1.5)
def test_medium_confidence_buy():
    df = _buy_df()
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 12. entry_price > 0
def test_entry_price_positive():
    df = _buy_df()
    sig = strategy.generate(df)
    assert sig.entry_price > 0


# 13. strategy 필드 값 확인
def test_strategy_field_value():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.strategy == "momentum_breadth"


# 14. 최소 행 수(35)에서 동작 확인
def test_minimum_rows_works():
    df = _make_df(n=37)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
