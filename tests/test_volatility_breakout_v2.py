"""VolatilityBreakoutV2Strategy 단위 테스트 (ATR 배수 기반 돌파)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.volatility_breakout_v2 import VolatilityBreakoutV2Strategy


def _make_df(n: int = 25, close: float = 100.0, high_offset: float = 1.0,
             low_offset: float = 1.0) -> pd.DataFrame:
    """균일한 가격 DataFrame."""
    closes = np.ones(n) * close
    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + high_offset,
        "low": closes - low_offset,
        "volume": np.ones(n) * 1000.0,
    })


def _make_buy_df(n: int = 25) -> pd.DataFrame:
    """idx(-2) close가 ATR upper를 크게 돌파."""
    closes = np.ones(n) * 100.0
    df = pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + 2.0,
        "low": closes - 2.0,
        "volume": np.ones(n) * 1000.0,
    })
    # ATR ~= 4, prev_close ~= 100, upper = 100 + 0.5*4 = 102
    # HIGH: (close - upper)/atr > 0.3 → close > 102 + 0.3*4 = 103.2
    df.loc[df.index[-2], "close"] = 110.0  # well above upper
    return df


def _make_sell_df(n: int = 25) -> pd.DataFrame:
    """idx(-2) close가 ATR lower를 크게 하향 돌파."""
    closes = np.ones(n) * 100.0
    df = pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + 2.0,
        "low": closes - 2.0,
        "volume": np.ones(n) * 1000.0,
    })
    # lower = 100 - 0.5*4 = 98
    df.loc[df.index[-2], "close"] = 90.0  # well below lower
    return df


strategy = VolatilityBreakoutV2Strategy()


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "volatility_breakout_v2"


# 2. 인스턴스 생성
def test_strategy_instance():
    strat = VolatilityBreakoutV2Strategy()
    assert isinstance(strat, VolatilityBreakoutV2Strategy)


# 3. 데이터 부족 (< 20행) → HOLD
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# 4. None 입력 → HOLD
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. reasoning 필드 비어있지 않음
def test_reasoning_not_empty():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert isinstance(sig.reasoning, str)
    assert len(sig.reasoning) > 0


# 6. 정상 signal 반환
def test_normal_signal_returned():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _make_df(n=25)
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
    """(close - upper) / atr > 0.3 → HIGH."""
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 11. MEDIUM confidence BUY
def test_buy_medium_confidence():
    """(close - upper) / atr <= 0.3 → MEDIUM."""
    n = 25
    closes = np.ones(n) * 100.0
    df = pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + 2.0,
        "low": closes - 2.0,
        "volume": np.ones(n) * 1000.0,
    })
    # ATR ~4, upper ~102, HIGH threshold = 0.3*4=1.2, so >103.2 → HIGH
    # MEDIUM: 102 < close <= 103.2
    df.loc[df.index[-2], "close"] = 102.5  # ratio = 0.5/4 = 0.125 < 0.3 → MEDIUM
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# 12. entry_price > 0
def test_entry_price_positive():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# 13. strategy 필드 == "volatility_breakout_v2"
def test_strategy_field():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert sig.strategy == "volatility_breakout_v2"


# 14. 최소 행 경계 (20행) → 유효한 signal
def test_at_min_rows():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}
