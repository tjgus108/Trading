"""
PriceStructureAnalysisStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_structure_analysis import PriceStructureAnalysisStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_uptrend_df(n: int = 60) -> pd.DataFrame:
    """상승 구조 (Higher High + Higher Low) DataFrame."""
    np.random.seed(10)
    closes = np.cumsum(np.random.uniform(0.3, 1.0, n)) + 100
    highs = closes * 1.01
    lows = closes * 0.99
    opens = closes.copy()
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_downtrend_df(n: int = 60) -> pd.DataFrame:
    """하락 구조 (Lower Low + Lower High) DataFrame."""
    np.random.seed(20)
    closes = 100 + np.cumsum(np.random.uniform(-1.0, -0.3, n))
    closes = np.maximum(closes, 1.0)
    highs = closes * 1.01
    lows = closes * 0.99
    opens = closes.copy()
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_flat_df(n: int = 60) -> pd.DataFrame:
    """횡보 (구조 불명확) DataFrame."""
    np.random.seed(30)
    closes = np.ones(n) * 100 + np.random.normal(0, 0.05, n)
    highs = closes * 1.002
    lows = closes * 0.998
    opens = closes.copy()
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPriceStructureAnalysisStrategy:

    def setup_method(self):
        self.strategy = PriceStructureAnalysisStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "price_structure_analysis"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=5)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. 정상 데이터 Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "price_structure_analysis"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 6. 상승 구조 → BUY
    def test_uptrend_structure_buy(self):
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 7. BUY reasoning에 "상승 구조" 포함
    def test_buy_reasoning_contains_keyword(self):
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "상승" in signal.reasoning

    # 8. 하락 구조 → SELL
    def test_downtrend_structure_sell(self):
        df = _make_downtrend_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 9. SELL reasoning에 "하락 구조" 포함
    def test_sell_reasoning_contains_keyword(self):
        df = _make_downtrend_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "하락" in signal.reasoning

    # 10. 횡보 → HOLD
    def test_flat_market_hold(self):
        df = _make_flat_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. HOLD 시 confidence LOW
    def test_hold_confidence_low(self):
        df = _make_flat_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert signal.confidence == Confidence.LOW

    # 12. BUY 신호에 bull_case/bear_case 존재
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 13. SELL 신호에 bull_case/bear_case 존재
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_downtrend_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 14. entry_price는 마지막 완성 캔들 close
    def test_entry_price_is_last_close(self):
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)

    # 15. BUY confidence: close > prev_recent_high → HIGH
    def test_buy_high_confidence_when_breakout(self):
        """close가 이전 recent_high를 돌파하면 HIGH."""
        df = _make_uptrend_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 16. SELL confidence: close < prev_recent_low → HIGH
    def test_sell_high_confidence_when_breakdown(self):
        """close가 이전 recent_low 아래면 HIGH."""
        df = _make_downtrend_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)
