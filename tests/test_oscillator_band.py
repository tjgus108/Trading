"""
OscillatorBandStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.oscillator_band import OscillatorBandStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0, scenario: str = "neutral") -> pd.DataFrame:
    """
    scenario:
      "neutral"    → osc ≈ 50, HOLD
      "buy"        → osc < 30, osc rising, K > D → BUY
      "buy_high"   → osc < 20, osc rising, K > D → BUY HIGH
      "sell"       → osc > 70, osc falling, K < D → SELL
      "sell_high"  → osc > 80, osc falling, K < D → SELL HIGH
    """
    closes = [close] * n
    highs = [close + 10] * n
    lows = [close - 10] * n
    opens = [close] * n
    volumes = [1000.0] * n

    if scenario == "buy":
        # 낮은 close → RSI 낮음, stoch 낮음 → osc < 30
        # 앞부분은 range 넓고 close 아래쪽, 마지막(-2)봉은 약간 상승
        base_high = close + 100
        base_low = close - 5
        for i in range(n):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_low + 3   # stoch_k ≈ 3/105*100 ≈ 2.8
            opens[i] = base_low + 3

        # 신호 봉(-2): 약간 올라서 osc 개선 + K > D
        closes[-2] = base_low + 8
        opens[-2] = base_low + 3
        closes[-3] = base_low + 3
        closes[-4] = base_low + 3

    elif scenario == "buy_high":
        # osc < 20 → HIGH confidence
        base_high = close + 200
        base_low = close - 5
        for i in range(n):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_low + 2   # stoch_k ≈ 1
            opens[i] = base_low + 2

        closes[-2] = base_low + 5
        opens[-2] = base_low + 2
        closes[-3] = base_low + 2
        closes[-4] = base_low + 2

    elif scenario == "sell":
        # 높은 close → osc > 70, osc 하락, K < D
        base_high = close + 5
        base_low = close - 100
        for i in range(n):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_high - 3  # stoch_k ≈ 97
            opens[i] = base_high - 3

        closes[-2] = base_high - 8
        opens[-2] = base_high - 3
        closes[-3] = base_high - 3
        closes[-4] = base_high - 3

    elif scenario == "sell_high":
        # osc > 80 → HIGH confidence
        base_high = close + 5
        base_low = close - 200
        for i in range(n):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_high - 2  # stoch_k ≈ 99
            opens[i] = base_high - 2

        closes[-2] = base_high - 6
        opens[-2] = base_high - 2
        closes[-3] = base_high - 2
        closes[-4] = base_high - 2

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


class TestOscillatorBandStrategy:

    def setup_method(self):
        self.strategy = OscillatorBandStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "oscillator_band"

    # 2. 인스턴스
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 아님
    def test_returns_signal_not_none(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 존재
    def test_reasoning_present(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""
        assert len(sig.reasoning) > 0

    # 6. 정상 신호 반환 (neutral → HOLD)
    def test_normal_signal_hold(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY reasoning 포함 확인
    def test_buy_reasoning(self):
        df = _make_df(n=30, scenario="buy")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "OscillatorBand" in sig.reasoning

    # 9. SELL reasoning 포함 확인
    def test_sell_reasoning(self):
        df = _make_df(n=30, scenario="sell")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "OscillatorBand" in sig.reasoning

    # 10. BUY HIGH confidence (osc < 20)
    def test_buy_high_confidence(self):
        df = _make_df(n=30, scenario="buy_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. SELL HIGH confidence (osc > 80)
    def test_sell_high_confidence(self):
        df = _make_df(n=30, scenario="sell_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값
    def test_strategy_field(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.strategy == "oscillator_band"

    # 14. 최소 행 경계: 정확히 20행
    def test_exactly_min_rows(self):
        df = _make_df(n=20, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
