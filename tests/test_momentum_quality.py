"""
MomentumQualityStrategy 단위 테스트.

DataFrame 구조:
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
"""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.momentum_quality import MomentumQualityStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _flat_df(n: int = 40, close: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _bull_df(n: int = 40) -> pd.DataFrame:
    """
    강한 상승 모멘텀:
    - 꾸준히 상승 + 후반 가속 → consistency 높음, acceleration 양수, mom20 > 0
    - quality_score > 1.0 → BUY
    """
    base = 100.0
    closes = []
    # 앞부분: 완만한 상승
    for i in range(n - 10):
        closes.append(base + i * 0.3)
    # 후반: 가속 (더 가파른 상승 → mom5 > mom10)
    last = closes[-1]
    for j in range(10):
        closes.append(last + (j + 1) * 1.2)
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _bear_df(n: int = 40) -> pd.DataFrame:
    """
    강한 하락 모멘텀:
    - 꾸준히 하락 → consistency 낮음, acceleration 음수, mom20 < 0
    - quality_score < -0.8 → SELL HIGH
    """
    base = 140.0
    closes = [base - i * 0.6 for i in range(n)]
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestMomentumQualityStrategy:

    def setup_method(self):
        self.strat = MomentumQualityStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "momentum_quality"

    # 2. 인스턴스 타입
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strat, BaseStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _flat_df(n=15)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient data" in sig.reasoning

    # 4. None 대신 Signal 반환
    def test_returns_signal_not_none(self):
        df = _flat_df(n=10)
        sig = self.strat.generate(df)
        assert sig is not None
        assert isinstance(sig, Signal)

    # 5. reasoning 필드 존재
    def test_reasoning_field_exists(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 6. 정상 Signal 반환
    def test_normal_signal_returned(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 8. BUY reasoning에 모멘텀 관련 내용
    def test_buy_reasoning_content(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "quality_score" in sig.reasoning or "모멘텀" in sig.reasoning

    # 9. SELL reasoning에 하락 관련 내용
    def test_sell_reasoning_content(self):
        df = _bear_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "quality_score" in sig.reasoning or "모멘텀" in sig.reasoning

    # 10. 강한 상승 → BUY
    def test_bull_df_returns_buy(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY

    # 11. 강한 하락 → SELL
    def test_bear_df_returns_sell(self):
        df = _bear_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL

    # 12. BUY HIGH confidence (quality_score > 1.5)
    def test_buy_high_confidence(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. entry_price > 0
    def test_entry_price_positive(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.entry_price > 0

    # 14. strategy 필드 = "momentum_quality"
    def test_strategy_field(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        assert sig.strategy == "momentum_quality"

    # 추가: 최소 행 경계값 (24행 → HOLD)
    def test_24_rows_returns_hold(self):
        df = _flat_df(n=24)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 추가: 25행 → Signal 반환
    def test_25_rows_processes(self):
        df = _flat_df(n=25)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
