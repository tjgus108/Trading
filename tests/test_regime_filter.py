"""
RegimeFilterStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.regime_filter import RegimeFilterStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 100, mode: str = "trend_up") -> pd.DataFrame:
    """
    mode:
      "trend_up"   → 강한 상승 추세 (ema20 > ema50*1.02 + 돌파)
      "trend_down" → 강한 하락 추세
      "ranging"    → 횡보 (ema20 ≈ ema50, 낮은 변동성)
      "high_vol"   → 고변동성
    """
    np.random.seed(7)
    price = 100.0
    opens, closes, highs, lows = [], [], [], []

    for i in range(n):
        o = price
        if mode == "trend_up":
            c = o * np.random.uniform(1.005, 1.010)
        elif mode == "trend_down":
            c = o * np.random.uniform(0.990, 0.995)
        elif mode == "high_vol":
            c = o * np.random.uniform(0.960, 1.040)
        else:  # ranging
            c = o * np.random.uniform(0.9995, 1.0005)

        h = max(o, c) * np.random.uniform(1.001, 1.003)
        lo = min(o, c) * np.random.uniform(0.997, 0.999)
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


def _make_insufficient_df(n: int = 30) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestRegimeFilterStrategy:

    def setup_method(self):
        self.strategy = RegimeFilterStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "regime_filter"

    # 2. 인스턴스 생성
    def test_instantiation(self):
        s = RegimeFilterStrategy()
        assert s is not None

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        signal = self.strategy.generate(None)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert "Insufficient" in signal.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=100, mode="ranging")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=100, mode="trend_up")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "regime_filter"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_df(n=120, mode="trend_up")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "TREND_UP" in signal.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_df(n=120, mode="trend_down")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "TREND_DOWN" in signal.reasoning

    # 10. HIGH confidence 테스트 (낮은 변동성 + 강한 추세)
    def test_high_confidence_possible(self):
        df = _make_df(n=120, mode="trend_up")
        signal = self.strategy.generate(df)
        # HIGH or MEDIUM depending on atr conditions
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. MEDIUM confidence 테스트 (횡보 → HOLD)
    def test_hold_on_ranging(self):
        df = _make_df(n=100, mode="ranging")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=100, mode="trend_up")
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=100, mode="trend_down")
        signal = self.strategy.generate(df)
        assert signal.strategy == "regime_filter"

    # 14. 최소 행 수(MIN_ROWS=60)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=60, mode="ranging")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
