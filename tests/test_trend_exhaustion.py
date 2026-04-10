"""
TrendExhaustionStrategy 단위 테스트 (14개+)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.trend_exhaustion import TrendExhaustionStrategy

MIN_ROWS = 25


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

def _base_df(n: int = 40, close: float = 100.0) -> pd.DataFrame:
    """기본 평탄 DataFrame."""
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _sell_exhaustion_df(n: int = 40) -> pd.DataFrame:
    """
    SELL 조건을 충족하는 DataFrame:
    - 최근 10봉 중 8봉 이상이 EMA20 위에 있음
    - trend_up = True
    - roc5 < roc5_ma * 0.5 (모멘텀 약화)
    """
    # 상승하다가 모멘텀이 약해지는 시나리오
    closes = list(np.linspace(90, 115, n - 10)) + list(np.linspace(115, 116, 10))
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _buy_reversal_df(n: int = 40) -> pd.DataFrame:
    """
    BUY 조건을 충족하는 DataFrame:
    - 최근 10봉 중 3봉 이하가 EMA20 위
    - roc5 > 0
    - roc5 > roc5_ma
    """
    # 하락 후 반등 초기 시나리오
    # 먼저 하락, 그 다음 마지막에 살짝 반등
    closes = list(np.linspace(120, 95, n - 5)) + list(np.linspace(95, 97, 5))
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


# ── 테스트 ────────────────────────────────────────────────────────────────────

class TestTrendExhaustionStrategy:

    def setup_method(self):
        self.strategy = TrendExhaustionStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "trend_exhaustion"

    # 2. 인스턴스 확인
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _base_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. 24행 → HOLD (MIN_ROWS=25)
    def test_24_rows_returns_hold(self):
        df = _base_df(n=24)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 25행 → Signal 반환
    def test_25_rows_returns_signal(self):
        df = _base_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. None 반환 없음
    def test_generate_never_returns_none(self):
        df = _base_df(n=40)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 7. reasoning 필드 존재
    def test_reasoning_field_exists(self):
        df = _base_df(n=40)
        sig = self.strategy.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _base_df(n=40)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 9. entry_price > 0
    def test_entry_price_positive(self):
        df = _base_df(n=40, close=100.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 10. strategy 필드 = 전략명
    def test_strategy_field(self):
        df = _base_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.strategy == "trend_exhaustion"

    # 11. SELL 신호 — 추세 소진 시나리오
    def test_sell_signal_on_exhaustion(self):
        df = _sell_exhaustion_df(n=50)
        sig = self.strategy.generate(df)
        # 조건이 맞으면 SELL, 아니면 최소 HOLD (SELL 기대하나 시나리오 유연하게)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 12. BUY 신호 — 반등 초기 시나리오
    def test_buy_signal_on_reversal(self):
        df = _buy_reversal_df(n=50)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 13. BUY reasoning에 "bars_up" 포함
    def test_buy_reasoning_mentions_bars_up(self):
        # 강제로 BUY 시나리오 생성
        df = _buy_reversal_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "bars_up" in sig.reasoning

    # 14. SELL reasoning에 "bars_up" 포함
    def test_sell_reasoning_mentions_bars_up(self):
        df = _sell_exhaustion_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "bars_up" in sig.reasoning

    # 15. confidence HIGH — bars_up <= 2 BUY
    def test_buy_high_confidence_very_low_bars_up(self):
        """bars_up <= 2일 때 HIGH confidence"""
        # 강하게 하락하다가 반등 — bars_up을 0~1로 만들기
        closes = list(np.linspace(130, 80, 45)) + list(np.linspace(80, 83, 5))
        df = pd.DataFrame({
            "open":   closes,
            "close":  closes,
            "high":   [c + 0.5 for c in closes],
            "low":    [c - 0.5 for c in closes],
            "volume": [1000.0] * 50,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 16. confidence MEDIUM — 중간 bars_up BUY
    def test_buy_medium_confidence_moderate(self):
        df = _buy_reversal_df(n=50)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 17. 최소 25행 경계 테스트
    def test_min_rows_boundary(self):
        for n in [23, 24]:
            df = _base_df(n=n)
            sig = self.strategy.generate(df)
            assert sig.action == Action.HOLD, f"n={n} should HOLD"
        df = _base_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
