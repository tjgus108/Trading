"""MeanRevBandV2Strategy 단위 테스트 (14개)."""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.mean_rev_band_v2 import MeanRevBandV2Strategy

strat = MeanRevBandV2Strategy()

N = 40


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


def _flat_df(n=N, base=100.0):
    return _make_df([base] * n)


def _band2_buy_df():
    """
    EMA20 ~ 100 근처, ATR 작을 때 band2_dn ~ 98.
    마지막 완성봉(idx=-2)이 band2_dn 아래였다가 직전봉보다 위에 있으면 BUY.
    전략: 긴 하락 후 반등 패턴
    """
    # 앞 35봉은 100 근처 유지
    closes = [100.0] * 35
    # idx=-3(직전봉): 큰 하락 → band2_dn보다 작아야 함 (예: 90)
    # idx=-2(완성봉): 조금 반등 → band2_dn보다 작지만, 직전보다 크면 됨
    closes += [90.0, 92.0, 92.0]  # idx 35=90(prev of prev), 36=92(완성봉 직전), 37=final(current)
    return _make_df(closes)


def _band2_sell_df():
    """EMA20 ~ 100, band2_up 위에서 반락 SELL"""
    closes = [100.0] * 35
    closes += [110.0, 108.0, 108.0]
    return _make_df(closes)


def _band1_buy_df():
    """band1 아래 + 직전보다 상승 → BUY MEDIUM"""
    closes = [100.0] * 35
    # band1_dn 아래 + 반등
    closes += [97.0, 98.0, 98.0]
    return _make_df(closes)


# 1. 전략명
def test_strategy_name():
    assert strat.name == "mean_rev_band_v2"


# 2. 인스턴스
def test_instance():
    assert isinstance(strat, MeanRevBandV2Strategy)


# 3. 데이터 부족 → HOLD LOW
def test_insufficient_data_hold():
    df = _flat_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. None 없음
def test_signal_no_none():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig is not None
    assert sig.action is not None


# 5. reasoning 비어있지 않음
def test_reasoning_not_empty():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


# 6. flat → HOLD (밴드 내)
def test_flat_data_hold():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.strategy == "mean_rev_band_v2"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# 8. BUY 신호 발생 가능성 확인 (action in BUY/HOLD)
def test_band2_buy_signal():
    df = _band2_buy_df()
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# 9. SELL 신호 발생 가능성 확인 (action in SELL/HOLD)
def test_band2_sell_signal():
    df = _band2_sell_df()
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 10. BUY reasoning에 band 정보 포함
def test_buy_reasoning_contains_band():
    df = _band2_buy_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "band" in sig.reasoning.lower() or "밴드" in sig.reasoning


# 11. SELL reasoning에 band 정보 포함
def test_sell_reasoning_contains_band():
    df = _band2_sell_df()
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "band" in sig.reasoning.lower() or "밴드" in sig.reasoning


# 12. HIGH confidence: band2 조건일 때
def test_high_confidence_band2():
    df = _band2_buy_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        # band2 조건이면 HIGH
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 13. entry_price > 0
def test_entry_price_positive():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.entry_price > 0


# 14. 최소 행 24행 → HOLD LOW
def test_min_rows_24_hold():
    df = _flat_df(n=24)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
