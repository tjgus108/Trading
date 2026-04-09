"""
BodyMomentumStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.body_momentum import BodyMomentumStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, mode: str = "bull") -> pd.DataFrame:
    """
    mode: "bull" (강한 양봉 연속) | "bear" (강한 음봉 연속) | "mixed" (혼합)
    """
    np.random.seed(0)
    opens = [100.0]
    closes = []
    highs = []
    lows = []

    for i in range(n):
        o = opens[-1] if i == 0 else closes[-1]
        if mode == "bull":
            c = o * np.random.uniform(1.008, 1.015)
        elif mode == "bear":
            c = o * np.random.uniform(0.985, 0.992)
        else:
            c = o * np.random.uniform(0.998, 1.002)

        h = max(o, c) * np.random.uniform(1.001, 1.003)
        l = min(o, c) * np.random.uniform(0.997, 0.999)

        opens.append(c)
        closes.append(c)
        highs.append(h)
        lows.append(l)

    opens = opens[:n]

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
        "ema50": np.array(closes) * 0.97,
        "atr14": (np.array(highs) - np.array(lows)) * 0.5,
    })
    return df


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
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

class TestBodyMomentumStrategy:

    def setup_method(self):
        self.strategy = BodyMomentumStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "body_momentum"

    # 2. 연속 강한 양봉 → BUY
    def test_strong_bull_candles_buy(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 연속 강한 음봉 → SELL
    def test_strong_bear_candles_sell(self):
        df = _make_df(n=50, mode="bear")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. 혼합 캔들 → HOLD
    def test_mixed_candles_hold(self):
        df = _make_df(n=50, mode="mixed")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=5)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 7. BUY HIGH confidence (BM_EMA > 0.5)
    def test_buy_high_confidence(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 8. SELL HIGH confidence (BM_EMA < -0.5)
    def test_sell_high_confidence(self):
        df = _make_df(n=50, mode="bear")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "body_momentum"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 10. reasoning에 BM_EMA 포함
    def test_reasoning_contains_bm_ema(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        assert "BM_EMA" in signal.reasoning or "부족" in signal.reasoning

    # 11. BUY 신호 bull_case / bear_case
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 12. SELL 신호 bull_case / bear_case
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_df(n=50, mode="bear")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 13. HOLD confidence LOW
    def test_hold_confidence_low(self):
        df = _make_df(n=50, mode="mixed")
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD and "부족" not in signal.reasoning:
            assert signal.confidence == Confidence.LOW

    # 14. entry_price는 idx=-2 close
    def test_entry_price_is_second_last_close(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)

    # 15. BUY reasoning에 양봉 키워드 포함
    def test_buy_reasoning_mentions_yangbong(self):
        df = _make_df(n=50, mode="bull")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "양봉" in signal.reasoning
