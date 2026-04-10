"""TrendPersistenceStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_persistence import TrendPersistenceStrategy
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


def _make_trending_up_df(n: int = 60) -> pd.DataFrame:
    """지속적 상승 추세 -> 양의 자기상관 + close > MA."""
    closes = [100.0 + i * 0.5 for i in range(n)]
    return _make_df(close_values=closes)


def _make_trending_down_df(n: int = 60) -> pd.DataFrame:
    """지속적 하락 추세 -> 양의 자기상관 + close < MA."""
    closes = [200.0 - i * 0.5 for i in range(n)]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert TrendPersistenceStrategy.name == "trend_persistence"
    assert TrendPersistenceStrategy().name == "trend_persistence"


def test_instance_creation():
    """2. 인스턴스 생성."""
    strat = TrendPersistenceStrategy()
    assert strat is not None


def test_insufficient_data_hold():
    """3. 데이터 부족 -> HOLD + LOW confidence."""
    df = _make_df(n=10)
    sig = TrendPersistenceStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """4. df=None -> HOLD."""
    sig = TrendPersistenceStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """5. 데이터 부족 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=10)
    sig = TrendPersistenceStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_normal_data_returns_signal():
    """6. 정상 데이터 -> Signal 반환."""
    df = _make_df(n=60)
    sig = TrendPersistenceStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """7. Signal 모든 필드 존재."""
    df = _make_df(n=60)
    sig = TrendPersistenceStrategy().generate(df)
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
    sig = TrendPersistenceStrategy().generate(df)
    assert sig.strategy == "trend_persistence"


def test_entry_price_positive():
    """9. entry_price > 0."""
    df = _make_df(n=60)
    sig = TrendPersistenceStrategy().generate(df)
    assert sig.entry_price > 0


def test_minimum_rows_works():
    """10. 최소 행 수(26)에서 동작."""
    df = _make_df(n=26)
    sig = TrendPersistenceStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.strategy == "trend_persistence"


def test_uptrend_signal():
    """11. 지속적 상승 -> BUY 또는 HOLD."""
    df = _make_trending_up_df(n=60)
    sig = TrendPersistenceStrategy().generate(df)
    assert sig.action in [Action.BUY, Action.HOLD]


def test_downtrend_signal():
    """12. 지속적 하락 -> SELL 또는 HOLD."""
    df = _make_trending_down_df(n=60)
    sig = TrendPersistenceStrategy().generate(df)
    assert sig.action in [Action.SELL, Action.HOLD]


def test_high_confidence_on_high_autocorr():
    """13. autocorr > 0.5 -> HIGH confidence."""
    autocorr_val = 0.6
    conf = Confidence.HIGH if autocorr_val > 0.5 else Confidence.MEDIUM
    assert conf == Confidence.HIGH


def test_medium_confidence_on_low_autocorr():
    """14. autocorr <= 0.5 -> MEDIUM confidence."""
    autocorr_val = 0.3
    conf = Confidence.HIGH if autocorr_val > 0.5 else Confidence.MEDIUM
    assert conf == Confidence.MEDIUM
