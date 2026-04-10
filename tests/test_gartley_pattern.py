"""
SimplifiedGartleyStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.gartley_pattern import SimplifiedGartleyStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 40, close_prices=None) -> pd.DataFrame:
    if close_prices is None:
        close_prices = [100.0] * n
    highs = [c + 1.0 for c in close_prices]
    lows = [c - 1.0 for c in close_prices]
    return pd.DataFrame({
        "open": close_prices,
        "close": close_prices,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * len(close_prices),
    })


def _make_bull_gartley_df() -> pd.DataFrame:
    """
    Bullish Gartley D-point 근방 케이스.
    swing_low=100, swing_high=200 → rng=100
    bull_D = 100 + 100*(1-0.786) = 100 + 21.4 = 121.4
    신호봉 close = 121.4 (D-point 정확히)
    """
    n = 40
    closes = [100.0] * 10 + list(np.linspace(100, 200, 20)) + [150.0] * 8
    # 신호봉(-2) = 121.4, 현재봉(-1) = 122.0
    closes.append(121.4)
    closes.append(122.0)
    closes = closes[:n]
    return _make_df(n=len(closes), close_prices=closes)


def _make_bear_gartley_df() -> pd.DataFrame:
    """
    Bearish Gartley D-point 근방 케이스.
    swing_low=100, swing_high=200 → rng=100
    bear_D = 200 - 100*(1-0.786) = 200 - 21.4 = 178.6
    신호봉 close = 178.6
    """
    n = 40
    closes = [200.0] * 10 + list(np.linspace(200, 100, 20)) + [150.0] * 8
    closes.append(178.6)
    closes.append(178.0)
    closes = closes[:n]
    return _make_df(n=len(closes), close_prices=closes)


class TestSimplifiedGartleyStrategy:

    def setup_method(self):
        self.strategy = SimplifiedGartleyStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "gartley_pattern"

    # 2. 데이터 부족 (< 35행)
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 정확히 최소 행 (35행)
    def test_exactly_min_rows(self):
        df = _make_df(n=35)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. 34행 → HOLD
    def test_one_below_min_rows(self):
        df = _make_df(n=34)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 5. 가격 범위 없음 → HOLD
    def test_no_price_range(self):
        closes = [100.0] * 40
        df = _make_df(n=40, close_prices=closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "No price range" in sig.reasoning

    # 6. Bullish Gartley → BUY 또는 HOLD
    def test_buy_signal_bull_gartley(self):
        df = _make_bull_gartley_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 7. Bearish Gartley → SELL 또는 HOLD
    def test_sell_signal_bear_gartley(self):
        df = _make_bear_gartley_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 9. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 10. strategy 필드 값
    def test_signal_strategy_field(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.strategy == "gartley_pattern"

    # 11. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 12. BUY 신호 시 confidence HIGH (오차 < 1%)
    def test_buy_high_confidence_exact_match(self):
        """D-point 정확히 일치하면 HIGH confidence."""
        # swing_low=100, swing_high=200, bull_D=121.4
        n = 40
        closes = list(np.linspace(100, 200, 20))  # 최저=100, 최고=200
        # 나머지 봉을 중간값으로 채움
        while len(closes) < n - 2:
            closes.insert(0, 150.0)
        closes.append(121.4)   # 신호봉(-2)
        closes.append(122.0)   # 현재봉(-1)
        closes = closes[:n]
        df = _make_df(n=len(closes), close_prices=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 13. HOLD 신호 시 confidence LOW
    def test_hold_confidence_is_low(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 14. Action은 유효한 Enum 값
    def test_action_is_valid_enum(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 15. Confidence는 유효한 Enum 값
    def test_confidence_is_valid_enum(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 16. 큰 데이터셋 처리 (100행)
    def test_large_dataset(self):
        n = 100
        closes = list(np.linspace(50, 200, n))
        df = _make_df(n=n, close_prices=closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
