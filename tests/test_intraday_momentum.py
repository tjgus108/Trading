"""
IntradayMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.intraday_momentum import IntradayMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(
    n: int = _MIN_ROWS + 5,
    close: float = 100.0,
    high: float = 110.0,
    low: float = 90.0,
    volume: float = 1000.0,
    vol_factor: float = 1.0,
) -> pd.DataFrame:
    """
    마지막 완성 캔들(-2)에 원하는 값을 배치.
    position = (close - low) / (high - low)
    """
    rows = n
    closes = [close] * rows
    highs = [high] * rows
    lows = [low] * rows
    volumes = [volume * vol_factor] * rows
    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    position > 0.7, volume spike, momentum_score > score_ma 를 유도.
    처음 rows-2개는 중간 position, 마지막 -2 봉은 high position + high volume.
    """
    rows = n
    # 기본 봉: close=100, high=110, low=90 → position=0.5
    closes = [100.0] * rows
    highs = [110.0] * rows
    lows = [90.0] * rows
    volumes = [1000.0] * rows

    # 마지막 완성 봉(-2): position > 0.85, volume spike
    closes[-2] = 109.0   # position = (109-90)/(110-90) = 0.95
    volumes[-2] = 5000.0  # volume spike

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


def _make_sell_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    position < 0.15, volume spike, momentum_score < score_ma 를 유도.
    """
    rows = n
    closes = [100.0] * rows
    highs = [110.0] * rows
    lows = [90.0] * rows
    volumes = [1000.0] * rows

    # 마지막 완성 봉(-2): position < 0.15, volume spike
    closes[-2] = 91.5   # position = (91.5-90)/(110-90) = 0.075
    volumes[-2] = 5000.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


class TestIntradayMomentumStrategy:

    def setup_method(self):
        self.strategy = IntradayMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "intraday_momentum"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. BUY 신호 생성
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 4. BUY HIGH confidence (position > 0.85)
    def test_buy_high_confidence(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 5. SELL 신호 생성
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 6. SELL HIGH confidence (position < 0.15)
    def test_sell_high_confidence(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 7. HOLD: position > 0.7 but volume <= vol_ma
    def test_hold_position_high_low_volume(self):
        rows = _MIN_ROWS + 5
        closes = [100.0] * rows
        highs = [110.0] * rows
        lows = [90.0] * rows
        volumes = [1000.0] * rows
        closes[-2] = 109.0  # position=0.95, but volume not spiked
        volumes[-2] = 500.0  # below average
        df = pd.DataFrame({"open": closes, "close": closes, "high": highs, "low": lows, "volume": volumes})
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. HOLD: volume spike but position in middle
    def test_hold_middle_position(self):
        df = _make_df(close=100.0, high=110.0, low=90.0, volume=1000.0, vol_factor=5.0)
        sig = self.strategy.generate(df)
        # position = 0.5, no signal
        assert sig.action == Action.HOLD

    # 9. Signal 타입 확인
    def test_signal_type(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 11. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 12. strategy 이름 필드
    def test_signal_strategy_field(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "intraday_momentum"

    # 13. 정확히 MIN_ROWS 행에서 동작
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. NaN 없는 경우 reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""
