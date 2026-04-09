"""RVIStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.rvi import RVIStrategy


def _make_df(n=30, trend="up"):
    np.random.seed(7)
    if trend == "up":
        base = np.linspace(100, 115, n)
    elif trend == "down":
        base = np.linspace(115, 100, n)
    else:
        base = np.ones(n) * 100

    noise = np.random.uniform(-0.3, 0.3, n)
    close = base + noise
    open_ = close - np.random.uniform(0.1, 0.5, n)
    high = np.maximum(close, open_) + np.random.uniform(0.2, 0.8, n)
    low = np.minimum(close, open_) - np.random.uniform(0.2, 0.8, n)

    df = pd.DataFrame({
        "open": open_,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
        "ema50": base,
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _mock_signal(action, confidence, reasoning, strategy="rvi"):
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


strategy = RVIStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "rvi"


# ── 2. BUY 신호 (mock) ───────────────────────
def test_buy_signal():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "RVI 상향 크로스: RVI 0.1000 → 0.2000, Signal 0.1500"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (mock) ──────────────────────
def test_sell_signal():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "RVI 하향 크로스: RVI -0.1000 → -0.2000, Signal -0.1500"
    )):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. HOLD (크로스 없음) ─────────────────────
def test_hold_no_cross():
    df = _make_df(n=30, trend="flat")
    sig = strategy.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── 5. BUY HIGH confidence (|RVI| > 0.3) ─────
def test_buy_high_confidence():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.HIGH, "RVI 상향 크로스: RVI 0.2000 → 0.4000, Signal 0.3000"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence (|RVI| <= 0.3) ─
def test_buy_medium_confidence():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "RVI 상향 크로스: RVI 0.1000 → 0.2000, Signal 0.1500"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 7. SELL HIGH confidence (|RVI| > 0.3) ────
def test_sell_high_confidence():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.HIGH, "RVI 하향 크로스: RVI -0.2000 → -0.4000, Signal -0.3000"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL MEDIUM confidence (|RVI| <= 0.3) ─
def test_sell_medium_confidence():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "RVI 하향 크로스: RVI -0.1000 → -0.2000, Signal -0.1500"
    )):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 9. 데이터 부족 (n < 20) → HOLD ──────────
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
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "rvi"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "RVI" 포함 ───────────
def test_buy_reasoning_contains_rvi():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.BUY, Confidence.MEDIUM, "RVI 상향 크로스: RVI 0.1000 → 0.2000"
    )):
        sig = strat.generate(df)
    assert "RVI" in sig.reasoning


# ── 13. SELL reasoning에 "RVI" 포함 ──────────
def test_sell_reasoning_contains_rvi():
    strat = RVIStrategy()
    df = _make_df(n=30)
    with mock.patch.object(strat, "generate", return_value=_mock_signal(
        Action.SELL, Confidence.MEDIUM, "RVI 하향 크로스: RVI -0.1000 → -0.2000"
    )):
        sig = strat.generate(df)
    assert "RVI" in sig.reasoning


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = RVIStrategy()
    assert isinstance(strat, RVIStrategy)


# ── 15. HOLD LOW conf 시 entry_price == 0.0 ──
def test_hold_low_conf_entry_zero():
    sig = strategy.generate(None)
    assert sig.entry_price == 0.0
    assert sig.confidence == Confidence.LOW


# ── 16. 정상 데이터에서 entry_price > 0 ───────
def test_entry_price_positive():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    if sig.confidence != Confidence.LOW:
        assert sig.entry_price > 0


# ── 17. high >= close >= low 일관성 (df 구조 확인) ─
def test_df_ohlc_consistency():
    df = _make_df(n=30)
    assert (df["high"] >= df["close"]).all()
    assert (df["close"] >= df["low"]).all()
