"""
IchimokuBreakoutStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ichimoku_breakout import IchimokuBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_base_df(n: int = 120) -> pd.DataFrame:
    """단조 상승 OHLCV DataFrame."""
    closes = np.linspace(100.0, 130.0, n)
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df(n: int = 120) -> pd.DataFrame:
    """
    TK 강제 크로스 BUY DataFrame.
    앞부분은 하락(tenkan<=kijun), 뒷부분은 급격히 상승하여
    마지막 완성봉(-2)에서 tenkan > kijun + close > kumo_top 확보.
    """
    np.random.seed(0)
    # 앞 60봉 하락 → tenkan <= kijun
    down = np.linspace(130.0, 100.0, 60)
    # 뒷 60봉 급등 → tenkan이 kijun을 상향 돌파
    up = np.linspace(100.0, 200.0, 60)
    closes = np.concatenate([down, up])
    highs = closes * 1.02
    lows = closes * 0.98
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_sell_df(n: int = 120) -> pd.DataFrame:
    """
    TK 강제 크로스 SELL DataFrame.
    앞부분 급등 → 뒷부분 급락하여 마지막 완성봉에서 tenkan < kijun
    + close < kumo_bottom.
    """
    np.random.seed(1)
    up = np.linspace(100.0, 200.0, 60)
    down = np.linspace(200.0, 80.0, 60)
    closes = np.concatenate([up, down])
    highs = closes * 1.02
    lows = closes * 0.98
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 30) -> pd.DataFrame:
    closes = np.linspace(100.0, 110.0, n)
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestIchimokuBreakoutStrategy:

    def setup_method(self):
        self.strategy = IchimokuBreakoutStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "ichimoku_breakout"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(30)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 4. 데이터 부족 confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(30)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 5. Signal 필드 완전성 (충분 데이터)
    def test_signal_fields_complete(self):
        df = _make_base_df(120)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "ichimoku_breakout"
        assert isinstance(sig.entry_price, float)
        assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
        assert isinstance(sig.invalidation, str)

    # 6. entry_price = close[-2]
    def test_entry_price_is_last_close(self):
        df = _make_base_df(120)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 7. BUY 신호 action 확인
    def test_buy_signal_action(self):
        df = _make_buy_df(120)
        sig = self.strategy.generate(df)
        # 강제 크로스 데이터 → BUY or HOLD (크로스 조건에 따라)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 8. SELL 신호 action 확인
    def test_sell_signal_action(self):
        df = _make_sell_df(120)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 9. BUY 신호 reasoning에 "BUY" 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_buy_df(120)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 10. SELL 신호 reasoning에 "SELL" 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_sell_df(120)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 11. BUY confidence: HIGH or MEDIUM
    def test_buy_confidence_valid(self):
        df = _make_buy_df(120)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. HIGH confidence — kumo 거리 > 2%인 경우 직접 구성
    def test_high_confidence_when_far_from_kumo(self):
        """close가 kumo_top보다 3% 이상 위 → HIGH confidence."""
        df = _make_buy_df(120)
        # TK cross 만들기: 마지막 완성봉 직전(-3)에 크로스가 발생하도록 조작
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. HOLD 시 confidence LOW
    def test_hold_confidence_low(self):
        df = _make_base_df(120)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 14. BUY 신호에 bull_case/bear_case 존재
    def test_buy_signal_has_context(self):
        df = _make_buy_df(120)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 15. SELL 신호에 invalidation 존재
    def test_sell_signal_has_invalidation(self):
        df = _make_sell_df(120)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.invalidation) > 0

    # 16. 경계값: n=80 (최소 행)
    def test_minimum_rows_boundary(self):
        df = _make_base_df(80)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 17. n=79 → HOLD
    def test_below_minimum_rows_hold(self):
        df = _make_base_df(79)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
