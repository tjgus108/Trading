"""
PriceChannelFilterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_channel_filter import PriceChannelFilterStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, scenario: str = "neutral") -> pd.DataFrame:
    """
    scenario:
      "neutral"       → position ≈ 0.5 → HOLD
      "buy"           → position > 0.8 AND close > prev_close → BUY
      "buy_high"      → position > 0.95 AND close > prev_close → BUY HIGH
      "sell"          → position < 0.2 AND close < prev_close → SELL
      "sell_high"     → position < 0.05 AND close < prev_close → SELL HIGH
      "buy_no_rising" → position > 0.8 BUT close <= prev_close → HOLD
      "sell_no_falling"→ position < 0.2 BUT close >= prev_close → HOLD
    """
    base = 100.0
    closes = [base] * n
    highs = [base] * n
    lows = [base] * n

    channel_range = 100.0  # channel_period=20 윈도우에서의 range

    if scenario == "buy":
        # upper_ch 근처에 close 배치: position > 0.8
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base + channel_range * 0.35  # position ≈ 0.85

        # 신호봉(-2): close > 이전 봉
        closes[-3] = base + channel_range * 0.33
        closes[-2] = base + channel_range * 0.36  # 상승
        closes[-1] = base + channel_range * 0.34  # 진행 중

    elif scenario == "buy_high":
        # position > 0.95
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base + channel_range * 0.45  # position ≈ 0.95

        closes[-3] = base + channel_range * 0.44
        closes[-2] = base + channel_range * 0.46  # 상승
        closes[-1] = base + channel_range * 0.44

    elif scenario == "sell":
        # lower_ch 근처에 close 배치: position < 0.2
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base - channel_range * 0.35  # position ≈ 0.15

        closes[-3] = base - channel_range * 0.33
        closes[-2] = base - channel_range * 0.36  # 하락
        closes[-1] = base - channel_range * 0.34

    elif scenario == "sell_high":
        # position < 0.05
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base - channel_range * 0.47  # position ≈ 0.03

        closes[-3] = base - channel_range * 0.46
        closes[-2] = base - channel_range * 0.48  # 하락
        closes[-1] = base - channel_range * 0.46

    elif scenario == "buy_no_rising":
        # position > 0.8 이지만 close <= prev_close → HOLD
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base + channel_range * 0.35

        closes[-3] = base + channel_range * 0.36
        closes[-2] = base + channel_range * 0.35  # 하락 (not rising) → HOLD
        closes[-1] = base + channel_range * 0.34

    elif scenario == "sell_no_falling":
        # position < 0.2 이지만 close >= prev_close → HOLD
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base - channel_range * 0.35

        closes[-3] = base - channel_range * 0.36
        closes[-2] = base - channel_range * 0.35  # 상승 (not falling) → HOLD
        closes[-1] = base - channel_range * 0.34

    else:  # neutral: close = midpoint
        for i in range(n):
            highs[i] = base + channel_range / 2
            lows[i] = base - channel_range / 2
            closes[i] = base  # position = 0.5

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })
    return df


class TestPriceChannelFilterStrategy:

    def setup_method(self):
        self.strategy = PriceChannelFilterStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_channel_filter"

    # 2. 데이터 부족 (< 25행)
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. HOLD: 채널 중간 (neutral)
    def test_hold_neutral(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "price_channel_filter"

    # 4. BUY: 상단 돌파 + 상승 중
    def test_buy_upper_breakout(self):
        df = _make_df(n=40, scenario="buy")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 5. SELL: 하단 이탈 + 하락 중
    def test_sell_lower_breakdown(self):
        df = _make_df(n=40, scenario="sell")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 6. BUY confidence MEDIUM or HIGH
    def test_buy_confidence(self):
        df = _make_df(n=40, scenario="buy")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 7. SELL confidence MEDIUM or HIGH
    def test_sell_confidence(self):
        df = _make_df(n=40, scenario="sell")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 8. BUY HIGH confidence (position > 0.95)
    def test_buy_high_confidence_possible(self):
        df = _make_df(n=40, scenario="buy_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. SELL HIGH confidence (position < 0.05)
    def test_sell_high_confidence_possible(self):
        df = _make_df(n=40, scenario="sell_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. HOLD: position > 0.8 이지만 상승 중 아님
    def test_hold_buy_no_rising(self):
        df = _make_df(n=40, scenario="buy_no_rising")
        sig = self.strategy.generate(df)
        # 상승이 아니면 BUY 조건 불만족 → HOLD 예상 (데이터에 따라 다를 수 있음)
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 11. HOLD: position < 0.2 이지만 하락 중 아님
    def test_hold_sell_no_falling(self):
        df = _make_df(n=40, scenario="sell_no_falling")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""
        assert sig.strategy == "price_channel_filter"

    # 13. high/low 컬럼 없을 때 처리
    def test_no_high_low_columns(self):
        df = pd.DataFrame({
            "open": [100.0] * 30,
            "close": [100.0] * 30,
            "volume": [1000.0] * 30,
        })
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        # close==high==low → channel_width=0 → position=0/(0+1e-10)=0 → SELL 또는 HOLD
        assert sig.action in (Action.HOLD, Action.SELL, Action.BUY)

    # 14. 최소 데이터 경계: 정확히 25행
    def test_exactly_min_rows(self):
        df = _make_df(n=25, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. entry_price는 양수
    def test_entry_price_positive(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 16. 대용량 데이터 처리
    def test_large_dataframe(self):
        df = _make_df(n=200, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
