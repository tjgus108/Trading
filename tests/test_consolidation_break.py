"""Tests for ConsolidationBreakStrategy."""

import pandas as pd
import pytest

from src.strategy.consolidation_break import ConsolidationBreakStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 30) -> list:
    """기본 중립 캔들 n개."""
    return [
        {"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1000.0}
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _make_tight_then_breakout(direction: str = "up", n_base: int = 30) -> pd.DataFrame:
    """
    20봉 횡보(tight range) + 직전 봉까지 횡보 유지 후 마지막 완성 캔들에서 돌파.
    idx = len-2 (마지막 완성 캔들)
    """
    rows = []
    # 처음 15봉: 넓은 range (range_ma 기준선 높이기)
    for i in range(15):
        rows.append({"open": 100.0, "high": 105.0, "low": 95.0, "close": 100.0, "volume": 1000.0})
    # 다음 14봉: 매우 좁은 range (횡보)
    for i in range(14):
        rows.append({"open": 100.0, "high": 100.3, "low": 99.7, "close": 100.0, "volume": 1000.0})
    # 마지막 완성 캔들(idx = len-2): 돌파
    if direction == "up":
        rows.append({"open": 100.3, "high": 106.0, "low": 100.2, "close": 105.5, "volume": 8000.0})
    else:
        rows.append({"open": 99.7, "high": 99.8, "low": 94.0, "close": 94.5, "volume": 8000.0})
    # 현재 진행 캔들 (idx = len-1)
    rows.append({"open": 105.5, "high": 106.0, "low": 105.0, "close": 105.6, "volume": 500.0})
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ─────────────────────────────────────────────────────────

def test_name():
    assert ConsolidationBreakStrategy.name == "consolidation_break"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    strat = ConsolidationBreakStrategy()
    df = _make_df(_base_rows(15))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 25행 → 처리 가능."""
    strat = ConsolidationBreakStrategy()
    df = _make_df(_base_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 3. BUY 신호 ──────────────────────────────────────────────────────────

def test_buy_signal_breakout_up():
    """횡보 후 상향 돌파 → BUY."""
    strat = ConsolidationBreakStrategy()
    df = _make_tight_then_breakout("up")
    sig = strat.generate(df)
    assert sig.action == Action.BUY


def test_buy_signal_confidence_medium_normal_volume():
    """돌파 + 일반 거래량 → BUY MEDIUM."""
    strat = ConsolidationBreakStrategy()
    rows = []
    for i in range(15):
        rows.append({"open": 100.0, "high": 106.0, "low": 94.0, "close": 100.0, "volume": 1000.0})
    for i in range(13):
        rows.append({"open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0, "volume": 1000.0})
    # 직전 봉: 횡보 (range_width < range_ma * 0.6)
    rows.append({"open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0, "volume": 1000.0})
    # 마지막 완성 캔들: 돌파, 보통 거래량
    rows.append({"open": 100.2, "high": 106.0, "low": 100.1, "close": 105.0, "volume": 1200.0})
    # 현재 진행 캔들
    rows.append({"open": 105.0, "high": 106.0, "low": 104.8, "close": 105.2, "volume": 500.0})
    df = pd.DataFrame(rows)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 4. SELL 신호 ─────────────────────────────────────────────────────────

def test_sell_signal_breakout_down():
    """횡보 후 하향 돌파 → SELL."""
    strat = ConsolidationBreakStrategy()
    df = _make_tight_then_breakout("down")
    sig = strat.generate(df)
    assert sig.action == Action.SELL


def test_sell_signal_confidence():
    """하향 돌파 신호 confidence 확인."""
    strat = ConsolidationBreakStrategy()
    rows = []
    for i in range(15):
        rows.append({"open": 100.0, "high": 106.0, "low": 94.0, "close": 100.0, "volume": 1000.0})
    for i in range(13):
        rows.append({"open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0, "volume": 1000.0})
    rows.append({"open": 100.0, "high": 100.2, "low": 99.8, "close": 100.0, "volume": 1000.0})
    rows.append({"open": 99.8, "high": 99.9, "low": 93.0, "close": 93.5, "volume": 1200.0})
    rows.append({"open": 93.5, "high": 94.0, "low": 93.0, "close": 93.6, "volume": 500.0})
    df = pd.DataFrame(rows)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 5. 횡보 없는 돌파 → HOLD ─────────────────────────────────────────────

def test_no_consolidation_no_signal():
    """이전 봉이 횡보가 아니면 HOLD."""
    strat = ConsolidationBreakStrategy()
    rows = _base_rows(30)
    # 중립 데이터 → consolidating=False 가능성 높음
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_wide_range_no_signal():
    """Range가 넓으면 consolidating=False → HOLD."""
    strat = ConsolidationBreakStrategy()
    rows = []
    for i in range(30):
        rows.append({"open": 100.0, "high": 110.0, "low": 90.0, "close": 100.0, "volume": 1000.0})
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Signal 필드 확인 ──────────────────────────────────────────────────

def test_signal_fields_buy():
    """BUY 신호 시 필드 확인."""
    strat = ConsolidationBreakStrategy()
    df = _make_tight_then_breakout("up")
    sig = strat.generate(df)
    assert sig.strategy == "consolidation_break"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.invalidation != ""


def test_signal_fields_sell():
    """SELL 신호 시 필드 확인."""
    strat = ConsolidationBreakStrategy()
    df = _make_tight_then_breakout("down")
    sig = strat.generate(df)
    assert sig.strategy == "consolidation_break"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.invalidation != ""


def test_hold_reasoning():
    """HOLD reasoning 포함 확인."""
    strat = ConsolidationBreakStrategy()
    df = _make_df(_base_rows(30))
    sig = strat.generate(df)
    assert sig.reasoning != ""


# ── 7. 경계값 테스트 ──────────────────────────────────────────────────────

def test_26_rows_valid():
    """26행 → 처리 가능."""
    strat = ConsolidationBreakStrategy()
    df = _make_df(_base_rows(26))
    sig = strat.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


def test_entry_price_equals_close():
    """entry_price가 마지막 완성 캔들의 close값과 일치."""
    strat = ConsolidationBreakStrategy()
    df = _make_tight_then_breakout("up")
    sig = strat.generate(df)
    expected_close = float(df.iloc[-2]["close"])
    assert sig.entry_price == pytest.approx(expected_close)
