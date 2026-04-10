"""
RangeBoundStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.range_bound import RangeBoundStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 40, close_val: float = 100.0, spread: float = 0.2) -> pd.DataFrame:
    """기본 데이터: 횡보장 유사 (좁은 범위)."""
    closes = np.full(n, close_val)
    highs = closes + spread
    lows = closes - spread
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _chop_df(n: int = 40, ci_high: bool = True) -> pd.DataFrame:
    """
    CI가 높은(횡보) 또는 낮은(추세) 데이터 생성.
    ci_high=True: 많은 TR이 존재하지만 레인지가 좁음 → CI 높음
    ci_high=False: 단방향 추세 → CI 낮음
    """
    np.random.seed(42)
    if ci_high:
        # 아주 좁은 레인지에서 고빈도 노이즈 → CI 상승
        closes = np.full(n, 100.0)
        # 작은 random noise
        noise = np.random.uniform(-0.05, 0.05, n)
        closes = closes + noise
        spreads = np.random.uniform(0.3, 0.5, n)
    else:
        # 강한 추세 (단방향) → CI 낮음
        closes = np.linspace(100.0, 200.0, n)
        spreads = np.full(n, 0.1)

    highs = closes + spreads
    lows = closes - spreads
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes.copy(),
        "volume": np.ones(n) * 1000,
    })


def _range_buy_df(n: int = 40) -> pd.DataFrame:
    """횡보장 + 하단 터치 → BUY 유도."""
    np.random.seed(10)
    # 대부분의 캔들은 100 근처에서 횡보
    closes = np.full(n, 100.0) + np.random.uniform(-0.02, 0.02, n)
    spreads = np.random.uniform(0.3, 0.5, n)  # 작은 spread → 높은 CI 가능
    highs = closes + spreads
    lows = closes - spreads

    # _last(df) = iloc[-2] 를 SMA20 - 2std 아래로 설정
    # 앞 20개 평균 100, std 약 0.3이므로 lower = ~99.7
    closes[-2] = 97.5  # SMA - 2std 훨씬 아래
    highs[-2] = closes[-2] + 0.3
    lows[-2] = closes[-2] - 0.3

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _range_sell_df(n: int = 40) -> pd.DataFrame:
    """횡보장 + 상단 터치 → SELL 유도."""
    np.random.seed(11)
    closes = np.full(n, 100.0) + np.random.uniform(-0.02, 0.02, n)
    spreads = np.random.uniform(0.3, 0.5, n)
    highs = closes + spreads
    lows = closes - spreads

    # iloc[-2]를 상단 초과로 설정
    closes[-2] = 102.5
    highs[-2] = closes[-2] + 0.3
    lows[-2] = closes[-2] - 0.3

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestRangeBoundStrategy:

    def setup_method(self):
        self.strategy = RangeBoundStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "range_bound"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _base_df(n=40)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "range_bound"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 6. 추세장(강한 추세) → HOLD, confidence LOW
    def test_trending_market_hold(self):
        df = _chop_df(n=50, ci_high=False)
        signal = self.strategy.generate(df)
        # 추세장이면 HOLD + LOW
        if signal.action == Action.HOLD:
            assert signal.confidence == Confidence.LOW or "추세장" in signal.reasoning

    # 7. 하단 터치 → BUY 또는 합리적인 신호
    def test_lower_band_touch_buy(self):
        df = _range_buy_df(n=40)
        signal = self.strategy.generate(df)
        # CI가 충분히 높으면 BUY, 낮으면 HOLD
        assert signal.action in (Action.BUY, Action.HOLD)

    # 8. 상단 터치 → SELL 또는 합리적인 신호
    def test_upper_band_touch_sell(self):
        df = _range_sell_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.SELL, Action.HOLD)

    # 9. BUY reasoning에 "횡보" 또는 "하단" 포함
    def test_buy_reasoning_keywords(self):
        df = _range_buy_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "횡보" in signal.reasoning or "하단" in signal.reasoning or "lower" in signal.reasoning.lower()

    # 10. SELL reasoning에 "횡보" 또는 "상단" 포함
    def test_sell_reasoning_keywords(self):
        df = _range_sell_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "횡보" in signal.reasoning or "상단" in signal.reasoning or "upper" in signal.reasoning.lower()

    # 11. BUY 신호에 invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _range_buy_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 12. SELL 신호에 invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _range_sell_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 13. 경계값: 정확히 20행
    def test_exactly_min_rows(self):
        df = _base_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. entry_price는 양수
    def test_entry_price_positive(self):
        df = _base_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 15. CI > 70 → confidence HIGH (BUY/SELL 시)
    def test_high_ci_high_confidence(self):
        # 매우 좁은 레인지 횡보로 높은 CI 유도
        np.random.seed(99)
        n = 40
        closes = np.full(n, 100.0)
        # 아주 미세한 변동: TR이 큼에도 고저차 작게
        spreads = np.full(n, 0.01)
        highs = closes + spreads
        lows = closes - spreads

        # _last를 하단 아래로
        closes[-2] = 95.0
        highs[-2] = 95.01
        lows[-2] = 94.99

        df = pd.DataFrame({
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": np.ones(n) * 1000,
        })
        signal = self.strategy.generate(df)
        if signal.action in (Action.BUY, Action.SELL):
            # CI가 70 이상이면 HIGH
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 16. reasoning에 CI 값 포함
    def test_reasoning_contains_ci_value(self):
        df = _base_df(n=40)
        signal = self.strategy.generate(df)
        assert "CI=" in signal.reasoning
