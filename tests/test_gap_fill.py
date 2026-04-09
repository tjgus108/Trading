"""Tests for GapFillStrategy."""

import pandas as pd
import pytest

from src.strategy.gap_fill import GapFillStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 7) -> list:
    """기본 중립 캔들 n개 (갭 없음)."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000.0}
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert GapFillStrategy.name == "gap_fill"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strategy = GapFillStrategy()
    df = _make_df(_base_rows(3))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 5행 → 처리 가능."""
    strategy = GapFillStrategy()
    df = _make_df(_base_rows(5))
    sig = strategy.generate(df)
    # 중립 데이터이므로 HOLD
    assert sig.action == Action.HOLD


# ── 3. Gap Down Fill → BUY 신호 ──────────────────────────────────────────

def test_gap_down_fill_buy():
    """Gap Down 후 회복 양봉 → BUY."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    # _last = iloc[-2] = index 5
    # prev = iloc[-3] = index 4
    rows[4]["close"] = 100.0        # prev_close
    # gap down: open < prev_close * 0.995
    rows[5] = {"open": 99.0, "high": 100.5, "low": 98.5, "close": 99.8,
               "volume": 1000.0}   # close > open → 회복 양봉
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "Gap Down" in sig.reasoning


def test_gap_down_fill_buy_reasoning():
    """BUY 신호 reasoning에 gap fill 포함."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    rows[5] = {"open": 99.0, "high": 100.5, "low": 98.5, "close": 99.8, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert "gap fill" in sig.reasoning.lower()


def test_gap_down_high_confidence():
    """Gap Down > 1.5% → HIGH confidence."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    # gap = (98.4 - 100) / 100 = -1.6% (> 1.5%)
    rows[5] = {"open": 98.4, "high": 99.5, "low": 98.0, "close": 99.0, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_gap_down_medium_confidence():
    """Gap Down 0.6% (0.5%~1.5%) → MEDIUM confidence."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    # gap = (99.4 - 100) / 100 = -0.6%
    rows[5] = {"open": 99.4, "high": 100.0, "low": 99.0, "close": 99.7, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 4. Gap Up Fill → SELL 신호 ───────────────────────────────────────────

def test_gap_up_fill_sell():
    """Gap Up 후 하락 음봉 → SELL."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    # gap up: open > prev_close * 1.005
    rows[5] = {"open": 101.0, "high": 101.5, "low": 100.0, "close": 100.3,
               "volume": 1000.0}   # close < open → 하락
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "Gap Up" in sig.reasoning


def test_gap_up_fill_sell_high_confidence():
    """Gap Up > 1.5% + 음봉 → HIGH confidence."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    # gap = (101.6 - 100) / 100 = 1.6%
    rows[5] = {"open": 101.6, "high": 102.0, "low": 100.5, "close": 101.0, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 5. 조건 미충족 → HOLD ─────────────────────────────────────────────────

def test_gap_down_no_recovery_hold():
    """Gap Down이지만 음봉 유지 (close < open) → HOLD."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    rows[5] = {"open": 99.0, "high": 99.5, "low": 97.5, "close": 98.0, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_gap_up_no_reversal_hold():
    """Gap Up이지만 양봉 유지 (close > open) → HOLD."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    rows[5] = {"open": 101.0, "high": 103.0, "low": 100.8, "close": 102.5, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_gap_too_small_hold():
    """Gap 0.3% (0.5% 미만) → HOLD."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    rows[5] = {"open": 99.7, "high": 100.5, "low": 99.5, "close": 100.1, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Signal 필드 검증 ───────────────────────────────────────────────────

def test_buy_signal_fields():
    """BUY 시그널 필드 확인."""
    strategy = GapFillStrategy()
    rows = _base_rows(7)
    rows[4]["close"] = 100.0
    rows[5] = {"open": 99.0, "high": 100.5, "low": 98.5, "close": 99.8, "volume": 1000.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.strategy == "gap_fill"
    assert sig.entry_price == pytest.approx(99.8)
    assert "prev_close" in sig.bull_case or "gap fill" in sig.bull_case.lower()
    assert sig.invalidation != ""


def test_hold_signal_fields():
    """HOLD 시그널 필드 확인."""
    strategy = GapFillStrategy()
    df = _make_df(_base_rows(7))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "gap_fill"
    assert sig.confidence == Confidence.LOW
