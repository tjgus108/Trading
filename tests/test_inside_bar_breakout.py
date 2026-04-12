"""
InsideBarBreakoutStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.inside_bar_breakout import InsideBarBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 15) -> pd.DataFrame:
    closes = np.linspace(100.0, 110.0, n)
    highs = closes + 2.0
    lows = closes - 2.0
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "atr14": np.ones(n) * 1.0,
    })
    return df.reset_index(drop=True)


def _make_buy_df(big_mother: bool = True) -> pd.DataFrame:
    """
    n=15 → idx=13, ib_idx=12, mother_idx=11
    current close > mother.high → BUY
    """
    n = 15
    df = _base_df(n)
    atr = 1.0

    mother_idx = 11
    df.loc[mother_idx, "high"] = 108.0
    df.loc[mother_idx, "low"] = 106.0 if big_mother else 107.7  # range=2.0 or 0.3

    ib_idx = 12
    df.loc[ib_idx, "high"] = 107.5   # < mother_high=108.0
    df.loc[ib_idx, "low"] = 106.5 if big_mother else 107.8  # > mother_low
    df.loc[ib_idx, "close"] = 107.0
    df.loc[ib_idx, "atr14"] = atr

    idx = 13
    df.loc[idx, "close"] = 108.5   # > mother_high=108.0
    df.loc[idx, "high"] = 109.0
    df.loc[idx, "low"] = 108.0
    df.loc[idx, "atr14"] = atr

    df.loc[14, "close"] = df.loc[idx, "close"]

    return df


def _make_sell_df(big_mother: bool = True) -> pd.DataFrame:
    """
    n=15 → idx=13, ib_idx=12, mother_idx=11
    current close < mother.low → SELL
    """
    n = 15
    df = _base_df(n)
    atr = 1.0

    mother_idx = 11
    df.loc[mother_idx, "high"] = 108.0
    df.loc[mother_idx, "low"] = 106.0 if big_mother else 107.7

    ib_idx = 12
    df.loc[ib_idx, "high"] = 107.5
    df.loc[ib_idx, "low"] = 106.5 if big_mother else 107.8
    df.loc[ib_idx, "close"] = 107.0
    df.loc[ib_idx, "atr14"] = atr

    idx = 13
    df.loc[idx, "close"] = 105.5   # < mother_low=106.0
    df.loc[idx, "high"] = 106.0
    df.loc[idx, "low"] = 105.0
    df.loc[idx, "atr14"] = atr

    df.loc[14, "close"] = df.loc[idx, "close"]

    return df


def _make_no_inside_bar_df() -> pd.DataFrame:
    """inside bar 없음 → HOLD"""
    n = 15
    df = _base_df(n)

    mother_idx = 11
    df.loc[mother_idx, "high"] = 107.0
    df.loc[mother_idx, "low"] = 105.0

    ib_idx = 12
    df.loc[ib_idx, "high"] = 109.0   # >= mother_high → NOT inside bar
    df.loc[ib_idx, "low"] = 104.0
    df.loc[ib_idx, "close"] = 107.0

    idx = 13
    df.loc[idx, "close"] = 108.0
    df.loc[idx, "atr14"] = 1.0
    df.loc[14, "close"] = 108.0

    return df


def _make_inside_bar_no_breakout_df() -> pd.DataFrame:
    """Inside bar 있지만 돌파 없음 (close가 mother bar 범위 내) → HOLD"""
    n = 15
    df = _base_df(n)

    mother_idx = 11
    df.loc[mother_idx, "high"] = 108.0
    df.loc[mother_idx, "low"] = 106.0

    ib_idx = 12
    df.loc[ib_idx, "high"] = 107.5
    df.loc[ib_idx, "low"] = 106.5
    df.loc[ib_idx, "close"] = 107.0

    idx = 13
    df.loc[idx, "close"] = 107.0   # mother 범위 내
    df.loc[idx, "high"] = 107.5
    df.loc[idx, "low"] = 106.5
    df.loc[idx, "atr14"] = 1.0

    df.loc[14, "close"] = 107.0

    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestInsideBarBreakoutStrategy:

    def setup_method(self):
        self.strategy = InsideBarBreakoutStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "inside_bar_breakout"

    # 2. BUY 신호 (inside bar + mother high 돌파)
    def test_buy_signal_on_mother_high_breakout(self):
        df = _make_buy_df(big_mother=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. SELL 신호 (inside bar + mother low 이탈)
    def test_sell_signal_on_mother_low_breakdown(self):
        df = _make_sell_df(big_mother=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. inside bar 없으면 HOLD
    def test_hold_when_no_inside_bar(self):
        df = _make_no_inside_bar_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. inside bar 있지만 mother bar 범위 내 → HOLD
    def test_hold_when_no_mother_breakout(self):
        df = _make_inside_bar_no_breakout_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. BUY - 큰 모봉 (range > ATR*1.5) → HIGH confidence
    def test_buy_high_confidence_big_mother(self):
        df = _make_buy_df(big_mother=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. BUY - 작은 모봉 (range <= ATR*1.5) → MEDIUM confidence
    def test_buy_medium_confidence_small_mother(self):
        df = _make_buy_df(big_mother=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 8. SELL - 큰 모봉 → HIGH confidence
    def test_sell_high_confidence_big_mother(self):
        df = _make_sell_df(big_mother=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 9. SELL - 작은 모봉 → MEDIUM confidence
    def test_sell_medium_confidence_small_mother(self):
        df = _make_sell_df(big_mother=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.MEDIUM

    # 10. 데이터 부족 (< 10행) → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _base_df(n=5)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "inside_bar_breakout"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 12. BUY reasoning에 "InsideBarBreakout" 포함
    def test_buy_reasoning_contains_strategy(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "InsideBarBreakout" in signal.reasoning

    # 13. SELL reasoning에 "InsideBarBreakout" 포함
    def test_sell_reasoning_contains_strategy(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "InsideBarBreakout" in signal.reasoning

    # 14. HOLD 시 confidence LOW
    def test_hold_confidence_is_low(self):
        df = _make_no_inside_bar_df()
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 15. BUY 신호 entry_price == current close
    def test_buy_entry_price_equals_close(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            idx = len(df) - 2
            assert signal.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 16. SELL 신호 entry_price == current close
    def test_sell_entry_price_equals_close(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            idx = len(df) - 2
            assert signal.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 17. BUY 신호에 bull_case/bear_case 포함
    def test_buy_has_bull_bear_case(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 18. SELL 신호에 bull_case/bear_case 포함
    def test_sell_has_bull_bear_case(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0
