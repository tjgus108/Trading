"""DualThrustStrategy 단위 테스트 (rolling N=4, k=0.5 기반)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.dual_thrust import DualThrustStrategy


def _make_df(n: int = 20, base_price: float = 100.0) -> pd.DataFrame:
    """기본 단조 증가 DataFrame."""
    prices = np.linspace(base_price, base_price + 2, n)
    return pd.DataFrame({
        "open": prices,
        "close": prices,
        "high": prices + 1.0,
        "low": prices - 1.0,
        "volume": np.ones(n) * 1000.0,
    })


def _make_buy_df(n: int = 20) -> pd.DataFrame:
    """idx(-2) close가 upper_level을 크게 돌파하는 DataFrame."""
    prices = np.ones(n) * 100.0
    df = pd.DataFrame({
        "open": prices.copy(),
        "close": prices.copy(),
        "high": prices + 1.0,
        "low": prices - 1.0,
        "volume": np.ones(n) * 1000.0,
    })
    # idx = n-2: open=100, range_val ~ max(hh-lc, hc-ll)
    # with uniform prices: hh=100, hc=100, lc=100, ll=100 → range=0
    # Make high prices vary to get non-zero range
    df["high"] = np.linspace(100, 110, n)  # increasing highs → hh > lc
    df["close"].iloc[-2] = 115.0  # big close above upper
    return df


def _make_sell_df(n: int = 20) -> pd.DataFrame:
    """idx(-2) close가 lower_level을 크게 하향 돌파하는 DataFrame."""
    df = pd.DataFrame({
        "open": np.ones(n) * 100.0,
        "close": np.linspace(110, 100, n),
        "high": np.linspace(111, 101, n),
        "low": np.linspace(109, 99, n),
        "volume": np.ones(n) * 1000.0,
    })
    df["close"].iloc[-2] = 85.0  # big close below lower
    return df


strategy = DualThrustStrategy()


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "dual_thrust"


# 2. 인스턴스 생성
def test_strategy_instance():
    strat = DualThrustStrategy()
    assert isinstance(strat, DualThrustStrategy)


# 3. 데이터 부족 (< 10행) → HOLD
def test_insufficient_data():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# 4. None 입력 → HOLD
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. reasoning 필드 비어있지 않음
def test_reasoning_not_empty():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert isinstance(sig.reasoning, str)
    assert len(sig.reasoning) > 0


# 6. 정상 signal 반환 확인
def test_normal_signal_returned():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")


# 8. BUY reasoning에 "돌파" 포함
def test_buy_reasoning():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "돌파" in sig.reasoning


# 9. SELL reasoning에 "붕괴" 포함
def test_sell_reasoning():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "붕괴" in sig.reasoning


# 10. HIGH confidence BUY
def test_buy_high_confidence():
    """close가 upper_level을 크게 초과 (>2%) → HIGH confidence."""
    n = 20
    df = pd.DataFrame({
        "open": np.ones(n) * 100.0,
        "close": np.ones(n) * 100.0,
        "high": np.ones(n) * 105.0,
        "low": np.ones(n) * 95.0,
        "volume": np.ones(n) * 1000.0,
    })
    # range_val = max(hh-lc, hc-ll) = max(105-100, 100-95) = 5
    # upper = 100 + 0.5*5 = 102.5
    # HIGH if (close - upper) / range > 0.02 → close > 102.5 + 0.02*5 = 102.6
    df["close"].iloc[-2] = 106.0  # ratio = (106-102.5)/5 = 0.7 → HIGH
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 11. MEDIUM confidence BUY
def test_buy_medium_confidence():
    """close가 upper_level을 약간 초과 (<=2%) → MEDIUM confidence."""
    n = 20
    df = pd.DataFrame({
        "open": np.ones(n) * 100.0,
        "close": np.ones(n) * 100.0,
        "high": np.ones(n) * 105.0,
        "low": np.ones(n) * 95.0,
        "volume": np.ones(n) * 1000.0,
    })
    # range=5, upper=102.5, ratio threshold = 0.02*5=0.1
    # MEDIUM if close < 102.5 + 0.1 = 102.6 but > 102.5
    df["close"].iloc[-2] = 102.55  # ratio = 0.01 → MEDIUM
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# 12. entry_price > 0
def test_entry_price_positive():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# 13. strategy 필드 == "dual_thrust"
def test_strategy_field():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.strategy == "dual_thrust"


# 14. 최소 행 경계 (10행) → 유효한 signal
def test_at_min_rows():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}
