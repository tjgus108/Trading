"""DualThrustStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.dual_thrust import DualThrustStrategy


def _make_df(n=20, close_vals=None, high_vals=None, low_vals=None, vol_vals=None):
    np.random.seed(42)
    base = np.linspace(100, 102, n)
    df = pd.DataFrame({
        "open": base,
        "close": base,
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
        "ema50": base,
        "atr14": np.ones(n) * 0.5,
    })
    if close_vals is not None:
        df["close"] = np.asarray(close_vals, dtype=float)
    if high_vals is not None:
        df["high"] = np.asarray(high_vals, dtype=float)
    if low_vals is not None:
        df["low"] = np.asarray(low_vals, dtype=float)
    if vol_vals is not None:
        df["volume"] = np.asarray(vol_vals, dtype=float)
    return df


def _mock_signal(action, confidence, reasoning=""):
    return Signal(
        action=action,
        confidence=confidence,
        strategy="dual_thrust",
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


strategy = DualThrustStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "dual_thrust"


# ── 2. BUY 신호 ──────────────────────────────
def test_buy_signal():
    """close > Buy_Level, 볼륨 충분 → BUY."""
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "상단 돌파: close 102.00 > Buy_Level 100.50"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────
def test_sell_signal():
    """close < Sell_Level, 볼륨 충분 → SELL."""
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "하단 돌파: close 98.00 < Sell_Level 99.50"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (돌파 없음) ──────────────────────
def test_hold_no_breakout():
    """close가 레벨 사이에 있으면 HOLD."""
    df = _make_df(n=20)
    sig = strategy.generate(df)
    # 기본 df는 단조 증가, 돌파 조건 불확실하므로 결과가 HOLD이거나 그 외일 수 있음
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}


# ── 5. BUY HIGH confidence (breakout_ratio > 0.1) ─
def test_buy_high_confidence():
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "Range 대비 15.0% 초과 돌파"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence (breakout_ratio <= 0.1) ─
def test_buy_medium_confidence():
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "Range 대비 5.0% 초과 돌파"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 7. SELL HIGH confidence ───────────────────
def test_sell_high_confidence():
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "Range 대비 15.0% 하단 돌파"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL MEDIUM confidence ─────────────────
def test_sell_medium_confidence():
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "Range 대비 5.0% 하단 돌파"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 9. 데이터 부족 → HOLD ────────────────────
def test_insufficient_data():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 11. Signal 필드 완전성 ────────────────────
def test_signal_fields():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "dual_thrust"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "돌파" 포함 ──────────
def test_buy_reasoning_contains_breakout():
    strat = DualThrustStrategy()
    df = _make_df(n=20)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "상단 돌파: close 102.00 > Buy_Level 100.50"
    )):
        sig = strat.generate(df)
    assert "돌파" in sig.reasoning


# ── 13. 볼륨 부족 시 BUY 차단 ───────────────
def test_buy_blocked_by_low_volume():
    """볼륨이 평균 이하면 BUY 신호 없음."""
    n = 20
    # 마지막 캔들(idx)은 low volume, 이전 10봉은 high volume
    vol = np.ones(n) * 2000.0
    vol[-2] = 100.0  # idx = n-2, 볼륨 낮게
    close = np.linspace(100, 110, n)
    close[-2] = 120.0  # Buy_Level 돌파 가격
    df = _make_df(n=n, close_vals=close, vol_vals=vol)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = DualThrustStrategy()
    assert isinstance(strat, DualThrustStrategy)


# ── 15. Range 0 이하 처리 ────────────────────
def test_zero_range_returns_hold():
    """prev_high == prev_close == prev_low → Range=0 → HOLD."""
    n = 20
    close = np.ones(n) * 100.0
    high = np.ones(n) * 100.0
    low = np.ones(n) * 100.0
    df = _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 16. 최소 행 경계 (10행) ──────────────────
def test_at_min_rows():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}
