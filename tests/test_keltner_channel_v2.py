"""
KeltnerChannelV2Strategy 단위 테스트 (14개)
"""

import pandas as pd
import pytest

from src.strategy.keltner_channel_v2 import KeltnerChannelV2Strategy
from src.strategy.base import Action, Confidence


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, close_values=None, high_values=None, low_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    if high_values is None:
        high_values = [c * 1.01 for c in close_values]
    if low_values is None:
        low_values = [c * 0.99 for c in close_values]
    return pd.DataFrame({
        "open":   close_values,
        "high":   high_values,
        "low":    low_values,
        "close":  close_values,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """
    iloc[-2]에서 close < lower 이탈 AND close > prev_close (반등).
    EMA20 ≈ 100, ATR14 ≈ 2 → lower ≈ 96.
    [-3]: 95 (하단 이탈), [-2]: 94 → 93 → 94로 반등.
    실제: [-3]=93, [-2]=94 (전봉 대비 상승, lower 아래)
    """
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0]  * n
    # 마지막 몇 봉을 낮게 설정해 EMA를 끌어내리고 lower 아래로 이탈
    for i in range(n - 4, n):
        closes[i] = 70.0
        highs[i]  = 71.0
        lows[i]   = 69.0
    # [-2]: lower 아래이면서 prev_close보다 위 (반등)
    closes[-3] = 68.0
    closes[-2] = 69.0  # 68 → 69 상승
    highs[-2]  = 70.0
    lows[-2]   = 68.0
    closes[-1] = 100.0  # 현재 진행 중 캔들 (무시됨)
    return pd.DataFrame({
        "open":   closes,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": [1000.0] * n,
    })


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """
    iloc[-2]에서 close > upper 이탈 AND close < prev_close (반락).
    """
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0]  * n
    for i in range(n - 4, n):
        closes[i] = 130.0
        highs[i]  = 131.0
        lows[i]   = 129.0
    closes[-3] = 132.0
    closes[-2] = 131.0  # 132 → 131 하락
    highs[-2]  = 133.0
    lows[-2]   = 130.0
    closes[-1] = 100.0
    return pd.DataFrame({
        "open":   closes,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": [1000.0] * n,
    })


# ── 기본 ───────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert KeltnerChannelV2Strategy().name == "keltner_channel_v2"


def test_strategy_instantiable():
    assert KeltnerChannelV2Strategy() is not None


# ── 데이터 부족 ────────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = KeltnerChannelV2Strategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_crash():
    s = KeltnerChannelV2Strategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY ────────────────────────────────────────────────────────────────────────

def test_buy_signal_below_lower():
    s = KeltnerChannelV2Strategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_not_low():
    s = KeltnerChannelV2Strategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_entry_price_is_last_close():
    s = KeltnerChannelV2Strategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_reasoning_mentions_lower():
    s = KeltnerChannelV2Strategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert "lower" in sig.reasoning


# ── SELL ───────────────────────────────────────────────────────────────────────

def test_sell_signal_above_upper():
    s = KeltnerChannelV2Strategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_not_low():
    s = KeltnerChannelV2Strategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_entry_price_is_last_close():
    s = KeltnerChannelV2Strategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_sell_reasoning_mentions_upper():
    s = KeltnerChannelV2Strategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert "upper" in sig.reasoning


# ── HOLD ───────────────────────────────────────────────────────────────────────

def test_hold_flat_market():
    s = KeltnerChannelV2Strategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = KeltnerChannelV2Strategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


def test_signal_strategy_field():
    s = KeltnerChannelV2Strategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.strategy == "keltner_channel_v2"
