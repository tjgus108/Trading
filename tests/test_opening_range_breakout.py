"""
OpeningRangeBreakoutStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.opening_range_breakout import OpeningRangeBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 20,
    range_bars: int = 5,
    range_high: float = 110.0,
    range_low: float = 90.0,
    last_close: float = 100.0,
) -> pd.DataFrame:
    """
    처음 range_bars봉은 오프닝 레인지(high/low 포함),
    나머지 봉은 중간 값으로 채우고,
    신호 봉(-2)의 close를 last_close로 설정.
    """
    highs = [range_high] * range_bars + [100.0] * (n - range_bars)
    lows = [range_low] * range_bars + [100.0] * (n - range_bars)
    closes = [100.0] * n
    opens = [100.0] * n
    volumes = [1000.0] * n

    # 신호 봉 = -2
    closes[-2] = last_close

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


class TestOpeningRangeBreakoutStrategy:

    def setup_method(self):
        self.strategy = OpeningRangeBreakoutStrategy(range_bars=5)

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "opening_range_breakout"

    # 2. BUY 신호: close > range_high
    def test_buy_signal(self):
        df = _make_df(last_close=115.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "opening_range_breakout"
        assert sig.entry_price == 115.0

    # 3. SELL 신호: close < range_low
    def test_sell_signal(self):
        df = _make_df(last_close=85.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == 85.0

    # 4. HOLD: close 레인지 내
    def test_hold_in_range(self):
        df = _make_df(last_close=100.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY HIGH confidence: 돌파 폭 > range * 1%
    def test_buy_high_confidence(self):
        # range = 110 - 90 = 20, threshold = 0.2, breakout = 115 - 110 = 5 > 0.2
        df = _make_df(last_close=115.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 6. BUY MEDIUM confidence: 돌파 폭 <= range * 1%
    def test_buy_medium_confidence(self):
        # range = 110 - 90 = 20, threshold = 0.2, breakout = 110.1 - 110 = 0.1 < 0.2
        df = _make_df(last_close=110.1, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 7. SELL HIGH confidence: 돌파 폭 > range * 1%
    def test_sell_high_confidence(self):
        # range = 20, threshold = 0.2, breakout = 90 - 85 = 5 > 0.2
        df = _make_df(last_close=85.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. SELL MEDIUM confidence: 돌파 폭 <= range * 1%
    def test_sell_medium_confidence(self):
        # range = 20, threshold = 0.2, breakout = 90 - 89.9 = 0.1 < 0.2
        df = _make_df(last_close=89.9, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 9. 데이터 부족 (range_bars=5 → min=10, n=8)
    def test_insufficient_data(self):
        df = _make_df(n=8, last_close=115.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 10. 커스텀 range_bars 파라미터
    def test_custom_range_bars(self):
        strategy = OpeningRangeBreakoutStrategy(range_bars=3)
        # 처음 3봉: high=110, low=90
        df = _make_df(n=20, range_bars=3, range_high=110.0, range_low=90.0, last_close=115.0)
        sig = strategy.generate(df)
        assert sig.action == Action.BUY

    # 11. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_df(last_close=115.0)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")
        assert sig.reasoning != ""

    # 12. HOLD reasoning 포함
    def test_hold_reasoning(self):
        df = _make_df(last_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.reasoning != ""

    # 13. range_high == close (경계: 돌파 아님)
    def test_close_equals_range_high_is_hold(self):
        df = _make_df(last_close=110.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 14. range_low == close (경계: 돌파 아님)
    def test_close_equals_range_low_is_hold(self):
        df = _make_df(last_close=90.0, range_high=110.0, range_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
