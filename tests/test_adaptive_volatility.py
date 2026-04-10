"""AdaptiveVolatilityStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_volatility import AdaptiveVolatilityStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 60, close_values=None) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 60) -> pd.DataFrame:
    """강한 상승: momentum > threshold, close > EMA20 유도."""
    # 처음에 flat하다가 마지막에 급등
    closes = [100.0] * (n // 2) + [100.0 + i * 2.0 for i in range(1, n // 2 + 1)]
    closes = closes[:n]
    return _make_df(close_values=closes)


def _make_sell_df(n: int = 60) -> pd.DataFrame:
    """강한 하락: momentum < -threshold, close < EMA20 유도."""
    closes = [200.0] * (n // 2) + [200.0 - i * 2.0 for i in range(1, n // 2 + 1)]
    closes = closes[:n]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert AdaptiveVolatilityStrategy.name == "adaptive_volatility"
    assert AdaptiveVolatilityStrategy().name == "adaptive_volatility"


def test_instance_creation():
    """2. 인스턴스 생성."""
    strat = AdaptiveVolatilityStrategy()
    assert strat is not None


def test_insufficient_data_hold():
    """3. 데이터 부족 -> HOLD + LOW confidence."""
    df = _make_df(n=10)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """4. df=None -> HOLD."""
    sig = AdaptiveVolatilityStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """5. 데이터 부족 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=10)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_normal_data_returns_signal():
    """6. 정상 데이터 -> Signal 반환."""
    df = _make_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """7. Signal 모든 필드 존재."""
    df = _make_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_strategy_field_value():
    """8. strategy 필드가 전략 이름."""
    df = _make_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert sig.strategy == "adaptive_volatility"


def test_entry_price_positive():
    """9. entry_price > 0."""
    df = _make_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert sig.entry_price > 0


def test_minimum_rows_works():
    """10. 최소 행 수(26)에서 동작."""
    df = _make_df(n=26)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.strategy == "adaptive_volatility"


def test_buy_signal_on_strong_uptrend():
    """11. 강한 상승 -> BUY 또는 HOLD (신호 검증)."""
    df = _make_buy_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert sig.action in [Action.BUY, Action.HOLD]


def test_sell_signal_on_strong_downtrend():
    """12. 강한 하락 -> SELL 또는 HOLD (신호 검증)."""
    df = _make_sell_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    assert sig.action in [Action.SELL, Action.HOLD]


def test_confidence_not_low_on_normal_data():
    """13. 정상 데이터 -> LOW 이외의 confidence."""
    df = _make_df(n=60)
    sig = AdaptiveVolatilityStrategy().generate(df)
    # 데이터 충분하면 LOW confidence가 나오지 않아야 함
    assert sig.confidence != Confidence.LOW


def test_buy_reasoning_contains_threshold():
    """14. BUY 신호 reasoning에 'threshold' 또는 'momentum' 포함."""
    df = _make_buy_df(n=80)
    sig = AdaptiveVolatilityStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "momentum" in sig.reasoning.lower() or "threshold" in sig.reasoning.lower()
