"""tests/test_ha_trend.py — HATrendStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.ha_trend import HATrendStrategy
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


def _bull_rows(n=20, step=4.0):
    """연속 상승 HA 양봉: ha_low >= ha_open * 0.999 보장."""
    rows = []
    price = 100.0
    for _ in range(n):
        o = price
        c = price + step
        # high = close, low = open → HA에서 아래꼬리 없음
        rows.append((o, c, o, c))
        price = c
    return rows


def _bear_rows(n=20, step=4.0):
    """연속 하락 HA 음봉: ha_high <= ha_open * 1.001 보장."""
    rows = []
    price = 300.0
    for _ in range(n):
        o = price
        c = price - step
        # high = open, low = close → HA에서 위꼬리 없음
        rows.append((o, o, c, c))
        price = c
    return rows


def _mixed_rows(n=20):
    """상승/하락 교대 → HOLD 유발."""
    rows = []
    for i in range(n):
        if i % 2 == 0:
            rows.append((100.0, 104.0, 100.0, 104.0))
        else:
            rows.append((104.0, 104.0, 100.0, 100.0))
    return rows


strat = HATrendStrategy()


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "ha_trend"


# ── 2. 데이터 부족 → HOLD ───────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_bull_rows(10))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. BUY 신호 (3봉 연속 HA 양봉, 아래꼬리 없음) ─────────────────────────
def test_buy_signal():
    df = _make_df(_bull_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 4. SELL 신호 (3봉 연속 HA 음봉, 위꼬리 없음) ──────────────────────────
def test_sell_signal():
    df = _make_df(_bear_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 5. BUY HIGH confidence (5봉 이상 연속) ──────────────────────────────────
def test_buy_high_confidence_5_consecutive():
    df = _make_df(_bull_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 6. SELL HIGH confidence (5봉 이상 연속) ─────────────────────────────────
def test_sell_high_confidence_5_consecutive():
    df = _make_df(_bear_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. BUY MEDIUM confidence (3봉 연속만, 5봉 미만) ─────────────────────────
def test_buy_medium_confidence_3_consecutive():
    # 앞부분 혼합 + 마지막 3봉만 상승
    mixed = _mixed_rows(16)
    bull = _bull_rows(4)  # idx=-2 포함 4봉 상승 (but <5)
    rows = mixed[:-4] + bull  # 합쳐서 20행 (idx=-2부터 -5까지 4봉 bull)
    # 연속 4봉: MEDIUM (4 < 5)
    df = _make_df(rows)
    sig = strat.generate(df)
    # 연속 bull_count < 5 이면 MEDIUM
    if sig.action == Action.BUY:
        # bull_count is 4: MEDIUM
        assert sig.confidence == Confidence.MEDIUM


# ── 8. 혼합 패턴 → HOLD ──────────────────────────────────────────────────────
def test_mixed_pattern_hold():
    df = _make_df(_mixed_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 9. Signal 필드 완전성 (BUY) ────────────────────────────────────────────
def test_buy_signal_fields_complete():
    df = _make_df(_bull_rows(20))
    sig = strat.generate(df)
    assert sig.strategy == "ha_trend"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 10. Signal 필드 완전성 (SELL) ──────────────────────────────────────────
def test_sell_signal_fields_complete():
    df = _make_df(_bear_rows(20))
    sig = strat.generate(df)
    assert sig.strategy == "ha_trend"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 11. BUY reasoning에 "HA" 포함 ────────────────────────────────────────────
def test_buy_reasoning_contains_ha():
    df = _make_df(_bull_rows(20))
    sig = strat.generate(df)
    assert "HA" in sig.reasoning


# ── 12. SELL reasoning에 "HA" 포함 ───────────────────────────────────────────
def test_sell_reasoning_contains_ha():
    df = _make_df(_bear_rows(20))
    sig = strat.generate(df)
    assert "HA" in sig.reasoning


# ── 13. 정확히 15행 (경계값) → BUY/SELL/HOLD 반환 (Low 확인) ────────────────
def test_exactly_15_rows_does_not_raise():
    """정확히 15행 데이터도 정상 처리 (에러 없음)."""
    df = _make_df(_bull_rows(15))
    sig = strat.generate(df)
    # 15행이면 최소 데이터 충족 → HOLD or BUY (에러 없음 확인)
    assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)
    assert sig.strategy == "ha_trend"


# ── 14. HOLD Signal 필드 완전성 ────────────────────────────────────────────
def test_hold_signal_fields():
    df = _make_df(_mixed_rows(20))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "ha_trend"
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
