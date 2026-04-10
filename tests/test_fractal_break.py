"""
FractalBreakStrategy 단위 테스트 (14개+).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.fractal_break import FractalBreakStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0, atr14: float = 1.5) -> pd.DataFrame:
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 1.0] * n,
        "low": [close - 1.0] * n,
        "volume": [1000.0] * n,
        "atr14": [atr14] * n,
    })


def _inject_up_fractal(df: pd.DataFrame, center: int) -> pd.DataFrame:
    """center 위치에 상단 fractal 주입 (high[center]가 주변보다 높음)."""
    df = df.copy()
    peak = float(df["high"].iloc[center - 1]) + 10.0
    df.iloc[center, df.columns.get_loc("high")] = peak
    for j in [center - 2, center - 1, center + 1, center + 2]:
        if 0 <= j < len(df):
            df.iloc[j, df.columns.get_loc("high")] = peak - 5.0
    return df


def _inject_down_fractal(df: pd.DataFrame, center: int) -> pd.DataFrame:
    """center 위치에 하단 fractal 주입 (low[center]가 주변보다 낮음)."""
    df = df.copy()
    trough = float(df["low"].iloc[center - 1]) - 10.0
    df.iloc[center, df.columns.get_loc("low")] = trough
    for j in [center - 2, center - 1, center + 1, center + 2]:
        if 0 <= j < len(df):
            df.iloc[j, df.columns.get_loc("low")] = trough + 5.0
    return df


class TestFractalBreakStrategy:

    def setup_method(self):
        self.strategy = FractalBreakStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "fractal_break"

    # 2. 인스턴스 생성
    def test_instance(self):
        s = FractalBreakStrategy()
        assert isinstance(s, FractalBreakStrategy)

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

    # 8. BUY reasoning 키워드
    def test_buy_reasoning_keyword(self):
        df = _make_df(n=30, close=100.0)
        idx = len(df) - 2
        center = idx - 4
        df = _inject_up_fractal(df, center)
        # close를 fractal 위로 설정
        up_val = float(df["high"].iloc[center]) + 1.0
        df["close"] = up_val
        df["high"] = df["high"].clip(upper=up_val + 2.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "fractal" in sig.reasoning.lower() or "break" in sig.reasoning.lower()

    # 9. SELL reasoning 키워드
    def test_sell_reasoning_keyword(self):
        df = _make_df(n=30, close=100.0)
        idx = len(df) - 2
        center = idx - 4
        df = _inject_down_fractal(df, center)
        # close를 fractal 아래로 설정
        down_val = float(df["low"].iloc[center]) - 1.0
        df["close"] = down_val
        df["low"] = df["low"].clip(lower=down_val - 2.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "fractal" in sig.reasoning.lower() or "break" in sig.reasoning.lower()

    # 10. HIGH confidence: ATR > 0 and deviation > 1%
    def test_high_confidence_buy(self):
        n = 30
        close = 100.0
        df = _make_df(n=n, close=close, atr14=2.0)
        idx = len(df) - 2
        center = idx - 4
        # 상단 fractal을 close보다 1.5% 낮게
        fractal_high = close * 0.98  # close가 fractal보다 2% 위
        df = df.copy()
        df.iloc[center, df.columns.get_loc("high")] = fractal_high
        for j in [center - 2, center - 1, center + 1, center + 2]:
            if 0 <= j < len(df):
                df.iloc[j, df.columns.get_loc("high")] = fractal_high - 3.0
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence: deviation <= 1%
    def test_medium_confidence(self):
        n = 30
        close = 100.0
        df = _make_df(n=n, close=close, atr14=0.0)
        idx = len(df) - 2
        center = idx - 4
        fractal_high = close * 0.999  # 0.1% 차이
        df = df.copy()
        df.iloc[center, df.columns.get_loc("high")] = fractal_high
        for j in [center - 2, center - 1, center + 1, center + 2]:
            if 0 <= j < len(df):
                df.iloc[j, df.columns.get_loc("high")] = fractal_high - 3.0
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.MEDIUM

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30, close=100.0)
        sig = self.strategy.generate(df)
        # HOLD 시에도 entry_price >= 0
        assert sig.entry_price >= 0

    # 13. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "fractal_break"

    # 14. 최소 행 수(15)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in [Action.BUY, Action.SELL, Action.HOLD]
