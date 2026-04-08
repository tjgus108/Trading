"""tests/test_heikin_ashi.py — HeikinAshiStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.heikin_ashi import HeikinAshiStrategy
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


# 연속 상승 HA를 만드는 캔들 시퀀스
# h = open 으로 설정 → raw_high <= ha_close 보장 → HA 위꼬리 없음 (HIGH confidence)
def _bull_rows(n=15):
    rows = []
    price = 100.0
    for i in range(n):
        o = price
        c = price + 4.0
        h = o          # raw_high = open <= ha_close → HA 위꼬리 없음
        l = o
        rows.append((o, h, l, c))
        price = c
    return rows


# 연속 하락 HA를 만드는 캔들 시퀀스
# l = open 으로 설정 → raw_low >= ha_open 보장 → HA 아래꼬리 없음 (HIGH confidence)
def _bear_rows(n=15):
    rows = []
    price = 200.0
    for i in range(n):
        o = price
        c = price - 4.0
        h = o
        l = o          # raw_low = open >= ha_open → HA 아래꼬리 없음
        rows.append((o, h, l, c))
        price = c
    return rows


strat = HeikinAshiStrategy()


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "heikin_ashi"


# ── 2. BUY 신호 ─────────────────────────────────────────────────────────────
def test_buy_signal():
    df = _make_df(_bull_rows(15))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ────────────────────────────────────────────────────────────
def test_sell_signal():
    df = _make_df(_bear_rows(15))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (위꼬리 없음) ────────────────────────────────────
def test_buy_high_confidence():
    """위꼬리 없는 연속 상승 → HIGH."""
    df = _make_df(_bull_rows(15))
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence (위꼬리 있음) ──────────────────────────────────
def test_buy_medium_confidence():
    """위꼬리 추가 → MEDIUM."""
    rows = _bull_rows(15)
    # 마지막 완성 캔들(idx=-2)에 위꼬리 추가
    last_idx = len(rows) - 2
    o, h, l, c = rows[last_idx]
    rows[last_idx] = (o, c + 1.0, l, c)   # high > close → 위꼬리 발생
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence (아래꼬리 없음) ─────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(_bear_rows(15))
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence (아래꼬리 있음) ───────────────────────────────
def test_sell_medium_confidence():
    rows = _bear_rows(15)
    last_idx = len(rows) - 2
    o, h, l, c = rows[last_idx]
    rows[last_idx] = (o, h, c - 1.0, c)   # low < open → 아래꼬리 발생
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. 2봉만 상승 → HOLD ─────────────────────────────────────────────────────
def test_two_bull_candles_hold():
    """3봉 연속 조건 미충족 → HOLD.
    상승/하락 교대 패턴으로 3봉 연속 달성 불가.
    """
    rows = _make_mixed_rows()
    df = _make_df(rows)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ───────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_bull_rows(5))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 10. Signal 필드 완전성 ──────────────────────────────────────────────────
def test_signal_fields_complete():
    df = _make_df(_bull_rows(15))
    sig = strat.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "heikin_ashi"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


# ── 11. BUY reasoning에 "Heikin" 또는 "HA" 포함 ─────────────────────────────
def test_buy_reasoning_contains_heikin_or_ha():
    df = _make_df(_bull_rows(15))
    sig = strat.generate(df)
    assert "Heikin" in sig.reasoning or "HA" in sig.reasoning


# ── 12. SELL reasoning에 "Heikin" 또는 "HA" 포함 ────────────────────────────
def test_sell_reasoning_contains_heikin_or_ha():
    df = _make_df(_bear_rows(15))
    sig = strat.generate(df)
    assert "Heikin" in sig.reasoning or "HA" in sig.reasoning


# ── 보너스: HOLD reasoning 체크 ─────────────────────────────────────────────
def test_hold_signal_fields():
    df = _make_df(_make_mixed_rows())
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "heikin_ashi"


def _make_mixed_rows():
    """상승/하락 혼합 → HOLD 유발."""
    rows = []
    for i in range(15):
        if i % 2 == 0:
            rows.append((100.0, 103.0, 99.0, 102.0))
        else:
            rows.append((102.0, 103.0, 98.0, 99.0))
    return rows
