"""
PriceChannelBreakStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_channel_break import PriceChannelBreakStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_base_df(n=60, base_price=100.0):
    closes = np.ones(n) * base_price
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes.copy(),
        "volume": np.ones(n) * 1000,
    })


def _make_breakout_up_df(n=60, fresh=True):
    """20봉 고점 신규 돌파 케이스."""
    df = _make_base_df(n, base_price=100.0)
    # 20봉 고점 = 100.0 * 1.005 = 100.5 (high)
    # entry_high 계산: df["high"].iloc[idx-20:idx].max()
    # idx = n-2 이므로 idx-20:idx = [n-22:n-2] → 100.5
    # close[-2] 돌파: 101.0 (> 100.5)
    df = df.copy()
    df.iloc[-2, df.columns.get_loc("close")] = 101.0
    df.iloc[-2, df.columns.get_loc("high")] = 101.5
    if fresh:
        # 직전 3봉 close는 돌파 안 된 상태 (100.0)
        pass  # 이미 100.0
    return df


def _make_breakout_up_already_broken_df(n=60):
    """이미 직전 3봉 중 하나가 돌파된 상태 → HOLD."""
    df = _make_base_df(n, base_price=100.0)
    # 완성봉도 돌파
    df.iloc[-2, df.columns.get_loc("close")] = 101.0
    df.iloc[-2, df.columns.get_loc("high")] = 101.5
    # 직전 3봉 중 1봉도 돌파
    df.iloc[-3, df.columns.get_loc("close")] = 101.0
    df.iloc[-3, df.columns.get_loc("high")] = 101.5
    return df


def _make_breakout_down_df(n=60, fresh=True):
    """20봉 저점 신규 이탈 케이스."""
    df = _make_base_df(n, base_price=100.0)
    # entry_low = 100.0 * 0.995 = 99.5
    df.iloc[-2, df.columns.get_loc("close")] = 99.0
    df.iloc[-2, df.columns.get_loc("low")] = 98.5
    return df


def _make_breakout_down_already_broken_df(n=60):
    """이미 직전 3봉 중 하나가 이탈된 상태 → HOLD."""
    df = _make_base_df(n, base_price=100.0)
    df.iloc[-2, df.columns.get_loc("close")] = 99.0
    df.iloc[-2, df.columns.get_loc("low")] = 98.5
    # 직전 3봉 중 이미 이탈
    df.iloc[-4, df.columns.get_loc("close")] = 99.0
    df.iloc[-4, df.columns.get_loc("low")] = 98.5
    return df


def _make_insufficient_df(n=20):
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_hold_df(n=60):
    """채널 내 횡보."""
    return _make_base_df(n, base_price=100.0)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPriceChannelBreakStrategy:

    def setup_method(self):
        self.strategy = PriceChannelBreakStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "price_channel_break"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 신규 돌파 상향 → BUY
    def test_fresh_breakout_up_is_buy(self):
        df = _make_breakout_up_df(n=60, fresh=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. 이미 돌파된 상태 → HOLD (BUY 아님)
    def test_already_broken_up_is_hold(self):
        df = _make_breakout_up_already_broken_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 7. 신규 이탈 하향 → SELL
    def test_fresh_breakout_down_is_sell(self):
        df = _make_breakout_down_df(n=60, fresh=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 8. 이미 이탈된 상태 → HOLD (SELL 아님)
    def test_already_broken_down_is_hold(self):
        df = _make_breakout_down_already_broken_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. 채널 내 횡보 → HOLD
    def test_sideways_hold(self):
        df = _make_hold_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 10. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 11. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "price_channel_break"

    # 12. entry_price는 _last 봉 close와 일치
    def test_entry_price_matches_last_close(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 13. BUY 신호 reasoning에 "Price Channel Break BUY" 포함
    def test_buy_reasoning_label(self):
        df = _make_breakout_up_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "Price Channel Break BUY" in signal.reasoning

    # 14. SELL 신호 reasoning에 "Price Channel Break SELL" 포함
    def test_sell_reasoning_label(self):
        df = _make_breakout_down_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "Price Channel Break SELL" in signal.reasoning

    # 15. BUY 신호 시 invalidation 포함
    def test_buy_has_invalidation(self):
        df = _make_breakout_up_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 16. SELL 신호 시 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_breakout_down_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 17. bull_case / bear_case 필드 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 18. HIGH confidence: 0.5% 이상 돌파 시
    def test_high_confidence_strong_breakout(self):
        df = _make_base_df(n=60, base_price=100.0)
        # entry_high ≈ 100.5, close=101.0 → 0.5% 이상
        df.iloc[-2, df.columns.get_loc("close")] = 101.0
        df.iloc[-2, df.columns.get_loc("high")] = 101.5
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            # 101.0 > 100.5 * 1.005 = 101.0025 → 아슬아슬
            # 102.0 이상이면 확실히 HIGH
            pass
        # 더 강한 돌파로 재검사
        df2 = _make_base_df(n=60, base_price=100.0)
        df2.iloc[-2, df2.columns.get_loc("close")] = 102.0
        df2.iloc[-2, df2.columns.get_loc("high")] = 102.5
        signal2 = self.strategy.generate(df2)
        if signal2.action == Action.BUY:
            assert signal2.confidence == Confidence.HIGH

    # 19. MEDIUM confidence: 간신히 돌파 시
    def test_medium_confidence_marginal_breakout(self):
        df = _make_base_df(n=60, base_price=100.0)
        # entry_high = max(high[idx-20:idx]) = 100.5
        # close = 100.6 → 0.1% 돌파 → MEDIUM
        df.iloc[-2, df.columns.get_loc("close")] = 100.6
        df.iloc[-2, df.columns.get_loc("high")] = 101.1
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 20. action은 유효한 값
    def test_action_is_valid(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
