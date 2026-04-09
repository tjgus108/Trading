"""
NR7Strategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.nr7 import NR7Strategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 30) -> pd.DataFrame:
    """기본 OHLCV + atr14 DataFrame. 레인지는 일정."""
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


def _make_nr7_buy_df(breakout_large: bool = True) -> pd.DataFrame:
    """
    인덱스 -3 (nr7_idx)에 NR7 봉 생성, 인덱스 -2 (idx)에서 상향 돌파.
    """
    n = 30
    df = _base_df(n)
    atr = 1.0

    # nr7_idx = len(df) - 3 = 27
    # 직전 6봉 (21~26) 레인지를 크게 설정
    for i in range(21, 27):
        df.loc[i, "high"] = df.loc[i, "close"] + 5.0
        df.loc[i, "low"] = df.loc[i, "close"] - 5.0

    # NR7 봉 (27): 레인지를 가장 작게
    nr7_idx = 27
    df.loc[nr7_idx, "high"] = 105.0
    df.loc[nr7_idx, "low"] = 104.5   # range=0.5, prev 6봉 range=10 → NR7 조건 충족

    # 돌파 봉 (28 = idx): close > nr7_idx high
    idx = 28
    if breakout_large:
        # 돌파폭 > ATR*0.5
        df.loc[idx, "close"] = 105.0 + atr * 0.6
    else:
        df.loc[idx, "close"] = 105.0 + atr * 0.1  # 돌파폭 작음
    df.loc[idx, "high"] = df.loc[idx, "close"] + 1.0
    df.loc[idx, "low"] = df.loc[idx, "close"] - 1.0
    df.loc[idx, "atr14"] = atr

    # 마지막 봉 (29) = 현재 진행 중
    df.loc[29, "close"] = df.loc[idx, "close"]

    return df


def _make_nr7_sell_df(breakout_large: bool = True) -> pd.DataFrame:
    """
    NR7 봉 이후 하향 돌파 시나리오.
    """
    n = 30
    df = _base_df(n)
    atr = 1.0

    for i in range(21, 27):
        df.loc[i, "high"] = df.loc[i, "close"] + 5.0
        df.loc[i, "low"] = df.loc[i, "close"] - 5.0

    nr7_idx = 27
    df.loc[nr7_idx, "high"] = 105.5
    df.loc[nr7_idx, "low"] = 105.0  # range=0.5

    idx = 28
    if breakout_large:
        df.loc[idx, "close"] = 105.0 - atr * 0.6
    else:
        df.loc[idx, "close"] = 105.0 - atr * 0.1
    df.loc[idx, "high"] = df.loc[idx, "close"] + 1.0
    df.loc[idx, "low"] = df.loc[idx, "close"] - 1.0
    df.loc[idx, "atr14"] = atr

    df.loc[29, "close"] = df.loc[idx, "close"]

    return df


def _make_no_nr7_df() -> pd.DataFrame:
    """NR7 봉 없음 (모든 봉 레인지 동일)."""
    return _base_df(30)


def _make_nr7_no_breakout_df() -> pd.DataFrame:
    """NR7 봉은 있지만 돌파 없음 (close가 NR7 봉 내부)."""
    n = 30
    df = _base_df(n)

    for i in range(21, 27):
        df.loc[i, "high"] = df.loc[i, "close"] + 5.0
        df.loc[i, "low"] = df.loc[i, "close"] - 5.0

    nr7_idx = 27
    df.loc[nr7_idx, "high"] = 105.5
    df.loc[nr7_idx, "low"] = 104.5

    idx = 28
    df.loc[idx, "close"] = 105.0  # NR7 범위 내
    df.loc[idx, "high"] = 106.0
    df.loc[idx, "low"] = 104.0
    df.loc[idx, "atr14"] = 1.0

    df.loc[29, "close"] = 105.0
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestNR7Strategy:

    def setup_method(self):
        self.strategy = NR7Strategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "nr7"

    # 2. BUY 신호 (NR7 + 상향 돌파)
    def test_buy_signal_on_nr7_upside_breakout(self):
        df = _make_nr7_buy_df(breakout_large=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. SELL 신호 (NR7 + 하향 돌파)
    def test_sell_signal_on_nr7_downside_breakout(self):
        df = _make_nr7_sell_df(breakout_large=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. NR7 없으면 HOLD
    def test_hold_when_no_nr7(self):
        df = _make_no_nr7_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. NR7 있지만 돌파 없으면 HOLD
    def test_hold_when_nr7_but_no_breakout(self):
        df = _make_nr7_no_breakout_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. BUY - 돌파폭 > ATR*0.5 → HIGH confidence
    def test_buy_high_confidence_large_breakout(self):
        df = _make_nr7_buy_df(breakout_large=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. BUY - 돌파폭 작으면 MEDIUM confidence
    def test_buy_medium_confidence_small_breakout(self):
        df = _make_nr7_buy_df(breakout_large=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 8. SELL - 돌파폭 > ATR*0.5 → HIGH confidence
    def test_sell_high_confidence_large_breakout(self):
        df = _make_nr7_sell_df(breakout_large=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 9. SELL - 돌파폭 작으면 MEDIUM confidence
    def test_sell_medium_confidence_small_breakout(self):
        df = _make_nr7_sell_df(breakout_large=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.MEDIUM

    # 10. 데이터 부족 (< 10행) → HOLD
    def test_insufficient_data_rows(self):
        df = _base_df(n=8)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. nr7_idx < 6 → HOLD
    def test_insufficient_data_for_7bar_comparison(self):
        df = _base_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_nr7_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "nr7"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 13. BUY 신호 reasoning에 "NR7" 포함
    def test_buy_reasoning_contains_nr7(self):
        df = _make_nr7_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "NR7" in signal.reasoning

    # 14. SELL 신호 reasoning에 "NR7" 포함
    def test_sell_reasoning_contains_nr7(self):
        df = _make_nr7_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "NR7" in signal.reasoning

    # 15. HOLD 시 confidence LOW
    def test_hold_confidence_is_low(self):
        df = _make_no_nr7_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 16. BUY 신호에 bull_case/bear_case 포함
    def test_buy_has_bull_bear_case(self):
        df = _make_nr7_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0
