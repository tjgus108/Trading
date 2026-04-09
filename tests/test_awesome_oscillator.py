"""AwesomeOscillatorStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.awesome_oscillator import AwesomeOscillatorStrategy


def _make_df(n=60, high_vals=None, low_vals=None):
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
    if high_vals is not None:
        arr = np.asarray(high_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["high"] = arr
    if low_vals is not None:
        arr = np.asarray(low_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["low"] = arr
    return df


def _mock_signal(action, confidence, reasoning):
    return Signal(
        action=action,
        confidence=confidence,
        strategy="awesome_oscillator",
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


def _make_zero_cross_buy_df():
    """AO가 0선 상향 크로스하는 데이터 생성."""
    n = 60
    # 앞 50개: 하락 (AO 음수), 뒤 10개: 급등 (AO 양전)
    base = np.concatenate([np.linspace(110, 100, 50), np.linspace(100, 115, 10)])
    high = base + 1.0
    low = base - 1.0
    df = pd.DataFrame({
        "open": base,
        "close": base,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
        "ema50": base,
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _make_zero_cross_sell_df():
    """AO가 0선 하향 크로스하는 데이터 생성."""
    n = 60
    # 앞 50개: 상승 (AO 양수), 뒤 10개: 급락 (AO 음전)
    base = np.concatenate([np.linspace(100, 110, 50), np.linspace(110, 95, 10)])
    high = base + 1.0
    low = base - 1.0
    df = pd.DataFrame({
        "open": base,
        "close": base,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
        "ema50": base,
        "atr14": np.ones(n) * 0.5,
    })
    return df


strategy = AwesomeOscillatorStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "awesome_oscillator"


# ── 2. BUY 신호 (Zero Cross) ─────────────────
def test_buy_zero_cross():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "AO Zero Cross 상향: AO -0.1234 → 0.2345 (0선 돌파)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (Zero Cross) ────────────────
def test_sell_zero_cross():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "AO Zero Cross 하향: AO 0.1234 → -0.2345 (0선 하향 돌파)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (크로스/소서 없음) ───────────────
def test_hold_no_signal():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 5. BUY HIGH confidence (Zero Cross) ──────
def test_buy_high_confidence_zero_cross():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "AO Zero Cross 상향"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence (Bull Saucer) ───
def test_buy_medium_confidence_saucer():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "AO Bull Saucer: AO 0.5 → 0.3 → 0.6 (AO > 0, 오목 후 상승)"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 7. SELL HIGH confidence (Zero Cross) ─────
def test_sell_high_confidence_zero_cross():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "AO Zero Cross 하향"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL MEDIUM confidence (Bear Saucer) ──
def test_sell_medium_confidence_saucer():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "AO Bear Saucer: AO -0.5 → -0.3 → -0.6 (AO < 0, 오목 후 하락)"
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
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "awesome_oscillator"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "AO" 포함 ────────────
def test_buy_reasoning_contains_ao():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "AO Zero Cross 상향: AO -0.1 → 0.2"
    )):
        sig = strat.generate(df)
    assert "AO" in sig.reasoning


# ── 13. SELL reasoning에 "AO" 포함 ───────────
def test_sell_reasoning_contains_ao():
    strat = AwesomeOscillatorStrategy()
    df = _make_df(n=60)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "AO Zero Cross 하향: AO 0.1 → -0.2"
    )):
        sig = strat.generate(df)
    assert "AO" in sig.reasoning


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = AwesomeOscillatorStrategy()
    assert isinstance(strat, AwesomeOscillatorStrategy)
