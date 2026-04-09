"""
WilliamsFractalStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.williams_fractal import WilliamsFractalStrategy, _has_bullish_fractal, _has_bearish_fractal
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0, ema50: float = 95.0, rsi14: float = 45.0) -> pd.DataFrame:
    """기본 DataFrame 생성 (fractal 없음, 중립 상태)."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 1.0] * n,
        "low": [close - 1.0] * n,
        "volume": [1000.0] * n,
        "ema50": [ema50] * n,
        "atr14": [1.0] * n,
        "rsi14": [rsi14] * n,
    })


def _inject_bullish_fractal(df: pd.DataFrame, center: int) -> pd.DataFrame:
    """center 위치에 bullish fractal 주입 (중심 low가 주변 4봉보다 낮음)."""
    df = df.copy()
    low_val = float(df["low"].iloc[center - 1]) - 5.0  # 확실히 낮게
    df.iloc[center, df.columns.get_loc("low")] = low_val
    # 주변 4봉 low는 더 높게
    for j in [center - 2, center - 1, center + 1, center + 2]:
        if 0 <= j < len(df):
            df.iloc[j, df.columns.get_loc("low")] = low_val + 3.0
    return df


def _inject_bearish_fractal(df: pd.DataFrame, center: int) -> pd.DataFrame:
    """center 위치에 bearish fractal 주입 (중심 high가 주변 4봉보다 높음)."""
    df = df.copy()
    high_val = float(df["high"].iloc[center - 1]) + 5.0
    df.iloc[center, df.columns.get_loc("high")] = high_val
    for j in [center - 2, center - 1, center + 1, center + 2]:
        if 0 <= j < len(df):
            df.iloc[j, df.columns.get_loc("high")] = high_val - 3.0
    return df


class TestWilliamsFractalStrategy:

    def setup_method(self):
        self.strategy = WilliamsFractalStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "williams_fractal"

    # 2. 데이터 부족 (< 15행)
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. None 입력
    def test_none_input(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 4. HOLD: fractal 없는 중립 상태
    def test_hold_no_fractal(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "williams_fractal"

    # 5. BUY: bullish fractal + close > ema50
    def test_buy_bullish_fractal_above_ema50(self):
        df = _make_df(n=30, close=100.0, ema50=95.0, rsi14=45.0)
        # idx = len(df)-2 = 28, fractal center = 28-2=26
        idx = len(df) - 2
        df = _inject_bullish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price > 0

    # 6. BUY confidence HIGH when rsi < 50
    def test_buy_high_confidence_rsi_below_50(self):
        df = _make_df(n=30, close=100.0, ema50=95.0, rsi14=40.0)
        idx = len(df) - 2
        df = _inject_bullish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. BUY confidence MEDIUM when rsi >= 50
    def test_buy_medium_confidence_rsi_above_50(self):
        df = _make_df(n=30, close=100.0, ema50=95.0, rsi14=60.0)
        idx = len(df) - 2
        df = _inject_bullish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 8. HOLD: bullish fractal 있지만 close < ema50
    def test_hold_bullish_fractal_below_ema50(self):
        df = _make_df(n=30, close=90.0, ema50=95.0, rsi14=45.0)
        idx = len(df) - 2
        df = _inject_bullish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. SELL: bearish fractal + close < ema50
    def test_sell_bearish_fractal_below_ema50(self):
        df = _make_df(n=30, close=90.0, ema50=95.0, rsi14=60.0)
        idx = len(df) - 2
        df = _inject_bearish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price > 0

    # 10. SELL confidence HIGH when rsi > 50
    def test_sell_high_confidence_rsi_above_50(self):
        df = _make_df(n=30, close=90.0, ema50=95.0, rsi14=65.0)
        idx = len(df) - 2
        df = _inject_bearish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 11. SELL confidence MEDIUM when rsi <= 50
    def test_sell_medium_confidence_rsi_below_50(self):
        df = _make_df(n=30, close=90.0, ema50=95.0, rsi14=40.0)
        idx = len(df) - 2
        df = _inject_bearish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 12. HOLD: bearish fractal 있지만 close > ema50
    def test_hold_bearish_fractal_above_ema50(self):
        df = _make_df(n=30, close=100.0, ema50=95.0, rsi14=55.0)
        idx = len(df) - 2
        df = _inject_bearish_fractal(df, idx - 2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ["action", "confidence", "strategy", "entry_price", "reasoning", "invalidation", "bull_case", "bear_case"]:
            assert hasattr(sig, field)

    # 14. _has_bullish_fractal 헬퍼: idx < 4 경계
    def test_bullish_fractal_helper_too_small_idx(self):
        df = _make_df(n=10)
        found, level = _has_bullish_fractal(df, 3)
        assert found is False
        assert level is None

    # 15. _has_bearish_fractal 헬퍼: idx < 4 경계
    def test_bearish_fractal_helper_too_small_idx(self):
        df = _make_df(n=10)
        found, level = _has_bearish_fractal(df, 3)
        assert found is False
        assert level is None

    # 16. _has_bullish_fractal 헬퍼: 실제 fractal 감지
    def test_bullish_fractal_helper_detects_correctly(self):
        df = _make_df(n=20)
        df = _inject_bullish_fractal(df, 10)
        found, level = _has_bullish_fractal(df, 12)  # center=10, idx=12
        assert found is True
        assert level is not None

    # 17. _has_bearish_fractal 헬퍼: 실제 fractal 감지
    def test_bearish_fractal_helper_detects_correctly(self):
        df = _make_df(n=20)
        df = _inject_bearish_fractal(df, 10)
        found, level = _has_bearish_fractal(df, 12)  # center=10, idx=12
        assert found is True
        assert level is not None
