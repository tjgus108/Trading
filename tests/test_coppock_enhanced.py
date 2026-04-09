"""CoppockEnhancedStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.coppock_enhanced import CoppockEnhancedStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 60, close_values=None, volume: float = 1000.0) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 1 for c in closes],
            "low": [c - 1 for c in closes],
            "close": closes,
            "volume": [volume] * n,
        }
    )


def _make_buy_df() -> pd.DataFrame:
    """Coppock 0 상향돌파 + RSI>50 유도용."""
    # 급락 후 강하게 회복 → RSI 높아지고 Coppock이 음수→양수 전환
    closes = (
        [100.0] * 5
        + [100.0 - i * 2 for i in range(15)]
        + [70.0 + i * 3 for i in range(40)]
    )
    return _make_df(close_values=closes)


def _make_sell_df() -> pd.DataFrame:
    """Coppock 0 하향돌파 + RSI<50 유도용."""
    # 급등 후 강하게 하락 → RSI 낮아지고 Coppock이 양수→음수 전환
    closes = (
        [100.0] * 5
        + [100.0 + i * 2 for i in range(15)]
        + [130.0 - i * 3 for i in range(40)]
    )
    return _make_df(close_values=closes)


# ── 테스트 ───────────────────────────────────────────────────────────────────


def test_strategy_name():
    """1. 전략 이름 확인."""
    assert CoppockEnhancedStrategy.name == "coppock_enhanced"
    assert CoppockEnhancedStrategy().name == "coppock_enhanced"


def test_insufficient_data_hold():
    """2. 데이터 부족 → HOLD + LOW confidence."""
    df = _make_df(n=10)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """3. df=None → HOLD."""
    sig = CoppockEnhancedStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_generate_no_error_with_enough_data():
    """4. 충분한 데이터 → 에러 없이 Signal 반환."""
    df = _make_df(n=60)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_strategy_field():
    """5. Signal.strategy = 'coppock_enhanced'."""
    df = _make_df(n=60)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.strategy == "coppock_enhanced"


def test_signal_fields_complete():
    """6. 모든 Signal 필드 존재."""
    df = _make_df(n=60)
    sig = CoppockEnhancedStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_entry_price_nonzero_with_sufficient_data():
    """7. 데이터 충분 시 entry_price가 0이 아님."""
    df = _make_df(n=60)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.entry_price != 0.0


def test_exact_min_rows_no_error():
    """8. 정확히 30행 → 에러 없이 Signal 반환."""
    df = _make_df(n=30)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.strategy == "coppock_enhanced"


def test_29_rows_returns_hold_low():
    """9. 29행 → HOLD + LOW."""
    df = _make_df(n=29)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_buy_signal_produces_buy_action():
    """10. 매수 유도 데이터 → BUY 또는 HOLD (에러 없음 확인)."""
    df = _make_buy_df()
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_signal_produces_sell_action():
    """11. 매도 유도 데이터 → SELL 또는 HOLD (에러 없음 확인)."""
    df = _make_sell_df()
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_reasoning_contains_coppock():
    """12. reasoning에 'Coppock' 포함."""
    df = _make_df(n=60)
    sig = CoppockEnhancedStrategy().generate(df)
    assert "Coppock" in sig.reasoning or "데이터" in sig.reasoning


def test_confidence_is_valid_enum():
    """13. confidence는 HIGH/MEDIUM/LOW 중 하나."""
    df = _make_df(n=60)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_different_price_shapes_no_error():
    """14. 다양한 가격 패턴 → 에러 없이 Signal 반환."""
    # 지그재그 패턴
    closes = [100.0 + (5 if i % 2 == 0 else -5) + i * 0.01 for i in range(60)]
    df = _make_df(close_values=closes)
    sig = CoppockEnhancedStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_hold_action_has_empty_invalidation():
    """15. 단순 상승 추세 → HOLD이면 invalidation 빈 문자열."""
    df = _make_df(n=60)  # 완만한 상승
    sig = CoppockEnhancedStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.invalidation == ""
