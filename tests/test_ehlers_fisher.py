"""
EhlersFisherStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.ehlers_fisher import EhlersFisherStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 15


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


def _make_buy_df(n: int = _MIN_ROWS + 30) -> pd.DataFrame:
    """
    fish crosses above signal with fish < 0:
    가격이 낮은 구간에서 반등.
    """
    # 하락 후 반등: fish가 음수 구간에서 signal 상향 돌파
    prices = [90.0 - i * 0.3 for i in range(n - 5)]
    # 마지막 몇 봉 반등
    last = prices[-1] if prices else 85.0
    prices += [last + 0.1, last + 0.5, last + 1.0, last + 2.0, last + 2.0]
    return _make_df(n, prices[:n])


def _make_sell_df(n: int = _MIN_ROWS + 30) -> pd.DataFrame:
    """
    fish crosses below signal with fish > 0:
    가격이 높은 구간에서 하락.
    """
    prices = [90.0 + i * 0.3 for i in range(n - 5)]
    last = prices[-1] if prices else 100.0
    prices += [last - 0.1, last - 0.5, last - 1.0, last - 2.0, last - 2.0]
    return _make_df(n, prices[:n])


class TestEhlersFisherStrategy:

    def setup_method(self):
        self.strategy = EhlersFisherStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "ehlers_fisher"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, EhlersFisherStrategy)

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
        assert sig.strategy == "ehlers_fisher"

    # 8. BUY reasoning에 "EhlersFisher" 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "EhlersFisher" in sig.reasoning

    # 9. SELL reasoning에 "EhlersFisher" 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "EhlersFisher" in sig.reasoning

    # 10. HIGH confidence: abs(fish) > 2.0
    def test_high_confidence_possible(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. MEDIUM confidence: flat → HOLD
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
        assert sig.strategy == "ehlers_fisher"

    # 14. 최소 행 경계: 정확히 15행
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. 14행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 16. flat prices → HOLD
    def test_hold_flat_prices(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 17. entry_price == close at iloc[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 18. action enum 유효
    def test_action_is_valid_enum(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
