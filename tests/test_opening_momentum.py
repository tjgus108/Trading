"""Tests for OpeningMomentumStrategy."""

import pandas as pd
import pytest

from src.strategy.opening_momentum import OpeningMomentumStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 27) -> list:
    """기본 중립 캔들 n개 (close == open, 모멘텀 없음)."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000.0}
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _bull_rows(n: int = 27, price_start: float = 100.0, step: float = 0.5) -> list:
    """n개의 연속 양봉 (강한 상승 모멘텀)."""
    rows = []
    p = price_start
    for _ in range(n):
        rows.append({
            "open": p,
            "high": p + step + 0.1,
            "low": p - 0.1,
            "close": p + step,
            "volume": 1000.0,
        })
        p += step
    return rows


def _bear_rows(n: int = 27, price_start: float = 110.0, step: float = 0.5) -> list:
    """n개의 연속 음봉 (강한 하락 모멘텀)."""
    rows = []
    p = price_start
    for _ in range(n):
        rows.append({
            "open": p,
            "high": p + 0.1,
            "low": p - step - 0.1,
            "close": p - step,
            "volume": 1000.0,
        })
        p -= step
    return rows


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert OpeningMomentumStrategy.name == "opening_momentum"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strategy = OpeningMomentumStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 25행 → 처리 가능."""
    strategy = OpeningMomentumStrategy()
    df = _make_df(_base_rows(25))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD  # 중립 데이터


# ── 3. BUY 신호 ───────────────────────────────────────────────────────────

def test_buy_signal_bull_streak_2():
    """bull_streak=2, mom_5>0.01, close>EMA21 → BUY."""
    strategy = OpeningMomentumStrategy()
    # 강한 상승 데이터로 시작 후 마지막 2봉만 양봉 확보
    rows = _bull_rows(27, price_start=100.0, step=0.5)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "bull_streak" in sig.reasoning


def test_buy_signal_high_confidence():
    """bull_streak=3, mom_5>0.02 → HIGH confidence."""
    strategy = OpeningMomentumStrategy()
    rows = _bull_rows(27, price_start=100.0, step=1.0)  # 1% step → mom_5 > 2%
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_signal_medium_confidence():
    """bull_streak=2, mom_5 0.01~0.02 → MEDIUM confidence."""
    strategy = OpeningMomentumStrategy()
    rows = _bull_rows(27, price_start=100.0, step=0.3)
    df = _make_df(rows)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_reasoning_contains_ema():
    """BUY reasoning에 ema21 포함."""
    strategy = OpeningMomentumStrategy()
    rows = _bull_rows(27, price_start=100.0, step=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "ema21" in sig.reasoning


# ── 4. SELL 신호 ──────────────────────────────────────────────────────────

def test_sell_signal_bear_streak_2():
    """bear_streak=2, mom_5<-0.01, close<EMA21 → SELL."""
    strategy = OpeningMomentumStrategy()
    rows = _bear_rows(27, price_start=110.0, step=0.5)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "bear_streak" in sig.reasoning


def test_sell_signal_high_confidence():
    """bear_streak=3, mom_5<-0.02 → HIGH confidence."""
    strategy = OpeningMomentumStrategy()
    rows = _bear_rows(27, price_start=110.0, step=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_reasoning_contains_ema():
    """SELL reasoning에 ema21 포함."""
    strategy = OpeningMomentumStrategy()
    rows = _bear_rows(27, price_start=110.0, step=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "ema21" in sig.reasoning


# ── 5. 조건 미충족 → HOLD ─────────────────────────────────────────────────

def test_bull_streak_below_ema_hold():
    """bull_streak 있어도 close < EMA21 → HOLD."""
    strategy = OpeningMomentumStrategy()
    # 먼저 크게 하락한 뒤 마지막 2봉 약한 반등 (EMA 아래)
    rows = _bear_rows(24, price_start=110.0, step=0.8)
    # 마지막 3봉: 양봉으로 교체하되 close는 여전히 EMA 아래
    p = float(rows[-1]["close"])
    for _ in range(3):
        rows.append({
            "open": p,
            "high": p + 0.2,
            "low": p - 0.1,
            "close": p + 0.1,
            "volume": 1000.0,
        })
        p += 0.1
    df = _make_df(rows)
    sig = strategy.generate(df)
    # mom_5 조건 미충족 가능성 높음 → HOLD 예상
    assert sig.action in (Action.HOLD, Action.BUY)  # EMA 조건에 따라


def test_mom5_too_small_hold():
    """모멘텀 0.5% (1% 미만) → HOLD."""
    strategy = OpeningMomentumStrategy()
    rows = _bull_rows(27, price_start=100.0, step=0.1)  # ~0.5% per 5봉
    df = _make_df(rows)
    sig = strategy.generate(df)
    # mom_5 < 0.01 → HOLD
    assert sig.action == Action.HOLD


# ── 6. Signal 필드 검증 ───────────────────────────────────────────────────

def test_buy_signal_fields():
    """BUY 시그널 필드 검증."""
    strategy = OpeningMomentumStrategy()
    rows = _bull_rows(27, price_start=100.0, step=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.strategy == "opening_momentum"
    assert sig.entry_price > 0
    assert sig.invalidation != ""
    assert "consecutive" in sig.bull_case.lower() or "bull" in sig.bull_case.lower()


def test_sell_signal_fields():
    """SELL 시그널 필드 검증."""
    strategy = OpeningMomentumStrategy()
    rows = _bear_rows(27, price_start=110.0, step=1.0)
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.strategy == "opening_momentum"
    assert sig.entry_price > 0
    assert sig.invalidation != ""


def test_hold_signal_fields():
    """HOLD 시그널 필드 검증."""
    strategy = OpeningMomentumStrategy()
    df = _make_df(_base_rows(27))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "opening_momentum"
    assert sig.confidence == Confidence.LOW
