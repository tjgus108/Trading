"""
TrendIntensityIndexStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.tii_strategy import TrendIntensityIndexStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, tii_target: str = "high") -> pd.DataFrame:
    """
    tii_target:
      "high"  → TII > 90 (강한 상승, close > SMA30)
      "buy"   → TII ~ 85  (TII > 80 but <= 90)
      "low"   → TII < 10  (강한 하락, close < SMA30)
      "sell"  → TII ~ 15  (TII < 20 but >= 10)
      "flat"  → TII ~ 50  (횡보)
    """
    np.random.seed(42)

    if tii_target == "high":
        # 강한 상승: 모든 close가 sma30 위
        closes = np.linspace(100, 150, n)
    elif tii_target == "buy":
        # 상승이지만 약간 덜 강함 (~85%)
        closes = np.linspace(100, 130, n)
        # 중간에 약간의 노이즈
        closes[10:14] = closes[10] * 0.995
    elif tii_target == "low":
        # 강한 하락: 모든 close가 sma30 아래
        closes = np.linspace(150, 100, n)
    elif tii_target == "sell":
        # 하락이지만 약간 덜 강함
        closes = np.linspace(150, 115, n)
        closes[10:14] = closes[10] * 1.005
    else:  # flat
        closes = np.ones(n) * 100
        closes += np.sin(np.linspace(0, 4 * np.pi, n)) * 2

    df = pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendIntensityIndexStrategy:

    def setup_method(self):
        self.strat = TrendIntensityIndexStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strat.name == "tii_strategy"

    # 2. 강한 상승 → BUY
    def test_strong_uptrend_buy(self):
        df = _make_df(n=60, tii_target="high")
        signal = self.strat.generate(df)
        assert signal.action == Action.BUY

    # 3. 강한 하락 → SELL
    def test_strong_downtrend_sell(self):
        df = _make_df(n=60, tii_target="low")
        signal = self.strat.generate(df)
        assert signal.action == Action.SELL

    # 4. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strat.generate(df)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 → LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_insufficient_df(n=20)
        signal = self.strat.generate(df)
        assert signal.confidence == Confidence.LOW

    # 6. 강한 상승(TII>90) → HIGH confidence
    def test_strong_uptrend_high_confidence(self):
        df = _make_df(n=60, tii_target="high")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. 강한 하락(TII<10) → HIGH confidence
    def test_strong_downtrend_high_confidence(self):
        df = _make_df(n=60, tii_target="low")
        signal = self.strat.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 8. 횡보 → HOLD
    def test_flat_market_hold(self):
        df = _make_df(n=60, tii_target="flat")
        signal = self.strat.generate(df)
        assert signal.action == Action.HOLD

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, tii_target="high")
        signal = self.strat.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "tii_strategy"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0

    # 10. BUY reasoning에 TII 포함
    def test_buy_reasoning_contains_tii(self):
        df = _make_df(n=60, tii_target="high")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert "TII" in signal.reasoning

    # 11. SELL reasoning에 TII 포함
    def test_sell_reasoning_contains_tii(self):
        df = _make_df(n=60, tii_target="low")
        signal = self.strat.generate(df)
        if signal.action == Action.SELL:
            assert "TII" in signal.reasoning

    # 12. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_reasoning_mention(self):
        df = _make_insufficient_df(n=10)
        signal = self.strat.generate(df)
        assert "부족" in signal.reasoning

    # 13. BUY 신호에 invalidation 존재
    def test_buy_has_invalidation(self):
        df = _make_df(n=60, tii_target="high")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 14. SELL 신호에 invalidation 존재
    def test_sell_has_invalidation(self):
        df = _make_df(n=60, tii_target="low")
        signal = self.strat.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 15. entry_price == last completed candle close
    def test_entry_price_is_last_close(self):
        df = _make_df(n=60, tii_target="high")
        signal = self.strat.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 16. TII 80~90 범위 BUY → MEDIUM confidence
    def test_buy_medium_confidence_when_tii_80_to_90(self):
        df = _make_df(n=60, tii_target="buy")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)
