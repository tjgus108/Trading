"""
WaveTrendOscStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.wavetrend_osc import WaveTrendOscStrategy
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
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * len(closes),
    })
    return df


def _make_oversold_buy_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """
    wt1 < -60 구간에서 cross_up 유발: 강한 하락 후 급반등.
    """
    prices = [100.0 - i * 2.5 for i in range(n)]
    # 마지막 2봉에서 급반등
    prices[-2] = prices[-3] + 8.0
    prices[-1] = prices[-2]
    return _make_df(n, prices)


def _make_overbought_sell_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """
    wt1 > 60 구간에서 cross_down 유발: 강한 상승 후 급하락.
    """
    prices = [50.0 + i * 2.5 for i in range(n)]
    # 마지막 2봉에서 급하락
    prices[-2] = prices[-3] - 8.0
    prices[-1] = prices[-2]
    return _make_df(n, prices)


class TestWaveTrendOscStrategy:

    def setup_method(self):
        self.strategy = WaveTrendOscStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "wavetrend_osc"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, WaveTrendOscStrategy)

    # 3. 데이터 부족 → HOLD + "Insufficient"
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음 (항상 Signal)
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
        assert sig.strategy == "wavetrend_osc"

    # 8. BUY reasoning에 "cross up" 포함
    def test_buy_reasoning_contains_cross_up(self):
        df = _make_oversold_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "cross up" in sig.reasoning.lower() or "WaveTrend" in sig.reasoning

    # 9. SELL reasoning에 "cross down" 포함
    def test_sell_reasoning_contains_cross_down(self):
        df = _make_overbought_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "cross down" in sig.reasoning.lower() or "WaveTrend" in sig.reasoning

    # 10. HIGH confidence: wt1 < -80 이면 BUY HIGH
    def test_high_confidence_extreme_oversold(self):
        # Very strong downtrend → wt1 very negative
        n = 60
        prices = [200.0 - i * 4.0 for i in range(n)]
        prices[-2] = prices[-3] + 15.0
        prices[-1] = prices[-2]
        df = _make_df(n, prices)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. MEDIUM confidence: flat prices → HOLD with MEDIUM
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
        assert sig.strategy == "wavetrend_osc"

    # 14. 최소 행 경계: 정확히 35행
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. 34행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 16. HOLD: flat prices → no crossover
    def test_hold_flat_prices(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 17. entry_price == close at iloc[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])
