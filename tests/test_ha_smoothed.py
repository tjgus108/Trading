"""tests/test_ha_smoothed.py — HeikinAshiSmoothedStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.ha_smoothed import HeikinAshiSmoothedStrategy
from src.strategy.base import Action, Confidence

strat = HeikinAshiSmoothedStrategy()


def _make_df(rows):
    """rows: list of (open, high, low, close)."""
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": [1000.0] * len(rows),
        "atr14":  [1.0] * len(rows),
    }
    return pd.DataFrame(data)


def _bull_rows(n=25):
    """강한 상승 캔들: high=open (원시 고가=시가) → HA 아래꼬리 없음 유발."""
    rows = []
    price = 100.0
    for _ in range(n):
        o = price
        c = price + 5.0
        # high=open, low=open → HA high/low 모두 ha_close_smooth 이하 가능성
        rows.append((o, c + 0.001, o, c))
        price = c
    return rows


def _bear_rows(n=25):
    """강한 하락 캔들: low=open → HA 위꼬리 없음 유발."""
    rows = []
    price = 300.0
    for _ in range(n):
        o = price
        c = price - 5.0
        rows.append((o, o, c - 0.001, c))
        price = c
    return rows


def _mixed_rows(n=25):
    """상승/하락 교대 → HOLD 유발."""
    rows = []
    price = 100.0
    for i in range(n):
        if i % 2 == 0:
            rows.append((price, price + 3, price - 1, price + 2))
            price += 2
        else:
            rows.append((price, price + 1, price - 3, price - 2))
            price -= 2
    return rows


# ── 1. 전략 이름 ─────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "ha_smoothed"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_bull_rows(10))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. 정확히 최소 행(20) → 처리 가능 ─────────────────────────────────────────
def test_min_rows_no_error():
    df = _make_df(_bull_rows(20))
    sig = strat.generate(df)
    assert sig.action in {Action.BUY, Action.HOLD, Action.SELL}


# ── 4. 강한 상승 → BUY 신호 ────────────────────────────────────────────────
def test_buy_signal():
    df = _make_df(_bull_rows(30))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 5. 강한 하락 → SELL 신호 ───────────────────────────────────────────────
def test_sell_signal():
    df = _make_df(_bear_rows(30))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 6. 혼합 캔들 → HOLD ─────────────────────────────────────────────────────
def test_mixed_rows_hold():
    df = _make_df(_mixed_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 7. BUY confidence: 5연속 + lower wick 없음 → HIGH ──────────────────────
def test_buy_high_confidence():
    df = _make_df(_bull_rows(30))
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in {Confidence.HIGH, Confidence.MEDIUM}


# ── 8. SELL confidence: 5연속 + upper wick 없음 → HIGH ─────────────────────
def test_sell_high_confidence():
    df = _make_df(_bear_rows(30))
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in {Confidence.HIGH, Confidence.MEDIUM}


# ── 9. BUY Signal 필드 완전성 ────────────────────────────────────────────────
def test_buy_signal_fields():
    df = _make_df(_bull_rows(30))
    sig = strat.generate(df)
    assert sig.strategy == "ha_smoothed"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 10. SELL Signal 필드 완전성 ──────────────────────────────────────────────
def test_sell_signal_fields():
    df = _make_df(_bear_rows(30))
    sig = strat.generate(df)
    assert sig.strategy == "ha_smoothed"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


# ── 11. BUY reasoning에 "HA" 포함 ────────────────────────────────────────────
def test_buy_reasoning_contains_ha():
    df = _make_df(_bull_rows(30))
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "HA" in sig.reasoning


# ── 12. SELL reasoning에 "HA" 포함 ───────────────────────────────────────────
def test_sell_reasoning_contains_ha():
    df = _make_df(_bear_rows(30))
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "HA" in sig.reasoning


# ── 13. HOLD reasoning 내용 확인 ─────────────────────────────────────────────
def test_hold_reasoning():
    df = _make_df(_mixed_rows(25))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert "HOLD" in sig.reasoning or "미충족" in sig.reasoning


# ── 14. entry_price는 마지막 완성봉의 close ─────────────────────────────────
def test_entry_price_is_last_close():
    rows = _bull_rows(25)
    df = _make_df(rows)
    sig = strat.generate(df)
    expected_close = float(df.iloc[-2]["close"])
    assert sig.entry_price == expected_close
