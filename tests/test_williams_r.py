"""
WilliamsRStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

from typing import Optional

import numpy as np
import pandas as pd
import pytest

from src.strategy.williams_r import WilliamsRStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20
_PERIOD = 14


def _make_df(n: int = _MIN_ROWS + 5,
             close: float = 100.0,
             high: float = 110.0,
             low: float = 90.0,
             prev_wr: Optional[float] = None) -> pd.DataFrame:
    """
    %R = (highest_high_14 - close) / (highest_high_14 - lowest_low_14) * -100
    기본적으로 균일한 OHLCV를 생성하되 마지막 2개 봉만 신호 조건 제어.

    prev_wr 를 지정하면 -3 봉의 %R 을 해당 값으로 근사하도록 high/low를 조정한다.
    """
    rows = n
    highs = [high] * rows
    lows = [low] * rows
    closes = [close] * rows
    df = pd.DataFrame({
        "open": [close] * rows,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * rows,
        "ema50": [close] * rows,
        "atr14": [1.0] * rows,
    })
    return df


def _make_buy_df(curr_wr: float = -85.0, prev_wr_val: float = -88.0,
                 n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    curr_wr < -80 AND curr_wr > prev_wr (반등) 조건을 정확히 맞춘 DataFrame.
    14봉 고가/저가를 고정하고 close 만 변경하여 %R 을 제어한다.
      %R = (HH14 - close) / (HH14 - LL14) * -100
      => close = HH14 - %R / -100 * (HH14 - LL14)
    HH14=110, LL14=90 → range=20
    """
    hh, ll = 110.0, 90.0
    rng = hh - ll

    close_curr = hh - (curr_wr / -100) * rng    # 마지막 완성 봉 (-2)
    close_prev = hh - (prev_wr_val / -100) * rng  # 그 직전 봉 (-3)

    rows = n
    highs = [hh] * rows
    lows = [ll] * rows
    closes = [close_curr] * rows
    closes[-3] = close_prev   # -3 위치: prev 봉
    closes[-2] = close_curr   # -2 위치: curr 봉 (BaseStrategy._last)
    df = pd.DataFrame({
        "open": closes[:],
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * rows,
        "ema50": [close_curr] * rows,
        "atr14": [1.0] * rows,
    })
    return df


def _make_sell_df(curr_wr: float = -15.0, prev_wr_val: float = -12.0,
                  n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """curr_wr > -20 AND curr_wr < prev_wr (반락)"""
    hh, ll = 110.0, 90.0
    rng = hh - ll
    close_curr = hh - (curr_wr / -100) * rng
    close_prev = hh - (prev_wr_val / -100) * rng
    rows = n
    closes = [close_curr] * rows
    closes[-3] = close_prev
    closes[-2] = close_curr
    df = pd.DataFrame({
        "open": closes[:],
        "close": closes,
        "high": [hh] * rows,
        "low": [ll] * rows,
        "volume": [1000.0] * rows,
        "ema50": [close_curr] * rows,
        "atr14": [1.0] * rows,
    })
    return df


class TestWilliamsRStrategy:

    def setup_method(self):
        self.strategy = WilliamsRStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "williams_r"

    # 2. BUY 신호: %R < -80, 반등
    def test_buy_signal(self):
        df = _make_buy_df(curr_wr=-85.0, prev_wr_val=-88.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "williams_r"

    # 3. BUY HIGH confidence: %R < -90
    def test_buy_high_confidence(self):
        df = _make_buy_df(curr_wr=-92.0, prev_wr_val=-95.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 4. BUY MEDIUM confidence: -90 <= %R < -80
    def test_buy_medium_confidence(self):
        df = _make_buy_df(curr_wr=-83.0, prev_wr_val=-86.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 5. SELL 신호: %R > -20, 반락
    def test_sell_signal(self):
        df = _make_sell_df(curr_wr=-15.0, prev_wr_val=-12.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "williams_r"

    # 6. SELL HIGH confidence: %R > -10
    def test_sell_high_confidence(self):
        df = _make_sell_df(curr_wr=-5.0, prev_wr_val=-2.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. SELL MEDIUM confidence: -20 < %R <= -10
    def test_sell_medium_confidence(self):
        df = _make_sell_df(curr_wr=-15.0, prev_wr_val=-12.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 8. HOLD: %R < -80 BUT 하락 중 (반등 아님)
    def test_hold_oversold_still_falling(self):
        # curr_wr < prev_wr → 반등 아니므로 HOLD
        df = _make_buy_df(curr_wr=-88.0, prev_wr_val=-85.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: %R > -20 BUT 상승 중 (반락 아님)
    def test_hold_overbought_still_rising(self):
        # curr_wr > prev_wr → 반락 아니므로 HOLD
        df = _make_sell_df(curr_wr=-12.0, prev_wr_val=-15.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: 중립 구간 (-80 <= %R <= -20)
    def test_hold_neutral_zone(self):
        df = _make_buy_df(curr_wr=-50.0, prev_wr_val=-55.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 12. Signal 필드 완전성 확인
    def test_signal_fields_complete(self):
        df = _make_buy_df(curr_wr=-85.0, prev_wr_val=-88.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 13. entry_price 는 현재 close
    def test_entry_price_is_close(self):
        df = _make_buy_df(curr_wr=-85.0, prev_wr_val=-88.0)
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_close, rel=1e-3)
