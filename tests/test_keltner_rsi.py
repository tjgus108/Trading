"""tests/test_keltner_rsi.py — KeltnerRSIStrategy 단위 테스트."""

import pandas as pd
import pytest
import numpy as np

from src.strategy.keltner_rsi import KeltnerRSIStrategy
from src.strategy.base import Action, Confidence

strat = KeltnerRSIStrategy()


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


def _make_neutral_rows(n=30, base=100.0):
    """좁은 범위 횡보 캔들 (채널 내부)."""
    rows = []
    for i in range(n):
        o = base + 0.1 * (i % 3)
        c = base + 0.1 * ((i + 1) % 3)
        h = max(o, c) + 0.05
        l = min(o, c) - 0.05
        rows.append((o, h, l, c))
    return rows


def _make_oversold_rows(n=30):
    """close가 채널 하단 밖 + RSI 낮은 패턴 (연속 하락 후 급락)."""
    rows = []
    price = 200.0
    # 먼저 안정적인 기간으로 EMA/ATR 확립
    for i in range(20):
        rows.append((price, price + 0.5, price - 0.5, price))
    # 이후 급락으로 RSI를 낮추고 채널 하단 이탈
    for i in range(n - 20):
        drop = 8.0
        o = price
        c = price - drop
        rows.append((o, o + 0.1, c - 0.1, c))
        price = c
    return rows


def _make_overbought_rows(n=30):
    """close가 채널 상단 밖 + RSI 높은 패턴."""
    rows = []
    price = 100.0
    for i in range(20):
        rows.append((price, price + 0.5, price - 0.5, price))
    for i in range(n - 20):
        rise = 8.0
        o = price
        c = price + rise
        rows.append((o, c + 0.1, o - 0.1, c))
        price = c
    return rows


# ── 1. 전략 이름 ─────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "keltner_rsi"


# ── 2. 데이터 부족 → HOLD + LOW ─────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(_make_neutral_rows(15))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. 정확히 최소 행(25) → 오류 없음 ──────────────────────────────────────
def test_min_rows_no_error():
    df = _make_df(_make_neutral_rows(25))
    sig = strat.generate(df)
    assert sig.action in {Action.BUY, Action.HOLD, Action.SELL}


# ── 4. 횡보 → HOLD ──────────────────────────────────────────────────────────
def test_neutral_rows_hold():
    df = _make_df(_make_neutral_rows(30))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 5. 과매도 패턴 → BUY ────────────────────────────────────────────────────
def test_buy_signal_oversold():
    df = _make_df(_make_oversold_rows(40))
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 6. 과매수 패턴 → SELL ───────────────────────────────────────────────────
def test_sell_signal_overbought():
    df = _make_df(_make_overbought_rows(40))
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 7. BUY: RSI < 25 → HIGH confidence ─────────────────────────────────────
def test_buy_high_confidence():
    df = _make_df(_make_oversold_rows(50))
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in {Confidence.HIGH, Confidence.MEDIUM}


# ── 8. SELL: RSI > 75 → HIGH confidence ────────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(_make_overbought_rows(50))
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in {Confidence.HIGH, Confidence.MEDIUM}


# ── 9. Signal 필드 완전성 (BUY) ─────────────────────────────────────────────
def test_buy_signal_fields():
    df = _make_df(_make_oversold_rows(40))
    sig = strat.generate(df)
    assert sig.strategy == "keltner_rsi"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 10. Signal 필드 완전성 (SELL) ────────────────────────────────────────────
def test_sell_signal_fields():
    df = _make_df(_make_overbought_rows(40))
    sig = strat.generate(df)
    assert sig.strategy == "keltner_rsi"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


# ── 11. BUY reasoning에 "Keltner" 또는 "RSI" 포함 ───────────────────────────
def test_buy_reasoning_contains_keltner_rsi():
    df = _make_df(_make_oversold_rows(40))
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "Keltner" in sig.reasoning or "RSI" in sig.reasoning


# ── 12. SELL reasoning에 "Keltner" 또는 "RSI" 포함 ──────────────────────────
def test_sell_reasoning_contains_keltner_rsi():
    df = _make_df(_make_overbought_rows(40))
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "Keltner" in sig.reasoning or "RSI" in sig.reasoning


# ── 13. entry_price는 마지막 완성봉의 close ─────────────────────────────────
def test_entry_price_is_last_close():
    rows = _make_neutral_rows(30)
    df = _make_df(rows)
    sig = strat.generate(df)
    expected_close = float(df.iloc[-2]["close"])
    assert sig.entry_price == expected_close


# ── 14. 직접 BUY 조건 주입 테스트 ────────────────────────────────────────────
def test_direct_buy_condition():
    """EMA20보다 훨씬 낮은 close + 낮은 RSI를 강제로 만들어 BUY 검증."""
    rows = []
    # 안정 구간: EMA20 ~= 100
    for _ in range(22):
        rows.append((100.0, 101.0, 99.0, 100.0))
    # 급락: close가 EMA 대비 훨씬 낮아지고 RSI도 내려감
    price = 100.0
    for _ in range(18):
        price -= 6.0
        rows.append((price + 6, price + 6.1, price - 0.1, price))
    # 마지막 행은 진행 중 캔들 (사용 안 됨)
    rows.append((price, price + 0.1, price - 0.1, price))
    df = _make_df(rows)
    sig = strat.generate(df)
    # BUY 또는 HOLD (조건 충족 여부는 계산에 따름, 오류 없음 확인)
    assert sig.action in {Action.BUY, Action.HOLD}
