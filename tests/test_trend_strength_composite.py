"""
TrendStrengthCompositeStrategy 단위 테스트
"""

import pandas as pd
import pytest

from src.strategy.trend_strength_composite import TrendStrengthCompositeStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, close_values=None, volume_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    highs = [c * 1.005 for c in close_values]
    lows = [c * 0.995 for c in close_values]
    if volume_values is None:
        volume_values = [1000.0] * n
    return pd.DataFrame({
        "open": close_values,
        "high": highs,
        "low": lows,
        "close": close_values,
        "volume": volume_values,
    })


def _make_buy_df(n: int = 60) -> pd.DataFrame:
    """
    강한 상승 추세: ADX > 25, price > EMA20, DI+ > DI-, volume surge
    초반 베이스 후 강한 상승으로 ADX 높이고 DI+ 우세 유도.
    """
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    volumes = [1000.0] * n

    # 강한 상승 트렌드 (마지막 20개 강한 상승)
    for i in range(n - 20, n):
        closes[i] = 100.0 + (i - (n - 20)) * 3.0
        highs[i] = closes[i] + 2.0
        lows[i] = closes[i] - 0.5
        volumes[i] = 5000.0  # volume surge

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_sell_df(n: int = 60) -> pd.DataFrame:
    """
    강한 하락 추세: ADX > 25, price < EMA20, DI- > DI+, volume surge
    """
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    volumes = [1000.0] * n

    for i in range(n - 20, n):
        closes[i] = 100.0 - (i - (n - 20)) * 3.0
        highs[i] = closes[i] + 0.5
        lows[i] = closes[i] - 2.0
        volumes[i] = 5000.0  # volume surge

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


# ── 인스턴스 / 이름 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert TrendStrengthCompositeStrategy().name == "trend_strength_composite"


def test_strategy_instantiable():
    assert TrendStrengthCompositeStrategy() is not None


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.reasoning != ""


def test_exactly_29_rows_returns_hold():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=29)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── Signal 공통 필드 ──────────────────────────────────────────────────────────

def test_signal_has_reasoning():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


def test_signal_strategy_field():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.strategy == "trend_strength_composite"


def test_entry_price_nonnegative():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.entry_price >= 0.0


def test_entry_price_positive_on_buy():
    s = TrendStrengthCompositeStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price > 0.0


def test_entry_price_positive_on_sell():
    s = TrendStrengthCompositeStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price > 0.0


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_action():
    s = TrendStrengthCompositeStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_signal_confidence_not_low():
    s = TrendStrengthCompositeStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_signal_entry_price_equals_last_close():
    s = TrendStrengthCompositeStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_action():
    s = TrendStrengthCompositeStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_signal_confidence_not_low():
    s = TrendStrengthCompositeStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_signal_entry_price_equals_last_close():
    s = TrendStrengthCompositeStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── HOLD ──────────────────────────────────────────────────────────────────────

def test_hold_on_flat_data():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = TrendStrengthCompositeStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW
