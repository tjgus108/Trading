"""
VolSpreadAnalysisStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vol_spread_analysis import VolSpreadAnalysisStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 50) -> pd.DataFrame:
    """정상 OHLCV DataFrame (신호 없는 중립 상태)."""
    np.random.seed(42)
    closes = 100.0 + np.cumsum(np.random.uniform(-0.2, 0.2, n))
    spread = 1.0
    highs = closes + spread / 2
    lows = closes - spread / 2
    volume = np.full(n, 1000.0)
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volume,
    })


def _upthrust_df() -> pd.DataFrame:
    """마지막 완성봉(-2)이 Upthrust bar인 DataFrame."""
    df = _base_df(n=50)
    # avg_spread ≈ 1.0, avg_vol ≈ 1000
    # 마지막 완성봉 (-2): spread 큼 + vol 큼 + close near low
    i = -2
    df.iloc[i, df.columns.get_loc("high")] = df.iloc[i]["close"] + 3.0   # spread=6 > 1.5*1=1.5
    df.iloc[i, df.columns.get_loc("low")] = df.iloc[i]["close"] - 3.0
    # close near low: (close - low) / spread < 0.3
    close_val = df.iloc[i]["low"] + 0.5   # ratio = 0.5/6 ≈ 0.083
    df.iloc[i, df.columns.get_loc("close")] = close_val
    df.iloc[i, df.columns.get_loc("volume")] = 5000.0   # > 1.5 * 1000
    return df


def _test_supply_df() -> pd.DataFrame:
    """마지막 완성봉(-2)이 Test for supply인 DataFrame."""
    df = _base_df(n=50)
    # avg_spread ≈ 1.0, avg_vol ≈ 1000
    # 마지막 완성봉 (-2): spread 작음 + vol 작음 + close near high
    i = -2
    df.iloc[i, df.columns.get_loc("high")] = df.iloc[i]["close"] + 0.2   # spread=0.4 < 0.7
    df.iloc[i, df.columns.get_loc("low")] = df.iloc[i]["close"] - 0.2
    # close near high: (close - low) / spread > 0.7
    close_val = df.iloc[i]["low"] + 0.35   # ratio = 0.35/0.4 = 0.875
    df.iloc[i, df.columns.get_loc("close")] = close_val
    df.iloc[i, df.columns.get_loc("volume")] = 200.0   # < 0.7 * 1000
    return df


def _short_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestVolSpreadAnalysisStrategy:

    def setup_method(self):
        self.strategy = VolSpreadAnalysisStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "vol_spread_analysis"

    # 2. 데이터 부족 HOLD
    def test_insufficient_data_hold(self):
        df = _short_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _short_df(n=10)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 4. Upthrust → SELL
    def test_upthrust_sell(self):
        df = _upthrust_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 5. Test for supply → BUY
    def test_test_supply_buy(self):
        df = _test_supply_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 6. 중립 상태 HOLD
    def test_neutral_hold(self):
        df = _base_df(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 7. SELL reasoning에 "Upthrust" 포함
    def test_sell_reasoning_upthrust(self):
        df = _upthrust_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "Upthrust" in sig.reasoning or "upthrust" in sig.reasoning.lower()

    # 8. BUY reasoning에 "supply" 포함
    def test_buy_reasoning_supply(self):
        df = _test_supply_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "supply" in sig.reasoning.lower()

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _base_df(n=50)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "vol_spread_analysis"
        assert isinstance(sig.entry_price, float)
        assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0

    # 10. 볼륨 극단값 > 2x → HIGH confidence
    def test_extreme_high_volume_high_confidence(self):
        df = _upthrust_df()
        # 볼륨을 avg의 3배 이상으로 설정
        df.iloc[-2, df.columns.get_loc("volume")] = 10000.0
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 11. 볼륨 극단값 < 0.5x → HIGH confidence (test_supply)
    def test_extreme_low_volume_high_confidence(self):
        df = _test_supply_df()
        # avg 1000, volume 50 < 0.5 * 1000
        df.iloc[-2, df.columns.get_loc("volume")] = 50.0
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 12. entry_price는 last close
    def test_entry_price_equals_last_close(self):
        df = _upthrust_df()
        sig = self.strategy.generate(df)
        last_close = float(df["close"].iloc[-2])
        assert abs(sig.entry_price - last_close) < 1e-6

    # 13. None df 처리
    def test_none_df_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 14. BUY 시 bull_case/bear_case 있음
    def test_buy_has_bull_bear_case(self):
        df = _test_supply_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 15. SELL 시 bull_case/bear_case 있음
    def test_sell_has_bull_bear_case(self):
        df = _upthrust_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 16. spread=0인 봉에서 NaN 처리 (ZeroDivision 방지)
    def test_zero_spread_no_crash(self):
        df = _base_df(n=50)
        # 마지막 완성봉의 high=low=close (spread=0)
        df.iloc[-2, df.columns.get_loc("high")] = df.iloc[-2]["close"]
        df.iloc[-2, df.columns.get_loc("low")] = df.iloc[-2]["close"]
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
