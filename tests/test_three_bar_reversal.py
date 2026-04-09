"""tests/test_three_bar_reversal.py — ThreeBarReversalStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.three_bar_reversal import ThreeBarReversalStrategy
from src.strategy.base import Action, Confidence


strat = ThreeBarReversalStrategy()

BASE_VOLUME = 1000.0
HIGH_VOLUME = BASE_VOLUME * 1.3  # avg * 1.2 초과


def _make_df(rows, volumes=None):
    n = len(rows)
    vols = volumes if volumes is not None else [BASE_VOLUME] * n
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": vols,
    }
    return pd.DataFrame(data)


def _neutral(n=15, base=100.0):
    return [(base, base + 2, base - 1, base + 1)] * n


def _bullish_3bar_rows(vol_confirm=True, strong=False):
    """
    Bullish 3-bar reversal:
    - prev2: 음봉
    - prev1: inside bar (prev2 내부)
    - current: 양봉, close > prev2 open
    총 17봉 (idx=-2가 current)
    """
    rows = list(_neutral(14))
    # prev2: 음봉
    p2_o = 102.0
    p2_c = 99.0   # 음봉
    p2_h = 103.0
    p2_l = 98.5
    # prev1: inside bar (H < p2_h, L > p2_l)
    p1_h = 101.5
    p1_l = 99.5
    p1_o = 100.5
    p1_c = 100.0
    # current: 양봉, close > p2_o=102
    if strong:
        c_o = 99.0
        c_c = 104.0
        c_h = 104.5
        c_l = 98.8
    else:
        c_o = 99.2
        c_c = 102.5   # close > p2_o=102
        c_h = 102.8
        c_l = 99.0

    rows.append((p2_o, p2_h, p2_l, p2_c))   # index 14 = prev2
    rows.append((p1_o, p1_h, p1_l, p1_c))   # index 15 = prev1
    rows.append((c_o, c_h, c_l, c_c))        # index 16 = current (idx=-2)
    rows.append((c_o, c_h, c_l, c_c))        # index 17 = trailing

    vols = [BASE_VOLUME] * 17
    if vol_confirm:
        vols[16] = HIGH_VOLUME  # current 볼륨 높음
    else:
        vols[16] = BASE_VOLUME * 0.5  # 볼륨 낮음
    vols.append(BASE_VOLUME)  # trailing
    return rows, vols


def _bearish_3bar_rows(vol_confirm=True, strong=False):
    """
    Bearish 3-bar reversal:
    - prev2: 양봉
    - prev1: inside bar
    - current: 음봉, close < prev2 open
    """
    rows = list(_neutral(14))
    # prev2: 양봉
    p2_o = 99.0
    p2_c = 102.0  # 양봉
    p2_h = 102.5
    p2_l = 98.5
    # prev1: inside bar
    p1_h = 101.5
    p1_l = 99.5
    p1_o = 101.0
    p1_c = 100.5
    # current: 음봉, close < p2_o=99
    if strong:
        c_o = 102.0
        c_c = 97.0
        c_h = 102.5
        c_l = 96.5
    else:
        c_o = 101.5
        c_c = 98.5   # close < p2_o=99
        c_h = 101.8
        c_l = 98.2

    rows.append((p2_o, p2_h, p2_l, p2_c))
    rows.append((p1_o, p1_h, p1_l, p1_c))
    rows.append((c_o, c_h, c_l, c_c))
    rows.append((c_o, c_h, c_l, c_c))  # trailing

    vols = [BASE_VOLUME] * 17
    if vol_confirm:
        vols[16] = HIGH_VOLUME
    else:
        vols[16] = BASE_VOLUME * 0.5
    vols.append(BASE_VOLUME)
    return rows, vols


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "three_bar_reversal"


# ── 2. 데이터 부족 → HOLD ───────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_neutral(10))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. 패턴 없음 → HOLD ─────────────────────────────────────────────────────
def test_no_pattern_hold():
    df = _make_df(_neutral(17))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 4. Bullish 3-bar + 볼륨 확인 → BUY ─────────────────────────────────────
def test_bullish_3bar_buy():
    rows, vols = _bullish_3bar_rows(vol_confirm=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 5. Bullish 3-bar + 볼륨 부족 → HOLD ────────────────────────────────────
def test_bullish_3bar_no_volume_hold():
    rows, vols = _bullish_3bar_rows(vol_confirm=False)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Bearish 3-bar + 볼륨 확인 → SELL ────────────────────────────────────
def test_bearish_3bar_sell():
    rows, vols = _bearish_3bar_rows(vol_confirm=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 7. Bearish 3-bar + 볼륨 부족 → HOLD ────────────────────────────────────
def test_bearish_3bar_no_volume_hold():
    rows, vols = _bearish_3bar_rows(vol_confirm=False)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 8. Bullish HIGH confidence (range > 2x prev1) ───────────────────────────
def test_bullish_3bar_high_confidence():
    rows, vols = _bullish_3bar_rows(vol_confirm=True, strong=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 9. Bullish MEDIUM confidence (range <= 2x prev1) ────────────────────────
def test_bullish_3bar_medium_confidence():
    rows, vols = _bullish_3bar_rows(vol_confirm=True, strong=False)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 10. Bearish HIGH confidence (range > 2x prev1) ──────────────────────────
def test_bearish_3bar_high_confidence():
    rows, vols = _bearish_3bar_rows(vol_confirm=True, strong=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 11. Bearish MEDIUM confidence (range <= 2x prev1) ───────────────────────
def test_bearish_3bar_medium_confidence():
    rows, vols = _bearish_3bar_rows(vol_confirm=True, strong=False)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 12. BUY Signal 필드 완전성 ─────────────────────────────────────────────
def test_buy_signal_fields():
    rows, vols = _bullish_3bar_rows(vol_confirm=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.strategy == "three_bar_reversal"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 13. SELL Signal 필드 완전성 ────────────────────────────────────────────
def test_sell_signal_fields():
    rows, vols = _bearish_3bar_rows(vol_confirm=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.strategy == "three_bar_reversal"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 14. BUY reasoning에 "Reversal" 포함 ─────────────────────────────────────
def test_buy_reasoning_contains_reversal():
    rows, vols = _bullish_3bar_rows(vol_confirm=True)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert "Reversal" in sig.reasoning or "3-Bar" in sig.reasoning


# ── 15. inside bar 조건 미충족 → HOLD ───────────────────────────────────────
def test_not_inside_bar_hold():
    """prev1이 inside bar가 아닌 경우 HOLD."""
    rows = list(_neutral(14))
    # prev2: 음봉
    rows.append((102.0, 103.0, 98.5, 99.0))   # prev2
    # prev1: NOT inside bar (high > prev2 high)
    rows.append((100.5, 104.0, 99.5, 100.0))  # prev1 (H=104 > 103, 아님)
    rows.append((99.2, 102.8, 99.0, 102.5))   # current
    rows.append((99.2, 102.8, 99.0, 102.5))   # trailing
    vols = [BASE_VOLUME] * 17
    vols[16] = HIGH_VOLUME
    vols.append(BASE_VOLUME)
    df = _make_df(rows, vols)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
