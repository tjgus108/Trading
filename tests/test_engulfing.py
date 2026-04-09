"""tests/test_engulfing.py — EngulfingStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.engulfing import EngulfingStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows):
    """rows: list of (open, high, low, close) tuples."""
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": [1000.0] * len(rows),
        "ema50":  [100.0] * len(rows),
        "atr14":  [1.0] * len(rows),
    }
    return pd.DataFrame(data)


def _neutral_rows(n=8):
    """평범한 캔들 (패턴 없음)."""
    return [(100.0, 102.0, 99.0, 101.0)] * n


def _bullish_engulfing_rows(prev_body=4.0, curr_body=6.0, strong=False):
    """
    이전봉: 음봉 (open=104, close=100, body=4)
    현재봉: 양봉 (open=99, close=105, body=6) → engulfs prev
    strong=True: curr_body > prev_body * 1.5
    """
    base = _neutral_rows(8)
    prev_o = 104.0
    prev_c = prev_o - prev_body   # 100.0
    curr_o = prev_c - 1.0         # 99.0 (open <= close_prev)
    if strong:
        curr_c = prev_o + prev_body * 1.5 + 1.0  # body > prev_body * 1.5
    else:
        curr_c = prev_o + 0.5     # 104.5 (close >= open_prev, but not 1.5x)
    # base[7] = 현재봉(idx=-2), base[6] = 이전봉(idx=-3) → need prev at idx=-3, curr at idx=-2
    # df has 10 rows: indices 0-9, idx=-2 = index 8, prev = index 7
    rows = _neutral_rows(8)
    rows.append((prev_o, prev_o, prev_c, prev_c))   # index 8 = prev (idx=-2 will be curr)
    rows.append((curr_o, curr_c, curr_o, curr_c))   # index 9 = trailing (not used)
    # Wait: _last = df.iloc[-2], so idx=-2 is index 8 for 10-row df
    # We need prev at index 7 and curr at index 8
    rows2 = _neutral_rows(7)
    rows2.append((prev_o, prev_o, prev_c, prev_c))  # index 7 = prev
    rows2.append((curr_o, curr_c, curr_o, curr_c))  # index 8 = curr (idx=-2)
    rows2.append((curr_o, curr_c, curr_o, curr_c))  # index 9 = trailing (not used)
    return rows2


def _bearish_engulfing_rows(prev_body=4.0, curr_body=6.0, strong=False):
    """
    이전봉: 양봉 (open=100, close=104, body=4)
    현재봉: 음봉 (open=105, close=99, body=6) → engulfs prev
    """
    prev_o = 100.0
    prev_c = prev_o + prev_body   # 104.0
    curr_o = prev_c + 1.0         # 105.0 (open >= close_prev)
    if strong:
        curr_c = prev_o - prev_body * 1.5 - 1.0
    else:
        curr_c = prev_o - 0.5     # 99.5 (close <= open_prev)
    rows = _neutral_rows(7)
    rows.append((prev_o, prev_c, prev_o, prev_c))   # index 7 = prev
    rows.append((curr_o, curr_o, curr_c, curr_c))   # index 8 = curr (idx=-2)
    rows.append((curr_o, curr_o, curr_c, curr_c))   # index 9 = trailing
    return rows


strat = EngulfingStrategy()


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "engulfing"


# ── 2. 데이터 부족 → HOLD ───────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df([(100.0, 102.0, 99.0, 101.0)] * 4)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. Bullish Engulfing → BUY ───────────────────────────────────────────────
def test_bullish_engulfing_buy():
    df = _make_df(_bullish_engulfing_rows())
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 4. Bearish Engulfing → SELL ──────────────────────────────────────────────
def test_bearish_engulfing_sell():
    df = _make_df(_bearish_engulfing_rows())
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 5. Bullish Engulfing HIGH confidence (body > 1.5x) ──────────────────────
def test_bullish_engulfing_high_confidence():
    df = _make_df(_bullish_engulfing_rows(strong=True))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 6. Bullish Engulfing MEDIUM confidence (body <= 1.5x) ───────────────────
def test_bullish_engulfing_medium_confidence():
    df = _make_df(_bullish_engulfing_rows(strong=False))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 7. Bearish Engulfing HIGH confidence (body > 1.5x) ──────────────────────
def test_bearish_engulfing_high_confidence():
    df = _make_df(_bearish_engulfing_rows(strong=True))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 8. Bearish Engulfing MEDIUM confidence (body <= 1.5x) ───────────────────
def test_bearish_engulfing_medium_confidence():
    df = _make_df(_bearish_engulfing_rows(strong=False))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 9. 패턴 없음 → HOLD ──────────────────────────────────────────────────────
def test_no_pattern_hold():
    # 두 양봉 연속 → engulfing 아님
    rows = _neutral_rows(8)
    rows.append((100.0, 104.0, 100.0, 104.0))  # prev: 양봉
    rows.append((101.0, 103.0, 101.0, 103.0))  # curr: 양봉 (not engulfing)
    rows.append((101.0, 103.0, 101.0, 103.0))  # trailing
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 10. BUY Signal 필드 완전성 ─────────────────────────────────────────────
def test_buy_signal_fields_complete():
    df = _make_df(_bullish_engulfing_rows())
    sig = strat.generate(df)
    assert sig.strategy == "engulfing"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 11. SELL Signal 필드 완전성 ────────────────────────────────────────────
def test_sell_signal_fields_complete():
    df = _make_df(_bearish_engulfing_rows())
    sig = strat.generate(df)
    assert sig.strategy == "engulfing"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 12. BUY reasoning에 "Engulfing" 포함 ─────────────────────────────────────
def test_buy_reasoning_contains_engulfing():
    df = _make_df(_bullish_engulfing_rows())
    sig = strat.generate(df)
    assert "Engulfing" in sig.reasoning


# ── 13. SELL reasoning에 "Engulfing" 포함 ────────────────────────────────────
def test_sell_reasoning_contains_engulfing():
    df = _make_df(_bearish_engulfing_rows())
    sig = strat.generate(df)
    assert "Engulfing" in sig.reasoning


# ── 14. HOLD Signal 필드 완전성 ────────────────────────────────────────────
def test_hold_signal_fields():
    rows = _neutral_rows(8)
    rows.append((100.0, 104.0, 100.0, 104.0))
    rows.append((101.0, 103.0, 101.0, 103.0))
    rows.append((101.0, 103.0, 101.0, 103.0))
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "engulfing"
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
