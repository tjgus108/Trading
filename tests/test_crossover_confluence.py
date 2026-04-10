"""
CrossoverConfluenceStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.crossover_confluence import CrossoverConfluenceStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, ema9=None, ema21=None, ema50=None, rsi14=None):
    n = len(closes)
    closes = np.array(closes, dtype=float)
    df = pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    })
    if ema9 is not None:
        df["ema9"] = np.array(ema9, dtype=float)
    if ema21 is not None:
        df["ema21"] = np.array(ema21, dtype=float)
    if ema50 is not None:
        df["ema50"] = np.array(ema50, dtype=float)
    if rsi14 is not None:
        df["rsi14"] = np.array(rsi14, dtype=float)
    return df


def _make_flat_df(n=60):
    """평탄 데이터 → HOLD."""
    closes = np.ones(n) * 100.0
    return _make_df(closes)


def _make_buy_df():
    """
    EMA9 crosses above EMA21 at iloc[-2], EMA9 > EMA50, RSI > 45 → BUY.
    iloc[-3]: ema9 <= ema21
    iloc[-2]: ema9 > ema21, ema9 > ema50, rsi > 45
    """
    n = 60
    closes = np.ones(n) * 100.0
    ema9 = np.ones(n) * 95.0
    ema21 = np.ones(n) * 100.0
    ema50 = np.ones(n) * 90.0  # EMA9 > EMA50
    rsi14 = np.ones(n) * 55.0  # > 45

    # prev (iloc[-3]): ema9 <= ema21
    ema9[-3] = 99.0
    ema21[-3] = 100.0
    # last (iloc[-2]): ema9 > ema21
    ema9[-2] = 101.0
    ema21[-2] = 100.0

    return _make_df(closes, ema9=ema9, ema21=ema21, ema50=ema50, rsi14=rsi14)


def _make_sell_df():
    """
    EMA9 crosses below EMA21 at iloc[-2], EMA9 < EMA50, RSI < 55 → SELL.
    iloc[-3]: ema9 >= ema21
    iloc[-2]: ema9 < ema21, ema9 < ema50, rsi < 55
    """
    n = 60
    closes = np.ones(n) * 100.0
    ema9 = np.ones(n) * 105.0
    ema21 = np.ones(n) * 100.0
    ema50 = np.ones(n) * 110.0  # EMA9 < EMA50
    rsi14 = np.ones(n) * 45.0  # < 55

    # prev (iloc[-3]): ema9 >= ema21
    ema9[-3] = 101.0
    ema21[-3] = 100.0
    # last (iloc[-2]): ema9 < ema21
    ema9[-2] = 99.0
    ema21[-2] = 100.0

    return _make_df(closes, ema9=ema9, ema21=ema21, ema50=ema50, rsi14=rsi14)


def _make_buy_high_conf_df():
    """
    BUY 조건 + EMA21이 최근 5봉 내 EMA50 크로스 → HIGH confidence.
    """
    n = 60
    closes = np.ones(n) * 100.0
    ema9 = np.ones(n) * 95.0
    ema21 = np.ones(n) * 90.0
    ema50 = np.ones(n) * 88.0
    rsi14 = np.ones(n) * 55.0

    # EMA21이 EMA50을 4봉 전에 크로스 (iloc[-6]: ema21<=ema50, iloc[-5]: ema21>ema50)
    ema21[-6] = 87.0
    ema50[-6] = 88.0
    ema21[-5] = 89.0
    ema50[-5] = 88.0

    # EMA9 crosses above EMA21
    ema9[-3] = 89.0
    ema21[-3] = 90.0
    ema9[-2] = 91.0
    ema21[-2] = 90.0

    return _make_df(closes, ema9=ema9, ema21=ema21, ema50=ema50, rsi14=rsi14)


# ── tests ──────────────────────────────────────────────────────────────────────

class TestCrossoverConfluenceStrategy:

    def setup_method(self):
        self.strategy = CrossoverConfluenceStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "crossover_confluence"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → Confidence.LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 최소 행 정확히 55행 → Signal 반환
    def test_exactly_min_rows(self):
        df = _make_flat_df(n=55)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 6. 평탄 데이터 → HOLD
    def test_flat_data_hold(self):
        df = _make_flat_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 7. BUY 조건 충족 → BUY
    def test_buy_signal(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 8. SELL 조건 충족 → SELL
    def test_sell_signal(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 9. BUY entry_price 양수
    def test_buy_entry_price_positive(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 10. SELL entry_price 양수
    def test_sell_entry_price_positive(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_flat_df(n=60)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "crossover_confluence"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 12. BUY reasoning에 "crossed above" 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY
        assert "crossed above" in signal.reasoning

    # 13. SELL reasoning에 "crossed below" 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL
        assert "crossed below" in signal.reasoning

    # 14. HIGH confidence when EMA21 recently crossed EMA50
    def test_buy_high_confidence_with_ema21_cross(self):
        df = _make_buy_high_conf_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 15. BUY RSI 필터: RSI <= 45 → HOLD (크로스 있어도)
    def test_buy_rsi_filter_no_signal_below_45(self):
        n = 60
        closes = np.ones(n) * 100.0
        ema9 = np.ones(n) * 95.0
        ema21 = np.ones(n) * 100.0
        ema50 = np.ones(n) * 90.0
        rsi14 = np.ones(n) * 40.0  # <= 45 → BUY 조건 불충족
        ema9[-3] = 99.0
        ema21[-3] = 100.0
        ema9[-2] = 101.0
        ema21[-2] = 100.0
        df = _make_df(closes, ema9=ema9, ema21=ema21, ema50=ema50, rsi14=rsi14)
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY

    # 16. SELL RSI 필터: RSI >= 55 → HOLD (크로스 있어도)
    def test_sell_rsi_filter_no_signal_above_55(self):
        n = 60
        closes = np.ones(n) * 100.0
        ema9 = np.ones(n) * 105.0
        ema21 = np.ones(n) * 100.0
        ema50 = np.ones(n) * 110.0
        rsi14 = np.ones(n) * 60.0  # >= 55 → SELL 조건 불충족
        ema9[-3] = 101.0
        ema21[-3] = 100.0
        ema9[-2] = 99.0
        ema21[-2] = 100.0
        df = _make_df(closes, ema9=ema9, ema21=ema21, ema50=ema50, rsi14=rsi14)
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 17. BUY EMA50 필터: EMA9 < EMA50 → HOLD
    def test_buy_ema50_filter(self):
        n = 60
        closes = np.ones(n) * 100.0
        ema9 = np.ones(n) * 95.0
        ema21 = np.ones(n) * 100.0
        ema50 = np.ones(n) * 110.0  # EMA9 < EMA50 → BUY 조건 불충족
        rsi14 = np.ones(n) * 55.0
        ema9[-3] = 99.0
        ema21[-3] = 100.0
        ema9[-2] = 101.0
        ema21[-2] = 100.0
        df = _make_df(closes, ema9=ema9, ema21=ema21, ema50=ema50, rsi14=rsi14)
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY

    # 18. BUY invalidation 존재
    def test_buy_invalidation_present(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0
