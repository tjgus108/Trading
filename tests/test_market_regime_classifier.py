"""
MarketRegimeClassifierStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.market_regime_classifier import MarketRegimeClassifierStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_trending_up(n: int = 80) -> pd.DataFrame:
    """강한 상승 추세: EMA20 > EMA50, close > EMA20, ADX 높음."""
    np.random.seed(0)
    closes = np.cumprod(1 + np.random.uniform(0.006, 0.012, n)) * 100
    highs = closes * 1.03
    lows = closes * 0.97
    opens = closes * np.random.uniform(0.998, 1.002, n)
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows, "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_trending_down(n: int = 80) -> pd.DataFrame:
    """강한 하락 추세: EMA20 < EMA50, close < EMA20, ADX 높음."""
    np.random.seed(1)
    closes = np.cumprod(1 - np.random.uniform(0.006, 0.012, n)) * 100
    highs = closes * 1.03
    lows = closes * 0.97
    opens = closes * np.random.uniform(0.998, 1.002, n)
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows, "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_sideways(n: int = 80) -> pd.DataFrame:
    """횡보: ADX 낮음, 가격 범위 좁음."""
    np.random.seed(2)
    closes = np.ones(n) * 100 + np.random.randn(n) * 0.02
    highs = closes * 1.001
    lows = closes * 0.999
    opens = closes.copy()
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows, "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_crash(n: int = 60) -> pd.DataFrame:
    """급락: 5봉 연속 음봉 + 5봉 대비 -10% 하락."""
    np.random.seed(3)
    closes = np.ones(n) * 100
    # 마지막 10봉에서 급락 삽입
    for i in range(n - 10, n):
        closes[i] = closes[i - 1] * 0.978  # 매봉 -2.2% → 10봉 = ~-20%
    highs = closes * 1.005
    lows = closes * 0.995
    # 음봉: open > close
    opens = closes * 1.01
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows, "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_insufficient(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes, "high": closes * 1.005, "low": closes * 0.995,
        "close": closes, "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMarketRegimeClassifier:

    def setup_method(self):
        self.strategy = MarketRegimeClassifierStrategy()

    # 1. strategy name
    def test_strategy_name(self):
        assert self.strategy.name == "market_regime_classifier"

    # 2. 상승 추세 → BUY
    def test_trending_up_buy(self):
        df = _make_trending_up(n=100)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 하락 추세 → SELL
    def test_trending_down_sell(self):
        df = _make_trending_down(n=100)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. 횡보 → HOLD
    def test_sideways_hold(self):
        df = _make_sideways(n=100)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. 횡보 → LOW confidence
    def test_sideways_low_confidence(self):
        df = _make_sideways(n=100)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 6. CRASH → SELL HIGH confidence
    def test_crash_sell_high(self):
        df = _make_crash(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.HIGH

    # 7. CRASH reasoning에 "CRASH" 포함
    def test_crash_reasoning_contains_crash(self):
        df = _make_crash(n=60)
        signal = self.strategy.generate(df)
        assert "CRASH" in signal.reasoning

    # 8. 데이터 부족 (n=25) → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient(n=25)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 9. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_trending_up(n=100)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "market_regime_classifier"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 11. BUY signal has bull_case and bear_case
    def test_buy_has_bull_bear_case(self):
        df = _make_trending_up(n=100)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 12. SELL signal has bull_case and bear_case
    def test_sell_has_bull_bear_case(self):
        df = _make_trending_down(n=100)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 13. entry_price == close.iloc[-2]
    def test_entry_price_is_close_iloc_minus2(self):
        df = _make_trending_up(n=100)
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 14. n=30 경계값 → Signal 반환
    def test_min_rows_boundary(self):
        df = _make_trending_up(n=30)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 15. n=29 → HOLD (데이터 부족)
    def test_below_min_rows(self):
        df = _make_insufficient(n=29)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 16. 상승 추세 confidence는 MEDIUM 또는 HIGH
    def test_trending_up_confidence_valid(self):
        df = _make_trending_up(n=100)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 17. 하락 추세 confidence는 MEDIUM 또는 HIGH
    def test_trending_down_confidence_valid(self):
        df = _make_trending_down(n=100)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)
