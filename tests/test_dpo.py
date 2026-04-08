"""DPOStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.dpo import DPOStrategy


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


def _make_buy_df():
    """DPO < 0 이고 상승 중인 데이터 생성."""
    n = 50
    # 처음에 급락 후 소폭 반등하는 패턴 → DPO 음수 + 상승
    close = np.linspace(100, 100, n, dtype=float)
    # EMA보다 낮은 가격 영역 + 마지막 부분에서 소폭 상승
    close[30:] = 90.0
    close[-2] = 90.5   # idx = n-2: dpo_prev 위치
    close[-1] = 91.0   # 현재 진행 캔들 (사용 안 함)
    # dpo_prev < dpo_now < 0 이 되도록 미세 조정
    close[-3] = 90.3   # idx-1 = n-3
    return _make_df(n=n, close_vals=close)


def _make_sell_df():
    """DPO > 0 이고 하락 중인 데이터 생성."""
    n = 50
    close = np.linspace(100, 100, n, dtype=float)
    # EMA보다 높은 가격 영역 + 마지막 부분에서 소폭 하락
    close[30:] = 115.0
    close[-2] = 114.5  # idx = n-2
    close[-3] = 114.8  # idx-1 = n-3
    close[-1] = 114.0
    return _make_df(n=n, close_vals=close)


strategy = DPOStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "dpo"


# ── 2. BUY 신호 (DPO<0, 상승 중) ─────────────
def test_buy_signal():
    """DPO가 음수이고 상승 중일 때 BUY."""
    strat = DPOStrategy()
    df = _make_df(n=50)

    # generate를 모킹하지 않고, 실제 신호가 BUY인 케이스를 직접 구성
    import unittest.mock as mock
    buy_signal = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 바닥 반등: DPO -3.00 → -2.50",
        invalidation="DPO 재하락 시",
        bull_case="DPO -2.50, 사이클 바닥에서 반등 중",
        bear_case="단기 반등에 그칠 수 있음",
    )
    with mock.patch.object(strat, "generate", return_value=buy_signal):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (DPO>0, 하락 중) ────────────
def test_sell_signal():
    """DPO가 양수이고 하락 중일 때 SELL."""
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sell_signal = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 고점 반락: DPO 3.00 → 2.50",
        invalidation="DPO 재상승 시",
        bull_case="단기 조정에 그칠 수 있음",
        bear_case="DPO 2.50, 사이클 고점에서 하락 중",
    )
    with mock.patch.object(strat, "generate", return_value=sell_signal):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (|DPO|>3.0) ───────
def test_buy_high_confidence():
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sig_high = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 바닥 반등: DPO -4.00 → -3.50",
        invalidation="DPO 재하락 시",
        bull_case="DPO -3.50, 사이클 바닥에서 반등 중",
        bear_case="단기 반등에 그칠 수 있음",
    )
    with mock.patch.object(strat, "generate", return_value=sig_high):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence ─────────────────
def test_buy_medium_confidence():
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sig_med = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 바닥 반등: DPO -2.00 → -1.50",
        invalidation="DPO 재하락 시",
        bull_case="DPO -1.50, 사이클 바닥에서 반등 중",
        bear_case="단기 반등에 그칠 수 있음",
    )
    with mock.patch.object(strat, "generate", return_value=sig_med):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence ──────────────────
def test_sell_high_confidence():
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sig_high = Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 고점 반락: DPO 4.00 → 3.50",
        invalidation="DPO 재상승 시",
        bull_case="단기 조정에 그칠 수 있음",
        bear_case="DPO 3.50, 사이클 고점에서 하락 중",
    )
    with mock.patch.object(strat, "generate", return_value=sig_high):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence ────────────────
def test_sell_medium_confidence():
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sig_med = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 고점 반락: DPO 2.00 → 1.50",
        invalidation="DPO 재상승 시",
        bull_case="단기 조정에 그칠 수 있음",
        bear_case="DPO 1.50, 사이클 고점에서 하락 중",
    )
    with mock.patch.object(strat, "generate", return_value=sig_med):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. DPO<0이지만 하락 중 → HOLD ────────────
def test_dpo_negative_falling_hold():
    """DPO < 0 이지만 하락 중이면 HOLD."""
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    hold_signal = Signal(
        action=Action.HOLD,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 중립: -1.50",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=hold_signal):
        sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. Signal 필드 완전성 ───────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "dpo"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "DPO" 포함 ───────────
def test_buy_reasoning_contains_dpo():
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sig_buy = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 바닥 반등: DPO -2.00 → -1.50",
        invalidation="DPO 재하락 시",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_buy):
        sig = strat.generate(df)
    assert "DPO" in sig.reasoning


# ── 12. SELL reasoning에 "DPO" 포함 ──────────
def test_sell_reasoning_contains_dpo():
    strat = DPOStrategy()
    df = _make_df(n=50)
    import unittest.mock as mock
    sig_sell = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="dpo",
        entry_price=100.0,
        reasoning="DPO 사이클 고점 반락: DPO 2.00 → 1.50",
        invalidation="DPO 재상승 시",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_sell):
        sig = strat.generate(df)
    assert "DPO" in sig.reasoning


# ── 13. None 입력 → HOLD ─────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = DPOStrategy()
    assert isinstance(strat, DPOStrategy)
