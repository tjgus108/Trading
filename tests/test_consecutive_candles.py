"""
ConsecutiveCandlesStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.consecutive_candles import ConsecutiveCandlesStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 15
_MIN_COUNT = 4
_HIGH_CONF_COUNT = 6


def _make_df(n: int, opens, closes, volumes=None) -> pd.DataFrame:
    if volumes is None:
        volumes = [1000.0] * n
    highs = [max(o, c) + 0.5 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 0.5 for o, c in zip(opens, closes)]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": closes,
        "atr14": [1.0] * n,
    })


def _make_bull_df(n: int = _MIN_ROWS + 1, count: int = 4,
                  vol_increasing: bool = True) -> pd.DataFrame:
    """
    count봉 연속 양봉 + volume 증가 설계.
    마지막 완성 캔들 = idx = n-2.
    연속 양봉: idx-count+1 ~ idx
    """
    opens = [100.0] * n
    closes = [100.0] * n
    volumes = [1000.0] * n

    idx = n - 2
    start = idx - count + 1
    for i in range(start, idx + 1):
        opens[i] = 100.0
        closes[i] = 101.0  # 양봉
        if vol_increasing:
            volumes[i] = 1000.0 + (i - start + 1) * 100  # 단조 증가
        else:
            volumes[i] = 1000.0  # flat

    # 연속 끊기: start-1 봉을 음봉으로
    if start > 0:
        opens[start - 1] = 101.0
        closes[start - 1] = 99.0  # 음봉

    return _make_df(n, opens, closes, volumes)


def _make_bear_df(n: int = _MIN_ROWS + 1, count: int = 4,
                  vol_increasing: bool = True) -> pd.DataFrame:
    """
    count봉 연속 음봉 + volume 증가 설계.
    """
    opens = [100.0] * n
    closes = [100.0] * n
    volumes = [1000.0] * n

    idx = n - 2
    start = idx - count + 1
    for i in range(start, idx + 1):
        opens[i] = 101.0
        closes[i] = 100.0  # 음봉
        if vol_increasing:
            volumes[i] = 1000.0 + (i - start + 1) * 100
        else:
            volumes[i] = 1000.0

    if start > 0:
        opens[start - 1] = 99.0
        closes[start - 1] = 101.0  # 양봉

    return _make_df(n, opens, closes, volumes)


class TestConsecutiveCandlesStrategy:

    def setup_method(self):
        self.strategy = ConsecutiveCandlesStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "consecutive_candles"

    # 2. BUY 신호 (4봉 연속 양봉 + volume 증가)
    def test_buy_signal(self):
        df = _make_bull_df(count=4)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "consecutive_candles"

    # 3. BUY MEDIUM confidence (4~5봉)
    def test_buy_medium_confidence(self):
        df = _make_bull_df(count=4)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 4. BUY HIGH confidence (6봉 이상)
    def test_buy_high_confidence(self):
        df = _make_bull_df(n=_MIN_ROWS + 5, count=6)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. SELL 신호 (4봉 연속 음봉 + volume 증가)
    def test_sell_signal(self):
        df = _make_bear_df(count=4)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "consecutive_candles"

    # 6. SELL MEDIUM confidence (4~5봉)
    def test_sell_medium_confidence(self):
        df = _make_bear_df(count=4)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 7. SELL HIGH confidence (6봉 이상)
    def test_sell_high_confidence(self):
        df = _make_bear_df(n=_MIN_ROWS + 5, count=6)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. HOLD: 4봉 양봉이지만 volume 증가 없음
    def test_hold_bull_no_volume_increase(self):
        df = _make_bull_df(count=4, vol_increasing=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: 4봉 음봉이지만 volume 증가 없음
    def test_hold_bear_no_volume_increase(self):
        df = _make_bear_df(count=4, vol_increasing=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: 3봉 연속 양봉 (조건 미달)
    def test_hold_bull_only_3_candles(self):
        df = _make_bull_df(count=3)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: 3봉 연속 음봉 (조건 미달)
    def test_hold_bear_only_3_candles(self):
        df = _make_bear_df(count=3)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. 데이터 부족 (< 15행)
    def test_insufficient_data(self):
        rows = 10
        opens = [100.0] * rows
        closes = [101.0] * rows
        df = _make_df(rows, opens, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_bull_df(count=4)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "consecutive_candles"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 14. BUY reasoning에 연속 봉 정보 포함
    def test_buy_reasoning_contains_candle_info(self):
        df = _make_bull_df(count=4)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "양봉" in sig.reasoning or "BUY" in sig.reasoning

    # 15. SELL reasoning에 연속 봉 정보 포함
    def test_sell_reasoning_contains_candle_info(self):
        df = _make_bear_df(count=4)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "음봉" in sig.reasoning or "SELL" in sig.reasoning
