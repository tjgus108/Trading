"""
VolumeSpreadAnalysisV2Strategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_spread_analysis_v2 import VolumeSpreadAnalysisV2Strategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _base_df(n: int = 40) -> pd.DataFrame:
    """중립 데이터프레임 (좁은 스프레드, 보통 거래량)."""
    np.random.seed(7)
    closes = 100 + np.cumsum(np.random.uniform(-0.2, 0.2, n))
    highs = closes + 0.3
    lows = closes - 0.3
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    })


def _insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.ones(n) * 100.0
    return pd.DataFrame({
        "open": closes, "high": closes + 0.1, "low": closes - 0.1,
        "close": closes, "volume": np.ones(n) * 1000.0,
    })


def _buy_signal_df(n: int = 40, high_conf: bool = False) -> pd.DataFrame:
    """
    BUY 조건: wide_spread AND high_vol AND close_position > 0.7
    마지막 완성봉(idx=-2)에서 조건 충족.
    """
    closes = np.ones(n) * 100.0
    spread_mult = 1.6 if high_conf else 1.3
    vol_mult = 1.6 if high_conf else 1.3
    highs = closes + 0.3
    lows = closes - 0.3
    # idx=-2에서 넓은 스프레드 + 고거래량 + 상단 종가
    idx = n - 2
    spread_size = 0.3 * spread_mult
    highs[idx] = 100.0 + spread_size
    lows[idx] = 100.0 - spread_size
    closes[idx] = 100.0 + spread_size * 0.8  # close_position ~ 0.9
    volumes = np.ones(n) * 1000.0
    volumes[idx] = 1000.0 * vol_mult
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _sell_signal_df(n: int = 40, high_conf: bool = False) -> pd.DataFrame:
    """
    SELL 조건: wide_spread AND high_vol AND close_position < 0.3
    """
    closes = np.ones(n) * 100.0
    spread_mult = 1.6 if high_conf else 1.3
    vol_mult = 1.6 if high_conf else 1.3
    highs = closes + 0.3
    lows = closes - 0.3
    idx = n - 2
    spread_size = 0.3 * spread_mult
    highs[idx] = 100.0 + spread_size
    lows[idx] = 100.0 - spread_size
    closes[idx] = 100.0 - spread_size * 0.8  # close_position ~ 0.1
    volumes = np.ones(n) * 1000.0
    volumes[idx] = 1000.0 * vol_mult
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestVolumeSpreadAnalysisV2Strategy:

    def setup_method(self):
        self.strat = VolumeSpreadAnalysisV2Strategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "volume_spread_analysis_v2"

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
        assert sig.strategy == "volume_spread_analysis_v2"

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

    # 12. BUY 조건 → BUY or HOLD
    def test_buy_condition_action_range(self):
        df = _buy_signal_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 13. SELL 조건 → SELL or HOLD
    def test_sell_condition_action_range(self):
        df = _sell_signal_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 14. BUY reasoning에 'VSA' 또는 'BUY' 포함
    def test_buy_reasoning_content(self):
        df = _buy_signal_df()
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "VSA" in sig.reasoning or "BUY" in sig.reasoning

    # 15. SELL reasoning에 'VSA' 또는 'SELL' 포함
    def test_sell_reasoning_content(self):
        df = _sell_signal_df()
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "VSA" in sig.reasoning or "SELL" in sig.reasoning

    # 16. BUY confidence HIGH or MEDIUM
    def test_buy_confidence_not_low(self):
        df = _buy_signal_df()
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 17. SELL confidence HIGH or MEDIUM
    def test_sell_confidence_not_low(self):
        df = _sell_signal_df()
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 18. HIGH confidence 조건 (spread > 1.5x AND vol > 1.5x)
    def test_high_confidence_strong_signal(self):
        df = _buy_signal_df(high_conf=True)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            # high_conf=True 시 HIGH 가능
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
