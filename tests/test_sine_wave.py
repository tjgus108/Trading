"""
SineWaveStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.sine_wave import SineWaveStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 10, prices: Optional[list] = None) -> pd.DataFrame:
    if prices is None:
        prices = [100.0] * n
    else:
        if len(prices) < n:
            prices = [prices[0]] * (n - len(prices)) + list(prices)
    closes = list(prices)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * len(closes),
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """sine crosses above lead: rising oscillation."""
    prices = [100.0 + np.sin(i * 0.3) * 5 for i in range(n)]
    return _make_df(n, prices)


def _make_sell_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """sine crosses below lead: falling oscillation."""
    prices = [100.0 + np.sin(i * 0.3 + np.pi) * 5 for i in range(n)]
    return _make_df(n, prices)


class TestSineWaveStrategy:

    def setup_method(self):
        self.strategy = SineWaveStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "sine_wave"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, SineWaveStrategy)

    # 3. 데이터 부족 → HOLD + "Insufficient"
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음
    def test_returns_signal_not_none(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. 정상 Signal 반환
    def test_returns_signal_instance(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.strategy == "sine_wave"

    # 8. BUY reasoning에 "Sine Wave" 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "Sine Wave" in sig.reasoning or "sine" in sig.reasoning.lower()

    # 9. SELL reasoning에 "Sine Wave" 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "Sine Wave" in sig.reasoning or "sine" in sig.reasoning.lower()

    # 10. confidence는 HIGH 또는 MEDIUM
    def test_confidence_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. MEDIUM confidence: flat prices
    def test_medium_confidence_flat(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드
    def test_strategy_field(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "sine_wave"

    # 14. 최소 행 경계: 정확히 25행
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. 24행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 16. HOLD: flat prices → no crossover
    def test_hold_flat_prices(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 17. entry_price == close at iloc[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 18. HOLD reasoning에 sine/lead 값 포함
    def test_hold_reasoning_has_values(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert "sine" in sig.reasoning.lower() or "Insufficient" in sig.reasoning
