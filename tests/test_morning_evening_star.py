"""tests/test_morning_evening_star.py — MorningEveningStarStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.morning_evening_star import MorningEveningStarStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows, atr=2.0):
    """rows: list of (open, high, low, close) tuples."""
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


def _neutral(n=8):
    return [(100.0, 102.0, 99.0, 101.0)] * n


def _morning_star_rows(recovery_ratio=0.6, atr=2.0):
    """
    봉-3: 강한 음봉 body=3.0 > atr*0.7=1.4
    봉-2: 소형 몸통 body=0.1 < atr*0.3=0.6
    봉-1: 양봉, c3 + body3*recovery_ratio 이상 회복
    df[-2] = 봉-1(idx), df[-3] = 봉-2, df[-4] = 봉-3
    """
    # atr=2.0 → strong candle > 1.4, small < 0.6
    body3 = 3.0   # > 2.0*0.7
    o3 = 105.0
    c3 = o3 - body3   # 102.0 (음봉)

    o2 = 101.8
    c2 = 101.9        # body=0.1 < 0.6

    # recovery: c1 = c3 + body3*recovery_ratio
    c1_target = c3 + body3 * recovery_ratio
    o1 = c3 - 0.1     # 양봉: c1 > o1
    c1 = c1_target

    rows = _neutral(7)
    rows.append((o3, o3, c3, c3))         # idx3
    rows.append((o2, o2 + 0.1, c2, c2))   # idx2
    rows.append((o1, c1 + 0.1, o1, c1))   # idx (봉-1, last completed)
    rows.append((o1, c1 + 0.1, o1, c1))   # trailing (not used)
    return rows


def _evening_star_rows(penetration_ratio=0.6, atr=2.0):
    """
    봉-3: 강한 양봉 body=3.0
    봉-2: 소형 몸통 body=0.1
    봉-1: 음봉, c3 - body3*penetration_ratio 이하
    """
    body3 = 3.0
    o3 = 100.0
    c3 = o3 + body3   # 103.0 (양봉)

    o2 = 103.3
    c2 = 103.2        # body=0.1

    c1_target = c3 - body3 * penetration_ratio
    o1 = c3 + 0.1     # 음봉: c1 < o1
    c1 = c1_target

    rows = _neutral(7)
    rows.append((o3, c3, o3, c3))         # idx3
    rows.append((o2, o2 + 0.1, c2, c2))   # idx2
    rows.append((o1, o1, c1, c1))         # idx (봉-1)
    rows.append((o1, o1, c1, c1))         # trailing
    return rows


strat = MorningEveningStarStrategy()


# ── 1. 전략 이름 ─────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "morning_evening_star"


# ── 2. 데이터 부족 → HOLD LOW ────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_neutral(5))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. Morning Star → BUY ─────────────────────────────────────────────────────
def test_morning_star_buy():
    df = _make_df(_morning_star_rows(recovery_ratio=0.6))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 4. Morning Star MEDIUM confidence (50%~75%) ───────────────────────────────
def test_morning_star_medium_confidence():
    df = _make_df(_morning_star_rows(recovery_ratio=0.6))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 5. Morning Star HIGH confidence (>75%) ───────────────────────────────────
def test_morning_star_high_confidence():
    df = _make_df(_morning_star_rows(recovery_ratio=0.8))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 6. Morning Star 회복 < 50% → HOLD ────────────────────────────────────────
def test_morning_star_insufficient_recovery_hold():
    df = _make_df(_morning_star_rows(recovery_ratio=0.3))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 7. Evening Star → SELL ───────────────────────────────────────────────────
def test_evening_star_sell():
    df = _make_df(_evening_star_rows(penetration_ratio=0.6))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 8. Evening Star MEDIUM confidence ────────────────────────────────────────
def test_evening_star_medium_confidence():
    df = _make_df(_evening_star_rows(penetration_ratio=0.6))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 9. Evening Star HIGH confidence (>75%) ───────────────────────────────────
def test_evening_star_high_confidence():
    df = _make_df(_evening_star_rows(penetration_ratio=0.8))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 10. Evening Star 침범 < 50% → HOLD ───────────────────────────────────────
def test_evening_star_insufficient_penetration_hold():
    df = _make_df(_evening_star_rows(penetration_ratio=0.3))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 11. 패턴 없음 → HOLD ──────────────────────────────────────────────────────
def test_no_pattern_hold():
    rows = _neutral(12)
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 12. BUY Signal 필드 완전성 ────────────────────────────────────────────────
def test_buy_signal_fields():
    df = _make_df(_morning_star_rows(recovery_ratio=0.6))
    sig = strat.generate(df)
    assert sig.strategy == "morning_evening_star"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 13. SELL Signal 필드 완전성 ───────────────────────────────────────────────
def test_sell_signal_fields():
    df = _make_df(_evening_star_rows(penetration_ratio=0.6))
    sig = strat.generate(df)
    assert sig.strategy == "morning_evening_star"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 14. BUY reasoning에 "Morning Star" 포함 ──────────────────────────────────
def test_buy_reasoning_contains_morning_star():
    df = _make_df(_morning_star_rows(recovery_ratio=0.6))
    sig = strat.generate(df)
    assert "Morning Star" in sig.reasoning


# ── 15. SELL reasoning에 "Evening Star" 포함 ─────────────────────────────────
def test_sell_reasoning_contains_evening_star():
    df = _make_df(_evening_star_rows(penetration_ratio=0.6))
    sig = strat.generate(df)
    assert "Evening Star" in sig.reasoning
