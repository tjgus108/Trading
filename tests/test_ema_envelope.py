"""
EMAEnvelopeStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ema_envelope import EMAEnvelopeStrategy
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
    """
    prev_close < lower, curr_close > lower 유도.
    ema20 기반이므로 충분한 데이터 후 마지막 두 봉 조작.
    """
    n = 40
    closes = np.ones(n) * 100.0
    # ema20 ~ 100.0, lower ~ 97.5
    # prev(-3): 97.0 (below lower), curr(-2): 98.0 (above lower)
    closes[-3] = 97.0
    closes[-2] = 98.0
    return _make_df(closes)


def _make_sell_df():
    """
    prev_close > upper, curr_close < upper 유도.
    """
    n = 40
    closes = np.ones(n) * 100.0
    # ema20 ~ 100.0, upper ~ 102.5
    # prev(-3): 103.0 (above upper), curr(-2): 102.0 (below upper)
    closes[-3] = 103.0
    closes[-2] = 102.0
    return _make_df(closes)


def _make_insufficient_df():
    closes = np.linspace(100, 110, 20)
    return _make_df(closes)


def _make_hold_df():
    n = 40
    closes = np.ones(n) * 100.0
    return _make_df(closes)


class TestEMAEnvelopeStrategy:

    def setup_method(self):
        self.strategy = EMAEnvelopeStrategy()

    # 1. 전략명
    def test_strategy_name(self):
        assert self.strategy.name == "ema_envelope"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, EMAEnvelopeStrategy)

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
        assert sig.strategy == "ema_envelope"

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
            assert "lower envelope" in sig.reasoning

    # 13. SELL reasoning 포함
    def test_sell_reasoning(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "upper envelope" in sig.reasoning

    # 14. 최소 25행 요구 (24행 → HOLD)
    def test_min_rows_boundary(self):
        closes = np.linspace(100, 110, 24)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
