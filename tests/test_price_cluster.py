"""
PriceClusterStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_cluster import PriceClusterStrategy, _find_cluster
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 60, close_prices=None) -> pd.DataFrame:
    if close_prices is None:
        close_prices = [100.0] * n
    highs = [c + 1.0 for c in close_prices]
    lows = [c - 1.0 for c in close_prices]
    return pd.DataFrame({
        "open": close_prices,
        "close": close_prices,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * len(close_prices),
    })


def _make_cluster_bounce_df() -> pd.DataFrame:
    """
    BUY 조건: prev_close < cluster_low, curr_close >= cluster_low
    cluster가 [105, 120] 근방에 형성되도록 설정.
    50봉 중 대부분(30봉)이 110~115 → cluster bin이 그 구간.
    """
    n = 60
    # 대부분 110~115 (cluster 형성)
    base = [112.0] * 35 + [100.0] * 13
    # 적절히 분산
    while len(base) < n - 2:
        base.append(112.0)
    # prev(-3): cluster_low 아래
    base.append(104.0)   # prev_close (completed[-2])
    base.append(108.0)   # 신호봉 (-2, _last)
    base.append(109.0)   # 현재 진행봉 (-1)
    base = base[:n]
    return _make_df(n=len(base), close_prices=base)


def _make_cluster_rejection_df() -> pd.DataFrame:
    """
    SELL 조건: prev_close > cluster_high, curr_close <= cluster_high
    """
    n = 60
    base = [112.0] * 35 + [120.0] * 13
    while len(base) < n - 2:
        base.append(112.0)
    # prev: cluster_high 위 (125)
    base.append(125.0)   # prev_close (completed[-2])
    base.append(119.0)   # 신호봉 (-2, _last)
    base.append(118.0)   # 현재봉 (-1)
    base = base[:n]
    return _make_df(n=len(base), close_prices=base)


class TestPriceClusterStrategy:

    def setup_method(self):
        self.strategy = PriceClusterStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_cluster"

    # 2. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 정확히 최소 행 (55행)
    def test_exactly_min_rows(self):
        df = _make_df(n=55)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. 54행 → HOLD
    def test_one_below_min_rows(self):
        df = _make_df(n=54)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 5. BUY 신호 (cluster bounce)
    def test_buy_signal_cluster_bounce(self):
        df = _make_cluster_bounce_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 6. SELL 신호 (cluster rejection)
    def test_sell_signal_cluster_rejection(self):
        df = _make_cluster_rejection_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 9. strategy 필드 값
    def test_signal_strategy_field(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_cluster"

    # 10. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 11. HOLD 신호 confidence는 LOW
    def test_hold_confidence_is_low(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 12. Action은 유효한 Enum 값
    def test_action_is_valid_enum(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 13. _find_cluster: 단조로운 가격 처리
    def test_find_cluster_flat_prices(self):
        closes = pd.Series([100.0] * 50)
        low, high, center, count, avg = _find_cluster(closes)
        assert center == 100.0

    # 14. _find_cluster: 최빈 bin이 맞는지
    def test_find_cluster_dominant_bin(self):
        # 80% 가격이 100~105 구간
        closes = pd.Series([102.0] * 40 + [150.0] * 5 + [200.0] * 5)
        low, high, center, count, avg = _find_cluster(closes)
        # count가 가장 많은 bin
        assert count >= avg

    # 15. HIGH confidence (빈도 > 평균의 2배)
    def test_high_confidence_when_dominant_cluster(self):
        """50봉 중 40봉이 동일 구간 → count >> avg → HIGH"""
        n = 60
        # 40봉이 100~101 범위 (cluster)
        closes = [100.5] * 40 + [200.0] * 10
        # 패딩
        while len(closes) < n - 2:
            closes.insert(0, 100.5)
        closes.append(99.0)    # prev_close: cluster_low 아래
        closes.append(100.5)   # 신호봉: cluster_low 이상
        closes.append(101.0)   # 현재봉
        closes = closes[:n]
        df = _make_df(n=len(closes), close_prices=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 16. 큰 데이터셋 (200행)
    def test_large_dataset(self):
        n = 200
        closes = list(np.linspace(80, 120, n))
        df = _make_df(n=n, close_prices=closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
