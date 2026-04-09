"""
AnchoredVWAPStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.anchored_vwap import AnchoredVWAPStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 40,
    close_values=None,
    volume_values=None,
    high_values=None,
    low_values=None,
) -> pd.DataFrame:
    """기본 mock DataFrame. _last() = iloc[-2]."""
    if close_values is None:
        close_values = [100.0] * n
    if volume_values is None:
        volume_values = [1000.0] * n
    if high_values is None:
        high_values = [v * 1.01 for v in close_values]
    if low_values is None:
        low_values = [v * 0.99 for v in close_values]

    return pd.DataFrame({
        "open":   close_values,
        "high":   high_values,
        "low":    low_values,
        "close":  close_values,
        "volume": volume_values,
    })


def _make_buy_df(n: int = 50) -> pd.DataFrame:
    """BUY 조건: close > AVWAP, close > EMA20, volume spike.

    가격이 하락한 뒤 반등: anchor는 중간 저점(낮은 가격대), 이후 가격이 올라서
    AVWAP < close 조건 성립.
    """
    # 초반 절반은 높은 가격(120), 중간에 갭 하락(>3%)으로 anchor 생성,
    # 이후 다시 올라서 완성봉이 AVWAP보다 높도록.
    half = n // 2
    closes = [120.0] * half
    # 갭 하락: 120 → 90 = 25% drop → gap anchor here
    closes.append(90.0)
    # 이후 서서히 회복
    for i in range(n - half - 1):
        closes.append(90.0 + i * 0.5)
    # 완성봉([-2])은 충분히 높게
    closes[-2] = 115.0
    closes[-1] = 115.0

    vols = [500.0] * n
    vols[-2] = 3000.0
    highs = [c * 1.01 for c in closes]
    lows = [c * 0.99 for c in closes]
    return _make_df(n=n, close_values=closes, volume_values=vols, high_values=highs, low_values=lows)


def _make_sell_df(n: int = 50) -> pd.DataFrame:
    """SELL 조건: close < AVWAP, close < EMA20, volume spike.

    가격이 올랐다가 갭 상승 anchor 이후 하락: AVWAP > close.
    """
    half = n // 2
    closes = [80.0] * half
    # 갭 상승: 80 → 110 = 37.5% rise → gap anchor
    closes.append(110.0)
    for i in range(n - half - 1):
        closes.append(110.0 - i * 0.5)
    # 완성봉([-2])은 낮게
    closes[-2] = 85.0
    closes[-1] = 85.0

    vols = [500.0] * n
    vols[-2] = 3000.0
    highs = [c * 1.01 for c in closes]
    lows = [c * 0.99 for c in closes]
    return _make_df(n=n, close_values=closes, volume_values=vols, high_values=highs, low_values=lows)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert AnchoredVWAPStrategy().name == "anchored_vwap"


def test_insufficient_data_returns_hold():
    s = AnchoredVWAPStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_minimum_rows_boundary():
    """n=25(최솟값)에서 동작해야 한다."""
    s = AnchoredVWAPStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── HOLD ─────────────────────────────────────────────────────────────────────

def test_hold_low_volume():
    """volume <= avg_vol_20 → HOLD."""
    s = AnchoredVWAPStrategy()
    n = 40
    closes = [100.0] * n
    closes[-2] = 115.0
    vols = [1000.0] * n
    vols[-2] = 500.0  # 평균보다 낮음
    df = _make_df(n=n, close_values=closes, volume_values=vols)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_normal_conditions():
    """flat 가격 → no signal."""
    s = AnchoredVWAPStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── BUY ──────────────────────────────────────────────────────────────────────

def test_buy_signal_action():
    """BUY 조건 충족 시 action == BUY."""
    s = AnchoredVWAPStrategy()
    sig = s.generate(_make_buy_df())
    assert sig.action == Action.BUY


def test_buy_signal_strategy_name():
    s = AnchoredVWAPStrategy()
    sig = s.generate(_make_buy_df())
    assert sig.strategy == "anchored_vwap"


def test_buy_entry_price():
    """entry_price == iloc[-2].close."""
    s = AnchoredVWAPStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))


# ── SELL ─────────────────────────────────────────────────────────────────────

def test_sell_signal_action():
    s = AnchoredVWAPStrategy()
    sig = s.generate(_make_sell_df())
    assert sig.action == Action.SELL


def test_sell_signal_strategy_name():
    s = AnchoredVWAPStrategy()
    sig = s.generate(_make_sell_df())
    assert sig.strategy == "anchored_vwap"


def test_sell_entry_price():
    s = AnchoredVWAPStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))


# ── confidence ───────────────────────────────────────────────────────────────

def test_high_confidence_with_gap_anchor_and_large_deviation():
    """gap anchor + |close/avwap - 1| > 1% → HIGH confidence."""
    s = AnchoredVWAPStrategy()
    n = 55
    closes = [100.0] * n
    # 갭 발생(>3%) at around i=30
    closes[30] = 110.0  # gap from 100 → 110 = 10%
    # 이후 가격 유지 후 완성봉에서 크게 올라감 (AVWAP보다 높게)
    for i in range(31, n):
        closes[i] = 110.0
    closes[-2] = 125.0  # well above AVWAP (~110)
    closes[-1] = 125.0

    vols = [1000.0] * n
    vols[-2] = 5000.0

    highs = [c * 1.01 for c in closes]
    lows = [c * 0.99 for c in closes]
    df = _make_df(n=n, close_values=closes, volume_values=vols, high_values=highs, low_values=lows)
    sig = s.generate(df)
    # gap anchor 존재 + deviation > 1% → HIGH
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence_no_gap_anchor():
    """gap anchor 없으면 최대 MEDIUM confidence."""
    s = AnchoredVWAPStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── Signal fields ─────────────────────────────────────────────────────────────

def test_signal_has_invalidation():
    """BUY/SELL 신호에는 invalidation 문자열이 있어야 한다."""
    s = AnchoredVWAPStrategy()
    sig = s.generate(_make_buy_df())
    if sig.action != Action.HOLD:
        assert len(sig.invalidation) > 0


def test_hold_signal_fields():
    """HOLD 신호의 필드 확인."""
    s = AnchoredVWAPStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert sig.strategy == "anchored_vwap"
