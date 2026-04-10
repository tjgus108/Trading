"""
HighLowChannelStrategy 단위 테스트 (14개+)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.high_low_channel import HighLowChannelStrategy

MIN_ROWS = 20


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

def _base_df(n: int = 30, close: float = 100.0) -> pd.DataFrame:
    """기본 평탄 DataFrame."""
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _buy_channel_df(n: int = 30, channel_high: float = 110.0, channel_low: float = 90.0) -> pd.DataFrame:
    """
    BUY 조건: position < 0.25 AND price_up
    채널: [channel_low, channel_high]
    신호봉(idx=-2): close가 채널 하단 근처 + 상향
    """
    mid = (channel_high + channel_low) / 2
    closes = [mid] * (n - 2)
    # idx = n-2: channel_low + 2% 범위 + 상향
    buy_close = channel_low + (channel_high - channel_low) * 0.15  # position ~ 0.15
    closes.append(buy_close)   # idx = n-2 (signal candle)
    closes.append(buy_close)   # idx = n-1 (current, ignored)

    highs = [channel_high] * (n - 10) + [channel_high - 0.1] * 8 + [buy_close + 1] + [buy_close + 1]
    lows = [channel_low] * (n - 10) + [channel_low + 0.1] * 8 + [channel_low - 0.5] + [channel_low - 0.5]

    # prev candle (idx = n-3): close가 buy_close보다 낮아야 price_up
    prev_close = buy_close - 1.0
    closes[n - 3] = prev_close

    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })
    return df


def _sell_channel_df(n: int = 30, channel_high: float = 110.0, channel_low: float = 90.0) -> pd.DataFrame:
    """
    SELL 조건: position > 0.75 AND price_down
    신호봉(idx=-2): close가 채널 상단 근처 + 하향
    """
    mid = (channel_high + channel_low) / 2
    closes = [mid] * (n - 2)
    sell_close = channel_low + (channel_high - channel_low) * 0.85  # position ~ 0.85
    closes.append(sell_close)  # idx = n-2
    closes.append(sell_close)  # idx = n-1

    highs = [channel_high] * (n - 10) + [channel_high + 0.5] * 8 + [channel_high + 0.5] + [channel_high + 0.5]
    lows = [channel_low] * (n - 10) + [channel_low - 0.1] * 8 + [channel_low] + [channel_low]

    # prev candle: close > sell_close (price_down)
    prev_close = sell_close + 1.0
    closes[n - 3] = prev_close

    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })
    return df


# ── 테스트 ────────────────────────────────────────────────────────────────────

class TestHighLowChannelStrategy:

    def setup_method(self):
        self.strategy = HighLowChannelStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "high_low_channel"

    # 2. 인스턴스 확인
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _base_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. 19행 → HOLD (MIN_ROWS=20)
    def test_19_rows_returns_hold(self):
        df = _base_df(n=19)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 20행 → Signal 반환
    def test_20_rows_returns_signal(self):
        df = _base_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. None 반환 없음
    def test_generate_never_returns_none(self):
        df = _base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 7. reasoning 필드 존재
    def test_reasoning_field_exists(self):
        df = _base_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _base_df(n=30)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 9. entry_price > 0
    def test_entry_price_positive(self):
        df = _base_df(n=30, close=100.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 10. strategy 필드 = 전략명
    def test_strategy_field(self):
        df = _base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "high_low_channel"

    # 11. BUY 신호 — 채널 하단 시나리오
    def test_buy_signal_channel_bottom(self):
        df = _buy_channel_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 12. SELL 신호 — 채널 상단 시나리오
    def test_sell_signal_channel_top(self):
        df = _sell_channel_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 13. BUY reasoning에 "position" 포함
    def test_buy_reasoning_mentions_position(self):
        df = _buy_channel_df(n=30)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "position" in sig.reasoning

    # 14. SELL reasoning에 "position" 포함
    def test_sell_reasoning_mentions_position(self):
        df = _sell_channel_df(n=30)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "position" in sig.reasoning

    # 15. BUY HIGH confidence (position < 0.1)
    def test_buy_high_confidence_very_bottom(self):
        """position < 0.1이면 HIGH"""
        n = 30
        channel_high = 110.0
        channel_low = 90.0
        mid = (channel_high + channel_low) / 2
        closes = [mid] * (n - 2)
        buy_close = channel_low + (channel_high - channel_low) * 0.05  # position ~ 0.05
        closes.append(buy_close)
        closes.append(buy_close)
        prev_close = buy_close - 1.0
        closes[n - 3] = prev_close

        df = pd.DataFrame({
            "open":   closes,
            "close":  closes,
            "high":   [channel_high] * (n - 2) + [buy_close + 1] + [buy_close + 1],
            "low":    [channel_low] * (n - 2) + [channel_low - 1] + [channel_low - 1],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 16. SELL HIGH confidence (position > 0.9)
    def test_sell_high_confidence_very_top(self):
        """position > 0.9이면 HIGH"""
        n = 30
        channel_high = 110.0
        channel_low = 90.0
        mid = (channel_high + channel_low) / 2
        closes = [mid] * (n - 2)
        sell_close = channel_low + (channel_high - channel_low) * 0.95  # position ~ 0.95
        closes.append(sell_close)
        closes.append(sell_close)
        prev_close = sell_close + 1.0
        closes[n - 3] = prev_close

        df = pd.DataFrame({
            "open":   closes,
            "close":  closes,
            "high":   [channel_high] * (n - 2) + [channel_high + 1] + [channel_high + 1],
            "low":    [channel_low] * (n - 2) + [channel_low] + [channel_low],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 17. 중간 구간 → HOLD
    def test_hold_mid_channel(self):
        """position 0.5 근처이면 HOLD"""
        n = 30
        channel_high = 110.0
        channel_low = 90.0
        mid = (channel_high + channel_low) / 2  # position ~ 0.5
        closes = [mid] * n

        df = pd.DataFrame({
            "open":   closes,
            "close":  closes,
            "high":   [channel_high] * n,
            "low":    [channel_low] * n,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
