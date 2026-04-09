"""Tests for StarPatternStrategy."""

import pandas as pd
import pytest

from src.strategy.star_pattern import StarPatternStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 12) -> list:
    """기본 중립 캔들 n개."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5,
         "volume": 1000.0, "ema50": 100.0, "atr14": 2.0}
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert StarPatternStrategy.name == "star_pattern"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strategy = StarPatternStrategy()
    df = _make_df(_base_rows(5))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 10행 → 처리 가능."""
    strategy = StarPatternStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    # 중립 데이터 → HOLD
    assert sig.action == Action.HOLD


# ── 3. Morning Star → BUY ────────────────────────────────────────────────

def test_morning_star_buy():
    """완벽한 Morning Star → BUY HIGH confidence."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    idx = 10  # len=12, idx = 12-2 = 10

    # c1 (idx-2=8): 큰 음봉, body > atr*0.5=1.0
    rows[8] = {"open": 105.0, "high": 106.0, "low": 99.0, "close": 102.0,
               "volume": 2000.0, "ema50": 103.0, "atr14": atr}
    # body1_bear = 105-102 = 3.0 > 1.0 ✓

    # c2 (idx-1=9): 작은 별봉, body < atr*0.3=0.6
    rows[9] = {"open": 101.3, "high": 101.8, "low": 100.8, "close": 101.0,
               "volume": 500.0, "ema50": 103.0, "atr14": atr}
    # body2 = |101.0-101.3| = 0.3 < 0.6 ✓

    # c3 (idx=10): 큰 양봉, body > atr*0.5=1.0, recovery: close > (c1.open+c1.close)/2 = 103.5
    rows[10] = {"open": 101.0, "high": 106.0, "low": 100.5, "close": 104.5,
                "volume": 2500.0, "ema50": 103.0, "atr14": atr}
    # body3_bull = 104.5-101.0 = 3.5 > 1.0 ✓
    # recovery: 104.5 > (105+102)/2=103.5 ✓

    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH
    assert "Morning Star" in sig.reasoning


def test_morning_star_partial_medium_confidence():
    """3/4 조건 충족 → BUY MEDIUM confidence."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    idx = 10

    # c1: 큰 음봉
    rows[8] = {"open": 105.0, "high": 106.0, "low": 99.0, "close": 102.0,
               "volume": 2000.0, "ema50": 103.0, "atr14": atr}
    # c2: 작은 별봉
    rows[9] = {"open": 101.3, "high": 101.8, "low": 100.8, "close": 101.0,
               "volume": 500.0, "ema50": 103.0, "atr14": atr}
    # c3: 큰 양봉이지만 recovery 미충족 (close < 103.5)
    rows[10] = {"open": 101.0, "high": 103.0, "low": 100.5, "close": 102.8,
                "volume": 2500.0, "ema50": 103.0, "atr14": atr}
    # body3_bull = 102.8-101.0 = 1.8 > 1.0 ✓, recovery = 102.8 < 103.5 ✗

    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 4. Evening Star → SELL ───────────────────────────────────────────────

def test_evening_star_sell():
    """완벽한 Evening Star → SELL HIGH confidence."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    idx = 10

    # c1 (idx-2=8): 큰 양봉, body > atr*0.5=1.0
    rows[8] = {"open": 100.0, "high": 106.0, "low": 99.0, "close": 104.0,
               "volume": 2000.0, "ema50": 102.0, "atr14": atr}
    # body1_bull = 104-100 = 4.0 > 1.0 ✓

    # c2 (idx-1=9): 작은 별봉, body < atr*0.3=0.6
    rows[9] = {"open": 104.2, "high": 105.0, "low": 103.8, "close": 104.4,
               "volume": 500.0, "ema50": 102.0, "atr14": atr}
    # body2 = |104.4-104.2| = 0.2 < 0.6 ✓

    # c3 (idx=10): 큰 음봉, body > atr*0.5=1.0, decline: close < (c1.open+c1.close)/2 = 102
    rows[10] = {"open": 104.0, "high": 104.5, "low": 98.5, "close": 100.5,
                "volume": 2500.0, "ema50": 102.0, "atr14": atr}
    # body3_bear = 104-100.5 = 3.5 > 1.0 ✓
    # decline: 100.5 < (100+104)/2=102 ✓

    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH
    assert "Evening Star" in sig.reasoning


def test_evening_star_partial_medium_confidence():
    """Evening Star 3/4 조건 → SELL MEDIUM confidence."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    idx = 10

    rows[8] = {"open": 100.0, "high": 106.0, "low": 99.0, "close": 104.0,
               "volume": 2000.0, "ema50": 102.0, "atr14": atr}
    rows[9] = {"open": 104.2, "high": 105.0, "low": 103.8, "close": 104.4,
               "volume": 500.0, "ema50": 102.0, "atr14": atr}
    # c3: 큰 음봉이지만 decline 미충족 (close > 102)
    rows[10] = {"open": 104.0, "high": 104.5, "low": 102.0, "close": 102.5,
                "volume": 2500.0, "ema50": 102.0, "atr14": atr}
    # body3_bear = 104-102.5 = 1.5 > 1.0 ✓, decline = 102.5 < 102? 아니오 ✗

    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 5. 조건 미충족 → HOLD ─────────────────────────────────────────────────

def test_no_pattern_hold():
    """패턴 없으면 HOLD."""
    strategy = StarPatternStrategy()
    df = _make_df(_base_rows(12))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_atr_zero_hold():
    """ATR = 0 → HOLD."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    for r in rows:
        r["atr14"] = 0.0
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_morning_star_only_2_conditions_hold():
    """2/4 조건만 충족 → HOLD."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    idx = 10

    # c1: 큰 음봉 ✓
    rows[8] = {"open": 105.0, "high": 106.0, "low": 99.0, "close": 102.0,
               "volume": 2000.0, "ema50": 103.0, "atr14": atr}
    # c2: 큰 별봉 (조건 미충족, body > atr*0.3)
    rows[9] = {"open": 101.0, "high": 103.0, "low": 99.0, "close": 102.5,
               "volume": 800.0, "ema50": 103.0, "atr14": atr}
    # c3: 작은 양봉 (body < atr*0.5 미충족)
    rows[10] = {"open": 101.5, "high": 102.5, "low": 101.0, "close": 102.0,
                "volume": 1000.0, "ema50": 103.0, "atr14": atr}

    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Signal 필드 검증 ───────────────────────────────────────────────────

def test_signal_fields_on_buy():
    """BUY 시그널 필드 검증."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    rows[8] = {"open": 105.0, "high": 106.0, "low": 99.0, "close": 102.0,
               "volume": 2000.0, "ema50": 103.0, "atr14": atr}
    rows[9] = {"open": 101.3, "high": 101.8, "low": 100.8, "close": 101.0,
               "volume": 500.0, "ema50": 103.0, "atr14": atr}
    rows[10] = {"open": 101.0, "high": 106.0, "low": 100.5, "close": 104.5,
                "volume": 2500.0, "ema50": 103.0, "atr14": atr}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.strategy == "star_pattern"
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")


def test_signal_fields_on_sell():
    """SELL 시그널 필드 검증."""
    strategy = StarPatternStrategy()
    rows = _base_rows(12)
    atr = 2.0
    rows[8] = {"open": 100.0, "high": 106.0, "low": 99.0, "close": 104.0,
               "volume": 2000.0, "ema50": 102.0, "atr14": atr}
    rows[9] = {"open": 104.2, "high": 105.0, "low": 103.8, "close": 104.4,
               "volume": 500.0, "ema50": 102.0, "atr14": atr}
    rows[10] = {"open": 104.0, "high": 104.5, "low": 98.5, "close": 100.5,
                "volume": 2500.0, "ema50": 102.0, "atr14": atr}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.strategy == "star_pattern"
    assert sig.action == Action.SELL
    assert sig.entry_price == 100.5


def test_hold_signal_fields():
    """HOLD 시그널 필드 검증."""
    strategy = StarPatternStrategy()
    df = _make_df(_base_rows(12))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "star_pattern"
    assert sig.confidence == Confidence.LOW
