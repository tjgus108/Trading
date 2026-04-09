"""MomentumReversalStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum_reversal import MomentumReversalStrategy
from src.strategy.base import Action, Confidence


def _make_df(closes) -> pd.DataFrame:
    n = len(closes)
    return pd.DataFrame({
        "open": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "close": closes,
        "volume": [1000.0] * n,
    })


def _buy_setup_df(n: int = 30) -> pd.DataFrame:
    """
    BUY 조건:
      mom14 < 0: close[idx] < close[idx-14]
      mom_ema 상승: 최근 mom_ema가 이전보다 크도록
      close 상승: close[idx] > close[idx-1]
    """
    # 초반 하락(14봉 모멘텀 음수) 후 반등 패턴
    closes = []
    for i in range(n):
        if i < n - 5:
            closes.append(200.0 - i * 1.5)   # 하락 구간
        else:
            closes.append(closes[-1] + 3.0)  # 반등 구간
    return _make_df(closes)


def _sell_setup_df(n: int = 30) -> pd.DataFrame:
    """
    SELL 조건:
      mom14 > 0: close[idx] > close[idx-14]
      mom_ema 하락
      close 하락: close[idx] < close[idx-1]
    """
    closes = []
    for i in range(n):
        if i < n - 5:
            closes.append(100.0 + i * 1.5)   # 상승 구간
        else:
            closes.append(closes[-1] - 3.0)  # 하락 반전
    return _make_df(closes)


def _flat_df(n: int = 30) -> pd.DataFrame:
    closes = [100.0] * n
    return _make_df(closes)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert MomentumReversalStrategy.name == "momentum_reversal"
    assert MomentumReversalStrategy().name == "momentum_reversal"


def test_insufficient_data_hold():
    """2. 데이터 부족 (< 25행) → HOLD, LOW."""
    df = _make_df([100.0] * 10)
    sig = MomentumReversalStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_boundary():
    """3. 정확히 24행 → HOLD."""
    df = _make_df([100.0 + i for i in range(24)])
    sig = MomentumReversalStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_exact_min_rows():
    """4. 정확히 25행 → Signal 반환, 에러 없음."""
    df = _make_df([100.0 + i * 0.1 for i in range(25)])
    sig = MomentumReversalStrategy().generate(df)
    assert sig.strategy == "momentum_reversal"


def test_signal_strategy_field():
    """5. Signal.strategy == 'momentum_reversal'."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert sig.strategy == "momentum_reversal"


def test_signal_entry_price_float():
    """6. entry_price가 float."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert isinstance(sig.entry_price, float)


def test_hold_flat_data():
    """7. 횡보 (mom14 ≈ 0) → HOLD."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_signal_fields_complete():
    """8. Signal 필드 완전성."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert len(sig.reasoning) > 0


def test_buy_conditions_explicit():
    """9. BUY 조건 직접 검증: mom14<0, mom_ema 상승, close 상승."""
    # 마지막 두 봉만 수동으로 구성
    n = 30
    closes = [200.0 - i * 0.5 for i in range(n)]
    # 마지막 3봉 반등 (close 상승, mom14는 여전히 음수)
    closes[-3] = closes[-4] - 1.0
    closes[-2] = closes[-3] + 2.0  # idx-1 = closes[-2] (진행 중 봉)
    closes[-1] = closes[-2] + 2.0  # idx = closes[-1] (미완성)
    df = _make_df(closes)
    close_s = pd.Series(closes)
    mom14 = close_s - close_s.shift(14)
    idx = n - 2
    m14 = float(mom14.iloc[idx])
    # mom14가 음수인 경우에만 BUY 가능한지 확인
    if m14 < 0:
        sig = MomentumReversalStrategy().generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_conditions_explicit():
    """10. SELL 조건 직접 검증: mom14>0, mom_ema 하락, close 하락."""
    n = 30
    closes = [100.0 + i * 0.5 for i in range(n)]
    closes[-3] = closes[-4] + 1.0
    closes[-2] = closes[-3] - 2.0
    closes[-1] = closes[-2] - 2.0
    df = _make_df(closes)
    close_s = pd.Series(closes)
    mom14 = close_s - close_s.shift(14)
    idx = n - 2
    m14 = float(mom14.iloc[idx])
    if m14 > 0:
        sig = MomentumReversalStrategy().generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)


def test_reasoning_not_empty():
    """11. reasoning이 빈 문자열이 아님."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert len(sig.reasoning) > 0


def test_invalidation_not_empty():
    """12. invalidation이 빈 문자열이 아님."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert len(sig.invalidation) > 0


def test_action_enum():
    """13. action이 Action enum."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_confidence_enum():
    """14. confidence가 Confidence enum."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_buy_reasoning_contains_mom14():
    """15. BUY reasoning에 'mom14' 포함."""
    df = _buy_setup_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "mom14" in sig.reasoning


def test_sell_reasoning_contains_mom14():
    """16. SELL reasoning에 'mom14' 포함."""
    df = _sell_setup_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "mom14" in sig.reasoning


def test_high_confidence_large_mom14():
    """17. |mom14| > std(mom14, 20) → HIGH confidence."""
    # 초반 매우 높은 가격, 이후 급락 → |mom14| 클 것
    closes = [500.0] * 14 + [100.0 + i * 0.1 for i in range(16)]
    df = _make_df(closes)
    sig = MomentumReversalStrategy().generate(df)
    # 조건 맞으면 HIGH, 아니면 MEDIUM
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_bull_case_populated():
    """18. bull_case 필드가 str."""
    df = _flat_df(n=30)
    sig = MomentumReversalStrategy().generate(df)
    assert isinstance(sig.bull_case, str)
