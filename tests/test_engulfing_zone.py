"""tests/test_engulfing_zone.py — BullishEngulfingZoneStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.engulfing_zone import BullishEngulfingZoneStrategy
from src.strategy.base import Action, Confidence


strat = BullishEngulfingZoneStrategy()


def _make_df(rows, volumes=None):
    """rows: list of (open, high, low, close)"""
    n = len(rows)
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": volumes if volumes is not None else [1000.0] * n,
    }
    return pd.DataFrame(data)


def _neutral(n=30, base=100.0):
    """평범한 캔들 (패턴 없음)."""
    return [(base, base + 2, base - 1, base + 1)] * n


def _build_bullish_zone_df(ratio=1.2, near_support=True):
    """
    Pivot low를 만들고 bullish engulfing at support zone 시나리오 생성.
    - pivot low: index 11, low=90.0 (좌우 3봉 low=99보다 확연히 낮음)
    - prev (idx-3): 음봉, open=92, close=90.5, body=1.5
    - curr (idx-2): 양봉, open=90.3, close=90.3+1.5*ratio (body=1.5*ratio)
      near_support=True: close ≈ 90.45 (within ±1% of 90.0)
    - trailing (idx-1): dummy
    """
    rows = []
    support = 90.0  # pivot low 가격
    # 0~9: 평범한 봉 (low=99)
    for _ in range(10):
        rows.append((100.0, 102.0, 99.0, 101.0))
    # 10~12: pivot low (index 11 low=90, 좌우 low=99)
    rows.append((100.0, 102.0, 99.0, 101.0))         # 10
    rows.append((100.0, 101.0, support, 100.5))        # 11 = pivot low
    rows.append((100.0, 102.0, 99.0, 101.0))         # 12
    # 13~24: 평범한 봉
    for _ in range(12):
        rows.append((100.0, 102.0, 99.0, 101.0))
    # prev (index 25): 음봉, body=1.5
    prev_o = 92.0
    body_prev = 1.5
    prev_c = prev_o - body_prev   # 90.5 (음봉)
    # curr (index 26): 양봉
    # body_curr = body_prev * ratio = 1.5 * ratio
    # near_support: close must be within ±1% of support=90.0 → [89.1, 90.9]
    # We set curr_c = 90.45 (within range), curr_o = curr_c - body_curr
    if near_support:
        curr_c = 90.45  # within ±1% of 90.0
        curr_o = curr_c - body_prev * ratio  # e.g. 90.45 - 1.8 = 88.65
    else:
        curr_c = 105.0  # far from support
        curr_o = curr_c - body_prev * ratio
    rows.append((prev_o, prev_o + 0.5, prev_c - 0.2, prev_c))        # index 25 = prev
    rows.append((curr_o, curr_c + 0.1, curr_o - 0.1, curr_c))        # index 26 = curr
    rows.append((curr_o, curr_c + 0.1, curr_o - 0.1, curr_c))        # index 27 = trailing
    return rows


def _build_bearish_zone_df(ratio=1.2, near_resistance=True):
    """
    Bearish engulfing at resistance zone 시나리오.
    - pivot high: index 11, high=112.0 (좌우 3봉 high=102보다 확연히 높음)
    - prev (idx-3): 양봉, open=108, close=109.5, body=1.5
    - curr (idx-2): 음봉, open=109.8, close=109.8-1.5*ratio (body=1.5*ratio)
      near_resistance=True: close ≈ 111.44 (within ±1% of 112.0)
    - trailing (idx-1): dummy
    """
    rows = []
    resistance = 112.0  # pivot high 가격
    # 0~9: 평범한 봉 (high=102)
    for _ in range(10):
        rows.append((100.0, 102.0, 99.0, 101.0))
    # 10~12: pivot high (index 11 high=112, 좌우 high=102)
    rows.append((100.0, 102.0, 99.0, 101.0))          # 10
    rows.append((111.0, resistance, 110.0, 111.5))     # 11 = pivot high
    rows.append((100.0, 102.0, 99.0, 101.0))          # 12
    # 13~24: 평범한 봉
    for _ in range(12):
        rows.append((100.0, 102.0, 99.0, 101.0))
    # prev (index 25): 양봉, body=1.5
    prev_o = 108.0
    body_prev = 1.5
    prev_c = prev_o + body_prev   # 109.5 (양봉)
    # curr (index 26): 음봉
    # near_resistance: close within ±1% of resistance=112.0 → [110.88, 113.12]
    if near_resistance:
        curr_c = 111.44  # within ±1% of 112.0
        curr_o = curr_c + body_prev * ratio  # 111.44 + 1.8 = 113.24
    else:
        curr_c = 95.0  # far from resistance
        curr_o = curr_c + body_prev * ratio
    rows.append((prev_o, prev_c + 0.1, prev_o - 0.1, prev_c))        # index 25 = prev
    rows.append((curr_o, curr_o + 0.1, curr_c - 0.1, curr_c))        # index 26 = curr
    rows.append((curr_o, curr_o + 0.1, curr_c - 0.1, curr_c))        # index 27 = trailing
    return rows


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "engulfing_zone"


# ── 2. 데이터 부족 → HOLD ───────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_neutral(20))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. 데이터 충분하지만 패턴 없음 → HOLD ──────────────────────────────────
def test_no_pattern_hold():
    df = _make_df(_neutral(30))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 4. Bullish Engulfing + Support Zone → BUY ───────────────────────────────
def test_bullish_engulfing_zone_buy():
    df = _make_df(_build_bullish_zone_df(ratio=1.2, near_support=True))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 5. Bullish Engulfing 없음 (support 아님) → HOLD ──────────────────────────
def test_bullish_engulfing_no_zone_hold():
    df = _make_df(_build_bullish_zone_df(ratio=1.2, near_support=False))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Bearish Engulfing + Resistance Zone → SELL ───────────────────────────
def test_bearish_engulfing_zone_sell():
    df = _make_df(_build_bearish_zone_df(ratio=1.2, near_resistance=True))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 7. Bearish Engulfing 없음 (resistance 아님) → HOLD ───────────────────────
def test_bearish_engulfing_no_zone_hold():
    df = _make_df(_build_bearish_zone_df(ratio=1.2, near_resistance=False))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 8. BUY HIGH confidence (ratio > 1.5) ────────────────────────────────────
def test_bullish_engulfing_high_confidence():
    df = _make_df(_build_bullish_zone_df(ratio=1.6, near_support=True))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 9. BUY MEDIUM confidence (ratio 1.1~1.5) ────────────────────────────────
def test_bullish_engulfing_medium_confidence():
    df = _make_df(_build_bullish_zone_df(ratio=1.2, near_support=True))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 10. SELL HIGH confidence (ratio > 1.5) ──────────────────────────────────
def test_bearish_engulfing_high_confidence():
    df = _make_df(_build_bearish_zone_df(ratio=1.6, near_resistance=True))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 11. SELL MEDIUM confidence (ratio 1.1~1.5) ──────────────────────────────
def test_bearish_engulfing_medium_confidence():
    df = _make_df(_build_bearish_zone_df(ratio=1.2, near_resistance=True))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 12. BUY Signal 필드 완전성 ─────────────────────────────────────────────
def test_buy_signal_fields():
    df = _make_df(_build_bullish_zone_df(ratio=1.2, near_support=True))
    sig = strat.generate(df)
    assert sig.strategy == "engulfing_zone"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 13. SELL Signal 필드 완전성 ────────────────────────────────────────────
def test_sell_signal_fields():
    df = _make_df(_build_bearish_zone_df(ratio=1.2, near_resistance=True))
    sig = strat.generate(df)
    assert sig.strategy == "engulfing_zone"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 14. reasoning에 "Zone" 포함 ────────────────────────────────────────────
def test_buy_reasoning_contains_zone():
    df = _make_df(_build_bullish_zone_df(ratio=1.2, near_support=True))
    sig = strat.generate(df)
    assert "Zone" in sig.reasoning or "zone" in sig.reasoning or "Support" in sig.reasoning


# ── 15. body ratio 1.05 (< 1.1) → HOLD (body 조건 미충족) ───────────────────
def test_body_ratio_too_small_hold():
    """ratio < 1.1 이면 engulfing 조건 미충족."""
    rows = list(_build_bullish_zone_df(ratio=1.05, near_support=True))
    df = _make_df(rows)
    sig = strat.generate(df)
    # ratio < 1.1 이므로 BUY 아님
    assert sig.action == Action.HOLD
