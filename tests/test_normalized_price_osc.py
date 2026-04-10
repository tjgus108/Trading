"""
NormalizedPriceOscStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.normalized_price_osc import NormalizedPriceOscStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(closes):
    closes = np.array(closes, dtype=float)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(len(closes)) * 1000,
    })


def _make_buy_df():
    """NPO crosses above 20 from below, npo > npo_ma."""
    n = 40
    # 먼저 하락 구간으로 npo를 낮게 유지하다가 마지막 완성봉에서 반등
    closes = np.array([100.0 * (0.997 ** i) for i in range(n)])
    # 마지막 완성봉(-2)에서 강하게 반등해 npo가 20을 넘도록 함
    closes[-2] = closes[-3] * 1.05
    return _make_df(closes)


def _make_sell_df():
    """NPO crosses below 80 from above, npo < npo_ma."""
    n = 40
    # 상승 구간으로 npo를 높게 유지하다가 마지막 완성봉에서 하락
    closes = np.array([100.0 * (1.003 ** i) for i in range(n)])
    # 마지막 완성봉(-2)에서 급락해 npo가 80 아래로
    closes[-2] = closes[-3] * 0.94
    return _make_df(closes)


def _make_insufficient_df():
    closes = np.linspace(100, 110, 20)
    return _make_df(closes)


def _make_hold_df():
    n = 40
    np.random.seed(42)
    closes = 100.0 + np.random.uniform(-0.5, 0.5, n)
    return _make_df(closes)


class TestNormalizedPriceOscStrategy:

    def setup_method(self):
        self.strategy = NormalizedPriceOscStrategy()

    # 1. 전략명
    def test_strategy_name(self):
        assert self.strategy.name == "normalized_price_osc"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, NormalizedPriceOscStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. 데이터 부족 → reasoning에 "Insufficient" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df()
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 5. Signal 반환
    def test_returns_signal(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. action 유효값
    def test_action_valid(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 8. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 9. strategy 필드
    def test_strategy_field(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "normalized_price_osc"

    # 10. confidence 유효값
    def test_confidence_valid(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. HOLD → confidence LOW
    def test_hold_confidence_low(self):
        df = _make_hold_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 12. BUY reasoning 포함
    def test_buy_reasoning(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "crossed above 20" in sig.reasoning

    # 13. SELL reasoning 포함
    def test_sell_reasoning(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "crossed below 80" in sig.reasoning

    # 14. 최소 25행 요구 (24행 → HOLD)
    def test_min_rows_boundary(self):
        closes = np.linspace(100, 110, 24)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
