"""Tests for PositionalScalingStrategy."""

import pandas as pd
import pytest

from src.strategy.positional_scaling import PositionalScalingStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows):
    return pd.DataFrame(rows)


def _base_rows(n=110, price=100.0):
    """중립 봉 n개."""
    return [
        {"open": price, "high": price + 1.0, "low": price - 1.0,
         "close": price, "volume": 1000.0}
        for _ in range(n)
    ]


def _make_bullish_buy_df():
    """
    EMA20 > EMA50 > EMA100, 풀백(close ≈ EMA20), 양봉 → BUY
    전략: 110행, 상승 추세 구성.
    - row 0~59: 100으로 시작
    - row 60~108: 120으로 상승 (EMA20 > EMA50 > EMA100 형성)
    - row 108 (idx=108=len-2): close=EMA20 근처 양봉
    """
    rows = _base_rows(110, price=100.0)
    # 60봉부터 상승 가격 설정
    for i in range(60, 109):
        rows[i] = {"open": 119.5, "high": 121.0, "low": 119.0,
                   "close": 120.0, "volume": 1000.0}
    # idx=108: 양봉, close가 EMA20 근처
    # EMA20은 최근 20봉(가격 120) 기준 약 120 근처
    # deviation = close/EMA20 - 1 이 [-0.01, 0.02] 이어야 함
    # close=120.5, EMA20≈120 → deviation≈0.004 (범위 내)
    rows[108] = {"open": 119.8, "high": 121.0, "low": 119.5,
                 "close": 120.5, "volume": 1000.0}
    # row 109: incomplete candle
    rows[109] = {"open": 120.5, "high": 121.0, "low": 120.0,
                 "close": 120.7, "volume": 1000.0}
    return _make_df(rows)


def _make_bearish_sell_df():
    """
    EMA20 < EMA50 < EMA100, 랠리(close ≈ EMA20), 음봉 → SELL
    - row 0~59: 120.0 고가
    - row 60~108: 100.0으로 하락 (EMA20 < EMA50 < EMA100)
    - idx=108: 음봉, close가 EMA20 근처
    """
    rows = _base_rows(110, price=120.0)
    for i in range(60, 109):
        rows[i] = {"open": 100.5, "high": 101.0, "low": 99.0,
                   "close": 100.0, "volume": 1000.0}
    # idx=108: 음봉, close≈EMA20≈100
    rows[108] = {"open": 100.2, "high": 100.5, "low": 99.0,
                 "close": 99.8, "volume": 1000.0}
    rows[109] = {"open": 99.8, "high": 100.2, "low": 99.0,
                 "close": 99.5, "volume": 1000.0}
    return _make_df(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────
def test_name():
    assert PositionalScalingStrategy.name == "positional_scaling"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────
def test_insufficient_data():
    s = PositionalScalingStrategy()
    df = _make_df(_base_rows(50))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exact_min_rows_neutral():
    """105행, 횡보 → HOLD (EMA alignment 없음)."""
    s = PositionalScalingStrategy()
    df = _make_df(_base_rows(105))
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 3. BUY 신호 ─────────────────────────────────────────────────────────
def test_bullish_buy_signal():
    """상승추세 + 풀백 + 양봉 → BUY."""
    s = PositionalScalingStrategy()
    df = _make_bullish_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_reasoning_contains_ema():
    s = PositionalScalingStrategy()
    sig = s.generate(_make_bullish_buy_df())
    if sig.action == Action.BUY:
        assert "EMA20" in sig.reasoning or "분할진입" in sig.reasoning


def test_buy_strategy_name():
    s = PositionalScalingStrategy()
    sig = s.generate(_make_bullish_buy_df())
    assert sig.strategy == "positional_scaling"


def test_buy_fields_populated():
    s = PositionalScalingStrategy()
    sig = s.generate(_make_bullish_buy_df())
    if sig.action == Action.BUY:
        assert sig.invalidation != ""
        assert sig.bull_case != ""
        assert isinstance(sig.entry_price, float)


# ── 4. SELL 신호 ─────────────────────────────────────────────────────────
def test_bearish_sell_signal():
    """하락추세 + 랠리 + 음봉 → SELL."""
    s = PositionalScalingStrategy()
    df = _make_bearish_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_strategy_name():
    s = PositionalScalingStrategy()
    sig = s.generate(_make_bearish_sell_df())
    assert sig.strategy == "positional_scaling"


def test_sell_fields_populated():
    s = PositionalScalingStrategy()
    sig = s.generate(_make_bearish_sell_df())
    if sig.action == Action.SELL:
        assert sig.invalidation != ""
        assert sig.bear_case != ""
        assert isinstance(sig.entry_price, float)


# ── 5. Confidence: volume 기반 ──────────────────────────────────────────
def test_high_confidence_on_high_volume():
    """volume > avg * 1.2 → HIGH (BUY 신호 시)."""
    rows = _base_rows(110, price=100.0)
    for i in range(60, 109):
        rows[i] = {"open": 119.5, "high": 121.0, "low": 119.0,
                   "close": 120.0, "volume": 1000.0}
    rows[108] = {"open": 119.8, "high": 121.0, "low": 119.5,
                 "close": 120.5, "volume": 2000.0}  # vol > avg*1.2
    rows[109] = {"open": 120.5, "high": 121.0, "low": 120.0,
                 "close": 120.7, "volume": 1000.0}
    s = PositionalScalingStrategy()
    sig = s.generate(_make_df(rows))
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence_on_normal_volume():
    s = PositionalScalingStrategy()
    df = _make_bullish_buy_df()
    sig = s.generate(df)
    # volume=1000, avg≈1000 → 1000 <= 1200 → MEDIUM
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 6. HOLD signal 필드 ────────────────────────────────────────────────
def test_hold_signal_fields():
    s = PositionalScalingStrategy()
    df = _make_df(_base_rows(110))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "positional_scaling"
    assert sig.confidence == Confidence.LOW


# ── 7. entry_price ───────────────────────────────────────────────────────
def test_entry_price_on_hold():
    s = PositionalScalingStrategy()
    df = _make_df(_base_rows(110))
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))
