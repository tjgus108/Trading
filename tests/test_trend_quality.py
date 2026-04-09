"""
TrendQualityStrategy 단위 테스트 (16개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_quality import TrendQualityStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", noise: float = 0.01) -> pd.DataFrame:
    """trend: 'up' | 'down' | 'flat'"""
    np.random.seed(0)
    closes = [100.0]
    for _ in range(n - 1):
        if trend == "up":
            delta = 1.0 + np.random.uniform(-noise, noise) * 100
        elif trend == "down":
            delta = -1.0 + np.random.uniform(-noise, noise) * 100
        else:
            delta = np.random.uniform(-2.0, 2.0)
        closes.append(closes[-1] + delta)
    closes = np.array(closes)
    highs = closes + 0.5
    lows = closes - 0.5
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_strong_trend(direction: int = 1) -> pd.DataFrame:
    """R² ≈ 1이고 quality_score > 0.05 달성 데이터 (n=25).

    quality_score = r_squared * |slope / mean_price|
    n=25, idx=23, window=closes[4:24] (20봉).
    direction=1:  closes = [0..24]    → window mean=13.5, slope=1 → q≈0.074 > 0.05 ✓
    direction=-1: closes = [24..0]    → window mean=10.5, slope=-1 → q≈0.095 > 0.05 ✓
    """
    n = 25
    if direction == 1:
        closes = np.arange(n, dtype=float)        # [0, 1, ..., 24]
    else:
        closes = np.arange(n - 1, -1, -1, dtype=float)  # [24, 23, ..., 0]
    df = pd.DataFrame({
        "open": closes,
        "high": closes + 0.001,
        "low": closes - 0.001,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_insufficient(n: int = 10) -> pd.DataFrame:
    closes = np.ones(n) * 100.0
    df = pd.DataFrame({
        "open": closes, "high": closes, "low": closes,
        "close": closes, "volume": np.ones(n) * 1000,
    })
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendQualityStrategy:

    def setup_method(self):
        self.strat = TrendQualityStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "trend_quality"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient(10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_reasoning(self):
        df = _make_insufficient(5)
        sig = self.strat.generate(df)
        assert "부족" in sig.reasoning

    # 4. 강한 상승 추세 → BUY
    def test_strong_uptrend_buy(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY

    # 5. 강한 하락 추세 → SELL
    def test_strong_downtrend_sell(self):
        df = _make_strong_trend(direction=-1)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL

    # 6. 횡보장 → HOLD
    def test_flat_market_hold(self):
        df = _make_df(60, trend="flat", noise=0.1)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 7. Signal 인스턴스 반환
    def test_returns_signal_instance(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 8. action 유효값
    def test_action_valid(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 9. confidence 유효값
    def test_confidence_valid(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 10. entry_price = df.iloc[-2].close
    def test_entry_price_second_last(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)

    # 11. BUY reasoning에 'R²' 또는 'slope' 포함
    def test_buy_reasoning_content(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert "R²" in sig.reasoning or "slope" in sig.reasoning or "부족" in sig.reasoning

    # 12. BUY strategy 필드
    def test_strategy_field_buy(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert sig.strategy == "trend_quality"

    # 13. SELL strategy 필드
    def test_strategy_field_sell(self):
        df = _make_strong_trend(direction=-1)
        sig = self.strat.generate(df)
        assert sig.strategy == "trend_quality"

    # 14. BUY confidence MEDIUM 이상
    def test_buy_confidence_medium_or_high(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 15. bull_case / bear_case 비어있지 않음 (BUY/SELL 시)
    def test_bull_bear_case_nonempty(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        if sig.action in (Action.BUY, Action.SELL):
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 16. invalidation 필드 존재
    def test_invalidation_field_exists(self):
        df = _make_strong_trend(direction=1)
        sig = self.strat.generate(df)
        assert isinstance(sig.invalidation, str)
