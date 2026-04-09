"""
ZeroLagMACDStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.zlmacd import ZeroLagMACDStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 35


def _make_df(n: int = _MIN_ROWS + 5, prices: Optional[list] = None) -> pd.DataFrame:
    if prices is None:
        prices = [100.0] * n
    else:
        if len(prices) < n:
            prices = [prices[0]] * (n - len(prices)) + list(prices)
    closes = list(prices)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1 for c in closes],
        "low":    [c - 1 for c in closes],
        "volume": [1000.0] * len(closes),
    })
    return df


class TestZeroLagMACDStrategy:

    def setup_method(self):
        self.strategy = ZeroLagMACDStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "zlmacd"

    # 2. 데이터 부족 → HOLD + Insufficient
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Signal 인스턴스 반환
    def test_returns_signal_instance(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""
        assert sig.strategy == "zlmacd"

    # 5. flat 가격 → HOLD
    def test_hold_flat_prices(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. entry_price = close.iloc[-2]
    def test_entry_price_is_last_complete_candle(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 7. confidence는 유효 값
    def test_confidence_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. 정확히 35행 → Signal 반환 (에러 없음)
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 9. 34행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 10. 강한 상승 후 histogram crossover → BUY or HOLD
    def test_buy_signal_uptrend(self):
        n = 60
        prices = [100.0 + i * 1.5 for i in range(n - 3)]
        prices.append(prices[-1] - 4.0)   # -3: 조정 (histogram < 0)
        prices.append(prices[-2] + 8.0)   # -2: 급반등
        prices.append(prices[-1])          # -1: 미완성
        df = _make_df(n, prices[:n])
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 11. 강한 하락 후 histogram crossover → SELL or HOLD
    def test_sell_signal_downtrend(self):
        n = 60
        prices = [200.0 - i * 1.5 for i in range(n - 3)]
        prices.append(prices[-1] + 4.0)   # -3: 반등 (histogram > 0)
        prices.append(prices[-2] - 8.0)   # -2: 급하락
        prices.append(prices[-1])          # -1: 미완성
        df = _make_df(n, prices[:n])
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 12. action 은 유효 Action 값
    def test_action_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 13. bull_case / bear_case 포함
    def test_bull_bear_case_present(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 14. BUY 신호의 reasoning에 histogram 언급
    def test_buy_reasoning_mentions_histogram(self):
        n = 80
        prices = [100.0 + i * 2.0 for i in range(n - 3)]
        prices.append(prices[-1] - 6.0)
        prices.append(prices[-2] + 12.0)
        prices.append(prices[-1])
        df = _make_df(n, prices[:n])
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "histogram" in sig.reasoning.lower() or "hist" in sig.reasoning.lower()

    # 15. SELL 신호의 reasoning에 histogram 언급
    def test_sell_reasoning_mentions_histogram(self):
        n = 80
        prices = [200.0 - i * 2.0 for i in range(n - 3)]
        prices.append(prices[-1] + 6.0)
        prices.append(prices[-2] - 12.0)
        prices.append(prices[-1])
        df = _make_df(n, prices[:n])
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "histogram" in sig.reasoning.lower() or "hist" in sig.reasoning.lower()
