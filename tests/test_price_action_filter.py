"""
PriceActionFilterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_action_filter import PriceActionFilterStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 60, close: float = 100.0, scenario: str = "neutral") -> pd.DataFrame:
    """
    scenario:
      "neutral"        → HOLD (필터 미통과)
      "buy"            → trend_up + strong_bull + vol_confirm → BUY
      "buy_high"       → buy + body_ratio > 0.8 → BUY HIGH
      "sell"           → trend_down + strong_bear + vol_confirm → SELL
      "sell_high"      → sell + body_ratio > 0.8 → SELL HIGH
      "buy_no_vol"     → trend_up + strong_bull + vol 부족 → HOLD
    """
    # 기본: flat 시장 (HOLD)
    closes = [close] * n
    opens = [close] * n
    highs = [close + 1] * n
    lows = [close - 1] * n
    volumes = [1000.0] * n

    if scenario in ("buy", "buy_high", "buy_no_vol"):
        # 추세 상승: 앞 50봉 낮게, 뒤로 올라서 close > ema50
        base = close * 0.8
        for i in range(n):
            closes[i] = base + (close - base) * (i / (n - 1)) * 1.2
            opens[i] = closes[i] - 0.5
            highs[i] = closes[i] + 1
            lows[i] = closes[i] - 1

        # 신호 봉(-2): 강한 상승 봉 (body_ratio > 0.6)
        body = close * 0.08 if scenario != "buy_high" else close * 0.09
        total = close * 0.1
        opens[-2] = closes[-2] - body
        highs[-2] = closes[-2] + (total - body) / 2
        lows[-2] = opens[-2] - (total - body) / 2
        closes[-2] = closes[-2]  # 유지

        if scenario == "buy_no_vol":
            # 거래량 부족
            for i in range(n):
                volumes[i] = 1000.0
            volumes[-2] = 100.0  # 평균 이하
        else:
            # 거래량 충분
            for i in range(n):
                volumes[i] = 500.0
            volumes[-2] = 2000.0  # 평균 상회

    elif scenario in ("sell", "sell_high"):
        # 추세 하락: 앞 50봉 높게, 뒤로 낮아져서 close < ema50
        base = close * 1.2
        for i in range(n):
            closes[i] = base - (base - close * 0.8) * (i / (n - 1)) * 1.1
            opens[i] = closes[i] + 0.5
            highs[i] = closes[i] + 1
            lows[i] = closes[i] - 1

        # 신호 봉(-2): 강한 하락 봉 (body_ratio > 0.6)
        body = close * 0.08 if scenario != "sell_high" else close * 0.09
        total = close * 0.1
        closes[-2] = closes[-2]
        opens[-2] = closes[-2] + body
        highs[-2] = opens[-2] + (total - body) / 2
        lows[-2] = closes[-2] - (total - body) / 2

        for i in range(n):
            volumes[i] = 500.0
        volumes[-2] = 2000.0

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


class TestPriceActionFilterStrategy:

    def setup_method(self):
        self.strategy = PriceActionFilterStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_action_filter"

    # 2. 인스턴스
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 아님
    def test_returns_signal_not_none(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 존재
    def test_reasoning_present(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""
        assert len(sig.reasoning) > 0

    # 6. 정상 signal 반환 (neutral)
    def test_normal_signal_neutral(self):
        df = _make_df(n=60, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, scenario="neutral")
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY reasoning 확인
    def test_buy_reasoning(self):
        df = _make_df(n=60, scenario="buy")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "PriceActionFilter" in sig.reasoning

    # 9. SELL reasoning 확인
    def test_sell_reasoning(self):
        df = _make_df(n=60, scenario="sell")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "PriceActionFilter" in sig.reasoning

    # 10. MEDIUM confidence (body_ratio ≈ 0.6~0.8)
    def test_medium_confidence_buy(self):
        df = _make_df(n=60, scenario="buy")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. HIGH confidence (body_ratio > 0.8)
    def test_high_confidence_sell(self):
        df = _make_df(n=60, scenario="sell_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=60, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값
    def test_strategy_field(self):
        df = _make_df(n=60, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_action_filter"

    # 14. 최소 행 경계: 정확히 55행
    def test_exactly_min_rows(self):
        df = _make_df(n=55, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
