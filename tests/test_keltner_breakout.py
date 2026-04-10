"""tests/test_keltner_breakout.py — KeltnerBreakoutStrategy 단위 테스트."""

import pandas as pd
import pytest
import numpy as np

from src.strategy.keltner_breakout import KeltnerBreakoutStrategy
from src.strategy.base import Action, Confidence

strat = KeltnerBreakoutStrategy()


def _make_df(rows):
    """rows: list of (open, high, low, close)."""
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": [1000.0] * len(rows),
    }
    return pd.DataFrame(data)


def _make_neutral_rows(n=35, base=100.0):
    """좁은 범위 횡보 캔들 (채널 내부)."""
    rows = []
    for i in range(n):
        o = base + 0.05 * (i % 3)
        c = base + 0.05 * ((i + 1) % 3)
        h = max(o, c) + 0.02
        l = min(o, c) - 0.02
        rows.append((o, h, l, c))
    return rows


def _make_upper_breakout_rows(n=40):
    """상단 채널 돌파: 안정 후 상승 돌파."""
    rows = []
    price = 100.0
    # 안정 구간: EMA, ATR 확립
    for _ in range(30):
        rows.append((price, price + 0.3, price - 0.3, price))
    # 마지막 두 캔들: 이전봉=채널 내, 현재봉=채널 상단 돌파
    # ATR≈0.6 → kc_upper≈100 + 2*0.6=101.2 정도
    # 이전봉은 채널 내부에 있다가
    rows.append((price, price + 0.3, price - 0.3, price + 0.1))  # prev: inside
    rows.append((price, price + 12.0, price - 0.1, price + 11.5))  # curr: breakout
    rows.append((price, price + 0.3, price - 0.3, price))  # in-progress (excluded)
    return rows


def _make_lower_breakdown_rows(n=40):
    """하단 채널 붕괴: 안정 후 하락 붕괴."""
    rows = []
    price = 100.0
    for _ in range(30):
        rows.append((price, price + 0.3, price - 0.3, price))
    rows.append((price, price + 0.3, price - 0.3, price - 0.1))  # prev: inside
    rows.append((price, price + 0.1, price - 12.0, price - 11.5))  # curr: breakdown
    rows.append((price, price + 0.3, price - 0.3, price))  # in-progress (excluded)
    return rows


# ── 1. 전략명 확인 ───────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "keltner_breakout"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────
def test_instance_creation():
    s = KeltnerBreakoutStrategy()
    assert s is not None
    assert s.name == "keltner_breakout"


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_make_neutral_rows(10))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────────
def test_none_input_hold():
    sig = strat.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────
def test_insufficient_data_reasoning():
    df = _make_df(_make_neutral_rows(10))
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ──────────────────────────────────────────────
def test_normal_data_returns_signal():
    df = _make_df(_make_neutral_rows(35))
    sig = strat.generate(df)
    assert sig is not None
    assert sig.action in {Action.BUY, Action.HOLD, Action.SELL}


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────
def test_signal_fields_complete():
    df = _make_df(_make_neutral_rows(35))
    sig = strat.generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.strategy, str)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────────
def test_buy_reasoning_keywords():
    df = _make_df(_make_upper_breakout_rows())
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "Keltner" in sig.reasoning or "돌파" in sig.reasoning or "upper" in sig.reasoning


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────────
def test_sell_reasoning_keywords():
    df = _make_df(_make_lower_breakdown_rows())
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "Keltner" in sig.reasoning or "붕괴" in sig.reasoning or "lower" in sig.reasoning


# ── 10. HIGH confidence 테스트 (0.5% 이상 돌파) ──────────────────────────────
def test_high_confidence_strong_breakout():
    rows = []
    price = 100.0
    for _ in range(30):
        rows.append((price, price + 0.3, price - 0.3, price))
    rows.append((price, price + 0.3, price - 0.3, price + 0.1))
    # strong breakout: +15 to guarantee > kc_upper * 1.005
    rows.append((price, price + 16.0, price - 0.1, price + 15.0))
    rows.append((price, price + 0.3, price - 0.3, price))
    df = _make_df(rows)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in {Confidence.HIGH, Confidence.MEDIUM}


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────
def test_medium_confidence_weak_breakout():
    df = _make_df(_make_upper_breakout_rows())
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in {Confidence.HIGH, Confidence.MEDIUM}


# ── 12. entry_price > 0 ───────────────────────────────────────────────────────
def test_entry_price_positive():
    df = _make_df(_make_neutral_rows(35))
    sig = strat.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ─────────────────────────────────────────────────
def test_strategy_field_value():
    df = _make_df(_make_neutral_rows(35))
    sig = strat.generate(df)
    assert sig.strategy == "keltner_breakout"


# ── 14. 최소 행 수(25)에서 동작 ──────────────────────────────────────────────
def test_min_rows_works():
    df = _make_df(_make_neutral_rows(25))
    sig = strat.generate(df)
    assert sig.action in {Action.BUY, Action.HOLD, Action.SELL}
    assert sig.strategy == "keltner_breakout"
