"""
PivotPointStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.pivot_point import PivotPointStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_val: float = None, prev_high: float = 110.0,
             prev_low: float = 90.0, prev_close: float = 100.0) -> pd.DataFrame:
    """
    피벗 포인트 테스트용 DataFrame.
    idx = len(df)-2 위치의 이전 봉(shift(1))이 prev_high/low/close가 되도록 설계.
    - df.iloc[idx-1]: prev_high/low/close
    - df.iloc[idx]:   close_val
    """
    np.random.seed(42)
    n = max(n, 5)

    # 기본 가격 생성
    closes = np.linspace(100.0, 100.0, n)
    highs = closes * 1.05
    lows = closes * 0.95
    opens = closes.copy()
    volumes = np.ones(n) * 1000.0

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })

    # idx = len(df) - 2
    idx = len(df) - 2

    # idx-1 봉: shift(1) 대상 → prev 값 설정
    df.at[idx - 1, "high"] = prev_high
    df.at[idx - 1, "low"] = prev_low
    df.at[idx - 1, "close"] = prev_close

    # idx 봉: 현재 완성 캔들
    if close_val is not None:
        df.at[idx, "close"] = close_val
        df.at[idx, "open"] = close_val * 0.999
        df.at[idx, "high"] = close_val * 1.01
        df.at[idx, "low"] = close_val * 0.99

    return df


def _pivot_levels(prev_high, prev_low, prev_close):
    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = 2 * pivot - prev_low
    s1 = 2 * pivot - prev_high
    r2 = pivot + (prev_high - prev_low)
    s2 = pivot - (prev_high - prev_low)
    return pivot, r1, s1, r2, s2


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPivotPointStrategy:

    def setup_method(self):
        self.strategy = PivotPointStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "pivot_point"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=5)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. BUY 신호: close > pivot AND close > r1
    def test_buy_signal_above_r1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        # close를 r1 위로 설정
        close_val = r1 + 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 5. SELL 신호: close < pivot AND close < s1
    def test_sell_signal_below_s1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = s1 - 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 6. BUY HIGH confidence when close > r2
    def test_buy_high_confidence_above_r2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = r2 + 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY
        assert signal.confidence == Confidence.HIGH

    # 7. BUY MEDIUM confidence when pivot < close <= r2
    def test_buy_medium_confidence_between_r1_r2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = r1 + 0.5  # between r1 and r2
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 8. SELL HIGH confidence when close < s2
    def test_sell_high_confidence_below_s2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = s2 - 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.HIGH

    # 9. SELL MEDIUM confidence when s2 <= close < s1
    def test_sell_medium_confidence_between_s2_s1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = s1 - 0.5  # between s2 and s1
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.MEDIUM

    # 10. HOLD when close is between s1 and r1
    def test_hold_between_support_resistance(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = pivot  # exactly at pivot
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = r1 + 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "pivot_point"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 12. BUY 신호 reasoning에 "피벗" 포함
    def test_buy_reasoning_contains_pivot(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = r1 + 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "피벗" in signal.reasoning

    # 13. SELL 신호 reasoning에 "피벗" 포함
    def test_sell_reasoning_contains_pivot(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = s1 - 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "피벗" in signal.reasoning

    # 14. BUY 신호 entry_price == close
    def test_buy_entry_price_equals_close(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = r1 + 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert abs(signal.entry_price - close_val) < 1e-6

    # 15. SELL 신호 bull_case/bear_case 포함
    def test_sell_signal_has_bull_bear_case(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = s1 - 1.0
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. HOLD confidence는 LOW
    def test_hold_confidence_low(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, r1, s1, r2, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        close_val = pivot
        df = _make_df(close_val=close_val, prev_high=prev_high,
                      prev_low=prev_low, prev_close=prev_close)
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert signal.confidence == Confidence.LOW
