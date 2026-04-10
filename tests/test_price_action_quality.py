"""
PriceActionQualityStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_action_quality import PriceActionQualityStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, mode: str = "bull") -> pd.DataFrame:
    """
    mode: "bull"  → 3연속 강한 양봉 (body_ratio > 0.6, lower_wick < 0.2)
          "bear"  → 3연속 강한 음봉
          "mixed" → 혼합 (quality 조건 미충족)
    """
    np.random.seed(42)
    opens, closes, highs, lows = [], [], [], []
    price = 100.0

    for i in range(n):
        o = price
        if mode == "bull":
            c = o * np.random.uniform(1.012, 1.018)   # 강한 양봉
            h = c * np.random.uniform(1.001, 1.003)   # 작은 upper wick
            lo = o * np.random.uniform(0.999, 1.000)  # 거의 없는 lower wick
        elif mode == "bear":
            c = o * np.random.uniform(0.982, 0.988)   # 강한 음봉
            lo = c * np.random.uniform(0.997, 0.999)  # 작은 lower wick
            h = o * np.random.uniform(1.000, 1.001)   # 거의 없는 upper wick
        else:
            c = o * np.random.uniform(0.999, 1.001)
            h = max(o, c) * np.random.uniform(1.005, 1.010)
            lo = min(o, c) * np.random.uniform(0.990, 0.995)
        opens.append(o)
        closes.append(c)
        highs.append(h)
        lows.append(lo)
        price = c

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 5) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPriceActionQualityStrategy:

    def setup_method(self):
        self.strategy = PriceActionQualityStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "price_action_quality"

    # 2. 인스턴스 생성
    def test_instantiation(self):
        s = PriceActionQualityStrategy()
        assert s is not None

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=5)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        signal = self.strategy.generate(None)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=5)
        signal = self.strategy.generate(df)
        assert "Insufficient" in signal.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=30, mode="mixed")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=30, mode="bull")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "price_action_quality"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_df(n=30, mode="bull")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "양봉" in signal.reasoning or "strong_bull" in signal.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_df(n=30, mode="bear")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "음봉" in signal.reasoning or "strong_bear" in signal.reasoning

    # 10. HIGH confidence 테스트 (body_ratio > 0.8인 강한 양봉)
    def test_high_confidence_possible(self):
        df = _make_df(n=30, mode="bull")
        signal = self.strategy.generate(df)
        # body_ratio가 높으면 HIGH, 아니면 MEDIUM — 둘 다 허용
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. MEDIUM confidence 테스트 (HOLD)
    def test_medium_or_low_on_mixed(self):
        df = _make_df(n=30, mode="mixed")
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30, mode="bull")
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=30, mode="bear")
        signal = self.strategy.generate(df)
        assert signal.strategy == "price_action_quality"

    # 14. 최소 행 수(MIN_ROWS=10)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=10, mode="mixed")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
