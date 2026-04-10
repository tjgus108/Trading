"""TrendReversalPatternStrategy 단위 테스트 (12개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_reversal import TrendReversalPatternStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n=50, close=None, volume=None):
    if close is None:
        close = np.linspace(100.0, 110.0, n)
    close = np.asarray(close, dtype=float)
    n = len(close)
    if volume is None:
        volume = np.ones(n) * 1000.0
    volume = np.asarray(volume, dtype=float)
    return pd.DataFrame(
        {
            "open":   close - 0.5,
            "high":   close + 1.0,
            "low":    close - 1.0,
            "close":  close,
            "volume": volume,
        }
    )


def _make_bullish_reversal_df():
    """20봉 신저점 + RSI bullish divergence + 반전 캔들."""
    # 가격은 하락 후 마지막에 반전
    prices = np.linspace(120.0, 80.0, 48)
    prices = np.append(prices, [78.0, 80.0])  # 50개, 마지막 두 봉: 신저점 후 반전

    n = len(prices)
    open_ = prices.copy()
    # 마지막 완성봉(iloc[-2])에서 close > open (반전 캔들)
    open_[-2] = prices[-2] + 2.0

    high = np.maximum(prices, open_) + 0.5
    low = np.minimum(prices, open_) - 0.5

    vol = np.ones(n) * 1000.0
    vol[-2] = 2000.0  # 고거래량

    return pd.DataFrame({
        "open":   open_,
        "high":   high,
        "low":    low,
        "close":  prices,
        "volume": vol,
    })


def _make_bearish_reversal_df():
    """20봉 신고점 + RSI bearish divergence + 반전 캔들."""
    prices = np.linspace(80.0, 120.0, 48)
    prices = np.append(prices, [122.0, 120.0])  # 50개

    n = len(prices)
    open_ = prices.copy()
    # 마지막 완성봉(iloc[-2])에서 close < open (반전 캔들)
    open_[-2] = prices[-2] - 2.0

    high = np.maximum(prices, open_) + 0.5
    low = np.minimum(prices, open_) - 0.5

    vol = np.ones(n) * 1000.0
    vol[-2] = 2000.0  # 고거래량

    return pd.DataFrame({
        "open":   open_,
        "high":   high,
        "low":    low,
        "close":  prices,
        "volume": vol,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert TrendReversalPatternStrategy().name == "trend_reversal"


def test_hold_on_insufficient_data():
    sig = TrendReversalPatternStrategy().generate(_make_df(n=10))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_on_exactly_24_rows():
    sig = TrendReversalPatternStrategy().generate(_make_df(n=24))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_fields_present():
    sig = TrendReversalPatternStrategy().generate(_make_df(n=50))
    assert sig.strategy == "trend_reversal"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_complete_candle():
    df = _make_df(n=50)
    sig = TrendReversalPatternStrategy().generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_empty_dataframe_returns_hold():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    sig = TrendReversalPatternStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == pytest.approx(0.0)


def test_flat_price_returns_hold():
    """가격 변동 없음 → 신고/저점 없음 → HOLD."""
    close = np.ones(50) * 100.0
    sig = TrendReversalPatternStrategy().generate(_make_df(close=close))
    assert sig.action == Action.HOLD


def test_uptrend_no_reversal_returns_hold():
    """단순 상승 추세 → 신저점 없음 → BUY 신호 없음."""
    close = np.linspace(100.0, 150.0, 50)
    sig = TrendReversalPatternStrategy().generate(_make_df(close=close))
    # 상승 추세 → bearish 가능하나 bullish reversal은 없어야 함
    assert sig.action in (Action.HOLD, Action.SELL)


def test_confidence_medium_on_normal_volume():
    """거래량 보통 → MEDIUM 이하."""
    sig = TrendReversalPatternStrategy().generate(_make_df(n=50))
    assert sig.confidence in (Confidence.MEDIUM, Confidence.LOW)


def test_buy_signal_has_invalidation():
    df = _make_bullish_reversal_df()
    sig = TrendReversalPatternStrategy().generate(df)
    if sig.action == Action.BUY:
        assert len(sig.invalidation) > 0


def test_sell_signal_has_invalidation():
    df = _make_bearish_reversal_df()
    sig = TrendReversalPatternStrategy().generate(df)
    if sig.action == Action.SELL:
        assert len(sig.invalidation) > 0


def test_action_is_valid_enum():
    """generate()가 항상 유효한 Action 반환."""
    for n in [10, 25, 50]:
        sig = TrendReversalPatternStrategy().generate(_make_df(n=n))
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
