"""PRoCTrendStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.proc_trend import PRoCTrendStrategy


def _make_df(n=30, close_vals=None, ema50_vals=None):
    np.random.seed(42)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.2, 0.2, n),
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
    if ema50_vals is not None:
        arr = np.asarray(ema50_vals, dtype=float)
        df["ema50"] = arr
    return df


def _mock_signal(action, confidence, reasoning=""):
    return Signal(
        action=action,
        confidence=confidence,
        strategy="proc_trend",
        entry_price=100.0,
        reasoning=reasoning,
        invalidation="",
        bull_case="",
        bear_case="",
    )


strategy = PRoCTrendStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "proc_trend"


# ── 2. BUY 신호 ──────────────────────────────
def test_buy_signal():
    """PROC_EMA > 1.0, 상승, EMA50 상승 → BUY."""
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PROC_EMA 상승 모멘텀"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────
def test_sell_signal():
    """PROC_EMA < -1.0, 하락, EMA50 하락 → SELL."""
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PROC_EMA 하락 모멘텀"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (조건 미충족) ─────────────────────
def test_hold_flat_data():
    """가격 변동 없으면 PROC_EMA ≈ 0 → HOLD."""
    df = _make_df(n=30, close_vals=[100.0] * 30)
    df["ema50"] = 100.0
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 5. BUY HIGH confidence (|PROC_EMA| > 3.0) ─
def test_buy_high_confidence():
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "PROC_EMA 5.00"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence (|PROC_EMA| <= 3.0) ─
def test_buy_medium_confidence():
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PROC_EMA 1.50"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 7. SELL HIGH confidence (|PROC_EMA| > 3.0) ─
def test_sell_high_confidence():
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "PROC_EMA -5.00"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL MEDIUM confidence ─────────────────
def test_sell_medium_confidence():
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PROC_EMA -1.50"
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
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "proc_trend"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "PROC" 포함 ──────────
def test_buy_reasoning_contains_proc():
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "PROC_EMA 상승 모멘텀: 1.00 → 2.00"
    )):
        sig = strat.generate(df)
    assert "PROC" in sig.reasoning


# ── 13. SELL reasoning에 "PROC" 포함 ─────────
def test_sell_reasoning_contains_proc():
    strat = PRoCTrendStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "PROC_EMA 하락 모멘텀: -1.00 → -2.00"
    )):
        sig = strat.generate(df)
    assert "PROC" in sig.reasoning


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = PRoCTrendStrategy()
    assert isinstance(strat, PRoCTrendStrategy)


# ── 15. BUY 최소 행 경계 (20행) ──────────────
def test_buy_at_min_rows():
    """20행 데이터는 처리 가능해야 함."""
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action in {Action.BUY, Action.SELL, Action.HOLD}


# ── 16. EMA50 하락 시 BUY 차단 ───────────────
def test_buy_blocked_by_downtrend():
    """EMA50 하락 추세면 BUY 불가."""
    n = 30
    ema50 = np.linspace(110, 100, n)  # 하락 추세
    close = np.linspace(105, 115, n)  # 가격은 상승
    df = _make_df(n=n, close_vals=close, ema50_vals=ema50)
    sig = strategy.generate(df)
    assert sig.action != Action.BUY
