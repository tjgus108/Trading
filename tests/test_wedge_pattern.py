"""
WedgePatternStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.wedge_pattern import WedgePatternStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n, closes=None, highs=None, lows=None, volumes=None):
    if closes is None:
        closes = np.ones(n) * 100.0
    if highs is None:
        highs = np.array(closes) * 1.005
    if lows is None:
        lows = np.array(closes) * 0.995
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_falling_wedge_buy_df():
    """
    Falling wedge + close > recent 5봉 최고가 → BUY.
    high_slope < 0, low_slope < 0, high_slope < low_slope (상단이 더 가팔름).
    마지막 완성봉(iloc[-2])의 close가 5봉 최고가 초과.
    """
    n = 30
    # 고점은 급격히 하락, 저점은 완만히 하락 → high_slope < low_slope (둘 다 음수)
    x = np.arange(n)
    # 예: high = 110 - 0.4*x, low = 100 - 0.2*x
    highs = 110.0 - 0.4 * x
    lows  = 100.0 - 0.2 * x

    # 중간 close는 낮게 설정 (recent 5봉 최고가가 낮도록)
    closes = (highs + lows) / 2.0

    # 마지막 완성봉(iloc[-2])의 close를 5봉 최고가보다 크게 설정
    # 5봉 = iloc[-6:-1] 의 high
    recent5_high = float(highs[-6:-1].max())
    closes[-2] = recent5_high + 5.0  # 돌파

    return _make_df(n, closes=closes, highs=highs, lows=lows)


def _make_rising_wedge_sell_df():
    """
    Rising wedge + close < recent 5봉 최저가 → SELL.
    high_slope > 0, low_slope > 0, low_slope > high_slope (하단이 더 가팔름).
    마지막 완성봉(iloc[-2])의 close가 5봉 최저가 미만.
    """
    n = 30
    x = np.arange(n)
    # 저점은 급격히 상승, 고점은 완만히 상승 → low_slope > high_slope
    highs = 100.0 + 0.2 * x
    lows  = 90.0  + 0.4 * x

    closes = (highs + lows) / 2.0

    # 마지막 완성봉(iloc[-2])의 close를 5봉 최저가보다 작게 설정
    recent5_low = float(lows[-6:-1].min())
    closes[-2] = recent5_low - 5.0  # 이탈

    return _make_df(n, closes=closes, highs=highs, lows=lows)


def _make_flat_df(n=30):
    """패턴 없는 평탄 데이터 → HOLD."""
    closes = np.ones(n) * 100.0
    return _make_df(n, closes=closes)


# ── tests ──────────────────────────────────────────────────────────────────────

class TestWedgePatternStrategy:

    def setup_method(self):
        self.strategy = WedgePatternStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "wedge_pattern"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → Confidence.LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_df(20)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_df(20)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 최소 행 정확히 25행 → Signal 반환
    def test_exactly_min_rows(self):
        df = _make_df(25)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 6. 평탄 데이터 → HOLD
    def test_flat_data_hold(self):
        df = _make_flat_df(30)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 7. Falling wedge + 돌파 → BUY
    def test_falling_wedge_buy(self):
        df = _make_falling_wedge_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 8. Rising wedge + 이탈 → SELL
    def test_rising_wedge_sell(self):
        df = _make_rising_wedge_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 9. BUY signal - entry_price 양수
    def test_buy_entry_price_positive(self):
        df = _make_falling_wedge_buy_df()
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 10. SELL signal - entry_price 양수
    def test_sell_entry_price_positive(self):
        df = _make_rising_wedge_sell_df()
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 11. Signal 필드 완전성 (HOLD)
    def test_signal_fields_complete(self):
        df = _make_flat_df(30)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "wedge_pattern"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0

    # 12. BUY reasoning에 "Falling" 포함
    def test_buy_reasoning_contains_falling(self):
        df = _make_falling_wedge_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY
        assert "Falling" in signal.reasoning or "falling" in signal.reasoning.lower()

    # 13. SELL reasoning에 "Rising" 포함
    def test_sell_reasoning_contains_rising(self):
        df = _make_rising_wedge_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL
        assert "Rising" in signal.reasoning or "rising" in signal.reasoning.lower()

    # 14. 수렴 각도 > 0.5 → HIGH confidence (falling wedge)
    def test_high_confidence_large_convergence(self):
        n = 30
        x = np.arange(n)
        # high_slope ≈ -1.0, low_slope ≈ -0.1 → convergence ≈ 0.9 > 0.5
        highs = 110.0 - 1.0 * x
        lows  = 100.0 - 0.1 * x
        closes = (highs + lows) / 2.0
        recent5_high = float(highs[-6:-1].max())
        closes[-2] = recent5_high + 5.0
        df = _make_df(n, closes=closes, highs=highs, lows=lows)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 15. Falling wedge but no breakout → HOLD
    def test_falling_wedge_no_breakout_hold(self):
        n = 30
        x = np.arange(n)
        highs = 110.0 - 0.4 * x
        lows  = 100.0 - 0.2 * x
        closes = (highs + lows) / 2.0
        # 마지막 완성봉을 5봉 최고가보다 낮게 설정
        recent5_high = float(highs[-6:-1].max())
        closes[-2] = recent5_high - 2.0  # 돌파 안 함
        df = _make_df(n, closes=closes, highs=highs, lows=lows)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 16. BUY invalidation 존재
    def test_buy_invalidation_present(self):
        df = _make_falling_wedge_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 17. SELL invalidation 존재
    def test_sell_invalidation_present(self):
        df = _make_rising_wedge_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0
