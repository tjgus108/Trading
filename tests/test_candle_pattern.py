"""Tests for CandlePatternStrategy."""

import pandas as pd
import pytest

from src.strategy.candle_pattern import CandlePatternStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows) -> pd.DataFrame:
    """각 row: open, high, low, close, volume, rsi"""
    return pd.DataFrame(rows)


def _base_rows(n: int = 22):
    """기본 HOLD 캔들 (neutral) n개."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000, "rsi": 50}
        for _ in range(n)
    ]


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert CandlePatternStrategy.name == "candle_pattern"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strategy = CandlePatternStrategy()
    df = _make_df(_base_rows(10))  # 20 미만
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 3. Hammer → BUY ──────────────────────────────────────────────────────

def test_hammer_buy():
    """양봉, lower_wick > body*2, RSI < 45."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    # 마지막에서 -2 위치(인덱스 20): hammer 캔들
    # open=100, close=103 (양봉, body=3), low=91 (lower_wick=9 > 6), rsi=40
    rows[20] = {"open": 100.0, "high": 103.5, "low": 91.0, "close": 103.0, "volume": 1000, "rsi": 40}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "hammer" in sig.reasoning


def test_hammer_rsi_too_high_no_signal():
    """hammer 조건 충족 but RSI >= 45 → hammer 패턴 미발동."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    rows[20] = {"open": 100.0, "high": 103.5, "low": 91.0, "close": 103.0, "volume": 1000, "rsi": 50}
    df = _make_df(rows)
    sig = strategy.generate(df)
    # hammer 없으므로 BUY가 아니어야 함 (HOLD 또는 다른 패턴 없으면 HOLD)
    assert sig.action != Action.BUY or "hammer" not in sig.reasoning


# ── 4. Shooting Star → SELL ──────────────────────────────────────────────

def test_shooting_star_sell():
    """음봉, upper_wick > body*2, RSI > 55."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    # close=97, open=100 (음봉, body=3), high=109 (upper_wick=12 > 6), rsi=60
    rows[20] = {"open": 100.0, "high": 109.0, "low": 96.5, "close": 97.0, "volume": 1000, "rsi": 60}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "shooting_star" in sig.reasoning


def test_shooting_star_rsi_too_low_no_signal():
    """shooting_star 조건 충족 but RSI <= 55 → 패턴 미발동."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    rows[20] = {"open": 100.0, "high": 109.0, "low": 96.5, "close": 97.0, "volume": 1000, "rsi": 50}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action != Action.SELL or "shooting_star" not in sig.reasoning


# ── 5. Bullish Engulfing → BUY ───────────────────────────────────────────

def test_bullish_engulfing_buy():
    """현재 양봉이 전봉 음봉을 완전히 감싸면 BUY."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    # 인덱스 19 (prev): 음봉 open=102, close=98 (body 98~102)
    rows[19] = {"open": 102.0, "high": 103.0, "low": 97.0, "close": 98.0, "volume": 1000, "rsi": 50}
    # 인덱스 20 (last): 양봉 open=96, close=105 (body 96~105, 완전 감쌈)
    rows[20] = {"open": 96.0, "high": 106.0, "low": 95.0, "close": 105.0, "volume": 1000, "rsi": 50}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "bullish_engulfing" in sig.reasoning


# ── 6. Bearish Engulfing → SELL ──────────────────────────────────────────

def test_bearish_engulfing_sell():
    """현재 음봉이 전봉 양봉을 완전히 감싸면 SELL."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    # 인덱스 19 (prev): 양봉 open=98, close=102
    rows[19] = {"open": 98.0, "high": 103.0, "low": 97.0, "close": 102.0, "volume": 1000, "rsi": 50}
    # 인덱스 20 (last): 음봉 open=105, close=95 (완전 감쌈)
    rows[20] = {"open": 105.0, "high": 106.0, "low": 94.0, "close": 95.0, "volume": 1000, "rsi": 50}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "bearish_engulfing" in sig.reasoning


# ── 7. HIGH confidence: 2개 이상 패턴 동시 ───────────────────────────────

def test_high_confidence_multiple_patterns():
    """hammer + bullish_engulfing 동시 → HIGH confidence."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    # prev: 음봉
    rows[19] = {"open": 102.0, "high": 103.0, "low": 97.0, "close": 98.0, "volume": 1000, "rsi": 50}
    # last: 양봉 + hammer(lower_wick > body*2) + engulfing + RSI < 45
    # open=96, close=105, body=9, low=78 (lower_wick=96-78=18 > 18 ✓, 正確: 18 > 9*2=18 는 > 아님)
    # low=75 → lower_wick=21 > 18 ✓
    rows[20] = {"open": 96.0, "high": 106.0, "low": 75.0, "close": 105.0, "volume": 1000, "rsi": 40}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 8. 패턴 없으면 HOLD ──────────────────────────────────────────────────

def test_no_pattern_hold():
    """특별한 패턴 없으면 HOLD."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. Signal 필드 검증 ───────────────────────────────────────────────────

def test_signal_fields_present():
    """Signal 객체에 필수 필드가 모두 있는지 확인."""
    strategy = CandlePatternStrategy()
    rows = _base_rows(22)
    rows[20] = {"open": 100.0, "high": 109.0, "low": 96.5, "close": 97.0, "volume": 1000, "rsi": 60}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")
    assert sig.strategy == "candle_pattern"
