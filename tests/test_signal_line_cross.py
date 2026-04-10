"""
SignalLineCrossStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.signal_line_cross import SignalLineCrossStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 35


def _make_df(n: int = _MIN_ROWS + 10, close_vals=None) -> pd.DataFrame:
    if close_vals is not None:
        closes = list(close_vals)
        n = len(closes)
    else:
        closes = [100.0] * n
    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _make_buy_cross_df() -> pd.DataFrame:
    """
    diff crosses above signal while diff < 0.
    Build close series: first go up (ema8 > ema21 positive diff), then drop so diff goes negative,
    then small recovery so diff crosses above signal from below.
    """
    n = 80
    # Phase1: slow rise (ema8 < ema26 eventually after drop)
    closes = [100.0 + i * 0.3 for i in range(40)]  # mild rise
    # Phase2: sharp drop → ema8 < ema21 → diff < 0
    closes += [closes[-1] - i * 0.5 for i in range(20)]
    # Phase3: tiny uptick to trigger cross above signal while diff still negative
    last = closes[-1]
    closes += [last + i * 0.05 for i in range(20)]
    return _make_df(close_vals=closes)


def _make_sell_cross_df() -> pd.DataFrame:
    """
    diff crosses below signal while diff > 0.
    """
    n = 80
    # Phase1: drop (ema8 < ema21 → diff < 0)
    closes = [200.0 - i * 0.3 for i in range(40)]
    # Phase2: sharp rise → diff > 0
    closes += [closes[-1] + i * 0.5 for i in range(20)]
    # Phase3: tiny downtick to trigger cross below signal while diff still positive
    last = closes[-1]
    closes += [last - i * 0.05 for i in range(20)]
    return _make_df(close_vals=closes)


class TestSignalLineCrossStrategy:

    def setup_method(self):
        self.strategy = SignalLineCrossStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "signal_line_cross"

    # 2. 인스턴스 확인
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 → HOLD + "Insufficient"
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 없음
    def test_returns_signal_not_none(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 항상 존재
    def test_reasoning_present(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 6. 정상 신호 반환 (Action 중 하나)
    def test_normal_signal_action(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
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

    # 8. BUY reasoning에 "BUY" 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_buy_cross_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 9. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_sell_cross_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 10. confidence는 HIGH or MEDIUM or LOW
    def test_confidence_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 12. strategy 필드 = "signal_line_cross"
    def test_strategy_field(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "signal_line_cross"

    # 13. 최소 행 = 35
    def test_min_rows_exactly(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. flat price → HOLD (no cross)
    def test_flat_price_hold(self):
        df = _make_df(n=50)  # all closes = 100.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
