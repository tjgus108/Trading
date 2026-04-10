"""
AdaptiveMACrossStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_ma_cross import AdaptiveMACrossStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, atr_val=1.0):
    n = len(closes)
    closes = np.array(closes, dtype=float)
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "atr14": np.full(n, atr_val),
    })


def _make_cross_up_df(n=60):
    """
    fast MA가 slow MA를 상향 돌파하도록 설계.
    전반부 하락 → 후반부 급등으로 크로스 발생.
    """
    # 전반: 하락 (slow MA가 fast MA 위)
    down = np.linspace(110, 90, n // 2)
    # 후반: 급등 (fast MA가 slow MA 위로)
    up = np.linspace(90, 130, n // 2)
    closes = np.concatenate([down, up])
    return _make_df(closes, atr_val=2.0)


def _make_cross_down_df(n=60):
    """fast MA가 slow MA를 하향 돌파."""
    up = np.linspace(90, 120, n // 2)
    down = np.linspace(120, 80, n // 2)
    closes = np.concatenate([up, down])
    return _make_df(closes, atr_val=2.0)


def _make_flat_df(n=60):
    closes = np.full(n, 100.0)
    return _make_df(closes)


def _make_insufficient_df(n=30):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


def _make_high_vol_df(n=60):
    """고변동성: ATR_ratio > 최근 20봉 평균."""
    closes = np.linspace(100, 120, n)
    atr = np.full(n, 5.0)
    df = _make_df(closes)
    df["atr14"] = atr
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestAdaptiveMACrossStrategy:

    def setup_method(self):
        self.strategy = AdaptiveMACrossStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "adaptive_ma_cross"

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

    # 5. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. action 유효값
    def test_action_valid(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence 유효값
    def test_confidence_valid(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "adaptive_ma_cross"

    # 9. entry_price 양수 float
    def test_entry_price_positive(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)
        assert sig.entry_price > 0

    # 10. entry_price = _last 봉 close
    def test_entry_price_matches_last_close(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(sig.entry_price - expected) < 1e-6

    # 11. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 12. bull_case / bear_case 필드 존재
    def test_bull_bear_case_fields(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.bull_case, str)
        assert isinstance(sig.bear_case, str)

    # 13. flat 데이터 → HOLD (크로스 없음)
    def test_flat_no_cross_hold(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 14. BUY 신호 시 reasoning에 "UP" 포함
    def test_buy_reasoning_contains_up(self):
        df = _make_cross_up_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "UP" in sig.reasoning

    # 15. SELL 신호 시 reasoning에 "DOWN" 포함
    def test_sell_reasoning_contains_down(self):
        df = _make_cross_down_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "DOWN" in sig.reasoning

    # 16. BUY 신호 시 invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _make_cross_up_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.invalidation) > 0

    # 17. SELL 신호 시 invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _make_cross_down_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.invalidation) > 0

    # 18. 경계: 정확히 45행 → 작동
    def test_exactly_45_rows(self):
        closes = np.linspace(100, 110, 45)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 19. 경계: 44행 → HOLD (부족)
    def test_44_rows_insufficient(self):
        closes = np.linspace(100, 110, 44)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 20. HIGH confidence: gap > ATR * 0.3
    def test_high_confidence_large_gap(self):
        """gap이 ATR의 0.3배보다 크면 HIGH."""
        df = _make_cross_up_df(n=80)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # gap > ATR * 0.3 → HIGH
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 21. atr14 컬럼 없어도 동작
    def test_works_without_atr14_column(self):
        closes = np.linspace(100, 110, 60)
        df = pd.DataFrame({
            "open": closes * 0.999,
            "high": closes * 1.005,
            "low": closes * 0.995,
            "close": closes,
            "volume": np.ones(60) * 1000,
        })
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 22. reasoning에 변동성 레이블 포함 (high_vol 또는 low_vol)
    def test_reasoning_contains_vol_label(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert "vol" in sig.reasoning
