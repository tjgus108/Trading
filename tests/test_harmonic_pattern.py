"""
HarmonicPatternStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.harmonic_pattern import HarmonicPatternStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 25, close_prices=None) -> pd.DataFrame:
    if close_prices is None:
        close_prices = [100.0] * n
    highs = [c + 1.0 for c in close_prices]
    lows = [c - 1.0 for c in close_prices]
    return pd.DataFrame({
        "open": close_prices,
        "close": close_prices,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * len(close_prices),
    })


def _make_buy_df() -> pd.DataFrame:
    """
    BUY 조건 충족 DataFrame.
    A = close[-20] = 100, B = max(close[-10:]) = 150, C = min(close[-10:]) = 85,
    D(신호봉 close) = 150 + something with CD > 0 and ratios OK.

    AB = 50, BC = -65 → BC/AB = 1.3 (비율 범위 초과)

    대신 명시적으로 조건 충족:
    A=100, B=160, C=100 (B-50*0.7=125... 재계산)
    AB = 60, BC = -60, BC/AB = 1.0 (여전히 초과)

    비율을 맞추려면:
    A=100, B=150 → AB=50
    BC/AB = 0.618 → BC = 30.9, C = B - BC = 119.1
    CD/BC = 1.618 → CD = 49.99, D = C + CD = 169.09  (CD > 0 → BUY)

    idx = len(df)-2 기준으로:
    close[-20] = A = 100
    close[-10:].max() = B = 150  (인덱스 -11 ~ -2)
    close[-10:].min() = C = 119.1
    close[-2] = D = 169.09
    """
    n = 25  # 최소 20 + 여유
    closes = [100.0] * (n - 13)  # A 위치들 (이전 봉들)
    # close[-20] (완성봉 기준) = A = 100
    # 중간 봉들 채우기
    # 완성봉 = df.iloc[-2], completed = df.iloc[:idx+1] = df.iloc[:-1]
    # completed.close.iloc[-20] = A
    # completed.close.iloc[-10:].max() = B = 150
    # completed.close.iloc[-10:].min() = C = 119.1
    # completed.close.iloc[-2] = D

    # 전략에서: idx = len(df)-2, completed = df.iloc[:idx+1]
    # completed.iloc[-20] = df.iloc[idx-19]
    # completed.iloc[-10:] = df.iloc[idx-9:idx+1]

    # n=25, idx=23
    # completed = df.iloc[:24] (24행)
    # completed.iloc[-20] = df.iloc[4] = A
    # completed.iloc[-10:] = df.iloc[14:24]

    closes = [100.0] * n
    closes[4] = 100.0  # A
    # B = max(iloc[14:24]) = 150
    for i in range(14, 24):
        closes[i] = 119.1  # C 값으로 채움
    closes[14] = 150.0  # B (최고)
    closes[23] = 169.09  # D (신호봉, idx=23=n-2)
    closes[24] = 170.0   # 진행 중 봉 (무시)

    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_sell_df() -> pd.DataFrame:
    """
    SELL 조건 충족 DataFrame.
    A=100, B=150, AB=50
    BC/AB = 0.618 → BC=-30.9, C=119.1
    CD/BC = 1.618 → CD=-49.99, D=69.1  (CD < 0 → SELL)
    """
    n = 25
    closes = [100.0] * n
    closes[4] = 100.0   # A
    for i in range(14, 24):
        closes[i] = 119.1
    closes[14] = 150.0  # B (max)
    closes[23] = 69.1   # D (신호봉, CD < 0)
    closes[24] = 68.0   # 진행 중 봉

    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


class TestHarmonicPatternStrategy:

    def setup_method(self):
        self.strat = HarmonicPatternStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "harmonic_pattern"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=15)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 최소 행(20) - Signal 반환 (HOLD 포함)
    def test_exactly_min_rows_returns_signal(self):
        # n=20: completed=19행 → iloc[-20] out-of-bounds → HOLD 반환
        df = _make_df(n=20)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.HOLD  # completed < 20 → HOLD

    # 4. Signal 객체 반환 확인
    def test_returns_signal_object(self):
        df = _make_df(n=25)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=25)
        sig = self.strat.generate(df)
        assert sig.reasoning != ""

    # 6. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=25)
        sig = self.strat.generate(df)
        assert sig.entry_price > 0

    # 7. strategy 필드
    def test_strategy_field(self):
        df = _make_df(n=25)
        sig = self.strat.generate(df)
        assert sig.strategy == "harmonic_pattern"

    # 8. BUY 조건 - action 확인
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 조건 - action 확인
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. HOLD: AB=0 일 때
    def test_hold_ab_zero(self):
        n = 25
        # A와 B가 같은 값 → AB=0
        closes = [100.0] * n
        df = _make_df(n=n, close_prices=closes)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 11. confidence는 HIGH 또는 MEDIUM
    def test_confidence_valid_values(self):
        df = _make_buy_df()
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. BUY 신호 시 entry_price = 신호봉 close
    def test_buy_entry_price_equals_close(self):
        df = _make_buy_df()
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            # idx = len(df)-2 = 23, close = 169.09
            assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]), rel=1e-4)

    # 13. HOLD 시 entry_price = 신호봉 close
    def test_hold_entry_price_equals_close(self):
        df = _make_df(n=25)
        sig = self.strat.generate(df)
        if sig.action == Action.HOLD:
            assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]), rel=1e-4)

    # 14. 데이터 19행 (최소-1) → HOLD
    def test_one_below_min_rows(self):
        df = _make_df(n=19)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning
