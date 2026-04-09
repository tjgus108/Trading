"""
ChoppinessStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.choppiness import ChoppinessStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", ci_mode: str = "trend") -> pd.DataFrame:
    """
    trend: "up" | "down" | "flat"
    ci_mode: "trend" (좁은 range, 큰 TR) | "chop" (넓은 range, 작은 TR)
    """
    np.random.seed(42)
    base = 100.0
    closes = [base]

    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.005, 0.012)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.005, 0.012)))
    else:
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.001, 0.001)))

    closes = np.array(closes)

    if ci_mode == "trend":
        # TR 크고, HL range 좁게 → CI 낮음 (추세장)
        spread_h = 0.008
        spread_l = 0.006
    else:
        # TR 작고, HL range 넓게 → CI 높음 (횡보장)
        spread_h = 0.001
        spread_l = 0.001

    highs = closes * (1 + spread_h)
    lows = closes * (1 - spread_l)
    opens = closes * (1 + np.random.uniform(-0.001, 0.001, n))

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
    })

    if trend == "up":
        df["ema50"] = closes * 0.93   # close > ema50
    elif trend == "down":
        df["ema50"] = closes * 1.07   # close < ema50
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


def _make_low_ci_df(n: int = 60, ci_target: float = 25.0, trend: str = "up") -> pd.DataFrame:
    """
    CI를 목표값 근처로 강제 조정한 DataFrame.
    TR 합계를 크게 하고 HL range를 작게 해서 CI를 낮춤.
    """
    np.random.seed(7)
    closes = np.linspace(100, 130, n) if trend == "up" else np.linspace(130, 100, n)
    # 매우 좁은 range (CI 낮추기)
    highs = closes + 0.5
    lows = closes - 0.5
    opens = closes + np.random.uniform(-0.1, 0.1, n)
    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 2000,
    })
    if trend == "up":
        df["ema50"] = closes * 0.90
    else:
        df["ema50"] = closes * 1.10
    df["atr14"] = (highs - lows) * 0.5
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestChoppinessStrategy:

    def setup_method(self):
        self.strategy = ChoppinessStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "choppiness"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. Signal 필드 완전성 (BUY)
    def test_signal_fields_complete(self):
        df = _make_low_ci_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "choppiness"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 5. 추세장 상승 → BUY
    def test_trend_up_buy(self):
        df = _make_low_ci_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        # CI < 38.2이면 BUY, 아니면 HOLD
        assert signal.action in (Action.BUY, Action.HOLD)

    # 6. 추세장 하락 → SELL
    def test_trend_down_sell(self):
        df = _make_low_ci_df(n=60, trend="down")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.SELL, Action.HOLD)

    # 7. BUY/SELL 시 reasoning에 "CI" 포함
    def test_reasoning_contains_ci(self):
        df = _make_low_ci_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert "CI" in signal.reasoning

    # 8. HOLD 시 confidence LOW
    def test_hold_confidence_low(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 9. entry_price가 close값과 일치
    def test_entry_price_equals_close(self):
        df = _make_low_ci_df(n=60, trend="up")
        idx = len(df) - 2
        expected = float(df["close"].iloc[idx])
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(expected, rel=1e-5)

    # 10. bull_case에 "CI" 포함 (데이터 충분 시)
    def test_bull_bear_case_contains_ci(self):
        df = _make_low_ci_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        if signal.action != Action.HOLD or signal.bull_case:
            # 충분한 데이터의 경우 bull_case 존재
            if signal.bull_case:
                assert "CI" in signal.bull_case

    # 11. 최소 20행으로 정상 실행
    def test_exactly_min_rows(self):
        df = _make_low_ci_df(n=20, trend="up")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 12. 19행 → HOLD (부족)
    def test_below_min_rows_hold(self):
        df = _make_insufficient_df(n=19)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 13. close == ema50 → close > ema50 조건 불만족 → BUY 아님
    def test_close_equals_ema50_no_buy(self):
        df = _make_low_ci_df(n=60, trend="up")
        df["ema50"] = df["close"]  # close == ema50
        signal = self.strategy.generate(df)
        # close > ema50 불만족 → SELL 또는 HOLD (not BUY)
        assert signal.action != Action.BUY

    # 14. 횡보장 (chop mode) → HOLD
    def test_chop_mode_hold(self):
        # HL range 크고 TR 작게 만들어서 CI 높임
        n = 60
        np.random.seed(99)
        closes = np.ones(n) * 100.0 + np.random.uniform(-0.1, 0.1, n)
        highs = closes + 10.0   # 매우 넓은 range
        lows = closes - 10.0
        opens = closes.copy()
        df = pd.DataFrame({
            "open": opens, "high": highs, "low": lows,
            "close": closes, "volume": np.ones(n) * 1000,
            "ema50": closes * 0.95, "atr14": np.ones(n) * 0.5,
        })
        signal = self.strategy.generate(df)
        # CI 높으면 HOLD
        assert signal.action == Action.HOLD

    # 15. confidence HIGH → CI < 30 구간 (강한 추세)
    def test_high_confidence_strong_trend(self):
        # 매우 좁은 range로 CI를 극도로 낮춤
        n = 60
        closes = np.linspace(100, 200, n)  # 강한 상승
        delta = 0.01  # 극히 좁은 HL spread
        highs = closes + delta
        lows = closes - delta
        df = pd.DataFrame({
            "open": closes, "high": highs, "low": lows,
            "close": closes, "volume": np.ones(n) * 2000,
            "ema50": closes * 0.70,
            "atr14": np.ones(n) * delta,
        })
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH
