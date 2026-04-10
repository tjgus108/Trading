"""
CandleBodyFilterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.candle_body_filter import CandleBodyFilterStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(n: int, opens, closes, highs=None, lows=None, volumes=None) -> pd.DataFrame:
    if volumes is None:
        volumes = [1000.0] * n
    if highs is None:
        highs = [max(o, c) + 0.1 for o, c in zip(opens, closes)]
    if lows is None:
        lows = [min(o, c) - 0.1 for o, c in zip(opens, closes)]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": closes,
        "atr14": [1.0] * n,
    })


def _make_strong_bull_df(n: int = _MIN_ROWS + 2, streak: int = 2,
                         vol_above_ma: bool = True) -> pd.DataFrame:
    """
    강한 양봉(body_ratio > 0.6) streak봉 설계.
    idx = n-2 (마지막 완성 캔들)
    streak봉: idx-(streak-1) ~ idx 모두 강한 양봉
    vol_ma는 rolling(10): streak봉에만 높은 volume으로도 ma를 넘게 설계
    """
    opens = [100.0] * n
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    volumes = [200.0] * n  # 기본 낮은 vol

    idx = n - 2
    start = max(0, idx - streak + 1)

    # streak봉 전체를 강한 양봉으로 설정 (close 단계적 상승으로 close > close.shift(1) 보장)
    base_close = 100.0
    for i in range(start, idx + 1):
        step = i - start
        opens[i] = base_close + step * 1.0
        closes[i] = base_close + step * 1.0 + 0.9  # body = 0.9, total_range = 1.0
        highs[i] = closes[i] + 0.05
        lows[i] = opens[i] - 0.05
        if vol_above_ma:
            volumes[i] = 5000.0  # vol_ma(200) 대비 충분히 큰 값

    return _make_df(n, opens, closes, highs, lows, volumes)


def _make_strong_bear_df(n: int = _MIN_ROWS + 2, streak: int = 2,
                         vol_above_ma: bool = True) -> pd.DataFrame:
    """
    강한 음봉(body_ratio > 0.6) streak봉 설계.
    """
    opens = [100.0] * n
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    volumes = [200.0] * n

    idx = n - 2
    start = max(0, idx - streak + 1)

    base_open = 110.0
    for i in range(start, idx + 1):
        step = i - start
        opens[i] = base_open - step * 1.0
        closes[i] = base_open - step * 1.0 - 0.9  # body = 0.9, total_range ≈ 1.0
        highs[i] = opens[i] + 0.05
        lows[i] = closes[i] - 0.05
        if vol_above_ma:
            volumes[i] = 5000.0

    return _make_df(n, opens, closes, highs, lows, volumes)


class TestCandleBodyFilterStrategy:

    def setup_method(self):
        self.strategy = CandleBodyFilterStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "candle_body_filter"

    # 2. BUY 신호 (streak=2, vol 확인)
    def test_buy_signal_streak2(self):
        df = _make_strong_bull_df(streak=2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 3. BUY MEDIUM confidence (streak=2)
    def test_buy_medium_confidence(self):
        df = _make_strong_bull_df(streak=2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 4. BUY HIGH confidence (streak=3)
    def test_buy_high_confidence_streak3(self):
        df = _make_strong_bull_df(streak=3)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. SELL 신호 (streak=2, vol 확인)
    def test_sell_signal_streak2(self):
        df = _make_strong_bear_df(streak=2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 6. SELL MEDIUM confidence (streak=2)
    def test_sell_medium_confidence(self):
        df = _make_strong_bear_df(streak=2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 7. SELL HIGH confidence (streak=3)
    def test_sell_high_confidence_streak3(self):
        df = _make_strong_bear_df(streak=3)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. HOLD: 강한 양봉이지만 volume 부족
    def test_hold_bull_low_volume(self):
        df = _make_strong_bull_df(streak=2, vol_above_ma=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: 강한 음봉이지만 volume 부족
    def test_hold_bear_low_volume(self):
        df = _make_strong_bear_df(streak=2, vol_above_ma=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        n = 15
        opens = [100.0] * n
        closes = [101.0] * n
        df = _make_df(n, opens, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_strong_bull_df(streak=2)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "candle_body_filter"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 12. BUY reasoning에 관련 정보 포함
    def test_buy_reasoning_info(self):
        df = _make_strong_bull_df(streak=2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "BUY" in sig.reasoning

    # 13. SELL reasoning에 관련 정보 포함
    def test_sell_reasoning_info(self):
        df = _make_strong_bear_df(streak=2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "SELL" in sig.reasoning

    # 14. HOLD: streak=1 (조건 미달)
    def test_hold_streak1(self):
        n = _MIN_ROWS + 2
        opens = [100.0] * n
        closes = [100.0] * n
        highs = [101.0] * n
        lows = [99.0] * n
        volumes = [2000.0] * n
        idx = n - 2
        opens[idx] = 100.0
        closes[idx] = 100.9
        highs[idx] = 101.0
        lows[idx] = 100.0
        closes[idx - 1] = 100.0
        df = _make_df(n, opens, closes, highs, lows, volumes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. entry_price는 마지막 완성 캔들의 close
    def test_entry_price_is_last_close(self):
        df = _make_strong_bull_df(streak=2)
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[len(df) - 2])
        assert sig.entry_price == pytest.approx(expected_close)
