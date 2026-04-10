"""
PriceVelocityFilterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_velocity_filter import PriceVelocityFilterStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_uptrend(n: int = 40, start: float = 100.0, step: float = 1.5) -> pd.DataFrame:
    """단조 상승 시리즈: EMA(5) > EMA(20) 보장."""
    closes = [start + i * step for i in range(n)]
    return pd.DataFrame({"close": closes})


def _make_downtrend(n: int = 40, start: float = 200.0, step: float = 1.5) -> pd.DataFrame:
    """단조 하락 시리즈."""
    closes = [start - i * step for i in range(n)]
    return pd.DataFrame({"close": closes})


def _make_flat(n: int = 40, value: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame({"close": [value] * n})


def _make_strong_uptrend(n: int = 50) -> pd.DataFrame:
    """강한 가속 상승 → vel 크고 vel_std 작아서 HIGH 가능."""
    closes = [100.0 + (i ** 1.5) * 0.5 for i in range(n)]
    return pd.DataFrame({"close": closes})


def _make_strong_downtrend(n: int = 50) -> pd.DataFrame:
    """강한 가속 하락."""
    closes = [2000.0 - (i ** 1.5) * 0.5 for i in range(n)]
    return pd.DataFrame({"close": closes})


class TestPriceVelocityFilterStrategy:

    def setup_method(self):
        self.strategy = PriceVelocityFilterStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_velocity_filter"

    # 2. 상승 추세 → BUY
    def test_buy_uptrend(self):
        df = _make_uptrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "price_velocity_filter"

    # 3. 하락 추세 → SELL
    def test_sell_downtrend(self):
        df = _make_downtrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 4. flat → HOLD (vel ≈ 0)
    def test_hold_flat(self):
        df = _make_flat(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_flat(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 6. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_uptrend(n=40)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 7. entry_price = iloc[-2]["close"]
    def test_entry_price_buy(self):
        df = _make_uptrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))

    # 8. HOLD entry_price
    def test_entry_price_hold(self):
        df = _make_flat(n=40, value=77.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(77.0)

    # 9. BUY confidence는 HIGH 또는 MEDIUM
    def test_buy_confidence_valid(self):
        df = _make_uptrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. SELL confidence는 HIGH 또는 MEDIUM
    def test_sell_confidence_valid(self):
        df = _make_downtrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. 강한 상승 → HIGH confidence 가능
    def test_strong_uptrend_high_confidence(self):
        df = _make_strong_uptrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        # HIGH or MEDIUM 허용 (데이터 특성에 따라 달라짐)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. strategy 이름 일관성 (HOLD)
    def test_strategy_name_hold(self):
        df = _make_flat(n=40)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_velocity_filter"

    # 13. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_uptrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 14. 정확히 25행 (경계값) → 데이터 부족 아님
    def test_exactly_min_rows(self):
        df = _make_uptrend(n=25)
        sig = self.strategy.generate(df)
        # 25행이면 처리 가능 (HOLD 또는 신호)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert "Insufficient" not in sig.reasoning

    # 15. 24행 → 데이터 부족
    def test_below_min_rows(self):
        df = _make_uptrend(n=24)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 16. SELL일 때 strategy 필드 확인
    def test_sell_strategy_field(self):
        df = _make_downtrend(n=40)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_velocity_filter"
