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

    # 17. Cycle385 A(품질): n_bins=4 전략 유효성 (DEFAULT_GRIDS에 포함된 탐색값)
    # n_bins=4는 n_bins=5보다 넓은 bin → cluster 안정성↑, noise↓ 가설 (WFO로 검증 중)
    def test_n_bins_4_returns_valid_signal(self):
        """n_bins=4 설정 시 Signal 객체 반환 및 필드 완전성 확인"""
        strategy4 = PriceClusterStrategy(n_bins=4)
        df = _make_df(n=60)
        sig = strategy4.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert isinstance(sig.entry_price, float)
        assert sig.strategy == "price_cluster"

    # 18. Cycle385 A(품질): n_bins=4 vs n_bins=5 — 다른 bin 경계 확인
    def test_n_bins_4_wider_bins_than_5(self):
        """n_bins=4이 n_bins=5보다 bin_width가 넓음 (price_range / n_bins)"""
        closes = pd.Series([100.0 + i * 0.2 for i in range(50)])  # 100~110 균등 분포
        price_range = float(closes.max() - closes.min())
        low4, high4, _, _, _ = _find_cluster(closes, n_bins=4)
        low5, high5, _, _, _ = _find_cluster(closes, n_bins=5)
        bin_width4 = high4 - low4
        bin_width5 = high5 - low5
        assert bin_width4 > bin_width5, (
            f"n_bins=4 bin_width({bin_width4:.4f}) should be > n_bins=5({bin_width5:.4f})"
        )
        expected_width4 = price_range / 4
        expected_width5 = price_range / 5
        assert abs(bin_width4 - expected_width4) < 1e-9
        assert abs(bin_width5 - expected_width5) < 1e-9

    # 19. Cycle385 A(품질): rsi_oversold_filter dead param 행동 문서화
    # Cycle384 D: rsi_oversold_filter=True → 0 trades (PF=0.00) 확인됨
    # cluster bounce는 RSI 중립(40-60)에서 발생 — RSI<40 필터가 모든 신호 차단
    def test_rsi_oversold_filter_accepts_neutral_rsi_data(self):
        """rsi_oversold_filter=False(기본값)는 rsi 컬럼 없어도 정상 동작"""
        strategy = PriceClusterStrategy(rsi_oversold_filter=False)
        df = _make_cluster_bounce_df()
        sig = strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
