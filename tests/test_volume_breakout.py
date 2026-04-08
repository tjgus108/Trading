"""
VolumeBreakoutStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_breakout import VolumeBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0, open_: float = 99.0,
             volume: float = 1000.0, avg_volume: float = 500.0,
             ema20: float = 98.0) -> pd.DataFrame:
    """
    마지막 봉(-2)이 신호 봉, 마지막 봉(-1)이 현재 진행 중 캔들.
    앞 n-2개 봉의 volume = avg_volume (평균 계산용).
    """
    rows = n
    volumes = [avg_volume] * rows
    closes = [close] * rows
    opens = [open_] * rows
    ema20s = [ema20] * rows

    # 신호 봉 = index -2
    volumes[-2] = volume

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "volume": volumes,
        "ema20": ema20s,
    })
    return df


class TestVolumeBreakoutStrategy:

    def setup_method(self):
        self.strategy = VolumeBreakoutStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "volume_breakout"

    # 2. BUY 신호: volume spike + 양봉 + close > ema20
    def test_buy_signal(self):
        df = _make_df(close=105.0, open_=99.0, volume=1100.0, avg_volume=500.0, ema20=100.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.BUY
        assert sig.strategy == "volume_breakout"
        assert sig.entry_price == 105.0

    # 3. BUY HIGH confidence: volume > 3x 평균
    def test_buy_high_confidence(self):
        df = _make_df(close=105.0, open_=99.0, volume=1600.0, avg_volume=500.0, ema20=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 4. SELL 신호: volume spike + 음봉 + close < ema20
    def test_sell_signal(self):
        df = _make_df(close=95.0, open_=101.0, volume=1100.0, avg_volume=500.0, ema20=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM
        assert sig.entry_price == 95.0

    # 5. HOLD: volume spike 없음
    def test_hold_no_spike(self):
        df = _make_df(close=105.0, open_=99.0, volume=900.0, avg_volume=500.0, ema20=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. HOLD: spike 있지만 양봉인데 close < ema20
    def test_hold_bull_candle_below_ema(self):
        df = _make_df(close=95.0, open_=90.0, volume=1100.0, avg_volume=500.0, ema20=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 7. 데이터 부족 (< 25행)
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 8. Signal 필드 완전성 확인
    def test_signal_fields(self):
        df = _make_df(close=105.0, open_=99.0, volume=1100.0, avg_volume=500.0, ema20=100.0)
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
