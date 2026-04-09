"""
PriceVelocityStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_velocity import PriceVelocityStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df_trending(
    n: int = 30,
    start: float = 100.0,
    step: float = 1.0,
) -> pd.DataFrame:
    """일정한 기울기로 상승/하락하는 close 시리즈."""
    closes = [start + i * step for i in range(n)]
    df = pd.DataFrame({"close": closes})
    return df


def _make_df_flat(n: int = 30, value: float = 100.0) -> pd.DataFrame:
    """변화 없는 flat 시리즈."""
    df = pd.DataFrame({"close": [value] * n})
    return df


def _make_df_accel(
    n: int = 40,
    base: float = 100.0,
    accel: float = 0.5,
) -> pd.DataFrame:
    """가속도를 갖는 시리즈: close[i] = base + accel * i^2 / 2."""
    closes = [base + accel * (i ** 2) / 2 for i in range(n)]
    df = pd.DataFrame({"close": closes})
    return df


class TestPriceVelocityStrategy:

    def setup_method(self):
        self.strategy = PriceVelocityStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_velocity"

    # 2. 상승 가속 → BUY
    def test_buy_signal_uptrend(self):
        df = _make_df_accel(n=40, base=100.0, accel=1.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.BUY
        assert sig.strategy == "price_velocity"

    # 3. 하락 가속 → SELL
    def test_sell_signal_downtrend(self):
        df = _make_df_accel(n=40, base=500.0, accel=-1.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.SELL

    # 4. flat → HOLD (velocity = 0)
    def test_hold_flat(self):
        df = _make_df_flat(n=30, value=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df_flat(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 6. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_df_trending(n=40, start=100.0, step=2.0)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 7. entry_price = _last(df)["close"]
    def test_entry_price(self):
        df = _make_df_trending(n=40, start=100.0, step=2.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))

    # 8. BUY confidence HIGH: |velocity| > vol_vel * 1.0
    def test_buy_high_confidence(self):
        # 강한 상승 가속 → HIGH
        df = _make_df_accel(n=40, base=100.0, accel=3.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 9. SELL confidence 존재 여부
    def test_sell_confidence_set(self):
        df = _make_df_accel(n=40, base=1000.0, accel=-3.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. 가속 시리즈 → BUY
    def test_buy_accelerating(self):
        df = _make_df_accel(n=40, base=100.0, accel=1.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 11. 감속 시리즈 → SELL
    def test_sell_accelerating_down(self):
        df = _make_df_accel(n=40, base=500.0, accel=-1.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 12. HOLD entry_price = 신호 봉 close
    def test_hold_entry_price(self):
        df = _make_df_flat(n=30, value=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.entry_price == pytest.approx(50.0)

    # 13. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df_trending(n=40, start=100.0, step=2.0)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 14. strategy 이름 일관성 (HOLD 포함)
    def test_strategy_name_in_hold(self):
        df = _make_df_flat(n=30, value=100.0)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_velocity"
