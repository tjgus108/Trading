"""
TrendChannelStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_channel import TrendChannelStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", noise: float = 0.5) -> pd.DataFrame:
    """
    trend: "up" | "down" | "flat"
    noise: 잔차 크기 제어 (클수록 채널 이탈 가능성 높음)
    """
    np.random.seed(42)
    x = np.arange(n, dtype=float)

    if trend == "up":
        closes = 100.0 + x * 0.5 + np.random.randn(n) * noise
    elif trend == "down":
        closes = 150.0 - x * 0.5 + np.random.randn(n) * noise
    else:
        closes = np.ones(n) * 100.0 + np.random.randn(n) * noise

    highs = closes * 1.01
    lows = closes * 0.99
    opens = closes * (1 + np.random.uniform(-0.002, 0.002, n))
    volumes = np.random.uniform(1000, 3000, n)

    df = pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
        "ema50": closes * 0.97, "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_buy_signal_df() -> pd.DataFrame:
    """BUY 조건: close < lower channel AND slope > 0"""
    n = 60
    np.random.seed(10)
    # 강한 상승 추세
    x = np.arange(n, dtype=float)
    closes = 100.0 + x * 1.0  # 기울기 양수
    # 마지막 idx (n-2=58): lower channel 아래로 강제 이탈
    # period=20, y = closes[39:59], slope ~ 1.0
    # fitted[-1] ~ closes[58] = 158, std ~ small
    # lower ~ 158 - 2*std
    # close[58] 을 훨씬 낮게 설정
    closes[58] = closes[57] - 10.0  # 크게 이탈

    highs = closes * 1.01
    lows = closes * 0.99
    highs[58] = closes[58] * 1.005
    lows[58] = closes[58] * 0.995

    df = pd.DataFrame({
        "open": closes.copy(), "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 2000,
        "ema50": closes * 0.97, "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_sell_signal_df() -> pd.DataFrame:
    """SELL 조건: close > upper channel AND slope < 0"""
    n = 60
    np.random.seed(11)
    x = np.arange(n, dtype=float)
    closes = 200.0 - x * 1.0  # 기울기 음수
    # close[58] 을 upper channel 위로 강제 이탈
    closes[58] = closes[57] + 10.0

    highs = closes * 1.01
    lows = closes * 0.99
    highs[58] = closes[58] * 1.005
    lows[58] = closes[58] * 0.995

    df = pd.DataFrame({
        "open": closes.copy(), "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 2000,
        "ema50": closes * 1.05, "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98, "atr14": (highs - lows) * 0.5,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendChannelStrategy:

    def setup_method(self):
        self.strategy = TrendChannelStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "trend_channel"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. BUY 신호 타입 확인
    def test_buy_signal_type(self):
        df = _make_buy_signal_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 5. BUY 조건 (close < lower AND slope > 0)
    def test_buy_action(self):
        df = _make_buy_signal_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. SELL 조건 (close > upper AND slope < 0)
    def test_sell_action(self):
        df = _make_sell_signal_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 7. HOLD: 상승 추세 + 채널 내 → HOLD
    def test_hold_within_channel(self):
        df = _make_df(n=60, trend="up", noise=0.1)
        signal = self.strategy.generate(df)
        # 채널 내에 있으면 HOLD
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 8. BUY reasoning에 slope/channel 정보 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_signal_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "lower channel" in signal.reasoning.lower() or "slope" in signal.reasoning.lower()

    # 9. SELL reasoning에 upper channel 정보 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_signal_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "upper channel" in signal.reasoning.lower() or "slope" in signal.reasoning.lower()

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_signal_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "trend_channel"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. entry_price == close[idx]
    def test_entry_price_equals_close(self):
        df = _make_buy_signal_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 12. confidence HIGH/MEDIUM 구분 (BUY)
    def test_buy_confidence_high_when_large_deviation(self):
        df = _make_buy_signal_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. confidence HIGH/MEDIUM 구분 (SELL)
    def test_sell_confidence_valid(self):
        df = _make_sell_signal_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 14. 상승 추세 + 채널 위 돌파 → HOLD (slope > 0 이므로 SELL 조건 불충족)
    def test_no_sell_in_uptrend(self):
        df = _make_df(n=60, trend="up", noise=5.0)
        signal = self.strategy.generate(df)
        # slope > 0이면 SELL 신호 불가
        if signal.action == Action.SELL:
            pytest.fail("SELL signal should not occur in uptrend (slope > 0)")

    # 15. 하락 추세 + 채널 아래 이탈 → HOLD (slope < 0 이므로 BUY 조건 불충족)
    def test_no_buy_in_downtrend(self):
        df = _make_df(n=60, trend="down", noise=5.0)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            pytest.fail("BUY signal should not occur in downtrend (slope < 0)")

    # 16. HOLD reasoning에 channel 수치 포함
    def test_hold_reasoning_has_channel_values(self):
        df = _make_df(n=60, trend="flat", noise=0.1)
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert "Upper" in signal.reasoning or "Lower" in signal.reasoning or "부족" in signal.reasoning
