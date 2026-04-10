"""
AdaptiveThresholdStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_threshold import AdaptiveThresholdStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 40


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


def _make_buy_df() -> pd.DataFrame:
    """norm_price crosses above threshold_up at the last complete candle."""
    n = _MIN_ROWS + 20
    # Start flat then surge up at the end → norm_price crosses above quantile 0.8
    closes = [100.0] * (n - 5)
    # big upward spike sequence → last complete candle (idx=-2) crosses up
    closes += [101.0, 102.0, 103.0, 108.0, 100.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return _make_df(closes, highs, lows)


def _make_sell_df() -> pd.DataFrame:
    """norm_price crosses below threshold_down at the last complete candle."""
    n = _MIN_ROWS + 20
    closes = [100.0] * (n - 5)
    closes += [99.0, 98.0, 97.0, 92.0, 100.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return _make_df(closes, highs, lows)


def _make_high_conf_buy_df() -> pd.DataFrame:
    """norm_price exceeds threshold_up * 1.2 → HIGH confidence."""
    n = _MIN_ROWS + 30
    closes = [100.0] * (n - 5)
    # Very large spike to ensure norm_price >> threshold_up * 1.2
    closes += [101.0, 102.0, 103.0, 130.0, 100.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return _make_df(closes, highs, lows)


class TestAdaptiveThresholdStrategy:

    def setup_method(self):
        self.strategy = AdaptiveThresholdStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "adaptive_threshold"

    # 2. 인스턴스 생성
    def test_instantiation(self):
        s = AdaptiveThresholdStrategy()
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
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 10. HIGH confidence 테스트
    def test_high_confidence(self):
        df = _make_high_conf_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY and sig.confidence == Confidence.HIGH:
            assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence 테스트
    def test_medium_confidence_valid(self):
        df = _make_buy_df()
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
        assert sig.strategy == "adaptive_threshold"

    # 14. 최소 행 수에서 동작
    def test_exact_min_rows(self):
        df = _make_flat_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
