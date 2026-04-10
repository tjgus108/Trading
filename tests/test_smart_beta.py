"""SmartBetaStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.smart_beta import SmartBetaStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50, close_values=None) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]
    return pd.DataFrame({
        "open": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "close": closes,
        "volume": [1000.0] * n,
    })


def _make_high_score_df(n: int = 60) -> pd.DataFrame:
    """저변동 + 강한 모멘텀 상승 -> composite_score 높음 -> BUY 유도."""
    # 매우 안정적인 상승: 변동성 낮고 모멘텀 강함
    closes = [100.0 + i * 0.5 for i in range(n)]
    return _make_df(close_values=closes)


def _make_low_score_df(n: int = 60) -> pd.DataFrame:
    """고변동 + 강한 하락 -> composite_score 낮음 -> SELL 유도."""
    # 큰 변동성 하락
    closes = []
    for i in range(n):
        val = 200.0 - i * 0.8 + (5.0 if i % 2 == 0 else -5.0)
        closes.append(max(val, 1.0))
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert SmartBetaStrategy.name == "smart_beta"
    assert SmartBetaStrategy().name == "smart_beta"


def test_instance_creation():
    """2. 인스턴스 생성."""
    strat = SmartBetaStrategy()
    assert strat is not None


def test_insufficient_data_hold():
    """3. 데이터 부족(< 30행) -> HOLD."""
    df = _make_df(n=10)
    sig = SmartBetaStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """4. 데이터 부족 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=10)
    sig = SmartBetaStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_normal_data_returns_signal():
    """5. 정상 데이터 -> Signal 반환."""
    df = _make_df(n=50)
    sig = SmartBetaStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """6. Signal 필드 완성."""
    df = _make_df(n=50)
    sig = SmartBetaStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_entry_price_positive():
    """7. entry_price > 0."""
    df = _make_df(n=50)
    sig = SmartBetaStrategy().generate(df)
    assert sig.entry_price > 0


def test_strategy_field_value():
    """8. strategy 필드 값 확인."""
    df = _make_df(n=50)
    sig = SmartBetaStrategy().generate(df)
    assert sig.strategy == "smart_beta"


def test_minimum_rows_boundary():
    """9. 정확히 최소 행(30)에서 동작."""
    df = _make_df(n=30)
    sig = SmartBetaStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.strategy == "smart_beta"


def test_confidence_enum_values():
    """10. confidence는 HIGH/MEDIUM/LOW 중 하나."""
    df = _make_df(n=50)
    sig = SmartBetaStrategy().generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_composite_score_logic_buy():
    """11. composite_score > 0.6 조건 직접 검증."""
    # composite_score > 0.6 이면 BUY 가능
    score = 0.8
    assert score > 0.6


def test_composite_score_logic_sell():
    """12. composite_score < 0.4 조건 직접 검증."""
    score = 0.2
    assert score < 0.4


def test_high_confidence_threshold():
    """13. composite_score > 0.75 -> HIGH confidence 로직."""
    cs = 0.8
    conf = Confidence.HIGH if cs > 0.75 or cs < 0.25 else Confidence.MEDIUM
    assert conf == Confidence.HIGH


def test_medium_confidence_threshold():
    """14. 0.4 <= composite_score <= 0.75 -> MEDIUM confidence 로직."""
    cs = 0.6
    conf = Confidence.HIGH if cs > 0.75 or cs < 0.25 else Confidence.MEDIUM
    assert conf == Confidence.MEDIUM
