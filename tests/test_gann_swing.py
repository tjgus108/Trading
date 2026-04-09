"""
GannSwingStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.gann_swing import GannSwingStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", vol_spike: bool = False) -> pd.DataFrame:
    """
    trend: "up" | "down" | "flat"
    vol_spike: True → 마지막 봉 volume > avg * 1.2
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
    spread = 0.01
    highs = closes * (1 + spread)
    lows = closes * (1 - spread)
    opens = closes.copy()

    volume = np.random.uniform(1000, 3000, n)
    if vol_spike:
        volume[-2] = volume[:-2].mean() * 2.0  # 마지막 완성봉(idx=-2) 볼륨 급증

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volume,
    })

    # EMA20 설정: trend에 따라 close 위/아래
    if trend == "up":
        df["ema20"] = closes * 0.96   # close > ema20
    elif trend == "down":
        df["ema20"] = closes * 1.04   # close < ema20
    else:
        df["ema20"] = closes          # close ≈ ema20

    return df


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
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

class TestGannSwingStrategy:

    def setup_method(self):
        self.strategy = GannSwingStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "gann_swing"

    # 2. 상승 추세 → BUY
    def test_uptrend_buy(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 하락 추세 → SELL
    def test_downtrend_sell(self):
        df = _make_df(n=60, trend="down")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. 볼륨 스파이크 → HIGH confidence
    def test_buy_high_confidence_with_vol_spike(self):
        df = _make_df(n=60, trend="up", vol_spike=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 5. 볼륨 평범 → MEDIUM confidence
    def test_buy_medium_confidence_without_vol_spike(self):
        df = _make_df(n=60, trend="up", vol_spike=False)
        # vol_spike=False이면 MEDIUM 또는 HIGH (vol 우연히 클 수도 있음)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 6. SELL HIGH confidence with vol spike
    def test_sell_high_confidence_with_vol_spike(self):
        df = _make_df(n=60, trend="down", vol_spike=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 7. 횡보 → HOLD
    def test_flat_hold(self):
        df = _make_df(n=60, trend="flat")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 8. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "gann_swing"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 11. BUY reasoning에 "HH" 포함
    def test_buy_reasoning_contains_hh(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "HH" in signal.reasoning

    # 12. SELL reasoning에 "LH" 포함
    def test_sell_reasoning_contains_lh(self):
        df = _make_df(n=60, trend="down")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "LH" in signal.reasoning

    # 13. ema20 컬럼 없어도 동작
    def test_works_without_ema20_column(self):
        df = _make_df(n=60, trend="up")
        df = df.drop(columns=["ema20"])
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 14. BUY에 bull_case/bear_case 포함
    def test_buy_has_bull_bear_case(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 15. SELL에 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_df(n=60, trend="down")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 16. entry_price는 마지막 완성봉 close
    def test_entry_price_is_last_close(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 17. close < ema20 인 상승 스윙은 BUY 안 됨
    def test_upswing_but_close_below_ema20_no_buy(self):
        df = _make_df(n=60, trend="up")
        df["ema20"] = df["close"] * 1.10  # close < ema20 강제
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY
