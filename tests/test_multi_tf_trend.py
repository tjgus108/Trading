"""Tests for MultiTFTrendStrategy (14 tests)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.multi_tf_trend import MultiTFTrendStrategy
from src.strategy.base import Action, Confidence, Signal


def make_df(n: int, close_val: float = 100.0) -> pd.DataFrame:
    """기본 OHLCV DataFrame (flat close)."""
    data = {
        "open":   [close_val] * n,
        "high":   [close_val + 1.0] * n,
        "low":    [close_val - 1.0] * n,
        "close":  [close_val] * n,
        "volume": [1000.0] * n,
    }
    return pd.DataFrame(data)


def make_uptrend_df(n: int = 150) -> pd.DataFrame:
    """꾸준히 상승하는 close → EMA10>EMA20>EMA50>EMA100 → score=3 (BUY)."""
    closes = [100.0 + i * 0.5 for i in range(n)]
    data = {
        "open":   closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "close":  closes,
        "volume": [1000.0] * n,
    }
    return pd.DataFrame(data)


def make_downtrend_df(n: int = 150) -> pd.DataFrame:
    """꾸준히 하락하는 close → EMA10<EMA20<EMA50<EMA100 → score=0 (SELL)."""
    closes = [200.0 - i * 0.5 for i in range(n)]
    data = {
        "open":   closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "close":  closes,
        "volume": [1000.0] * n,
    }
    return pd.DataFrame(data)


# ─── Tests ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략명 확인."""
    s = MultiTFTrendStrategy()
    assert s.name == "multi_tf_trend"


def test_instantiation():
    """2. 인스턴스 생성."""
    s = MultiTFTrendStrategy()
    assert isinstance(s, MultiTFTrendStrategy)


def test_insufficient_data_returns_hold():
    """3. 데이터 부족 → HOLD."""
    s = MultiTFTrendStrategy()
    df = make_df(50)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_none_input_returns_hold():
    """4. None 입력 → HOLD."""
    s = MultiTFTrendStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """5. 데이터 부족 reasoning 확인."""
    s = MultiTFTrendStrategy()
    df = make_df(80)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


def test_normal_data_returns_signal():
    """6. 정상 데이터 → Signal 반환."""
    s = MultiTFTrendStrategy()
    df = make_df(150)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """7. Signal 필드 완성."""
    s = MultiTFTrendStrategy()
    df = make_df(150)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "multi_tf_trend"
    assert sig.reasoning != ""


def test_buy_reasoning_keyword():
    """8. BUY reasoning 키워드 확인."""
    s = MultiTFTrendStrategy()
    df = make_uptrend_df(150)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "bullish" in sig.reasoning.lower() or "score" in sig.reasoning.lower()


def test_sell_reasoning_keyword():
    """9. SELL reasoning 키워드 확인."""
    s = MultiTFTrendStrategy()
    df = make_downtrend_df(150)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "bearish" in sig.reasoning.lower() or "score" in sig.reasoning.lower()


def test_uptrend_produces_buy():
    """10. 강한 상승 추세 → BUY."""
    s = MultiTFTrendStrategy()
    df = make_uptrend_df(150)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_downtrend_produces_sell():
    """11. 강한 하락 추세 → SELL."""
    s = MultiTFTrendStrategy()
    df = make_downtrend_df(150)
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_entry_price_positive():
    """12. entry_price > 0."""
    s = MultiTFTrendStrategy()
    df = make_df(150, close_val=50.0)
    sig = s.generate(df)
    assert sig.entry_price > 0


def test_strategy_field_value():
    """13. strategy 필드 값 확인."""
    s = MultiTFTrendStrategy()
    df = make_df(150)
    sig = s.generate(df)
    assert sig.strategy == "multi_tf_trend"


def test_minimum_rows():
    """14. 최소 행 수(110)에서 동작."""
    s = MultiTFTrendStrategy()
    df = make_df(110)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
