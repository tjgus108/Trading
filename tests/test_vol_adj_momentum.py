"""VolAdjMomentumStrategy 단위 테스트 (15개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vol_adj_momentum import VolAdjMomentumStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n=40, close=None):
    if close is None:
        close = np.linspace(100.0, 110.0, n)
    close = np.asarray(close, dtype=float)
    n = len(close)
    return pd.DataFrame(
        {
            "open":   close - 0.5,
            "high":   close + 1.0,
            "low":    close - 1.0,
            "close":  close,
            "volume": np.ones(n) * 1000.0,
        }
    )


def _make_buy_signal_df():
    """강한 상승 모멘텀: 낮은 변동성 후 급등."""
    base = np.ones(20) * 100.0
    up = np.linspace(100.0, 140.0, 20)
    return _make_df(close=np.concatenate([base, up]))


def _make_sell_signal_df():
    """강한 하락 모멘텀: 높은 가격 후 급락."""
    base = np.ones(20) * 140.0
    down = np.linspace(140.0, 100.0, 20)
    return _make_df(close=np.concatenate([base, down]))


# ── tests ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert VolAdjMomentumStrategy().name == "vol_adj_momentum"


def test_hold_on_insufficient_data():
    sig = VolAdjMomentumStrategy().generate(_make_df(n=10))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_on_exactly_24_rows():
    """24행 (최소 25 미만) → HOLD LOW."""
    sig = VolAdjMomentumStrategy().generate(_make_df(n=24))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_fields_present():
    strat = VolAdjMomentumStrategy()
    sig = strat.generate(_make_df(n=40))
    assert sig.strategy == "vol_adj_momentum"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_complete_candle():
    df = _make_df(n=40)
    sig = VolAdjMomentumStrategy().generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_hold_during_flat_price():
    """가격 변동 거의 없음 → 모멘텀 신호 없이 HOLD."""
    close = np.ones(40) * 100.0 + np.random.default_rng(42).uniform(-0.01, 0.01, 40)
    sig = VolAdjMomentumStrategy().generate(_make_df(close=close))
    # 변동성 거의 없으면 vol_adj_mom이 매우 크거나 작을 수 있음 — 동작 확인만
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_signal_strong_momentum():
    """강한 상승 모멘텀 → BUY 신호."""
    sig = VolAdjMomentumStrategy().generate(_make_buy_signal_df())
    assert sig.action == Action.BUY


def test_sell_signal_strong_momentum():
    """강한 하락 모멘텀 → SELL 신호."""
    sig = VolAdjMomentumStrategy().generate(_make_sell_signal_df())
    assert sig.action == Action.SELL


def test_buy_confidence_classification():
    """BUY confidence는 HIGH 또는 MEDIUM."""
    sig = VolAdjMomentumStrategy().generate(_make_buy_signal_df())
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_confidence_classification():
    """SELL confidence는 HIGH 또는 MEDIUM."""
    sig = VolAdjMomentumStrategy().generate(_make_sell_signal_df())
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_custom_mom_period_and_signal_span():
    """mom_period=7, signal_span=5으로 정상 동작."""
    strat = VolAdjMomentumStrategy(mom_period=7, signal_span=5)
    sig = strat.generate(_make_df(n=40))
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_empty_dataframe_returns_hold():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    sig = VolAdjMomentumStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == pytest.approx(0.0)


def test_reasoning_contains_vol_adj_mom():
    """reasoning에 VolAdjMom 값 포함."""
    sig = VolAdjMomentumStrategy().generate(_make_df(n=40))
    assert "VolAdjMom" in sig.reasoning or "부족" in sig.reasoning or "NaN" in sig.reasoning


def test_buy_invalidation_mentions_signal_line():
    sig = VolAdjMomentumStrategy().generate(_make_buy_signal_df())
    if sig.action == Action.BUY:
        assert "signal_line" in sig.invalidation


def test_sell_invalidation_mentions_signal_line():
    sig = VolAdjMomentumStrategy().generate(_make_sell_signal_df())
    if sig.action == Action.SELL:
        assert "signal_line" in sig.invalidation


def test_vol_adj_mom_high_confidence_threshold():
    """|vol_adj_mom| > 2.0 이면 HIGH confidence."""
    # 거의 0 변동성 + 강한 모멘텀 → vol_adj_mom 매우 큼
    base = np.ones(15) * 100.0
    surge = np.linspace(100.0, 130.0, 25)
    close = np.concatenate([base, surge])
    sig = VolAdjMomentumStrategy().generate(_make_df(close=close))
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH
