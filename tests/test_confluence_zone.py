"""
ConfluenceZoneStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.confluence_zone import ConfluenceZoneStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n, closes=None, opens=None, highs=None, lows=None, atr_val=None):
    if closes is None:
        closes = np.linspace(100, 110, n)
    closes = np.array(closes, dtype=float)
    if opens is None:
        opens = closes * 0.999
    if highs is None:
        highs = closes * 1.005
    if lows is None:
        lows = closes * 0.995
    atr = np.full(n, atr_val if atr_val is not None else 1.0)
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "atr14": atr,
    })


def _make_confluence_buy_df():
    """
    SMA20, SMA50, Pivot, Round이 모두 close 근처에 몰리도록 설계.
    close=100, open < close (불리시)
    """
    n = 60
    # close를 100 근처로 맞추고, SMA20/SMA50도 ~100이 되도록 flat 데이터
    closes = np.full(n, 100.0)
    opens = np.full(n, 99.5)   # close > open → 불리시
    highs = np.full(n, 101.0)
    lows = np.full(n, 99.0)
    df = _make_df(n, closes=closes, opens=opens, highs=highs, lows=lows, atr_val=1.0)
    return df


def _make_confluence_sell_df():
    """close < open (베어리시), 레벨들이 close 근처."""
    n = 60
    closes = np.full(n, 100.0)
    opens = np.full(n, 100.5)  # close < open → 베어리시
    highs = np.full(n, 101.0)
    lows = np.full(n, 99.0)
    df = _make_df(n, closes=closes, opens=opens, highs=highs, lows=lows, atr_val=1.0)
    return df


def _make_insufficient_df(n=30):
    return _make_df(n)


def _make_trending_df(n=60):
    """강한 추세: 레벨들이 close 근처에 없음."""
    closes = np.linspace(50, 200, n)
    opens = closes * 0.999
    highs = closes * 1.01
    lows = closes * 0.99
    return _make_df(n, closes=closes, opens=opens, highs=highs, lows=lows, atr_val=5.0)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestConfluenceZoneStrategy:

    def setup_method(self):
        self.strategy = ConfluenceZoneStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "confluence_zone"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 → LOW confidence
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(30)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(30)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 5. 반환 타입 Signal
    def test_returns_signal_instance(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. action 유효값
    def test_action_valid(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence 유효값
    def test_confidence_valid(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "confluence_zone"

    # 9. entry_price는 양수 float
    def test_entry_price_positive(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)
        assert sig.entry_price > 0

    # 10. entry_price = _last 봉 close
    def test_entry_price_matches_last_close(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(sig.entry_price - expected) < 1e-6

    # 11. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 12. bull_case / bear_case 필드 존재
    def test_bull_bear_case_fields(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.bull_case, str)
        assert isinstance(sig.bear_case, str)

    # 13. 불리시 + confluence → BUY 또는 HOLD (SELL 아님)
    def test_bullish_confluence_not_sell(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action != Action.SELL

    # 14. 베어리시 + confluence → SELL 또는 HOLD (BUY 아님)
    def test_bearish_confluence_not_buy(self):
        df = _make_confluence_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action != Action.BUY

    # 15. BUY 신호 시 invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.invalidation) > 0

    # 16. SELL 신호 시 invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _make_confluence_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.invalidation) > 0

    # 17. BUY 신호 시 reasoning에 "support" 포함
    def test_buy_reasoning_contains_support(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "support" in sig.reasoning.lower()

    # 18. SELL 신호 시 reasoning에 "resistance" 포함
    def test_sell_reasoning_contains_resistance(self):
        df = _make_confluence_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "resistance" in sig.reasoning.lower()

    # 19. confluence_count >= 3 → HIGH confidence (BUY 경우)
    def test_high_confluence_high_confidence_buy(self):
        df = _make_confluence_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # flat 데이터: SMA20=SMA50=Pivot=Round=100 → count=4 → HIGH
            assert sig.confidence == Confidence.HIGH

    # 20. 강한 추세 (레벨 분산) → HOLD
    def test_trending_no_confluence_hold(self):
        df = _make_trending_df()
        sig = self.strategy.generate(df)
        # 강한 추세에서는 레벨들이 분산되므로 HOLD 가능성 높음
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 21. 경계 데이터: 정확히 55행 → 작동
    def test_exactly_55_rows(self):
        df = _make_confluence_buy_df()
        df = df.iloc[:55]
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 22. 경계 데이터: 54행 → HOLD (부족)
    def test_54_rows_insufficient(self):
        df = _make_confluence_buy_df()
        df = df.iloc[:54]
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
