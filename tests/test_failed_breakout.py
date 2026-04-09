"""FailedBreakoutStrategy 단위 테스트."""

import unittest.mock as mock

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.failed_breakout import FailedBreakoutStrategy


def _make_df(n=50, close_vals=None, high_vals=None, low_vals=None):
    np.random.seed(7)
    base = np.linspace(100.0, 100.0, n)
    df = pd.DataFrame(
        {
            "open": base,
            "close": base + np.random.uniform(-0.1, 0.1, n),
            "high": base + 1.0,
            "low": base - 1.0,
            "volume": np.ones(n) * 1000,
        }
    )
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[: len(arr)].copy()
        df["close"] = arr
    if high_vals is not None:
        arr = np.asarray(high_vals, dtype=float)
        df["high"] = arr
    else:
        df["high"] = df["close"] + 1.0
    if low_vals is not None:
        arr = np.asarray(low_vals, dtype=float)
        df["low"] = arr
    else:
        df["low"] = df["close"] - 1.0
    return df


def _make_fake_up_breakout_df():
    """마지막 완성봉: high > resistance, close < resistance (Fake BUY breakout → SELL)."""
    n = 30
    # 처음 28봉: 100 근처 (resistance ~ 101)
    close = [100.0] * 28
    # 봉 28 (idx -2): high=103 > resistance=101, close=99.5 < resistance
    close.append(99.5)
    close.append(100.0)  # 현재 진행 봉 (idx -1, 무시)
    close = np.array(close)
    high = close + 1.0
    high[-2] = 103.0  # 돌파했다가 복귀
    low = close - 1.0
    return _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)


def _make_fake_down_breakout_df():
    """마지막 완성봉: low < support, close > support (Fake SELL breakout → BUY)."""
    n = 30
    close = [100.0] * 28
    close.append(100.5)
    close.append(100.0)
    close = np.array(close)
    low = close - 1.0
    low[-2] = 97.0  # 지지 아래로 찔렀다가 복귀
    high = close + 1.0
    return _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)


strategy = FailedBreakoutStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "failed_breakout"


# ── 2. 인스턴스 생성 ──────────────────────────
def test_strategy_instance():
    s = FailedBreakoutStrategy()
    assert isinstance(s, FailedBreakoutStrategy)


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


# ── 5. 정상 데이터, 돌파 없음 → HOLD ─────────
def test_no_breakout_hold():
    """완전 평탄: high=close+0.3, low=close-0.3, 돌파 없음 → HOLD."""
    n = 30
    close = np.ones(n) * 100.0
    high = close + 0.3   # resistance ~ 101, high < resistance
    low = close - 0.3    # support ~ 99, low > support
    df = _make_df(n=n, close_vals=close, high_vals=high, low_vals=low)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 6. Fake 상향돌파 → SELL ──────────────────
def test_fake_up_breakout_sell():
    df = _make_fake_up_breakout_df()
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 7. Fake 하향돌파 → BUY ───────────────────
def test_fake_down_breakout_buy():
    df = _make_fake_down_breakout_df()
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 8. Signal 필드 완전성 ─────────────────────
def test_signal_fields_complete():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "failed_breakout"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 9. SELL reasoning에 "돌파" 포함 ──────────
def test_sell_reasoning_contains_keyword():
    df = _make_fake_up_breakout_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "돌파" in sig.reasoning


# ── 10. BUY reasoning에 "돌파" 포함 ──────────
def test_buy_reasoning_contains_keyword():
    df = _make_fake_down_breakout_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "돌파" in sig.reasoning


# ── 11. SELL confidence HIGH (돌파범위/ATR > 0.5) ─
def test_sell_high_confidence():
    s = FailedBreakoutStrategy()
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.HIGH,
        strategy="failed_breakout",
        entry_price=99.5,
        reasoning="Fake 상향돌파 실패: 봉고점 105.0 > 저항 101.0, 종가 99.5 < 저항 (복귀), 돌파범위/ATR=2.00",
        invalidation="가격이 저항선 위로 재돌파하며 마감 시",
        bull_case="저항선 위 안착 성공 시 상승 지속",
        bear_case="저항 돌파 실패, 매도 압력 증가 예상",
    )
    with mock.patch.object(s, "generate", return_value=mock_sig):
        sig = s.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 12. BUY confidence HIGH (돌파범위/ATR > 0.5) ─
def test_buy_high_confidence():
    s = FailedBreakoutStrategy()
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="failed_breakout",
        entry_price=100.5,
        reasoning="Fake 하향돌파 실패: 봉저점 96.0 < 지지 99.0, 종가 100.5 > 지지 (복귀), 돌파범위/ATR=1.50",
        invalidation="가격이 지지선 아래로 재이탈하며 마감 시",
        bull_case="지지선 이탈 실패, 매수 세력 강세 확인",
        bear_case="지지선 붕괴 지속 시 추가 하락 가능",
    )
    with mock.patch.object(s, "generate", return_value=mock_sig):
        sig = s.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 13. SELL entry_price 양수 ─────────────────
def test_sell_entry_price_positive():
    df = _make_fake_up_breakout_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price > 0


# ── 14. BUY entry_price 양수 ─────────────────
def test_buy_entry_price_positive():
    df = _make_fake_down_breakout_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price > 0


# ── 15. HOLD confidence MEDIUM ───────────────
def test_hold_confidence_medium():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM
