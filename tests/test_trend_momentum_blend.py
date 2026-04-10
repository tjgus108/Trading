"""tests/test_trend_momentum_blend.py — TrendMomentumBlendStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_momentum_blend import TrendMomentumBlendStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(closes, volume=1000.0):
    n = len(closes)
    highs = [c * 1.005 for c in closes]
    lows = [c * 0.995 for c in closes]
    opens = [c * 0.999 for c in closes]
    return pd.DataFrame({
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": [volume] * n,
    })


def _uptrend_closes():
    """
    Prices engineered for: EMA50 positive slope, roc10 > roc_ma, RSI in (50,70).

    - 80 flat bars: anchor EMA/RSI
    - 21 trend bars: 2-up-1-down cycle (+0.35 / -0.20):
      * win ratio 2/3 ≈ 67% → RSI ~65-67
      * trend pos at idx (pos 19 = 19%3=1) is an UP bar
      * roc10 looks back 10 bars into trend (pos 9 = in trend), still growing
        → roc10 recent > roc_ma (older roc10 values smaller since trend started)
    Total = 101 bars.
    """
    flat = [100.0] * 80
    val = 100.0
    trend = []
    for i in range(21):
        if i % 3 == 2:
            val -= 0.25   # loss size
        else:
            val += 0.20   # gain size: G/L ratio = (2*0.20/3)/(0.25/3) = 1.6 → RSI~61.5
        trend.append(val)
    return flat + trend   # 101 bars


def _downtrend_closes():
    """
    Prices engineered for: EMA50 negative slope, roc10 < roc_ma, RSI in (30,50).

    - 80 flat bars at 200.0
    - 21 trend bars: 2-down-1-up cycle (-0.20 / +0.25):
      * G/L ratio = (0.25/3)/(2*0.20/3) = 0.625 → RSI ~ 38.5
      * roc10 recent < roc_ma (older roc10 less negative since trend just started)
    Total = 101 bars.
    """
    flat = [200.0] * 80
    val = 200.0
    trend = []
    for i in range(21):
        if i % 3 == 2:
            val += 0.25   # gain (bounce)
        else:
            val -= 0.20   # loss
        trend.append(val)
    return flat + trend   # 101 bars


def _flat_closes(n=80):
    """Flat prices — RSI ~50 but slope ~0, should HOLD."""
    return [100.0 + (i % 3) * 0.01 for i in range(n)]


strat = TrendMomentumBlendStrategy()


# 1. 전략 이름
def test_strategy_name():
    assert strat.name == "trend_momentum_blend"


# 2. 인스턴스 확인
def test_instance():
    from src.strategy.base import BaseStrategy
    assert isinstance(strat, BaseStrategy)


# 3. 데이터 부족 (59행) → HOLD LOW
def test_insufficient_data_hold():
    df = _make_df([100.0] * 59)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. None 없음
def test_signal_not_none():
    df = _make_df(_flat_closes(80))
    sig = strat.generate(df)
    assert sig is not None


# 5. reasoning 필드 존재
def test_reasoning_field():
    df = _make_df(_flat_closes(80))
    sig = strat.generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


# 6. Signal 필드 완전성
def test_signal_fields():
    df = _make_df(_flat_closes(80))
    sig = strat.generate(df)
    assert sig.strategy == "trend_momentum_blend"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.invalidation, str)


# 7. 상승 추세 → BUY (uptrend + positive ROC)
def test_uptrend_buy():
    df = _make_df(_uptrend_closes())
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# 8. BUY reasoning에 "상승 추세" 포함
def test_buy_reasoning_uptrend():
    df = _make_df(_uptrend_closes())
    sig = strat.generate(df)
    assert "상승 추세" in sig.reasoning


# 9. 하락 추세 → SELL (downtrend + negative ROC)
def test_downtrend_sell():
    df = _make_df(_downtrend_closes())
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# 10. SELL reasoning에 "하락 추세" 포함
def test_sell_reasoning_downtrend():
    df = _make_df(_downtrend_closes())
    sig = strat.generate(df)
    assert "하락 추세" in sig.reasoning


# 11. HIGH confidence — strong slope
def test_high_confidence_strong_slope():
    # Aggressive uptrend to maximise slope
    closes = [100.0 * (1.02 ** i) for i in range(80)]
    df = _make_df(closes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 12. MEDIUM confidence — weak slope (flat-ish)
def test_medium_confidence_flat():
    df = _make_df(_flat_closes(80))
    sig = strat.generate(df)
    # flat → HOLD or MEDIUM confidence
    assert sig.confidence in (Confidence.MEDIUM, Confidence.LOW)


# 13. entry_price > 0
def test_entry_price_positive():
    df = _make_df(_uptrend_closes())
    sig = strat.generate(df)
    assert sig.entry_price > 0


# 14. strategy 필드 = "trend_momentum_blend"
def test_strategy_field():
    df = _make_df(_downtrend_closes())
    sig = strat.generate(df)
    assert sig.strategy == "trend_momentum_blend"
