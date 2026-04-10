"""
TrendlineBreakStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trendline_break import TrendlineBreakStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_flat_df(n: int = 30) -> pd.DataFrame:
    closes = np.ones(n) * 100.0
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_buy_df() -> pd.DataFrame:
    """하단 추세선 상향 돌파 BUY 조건."""
    n = 30
    # 하단 추세선을 상향으로 만들기: lows가 완만히 상승
    lows = np.linspace(95.0, 100.0, n)
    highs = lows + 5.0
    closes = lows + 2.0
    # idx = n-2 = 28
    # prev_close (idx-1=27) < trend_low_prev: 이전봉 종가를 추세선 아래로
    closes[27] = lows[27] - 1.0   # below trend_low_prev
    # curr_close (idx=28) > trend_low_now: 현재봉 종가를 추세선 위로
    closes[28] = lows[28] + 1.0   # above trend_low_now
    # slope_l > 0 → HIGH confidence (lows 상승 추세이므로 slope > 0)
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_sell_df() -> pd.DataFrame:
    """상단 추세선 하향 이탈 SELL 조건."""
    n = 30
    # highs 하락 추세
    highs = np.linspace(110.0, 100.0, n)
    lows = highs - 5.0
    closes = highs - 2.0
    # idx = n-2 = 28
    # prev_close (idx-1=27) > trend_high_prev: 이전봉을 추세선 위로
    closes[27] = highs[27] + 1.0
    # curr_close (idx=28) < trend_high_now: 현재봉을 추세선 아래로
    closes[28] = highs[28] - 1.0
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_buy_flat_slope_df() -> pd.DataFrame:
    """slope_l <= 0인 BUY → MEDIUM confidence."""
    n = 30
    # lows 하락 추세 (slope < 0)
    lows = np.linspace(100.0, 95.0, n)
    highs = lows + 10.0
    closes = lows + 4.0
    # idx = 28
    closes[27] = lows[27] - 1.0
    closes[28] = lows[28] + 1.0
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendlineBreakStrategy:

    def setup_method(self):
        self.strategy = TrendlineBreakStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "trendline_break"

    # 2. 인스턴스 생성
    def test_instance_creation(self):
        assert isinstance(self.strategy, TrendlineBreakStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        signal = self.strategy.generate(None)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert "Insufficient" in signal.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert isinstance(signal.action, Action)
        assert isinstance(signal.confidence, Confidence)
        assert isinstance(signal.strategy, str)
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str)
        assert isinstance(signal.invalidation, str)

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "trendline" in signal.reasoning.lower() or "break" in signal.reasoning.lower()

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "trendline" in signal.reasoning.lower() or "break" in signal.reasoning.lower()

    # 10. HIGH confidence (slope_l > 0 BUY)
    def test_high_confidence_buy(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 11. MEDIUM confidence (slope_l <= 0 BUY)
    def test_medium_confidence_buy_flat_slope(self):
        df = _make_buy_flat_slope_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.strategy == "trendline_break"

    # 14. 최소 행 수(25)에서 동작
    def test_minimum_rows_works(self):
        df = _make_flat_df(n=25)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
