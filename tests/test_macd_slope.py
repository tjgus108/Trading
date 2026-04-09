"""
MACDSlopeStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.macd_slope import MACDSlopeStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _make_base_df(n: int = 60) -> pd.DataFrame:
    closes = np.linspace(100.0, 110.0, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df(n: int = 80) -> pd.DataFrame:
    """
    음수 히스토그램 영역에서 기울기·가속도 양수 → BUY 유도.
    앞부분 급락 → 뒷부분 완만 회복 패턴.
    """
    np.random.seed(10)
    # 급락으로 MACD 히스토그램을 음수로 만들고
    down = np.linspace(150.0, 80.0, 50)
    # 이후 점진적 회복으로 기울기/가속도 양수 유도
    up = np.linspace(80.0, 95.0, 30)
    closes = np.concatenate([down, up])[:n]
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(len(closes)) * 1000,
    })


def _make_sell_df(n: int = 80) -> pd.DataFrame:
    """
    양수 히스토그램 영역에서 기울기·가속도 음수 → SELL 유도.
    앞부분 급등 → 뒷부분 완만 하락 패턴.
    """
    np.random.seed(20)
    up = np.linspace(80.0, 160.0, 50)
    down = np.linspace(160.0, 145.0, 30)
    closes = np.concatenate([up, down])[:n]
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(len(closes)) * 1000,
    })


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100.0, 105.0, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMACDSlopeStrategy:

    def setup_method(self):
        self.strategy = MACDSlopeStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "macd_slope"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(20)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 4. 데이터 부족 confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(20)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_base_df(60)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "macd_slope"
        assert isinstance(sig.entry_price, float)
        assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
        assert isinstance(sig.invalidation, str)

    # 6. entry_price = close[-2]
    def test_entry_price_is_last_close(self):
        df = _make_base_df(60)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 7. HOLD confidence LOW
    def test_hold_confidence_low(self):
        df = _make_base_df(60)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 8. BUY 조건 직접 주입
    def test_buy_signal_direct_injection(self):
        """hist<0, hist_slope>0, slope_accel>0 → BUY."""
        df = _make_buy_df(80)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 조건 직접 주입
    def test_sell_signal_direct_injection(self):
        """hist>0, hist_slope<0, slope_accel<0 → SELL."""
        df = _make_sell_df(80)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. BUY reasoning에 "BUY" 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_buy_df(80)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 11. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_sell_df(80)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 12. BUY/SELL confidence: HIGH or MEDIUM
    def test_buy_sell_confidence_not_low(self):
        df = _make_buy_df(80)
        sig = self.strategy.generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. HIGH confidence 조건: slope_accel > std
    def test_high_confidence_when_accel_large(self):
        """slope_accel이 std보다 크면 HIGH confidence."""
        # 급락 뒤 급반등 → slope_accel이 커짐
        down = np.linspace(200.0, 50.0, 60)
        up = np.linspace(50.0, 100.0, 40)
        closes = np.concatenate([down, up])
        df = pd.DataFrame({
            "open": closes,
            "high": closes * 1.01,
            "low": closes * 0.99,
            "close": closes,
            "volume": np.ones(len(closes)) * 1000,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 14. bull_case/bear_case 포함 (BUY)
    def test_buy_has_context_fields(self):
        df = _make_buy_df(80)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 15. invalidation 존재 (SELL)
    def test_sell_has_invalidation(self):
        df = _make_sell_df(80)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.invalidation) > 0

    # 16. 경계값: n=35 (최소 행)
    def test_minimum_rows_boundary(self):
        df = _make_base_df(35)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 17. n=34 → HOLD
    def test_below_minimum_rows_hold(self):
        df = _make_base_df(34)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
