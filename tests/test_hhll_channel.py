"""HHLLChannelStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.hhll_channel import HHLLChannelStrategy

strategy = HHLLChannelStrategy()


def _make_df(n=50, pos_pct=50.0, vol_surge=True):
    """
    pos_pct: 채널 내 포지션 퍼센트 (0~100)
    vol_surge: True → 마지막 봉 volume > 평균
    """
    hh = 100.0
    ll = 0.0
    close = ll + (hh - ll) * pos_pct / 100.0

    highs = np.full(n, hh, dtype=float)
    lows = np.full(n, ll, dtype=float)
    closes = np.full(n, close, dtype=float)
    volumes = np.ones(n) * 1000.0

    # 마지막 봉(idx) volume 조건
    if vol_surge:
        volumes[-2] = 1500.0  # idx = n-2
    else:
        volumes[-2] = 500.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": np.full(n, 50.0),
        "atr14": np.ones(n) * 1.0,
    })
    return df


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "hhll_channel"


# ── 2. BUY 신호 (Position > 80, vol_ok) ─────────────────────────────────
def test_buy_signal():
    df = _make_df(pos_pct=85.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (Position < 20, vol_ok) ────────────────────────────────
def test_sell_signal():
    df = _make_df(pos_pct=15.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (Position 중간) ──────────────────────────────────────────────
def test_hold_middle_position():
    df = _make_df(pos_pct=50.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 5. HOLD (Position > 80이지만 Volume 부족) ────────────────────────────
def test_buy_no_vol_hold():
    df = _make_df(pos_pct=85.0, vol_surge=False)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. HOLD (Position < 20이지만 Volume 부족) ────────────────────────────
def test_sell_no_vol_hold():
    df = _make_df(pos_pct=15.0, vol_surge=False)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. BUY HIGH confidence (Position > 90) ───────────────────────────────
def test_buy_high_confidence():
    df = _make_df(pos_pct=95.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 8. BUY MEDIUM confidence (80 < Position <= 90) ───────────────────────
def test_buy_medium_confidence():
    df = _make_df(pos_pct=85.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 9. SELL HIGH confidence (Position < 10) ──────────────────────────────
def test_sell_high_confidence():
    df = _make_df(pos_pct=5.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 10. SELL MEDIUM confidence (10 <= Position < 20) ─────────────────────
def test_sell_medium_confidence():
    df = _make_df(pos_pct=15.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 11. 데이터 부족 → HOLD ───────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 12. None 입력 → HOLD ─────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 13. Signal 필드 완전성 ───────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "hhll_channel"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 14. BUY reasoning에 "Position" 포함 ──────────────────────────────────
def test_buy_reasoning_contains_position():
    df = _make_df(pos_pct=85.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "Position" in sig.reasoning


# ── 15. SELL reasoning에 "Position" 포함 ─────────────────────────────────
def test_sell_reasoning_contains_position():
    df = _make_df(pos_pct=15.0, vol_surge=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "Position" in sig.reasoning


# ── 16. entry_price == close ──────────────────────────────────────────────
def test_entry_price_equals_close():
    df = _make_df(pos_pct=85.0, vol_surge=True)
    sig = strategy.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected_close)
