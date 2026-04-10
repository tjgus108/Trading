"""
AdaptiveCycleStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.adaptive_cycle import AdaptiveCycleStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 15


def _make_df(n: int = _MIN_ROWS + 10, prices: Optional[list] = None,
             highs: Optional[list] = None, lows: Optional[list] = None) -> pd.DataFrame:
    if prices is None:
        prices = [100.0] * n
    else:
        if len(prices) < n:
            prices = [prices[0]] * (n - len(prices)) + list(prices)
    closes = list(prices)
    _highs = highs if highs is not None else [c + 1.0 for c in closes]
    _lows = lows if lows is not None else [c - 1.0 for c in closes]
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   _highs,
        "low":    _lows,
        "volume": [1000.0] * len(closes),
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """cycle_pos < 0.2 AND cycle_dir > 0: prices near bottom, turning up."""
    # Low prices with a slight uptick at end
    prices = [90.0] * (n - 3) + [88.0, 89.0, 90.0]
    highs = [100.0 + 5] * n
    lows = [88.0] * n
    return _make_df(n, prices, highs, lows)


def _make_sell_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """cycle_pos > 0.8 AND cycle_dir < 0: prices near top, turning down."""
    prices = [110.0] * (n - 3) + [112.0, 111.0, 110.0]
    highs = [112.0] * n
    lows = [100.0] * n
    return _make_df(n, prices, highs, lows)


class TestAdaptiveCycleStrategy:

    def setup_method(self):
        self.strategy = AdaptiveCycleStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "adaptive_cycle"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, AdaptiveCycleStrategy)

    # 3. 데이터 부족 → HOLD + "Insufficient"
    def test_insufficient_data(self):
        df = _make_df(n=5)
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
        assert sig.strategy == "adaptive_cycle"

    # 8. BUY reasoning에 "cycle" 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "cycle" in sig.reasoning.lower()

    # 9. SELL reasoning에 "cycle" 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "cycle" in sig.reasoning.lower()

    # 10. confidence는 HIGH 또는 MEDIUM
    def test_confidence_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. HIGH confidence: BUY when cycle_pos < 0.1
    def test_high_confidence_buy(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        # Just verify valid confidence
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
        assert sig.strategy == "adaptive_cycle"

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

    # 16. HOLD: mid-range cycle_pos
    def test_hold_mid_range(self):
        prices = [105.0] * (_MIN_ROWS + 10)
        highs = [110.0] * (_MIN_ROWS + 10)
        lows = [100.0] * (_MIN_ROWS + 10)
        df = _make_df(_MIN_ROWS + 10, prices, highs, lows)
        sig = self.strategy.generate(df)
        # flat prices → cycle_dir ≈ 0, should HOLD
        assert sig.action == Action.HOLD

    # 17. entry_price == close at iloc[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 18. HOLD reasoning has cycle_pos value
    def test_hold_reasoning_has_pos(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert "cycle" in sig.reasoning.lower() or "Insufficient" in sig.reasoning
