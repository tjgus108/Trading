"""
HybridTrendReversionStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.hybrid_trend_rev import HybridTrendReversionStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(closes, highs=None, lows=None, volumes=None):
    n = len(closes)
    closes = np.array(closes, dtype=float)
    if highs is None:
        highs = closes * 1.005
    if lows is None:
        lows = closes * 0.995
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_trending_bull_df(n=80):
    """강한 상승 추세: EMA9 > EMA21 > EMA50, RSI > 50 유도."""
    closes = np.array([100.0 * (1.003 ** i) for i in range(n)])
    return _make_df(closes)


def _make_trending_bear_df(n=80):
    """강한 하락 추세: EMA9 < EMA21 < EMA50, RSI < 50 유도."""
    closes = np.array([200.0 * (0.997 ** i) for i in range(n)])
    return _make_df(closes)


def _make_ranging_df(n=60):
    """횡보장: ADX 낮게 유도 (작은 변동)."""
    np.random.seed(42)
    closes = 100.0 + np.random.uniform(-0.3, 0.3, n)
    return _make_df(closes)


def _make_insufficient_df(n=15):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


def _make_bb_buy_df(n=60):
    """횡보 후 마지막 2봉을 BB 하단 아래로."""
    np.random.seed(10)
    closes = 100.0 + np.random.uniform(-0.2, 0.2, n)
    closes[-2] = 85.0  # close < BB_lower 유도
    highs = np.maximum(closes * 1.005, closes)
    lows = np.minimum(closes * 0.995, closes)
    return _make_df(closes, highs, lows)


def _make_bb_sell_df(n=60):
    """횡보 후 마지막 2봉을 BB 상단 위로."""
    np.random.seed(11)
    closes = 100.0 + np.random.uniform(-0.2, 0.2, n)
    closes[-2] = 115.0  # close > BB_upper 유도
    highs = np.maximum(closes * 1.005, closes)
    lows = np.minimum(closes * 0.995, closes)
    return _make_df(closes, highs, lows)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestHybridTrendReversionStrategy:

    def setup_method(self):
        self.strategy = HybridTrendReversionStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "hybrid_trend_rev"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 인스턴스 반환
    def test_returns_signal_instance(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 6. action은 유효한 값
    def test_action_is_valid(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence는 유효한 값
    def test_confidence_is_valid(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "hybrid_trend_rev"

    # 9. entry_price는 _last 봉 close와 일치
    def test_entry_price_matches_last_close(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 10. reasoning은 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0

    # 11. bull_case / bear_case 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 12. 상승 추세 → SELL 아님
    def test_bullish_trend_no_sell(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 13. 하락 추세 → BUY 아님
    def test_bearish_trend_no_buy(self):
        df = _make_trending_bear_df()
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY

    # 14. BB 하단 이탈 → BUY (횡보장)
    def test_bb_lower_break_buy(self):
        df = _make_bb_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 15. BB 상단 이탈 → SELL (횡보장)
    def test_bb_upper_break_sell(self):
        df = _make_bb_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 16. BUY 시 reasoning에 "BUY" 또는 "ranging"/"trending" 포함
    def test_buy_reasoning_contains_mode(self):
        df = _make_bb_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "ranging" in signal.reasoning or "trending" in signal.reasoning

    # 17. SELL 시 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_bb_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 18. BUY 시 invalidation 포함
    def test_buy_has_invalidation(self):
        df = _make_bb_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 19. entry_price는 양수 float
    def test_entry_price_positive(self):
        df = _make_trending_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)
        assert signal.entry_price > 0

    # 20. 정확히 30봉 → HOLD 아닌 신호 가능 (에러 없음)
    def test_exactly_30_rows_no_error(self):
        closes = np.linspace(100, 130, 30)
        df = _make_df(closes)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 21. ranging + 중간 close → HOLD
    def test_ranging_middle_close_hold(self):
        df = _make_ranging_df(n=60)
        signal = self.strategy.generate(df)
        # 중간 close라면 BB 이탈 없어 HOLD
        assert signal.action == Action.HOLD
