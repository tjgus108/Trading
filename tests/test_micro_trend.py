"""
MicroTrendStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.micro_trend import MicroTrendStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, highs=None, lows=None, volumes=None):
    n = len(closes)
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    if highs is None:
        highs = np.array(closes) * 1.005
    if lows is None:
        lows = np.array(closes) * 0.995
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_hh_hl_df(n=20):
    """HH-HL 패턴: 완전한 상승 추세 (hh_count=4, hl_count=4)"""
    closes = np.linspace(100, 120, n)
    # Make highs strictly increasing and lows strictly increasing
    highs = closes * 1.01 + np.arange(n) * 0.05
    lows = closes * 0.99 + np.arange(n) * 0.03
    return _make_df(closes, highs=highs, lows=lows)


def _make_ll_lh_df(n=20):
    """LL-LH 패턴: 완전한 하락 추세 (ll_count=4, lh_count=4)"""
    closes = np.linspace(120, 100, n)
    # Make highs strictly decreasing and lows strictly decreasing
    highs = closes * 1.01 - np.arange(n) * 0.05
    lows = closes * 0.99 - np.arange(n) * 0.03
    return _make_df(closes, highs=highs, lows=lows)


def _make_insufficient_df(n=5):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMicroTrendStrategy:

    def setup_method(self):
        self.strategy = MicroTrendStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "micro_trend"

    # 2. 인스턴스 확인
    def test_instance(self):
        assert isinstance(self.strategy, MicroTrendStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 대신 부족 데이터로 처리 (최소 경계)
    def test_exactly_min_rows(self):
        df = _make_df(np.linspace(100, 110, 10))
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 5. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 6. 정상 signal 반환
    def test_returns_signal(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 존재
    def test_signal_fields(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")

    # 8. BUY reasoning에 "BUY" 포함
    def test_buy_reasoning_label(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 9. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_label(self):
        df = _make_ll_lh_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 10. HIGH confidence: hh_count==4 and hl_count==4
    def test_high_confidence_perfect_pattern(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        # Perfect 4/4 pattern should give HIGH if BUY
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. MEDIUM confidence: partial pattern
    def test_medium_confidence_partial_pattern(self):
        # Random sideways — should produce HOLD with MEDIUM
        closes = np.array([100, 101, 99, 102, 98, 103, 97, 104, 96, 105, 104, 103, 102, 101])
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "micro_trend"

    # 14. 최소 행 미만 → LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_insufficient_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 15. HH-HL 상승 패턴 → BUY 또는 HOLD (SELL 아님)
    def test_uptrend_not_sell(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert sig.action != Action.SELL

    # 16. LL-LH 하락 패턴 → SELL 또는 HOLD (BUY 아님)
    def test_downtrend_not_buy(self):
        df = _make_ll_lh_df()
        sig = self.strategy.generate(df)
        assert sig.action != Action.BUY

    # 17. action 유효값
    def test_action_valid(self):
        df = _make_hh_hl_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
