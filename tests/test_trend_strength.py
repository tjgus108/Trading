"""TrendStrengthStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.trend_strength import TrendStrengthStrategy

strategy = TrendStrengthStrategy()


def _make_df(n=60, tsi_val=None, close_vs_ema="above"):
    """
    tsi_val: None → 자연 생성, float → 마지막 완성 캔들에서 해당 TSI 근사치 유도
    close_vs_ema: "above" → close > ema50, "below" → close < ema50
    """
    base = 100.0
    closes = np.full(n, base, dtype=float)

    if tsi_val is not None:
        if tsi_val > 0.65:
            # 상승 편향: 모든 봉 상승
            for i in range(1, n):
                closes[i] = closes[i - 1] + 0.5
        elif tsi_val < 0.35:
            # 하락 편향: 모든 봉 하락
            for i in range(1, n):
                closes[i] = closes[i - 1] - 0.5
        # else: 기본값 유지 (HOLD)

    if close_vs_ema == "above":
        ema50_val = closes[-2] - 5.0
    else:
        ema50_val = closes[-2] + 5.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, ema50_val),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _compute_tsi(df):
    """TSI bull 값 계산 (검증용)."""
    idx = len(df) - 2
    dm = df["close"].diff()
    pos_dm = dm.clip(lower=0)
    neg_dm = (-dm).clip(lower=0)
    pos_sum = pos_dm.rolling(10).sum()
    neg_sum = neg_dm.rolling(10).sum()
    total = pos_sum + neg_sum
    tsi = pos_sum / total.replace(0, float("nan"))
    return float(tsi.iloc[idx])


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "trend_strength"


# ── 2. BUY 신호 (tsi_bull > 0.65 AND close > EMA50) ─────────────────────
def test_buy_signal():
    df = _make_df(tsi_val=0.8, close_vs_ema="above")
    tsi = _compute_tsi(df)
    assert tsi > 0.65, f"tsi={tsi:.3f} > 0.65 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (tsi_bull < 0.35 AND close < EMA50) ────────────────────
def test_sell_signal():
    df = _make_df(tsi_val=0.1, close_vs_ema="below")
    tsi = _compute_tsi(df)
    assert tsi < 0.35, f"tsi={tsi:.3f} < 0.35 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (tsi_bull > 0.75) ─────────────────────────────
def test_buy_high_confidence():
    df = _make_df(tsi_val=0.9, close_vs_ema="above")
    tsi = _compute_tsi(df)
    assert tsi > 0.75, f"tsi={tsi:.3f} > 0.75 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. SELL HIGH confidence (tsi_bull < 0.25) ────────────────────────────
def test_sell_high_confidence():
    df = _make_df(tsi_val=0.05, close_vs_ema="below")
    tsi = _compute_tsi(df)
    assert tsi < 0.25, f"tsi={tsi:.3f} < 0.25 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 6. HOLD (tsi_bull 범위 내, 중립) ─────────────────────────────────────
def test_hold_neutral():
    # 가격 변화 없음 → tsi NaN or 0.5 근방
    df = _make_df(tsi_val=None, close_vs_ema="above")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. BUY 조건 충족 but close < EMA50 → HOLD ────────────────────────────
def test_buy_condition_but_below_ema50():
    df = _make_df(tsi_val=0.8, close_vs_ema="below")
    tsi = _compute_tsi(df)
    # TSI > 0.65 지만 close < ema50 → HOLD
    if tsi > 0.65:
        sig = strategy.generate(df)
        assert sig.action != Action.BUY


# ── 8. SELL 조건 충족 but close > EMA50 → HOLD ───────────────────────────
def test_sell_condition_but_above_ema50():
    df = _make_df(tsi_val=0.1, close_vs_ema="above")
    tsi = _compute_tsi(df)
    if tsi < 0.35:
        sig = strategy.generate(df)
        assert sig.action != Action.SELL


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
    assert sig.strategy == "trend_strength"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "TSI" 포함 ──────────────────────────────────────
def test_buy_reasoning_contains_tsi():
    df = _make_df(tsi_val=0.8, close_vs_ema="above")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "TSI" in sig.reasoning


# ── 13. SELL reasoning에 "TSI" 포함 ─────────────────────────────────────
def test_sell_reasoning_contains_tsi():
    df = _make_df(tsi_val=0.05, close_vs_ema="below")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "TSI" in sig.reasoning


# ── 14. entry_price == close[-2] ─────────────────────────────────────────
def test_entry_price_equals_close():
    df = _make_df(tsi_val=0.8, close_vs_ema="above")
    sig = strategy.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))
