"""
HigherHighMomentumStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.higher_high_momentum import HigherHighMomentumStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 30,
    close_values=None,
    high_values=None,
    low_values=None,
    volume_values=None,
) -> pd.DataFrame:
    """mock DataFrame 생성. _last() = iloc[-2]"""
    if close_values is None:
        close_values = [100.0] * n
    if high_values is None:
        high_values = [v + 2.0 for v in close_values]
    if low_values is None:
        low_values = [v - 2.0 for v in close_values]
    if volume_values is None:
        volume_values = [1000.0] * n

    return pd.DataFrame({
        "open":   [c - 0.5 for c in close_values],
        "high":   high_values,
        "low":    low_values,
        "close":  close_values,
        "volume": volume_values,
    })


def _rising_series(n: int, start: float = 90.0, step: float = 1.0):
    """단조 상승하는 가격 시리즈 생성"""
    return [start + i * step for i in range(n)]


def _falling_series(n: int, start: float = 110.0, step: float = 1.0):
    """단조 하락하는 가격 시리즈 생성"""
    return [start - i * step for i in range(n)]


# ── 기본 인스턴스 ─────────────────────────────────────────────────────────────

def test_strategy_name():
    s = HigherHighMomentumStrategy()
    assert s.name == "higher_high_momentum"


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = HigherHighMomentumStrategy()
    df = _make_df(n=20)  # < 25
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exact_min_rows_does_not_error():
    s = HigherHighMomentumStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_higher_high_higher_low_positive_roc():
    """상승 구조 + roc3 > 0 → BUY"""
    s = HigherHighMomentumStrategy()
    n = 30
    # 단조 상승 → hh5 > hh5_prev, ll5 > ll5_prev, roc3 > 0
    closes = _rising_series(n, start=90.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_high_confidence_on_volume_surge():
    """거래량이 MA * 1.3 초과 시 HIGH confidence"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _rising_series(n, start=90.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    # 완성 캔들([-2])의 거래량을 충분히 크게
    volumes = [1000.0] * n
    volumes[-2] = 2000.0  # MA(10) ≈ 1000, 2000 > 1000 * 1.3
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows, volume_values=volumes)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence_on_normal_volume():
    """거래량 일반적 → MEDIUM confidence BUY"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _rising_series(n, start=90.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    volumes = [1000.0] * n  # 균일 → vol/vol_ma == 1.0 < 1.3
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows, volume_values=volumes)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_buy_entry_price_is_last_close():
    """entry_price == iloc[-2].close"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _rising_series(n, start=90.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(closes[-2])


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_lower_low_lower_high_negative_roc():
    """하락 구조 + roc3 < 0 → SELL"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _falling_series(n, start=110.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_high_confidence_on_volume_surge():
    """하락 + 거래량 급증 → SELL HIGH"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _falling_series(n, start=110.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    volumes = [1000.0] * n
    volumes[-2] = 2000.0
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows, volume_values=volumes)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_strategy_name_in_signal():
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _falling_series(n, start=110.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    assert sig.strategy == "higher_high_momentum"


# ── HOLD 케이스 ───────────────────────────────────────────────────────────────

def test_hold_flat_market():
    """가격 횡보 → hh5/ll5 변화 없음 → HOLD"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = [100.0] * n
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_higher_high_but_negative_roc():
    """hh5>hh5_prev, ll5>ll5_prev 이지만 roc3 < 0 → HOLD"""
    s = HigherHighMomentumStrategy()
    n = 30
    # 전반 상승 후 마지막 완성 캔들만 급락 (roc3 < 0)
    closes = _rising_series(n, start=90.0, step=1.0)
    # 완성 캔들([-2])의 close를 3봉 전보다 낮게
    closes[-2] = closes[-5] - 1.0
    closes[-1] = closes[-2]  # 진행 중 캔들
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    # roc3 < 0 이므로 BUY 조건 불충족
    assert sig.action in (Action.HOLD, Action.SELL)


def test_hold_returns_low_confidence():
    s = HigherHighMomentumStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ──────────────────────────────────────────────────────────

def test_signal_fields_present():
    """Signal 객체의 필수 필드가 모두 설정됨"""
    s = HigherHighMomentumStrategy()
    n = 30
    closes = _rising_series(n, start=90.0, step=1.0)
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    assert sig.reasoning
    assert sig.strategy == "higher_high_momentum"
    assert isinstance(sig.entry_price, float)
