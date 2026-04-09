"""
RSquaredStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.r_squared import RSquaredStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", r_sq_target: str = "high") -> pd.DataFrame:
    """
    trend: "up" | "down" | "flat"
    r_sq_target: "high" (R²>0.85) | "medium" (0.7<R²<0.85) | "low" (R²<0.3)
    """
    np.random.seed(42)

    if r_sq_target == "high":
        noise = 0.0005
    elif r_sq_target == "medium":
        noise = 0.005
    else:
        noise = 0.05  # 횡보: 높은 노이즈

    closes = [100.0]
    for i in range(n - 1):
        if trend == "up":
            delta = 0.5 + np.random.uniform(-noise * 100, noise * 100)
        elif trend == "down":
            delta = -0.5 + np.random.uniform(-noise * 100, noise * 100)
        else:
            delta = np.random.uniform(-noise * 100, noise * 100)
        closes.append(closes[-1] + delta)

    closes = np.array(closes)
    highs = closes + np.abs(np.random.normal(0, 0.2, n))
    lows = closes - np.abs(np.random.normal(0, 0.2, n))
    opens = closes + np.random.uniform(-0.1, 0.1, n)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
    })

    if trend == "up":
        df["ema50"] = closes * 0.97
    elif trend == "down":
        df["ema50"] = closes * 1.03
    else:
        df["ema50"] = closes

    df["atr14"] = (highs - lows) * 0.5
    return df


def _make_insufficient_df(n: int = 15) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98,
        "atr14": (highs - lows) * 0.5,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestRSquaredStrategy:

    def setup_method(self):
        self.strategy = RSquaredStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "r_squared"

    # 2. 강한 상승 추세 → BUY
    def test_strong_uptrend_buy(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 강한 하락 추세 → SELL
    def test_strong_downtrend_sell(self):
        df = _make_df(n=60, trend="down", r_sq_target="high")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. 횡보장 → HOLD (R² < 0.7)
    def test_sideways_hold(self):
        df = _make_df(n=60, trend="flat", r_sq_target="low")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 7. BUY HIGH confidence (R² > 0.85)
    def test_buy_high_confidence(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "r_squared"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 9. reasoning에 R² 포함
    def test_reasoning_contains_r_sq(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        signal = self.strategy.generate(df)
        assert "R²" in signal.reasoning or "부족" in signal.reasoning

    # 10. ema50 방향 불일치 → HOLD (상승 추세지만 close < ema50)
    def test_uptrend_ema50_misalign_hold(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        df["ema50"] = df["close"] * 1.10  # close < ema50 강제
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. ema50 방향 불일치 → HOLD (하락 추세지만 close > ema50)
    def test_downtrend_ema50_misalign_hold(self):
        df = _make_df(n=60, trend="down", r_sq_target="high")
        df["ema50"] = df["close"] * 0.90  # close > ema50 강제
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 12. BUY 신호에 bull_case / bear_case 포함
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 13. SELL 신호에 bull_case / bear_case 포함
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_df(n=60, trend="down", r_sq_target="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 14. 횡보 HOLD confidence LOW
    def test_sideways_confidence_low(self):
        df = _make_df(n=60, trend="flat", r_sq_target="low")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 15. entry_price는 idx=-2 close
    def test_entry_price_is_second_last_close(self):
        df = _make_df(n=60, trend="up", r_sq_target="high")
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)
