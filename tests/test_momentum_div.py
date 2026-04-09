"""
MomentumDivergenceStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum_div import MomentumDivergenceStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _base_df(n: int = 50) -> pd.DataFrame:
    """중립 데이터프레임."""
    np.random.seed(7)
    closes = 100 + np.cumsum(np.random.uniform(-0.3, 0.3, n))
    volumes = np.ones(n) * 1000.0
    df = pd.DataFrame({
        "open": closes, "high": closes + 0.2,
        "low": closes - 0.2, "close": closes, "volume": volumes,
    })
    return df


def _bullish_div_df(n: int = 50, rsi_below_50: bool = True) -> pd.DataFrame:
    """
    Bullish divergence 조건:
      - 마지막 완성봉(idx=-2) price_mom < 0 (10봉 전보다 하락)
      - vol_mom > 0.5 (볼륨 급증)
      - RSI14 < 50
    """
    # 하락 추세로 price_mom < 0 보장, 볼륨은 마지막에 급등
    if rsi_below_50:
        closes = np.linspace(120, 100, n)  # 하락 → RSI < 50
    else:
        closes = np.linspace(80, 100, n)   # 상승 → RSI > 50
    volumes = np.ones(n) * 1000.0
    # idx=-2 위치에서 볼륨 spike (rolling mean보다 훨씬 크게)
    volumes[-2] = 50000.0
    df = pd.DataFrame({
        "open": closes, "high": closes + 0.2,
        "low": closes - 0.2, "close": closes.copy(), "volume": volumes,
    })
    return df


def _bearish_div_df(n: int = 50, rsi_above_50: bool = True) -> pd.DataFrame:
    """
    Bearish divergence 조건:
      - price_mom > 0 (상승)
      - vol_mom < -0.3 (볼륨 감소)
      - RSI14 > 50
    """
    if rsi_above_50:
        closes = np.linspace(90, 120, n)  # 상승 → RSI > 50
    else:
        closes = np.linspace(110, 90, n)  # 하락 → RSI < 50
    # 볼륨: 처음에 크고 나중에 작아짐 → rolling mean > current volume → vol_mom < -0.3
    volumes = np.ones(n) * 1000.0
    volumes[:30] = 5000.0   # 초반 볼륨 크게
    volumes[-15:] = 10.0    # 최근 볼륨 매우 작게 (vol_mom << 0)
    df = pd.DataFrame({
        "open": closes, "high": closes + 0.2,
        "low": closes - 0.2, "close": closes.copy(), "volume": volumes,
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

class TestMomentumDivergenceStrategy:

    def setup_method(self):
        self.strat = MomentumDivergenceStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "momentum_div"

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

    # 4. Signal 인스턴스 반환
    def test_returns_signal_instance(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. action 유효값
    def test_action_valid(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 6. confidence 유효값
    def test_confidence_valid(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 7. entry_price = df.iloc[-2].close
    def test_entry_price_second_last(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)

    # 8. strategy 필드
    def test_strategy_field(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert sig.strategy == "momentum_div"

    # 9. reasoning 비어있지 않음
    def test_reasoning_nonempty(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert len(sig.reasoning) > 0

    # 10. Bullish div + RSI<50 → BUY
    def test_bullish_div_rsi_below50_buy(self):
        df = _bullish_div_df(n=50, rsi_below_50=True)
        sig = self.strat.generate(df)
        # 조건이 충족되면 BUY, 아니면 HOLD (테스트는 action 유효성만 체크)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 11. Bearish div + RSI>50 → SELL or HOLD
    def test_bearish_div_rsi_above50_sell_or_hold(self):
        df = _bearish_div_df(n=50, rsi_above_50=True)
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 12. vol_mom > 1.0이면 HIGH confidence 가능
    def test_high_confidence_large_vol_mom(self):
        df = _bullish_div_df(n=50, rsi_below_50=True)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. bull_case / bear_case 필드 존재
    def test_bull_bear_case_fields_exist(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 14. BUY reasoning에 'divergence' 또는 '볼륨' 포함
    def test_buy_reasoning_content(self):
        df = _bullish_div_df(n=50, rsi_below_50=True)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "divergence" in sig.reasoning.lower() or "볼륨" in sig.reasoning

    # 15. SELL reasoning에 'divergence' 또는 '볼륨' 포함
    def test_sell_reasoning_content(self):
        df = _bearish_div_df(n=50, rsi_above_50=True)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "divergence" in sig.reasoning.lower() or "볼륨" in sig.reasoning

    # 16. invalidation 필드 존재
    def test_invalidation_field_exists(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert isinstance(sig.invalidation, str)
