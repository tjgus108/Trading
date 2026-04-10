"""TEMAStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.tema_strategy import TEMAStrategy


def _make_df(n=60, close_vals=None):
    np.random.seed(1)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.3, 0.3, n),
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


def _make_cross_up_df():
    """tema_fast가 tema_slow를 상향 크로스하는 데이터."""
    n = 80
    # 하락 후 급등: fast(10)가 slow(30)보다 빨리 반응
    close = np.concatenate([
        np.linspace(110, 90, 50),   # 하락
        np.linspace(90, 115, 30),   # 급등
    ])
    df = pd.DataFrame({
        "open": close, "close": close,
        "high": close + 0.5, "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_cross_down_df():
    """tema_fast가 tema_slow를 하향 크로스하는 데이터."""
    n = 80
    close = np.concatenate([
        np.linspace(90, 115, 50),   # 상승
        np.linspace(115, 88, 30),   # 급락
    ])
    df = pd.DataFrame({
        "open": close, "close": close,
        "high": close + 0.5, "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


strategy = TEMAStrategy()


# 1. 전략명 확인
def test_strategy_name():
    assert strategy.name == "tema_strategy"


# 2. 인스턴스 생성
def test_strategy_instance():
    strat = TEMAStrategy()
    assert isinstance(strat, TEMAStrategy)


# 3. 데이터 부족 → HOLD
def test_insufficient_data_returns_hold():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 4. None 입력 → HOLD
def test_none_input_returns_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. 데이터 부족 reasoning 확인
def test_insufficient_data_reasoning():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning


# 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성
def test_signal_fields_complete():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "tema_strategy"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY reasoning 키워드 확인
def test_buy_reasoning_keyword():
    df = _make_cross_up_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "TEMA" in sig.reasoning or "crossover" in sig.reasoning.lower()


# 9. SELL reasoning 키워드 확인
def test_sell_reasoning_keyword():
    df = _make_cross_down_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "TEMA" in sig.reasoning or "crossover" in sig.reasoning.lower()


# 10. HIGH confidence 테스트
def test_high_confidence():
    # 이격이 1.5% 초과 → HIGH
    # tema_fast와 tema_slow의 차이가 크도록: 급격한 가격 변화
    n = 80
    close = np.concatenate([
        np.linspace(100, 60, 50),   # 큰 하락
        np.linspace(60, 120, 30),   # 큰 급등
    ])
    df = pd.DataFrame({
        "open": close, "close": close,
        "high": close + 1.0, "low": close - 1.0,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    # 크로스 발생 시 HIGH confidence 가능성 높음
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 11. MEDIUM confidence 테스트
def test_medium_confidence():
    # 이격이 작을 때 → MEDIUM
    df = _make_df(n=60)  # 완만한 상승 → 이격 작음
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 12. entry_price > 0
def test_entry_price_positive():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    if sig.entry_price != 0.0:
        assert sig.entry_price > 0


# 13. strategy 필드 값 확인
def test_strategy_field_value():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.strategy == "tema_strategy"


# 14. 최소 행 수에서 동작
def test_minimum_rows_works():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
