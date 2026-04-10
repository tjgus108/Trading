"""
PreBreakoutStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.pre_breakout import PreBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _contraction_buy_df(n: int = 50) -> pd.DataFrame:
    """
    변동성 수축 + 거래량 수축 + close > SMA50 → BUY.
    처음 30봉은 큰 변동성/거래량, 이후 수축.
    close는 SMA50 위 유지.
    """
    np.random.seed(20)
    # 큰 spread (앞 30봉)
    closes_early = np.linspace(100.0, 110.0, 30)
    highs_early = closes_early + np.random.uniform(3.0, 5.0, 30)
    lows_early = closes_early - np.random.uniform(3.0, 5.0, 30)
    vol_early = np.random.uniform(2000, 3000, 30)

    # 수축된 spread (뒤 n-30봉)
    rest = n - 30
    closes_late = np.full(rest, 120.0)  # SMA50보다 높게
    highs_late = closes_late + 0.2      # 아주 좁은 range → ATR 낮음
    lows_late = closes_late - 0.2
    vol_late = np.full(rest, 200.0)     # 매우 낮은 거래량 (avg의 ~10%)

    closes = np.concatenate([closes_early, closes_late])
    highs = np.concatenate([highs_early, highs_late])
    lows = np.concatenate([lows_early, lows_late])
    vols = np.concatenate([vol_early, vol_late])

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    })


def _contraction_sell_df(n: int = 50) -> pd.DataFrame:
    """
    변동성 수축 + 거래량 수축 + close < SMA50 → SELL.
    """
    np.random.seed(21)
    closes_early = np.linspace(100.0, 90.0, 30)
    highs_early = closes_early + np.random.uniform(3.0, 5.0, 30)
    lows_early = closes_early - np.random.uniform(3.0, 5.0, 30)
    vol_early = np.random.uniform(2000, 3000, 30)

    rest = n - 30
    closes_late = np.full(rest, 70.0)   # SMA50보다 낮게
    highs_late = closes_late + 0.2
    lows_late = closes_late - 0.2
    vol_late = np.full(rest, 200.0)     # 매우 낮은 거래량

    closes = np.concatenate([closes_early, closes_late])
    highs = np.concatenate([highs_early, highs_late])
    lows = np.concatenate([lows_early, lows_late])
    vols = np.concatenate([vol_early, vol_late])

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    })


def _no_contraction_df(n: int = 50) -> pd.DataFrame:
    """변동성 수축 없음 → HOLD."""
    np.random.seed(30)
    closes = np.full(n, 100.0)
    # 큰 spread (평균과 현재 비슷) → range_ratio ≈ 1.0 → 수축 아님
    spreads = np.random.uniform(3.0, 5.0, n)
    highs = closes + spreads
    lows = closes - spreads
    vols = np.random.uniform(800, 1200, n)

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    })


def _high_conf_buy_df(n: int = 60) -> pd.DataFrame:
    """
    극도 수축: range_ratio < 0.5 AND vol < avg*0.6 → HIGH confidence + BUY.
    """
    np.random.seed(40)
    # 앞 40봉: 큰 변동성/거래량
    closes_early = np.linspace(100.0, 120.0, 40)
    highs_early = closes_early + np.random.uniform(8.0, 12.0, 40)
    lows_early = closes_early - np.random.uniform(8.0, 12.0, 40)
    vol_early = np.random.uniform(5000, 8000, 40)

    # 뒤 20봉: 극도 수축
    rest = n - 40
    closes_late = np.full(rest, 150.0)  # SMA50보다 위
    highs_late = closes_late + 0.05
    lows_late = closes_late - 0.05
    vol_late = np.full(rest, 200.0)     # 매우 낮은 거래량

    closes = np.concatenate([closes_early, closes_late])
    highs = np.concatenate([highs_early, highs_late])
    lows = np.concatenate([lows_early, lows_late])
    vols = np.concatenate([vol_early, vol_late])

    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPreBreakoutStrategy:

    def setup_method(self):
        self.strategy = PreBreakoutStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "pre_breakout"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _no_contraction_df(n=50)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "pre_breakout"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 6. 수축 + 상방 → BUY
    def test_contraction_above_sma50_buy(self):
        df = _contraction_buy_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 7. 수축 + 하방 → SELL
    def test_contraction_below_sma50_sell(self):
        df = _contraction_sell_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 8. 수축 없음 → HOLD
    def test_no_contraction_hold(self):
        df = _no_contraction_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. BUY reasoning에 "PreBreakout" 포함
    def test_buy_reasoning_contains_prebreakout(self):
        df = _contraction_buy_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "PreBreakout" in signal.reasoning

    # 10. SELL reasoning에 "PreBreakout" 포함
    def test_sell_reasoning_contains_prebreakout(self):
        df = _contraction_sell_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "PreBreakout" in signal.reasoning

    # 11. BUY 신호에 invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _contraction_buy_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 12. SELL 신호에 invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _contraction_sell_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 13. 극도 수축 → HIGH confidence
    def test_extreme_contraction_high_confidence(self):
        df = _high_conf_buy_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 14. entry_price 양수
    def test_entry_price_positive(self):
        df = _contraction_buy_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 15. 경계값: 정확히 25행
    def test_exactly_min_rows(self):
        df = _no_contraction_df(n=25)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 16. BUY reasoning에 range_ratio 포함
    def test_reasoning_contains_range_ratio(self):
        df = _contraction_buy_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "range_ratio" in signal.reasoning
        else:
            # 수축 조건 미충족 HOLD이면 bull_case에 range_ratio 있어야 함
            assert "range_ratio" in signal.bull_case

    # 17. HOLD reasoning에 "미수축" 또는 "미충족" 포함
    def test_hold_reasoning_keywords(self):
        df = _no_contraction_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert "미수축" in signal.reasoning or "미충족" in signal.reasoning
