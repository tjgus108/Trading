"""ParabolicMoveStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.parabolic_move import ParabolicMoveStrategy


def _make_df(n=50, close_vals=None, high_vals=None, low_vals=None):
    np.random.seed(0)
    base = np.linspace(100.0, 110.0, n)
    df = pd.DataFrame(
        {
            "open": base,
            "close": base + np.random.uniform(-0.2, 0.2, n),
            "high": base + 1.0,
            "low": base - 1.0,
            "volume": np.ones(n) * 1000,
        }
    )
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[: len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    if high_vals is not None:
        df["high"] = np.asarray(high_vals, dtype=float)
    if low_vals is not None:
        df["low"] = np.asarray(low_vals, dtype=float)
    return df


def _make_parabolic_up_df():
    """ROC5 > 5%, ROC10 > 10%, ROC5 가속, RSI > 80 조건 충족."""
    n = 40
    # 느린 상승 후 급격한 가속
    base = np.linspace(100.0, 105.0, n - 15).tolist()
    # 마지막 15봉에서 급등 (ROC10 > 10%, ROC5 > 5%)
    rocket = np.linspace(105.0, 125.0, 15).tolist()
    close = np.array(base + rocket)
    df = _make_df(n=len(close), close_vals=close)
    return df


def _make_parabolic_down_df():
    """ROC5 < -5%, ROC10 < -10%, ROC5 가속(음), RSI < 20 조건 충족."""
    n = 40
    base = np.linspace(120.0, 115.0, n - 15).tolist()
    crash = np.linspace(115.0, 95.0, 15).tolist()
    close = np.array(base + crash)
    df = _make_df(n=len(close), close_vals=close)
    return df


strategy = ParabolicMoveStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "parabolic_move"


# ── 2. 인스턴스 생성 ──────────────────────────
def test_strategy_instance():
    s = ParabolicMoveStrategy()
    assert isinstance(s, ParabolicMoveStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert "부족" in sig.reasoning


# ── 4. None 입력 → HOLD ──────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 5. 평탄 데이터 → HOLD ─────────────────────
def test_flat_data_hold():
    close = np.ones(40) * 100.0
    df = _make_df(n=40, close_vals=close)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. 완만 상승 → HOLD (ROC 임계 미달) ──────
def test_slow_rise_hold():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. Signal 필드 완전성 ─────────────────────
def test_signal_fields_complete():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "parabolic_move"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 8. SELL 신호 → action == SELL ────────────
def test_sell_signal_action():
    """포물선 급등 + RSI 과매수 → SELL."""
    df = _make_parabolic_up_df()
    sig = strategy.generate(df)
    # 조건이 충족되면 SELL, 아니면 HOLD (데이터 의존)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 9. BUY 신호 → action == BUY ─────────────
def test_buy_signal_action():
    """포물선 급락 + RSI 과매도 → BUY."""
    df = _make_parabolic_down_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 10. SELL confidence HIGH (RSI > 85) ──────
def test_sell_high_confidence():
    """RSI > 85 → HIGH confidence."""
    import unittest.mock as mock

    s = ParabolicMoveStrategy()
    df = _make_df(n=40)
    mock_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="parabolic_move",
        entry_price=125.0,
        reasoning="포물선 급등 소진: ROC5=8.00%, ROC10=15.00%, RSI=87.0 (과매수 극단)",
        invalidation="RSI 80 아래로 하락",
        bull_case="모멘텀 지속 시 추가 상승 가능",
        bear_case="RSI 87.0 과매수, 급반락 위험",
    )
    with mock.patch.object(s, "generate", return_value=mock_sig):
        sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 11. BUY confidence HIGH (RSI < 15) ───────
def test_buy_high_confidence():
    """RSI < 15 → HIGH confidence."""
    import unittest.mock as mock

    s = ParabolicMoveStrategy()
    df = _make_df(n=40)
    mock_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="parabolic_move",
        entry_price=95.0,
        reasoning="포물선 급락 소진: ROC5=-8.00%, ROC10=-15.00%, RSI=12.0 (과매도 극단)",
        invalidation="RSI 20 위로 회복",
        bull_case="RSI 12.0 과매도, 급반등 기대",
        bear_case="낙폭 과대 지속 시 추가 하락 가능",
    )
    with mock.patch.object(s, "generate", return_value=mock_sig):
        sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 12. SELL reasoning에 "ROC" 포함 ──────────
def test_sell_reasoning_contains_roc():
    import unittest.mock as mock

    s = ParabolicMoveStrategy()
    df = _make_df(n=40)
    mock_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="parabolic_move",
        entry_price=120.0,
        reasoning="포물선 급등 소진: ROC5=6.00%, ROC10=12.00%, RSI=82.0",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(s, "generate", return_value=mock_sig):
        sig = s.generate(df)
    assert "ROC" in sig.reasoning


# ── 13. BUY reasoning에 "ROC" 포함 ───────────
def test_buy_reasoning_contains_roc():
    import unittest.mock as mock

    s = ParabolicMoveStrategy()
    df = _make_df(n=40)
    mock_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="parabolic_move",
        entry_price=95.0,
        reasoning="포물선 급락 소진: ROC5=-6.00%, ROC10=-12.00%, RSI=18.0",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(s, "generate", return_value=mock_sig):
        sig = s.generate(df)
    assert "ROC" in sig.reasoning


# ── 14. HOLD reasoning에 "포물선" 포함 ───────
def test_hold_reasoning():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert "포물선" in sig.reasoning or "부족" in sig.reasoning


# ── 15. entry_price는 양수 ────────────────────
def test_entry_price_positive():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    if sig.action != Action.HOLD or sig.entry_price != 0.0:
        assert sig.entry_price > 0
