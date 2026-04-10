"""Tests for GapMomentumStrategy."""

import pandas as pd
import pytest

from src.strategy.gap_momentum import GapMomentumStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 25) -> list:
    """기본 중립 캔들 n개."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000.0}
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ─────────────────────────────────────────────────────────

def test_name():
    assert GapMomentumStrategy.name == "gap_momentum"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strat = GapMomentumStrategy()
    df = _make_df(_base_rows(10))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 20행 → 처리 가능."""
    strat = GapMomentumStrategy()
    df = _make_df(_base_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 3. Gap Up BUY 신호 ───────────────────────────────────────────────────

def test_gap_up_buy_medium():
    """gap_up_pct 0.3~1.0 → BUY MEDIUM."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23  # len=25, idx=23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 100.5, "high": 102.0, "low": 100.3, "close": 101.5, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_gap_up_buy_high():
    """gap_up_pct > 1.0 → BUY HIGH."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 101.5, "high": 103.0, "low": 101.2, "close": 102.5, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_gap_up_no_signal_bearish_candle():
    """gap_up 있어도 음봉이면 HOLD."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 101.5, "high": 102.0, "low": 100.0, "close": 100.8, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_gap_up_no_signal_low_volume():
    """gap_up 있어도 거래량 부족 → HOLD."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 101.5, "high": 103.0, "low": 101.2, "close": 102.5, "volume": 100.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 4. Gap Down SELL 신호 ────────────────────────────────────────────────

def test_gap_down_sell_medium():
    """gap_down_pct 0.3~1.0 → SELL MEDIUM."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 99.5, "high": 99.8, "low": 98.5, "close": 98.8, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


def test_gap_down_sell_high():
    """gap_down_pct > 1.0 → SELL HIGH."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.5, "high": 98.8, "low": 97.0, "close": 97.5, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_gap_down_no_signal_bullish_candle():
    """gap_down 있어도 양봉이면 HOLD."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.5, "high": 100.0, "low": 98.0, "close": 99.2, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_gap_down_no_signal_low_volume():
    """gap_down 있어도 거래량 부족 → HOLD."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.5, "high": 98.8, "low": 97.0, "close": 97.5, "volume": 50.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 5. 갭 없는 경우 → HOLD ────────────────────────────────────────────────

def test_no_gap_hold():
    """갭 없는 중립 데이터 → HOLD."""
    strat = GapMomentumStrategy()
    df = _make_df(_base_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_gap_too_small_hold():
    """갭이 0.3% 미만 → HOLD."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 100.1, "high": 100.8, "low": 100.0, "close": 100.6, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Signal 필드 확인 ──────────────────────────────────────────────────

def test_signal_fields_buy():
    """BUY 신호 시 entry_price, strategy 필드 확인."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 101.5, "high": 103.0, "low": 101.2, "close": 102.5, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.strategy == "gap_momentum"
    assert sig.entry_price == pytest.approx(102.5)
    assert sig.reasoning != ""
    assert sig.invalidation != ""


def test_signal_fields_sell():
    """SELL 신호 시 entry_price, strategy 필드 확인."""
    strat = GapMomentumStrategy()
    rows = _base_rows(25)
    idx = 23
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.5, "high": 98.8, "low": 97.0, "close": 97.5, "volume": 5000.0}
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.strategy == "gap_momentum"
    assert sig.entry_price == pytest.approx(97.5)
    assert sig.reasoning != ""
    assert sig.invalidation != ""


def test_hold_reasoning():
    """HOLD 신호에 reasoning 포함 확인."""
    strat = GapMomentumStrategy()
    df = _make_df(_base_rows(25))
    sig = strat.generate(df)
    assert sig.reasoning != ""
