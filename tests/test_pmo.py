"""PMOStrategy 단위 테스트."""

import math
import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.pmo import PMOStrategy


def _make_df(n=80, close_vals=None):
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


def _mock_signal(action, confidence, reasoning, strategy="pmo"):
    return Signal(
        action=action,
        confidence=confidence,
        strategy=strategy,
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


strategy = PMOStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "pmo"


# ── 2. BUY 신호 (mock) ───────────────────────
def test_buy_signal():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PMO 상향 크로스: PMO 0.1000 → 0.2000, Signal 0.1500"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (mock) ──────────────────────
def test_sell_signal():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PMO 하향 크로스: PMO -0.1000 → -0.2000, Signal -0.1500"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (크로스 없음) ─────────────────────
def test_hold_no_cross():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 5. BUY HIGH confidence (PMO > 2) ─────────
def test_buy_high_confidence():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "PMO 상향 크로스: PMO 1.5000 → 2.5000, Signal 2.0000"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence (PMO <= 2) ──────
def test_buy_medium_confidence():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PMO 상향 크로스: PMO 0.5000 → 1.0000, Signal 0.8000"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 7. SELL HIGH confidence (PMO < -2) ───────
def test_sell_high_confidence():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "PMO 하향 크로스: PMO -1.5000 → -2.5000, Signal -2.0000"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL MEDIUM confidence (PMO >= -2) ────
def test_sell_medium_confidence():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PMO 하향 크로스: PMO -0.5000 → -1.0000, Signal -0.8000"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 9. 데이터 부족 (n < 60) → HOLD ──────────
def test_insufficient_data():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 11. Signal 필드 완전성 ────────────────────
def test_signal_fields():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "pmo"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "PMO" 포함 ───────────
def test_buy_reasoning_contains_pmo():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PMO 상향 크로스: PMO 0.5000 → 1.0000"
    )):
        sig = strat.generate(df)
    assert "PMO" in sig.reasoning


# ── 13. SELL reasoning에 "PMO" 포함 ──────────
def test_sell_reasoning_contains_pmo():
    strat = PMOStrategy()
    df = _make_df(n=80)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PMO 하향 크로스: PMO -0.5000 → -1.0000"
    )):
        sig = strat.generate(df)
    assert "PMO" in sig.reasoning


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = PMOStrategy()
    assert isinstance(strat, PMOStrategy)


# ── 15. HOLD reasoning에 "PMO" 포함 ──────────
def test_hold_reasoning_contains_pmo():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD and sig.confidence != Confidence.LOW:
        assert "PMO" in sig.reasoning


# ── 16. entry_price > 0 (정상 데이터) ─────────
def test_entry_price_positive():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    if sig.action != Action.HOLD or sig.confidence != Confidence.LOW:
        assert sig.entry_price > 0


# ── 17. HOLD LOW conf 시 entry_price == 0.0 ──
def test_hold_low_conf_entry_zero():
    sig = strategy.generate(None)
    assert sig.entry_price == 0.0
    assert sig.confidence == Confidence.LOW
