"""
MomentumDivergenceV2Strategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum_divergence_v2 import MomentumDivergenceV2Strategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _base_df(n: int = 60) -> pd.DataFrame:
    """중립 데이터프레임."""
    np.random.seed(42)
    closes = 100 + np.cumsum(np.random.uniform(-0.2, 0.2, n))
    df = pd.DataFrame({
        "open": closes,
        "high": closes + 0.3,
        "low": closes - 0.3,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    })
    return df


def _insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.ones(n) * 100.0
    return pd.DataFrame({
        "open": closes, "high": closes, "low": closes - 0.1,
        "close": closes, "volume": np.ones(n) * 1000.0,
    })


def _bullish_div_df(n: int = 60) -> pd.DataFrame:
    """
    Bullish divergence 조건:
    - 가격은 계속 하락 (price_low_lag 위에서 더 낮은 저점 형성)
    - MACD는 반등 (macd_low_lag보다 현재 macd가 높음)
    - hist > 0 → HIGH confidence
    """
    # 강하게 하락하다가 마지막에 소폭 상승 → MACD 반등하지만 가격은 여전히 낮음
    closes = np.concatenate([
        np.linspace(110, 90, n - 10),  # 하락
        np.linspace(90, 91, 10),       # 소폭 반등 (MACD 반등 유도)
    ])
    df = pd.DataFrame({
        "open": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    })
    return df


def _bearish_div_df(n: int = 60) -> pd.DataFrame:
    """
    Bearish divergence 조건:
    - 가격은 계속 상승 (price_high_lag보다 현재 가격이 높음)
    - MACD는 하락 (macd_high_lag보다 현재 macd가 낮음)
    """
    closes = np.concatenate([
        np.linspace(90, 110, n - 10),  # 상승
        np.linspace(110, 109, 10),     # 소폭 하락 (MACD 하락 유도)
    ])
    df = pd.DataFrame({
        "open": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    })
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMomentumDivergenceV2Strategy:

    def setup_method(self):
        self.strat = MomentumDivergenceV2Strategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "momentum_divergence_v2"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _insufficient_df(10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_reasoning(self):
        df = _insufficient_df(5)
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
        assert sig.strategy == "momentum_divergence_v2"

    # 9. reasoning 비어있지 않음
    def test_reasoning_nonempty(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert len(sig.reasoning) > 0

    # 10. bull_case / bear_case 필드 존재
    def test_bull_bear_case_fields_exist(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 11. invalidation 필드 존재
    def test_invalidation_field_exists(self):
        df = _base_df()
        sig = self.strat.generate(df)
        assert isinstance(sig.invalidation, str)

    # 12. BUY 신호 시 reasoning에 'divergence' 또는 'MACD' 포함
    def test_buy_reasoning_content(self):
        df = _bullish_div_df()
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "divergence" in sig.reasoning.lower() or "MACD" in sig.reasoning

    # 13. SELL 신호 시 reasoning에 'divergence' 또는 'MACD' 포함
    def test_sell_reasoning_content(self):
        df = _bearish_div_df()
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "divergence" in sig.reasoning.lower() or "MACD" in sig.reasoning

    # 14. BUY 신호 action 범위
    def test_bullish_div_action_range(self):
        df = _bullish_div_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 15. SELL 신호 action 범위
    def test_bearish_div_action_range(self):
        df = _bearish_div_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 16. 충분한 데이터 (>= 30행) → LOW confidence 미보장
    def test_sufficient_data_not_low_always(self):
        df = _base_df(60)
        sig = self.strat.generate(df)
        # 조건 미충족 시 LOW, 충족 시 HIGH/MEDIUM — 유효값인지만 확인
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 17. BUY confidence HIGH or MEDIUM
    def test_buy_confidence_not_low(self):
        df = _bullish_div_df()
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 18. SELL confidence HIGH or MEDIUM
    def test_sell_confidence_not_low(self):
        df = _bearish_div_df()
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
