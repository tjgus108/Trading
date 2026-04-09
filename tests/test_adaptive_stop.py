"""
AdaptiveStopStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.adaptive_stop import AdaptiveStopStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 5, prices: Optional[list] = None, trend: str = "flat") -> pd.DataFrame:
    if prices is None:
        if trend == "up":
            prices = [80.0 + i * 0.5 for i in range(n)]
        elif trend == "down":
            prices = [120.0 - i * 0.5 for i in range(n)]
        else:
            prices = [100.0] * n
    else:
        if len(prices) < n:
            prices = [prices[0]] * (n - len(prices)) + list(prices)

    closes = list(prices)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 2 for c in closes],
        "low":    [c - 2 for c in closes],
        "volume": [1000.0] * len(closes),
    })
    return df


class TestAdaptiveStopStrategy:

    def setup_method(self):
        self.strategy = AdaptiveStopStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "adaptive_stop"

    # 2. 데이터 부족 → HOLD + Insufficient
    def test_insufficient_data(self):
        df = _make_df(n=15)
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
        assert sig.strategy == "adaptive_stop"

    # 5. entry_price = close.iloc[-2]
    def test_entry_price_is_last_complete_candle(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 6. confidence는 유효 값
    def test_confidence_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 7. 정확히 25행 → Signal 반환
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 8. 24행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 9. 상승 추세 → BUY 가능성 (close > EMA50, RSI > 50)
    def test_buy_possible_in_uptrend(self):
        n = 60
        df = _make_df(n=n, trend="up")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 10. 하락 추세 → SELL 가능성 (close < EMA50, RSI < 50)
    def test_sell_possible_in_downtrend(self):
        n = 60
        df = _make_df(n=n, trend="down")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 11. multiplier 커스터마이징
    def test_custom_multiplier(self):
        strategy = AdaptiveStopStrategy(multiplier=3.0)
        df = _make_df(trend="up")
        sig = strategy.generate(df)
        assert isinstance(sig, Signal)

    # 12. action 은 유효 Action 값
    def test_action_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 13. RSI > 60 이면 HIGH confidence (상승 추세에서 BUY 시)
    def test_high_confidence_strong_rsi(self):
        n = 80
        # 강한 상승: RSI > 60 유발
        prices = [50.0 + i * 1.0 for i in range(n)]
        df = _make_df(n=n, prices=prices)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 14. bull_case / bear_case 포함
    def test_bull_bear_case_present(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 15. BUY reasoning에 EMA50 및 RSI 언급
    def test_buy_reasoning_mentions_ema50_rsi(self):
        n = 80
        prices = [50.0 + i * 1.0 for i in range(n)]
        df = _make_df(n=n, prices=prices)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "EMA50" in sig.reasoning or "ema50" in sig.reasoning.lower()
            assert "RSI" in sig.reasoning

    # 16. SELL reasoning에 ShortStop 언급
    def test_sell_reasoning_mentions_shortstop(self):
        n = 80
        prices = [150.0 - i * 1.0 for i in range(n)]
        df = _make_df(n=n, prices=prices)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "ShortStop" in sig.reasoning or "short" in sig.reasoning.lower()
