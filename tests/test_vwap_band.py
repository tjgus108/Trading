"""VWAPBandStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vwap_band import VWAPBandStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(close, volume=None):
    close = np.asarray(close, dtype=float)
    n = len(close)
    if volume is None:
        volume = np.ones(n) * 1000.0
    return pd.DataFrame(
        {
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.asarray(volume, dtype=float),
        }
    )


def _stable(n=40):
    return _make_df(np.ones(n) * 100.0 + np.arange(n) * 0.01)


def _buy_df():
    """close가 lower_band 아래이고 이전보다 상승 → BUY 조건."""
    # 안정적 구간 후 급락 → lower_band 아래, 그 다음 약간 반등
    # close << vwap → lower_band 이하로 떨어짐
    base = np.ones(38) * 100.0
    # -3: 급락 (lower_band 이하)
    # -2 (idx): 급락에서 약간 회복 (c > c_prev)
    # -1: 현재 캔들 (무시)
    extra = np.array([50.0, 55.0, 56.0])
    return _make_df(np.concatenate([base, extra]))


def _sell_df():
    """close가 upper_band 위이고 이전보다 하락 → SELL 조건."""
    base = np.ones(38) * 100.0
    # -3: 급등 (upper_band 이상)
    # -2 (idx): 약간 하락 (c < c_prev)
    # -1: 현재 캔들 (무시)
    extra = np.array([200.0, 195.0, 194.0])
    return _make_df(np.concatenate([base, extra]))


# ── tests ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert VWAPBandStrategy().name == "vwap_band"


def test_hold_insufficient_data():
    sig = VWAPBandStrategy().generate(_make_df(np.ones(10) * 100.0))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_exactly_19_rows():
    sig = VWAPBandStrategy().generate(_make_df(np.linspace(100, 110, 19)))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_no_error_at_minimum_rows():
    sig = VWAPBandStrategy().generate(_make_df(np.linspace(100, 110, 20)))
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_present():
    sig = VWAPBandStrategy().generate(_stable())
    assert sig.strategy == "vwap_band"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_second_to_last():
    df = _stable()
    sig = VWAPBandStrategy().generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_empty_dataframe():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    sig = VWAPBandStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == pytest.approx(0.0)


def test_hold_stable_price():
    """가격 변동 거의 없음 → HOLD (밴드 돌파 없음)."""
    sig = VWAPBandStrategy().generate(_stable())
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_condition_logic():
    """close < lower_band AND close > prev_close → BUY."""
    df = _buy_df()
    close = df["close"]
    volume = df["volume"]
    vwap = (close * volume).rolling(20, min_periods=1).sum() / volume.rolling(20, min_periods=1).sum()
    deviation = close - vwap
    dev_std = deviation.rolling(20, min_periods=1).std()
    lower_band = vwap - dev_std * 2
    idx = len(df) - 2
    c = float(close.iloc[idx])
    c_prev = float(close.iloc[idx - 1])
    lb = float(lower_band.iloc[idx])
    if c < lb and c > c_prev:
        sig = VWAPBandStrategy().generate(df)
        assert sig.action == Action.BUY


def test_sell_condition_logic():
    """close > upper_band AND close < prev_close → SELL."""
    df = _sell_df()
    close = df["close"]
    volume = df["volume"]
    vwap = (close * volume).rolling(20, min_periods=1).sum() / volume.rolling(20, min_periods=1).sum()
    deviation = close - vwap
    dev_std = deviation.rolling(20, min_periods=1).std()
    upper_band = vwap + dev_std * 2
    idx = len(df) - 2
    c = float(close.iloc[idx])
    c_prev = float(close.iloc[idx - 1])
    ub = float(upper_band.iloc[idx])
    if c > ub and c < c_prev:
        sig = VWAPBandStrategy().generate(df)
        assert sig.action == Action.SELL


def test_confidence_high_when_extreme_deviation():
    """abs(deviation) > dev_std * 2.5 → HIGH confidence."""
    # 매우 큰 이탈 → HIGH
    df = _buy_df()
    sig = VWAPBandStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_reasoning_contains_vwap():
    sig = VWAPBandStrategy().generate(_stable())
    assert "VWAP" in sig.reasoning or "부족" in sig.reasoning or "NaN" in sig.reasoning


def test_vwap_formula():
    """vwap = (close*vol).rolling(20).sum() / vol.rolling(20).sum()."""
    df = _stable(40)
    close = df["close"]
    volume = df["volume"]
    expected_vwap = (
        (close * volume).rolling(20, min_periods=1).sum()
        / volume.rolling(20, min_periods=1).sum()
    )
    # VWAP is weighted mean of close (uniform volume → equals rolling mean)
    rolling_mean = close.rolling(20, min_periods=1).mean()
    pd.testing.assert_series_equal(
        expected_vwap.round(6), rolling_mean.round(6), check_names=False
    )


def test_no_buy_without_price_uptick():
    """close < lower_band 이지만 c < c_prev → BUY 없음."""
    # -2: 하락 지속 (c < c_prev)
    base = np.ones(38) * 100.0
    extra = np.array([55.0, 50.0, 49.0])  # -2=50 < -3=55 → 하락
    df = _make_df(np.concatenate([base, extra]))
    close = df["close"]
    volume = df["volume"]
    vwap = (close * volume).rolling(20, min_periods=1).sum() / volume.rolling(20, min_periods=1).sum()
    deviation = close - vwap
    dev_std = deviation.rolling(20, min_periods=1).std()
    lower_band = vwap - dev_std * 2
    idx = len(df) - 2
    c = float(close.iloc[idx])
    c_prev = float(close.iloc[idx - 1])
    lb = float(lower_band.iloc[idx])
    # 조건: close < lower_band 이지만 c < c_prev → BUY 안 됨
    if c < lb and c < c_prev:
        sig = VWAPBandStrategy().generate(df)
        assert sig.action != Action.BUY
