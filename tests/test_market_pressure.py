"""
MarketPressureStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.market_pressure import MarketPressureStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def make_buy_df(n: int = _MIN_ROWS + 1) -> pd.DataFrame:
    """pressure_diff > 0.2: close near high, volume high."""
    rows = n
    closes = [100.0] * rows
    highs = [110.0] * rows
    lows = [100.0] * rows
    volumes = [500.0] * rows

    # 신호 봉(-2): close near high → buying pressure dominates
    closes[-2] = 109.0  # close near high=110, low=100 → buy_ratio=(109-100)/10=0.9, sell=(110-109)/10=0.1, diff=0.8
    highs[-2] = 110.0
    lows[-2] = 100.0
    volumes[-2] = 2000.0  # well above vol_ma (~500)

    # 앞 봉들도 약간 매수 우세로 (pressure_trend > pressure_ma 조건)
    for i in range(max(0, rows - 5), rows - 2):
        closes[i] = 107.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


def make_sell_df(n: int = _MIN_ROWS + 1) -> pd.DataFrame:
    """
    pressure_diff < -0.2, pressure_trend < pressure_ma, volume > vol_ma.
    Strategy: earlier rows neutral (close=mid), recent rows drop toward low.
    - Earlier rows: close=105 (mid of 100-110) → diff≈0 → pressure_ma ≈ 0
    - Recent 3 rows before signal: close=102 → diff≈-0.8
    - Signal candle (-2): close=101 → diff≈-0.8
    → pressure_trend ≈ -0.8 < pressure_ma ≈ -0.24 (mix of 0s and -0.8s)
    Wait - need trend < ma, so pressure_ma must be HIGHER (less negative) than trend.
    Design: most earlier rows neutral (diff≈0), recent rows (incl signal) very negative.
    pressure_ma = mean of 10 values: ~7 neutral (0) + 3 negative (-0.8) = -0.24
    pressure_trend = mean of last 3 = -0.8
    → -0.8 < -0.24 ✓
    """
    rows = n
    closes = [105.0] * rows  # mid of range → diff≈0
    highs = [110.0] * rows
    lows = [100.0] * rows
    volumes = [500.0] * rows

    # Last 5 rows before signal: shift toward low
    for i in range(max(0, rows - 6), rows - 1):
        closes[i] = 102.0  # diff≈-0.8

    # 신호 봉(-2): close near low
    closes[-2] = 101.0
    highs[-2] = 110.0
    lows[-2] = 100.0
    volumes[-2] = 2000.0  # well above vol_ma

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


class TestMarketPressureStrategy:

    def setup_method(self):
        self.strategy = MarketPressureStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "market_pressure"

    # 2. BUY 신호
    def test_buy_signal(self):
        df = make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "market_pressure"

    # 3. BUY HIGH confidence: |pressure_diff| > 0.4
    def test_buy_high_confidence(self):
        df = make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH  # diff=0.8 > 0.4

    # 4. SELL 신호
    def test_sell_signal(self):
        df = make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "market_pressure"

    # 5. SELL HIGH confidence
    def test_sell_high_confidence(self):
        df = make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 6. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        rows = 10
        df = pd.DataFrame({
            "open": [100.0] * rows,
            "close": [100.0] * rows,
            "high": [105.0] * rows,
            "low": [95.0] * rows,
            "volume": [1000.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 7. HOLD: 중립 압력 (pressure_diff ≈ 0)
    def test_hold_neutral_pressure(self):
        rows = _MIN_ROWS + 1
        closes = [100.0] * rows
        highs = [110.0] * rows
        lows = [90.0] * rows
        volumes = [1000.0] * rows
        # close at midpoint → diff ≈ 0
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows, "volume": volumes,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. HOLD: 매수 조건이지만 volume < vol_ma
    def test_hold_buy_low_volume(self):
        rows = _MIN_ROWS + 1
        closes = [109.0] * rows
        highs = [110.0] * rows
        lows = [100.0] * rows
        # 낮은 volume: rolling mean >> current volume
        volumes = [2000.0] * rows
        volumes[-2] = 100.0  # 신호 봉 volume 낮음

        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows, "volume": volumes,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. entry_price는 close 값
    def test_entry_price_is_close(self):
        df = make_buy_df()
        sig = self.strategy.generate(df)
        # 신호 봉의 close = 109.0
        assert sig.entry_price == pytest.approx(109.0)

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ["action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"]:
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 11. HOLD 신호 필드 완전성
    def test_hold_signal_fields(self):
        rows = 10
        df = pd.DataFrame({
            "open": [100.0] * rows, "close": [100.0] * rows,
            "high": [105.0] * rows, "low": [95.0] * rows,
            "volume": [1000.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 12. SELL entry_price는 close 값
    def test_sell_entry_price(self):
        df = make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(101.0)

    # 13. SELL reasoning에 키워드 포함
    def test_sell_reasoning_keyword(self):
        df = make_sell_df()
        sig = self.strategy.generate(df)
        assert "pressure_diff" in sig.reasoning or "매도" in sig.reasoning

    # 14. BUY reasoning에 키워드 포함
    def test_buy_reasoning_keyword(self):
        df = make_buy_df()
        sig = self.strategy.generate(df)
        assert "pressure_diff" in sig.reasoning or "매수" in sig.reasoning

    # 15. 정확히 MIN_ROWS 행에서 동작
    def test_exactly_min_rows(self):
        df = make_buy_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert sig.action in [Action.BUY, Action.HOLD, Action.SELL]
