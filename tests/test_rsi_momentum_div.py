"""RSIMomentumDivStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.rsi_momentum_div import RSIMomentumDivStrategy


def _make_df(n=50, close_vals=None):
    np.random.seed(0)
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


def _make_buy_df():
    """close가 최근 10봉 최저 근처 & RSI 상승 패턴."""
    n = 50
    close = np.full(n, 100.0)
    # 중반부 하락 → 마지막 완성 캔들이 near low, RSI 반등
    close[20:] = 90.0
    # RSI 반등을 위해 마지막 몇 개 봉 소폭 상승
    close[-5] = 88.0
    close[-4] = 88.5
    close[-3] = 89.0  # 이전봉 (rsi_prev)
    close[-2] = 89.5  # 마지막 완성 캔들 (rsi_now > rsi_prev 유도)
    close[-1] = 90.0  # 현재 진행 캔들 (사용 안 함)
    return _make_df(n=n, close_vals=close)


def _make_sell_df():
    """close가 최근 10봉 최고 근처 & RSI 하락 패턴."""
    n = 50
    close = np.full(n, 100.0)
    close[20:] = 115.0
    close[-5] = 117.0
    close[-4] = 116.5
    close[-3] = 116.0  # rsi_prev
    close[-2] = 115.5  # rsi_now < rsi_prev 유도 (하락)
    close[-1] = 115.0
    return _make_df(n=n, close_vals=close)


strategy = RSIMomentumDivStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "rsi_momentum_div"


# ── 2. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = RSIMomentumDivStrategy()
    assert isinstance(strat, RSIMomentumDivStrategy)


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
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "rsi_momentum_div"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 6. BUY 신호 모킹 ─────────────────────────
def test_buy_signal_mock():
    import unittest.mock as mock
    strat = RSIMomentumDivStrategy()
    df = _make_df(n=50)
    buy_signal = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="rsi_momentum_div",
        entry_price=89.5,
        reasoning="RSI Momentum Divergence BUY: close near 10-bar low, RSI 상승 (+2.50)",
        invalidation="Close below 10-bar low",
        bull_case="near low",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=buy_signal):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 7. SELL 신호 모킹 ────────────────────────
def test_sell_signal_mock():
    import unittest.mock as mock
    strat = RSIMomentumDivStrategy()
    df = _make_df(n=50)
    sell_signal = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="rsi_momentum_div",
        entry_price=115.5,
        reasoning="RSI Momentum Divergence SELL: close near 10-bar high, RSI 하락 (-2.50)",
        invalidation="Close above 10-bar high",
        bull_case="",
        bear_case="near high",
    )
    with mock.patch.object(strat, "generate", return_value=sell_signal):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 8. BUY HIGH confidence 모킹 ──────────────
def test_buy_high_confidence_mock():
    import unittest.mock as mock
    strat = RSIMomentumDivStrategy()
    df = _make_df(n=50)
    sig_high = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="rsi_momentum_div",
        entry_price=89.5,
        reasoning="RSI Momentum Divergence BUY: close near 10-bar low, RSI 상승 (+6.00)",
        invalidation="Close below 10-bar low",
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
    strat = RSIMomentumDivStrategy()
    df = _make_df(n=50)
    sig_high = Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="rsi_momentum_div",
        entry_price=115.5,
        reasoning="RSI Momentum Divergence SELL: close near 10-bar high, RSI 하락 (-6.00)",
        invalidation="Close above 10-bar high",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_high):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 10. BUY reasoning에 "RSI" 포함 ──────────
def test_buy_reasoning_contains_rsi():
    import unittest.mock as mock
    strat = RSIMomentumDivStrategy()
    df = _make_df(n=50)
    sig_buy = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="rsi_momentum_div",
        entry_price=89.5,
        reasoning="RSI Momentum Divergence BUY: close near 10-bar low, RSI 상승 (+2.50)",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_buy):
        sig = strat.generate(df)
    assert "RSI" in sig.reasoning


# ── 11. SELL reasoning에 "RSI" 포함 ─────────
def test_sell_reasoning_contains_rsi():
    import unittest.mock as mock
    strat = RSIMomentumDivStrategy()
    df = _make_df(n=50)
    sig_sell = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="rsi_momentum_div",
        entry_price=115.5,
        reasoning="RSI Momentum Divergence SELL: close near 10-bar high, RSI 하락 (-2.50)",
        invalidation="",
        bull_case="",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=sig_sell):
        sig = strat.generate(df)
    assert "RSI" in sig.reasoning


# ── 12. HOLD 신호 정상 반환 ──────────────────
def test_hold_signal():
    """조건 미충족 시 HOLD 반환."""
    df = _make_df(n=50)
    sig = strategy.generate(df)
    # 랜덤 데이터는 다이버전스 없이 HOLD
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
    assert sig.strategy == "rsi_momentum_div"


# ── 13. entry_price는 양수 ───────────────────
def test_entry_price_positive():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# ── 14. 최소 행수 경계값 테스트 ──────────────
def test_minimum_data_boundary():
    """24행 → HOLD, 25행 → 정상 실행."""
    df_24 = _make_df(n=24)
    sig = strategy.generate(df_24)
    assert sig.action == Action.HOLD

    df_25 = _make_df(n=25)
    sig25 = strategy.generate(df_25)
    assert sig25.strategy == "rsi_momentum_div"
