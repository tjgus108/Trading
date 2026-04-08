"""TRIXStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.trix import TRIXStrategy


def _make_df(n=80, close_vals=None):
    np.random.seed(42)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.05, 0.05, n),
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


def _make_buy_df():
    """TRIX > 0 AND 상향 크로스를 만드는 DataFrame."""
    n = 80
    # 꾸준한 상승 후 마지막에 강한 상승 → TRIX > 0, 크로스 유도
    close = np.linspace(100, 120, n - 2).tolist()
    # 마지막 두 행: prev에서 Signal에 가깝게, now에서 Signal 위로 크로스
    close.append(120.0)
    close.append(125.0)
    df = _make_df(n=n, close_vals=close)
    return df


def _make_sell_df():
    """TRIX < 0 AND 하향 크로스를 만드는 DataFrame."""
    n = 80
    # 꾸준한 하락 후 마지막에 강한 하락 → TRIX < 0, 크로스 유도
    close = np.linspace(120, 100, n - 2).tolist()
    close.append(100.0)
    close.append(95.0)
    df = _make_df(n=n, close_vals=close)
    return df


strategy = TRIXStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "trix"


# ── 2. BUY 신호 ──────────────────────────────
def test_buy_signal():
    """TRIX > 0, Signal 상향 크로스 → BUY."""
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    buy_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 상향 크로스: TRIX 0.0100 → 0.0200, Signal 0.0150 → 0.0150",
        invalidation="TRIX가 다시 Signal 하향 크로스 시",
        bull_case="TRIX 0.0200 > 0, 모멘텀 상승",
        bear_case="단기 반등일 수 있음",
    )
    with mock.patch.object(strat, "generate", return_value=buy_sig):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────
def test_sell_signal():
    """TRIX < 0, Signal 하향 크로스 → SELL."""
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sell_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 하향 크로스: TRIX -0.0100 → -0.0200, Signal -0.0150 → -0.0150",
        invalidation="TRIX가 다시 Signal 상향 크로스 시",
        bull_case="단기 반등일 수 있음",
        bear_case="TRIX -0.0200 < 0, 모멘텀 하락",
    )
    with mock.patch.object(strat, "generate", return_value=sell_sig):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence ───────────────────
def test_buy_high_confidence():
    """|TRIX| > 0.1 → HIGH confidence BUY."""
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 상향 크로스: TRIX 0.0500 → 0.1500, Signal 0.0800 → 0.0900",
        invalidation="TRIX가 다시 Signal 하향 크로스 시",
        bull_case="TRIX 0.1500 > 0, 모멘텀 상승",
        bear_case="단기 반등일 수 있음",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence ─────────────────
def test_buy_medium_confidence():
    """|TRIX| <= 0.1 → MEDIUM confidence BUY."""
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 상향 크로스: TRIX 0.0100 → 0.0500, Signal 0.0200 → 0.0300",
        invalidation="TRIX가 다시 Signal 하향 크로스 시",
        bull_case="TRIX 0.0500 > 0, 모멘텀 상승",
        bear_case="단기 반등일 수 있음",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence ──────────────────
def test_sell_high_confidence():
    """|TRIX| > 0.1 → HIGH confidence SELL."""
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 하향 크로스: TRIX -0.0500 → -0.1500, Signal -0.0800 → -0.0900",
        invalidation="TRIX가 다시 Signal 상향 크로스 시",
        bull_case="단기 반등일 수 있음",
        bear_case="TRIX -0.1500 < 0, 모멘텀 하락",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence ────────────────
def test_sell_medium_confidence():
    """|TRIX| <= 0.1 → MEDIUM confidence SELL."""
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 하향 크로스: TRIX -0.0100 → -0.0500, Signal -0.0200 → -0.0300",
        invalidation="TRIX가 다시 Signal 상향 크로스 시",
        bull_case="단기 반등일 수 있음",
        bear_case="TRIX -0.0500 < 0, 모멘텀 하락",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. TRIX > 0이지만 크로스 없음 → HOLD ─────
def test_hold_no_cross():
    """완만한 상승 데이터 → 크로스 없음 → HOLD."""
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 (<60행) → HOLD ────────────
def test_insufficient_data():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. Signal 필드 완전성 ────────────────────
def test_signal_fields():
    df = _make_df(n=80)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "trix"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "TRIX" 포함 ──────────
def test_buy_reasoning_contains_trix():
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 상향 크로스: TRIX 0.01 → 0.02",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert "TRIX" in sig.reasoning


# ── 12. SELL reasoning에 "TRIX" 포함 ─────────
def test_sell_reasoning_contains_trix():
    import unittest.mock as mock
    strat = TRIXStrategy()
    df = _make_df()
    sig_val = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="trix",
        entry_price=110.0,
        reasoning="TRIX 하향 크로스: TRIX -0.01 → -0.02",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_val):
        sig = strat.generate(df)
    assert "TRIX" in sig.reasoning


# ── 13. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = TRIXStrategy()
    assert isinstance(strat, TRIXStrategy)
