"""
MeanReversionBandStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mean_rev_band import MeanReversionBandStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 40, close_values=None, open_values=None, volume=None) -> pd.DataFrame:
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


def _make_buy_df(n: int = 50) -> pd.DataFrame:
    """
    BUY 조건: close[-2] < lower_band[-2] AND close[-2] > lower_band[-3]

    구조 (period=30, idx_last_complete = n-2 = 48):
    - window[-2] = [19..48]: 모두 100 → mean=100, std=0 → lower_band[48]=100
    - window[-3] = [18..47]: idx 18에 아웃라이어(10) → mean≈97, std≈16 → lower_band[47]≈72
    - close[48] = 85 → 85 < 100 (✓) AND 85 > 72 (✓) → BUY
    """
    closes = [100.0] * n
    closes[n - 32] = 10.0   # idx=18 (window[-3]에만 포함, window[-2]에서 제외)
    closes[-2] = 85.0        # lower_band[-2]=100보다 낮고 lower_band[-3]≈72보다 높음
    closes[-1] = 88.0
    return _make_df(n=n, close_values=closes)


def _make_sell_df(n: int = 50) -> pd.DataFrame:
    """
    SELL 조건: close[-2] > upper_band[-2] AND close[-2] < upper_band[-3]

    구조 (period=30, idx_last_complete = n-2 = 48):
    - window[-2] = [19..48]: 모두 100 → mean=100, std=0 → upper_band[48]=100
    - window[-3] = [18..47]: idx 18에 아웃라이어(190) → mean≈103, std≈16 → upper_band[47]≈127
    - close[48] = 115 → 115 > 100 (✓) AND 115 < 127 (✓) → SELL
    """
    closes = [100.0] * n
    closes[n - 32] = 190.0  # idx=18 (window[-3]에만 포함)
    closes[-2] = 115.0       # upper_band[-2]=100보다 높고 upper_band[-3]≈127보다 낮음
    closes[-1] = 112.0
    return _make_df(n=n, close_values=closes)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert MeanReversionBandStrategy().name == "mean_rev_band"


def test_strategy_instantiable():
    assert MeanReversionBandStrategy() is not None


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MeanReversionBandStrategy()
    df = _make_df(n=30)  # < 35
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_crash():
    """35행 → HOLD (신호 없음, 크래시 없음)"""
    s = MeanReversionBandStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_generated():
    s = MeanReversionBandStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_not_low():
    s = MeanReversionBandStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_entry_price_is_last_close():
    s = MeanReversionBandStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_reasoning_contains_lower():
    s = MeanReversionBandStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "lower" in sig.reasoning or "하단" in sig.reasoning


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_generated():
    s = MeanReversionBandStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_not_low():
    s = MeanReversionBandStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_entry_price_is_last_close():
    s = MeanReversionBandStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_sell_reasoning_contains_upper():
    s = MeanReversionBandStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "upper" in sig.reasoning or "상단" in sig.reasoning


# ── HOLD 케이스 ───────────────────────────────────────────────────────────────

def test_hold_when_close_flat():
    """모든 close 동일 → z=0 → 밴드 조건 미충족 → HOLD"""
    s = MeanReversionBandStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = MeanReversionBandStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ──────────────────────────────────────────────────────────

def test_signal_strategy_field_buy():
    s = MeanReversionBandStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.strategy == "mean_rev_band"


def test_signal_strategy_field_hold():
    s = MeanReversionBandStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.strategy == "mean_rev_band"
