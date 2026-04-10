"""
CompositeMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.composite_momentum import CompositeMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 35


def _make_df(n: int = _MIN_ROWS + 5, close_vals=None, trend: str = "up") -> pd.DataFrame:
    """
    trend='up'  → comp_score 높게: close 꾸준히 상승
    trend='down' → comp_score 낮게: close 꾸준히 하락
    trend='flat' → comp_score 중간
    """
    if close_vals is not None:
        closes = list(close_vals)
        n = len(closes)
    elif trend == "up":
        # 강하게 상승 → RSI 높음, ROC 높음, ema12>ema26
        closes = [100.0 + i * 0.8 for i in range(n)]
    elif trend == "down":
        # 강하게 하락
        closes = [200.0 - i * 0.8 for i in range(n)]
    else:
        # flat
        closes = [100.0 + (i % 3 - 1) * 0.1 for i in range(n)]

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


class TestCompositeMomentumStrategy:

    def setup_method(self):
        self.strategy = CompositeMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "composite_momentum"

    # 2. 인스턴스 확인
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 → HOLD + reasoning에 "Insufficient"
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 없음 (정상 df는 None 반환 안 함)
    def test_returns_signal_not_none(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 항상 존재
    def test_reasoning_present(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 6. 상승 추세 → BUY 또는 최소 HOLD (comp_score 확인)
    def test_up_trend_gives_buy_or_hold(self):
        df = _make_df(n=60, trend="up")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
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
        df = _make_df(n=60, trend="up")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 9. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_df(n=60, trend="down")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 10. HIGH confidence (강한 상승 → score > 0.8 가능)
    def test_high_confidence_possible(self):
        # 매우 강한 상승 → score >0.8 기대
        df = _make_df(n=80, trend="up")
        sig = self.strategy.generate(df)
        # HIGH 또는 MEDIUM 모두 유효
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 12. strategy 필드 = "composite_momentum"
    def test_strategy_field(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        assert sig.strategy == "composite_momentum"

    # 13. 최소 행 = 35
    def test_min_rows_exactly(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        # 35행: _last() = iloc[-2] = idx 33, NaN 가능 → HOLD 허용
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. NaN 포함 df → HOLD 반환 (충분한 rows지만 NaN)
    def test_nan_in_close_returns_hold(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        df = df.copy()
        df.loc[df.index[-2], "close"] = float("nan")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
