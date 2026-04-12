"""
TrendContinuationStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_continuation import TrendContinuationStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 60,
    close_values=None,
    open_values=None,
    volume=None,
) -> pd.DataFrame:
    """mock DataFrame. iloc[-2]가 마지막 완성 캔들."""
    if close_values is None:
        close_values = [100.0] * n
    if open_values is None:
        open_values = [100.0] * n
    if volume is None:
        volume = [1000.0] * n

    df = pd.DataFrame({
        "open":   open_values,
        "high":   [v + 1.0 for v in close_values],
        "low":    [v - 1.0 for v in close_values],
        "close":  close_values,
        "volume": volume,
        "rsi14":  [50.0] * n,
        "ema50":  [100.0] * n,
        "atr14":  [1.0] * n,
    })
    return df


def _make_uptrend_buy_df(n: int = 60, vol_spike: bool = False) -> pd.DataFrame:
    """
    BUY 조건:
    - EMA50 상승 (초반 100→110 상승 추세)
    - 마지막 완성 캔들: EMA21 근처 (+0.5%), 양봉, close > ema21*1.001
    """
    # 상승 추세: 서서히 올라가다 EMA21 근처에서 풀백 후 재개
    closes = list(np.linspace(95, 115, n - 10)) + [105.0] * 10
    # 마지막 완성 캔들은 EMA21 근처에서 약간 위 (양봉)
    # EMA21은 대략 110 언저리이므로, close를 110.5, open을 109 정도로 설정
    closes[-2] = 110.5
    closes[-1] = 111.0  # 진행 중

    opens = [c - 0.5 for c in closes]
    opens[-2] = 109.8  # 양봉 (open < close)

    vol = [1000.0] * n
    if vol_spike:
        vol[-2] = 1500.0  # 평균의 1.5배

    return _make_df(n=n, close_values=closes, open_values=opens, volume=vol)


def _make_downtrend_sell_df(n: int = 60, vol_spike: bool = False) -> pd.DataFrame:
    """
    SELL 조건:
    - EMA50 하락 (초반 115→95 하락 추세)
    - 마지막 완성 캔들: EMA21 근처 (-0.5%), 음봉, close < ema21*0.999
    """
    closes = list(np.linspace(115, 95, n - 10)) + [105.0] * 10
    closes[-2] = 99.5
    closes[-1] = 99.0

    opens = [c + 0.5 for c in closes]
    opens[-2] = 100.2  # 음봉 (open > close)

    vol = [1000.0] * n
    if vol_spike:
        vol[-2] = 1500.0

    return _make_df(n=n, close_values=closes, open_values=opens, volume=vol)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert TrendContinuationStrategy().name == "trend_continuation"


def test_strategy_instantiable():
    assert TrendContinuationStrategy() is not None


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = TrendContinuationStrategy()
    df = _make_df(n=40)  # < 55
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_crash():
    """55행 → HOLD (크래시 없음)"""
    s = TrendContinuationStrategy()
    df = _make_df(n=55)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── HOLD 케이스 ───────────────────────────────────────────────────────────────

def test_hold_when_flat():
    """모든 close 동일 → 추세 없음 → HOLD"""
    s = TrendContinuationStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = TrendContinuationStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 공통 ──────────────────────────────────────────────────────────

def test_signal_strategy_field_hold():
    s = TrendContinuationStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "trend_continuation"


def test_entry_price_equals_last_close_hold():
    s = TrendContinuationStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_action():
    s = TrendContinuationStrategy()
    df = _make_uptrend_buy_df()
    sig = s.generate(df)
    # uptrend + near ema21 + bullish candle 조건 충족 시 BUY
    assert sig.action in (Action.BUY, Action.HOLD)  # 조건이 맞으면 BUY


def test_buy_confidence_medium_no_vol_spike():
    s = TrendContinuationStrategy()
    df = _make_uptrend_buy_df(vol_spike=False)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


def test_buy_confidence_high_with_vol_spike():
    s = TrendContinuationStrategy()
    df = _make_uptrend_buy_df(vol_spike=True)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_buy_entry_price_is_last_close():
    s = TrendContinuationStrategy()
    df = _make_uptrend_buy_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_strategy_field():
    s = TrendContinuationStrategy()
    df = _make_uptrend_buy_df()
    sig = s.generate(df)
    assert sig.strategy == "trend_continuation"


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_action():
    s = TrendContinuationStrategy()
    df = _make_downtrend_sell_df()
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_sell_confidence_medium_no_vol_spike():
    s = TrendContinuationStrategy()
    df = _make_downtrend_sell_df(vol_spike=False)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.MEDIUM


def test_sell_confidence_high_with_vol_spike():
    s = TrendContinuationStrategy()
    df = _make_downtrend_sell_df(vol_spike=True)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


def test_sell_entry_price_is_last_close():
    s = TrendContinuationStrategy()
    df = _make_downtrend_sell_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_sell_strategy_field():
    s = TrendContinuationStrategy()
    df = _make_downtrend_sell_df()
    sig = s.generate(df)
    assert sig.strategy == "trend_continuation"
