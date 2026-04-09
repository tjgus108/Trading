"""
EMAStackStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ema_stack import EMAStackStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_bull_df(n: int = 80, expanding: bool = True) -> pd.DataFrame:
    """Perfect Bull Stack: ema8 > ema21 > ema50, close > ema8."""
    np.random.seed(10)
    # 강한 상승 추세로 ema8 > ema21 > ema50 자연스럽게 형성
    closes = np.array([100.0 * (1.003 ** i) for i in range(n)])
    highs = closes * 1.005
    lows = closes * 0.995

    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })

    ema8 = df["close"].ewm(span=8, adjust=False).mean()
    ema21 = df["close"].ewm(span=21, adjust=False).mean()

    # ema50: ema21보다 낮게 고정 (bull stack 보장)
    if expanding:
        df["ema50"] = ema21 * 0.97  # 간격 확대 위해 충분히 낮게
    else:
        df["ema50"] = ema21 * 0.999  # 간격 좁게 (MEDIUM)

    return df


def _make_bear_df(n: int = 100, expanding: bool = True) -> pd.DataFrame:
    """Perfect Bear Stack: ema8 < ema21 < ema50, close < ema8."""
    np.random.seed(11)
    closes = np.array([100.0 * (0.995 ** i) for i in range(n)])
    highs = closes * 1.005
    lows = closes * 0.995

    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })

    ema8_series = df["close"].ewm(span=8, adjust=False).mean()
    ema21_series = df["close"].ewm(span=21, adjust=False).mean()

    # ema50: ema21보다 높게 고정 (bear stack 보장)
    # expanding=True: 간격이 확대되도록 ema50을 고정 고가로 설정
    if expanding:
        # ema50을 초기 close 값(100.0)에 가깝게 고정 → 하락할수록 ema21-ema8 + ema50-ema21 증가
        df["ema50"] = 100.0 * 1.05
    else:
        df["ema50"] = ema21_series * 1.001

    return df


def _make_hold_df(n: int = 80) -> pd.DataFrame:
    """횡보: 정렬 없음."""
    np.random.seed(12)
    closes = np.ones(n) * 100.0 + np.random.uniform(-0.5, 0.5, n)
    highs = closes * 1.002
    lows = closes * 0.998
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    ema21 = pd.Series(closes).ewm(span=21, adjust=False).mean()
    df["ema50"] = ema21 * 1.0  # ema50 ≈ ema21 → 정렬 안 됨
    return df


def _make_insufficient_df(n: int = 30) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98,
    })
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestEMAStackStrategy:

    def setup_method(self):
        self.strategy = EMAStackStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "ema_stack"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Perfect Bull Stack → BUY
    def test_bull_stack_buy(self):
        df = _make_bull_df(n=80, expanding=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. Perfect Bear Stack → SELL
    def test_bear_stack_sell(self):
        df = _make_bear_df(n=80, expanding=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 7. Bull stack + 간격 확대 → HIGH confidence
    def test_bull_expanding_high_confidence(self):
        df = _make_bull_df(n=80, expanding=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 8. Bear stack + 간격 확대 → HIGH confidence
    def test_bear_expanding_high_confidence(self):
        df = _make_bear_df(n=80, expanding=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 9. 횡보 → HOLD
    def test_sideways_hold(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "ema_stack"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 11. BUY reasoning에 "EMA Stack" 포함
    def test_buy_reasoning_contains_ema_stack(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "EMA Stack" in signal.reasoning

    # 12. SELL reasoning에 "EMA Stack" 포함
    def test_sell_reasoning_contains_ema_stack(self):
        df = _make_bear_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "EMA Stack" in signal.reasoning

    # 13. BUY 신호에 invalidation 포함
    def test_buy_has_invalidation(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 14. SELL 신호에 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_bear_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 15. bull_case / bear_case 필드 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 16. entry_price는 close 값과 일치
    def test_entry_price_is_close(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected_close) < 1e-6
