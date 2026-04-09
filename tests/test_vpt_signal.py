"""VPTSignalStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.vpt_signal import VPTSignalStrategy

strategy = VPTSignalStrategy()


def _make_df(n=100, cross="none", close_vs_ema="above", high_conf=False):
    """
    cross: "up"   → VPT_EMA 상향 크로스 VPT_Signal
           "down" → VPT_EMA 하향 크로스 VPT_Signal
           "none" → 크로스 없음
    close_vs_ema: "above" → close > ema50, "below" → close < ema50
    high_conf: True → 크로스 크기가 std보다 크도록 강한 변화
    """
    base = 100.0
    volumes = np.ones(n) * 1000.0

    # Strategy: build a price series that reliably triggers EWM14 vs EWM21 crossovers.
    # During sustained decline: EWM14 < EWM21 (faster reacts more to drops).
    # On a big spike up: EWM14 jumps above EWM21 → cross_up.
    # Reverse for cross_down.

    closes = np.full(n, base, dtype=float)

    if cross == "up":
        # Long declining phase to get EWM14 well below EWM21
        for i in range(1, n - 1):
            closes[i] = closes[i - 1] - 1.0
        # idx (n-2): massive spike up forces EWM14 above EWM21
        spike = 200.0 if high_conf else 80.0
        closes[n - 2] = closes[n - 3] + spike
        closes[n - 1] = closes[n - 2]  # last candle (ignored)
    elif cross == "down":
        # Long rising phase to get EWM14 well above EWM21
        for i in range(1, n - 1):
            closes[i] = closes[i - 1] + 1.0
        # idx (n-2): massive spike down forces EWM14 below EWM21
        # Drop must be very large relative to close to generate huge negative VPT
        drop_pct = 0.95 if high_conf else 0.80
        closes[n - 2] = closes[n - 3] * (1 - drop_pct)
        closes[n - 1] = closes[n - 2]
    # else: all flat → no cross

    close_last = closes[n - 2]
    if close_vs_ema == "above":
        ema50_val = close_last - 10.0
    else:
        ema50_val = close_last + 10.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": volumes,
        "ema50": np.full(n, ema50_val),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _compute_cross(df):
    """VPT_EMA / VPT_Signal 크로스 상태 반환 (검증용)."""
    idx = len(df) - 2
    price_change = df["close"].pct_change()
    vpt = (df["volume"] * price_change).cumsum()
    vpt_ema = vpt.ewm(span=14, adjust=False).mean()
    vpt_signal = vpt.ewm(span=21, adjust=False).mean()

    ema_now = float(vpt_ema.iloc[idx])
    ema_prev = float(vpt_ema.iloc[idx - 1])
    sig_now = float(vpt_signal.iloc[idx])
    sig_prev = float(vpt_signal.iloc[idx - 1])

    cross_up = ema_prev <= sig_prev and ema_now > sig_now
    cross_down = ema_prev >= sig_prev and ema_now < sig_now
    return cross_up, cross_down, ema_now, sig_now


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "vpt_signal"


# ── 2. BUY 신호 (상향 크로스 + close > EMA50) ────────────────────────────
def test_buy_signal():
    df = _make_df(cross="up", close_vs_ema="above")
    cross_up, _, _, _ = _compute_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (하향 크로스 + close < EMA50) ───────────────────────────
def test_sell_signal():
    df = _make_df(cross="down", close_vs_ema="below")
    _, cross_down, _, _ = _compute_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. 크로스 없음 → HOLD ────────────────────────────────────────────────
def test_hold_no_cross():
    df = _make_df(cross="none")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 5. BUY 크로스 but close < EMA50 → HOLD ───────────────────────────────
def test_buy_cross_but_below_ema50():
    df = _make_df(cross="up", close_vs_ema="below")
    cross_up, _, _, _ = _compute_cross(df)
    if cross_up:
        sig = strategy.generate(df)
        assert sig.action != Action.BUY


# ── 6. SELL 크로스 but close > EMA50 → HOLD ──────────────────────────────
def test_sell_cross_but_above_ema50():
    df = _make_df(cross="down", close_vs_ema="above")
    _, cross_down, _, _ = _compute_cross(df)
    if cross_down:
        sig = strategy.generate(df)
        assert sig.action != Action.SELL


# ── 7. 데이터 부족 → HOLD ───────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=15)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 8. None 입력 → HOLD ─────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 9. Signal 필드 완전성 ───────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "vpt_signal"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 10. BUY reasoning에 "VPT" 포함 ──────────────────────────────────────
def test_buy_reasoning_contains_vpt():
    df = _make_df(cross="up", close_vs_ema="above")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "VPT" in sig.reasoning


# ── 11. SELL reasoning에 "VPT" 포함 ─────────────────────────────────────
def test_sell_reasoning_contains_vpt():
    df = _make_df(cross="down", close_vs_ema="below")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "VPT" in sig.reasoning


# ── 12. entry_price == close[-2] ─────────────────────────────────────────
def test_entry_price_equals_close():
    df = _make_df(cross="up", close_vs_ema="above")
    sig = strategy.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── 13. BUY confidence 타입 검증 ─────────────────────────────────────────
def test_buy_confidence_type():
    df = _make_df(cross="up", close_vs_ema="above")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 14. SELL confidence 타입 검증 ────────────────────────────────────────
def test_sell_confidence_type():
    df = _make_df(cross="down", close_vs_ema="below")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
