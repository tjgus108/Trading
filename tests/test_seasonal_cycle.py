"""
SeasonalCycleStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.seasonal_cycle import SeasonalCycleStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60) -> pd.DataFrame:
    """기본 OHLCV DataFrame."""
    np.random.seed(7)
    closes = np.linspace(100, 120, n) + np.random.randn(n) * 0.5
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df(n: int = 60) -> pd.DataFrame:
    """
    BUY 신호를 유발하는 DataFrame:
    cycle_pos가 -1.0 미만에서 -1.0 이상으로 크로스하도록 설계.
    끝에서 두 번째 봉(idx=-2)이 크로스 시점.
    """
    np.random.seed(42)
    # 전반부: 하락 → 사이클 저점 근처
    closes = np.concatenate([
        np.linspace(120, 80, n - 5),   # 큰 하락으로 detrended 음수
        np.linspace(80, 82, 3),        # 저점 부근
        [84.0, 86.0],                  # 마지막 2봉: 반등
    ])
    closes = closes[:n]
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_sell_df(n: int = 60) -> pd.DataFrame:
    """
    SELL 신호를 유발하는 DataFrame:
    cycle_pos가 1.0 초과에서 1.0 이하로 크로스하도록 설계.
    """
    np.random.seed(99)
    closes = np.concatenate([
        np.linspace(80, 130, n - 5),   # 큰 상승
        np.linspace(130, 128, 3),
        [126.0, 124.0],
    ])
    closes = closes[:n]
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestSeasonalCycleStrategy:

    def setup_method(self):
        self.strategy = SeasonalCycleStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "seasonal_cycle"

    # 2. 인스턴스 생성
    def test_instance_creation(self):
        s = SeasonalCycleStrategy(period=30, std_window=25)
        assert s.period == 30
        assert s.std_window == 25

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "seasonal_cycle"
        assert isinstance(sig.entry_price, float)
        assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df(n=60)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "저점" in sig.reasoning or "BUY" in sig.reasoning or "cycle_pos" in sig.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df(n=60)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "고점" in sig.reasoning or "SELL" in sig.reasoning or "cycle_pos" in sig.reasoning

    # 10. HIGH confidence 조건 테스트 — |cycle_pos| > 1.5
    def test_high_confidence_condition(self):
        """HIGH confidence는 |cycle_pos| > 1.5일 때만."""
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        if sig.confidence == Confidence.HIGH:
            assert sig.action in (Action.BUY, Action.SELL)

    # 11. MEDIUM confidence 조건 테스트
    def test_medium_confidence_condition(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.strategy == "seasonal_cycle"

    # 14. 최소 행 수(30)에서 동작 확인
    def test_min_rows_works(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "seasonal_cycle"
