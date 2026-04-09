"""
ADXRegimeStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adx_regime import ADXRegimeStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 80, trend: str = "up", volatility: float = 0.015) -> pd.DataFrame:
    """
    테스트용 OHLCV DataFrame.
    trend: "up" | "down" | "flat"
    volatility: 캔들 spread 크기 (클수록 ADX 높음)
    """
    np.random.seed(42)
    if trend == "up":
        closes = np.cumprod(1 + np.random.uniform(0.004, 0.010, n)) * 100
    elif trend == "down":
        closes = np.cumprod(1 - np.random.uniform(0.004, 0.010, n)) * 100
    else:
        closes = np.ones(n) * 100 + np.random.randn(n) * 0.05

    highs = closes * (1 + volatility)
    lows = closes * (1 - volatility)
    opens = closes * (1 + np.random.uniform(-0.002, 0.002, n))

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
    })


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestADXRegimeStrategy:

    def setup_method(self):
        self.strategy = ADXRegimeStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "adx_regime"

    # 2. 강한 상승 추세 → BUY
    def test_strong_uptrend_buy(self):
        df = _make_df(n=100, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 강한 하락 추세 → SELL
    def test_strong_downtrend_sell(self):
        df = _make_df(n=100, trend="down", volatility=0.04)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. 횡보 (낮은 변동성) → HOLD
    def test_sideways_hold(self):
        df = _make_df(n=100, trend="flat", volatility=0.001)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 → HOLD, LOW
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=25)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 6. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 7. BUY confidence (HIGH or MEDIUM)
    def test_buy_confidence_valid(self):
        df = _make_df(n=100, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 8. SELL confidence (HIGH or MEDIUM)
    def test_sell_confidence_valid(self):
        df = _make_df(n=100, trend="down", volatility=0.04)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=100, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "adx_regime"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 10. BUY reasoning에 "ADX" 포함
    def test_buy_reasoning_contains_adx(self):
        df = _make_df(n=100, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        assert "ADX" in signal.reasoning

    # 11. BUY 신호 bull_case / bear_case 비어있지 않음
    def test_buy_has_bull_bear_case(self):
        df = _make_df(n=100, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 12. SELL 신호 bull_case / bear_case 비어있지 않음
    def test_sell_has_bull_bear_case(self):
        df = _make_df(n=100, trend="down", volatility=0.04)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 13. entry_price는 close 값
    def test_entry_price_is_close(self):
        df = _make_df(n=100, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 14. n=30 경계값 (정확히 30행)
    def test_min_rows_boundary(self):
        df = _make_df(n=30, trend="up", volatility=0.04)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 15. n=29 경계값 → HOLD
    def test_below_min_rows(self):
        df = _make_insufficient_df(n=29)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 16. 커스텀 파라미터 초기화
    def test_custom_params(self):
        s = ADXRegimeStrategy(adx_trending=30.0, adx_sideways=15.0, adx_high=40.0)
        assert s.adx_trending == 30.0
        assert s.adx_sideways == 15.0
        assert s.adx_high == 40.0
