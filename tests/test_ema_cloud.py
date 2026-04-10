"""
EMACloudStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ema_cloud import EMACloudStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 80, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    highs = [c * 1.01 for c in close_values]
    lows = [c * 0.99 for c in close_values]
    return pd.DataFrame({
        "open": close_values,
        "high": highs,
        "low": lows,
        "close": close_values,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 90) -> pd.DataFrame:
    """
    강한 상승 추세: fast_line > slow_line, close > cloud_top, cloud_top_future 위
    처음 60개는 베이스, 이후 급등.
    """
    closes = [100.0] * n
    # 마지막 30개 강하게 상승 → fast EMA가 slow EMA 위
    for i in range(n - 30, n):
        closes[i] = 100.0 + (i - (n - 30)) * 2.0  # 100 → 160
    df = _make_df(n=n, close_values=closes)
    return df


def _make_sell_df(n: int = 90) -> pd.DataFrame:
    """
    강한 하락 추세: fast_line < slow_line, close < cloud_bottom, cloud_bottom_future 아래
    처음 60개는 베이스, 이후 급락.
    """
    closes = [100.0] * n
    for i in range(n - 30, n):
        closes[i] = 100.0 - (i - (n - 30)) * 2.0  # 100 → 40
    df = _make_df(n=n, close_values=closes)
    return df


# ── 인스턴스 / 이름 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert EMACloudStrategy().name == "ema_cloud"


def test_strategy_instantiable():
    assert EMACloudStrategy() is not None


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = EMACloudStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    s = EMACloudStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.reasoning != ""


def test_exactly_59_rows_returns_hold():
    s = EMACloudStrategy()
    df = _make_df(n=59)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── Signal 공통 필드 ──────────────────────────────────────────────────────────

def test_signal_has_reasoning():
    s = EMACloudStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


def test_signal_strategy_field():
    s = EMACloudStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.strategy == "ema_cloud"


def test_entry_price_positive_on_hold():
    s = EMACloudStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    # flat data → HOLD, but entry_price should be 0 only for insufficient data
    assert sig.entry_price >= 0.0


def test_entry_price_positive_on_buy():
    s = EMACloudStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price > 0.0


def test_entry_price_positive_on_sell():
    s = EMACloudStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price > 0.0


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_action():
    s = EMACloudStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_signal_confidence_not_low():
    s = EMACloudStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_signal_entry_price_equals_last_close():
    s = EMACloudStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_action():
    s = EMACloudStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_signal_confidence_not_low():
    s = EMACloudStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_signal_entry_price_equals_last_close():
    s = EMACloudStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── HOLD ──────────────────────────────────────────────────────────────────────

def test_hold_on_flat_data():
    s = EMACloudStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = EMACloudStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW
