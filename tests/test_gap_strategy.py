"""Tests for GapStrategy."""

import pandas as pd
import pytest

from src.strategy.gap_strategy import GapStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 27) -> list:
    """기본 중립 캔들 n개."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000.0,
         "ema50": 100.0, "atr14": 1.0}
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert GapStrategy.name == "gap_strategy"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strategy = GapStrategy()
    df = _make_df(_base_rows(10))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 25행 → 처리 가능."""
    strategy = GapStrategy()
    df = _make_df(_base_rows(25))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD  # 갭 없는 중립 데이터


# ── 3. Gap Up BUY 신호 ────────────────────────────────────────────────────

def test_gap_up_buy_signal():
    """Gap Up + 양봉 + 볼륨 > 평균 → BUY."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25  # len=27, idx = 27-2 = 25
    # prev_close = 100.0 (기본), open_now = 101.5 → gap_size = 1.5%
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 101.5, "high": 103.0, "low": 101.0, "close": 102.5,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "Gap Up" in sig.reasoning


def test_gap_up_medium_confidence():
    """Gap Size 0.6% → MEDIUM confidence."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    # gap_size = 0.6 / 100 * 100 = 0.6%
    rows[idx] = {"open": 100.6, "high": 102.0, "low": 100.4, "close": 101.5,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_gap_up_high_confidence():
    """Gap Size > 1.5% → HIGH confidence."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    # gap_size = 2.0%
    rows[idx] = {"open": 102.0, "high": 104.0, "low": 101.5, "close": 103.0,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 4. Gap Down SELL 신호 ─────────────────────────────────────────────────

def test_gap_down_sell_signal():
    """Gap Down + 음봉 + 볼륨 > 평균 → SELL."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    # open = 98.0 → gap_size = 2.0% (gap down)
    rows[idx] = {"open": 98.0, "high": 98.5, "low": 96.5, "close": 97.0,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "Gap Down" in sig.reasoning


def test_gap_down_high_confidence():
    """Gap Down > 1.5% → HIGH confidence."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.0, "high": 98.5, "low": 96.0, "close": 96.5,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 5. 조건 미충족 → HOLD ─────────────────────────────────────────────────

def test_gap_up_but_bearish_candle_hold():
    """Gap Up이지만 음봉 (close < open) → HOLD."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 102.0, "high": 102.5, "low": 100.5, "close": 101.0,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_gap_up_low_volume_hold():
    """Gap Up + 양봉 but 볼륨 < 평균 → HOLD."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 102.0, "high": 104.0, "low": 101.5, "close": 103.0,
                 "volume": 100.0, "ema50": 100.0, "atr14": 1.0}  # volume 매우 낮음
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_gap_too_small_hold():
    """Gap Size <= 0.5% → HOLD."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    # gap_size = 0.3%
    rows[idx] = {"open": 100.3, "high": 101.0, "low": 100.1, "close": 100.8,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Signal 필드 검증 ───────────────────────────────────────────────────

def test_signal_fields_on_buy():
    """BUY 시그널의 모든 필드 확인."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 102.0, "high": 104.0, "low": 101.5, "close": 103.0,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.strategy == "gap_strategy"
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")


def test_hold_signal_fields():
    """HOLD 시그널 필드 확인."""
    strategy = GapStrategy()
    df = _make_df(_base_rows(27))
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "gap_strategy"
    assert sig.confidence == Confidence.LOW


# ── 7. Gap Down 음봉 방향 유지 ────────────────────────────────────────────

def test_gap_down_but_bullish_candle_hold():
    """Gap Down이지만 양봉 (close > open) → HOLD."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.0, "high": 100.0, "low": 97.5, "close": 99.0,
                 "volume": 5000.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_gap_down_low_volume_hold():
    """Gap Down + 음봉 but 볼륨 < 평균 → HOLD."""
    strategy = GapStrategy()
    rows = _base_rows(27)
    idx = 25
    rows[idx - 1]["close"] = 100.0
    rows[idx] = {"open": 98.0, "high": 98.5, "low": 96.0, "close": 96.5,
                 "volume": 50.0, "ema50": 100.0, "atr14": 1.0}
    df = _make_df(rows)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
