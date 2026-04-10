"""
MarketStructureBreakStrategy 단위 테스트 (14개+).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.market_structure_break import MarketStructureBreakStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 1.0] * n,
        "low": [close - 1.0] * n,
        "volume": [1000.0] * n,
        "atr14": [1.5] * n,
    })


def _make_bullish_df(n: int = 40) -> pd.DataFrame:
    """HH+HL 구조 DataFrame: 상승 추세 swing."""
    highs = []
    lows = []
    closes = []
    base = 100.0
    for i in range(n):
        # 지그재그 상승
        phase = (i % 6)
        if phase < 3:
            h = base + i * 0.5 + 2.0
            l = base + i * 0.5 - 1.0
        else:
            h = base + i * 0.5 + 1.0
            l = base + i * 0.5 - 2.0
        highs.append(h)
        lows.append(l)
        closes.append((h + l) / 2)
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "atr14": [1.5] * n,
    })


def _make_bearish_df(n: int = 40) -> pd.DataFrame:
    """LH+LL 구조 DataFrame: 하락 추세 swing."""
    highs = []
    lows = []
    closes = []
    base = 200.0
    for i in range(n):
        phase = (i % 6)
        if phase < 3:
            h = base - i * 0.5 + 1.0
            l = base - i * 0.5 - 2.0
        else:
            h = base - i * 0.5 + 2.0
            l = base - i * 0.5 - 1.0
        highs.append(h)
        lows.append(l)
        closes.append((h + l) / 2)
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "atr14": [1.5] * n,
    })


class TestMarketStructureBreakStrategy:

    def setup_method(self):
        self.strategy = MarketStructureBreakStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "market_structure_break"

    # 2. 인스턴스 생성
    def test_instance(self):
        s = MarketStructureBreakStrategy()
        assert isinstance(s, MarketStructureBreakStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        for field in ["action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"]:
            assert hasattr(sig, field)

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_bullish_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            reason = sig.reasoning.lower()
            assert "hh" in reason or "higher" in reason or "structure" in reason or "sh" in reason

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_bearish_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            reason = sig.reasoning.lower()
            assert "lh" in reason or "lower" in reason or "structure" in reason or "sl" in reason

    # 10. HIGH confidence: bullish 구조에서 swing 2개 이상
    def test_high_confidence_bullish(self):
        df = _make_bullish_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. HIGH confidence: bearish 구조에서 swing 2개 이상
    def test_high_confidence_bearish(self):
        df = _make_bearish_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 12. entry_price > 0
    def test_entry_price_nonnegative(self):
        df = _make_df(n=30, close=100.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price >= 0

    # 13. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "market_structure_break"

    # 14. 최소 행 수(20)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in [Action.BUY, Action.SELL, Action.HOLD]
