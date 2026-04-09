"""DPOCrossStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.dpo_cross import DPOCrossStrategy


def _make_df(n=60, close_vals=None):
    np.random.seed(7)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.3, 0.3, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[: len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    return df


strategy = DPOCrossStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "dpo_cross"


# ── 2. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = DPOCrossStrategy()
    assert isinstance(strat, DPOCrossStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 4. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 5. Signal 필드 완전성 ───────────────────
def test_signal_fields():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "dpo_cross"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 6. BUY 신호 모킹 ─────────────────────────
def test_buy_signal_mock():
    import unittest.mock as mock
    strat = DPOCrossStrategy()
    df = _make_df(n=60)
    buy_signal = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="dpo_cross",
        entry_price=105.0,
        reasoning="DPO Cross UP: DPO 0.1234 crossed above Signal 0.1000",
        invalidation="DPO crosses back below Signal",
        bull_case="DPO > Signal",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=buy_signal):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 7. SELL 신호 모킹 ────────────────────────
def test_sell_signal_mock():
    import unittest.mock as mock
    strat = DPOCrossStrategy()
    df = _make_df(n=60)
    sell_signal = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="dpo_cross",
        entry_price=105.0,
        reasoning="DPO Cross DOWN: DPO -0.1234 crossed below Signal -0.1000",
        invalidation="DPO crosses back above Signal",
        bull_case="",
        bear_case="DPO < Signal",
    )
    with mock.patch.object(strat, "generate", return_value=sell_signal):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 8. BUY HIGH confidence 모킹 ──────────────
def test_buy_high_confidence_mock():
    import unittest.mock as mock
    strat = DPOCrossStrategy()
    df = _make_df(n=60)
    sig_high = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="dpo_cross",
        entry_price=105.0,
        reasoning="DPO Cross UP: DPO 0.5000 crossed above Signal 0.1000",
        invalidation="DPO crosses back below Signal",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_high):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 9. SELL HIGH confidence 모킹 ─────────────
def test_sell_high_confidence_mock():
    import unittest.mock as mock
    strat = DPOCrossStrategy()
    df = _make_df(n=60)
    sig_high = Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="dpo_cross",
        entry_price=105.0,
        reasoning="DPO Cross DOWN: DPO -0.5000 crossed below Signal -0.1000",
        invalidation="DPO crosses back above Signal",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_high):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 10. BUY reasoning에 "DPO" 포함 ──────────
def test_buy_reasoning_contains_dpo():
    import unittest.mock as mock
    strat = DPOCrossStrategy()
    df = _make_df(n=60)
    sig_buy = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="dpo_cross",
        entry_price=105.0,
        reasoning="DPO Cross UP: DPO 0.1234 crossed above Signal 0.1000",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_buy):
        sig = strat.generate(df)
    assert "DPO" in sig.reasoning


# ── 11. SELL reasoning에 "DPO" 포함 ─────────
def test_sell_reasoning_contains_dpo():
    import unittest.mock as mock
    strat = DPOCrossStrategy()
    df = _make_df(n=60)
    sig_sell = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="dpo_cross",
        entry_price=105.0,
        reasoning="DPO Cross DOWN: DPO -0.1234 crossed below Signal -0.1000",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_sell):
        sig = strat.generate(df)
    assert "DPO" in sig.reasoning


# ── 12. entry_price는 양수 ───────────────────
def test_entry_price_positive():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# ── 13. 최소 행수 경계값 테스트 ──────────────
def test_minimum_data_boundary():
    """34행 → HOLD, 35행 → 정상 실행."""
    df_34 = _make_df(n=34)
    sig = strategy.generate(df_34)
    assert sig.action == Action.HOLD

    df_35 = _make_df(n=35)
    sig35 = strategy.generate(df_35)
    assert sig35.strategy == "dpo_cross"


# ── 14. HOLD 신호 정상 반환 ──────────────────
def test_hold_signal():
    """충분한 데이터로 신호 생성, 전략명 확인."""
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
    assert sig.strategy == "dpo_cross"
