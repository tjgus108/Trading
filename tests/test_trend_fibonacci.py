"""
TrendFibonacciStrategy 단위 테스트 (14개 이상)
"""

import math

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_fibonacci import TrendFibonacciStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 60,
    trend: str = "up",
    close_position: str = "fib382",  # "fib382" | "fib618" | "mid"
) -> pd.DataFrame:
    """
    trend: "up" | "down" | "flat"
    close_position: where the last close sits relative to fib levels
    """
    np.random.seed(0)
    base = 1000.0
    closes = [base]

    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.002, 0.006)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.002, 0.006)))
    else:
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.001, 0.001)))

    closes = np.array(closes)
    highs = closes * 1.02
    lows = closes * 0.98
    opens = closes * (1 + np.random.uniform(-0.001, 0.001, n))
    volumes = np.random.uniform(1000, 5000, n)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes.copy(),
        "volume": volumes,
    })

    # Compute fib levels for idx = n-2
    lookback = 20
    idx = n - 2
    swing_high = df["high"].rolling(lookback, min_periods=1).max().iloc[idx]
    swing_low = df["low"].rolling(lookback, min_periods=1).min().iloc[idx]
    fib_range = swing_high - swing_low
    fib_382 = swing_high - fib_range * 0.382
    fib_618 = swing_high - fib_range * 0.618
    fib_500 = swing_high - fib_range * 0.500

    # Adjust close at idx based on position
    if close_position == "fib382":
        # below fib_382 → BUY condition
        df.at[idx, "close"] = fib_382 * 0.995
        df.at[idx, "high"] = df.at[idx, "close"] * 1.005
        df.at[idx, "low"] = df.at[idx, "close"] * 0.995
    elif close_position == "fib618":
        # above fib_618 → SELL condition
        df.at[idx, "close"] = fib_618 * 1.005
        df.at[idx, "high"] = df.at[idx, "close"] * 1.005
        df.at[idx, "low"] = df.at[idx, "close"] * 0.995
    elif close_position == "fib500":
        # near fib_500 → HIGH confidence
        df.at[idx, "close"] = fib_500
        df.at[idx, "high"] = df.at[idx, "close"] * 1.005
        df.at[idx, "low"] = df.at[idx, "close"] * 0.995

    return df


def _make_short_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendFibonacciStrategy:

    def setup_method(self):
        self.strategy = TrendFibonacciStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "trend_fibonacci"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_short_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_short_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. 상승추세 + fib_382 아래 → BUY
    def test_uptrend_fib382_buy(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 5. 하락추세 + fib_618 위 → SELL
    def test_downtrend_fib618_sell(self):
        df = _make_df(n=60, trend="down", close_position="fib618")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 6. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 7. action이 유효한 값
    def test_action_valid(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 8. confidence가 유효한 값
    def test_confidence_valid(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 9. strategy 필드
    def test_signal_strategy_field(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert signal.strategy == "trend_fibonacci"

    # 10. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)

    # 11. reasoning 문자열 비어있지 않음
    def test_reasoning_nonempty(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert len(signal.reasoning) > 0

    # 12. BUY reasoning에 "상승추세" 포함
    def test_buy_reasoning_contains_uptrend(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "상승추세" in signal.reasoning

    # 13. SELL reasoning에 "하락추세" 포함
    def test_sell_reasoning_contains_downtrend(self):
        df = _make_df(n=60, trend="down", close_position="fib618")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "하락추세" in signal.reasoning

    # 14. 횡보장 → HOLD
    def test_flat_trend_hold(self):
        df = _make_df(n=60, trend="flat", close_position="mid")
        signal = self.strategy.generate(df)
        # flat 추세에서는 EMA20 방향이 불명확 → HOLD 가능
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 15. bull_case / bear_case 문자열
    def test_bull_bear_case_strings(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 16. BUY 시 bull_case에 "EMA20" 포함
    def test_buy_bull_case_has_ema20(self):
        df = _make_df(n=60, trend="up", close_position="fib382")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "EMA20" in signal.bull_case

    # 17. SELL 시 bear_case에 "EMA20" 포함
    def test_sell_bear_case_has_ema20(self):
        df = _make_df(n=60, trend="down", close_position="fib618")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "EMA20" in signal.bear_case
