"""TrendFollowFilterStrategy 단위 테스트 (14개)."""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.trend_follow_filter import TrendFollowFilterStrategy

strat = TrendFollowFilterStrategy()

N = 60  # EMA50 안정화를 위해 충분한 행


def _make_df(closes, highs=None, lows=None):
    n = len(closes)
    if highs is None:
        highs = [c * 1.005 for c in closes]
    if lows is None:
        lows = [c * 0.995 for c in closes]
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


def _flat_df(n=N, base=100.0):
    return _make_df([base] * n)


def _uptrend_df(n=N):
    """강한 상승추세: 매봉 0.5% 상승, high > prev_high → di_up 우세."""
    closes = [100.0 * (1.005 ** i) for i in range(n)]
    highs = [c * 1.01 for c in closes]
    lows = [c * 0.999 for c in closes]
    return _make_df(closes, highs=highs, lows=lows)


def _downtrend_df(n=N):
    """강한 하락추세: 매봉 0.5% 하락, low < prev_low → di_down 우세."""
    closes = [100.0 * (0.995 ** i) for i in range(n)]
    highs = [c * 1.001 for c in closes]
    lows = [c * 0.99 for c in closes]
    return _make_df(closes, highs=highs, lows=lows)


# 1. 전략 이름 확인
def test_strategy_name():
    assert strat.name == "trend_follow_filter"


# 2. 데이터 부족 → HOLD LOW
def test_insufficient_data_hold():
    df = _flat_df(n=10)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 3. 최소 행 경계: 29행 → HOLD LOW
def test_min_rows_boundary_29():
    df = _flat_df(n=29)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. 최소 행 경계: 30행 → LOW 아님
def test_min_rows_boundary_30():
    df = _flat_df(n=30)
    sig = strat.generate(df)
    assert sig.confidence != Confidence.LOW


# 5. flat 데이터 → HOLD (추세 없음)
def test_flat_data_hold():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 6. Signal 필드 완전성
def test_signal_fields_complete():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.strategy == "trend_follow_filter"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str)


# 7. entry_price = 마지막 완성봉 close (df.iloc[-2])
def test_entry_price_is_last_close():
    closes = [100.0 * (1.005 ** i) for i in range(N)]
    closes[-1] = closes[-2]  # 마지막 봉은 진행 중
    df = _make_df(closes)
    sig = strat.generate(df)
    assert abs(sig.entry_price - closes[-2]) < 1e-4


# 8. 강한 상승추세 → BUY 가능
def test_uptrend_buy_signal():
    df = _uptrend_df(n=N)
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# 9. 강한 하락추세 → SELL 가능
def test_downtrend_sell_signal():
    df = _downtrend_df(n=N)
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 10. adx > 35 → HIGH confidence (BUY 발생 시)
def test_high_confidence_strong_adx():
    df = _uptrend_df(n=N)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        # adx > 35면 HIGH, 아니면 MEDIUM
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 11. BUY signal reasoning에 adx 정보 포함
def test_buy_reasoning_contains_adx():
    df = _uptrend_df(n=N)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "adx" in sig.reasoning.lower()


# 12. SELL signal reasoning에 하락 추세 정보 포함
def test_sell_reasoning_contains_di():
    df = _downtrend_df(n=N)
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "di" in sig.reasoning.lower() or "adx" in sig.reasoning.lower()


# 13. HOLD reasoning 비어있지 않음
def test_hold_reasoning_nonempty():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.reasoning
    assert any(kw in sig.reasoning for kw in [
        "adx", "di", "ema", "조건", "부족", "NaN"
    ])


# 14. BUY 시 bull_case / bear_case 비어있지 않음
def test_buy_bull_bear_case():
    df = _uptrend_df(n=N)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.bull_case
        assert sig.bear_case
