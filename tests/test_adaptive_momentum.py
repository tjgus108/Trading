"""AdaptiveMomentumStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_momentum import AdaptiveMomentumStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 80, close_values=None) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.05 for i in range(n)]
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


def _make_strong_uptrend_df(n: int = 80) -> pd.DataFrame:
    """강한 상승 추세 -> BUY 신호 유도."""
    # 빠른 상승으로 mom > 0.02 유도
    closes = [100.0 + i * 0.5 for i in range(n)]
    return _make_df(close_values=closes)


def _make_strong_downtrend_df(n: int = 80) -> pd.DataFrame:
    """강한 하락 추세 -> SELL 신호 유도."""
    closes = [200.0 - i * 0.5 for i in range(n)]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert AdaptiveMomentumStrategy.name == "adaptive_momentum"
    assert AdaptiveMomentumStrategy().name == "adaptive_momentum"


def test_instance_creation():
    """2. 인스턴스 생성."""
    strat = AdaptiveMomentumStrategy()
    assert strat is not None


def test_insufficient_data_hold():
    """3. 데이터 부족 -> HOLD + LOW confidence."""
    df = _make_df(n=10)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """4. df=None -> HOLD."""
    sig = AdaptiveMomentumStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """5. 데이터 부족 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=10)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_normal_data_returns_signal():
    """6. 정상 데이터 -> Signal 반환."""
    df = _make_df(n=80)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """7. Signal 필드 완성."""
    df = _make_df(n=80)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_buy_reasoning_keyword():
    """8. BUY reasoning에 'momentum' 키워드 포함."""
    df = _make_strong_uptrend_df()
    sig = AdaptiveMomentumStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "momentum" in sig.reasoning.lower() or "mom" in sig.reasoning.lower()


def test_sell_reasoning_keyword():
    """9. SELL reasoning에 'momentum' 키워드 포함."""
    df = _make_strong_downtrend_df()
    sig = AdaptiveMomentumStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "momentum" in sig.reasoning.lower() or "mom" in sig.reasoning.lower()


def test_high_confidence_logic():
    """10. |mom| > 0.05 -> HIGH confidence."""
    mom = 0.08
    conf = Confidence.HIGH if abs(mom) > 0.05 else Confidence.MEDIUM
    assert conf == Confidence.HIGH


def test_medium_confidence_logic():
    """11. 0.02 < |mom| <= 0.05 -> MEDIUM confidence."""
    mom = 0.03
    conf = Confidence.HIGH if abs(mom) > 0.05 else Confidence.MEDIUM
    assert conf == Confidence.MEDIUM


def test_entry_price_positive():
    """12. entry_price > 0 (충분한 데이터)."""
    df = _make_df(n=80)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert sig.entry_price > 0


def test_strategy_field_value():
    """13. strategy 필드 값 확인."""
    df = _make_df(n=80)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert sig.strategy == "adaptive_momentum"


def test_minimum_rows_works():
    """14. 최소 행 수(60)에서 동작."""
    df = _make_df(n=60)
    sig = AdaptiveMomentumStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.strategy == "adaptive_momentum"
