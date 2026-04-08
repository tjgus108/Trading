"""CCIStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.cci import CCIStrategy


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
        strategy="cci",
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


strategy = CCIStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "cci"


# ── 2. BUY 신호 ──────────────────────────────
def test_buy_signal():
    """CCI -100 상향 크로스 시 BUY."""
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "CCI 과매도 반등: CCI -150.0 → -50.0 (-100 상향 크로스)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────
def test_sell_signal():
    """CCI +100 하향 크로스 시 SELL."""
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "CCI 과매수 하락: CCI 150.0 → 50.0 (+100 하향 크로스)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence ───────────────────
def test_buy_high_confidence():
    """|CCI| > 200 → HIGH."""
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "CCI 과매도 반등: CCI -250.0 → 210.0 (-100 상향 크로스)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence ─────────────────
def test_buy_medium_confidence():
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "CCI 과매도 반등: CCI -150.0 → -50.0 (-100 상향 크로스)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence ──────────────────
def test_sell_high_confidence():
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "CCI 과매수 하락: CCI 250.0 → -210.0 (+100 하향 크로스)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence ────────────────
def test_sell_medium_confidence():
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "CCI 과매수 하락: CCI 150.0 → 50.0 (+100 하향 크로스)"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. 중립 HOLD ─────────────────────────────
def test_hold_neutral():
    """완만한 데이터 → 크로스 없음 → HOLD."""
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. Signal 필드 완전성 ────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "cci"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "CCI" 포함 ───────────
def test_buy_reasoning_contains_cci():
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "CCI 과매도 반등: CCI -150.0 → -50.0"
    )):
        sig = strat.generate(df)
    assert "CCI" in sig.reasoning


# ── 12. SELL reasoning에 "CCI" 포함 ──────────
def test_sell_reasoning_contains_cci():
    strat = CCIStrategy()
    df = _make_df(n=50)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "CCI 과매수 하락: CCI 150.0 → 50.0"
    )):
        sig = strat.generate(df)
    assert "CCI" in sig.reasoning


# ── 13. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = CCIStrategy()
    assert isinstance(strat, CCIStrategy)
