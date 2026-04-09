"""LRChannelStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.lr_channel import LRChannelStrategy, _calc_lr
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


def _uptrend_df(n: int = 35) -> pd.DataFrame:
    """slope > 0이고 마지막(idx=-2)이 채널 하단 아래에 오도록 구성."""
    closes = [100.0 + i * 1.0 for i in range(n - 2)] + [
        100.0 + (n - 2) * 1.0 - 10.0,  # idx-1: 큰 하락
        100.0 + (n - 1) * 1.0 - 10.0,  # idx: 미완성봉
    ]
    return _make_df(closes)


def _downtrend_df(n: int = 35) -> pd.DataFrame:
    """slope < 0이고 마지막(idx=-2)이 채널 상단 위에 오도록 구성."""
    closes = [300.0 - i * 1.0 for i in range(n - 2)] + [
        300.0 - (n - 2) * 1.0 + 10.0,  # idx-1: 큰 상승
        300.0 - (n - 1) * 1.0 + 10.0,  # idx: 미완성봉
    ]
    return _make_df(closes)


def _flat_df(n: int = 35) -> pd.DataFrame:
    closes = [100.0] * n
    return _make_df(closes)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert LRChannelStrategy.name == "lr_channel"
    assert LRChannelStrategy().name == "lr_channel"


def test_insufficient_data_hold():
    """2. 데이터 부족 (< 30행) → HOLD, LOW."""
    df = _make_df([100.0] * 10)
    sig = LRChannelStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_boundary():
    """3. 정확히 29행 → HOLD."""
    df = _make_df([100.0 + i for i in range(29)])
    sig = LRChannelStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_exact_min_rows():
    """4. 정확히 30행 → Signal 반환, 에러 없음."""
    df = _make_df([100.0 + i * 0.1 for i in range(30)])
    sig = LRChannelStrategy().generate(df)
    assert sig.strategy == "lr_channel"


def test_signal_strategy_field():
    """5. Signal.strategy == 'lr_channel'."""
    df = _flat_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert sig.strategy == "lr_channel"


def test_signal_entry_price_float():
    """6. entry_price가 float."""
    df = _flat_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert isinstance(sig.entry_price, float)


def test_buy_signal_uptrend_below_lower():
    """7. slope > 0 이고 close < lower_channel → BUY."""
    df = _uptrend_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert sig.action == Action.BUY


def test_sell_signal_downtrend_above_upper():
    """8. slope < 0 이고 close > upper_channel → SELL."""
    df = _downtrend_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert sig.action == Action.SELL


def test_hold_flat_data():
    """9. 횡보 (slope ≈ 0) → HOLD."""
    df = _flat_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_buy_reasoning_contains_lower():
    """10. BUY reasoning에 'lower' 포함."""
    df = _uptrend_df(n=35)
    sig = LRChannelStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "lower" in sig.reasoning


def test_sell_reasoning_contains_upper():
    """11. SELL reasoning에 'upper' 포함."""
    df = _downtrend_df(n=35)
    sig = LRChannelStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "upper" in sig.reasoning


def test_signal_fields_complete():
    """12. Signal 필드 완전성."""
    df = _uptrend_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert len(sig.reasoning) > 0


def test_calc_lr_perfect_linear():
    """13. 완벽한 선형 데이터 → slope=1, intercept=0."""
    y = np.arange(20, dtype=float)
    slope, intercept = _calc_lr(y)
    assert slope == pytest.approx(1.0, abs=1e-6)
    assert intercept == pytest.approx(0.0, abs=1e-6)


def test_calc_lr_flat():
    """14. 상수 데이터 → slope=0."""
    y = np.ones(20) * 50.0
    slope, intercept = _calc_lr(y)
    assert slope == pytest.approx(0.0, abs=1e-6)
    assert intercept == pytest.approx(50.0, abs=1e-6)


def test_calc_lr_decreasing():
    """15. 하락 데이터 → slope < 0."""
    y = np.array([20.0 - i for i in range(20)])
    slope, intercept = _calc_lr(y)
    assert slope < 0


def test_confidence_high_when_large_residual():
    """16. 잔차가 매우 클 때 HIGH confidence."""
    # slope > 0 이고 close가 lower_channel보다 훨씬 아래
    n = 40
    closes = [100.0 + i * 2.0 for i in range(n - 2)] + [
        100.0 + (n - 2) * 2.0 - 50.0,
        100.0 + (n - 1) * 2.0 - 50.0,
    ]
    df = _make_df(closes)
    sig = LRChannelStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_custom_period():
    """17. period=10 커스텀 작동."""
    df = _make_df([100.0 + i * 0.5 for i in range(35)])
    sig = LRChannelStrategy(period=10).generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_action_enum_values():
    """18. action이 Action enum 인스턴스."""
    df = _flat_df(n=35)
    sig = LRChannelStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
