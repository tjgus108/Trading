"""tests/test_heikin_ashi_trend.py — HeikinAshiTrendStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.heikin_ashi_trend import HeikinAshiTrendStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows, volume=1000.0):
    """rows: list of (open, high, low, close) tuples."""
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": [volume] * len(rows),
    }
    return pd.DataFrame(data)


def _bull_rows(n=25):
    """연속 상승 HA 캔들 생성."""
    rows = []
    price = 100.0
    for i in range(n):
        o = price
        c = price + 3.0
        rows.append((o, c + 0.5, o - 0.5, c))
        price = c
    return rows


def _bear_rows(n=25):
    """연속 하락 HA 캔들 생성."""
    rows = []
    price = 200.0
    for i in range(n):
        o = price
        c = price - 3.0
        rows.append((o, o + 0.5, c - 0.5, c))
        price = c
    return rows


def _mixed_rows(n=25):
    """상승/하락 교대 → HOLD 유발."""
    rows = []
    for i in range(n):
        if i % 2 == 0:
            rows.append((100.0, 104.0, 99.0, 103.0))
        else:
            rows.append((103.0, 104.0, 98.0, 99.0))
    return rows


strat = HeikinAshiTrendStrategy()


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "heikin_ashi_trend"


# ── 2. BUY 신호 ─────────────────────────────────────────────────────────────
def test_buy_signal():
    df = _make_df(_bull_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ────────────────────────────────────────────────────────────
def test_sell_signal():
    df = _make_df(_bear_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (streak == 3) ───────────────────────────────────
def test_buy_high_confidence():
    df = _make_df(_bull_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. SELL HIGH confidence (streak == 3) ──────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(_bear_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 6. 데이터 부족(19행) → HOLD ─────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_bull_rows(19))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 7. 데이터 20행 경계 → 유효 처리 ─────────────────────────────────────────
def test_exactly_20_rows():
    df = _make_df(_bull_rows(20))
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 8. 혼합 패턴 → HOLD ──────────────────────────────────────────────────────
def test_mixed_pattern_hold():
    df = _make_df(_mixed_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 9. Signal 필드 완전성 (BUY) ─────────────────────────────────────────────
def test_signal_fields_buy():
    df = _make_df(_bull_rows(25))
    sig = strat.generate(df)
    assert sig.strategy == "heikin_ashi_trend"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 10. Signal 필드 완전성 (SELL) ────────────────────────────────────────────
def test_signal_fields_sell():
    df = _make_df(_bear_rows(25))
    sig = strat.generate(df)
    assert sig.strategy == "heikin_ashi_trend"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 11. BUY reasoning에 streak 정보 포함 ─────────────────────────────────────
def test_buy_reasoning_has_streak():
    df = _make_df(_bull_rows(25))
    sig = strat.generate(df)
    assert "streak" in sig.reasoning or "HA" in sig.reasoning


# ── 12. SELL reasoning에 streak 정보 포함 ────────────────────────────────────
def test_sell_reasoning_has_streak():
    df = _make_df(_bear_rows(25))
    sig = strat.generate(df)
    assert "streak" in sig.reasoning or "HA" in sig.reasoning


# ── 13. HOLD signal에 strategy 이름 포함 ─────────────────────────────────────
def test_hold_signal_strategy_name():
    df = _make_df(_mixed_rows(25))
    sig = strat.generate(df)
    assert sig.strategy == "heikin_ashi_trend"


# ── 14. entry_price는 마지막 완성 캔들의 close ──────────────────────────────
def test_entry_price_is_last_close():
    rows = _bull_rows(25)
    df = _make_df(rows)
    sig = strat.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected)
