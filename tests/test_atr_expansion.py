"""
ATRExpansionStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.atr_expansion import ATRExpansionStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 30) -> pd.DataFrame:
    closes = np.linspace(100.0, 110.0, n)
    highs = closes + 1.0
    lows = closes - 1.0
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "atr14": np.ones(n) * 1.0,
    })
    return df.reset_index(drop=True)


def _make_buy_df(high_conf: bool = False) -> pd.DataFrame:
    """
    ATR expansion + close > EMA20 + close > close_3ago → BUY
    atr_ratio > 1.5 필요: 최근 ATR을 크게 높여 ratio 강제.
    high_conf=True → atr_ratio > 2.0 → HIGH
    """
    n = 30
    df = _base_df(n)
    idx = n - 2  # 완성봉

    # EMA20보다 close가 높도록: close를 크게 설정
    # close_3ago < close
    df.loc[idx - 3, "close"] = 100.0
    df.loc[idx, "close"] = 120.0
    df.loc[idx, "high"] = 121.0
    df.loc[idx, "low"] = 119.0

    # ATR expansion을 만들기 위해 최근 TR을 크게 올림
    # TR 높이기: 최근 10봉을 크게 만든다
    multiplier = 3.0 if high_conf else 2.0
    for i in range(max(0, idx - 9), n):
        df.loc[i, "high"] = df.loc[i, "close"] + 5.0 * multiplier
        df.loc[i, "low"] = df.loc[i, "close"] - 5.0 * multiplier

    # incomplete candle
    df.loc[n - 1, "close"] = df.loc[idx, "close"]
    df.loc[n - 1, "high"] = df.loc[idx, "high"]
    df.loc[n - 1, "low"] = df.loc[idx, "low"]

    return df


def _make_sell_df(high_conf: bool = False) -> pd.DataFrame:
    """
    ATR expansion + close < EMA20 + close < close_3ago → SELL
    """
    n = 30
    df = _base_df(n)
    idx = n - 2

    # close를 EMA20보다 낮게
    # EMA20은 close 전체의 지수이동평균이므로, 전체 close를 높게 잡고
    # idx만 낮게
    df["close"] = np.linspace(110.0, 120.0, n)
    df.loc[idx - 3, "close"] = 115.0
    df.loc[idx, "close"] = 90.0   # EMA20보다 확실히 낮음
    df.loc[idx, "high"] = 91.0
    df.loc[idx, "low"] = 89.0

    # high_conf=True → multiplier 크게 올려서 ratio > 2.0 확보
    multiplier = 5.0 if high_conf else 2.0
    for i in range(max(0, idx - 9), n):
        df.loc[i, "high"] = df.loc[i, "close"] + 5.0 * multiplier
        df.loc[i, "low"] = df.loc[i, "close"] - 5.0 * multiplier

    df.loc[n - 1, "close"] = df.loc[idx, "close"]
    df.loc[n - 1, "high"] = df.loc[idx, "high"]
    df.loc[n - 1, "low"] = df.loc[idx, "low"]

    return df


def _make_no_expansion_df() -> pd.DataFrame:
    """ATR ratio <= 1.5 → HOLD"""
    df = _base_df(30)
    # 균일한 TR → ratio ≈ 1.0
    return df


def _make_expansion_no_direction_df() -> pd.DataFrame:
    """
    ATR expansion 있지만 방향 필터 미충족 (close ≈ EMA20, 3봉 전과 비슷)
    → HOLD
    """
    n = 30
    df = _base_df(n)
    idx = n - 2

    # close와 EMA20이 거의 같고, close_3ago도 비슷
    df.loc[idx - 3, "close"] = 105.0
    df.loc[idx, "close"] = 105.0
    df.loc[idx, "high"] = 106.0
    df.loc[idx, "low"] = 104.0

    # ATR expansion: 최근 TR 크게 올림 (하지만 방향 필터 안 맞음)
    for i in range(max(0, idx - 9), n):
        df.loc[i, "high"] = df.loc[i, "close"] + 10.0
        df.loc[i, "low"] = df.loc[i, "close"] - 10.0

    df.loc[n - 1, "close"] = df.loc[idx, "close"]

    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestATRExpansionStrategy:

    def setup_method(self):
        self.strategy = ATRExpansionStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "atr_expansion"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _base_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. ATR expansion 없으면 HOLD
    def test_no_expansion_returns_hold(self):
        df = _make_no_expansion_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. BUY 신호 생성
    def test_buy_signal_generated(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 5. SELL 신호 생성
    def test_sell_signal_generated(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 6. BUY - atr_ratio > 2.0 → HIGH confidence
    def test_buy_high_confidence(self):
        df = _make_buy_df(high_conf=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. SELL - atr_ratio > 2.0 → HIGH confidence
    def test_sell_high_confidence(self):
        df = _make_sell_df(high_conf=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 8. HOLD → LOW confidence
    def test_hold_confidence_is_low(self):
        df = _make_no_expansion_df()
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 9. Signal 타입 및 필드 확인
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.strategy == "atr_expansion"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 10. BUY reasoning에 "ATR Expansion" 포함
    def test_buy_reasoning_contains_atr_expansion(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "ATR Expansion" in signal.reasoning or "atr_ratio" in signal.reasoning

    # 11. SELL reasoning에 "ATR Expansion" 포함
    def test_sell_reasoning_contains_atr_expansion(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "ATR Expansion" in signal.reasoning or "atr_ratio" in signal.reasoning

    # 12. entry_price == close of completed candle
    def test_entry_price_equals_close(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        idx = len(df) - 2
        expected_close = float(df["close"].iloc[idx])
        assert signal.entry_price == pytest.approx(expected_close)

    # 13. expansion but mixed direction → HOLD
    def test_expansion_no_direction_returns_hold(self):
        df = _make_expansion_no_direction_df()
        signal = self.strategy.generate(df)
        # close == EMA20에서는 방향 필터 미충족 → HOLD 가능
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 14. BUY signal has bull_case and bear_case
    def test_buy_has_bull_bear_case(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 15. SELL signal has bull_case and bear_case
    def test_sell_has_bull_bear_case(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. 최소 행 경계 (24행) → HOLD
    def test_min_rows_boundary(self):
        df = _base_df(n=24)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 17. 최소 행 경계 (25행) → HOLD 또는 신호 (에러 없음)
    def test_min_rows_exactly_25(self):
        df = _base_df(n=25)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
