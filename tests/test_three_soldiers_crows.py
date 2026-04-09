"""tests/test_three_soldiers_crows.py — ThreeSoldiersAndCrowsStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.three_soldiers_crows import ThreeSoldiersAndCrowsStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows, atr=1.0):
    n = len(rows)
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": [1000.0] * n,
        "atr14":  [atr] * n,
    }
    return pd.DataFrame(data)


def _neutral(n=6):
    return [(100.0, 102.0, 99.0, 101.0)] * n


def _soldiers_rows(avg_body_ratio=1.0, atr=1.0):
    """
    Three White Soldiers: 3봉 연속 양봉, 상승 close, body > range*0.6
    df[-2]=봉-1, df[-3]=봉-2, df[-4]=봉-3
    avg_body_ratio: avg_body / atr  (HIGH if > 0.8)
    """
    # Each candle: open, high, low, close
    # body = close - open (양봉), range = high - low
    # body > range * 0.6  =>  range < body / 0.6
    # Let body = atr * avg_body_ratio (approximately)
    body = atr * avg_body_ratio

    # 봉-3 (idx3): c3=102, o3=102-body
    c3 = 102.0
    o3 = c3 - body
    h3 = c3 + body * 0.2   # small wick
    l3 = o3 - body * 0.2
    # body/range = body/(h3-l3) = body/(body*1.4) = 0.71 > 0.6 ✓

    # 봉-2: higher close
    c2 = c3 + body * 0.5
    o2 = c2 - body
    h2 = c2 + body * 0.2
    l2 = o2 - body * 0.2

    # 봉-1: even higher close
    c1 = c2 + body * 0.5
    o1 = c1 - body
    h1 = c1 + body * 0.2
    l1 = o1 - body * 0.2

    rows = _neutral(6)
    rows.append((o3, h3, l3, c3))   # idx3
    rows.append((o2, h2, l2, c2))   # idx2
    rows.append((o1, h1, l1, c1))   # idx (봉-1)
    rows.append((o1, h1, l1, c1))   # trailing
    return rows


def _crows_rows(avg_body_ratio=1.0, atr=1.0):
    """
    Three Black Crows: 3봉 연속 음봉, 하락 close, body > range*0.6
    """
    body = atr * avg_body_ratio

    c3 = 98.0
    o3 = c3 + body
    h3 = o3 + body * 0.2
    l3 = c3 - body * 0.2

    c2 = c3 - body * 0.5
    o2 = c2 + body
    h2 = o2 + body * 0.2
    l2 = c2 - body * 0.2

    c1 = c2 - body * 0.5
    o1 = c1 + body
    h1 = o1 + body * 0.2
    l1 = c1 - body * 0.2

    rows = _neutral(6)
    rows.append((o3, h3, l3, c3))
    rows.append((o2, h2, l2, c2))
    rows.append((o1, h1, l1, c1))
    rows.append((o1, h1, l1, c1))
    return rows


strat = ThreeSoldiersAndCrowsStrategy()


# ── 1. 전략 이름 ─────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "three_soldiers_crows"


# ── 2. 데이터 부족 → HOLD LOW ────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_neutral(4))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. Three White Soldiers → BUY ────────────────────────────────────────────
def test_three_white_soldiers_buy():
    df = _make_df(_soldiers_rows(avg_body_ratio=1.0), atr=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 4. Three White Soldiers MEDIUM confidence (avg_body <= atr*0.8) ──────────
def test_soldiers_medium_confidence():
    # avg_body = atr * 0.5 < atr * 0.8
    df = _make_df(_soldiers_rows(avg_body_ratio=0.5), atr=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 5. Three White Soldiers HIGH confidence (avg_body > atr*0.8) ─────────────
def test_soldiers_high_confidence():
    # avg_body = atr * 1.0 > atr * 0.8
    df = _make_df(_soldiers_rows(avg_body_ratio=1.0), atr=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 6. Three Black Crows → SELL ──────────────────────────────────────────────
def test_three_black_crows_sell():
    df = _make_df(_crows_rows(avg_body_ratio=1.0), atr=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 7. Three Black Crows MEDIUM confidence ────────────────────────────────────
def test_crows_medium_confidence():
    df = _make_df(_crows_rows(avg_body_ratio=0.5), atr=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. Three Black Crows HIGH confidence ─────────────────────────────────────
def test_crows_high_confidence():
    df = _make_df(_crows_rows(avg_body_ratio=1.0), atr=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 9. 패턴 없음 (혼합 봉) → HOLD ────────────────────────────────────────────
def test_no_pattern_mixed_candles_hold():
    rows = _neutral(10)
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 10. close 상승 불충족 (Soldiers 실패) → HOLD ─────────────────────────────
def test_soldiers_no_ascending_close_hold():
    # 3봉 양봉이지만 close가 내려감
    atr = 1.0
    body = 1.0
    rows = _neutral(6)
    rows.append((99.0, 100.4, 98.6, 100.0))    # c3=100
    rows.append((98.5, 99.9, 98.1, 99.5))       # c2=99.5 < c3 → ascending 실패
    rows.append((99.0, 100.4, 98.6, 100.0))     # c1=100
    rows.append((99.0, 100.4, 98.6, 100.0))
    df = _make_df(rows, atr=atr)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 11. BUY Signal 필드 완전성 ────────────────────────────────────────────────
def test_buy_signal_fields():
    df = _make_df(_soldiers_rows(), atr=1.0)
    sig = strat.generate(df)
    assert sig.strategy == "three_soldiers_crows"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 12. SELL Signal 필드 완전성 ───────────────────────────────────────────────
def test_sell_signal_fields():
    df = _make_df(_crows_rows(), atr=1.0)
    sig = strat.generate(df)
    assert sig.strategy == "three_soldiers_crows"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 13. BUY reasoning에 "Three White Soldiers" 포함 ──────────────────────────
def test_buy_reasoning_contains_soldiers():
    df = _make_df(_soldiers_rows(), atr=1.0)
    sig = strat.generate(df)
    assert "Three White Soldiers" in sig.reasoning


# ── 14. SELL reasoning에 "Three Black Crows" 포함 ────────────────────────────
def test_sell_reasoning_contains_crows():
    df = _make_df(_crows_rows(), atr=1.0)
    sig = strat.generate(df)
    assert "Three Black Crows" in sig.reasoning
