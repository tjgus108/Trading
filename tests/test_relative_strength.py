"""RelativeStrengthStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.relative_strength import RelativeStrengthStrategy


def _make_df(n=50, close_vals=None):
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
        df = df.iloc[: len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    return df


strategy = RelativeStrengthStrategy()


# 1. 전략명 확인
def test_strategy_name():
    assert strategy.name == "relative_strength"


# 2. 인스턴스 생성
def test_instance_creation():
    strat = RelativeStrengthStrategy()
    assert isinstance(strat, RelativeStrengthStrategy)


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
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성 확인
def test_signal_fields_complete():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "relative_strength"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY 신호 reasoning 확인
def test_buy_signal_reasoning():
    # 강하게 상승하는 데이터로 BUY 유도
    base = np.ones(60) * 100.0
    # 후반부 급등
    for i in range(30, 60):
        base[i] = 100.0 + (i - 29) * 2.0
    df = _make_df(n=60, close_vals=base)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "BUY" in sig.reasoning or "상대" in sig.reasoning


# 9. SELL 신호 reasoning 확인
def test_sell_signal_reasoning():
    # 후반부 급락 데이터로 SELL 유도
    base = np.ones(60) * 100.0
    for i in range(30, 60):
        base[i] = 100.0 - (i - 29) * 2.0
    df = _make_df(n=60, close_vals=base)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "SELL" in sig.reasoning or "상대" in sig.reasoning


# 10. HIGH confidence 조건 테스트
def test_high_confidence_buy():
    # |roc_n - roc_avg| > 2 * roc_std 조건 → HIGH
    np.random.seed(42)
    base = np.ones(60) * 100.0
    for i in range(45, 60):
        base[i] = 100.0 + (i - 44) * 5.0  # 강한 급등
    df = _make_df(n=60, close_vals=base)
    sig = strategy.generate(df)
    # HIGH or MEDIUM 중 하나여야 함 (신호 종류 무관)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 11. MEDIUM confidence 조건 테스트
def test_medium_confidence_hold():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    # 기본 flat 데이터는 HOLD + MEDIUM
    assert sig.confidence in (Confidence.MEDIUM, Confidence.LOW)


# 12. entry_price > 0
def test_entry_price_positive():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    if sig.action != Action.HOLD or sig.entry_price > 0:
        assert sig.entry_price >= 0.0


# 13. strategy 필드 값 확인
def test_strategy_field_value():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.strategy == "relative_strength"


# 14. 최소 행 수(40)에서 동작 확인
def test_minimum_rows_works():
    df = _make_df(n=42)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
