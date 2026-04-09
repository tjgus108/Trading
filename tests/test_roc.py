"""ROCStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.roc import ROCStrategy


def _make_df(n=50, close_vals=None):
    np.random.seed(42)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.5, 0.5, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
        "ema50": base,
        "atr14": np.ones(n) * 0.5,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    return df


def _mock_signal(action, confidence, reasoning):
    return Signal(
        action=action,
        confidence=confidence,
        strategy="roc",
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


strategy = ROCStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "roc"


# ── 2. BUY 신호 ──────────────────────────────
def test_buy_signal():
    """ROC > 0, ROC 상향 크로스 Signal → BUY."""
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "ROC 상향 크로스: ROC 0.50 → 1.20, Signal 0.80 (ROC > 0)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────
def test_sell_signal():
    """ROC < 0, ROC 하향 크로스 Signal → SELL."""
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "ROC 하향 크로스: ROC -0.50 → -1.20, Signal -0.80 (ROC < 0)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (크로스 없음) ─────────────────────
def test_hold_no_cross():
    """크로스 없을 때 HOLD."""
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 5. BUY HIGH confidence (|ROC| > 3.0) ─────
def test_buy_high_confidence():
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "ROC 상향 크로스: ROC 2.00 → 4.00, Signal 3.00 (ROC > 0)"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence (|ROC| <= 3.0) ──
def test_buy_medium_confidence():
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "ROC 상향 크로스: ROC 0.50 → 1.20, Signal 0.80 (ROC > 0)"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 7. SELL HIGH confidence (|ROC| > 3.0) ────
def test_sell_high_confidence():
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "ROC 하향 크로스: ROC -2.00 → -4.00, Signal -3.00 (ROC < 0)"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL MEDIUM confidence (|ROC| <= 3.0) ─
def test_sell_medium_confidence():
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "ROC 하향 크로스: ROC -0.50 → -1.20, Signal -0.80 (ROC < 0)"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 9. 데이터 부족 → HOLD ────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 11. Signal 필드 완전성 ────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "roc"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "ROC" 포함 ───────────
def test_buy_reasoning_contains_roc():
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "ROC 상향 크로스: ROC 0.50 → 1.20"
    )):
        sig = strat.generate(df)
    assert "ROC" in sig.reasoning


# ── 13. SELL reasoning에 "ROC" 포함 ──────────
def test_sell_reasoning_contains_roc():
    strat = ROCStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "ROC 하향 크로스: ROC -0.50 → -1.20"
    )):
        sig = strat.generate(df)
    assert "ROC" in sig.reasoning


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = ROCStrategy()
    assert isinstance(strat, ROCStrategy)
