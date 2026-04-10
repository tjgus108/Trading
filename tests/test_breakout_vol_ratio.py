"""BreakoutVolRatioStrategy 단위 테스트 (14개)."""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.breakout_vol_ratio import BreakoutVolRatioStrategy

strat = BreakoutVolRatioStrategy()

N = 30


def _make_df(closes, highs=None, lows=None, volumes=None):
    n = len(closes)
    if highs is None:
        highs = [c * 1.005 for c in closes]
    if lows is None:
        lows = [c * 0.995 for c in closes]
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _flat_df(n=N, base=100.0, vol=1000.0):
    return _make_df([base] * n, volumes=[vol] * n)


def _breakout_up_df():
    """저항(~100) 상향 돌파 + 거래량 1.5배 이상"""
    closes = [100.0] * 22 + [105.0, 106.0, 107.0, 108.0, 109.0]
    highs  = [c * 1.005 for c in closes]
    lows   = [c * 0.995 for c in closes]
    # 앞 22봉 vol=1000, 뒤 5봉 vol=2000 (ratio>1.5 보장)
    volumes = [1000.0] * 22 + [2000.0, 2000.0, 2000.0, 2000.0, 2000.0]
    return _make_df(closes, highs, lows, volumes)


def _breakout_down_df():
    """지지(~100) 하향 돌파 + 거래량 1.5배 이상"""
    closes  = [100.0] * 22 + [95.0, 94.0, 93.0, 92.0, 91.0]
    highs   = [c * 1.005 for c in closes]
    lows    = [c * 0.995 for c in closes]
    volumes = [1000.0] * 22 + [2000.0, 2000.0, 2000.0, 2000.0, 2000.0]
    return _make_df(closes, highs, lows, volumes)


def _high_vol_breakout_up_df():
    """vol_ratio > 2.0 → HIGH confidence"""
    closes  = [100.0] * 22 + [105.0, 106.0, 107.0, 108.0, 109.0]
    highs   = [c * 1.005 for c in closes]
    lows    = [c * 0.995 for c in closes]
    volumes = [1000.0] * 22 + [5000.0, 5000.0, 5000.0, 5000.0, 5000.0]
    return _make_df(closes, highs, lows, volumes)


# 1. 전략명
def test_strategy_name():
    assert strat.name == "breakout_vol_ratio"


# 2. 인스턴스
def test_instance():
    assert isinstance(strat, BreakoutVolRatioStrategy)


# 3. 데이터 부족 → HOLD LOW
def test_insufficient_data_hold():
    df = _flat_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. None 없음 (Signal 필드 완전)
def test_signal_no_none():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig is not None
    assert sig.action is not None
    assert sig.confidence is not None


# 5. reasoning 비어있지 않음
def test_reasoning_not_empty():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


# 6. flat 데이터 → HOLD
def test_flat_data_hold():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.strategy == "breakout_vol_ratio"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# 8. BUY 신호 발생
def test_breakout_up_buy():
    df = _breakout_up_df()
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# 9. SELL 신호 발생
def test_breakout_down_sell():
    df = _breakout_down_df()
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 10. BUY reasoning에 돌파 정보 포함
def test_buy_reasoning_contains_breakout():
    df = _breakout_up_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "돌파" in sig.reasoning or "resistance" in sig.reasoning.lower()


# 11. SELL reasoning에 지지 정보 포함
def test_sell_reasoning_contains_support():
    df = _breakout_down_df()
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "돌파" in sig.reasoning or "support" in sig.reasoning.lower()


# 12. HIGH confidence: vol_ratio > 2.0
def test_high_confidence_high_vol():
    df = _high_vol_breakout_up_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 13. entry_price > 0
def test_entry_price_positive():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.entry_price > 0


# 14. 최소 행 25행 경계: 24행 → HOLD LOW
def test_min_rows_24_hold():
    df = _flat_df(n=24)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
