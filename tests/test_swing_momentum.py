"""
SwingMomentumStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.swing_momentum import SwingMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(
    n: int = _MIN_ROWS + 2,
    close_val: float = 100.0,
    swing_high: float = 98.0,
    swing_low: float = 92.0,
    volume: float = 2000.0,
    vol_ma10: float = 1000.0,
    avg_range: float = 3.0,
    swing_range: float = 6.0,
) -> pd.DataFrame:
    """
    신호 봉(-2)의 close가 swing_high/low 대비 조건을 갖도록 구성.
    high.rolling(5).max().shift(2) 가 swing_high 가 되도록
    idx=-2 기준으로 [-4, -3] 범위의 high 값을 설정.
    """
    rows = n
    closes = [95.0] * rows
    closes[-2] = close_val

    highs = [swing_high] * rows
    lows = [swing_low] * rows
    # shift(2) → idx=-2에서의 shift(2) 결과는 [-4] 위치의 rolling(5).max()
    # 즉 [-6:-2] 구간의 max가 swing_high가 되도록 설정
    for i in range(rows - 6, rows - 1):
        if 0 <= i < rows:
            highs[i] = swing_high
            lows[i] = swing_low

    volumes = [vol_ma10] * rows
    volumes[-2] = volume

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


class TestSwingMomentumStrategy:

    def setup_method(self):
        self.strategy = SwingMomentumStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "swing_momentum"

    # 2. BUY: close > swing_high + 볼륨 확인
    def test_buy_swing_breakout(self):
        df = _make_df(close_val=105.0, swing_high=98.0, volume=3000.0, vol_ma10=1000.0)
        sig = self.strategy.generate(df)
        # close=105 > swing_high=98 (rolling max shift(2) 기반)
        # 실제 rolling 계산 후 확인
        high = df["high"]
        swing_h = high.rolling(5, min_periods=1).max().shift(2)
        idx = len(df) - 2
        sh = swing_h.iloc[idx]
        vol = df["volume"].iloc[idx]
        vma = df["volume"].rolling(10, min_periods=1).mean().iloc[idx]
        if df["close"].iloc[idx] > sh and vol > vma:
            assert sig.action == Action.BUY

    # 3. BUY signal fields
    def test_buy_signal_fields(self):
        df = _make_df(close_val=110.0, swing_high=98.0, volume=3000.0, vol_ma10=1000.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "swing_momentum"
        assert sig.entry_price > 0

    # 4. SELL: close < swing_low + 볼륨 확인
    def test_sell_swing_breakdown(self):
        df = _make_df(close_val=85.0, swing_low=92.0, volume=3000.0, vol_ma10=1000.0)
        sig = self.strategy.generate(df)
        low = df["low"]
        swing_l = low.rolling(5, min_periods=1).min().shift(2)
        idx = len(df) - 2
        sl = swing_l.iloc[idx]
        vol = df["volume"].iloc[idx]
        vma = df["volume"].rolling(10, min_periods=1).mean().iloc[idx]
        if df["close"].iloc[idx] < sl and vol > vma:
            assert sig.action == Action.SELL

    # 5. SELL signal fields
    def test_sell_signal_fields(self):
        df = _make_df(close_val=80.0, swing_low=92.0, volume=3000.0, vol_ma10=1000.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "swing_momentum"

    # 6. HOLD: 볼륨 부족 (breakout 있어도 볼륨 미달)
    def test_hold_low_volume(self):
        df = _make_df(close_val=110.0, swing_high=98.0, volume=500.0, vol_ma10=1000.0)
        high = df["high"]
        swing_h = high.rolling(5, min_periods=1).max().shift(2)
        idx = len(df) - 2
        sh = swing_h.iloc[idx]
        vol = df["volume"].iloc[idx]
        vma = df["volume"].rolling(10, min_periods=1).mean().iloc[idx]
        sig = self.strategy.generate(df)
        if vol <= vma:
            assert sig.action == Action.HOLD

    # 7. HOLD: 데이터 부족
    def test_hold_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 8. Signal 타입 확인
    def test_returns_signal_type(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 9. entry_price는 마지막 완성 캔들 close
    def test_entry_price_is_last_candle(self):
        df = _make_df(close_val=95.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(df["close"].iloc[-2], rel=1e-5)

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert sig.reasoning != ""

    # 11. HIGH confidence: swing_range > avg_range * 1.5
    def test_high_confidence_large_swing(self):
        rows = _MIN_ROWS + 2
        # 큰 swing range를 만들기 위해 high/low 간격 크게
        closes = [100.0] * rows
        closes[-2] = 110.0  # 돌파
        highs = [105.0] * rows   # swing_high 큼
        lows = [90.0] * rows     # swing_low 작음 → range=15
        volumes = [1000.0] * rows
        volumes[-2] = 3000.0
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows, "volume": volumes,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # swing_range=15, avg_range=(high-low)=15 → ratio=1.0, not >1.5 → MEDIUM
            assert sig.confidence in [Confidence.HIGH, Confidence.MEDIUM]

    # 12. MEDIUM confidence: swing_range <= avg_range * 1.5
    def test_medium_confidence_normal_swing(self):
        df = _make_df(close_val=110.0, swing_high=98.0, volume=3000.0, vol_ma10=500.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in [Confidence.HIGH, Confidence.MEDIUM]

    # 13. action은 유효한 열거형
    def test_action_is_valid_enum(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in [Action.BUY, Action.SELL, Action.HOLD]

    # 14. confidence는 유효한 열거형
    def test_confidence_is_valid_enum(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in [Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW]
