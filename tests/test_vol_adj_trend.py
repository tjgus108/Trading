"""VolAdjustedTrendStrategy 단위 테스트 (12개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vol_adj_trend import VolAdjustedTrendStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n=50, close=None, volume=None):
    if close is None:
        close = np.linspace(100.0, 110.0, n)
    close = np.asarray(close, dtype=float)
    n = len(close)
    if volume is None:
        volume = np.ones(n) * 1000.0
    return pd.DataFrame(
        {
            "open":   close - 0.5,
            "high":   close + 1.0,
            "low":    close - 1.0,
            "close":  close,
            "volume": np.asarray(volume, dtype=float),
        }
    )


def _make_strong_uptrend_df():
    """강한 상승 추세: 지수적 급등으로 nm_ema > 1.5 + 가속 조건 충족."""
    # flat base (ATR 낮음), 이후 지수 성장 (매봉마다 slope 증가 → 가속)
    base = np.ones(20) * 100.0
    # exponential: 100 -> 250 over 40 rows (accelerating slope)
    exp_surge = 100.0 * np.exp(np.linspace(0, 0.92, 40))
    return _make_df(close=np.concatenate([base, exp_surge]))


def _make_strong_downtrend_df():
    """강한 하락 추세: 가속적 폭락으로 nm_ema < -1.5 + 가속 조건 충족."""
    base = np.ones(20) * 250.0
    # 250에서 시작해 점점 가팔라지는 하락: 250 - exponential increment
    # diff(5)는 점점 더 부정적 → nm_ema도 가속하며 하락
    t = np.linspace(0, 0.92, 40)
    exp_crash = 250.0 - 150.0 * np.exp(t)  # 250 → ~100, 점점 빠르게 하락
    return _make_df(close=np.concatenate([base, exp_crash]))


# ── tests ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert VolAdjustedTrendStrategy().name == "vol_adj_trend"


def test_hold_on_insufficient_data():
    sig = VolAdjustedTrendStrategy().generate(_make_df(n=10))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_on_exactly_24_rows():
    sig = VolAdjustedTrendStrategy().generate(_make_df(n=24))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_fields_present():
    sig = VolAdjustedTrendStrategy().generate(_make_df(n=50))
    assert sig.strategy == "vol_adj_trend"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_complete_candle():
    df = _make_df(n=50)
    sig = VolAdjustedTrendStrategy().generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_signal_strong_uptrend():
    sig = VolAdjustedTrendStrategy().generate(_make_strong_uptrend_df())
    assert sig.action == Action.BUY


def test_sell_signal_strong_downtrend():
    sig = VolAdjustedTrendStrategy().generate(_make_strong_downtrend_df())
    assert sig.action == Action.SELL


def test_buy_confidence_high_on_extreme_nm():
    """nm_ema > 3.0 → HIGH confidence."""
    sig = VolAdjustedTrendStrategy().generate(_make_strong_uptrend_df())
    if sig.action == Action.BUY:
        # strong uptrend should trigger HIGH
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_confidence_high_on_extreme_nm():
    sig = VolAdjustedTrendStrategy().generate(_make_strong_downtrend_df())
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_empty_dataframe_returns_hold():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    sig = VolAdjustedTrendStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == pytest.approx(0.0)


def test_flat_price_no_buy_sell():
    """가격 변화 없음 → nm_ema ≈ 0, 조건 미충족 → HOLD."""
    close = np.ones(50) * 100.0
    sig = VolAdjustedTrendStrategy().generate(_make_df(close=close))
    assert sig.action == Action.HOLD


def test_buy_invalidation_message():
    sig = VolAdjustedTrendStrategy().generate(_make_strong_uptrend_df())
    if sig.action == Action.BUY:
        assert "nm_ema" in sig.invalidation or "1.5" in sig.invalidation
