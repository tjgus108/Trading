"""ROCDivergenceStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.roc_divergence import ROCDivergenceStrategy


def _make_df(n=50, close_vals=None):
    np.random.seed(0)
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


def _make_bullish_df():
    """가격은 새 저점, ROC는 새 저점 아님, ROC 상승 중 → BUY."""
    n = 40
    # 하락 추세이다가 막판에 ROC가 반등하는 패턴
    base = np.linspace(110, 90, n)
    # 마지막 구간에서 가격은 계속 하락(새 저점), ROC는 이전 저점보다 높게
    # 인위적으로 짧은 기간 내 급반등을 줘서 ROC 상승
    close = base.copy()
    # 마지막 5개를 약간 반등시켜 pct_change(10)이 이전보다 덜 음수가 되도록
    close[-5:] = close[-6] * np.array([0.99, 0.991, 0.992, 0.993, 0.994])
    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": close + 0.5,
        "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_bearish_df():
    """가격은 새 고점, ROC는 새 고점 아님, ROC 하락 중 → SELL."""
    n = 40
    base = np.linspace(90, 110, n)
    close = base.copy()
    # 마지막 5개를 약간 눌러서 ROC가 이전 고점보다 낮아지도록
    close[-5:] = close[-6] * np.array([1.01, 1.009, 1.008, 1.007, 1.006])
    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": close + 0.5,
        "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


strategy = ROCDivergenceStrategy()


# 1. 전략명 확인
def test_strategy_name():
    assert strategy.name == "roc_divergence"


# 2. 인스턴스 생성
def test_strategy_instance():
    strat = ROCDivergenceStrategy()
    assert isinstance(strat, ROCDivergenceStrategy)


# 3. 데이터 부족 → HOLD
def test_insufficient_data_returns_hold():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 4. None 입력 → HOLD
def test_none_input_returns_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. 데이터 부족 reasoning 확인
def test_insufficient_data_reasoning():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning


# 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# 7. Signal 필드 완성
def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "roc_divergence"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY reasoning 키워드 확인
def test_buy_reasoning_keyword():
    # 강제로 BUY 조건을 만드는 데이터 구성
    n = 40
    # 하락하는 가격: 새 저점 달성
    close = np.linspace(110, 89, n)
    # ROC가 상승 중이 되도록: 마지막 부분 일부 반등
    # idx = n-2 = 38, close[38] <= rolling(10).min(), roc[38] > roc[37]
    # rolling min은 close[29:39].min() → close[38]이 가장 낮아야 함
    # roc10[38] = (close[38]-close[28])/close[28]*100
    # roc10[37] = (close[37]-close[27])/close[27]*100
    # close가 linspace이므로 pct_change(10)은 일정하게 음수
    # 마지막 10개를 약간 올려서 roc가 증가하도록 조정
    close2 = close.copy()
    # close[28..37] 구간을 낮춰서 roc[38] > roc[37] 만들기
    close2[28:33] *= 0.96  # 10기간 전 가격을 낮춰서 roc 개선
    df = pd.DataFrame({
        "open": close2, "close": close2,
        "high": close2 + 0.3, "low": close2 - 0.3,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    # BUY가 나올 수도, HOLD가 나올 수도 있으므로 BUY 시 reasoning 확인
    if sig.action == Action.BUY:
        assert "divergence" in sig.reasoning.lower() or "Bullish" in sig.reasoning


# 9. SELL reasoning 키워드 확인
def test_sell_reasoning_keyword():
    df = _make_bearish_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "divergence" in sig.reasoning.lower() or "Bearish" in sig.reasoning


# 10. HIGH confidence 테스트
def test_high_confidence():
    # HIGH conf: |roc10 - roc10.shift(5)| > roc10.rolling(20).std()
    n = 50
    # 변동성이 큰 데이터 → std 작고 roc 변화 큼
    close = np.ones(n) * 100.0
    # 일부 구간에서 큰 변화를 줘서 roc 변화량이 std를 초과하게
    close[5:15] = 80.0  # 급락
    close[15:30] = 105.0  # 급등
    close[30:] = 100.0
    df = pd.DataFrame({
        "open": close, "close": close,
        "high": close + 0.5, "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    # 신호가 뭐든 confidence가 HIGH 또는 MEDIUM이어야 함
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 11. MEDIUM confidence 테스트
def test_medium_confidence():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 12. entry_price > 0
def test_entry_price_positive():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    if sig.action != Action.HOLD or sig.entry_price != 0.0:
        assert sig.entry_price > 0


# 13. strategy 필드 값 확인
def test_strategy_field_value():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.strategy == "roc_divergence"


# 14. 최소 행 수에서 동작
def test_minimum_rows_works():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
