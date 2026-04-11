"""CMFStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.cmf import CMFStrategy

_PERIOD = 20


def _make_df(n=50, cmf_target=None, close_above_ema=True, trend="bullish"):
    """
    cmf_target: None이면 기본 중립 데이터.
                'high_buy'  → CMF > 0.15
                'med_buy'   → 0.05 < CMF <= 0.15
                'high_sell' → CMF < -0.15
                'med_sell'  → -0.15 <= CMF < -0.05
    close_above_ema: True → close > ema50, False → close < ema50
    trend: 'bullish' → ema20 > ema50, 'bearish' → ema20 < ema50, 'neutral' → ema20 ≈ ema50
    """
    base_close = 110.0 if close_above_ema else 90.0
    ema50 = 100.0
    
    # 추세 반영
    if trend == "bullish":
        ema20 = 102.0  # ema50 > ema20 인데, 우리는 ema20 > ema50 원함 → swap
        ema20 = 105.0  # ema20 > ema50
    elif trend == "bearish":
        ema20 = 95.0   # ema20 < ema50
    else:  # neutral
        ema20 = 100.0

    if cmf_target in ("high_buy", "med_buy"):
        # MFM 양수: close 가 high 에 근접해야 함
        # MFM = ((close-low) - (high-close)) / (high-low)
        #      = (2*close - high - low) / (high - low)
        # close ≈ high → MFM ≈ +1
        closes = np.full(n, base_close)
        highs = closes + 0.1       # close ≈ high → MFM ≈ +1
        lows = closes - 2.0
        if cmf_target == "med_buy":
            # close=110, high=120, low=100 → range=20, num=220-120-100=0
            closes = np.full(n, base_close + 1.0)
            highs = closes + 9.0    # close=111, high=120
            lows = closes - 11.0    # low=100, range=20, MFM=(222-120-100)/20=2/20=0.10
    elif cmf_target in ("high_sell", "med_sell"):
        # MFM 음수: close 가 low 에 근접해야 함
        # close ≈ low → MFM ≈ -1
        closes = np.full(n, base_close)
        lows = closes - 0.1        # close ≈ low → MFM ≈ -1
        highs = closes + 2.0
        if cmf_target == "med_sell":
            # 대칭: close=89, low=80, high=100 → range=20, num=178-100-80=-2, mfm=-0.1
            closes = np.full(n, base_close - 1.0)
            lows = closes - 9.0
            highs = closes + 11.0
    else:
        # 중립: close 가 high-low 중간
        closes = np.full(n, base_close)
        highs = closes + 1.0
        lows = closes - 1.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": np.ones(n) * 1000.0,
        "ema20": np.full(n, ema20),
        "ema50": np.full(n, ema50),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _cmf_value(df):
    """실제 CMF 계산값 반환 (검증용)."""
    idx = len(df) - 2
    h = df["high"].iloc[idx - _PERIOD + 1: idx + 1]
    l = df["low"].iloc[idx - _PERIOD + 1: idx + 1]
    c = df["close"].iloc[idx - _PERIOD + 1: idx + 1]
    v = df["volume"].iloc[idx - _PERIOD + 1: idx + 1]
    hl = h - l
    mfm = ((c - l) - (h - c)) / hl.where(hl != 0, 1.0)
    return float((mfm * v).sum() / v.sum())


strategy = CMFStrategy()


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "cmf"


# ── 2. BUY 신호 (CMF>0.05, close>ema50, ema20>ema50, 볼륨 양호) ──────────
def test_buy_signal():
    df = _make_df(cmf_target="high_buy", close_above_ema=True, trend="bullish")
    cmf = _cmf_value(df)
    assert cmf > 0.05, f"CMF should be > 0.05, got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (CMF<-0.05, close<ema50, ema20<ema50, 볼륨 양호) ────────
def test_sell_signal():
    df = _make_df(cmf_target="high_sell", close_above_ema=False, trend="bearish")
    cmf = _cmf_value(df)
    assert cmf < -0.05, f"CMF should be < -0.05, got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (CMF > 0.15) ──────────────────────────────────
def test_buy_high_confidence():
    df = _make_df(cmf_target="high_buy", close_above_ema=True, trend="bullish")
    cmf = _cmf_value(df)
    assert cmf > 0.15, f"CMF should be > 0.15, got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence (0.05 < CMF <= 0.15) ────────────────────────
def test_buy_medium_confidence():
    df = _make_df(cmf_target="med_buy", close_above_ema=True, trend="bullish")
    cmf = _cmf_value(df)
    assert 0.05 < cmf <= 0.15, f"CMF should be in (0.05, 0.15], got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence (CMF < -0.15) ────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(cmf_target="high_sell", close_above_ema=False, trend="bearish")
    cmf = _cmf_value(df)
    assert cmf < -0.15, f"CMF should be < -0.15, got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence (-0.15 <= CMF < -0.05) ─────────────────────
def test_sell_medium_confidence():
    df = _make_df(cmf_target="med_sell", close_above_ema=False, trend="bearish")
    cmf = _cmf_value(df)
    assert -0.15 <= cmf < -0.05, f"CMF should be in [-0.15, -0.05), got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. CMF>0.05이지만 추세 역행 (ema20<ema50) → HOLD ──────────────────
def test_buy_cmf_but_no_trend_hold():
    df = _make_df(cmf_target="high_buy", close_above_ema=True, trend="bearish")
    cmf = _cmf_value(df)
    assert cmf > 0.05, f"CMF should be > 0.05, got {cmf}"
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ────────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. Signal 필드 완전성 ────────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "cmf"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "CMF" 포함 ───────────────────────────────────────
def test_buy_reasoning_contains_cmf():
    df = _make_df(cmf_target="high_buy", close_above_ema=True, trend="bullish")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "CMF" in sig.reasoning


# ── 12. SELL reasoning에 "CMF" 포함 ──────────────────────────────────────
def test_sell_reasoning_contains_cmf():
    df = _make_df(cmf_target="high_sell", close_above_ema=False, trend="bearish")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "CMF" in sig.reasoning


# ── 13. None 입력 → HOLD ─────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 14. HOLD 신호 (중립 데이터) ──────────────────────────────────────────
def test_hold_neutral():
    df = _make_df(n=50, trend="neutral")
    sig = strategy.generate(df)
    # 중립 데이터에서 CMF=0 → HOLD
    assert sig.action == Action.HOLD
