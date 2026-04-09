"""VPTStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.vpt import VPTStrategy

strategy = VPTStrategy()


def _make_df(n=60, cross="none", sustained=False):
    """
    cross: "up"   → VPT 상향 크로스 (idx-1: VPT<=EMA, idx: VPT>EMA)
           "down" → VPT 하향 크로스
           "none" → 크로스 없음
    sustained: True  → idx-2에서도 같은 방향 (HIGH conf)
               False → idx-2에서 반대 방향 (MEDIUM conf)
    """
    base = 100.0
    closes = np.full(n, base, dtype=float)
    volumes = np.ones(n) * 1000.0

    if cross == "up":
        if sustained:
            # idx-2: VPT > EMA (이미 상향), idx-1: 잠깐 하락, idx: 다시 강한 상승
            half = n // 2
            for i in range(half):
                closes[i] = base - 0.5
            for i in range(half, n - 3):
                closes[i] = base + 0.5   # VPT 상승
            closes[n - 3] = base - 1.5  # idx-1: 일시 하락 (VPT <= EMA)
            closes[n - 2] = base + 5.0  # idx: 강한 상승 → cross_up
        else:
            # idx-2까지 하락, idx-1 하락, idx: 강한 상승
            for i in range(n - 2):
                closes[i] = base - 0.3
            closes[n - 3] = base - 0.3  # idx-1: VPT <= EMA
            closes[n - 2] = base + 8.0  # idx: cross_up
    elif cross == "down":
        if sustained:
            # idx-2: VPT < EMA (이미 하향), idx-1: 잠깐 상승, idx: 다시 강한 하락
            half = n // 2
            for i in range(half):
                closes[i] = base + 0.5
            for i in range(half, n - 3):
                closes[i] = base - 0.5  # VPT 하락
            closes[n - 3] = base + 1.5  # idx-1: 일시 상승 (VPT >= EMA)
            closes[n - 2] = base - 5.0  # idx: 강한 하락 → cross_down
        else:
            # idx-2까지 상승, idx-1 상승, idx: 강한 하락
            for i in range(n - 2):
                closes[i] = base + 0.3
            closes[n - 3] = base + 0.3  # idx-1: VPT >= EMA
            closes[n - 2] = base - 8.0  # idx: cross_down
    # cross == "none": 기본값 유지 (변화 없음)

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": volumes,
        "ema50": np.full(n, base),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _compute_vpt_cross(df):
    """VPT 크로스 상태 반환 (검증용)."""
    idx = len(df) - 2
    price_change = df["close"].pct_change()
    vpt = (df["volume"] * price_change).cumsum()
    vpt_ema = vpt.ewm(span=14, adjust=False).mean()

    vpt_now = float(vpt.iloc[idx])
    vpt_prev = float(vpt.iloc[idx - 1])
    vpt_prev2 = float(vpt.iloc[idx - 2])
    ema_now = float(vpt_ema.iloc[idx])
    ema_prev = float(vpt_ema.iloc[idx - 1])
    ema_prev2 = float(vpt_ema.iloc[idx - 2])

    cross_up = vpt_prev <= ema_prev and vpt_now > ema_now
    cross_down = vpt_prev >= ema_prev and vpt_now < ema_now
    return cross_up, cross_down, vpt_prev2, ema_prev2


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "vpt"


# ── 2. BUY 신호 (VPT 상향 크로스) ───────────────────────────────────────
def test_buy_signal():
    df = _make_df(cross="up", sustained=False)
    cross_up, _, _, _ = _compute_vpt_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (VPT 하향 크로스) ──────────────────────────────────────
def test_sell_signal():
    df = _make_df(cross="down", sustained=False)
    _, cross_down, _, _ = _compute_vpt_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (2봉 이상 유지) ───────────────────────────────
def test_buy_high_confidence():
    df = _make_df(cross="up", sustained=True)
    cross_up, _, vpt_prev2, ema_prev2 = _compute_vpt_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    assert vpt_prev2 > ema_prev2, f"vpt_prev2({vpt_prev2:.2f}) > ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence (방금 크로스) ───────────────────────────────
def test_buy_medium_confidence():
    df = _make_df(cross="up", sustained=False)
    cross_up, _, vpt_prev2, ema_prev2 = _compute_vpt_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    assert vpt_prev2 <= ema_prev2, f"vpt_prev2({vpt_prev2:.2f}) <= ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence (2봉 이상 유지) ──────────────────────────────
def test_sell_high_confidence():
    df = _make_df(cross="down", sustained=True)
    _, cross_down, vpt_prev2, ema_prev2 = _compute_vpt_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    assert vpt_prev2 < ema_prev2, f"vpt_prev2({vpt_prev2:.2f}) < ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence (방금 크로스) ──────────────────────────────
def test_sell_medium_confidence():
    df = _make_df(cross="down", sustained=False)
    _, cross_down, vpt_prev2, ema_prev2 = _compute_vpt_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    assert vpt_prev2 >= ema_prev2, f"vpt_prev2({vpt_prev2:.2f}) >= ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. HOLD (크로스 없음) ────────────────────────────────────────────────
def test_hold_no_cross():
    df = _make_df(cross="none")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ───────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. None 입력 → HOLD ─────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 11. Signal 필드 완전성 ───────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "vpt"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "VPT" 포함 ──────────────────────────────────────
def test_buy_reasoning_contains_vpt():
    df = _make_df(cross="up", sustained=False)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "VPT" in sig.reasoning


# ── 13. SELL reasoning에 "VPT" 포함 ─────────────────────────────────────
def test_sell_reasoning_contains_vpt():
    df = _make_df(cross="down", sustained=False)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "VPT" in sig.reasoning


# ── 14. entry_price == close ──────────────────────────────────────────────
def test_entry_price_equals_close():
    df = _make_df(cross="up", sustained=False)
    sig = strategy.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected_close)
