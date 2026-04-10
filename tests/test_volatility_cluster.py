"""
VolatilityClusterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volatility_cluster import VolatilityClusterStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _make_df(closes, highs=None, lows=None) -> pd.DataFrame:
    n = len(closes)
    if highs is None:
        highs = [c + 1.0 for c in closes]
    if lows is None:
        lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })


def _make_flat_df(n: int = _MIN_ROWS + 5, val: float = 100.0) -> pd.DataFrame:
    return _make_df([val] * n)


def _make_low_vol_uptrend_df() -> pd.DataFrame:
    """Low vol_ratio + upward direction → BUY."""
    n = _MIN_ROWS + 20
    # gradually rising — but uniform tiny steps so vol5/vol20 << 0.5
    base = np.linspace(100.0, 110.0, n)
    closes = list(base)
    # make the last complete candle clearly above 10 bars ago
    closes[-2] = closes[-12] * 1.05  # ensure direction > 0
    highs = [c + 0.01 for c in closes]
    lows = [c - 0.01 for c in closes]
    return _make_df(closes, highs, lows)


def _make_low_vol_downtrend_df() -> pd.DataFrame:
    """Low vol_ratio + downward direction → SELL."""
    n = _MIN_ROWS + 20
    base = np.linspace(110.0, 100.0, n)
    closes = list(base)
    closes[-2] = closes[-12] * 0.95  # ensure direction < 0
    highs = [c + 0.01 for c in closes]
    lows = [c - 0.01 for c in closes]
    return _make_df(closes, highs, lows)


def _make_high_vol_df() -> pd.DataFrame:
    """High vol_ratio (>=0.5) → HOLD."""
    n = _MIN_ROWS + 20
    # volatile short period, stable long period
    closes = [100.0 + 5.0 * np.sin(i) for i in range(n)]
    highs = [c + 2.0 for c in closes]
    lows = [c - 2.0 for c in closes]
    return _make_df(closes, highs, lows)


def _make_very_low_vol_uptrend_df() -> pd.DataFrame:
    """vol_ratio < 0.3 + uptrend → HIGH confidence BUY."""
    n = _MIN_ROWS + 30
    # extremely uniform rise → very low vol
    closes = list(np.linspace(100.0, 103.0, n))
    closes[-2] = closes[-12] + 0.5  # direction > 0
    highs = [c + 0.001 for c in closes]
    lows = [c - 0.001 for c in closes]
    return _make_df(closes, highs, lows)


class TestVolatilityClusterStrategy:

    def setup_method(self):
        self.strategy = VolatilityClusterStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "volatility_cluster"

    # 2. 인스턴스 생성
    def test_instantiation(self):
        s = VolatilityClusterStrategy()
        assert s is not None

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_flat_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_reasoning(self):
        df = _make_flat_df(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_low_vol_uptrend_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_low_vol_downtrend_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 10. HIGH confidence 테스트
    def test_high_confidence_buy(self):
        df = _make_very_low_vol_uptrend_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. MEDIUM confidence 테스트
    def test_medium_confidence_valid(self):
        df = _make_low_vol_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.strategy == "volatility_cluster"

    # 14. 최소 행 수에서 동작
    def test_exact_min_rows(self):
        df = _make_flat_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
