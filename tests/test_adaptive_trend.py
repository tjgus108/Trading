"""AdaptiveTrendStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_trend import AdaptiveTrendStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, trend: str = "up") -> pd.DataFrame:
    """기본 DataFrame 생성."""
    if trend == "up":
        close = np.linspace(100.0, 130.0, n)
    elif trend == "down":
        close = np.linspace(130.0, 100.0, n)
    else:
        close = np.full(n, 100.0) + np.random.default_rng(42).normal(0, 0.5, n)
    return pd.DataFrame({
        "open":  close - 0.3,
        "high":  close + 1.0,
        "low":   close - 1.0,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


def _make_buy_df(n: int = 50) -> pd.DataFrame:
    """
    BUY 조건: fast_ema > adaptive_ema > slow_ema AND close > fast_ema
    상승 추세 + 마지막 봉 급등
    """
    close = np.linspace(100.0, 140.0, n)
    # 마지막 완성봉(iloc[-2])에서 close를 fast_ema 위로 밀어올림
    close[-2] = close[-3] * 1.05
    return pd.DataFrame({
        "open":  close - 0.3,
        "high":  close + 1.5,
        "low":   close - 1.0,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


def _make_sell_df(n: int = 50) -> pd.DataFrame:
    """
    SELL 조건: fast_ema < adaptive_ema < slow_ema AND close < fast_ema
    하락 추세 + 마지막 봉 급락
    """
    close = np.linspace(140.0, 100.0, n)
    close[-2] = close[-3] * 0.95
    return pd.DataFrame({
        "open":  close + 0.3,
        "high":  close + 1.0,
        "low":   close - 1.5,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


# ── 테스트 ─────────────────────────────────────────────────────────────────────

class TestAdaptiveTrendStrategy:

    def setup_method(self):
        self.strat = AdaptiveTrendStrategy()

    # 1. name 확인
    def test_name(self):
        assert self.strat.name == "adaptive_trend"

    # 2. MIN_ROWS 미만 → HOLD
    def test_insufficient_rows_hold(self):
        df = _make_df(n=10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "데이터 부족" in sig.reasoning

    # 3. MIN_ROWS 경계값 (29행) → HOLD
    def test_boundary_29_rows(self):
        df = _make_df(n=29)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. MIN_ROWS 정확히 (30행) → 신호 생성 가능
    def test_boundary_30_rows(self):
        df = _make_df(n=30)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 5. 상승 추세 → BUY 가능
    def test_uptrend_buy(self):
        df = _make_buy_df(n=60)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY

    # 6. 하락 추세 → SELL 가능
    def test_downtrend_sell(self):
        df = _make_sell_df(n=60)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL

    # 7. BUY 신호 confidence는 HIGH 또는 MEDIUM
    def test_buy_confidence_valid(self):
        df = _make_buy_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 8. SELL 신호 confidence는 HIGH 또는 MEDIUM
    def test_sell_confidence_valid(self):
        df = _make_sell_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. entry_price는 양수
    def test_entry_price_positive(self):
        df = _make_buy_df(n=60)
        sig = self.strat.generate(df)
        assert sig.entry_price > 0

    # 10. strategy 필드 일치
    def test_signal_strategy_field(self):
        df = _make_buy_df(n=60)
        sig = self.strat.generate(df)
        assert sig.strategy == "adaptive_trend"

    # 11. HOLD 시 LOW confidence
    def test_hold_low_confidence(self):
        df = _make_df(n=50, trend="flat")
        sig = self.strat.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 12. NaN 포함 데이터 → HOLD
    def test_nan_handling(self):
        df = _make_df(n=50)
        df.loc[df.index[-2], "close"] = float("nan")
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 13. reasoning 문자열 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_buy_df(n=60)
        sig = self.strat.generate(df)
        assert len(sig.reasoning) > 0

    # 14. 충분히 긴 데이터 (100행) → 예외 없음
    def test_long_data_no_exception(self):
        df = _make_buy_df(n=100)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 15. HOLD invalidation 비어있음
    def test_hold_invalidation_empty(self):
        df = _make_df(n=10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert sig.invalidation == ""

    # 16. BUY invalidation 비어있지 않음
    def test_buy_invalidation_not_empty(self):
        df = _make_buy_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.invalidation) > 0
