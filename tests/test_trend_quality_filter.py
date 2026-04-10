"""
TrendQualityFilterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_quality_filter import TrendQualityFilterStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _base_df(n: int, closes: list) -> pd.DataFrame:
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
    })


def make_uptrend_df(n: int = _MIN_ROWS + 1) -> pd.DataFrame:
    """
    지속 상승: 20봉 중 > 60% 양봉, momentum > 0.
    마지막 11봉(인덱스 -12 ~ -2)가 신호 구간.
    """
    # 첫 절반: 상승
    closes = list(np.linspace(100.0, 130.0, n))
    return _base_df(n, closes)


def make_downtrend_df(n: int = _MIN_ROWS + 1) -> pd.DataFrame:
    """지속 하락: 20봉 중 > 60% 음봉, momentum < 0."""
    closes = list(np.linspace(130.0, 100.0, n))
    return _base_df(n, closes)


def make_neutral_df(n: int = _MIN_ROWS + 1) -> pd.DataFrame:
    """지그재그: trend_consistency 낮음."""
    closes = [100.0 + (1 if i % 2 == 0 else -1) for i in range(n)]
    return _base_df(n, closes)


class TestTrendQualityFilterStrategy:

    def setup_method(self):
        self.strategy = TrendQualityFilterStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "trend_quality_filter"

    # 2. BUY 신호: 지속 상승
    def test_buy_signal(self):
        df = make_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "trend_quality_filter"

    # 3. SELL 신호: 지속 하락
    def test_sell_signal(self):
        df = make_downtrend_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "trend_quality_filter"

    # 4. HOLD: 지그재그 (consistency 낮음)
    def test_hold_neutral(self):
        df = make_neutral_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 (< 30행)
    def test_insufficient_data(self):
        closes = list(np.linspace(100.0, 120.0, 20))
        df = _base_df(20, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 6. BUY HIGH confidence: trend_consistency > 0.6
    def test_buy_high_confidence(self):
        # 강한 단조 상승 → consistency 높음
        n = 50
        closes = list(np.linspace(100.0, 200.0, n))
        df = _base_df(n, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. SELL HIGH confidence
    def test_sell_high_confidence(self):
        n = 50
        closes = list(np.linspace(200.0, 100.0, n))
        df = _base_df(n, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. BUY entry_price = close of signal candle
    def test_buy_entry_price(self):
        df = make_uptrend_df()
        sig = self.strategy.generate(df)
        # 신호 봉(-2)의 close
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 9. SELL entry_price = close of signal candle
    def test_sell_entry_price(self):
        df = make_downtrend_df()
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 10. Signal 필드 완전성 (BUY)
    def test_signal_fields_buy(self):
        df = make_uptrend_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ["action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"]:
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 11. Signal 필드 완전성 (HOLD/insufficient)
    def test_signal_fields_hold(self):
        closes = list(np.linspace(100.0, 110.0, 15))
        df = _base_df(15, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 12. BUY reasoning 키워드
    def test_buy_reasoning_keyword(self):
        df = make_uptrend_df()
        sig = self.strategy.generate(df)
        assert "consistency" in sig.reasoning or "상승" in sig.reasoning

    # 13. SELL reasoning 키워드
    def test_sell_reasoning_keyword(self):
        df = make_downtrend_df()
        sig = self.strategy.generate(df)
        assert "consistency" in sig.reasoning or "하락" in sig.reasoning

    # 14. 정확히 MIN_ROWS 행에서 동작
    def test_exactly_min_rows(self):
        closes = list(np.linspace(100.0, 130.0, _MIN_ROWS))
        df = _base_df(_MIN_ROWS, closes)
        sig = self.strategy.generate(df)
        assert sig.action in [Action.BUY, Action.HOLD, Action.SELL]

    # 15. 상승 후 하락 전환 → SELL
    def test_reversal_to_sell(self):
        n = 60
        # 앞 30: 상승, 뒤 30: 하락
        up = list(np.linspace(100.0, 130.0, 30))
        down = list(np.linspace(130.0, 100.0, 30))
        closes = up + down
        df = _base_df(n, closes)
        sig = self.strategy.generate(df)
        # 하락 추세가 지배적이어야 함
        assert sig.action in [Action.SELL, Action.HOLD]
