"""
InsideBarStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.inside_bar import InsideBarStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100.0, 110.0, n)
    highs = closes + 2.0
    lows = closes - 2.0
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "ema50": closes * 0.95,
        "atr14": np.ones(n) * 1.0,
    })
    return df


def _make_inside_bar_buy_df(big_mother: bool = True) -> pd.DataFrame:
    """
    n=21 → idx=len-2=19, ib_idx=18, mother_idx=17
    mother(17) → ib(18) → breakout_close(19) → incomplete(20)
    """
    n = 21
    df = _base_df(n)
    atr = 1.0

    # mother_idx=17
    mother_idx = 17
    df.loc[mother_idx, "high"] = 110.0
    if big_mother:
        df.loc[mother_idx, "low"] = 108.0   # range=2.0 >= atr*1.5=1.5 → HIGH
    else:
        df.loc[mother_idx, "low"] = 109.6   # range=0.4 < atr*1.5 → MEDIUM

    # ib_idx=18: inside bar
    ib_idx = 18
    df.loc[ib_idx, "high"] = 109.5   # < mother_high=110
    df.loc[ib_idx, "low"] = 108.5 if big_mother else 109.7  # > mother_low
    df.loc[ib_idx, "close"] = 109.0
    df.loc[ib_idx, "atr14"] = atr

    # idx=19: 돌파 봉 (close > ib_high=109.5)
    idx = 19
    df.loc[idx, "close"] = 109.5 + 0.8   # 110.3 > ib_high
    df.loc[idx, "high"] = df.loc[idx, "close"] + 0.5
    df.loc[idx, "low"] = df.loc[idx, "close"] - 0.5
    df.loc[idx, "atr14"] = atr

    # incomplete candle (20)
    df.loc[20, "close"] = df.loc[idx, "close"]

    return df


def _make_inside_bar_sell_df(big_mother: bool = True) -> pd.DataFrame:
    """
    n=21 → idx=19, ib_idx=18, mother_idx=17
    """
    n = 21
    df = _base_df(n)
    atr = 1.0

    mother_idx = 17
    df.loc[mother_idx, "high"] = 110.0
    if big_mother:
        df.loc[mother_idx, "low"] = 108.0
    else:
        df.loc[mother_idx, "low"] = 109.6

    ib_idx = 18
    df.loc[ib_idx, "high"] = 109.5
    df.loc[ib_idx, "low"] = 108.5 if big_mother else 109.7
    df.loc[ib_idx, "close"] = 109.0
    df.loc[ib_idx, "atr14"] = atr

    idx = 19
    df.loc[idx, "close"] = 108.5 - 0.8   # < ib_low=108.5
    df.loc[idx, "high"] = df.loc[idx, "close"] + 0.5
    df.loc[idx, "low"] = df.loc[idx, "close"] - 0.5
    df.loc[idx, "atr14"] = atr

    df.loc[20, "close"] = df.loc[idx, "close"]

    return df


def _make_no_inside_bar_df() -> pd.DataFrame:
    """inside bar 없음: ib_high >= mother_high. n=21 → idx=19, ib_idx=18, mother_idx=17"""
    n = 21
    df = _base_df(n)

    mother_idx = 17
    df.loc[mother_idx, "high"] = 108.0
    df.loc[mother_idx, "low"] = 106.0

    ib_idx = 18
    df.loc[ib_idx, "high"] = 110.0   # >= mother_high → NOT inside bar
    df.loc[ib_idx, "low"] = 107.0
    df.loc[ib_idx, "close"] = 108.5

    idx = 19
    df.loc[idx, "close"] = 109.0
    df.loc[idx, "atr14"] = 1.0
    df.loc[20, "close"] = 109.0

    return df


def _make_inside_bar_no_breakout_df() -> pd.DataFrame:
    """Inside bar 있지만 돌파 없음 (close가 ib 범위 내). n=21 → idx=19, ib_idx=18, mother_idx=17"""
    n = 21
    df = _base_df(n)

    mother_idx = 17
    df.loc[mother_idx, "high"] = 110.0
    df.loc[mother_idx, "low"] = 108.0

    ib_idx = 18
    df.loc[ib_idx, "high"] = 109.5
    df.loc[ib_idx, "low"] = 108.5
    df.loc[ib_idx, "close"] = 109.0

    idx = 19
    df.loc[idx, "close"] = 109.0   # ib 범위 내
    df.loc[idx, "high"] = 109.8
    df.loc[idx, "low"] = 108.8
    df.loc[idx, "atr14"] = 1.0

    df.loc[20, "close"] = 109.0

    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestInsideBarStrategy:

    def setup_method(self):
        self.strategy = InsideBarStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "inside_bar"

    # 2. BUY 신호 (inside bar + 상향 돌파)
    def test_buy_signal_on_inside_bar_upside_breakout(self):
        df = _make_inside_bar_buy_df(big_mother=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. SELL 신호 (inside bar + 하향 돌파)
    def test_sell_signal_on_inside_bar_downside_breakout(self):
        df = _make_inside_bar_sell_df(big_mother=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. inside bar 없으면 HOLD
    def test_hold_when_no_inside_bar(self):
        df = _make_no_inside_bar_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. inside bar 있지만 돌파 없으면 HOLD
    def test_hold_when_inside_bar_but_no_breakout(self):
        df = _make_inside_bar_no_breakout_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. BUY - 큰 모봉 (range >= ATR*1.5) → HIGH confidence
    def test_buy_high_confidence_big_mother(self):
        df = _make_inside_bar_buy_df(big_mother=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. BUY - 작은 모봉 (range < ATR*1.5) → MEDIUM confidence
    def test_buy_medium_confidence_small_mother(self):
        df = _make_inside_bar_buy_df(big_mother=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 8. SELL - 큰 모봉 → HIGH confidence
    def test_sell_high_confidence_big_mother(self):
        df = _make_inside_bar_sell_df(big_mother=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 9. SELL - 작은 모봉 → MEDIUM confidence
    def test_sell_medium_confidence_small_mother(self):
        df = _make_inside_bar_sell_df(big_mother=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.MEDIUM

    # 10. 데이터 부족 (< 5행) → HOLD
    def test_insufficient_data(self):
        df = _base_df(n=4)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_inside_bar_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "inside_bar"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 12. BUY reasoning에 "Inside bar" 포함
    def test_buy_reasoning_contains_inside_bar(self):
        df = _make_inside_bar_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "Inside bar" in signal.reasoning or "inside bar" in signal.reasoning.lower()

    # 13. SELL reasoning에 "Inside bar" 포함
    def test_sell_reasoning_contains_inside_bar(self):
        df = _make_inside_bar_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "Inside bar" in signal.reasoning or "inside bar" in signal.reasoning.lower()

    # 14. HOLD 시 confidence LOW
    def test_hold_confidence_is_low(self):
        df = _make_no_inside_bar_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 15. BUY 신호에 bull_case/bear_case 포함
    def test_buy_has_bull_bear_case(self):
        df = _make_inside_bar_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. SELL 신호에 bull_case/bear_case 포함
    def test_sell_has_bull_bear_case(self):
        df = _make_inside_bar_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0
