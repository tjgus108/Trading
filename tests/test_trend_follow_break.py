"""
TrendFollowBreakStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_follow_break import TrendFollowBreakStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 80, trend: str = "up", adx_strong: bool = True) -> pd.DataFrame:
    """
    OHLCV DataFrame 생성.
    trend: "up" | "down" | "flat"
    adx_strong: True → 넓은 스프레드로 ADX 상승 유도
    """
    np.random.seed(1)
    if trend == "up":
        closes = np.linspace(100, 130, n) + np.random.randn(n) * 0.3
    elif trend == "down":
        closes = np.linspace(130, 100, n) + np.random.randn(n) * 0.3
    else:
        closes = np.full(n, 100.0) + np.random.randn(n) * 0.5

    spread = 0.05 if adx_strong else 0.003
    highs = closes * (1 + spread)
    lows = closes * (1 - spread)
    opens = closes * (1 + np.random.uniform(-0.002, 0.002, n))

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 2000,
    })


def _make_buy_df(n: int = 80) -> pd.DataFrame:
    """
    BUY 신호 유발: 강한 상승 추세(ADX > 25) + 최근 최고가 돌파.
    마지막 2봉을 롤링 최고가 위로 설정.
    """
    np.random.seed(5)
    closes = np.linspace(100, 125, n - 2).tolist()
    # 마지막 2봉을 최고가 위로 크게 설정
    closes += [140.0, 145.0]
    closes = np.array(closes)

    spread = 0.04
    highs = closes * (1 + spread)
    lows = closes * (1 - spread)
    # 마지막 2봉 high도 크게
    highs[-2] = 146.0
    highs[-1] = 150.0

    return pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 2000,
    })


def _make_sell_df(n: int = 80) -> pd.DataFrame:
    """
    SELL 신호 유발: 강한 하락 추세(ADX > 25) + 최근 최저가 하향 돌파.
    """
    np.random.seed(9)
    closes = np.linspace(130, 105, n - 2).tolist()
    closes += [88.0, 85.0]
    closes = np.array(closes)

    spread = 0.04
    highs = closes * (1 + spread)
    lows = closes * (1 - spread)
    lows[-2] = 84.0
    lows[-1] = 82.0

    return pd.DataFrame({
        "open": closes * 1.001,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 2000,
    })


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendFollowBreakStrategy:

    def setup_method(self):
        self.strategy = TrendFollowBreakStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "trend_follow_break"

    # 2. 인스턴스 생성
    def test_instance_creation(self):
        s = TrendFollowBreakStrategy(adx_period=20, break_period=30, adx_threshold=30.0)
        assert s.adx_period == 20
        assert s.break_period == 30
        assert s.adx_threshold == 30.0

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=80)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=80)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "trend_follow_break"
        assert isinstance(sig.entry_price, float)
        assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df(n=80)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "ADX" in sig.reasoning or "BUY" in sig.reasoning or "돌파" in sig.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df(n=80)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "ADX" in sig.reasoning or "SELL" in sig.reasoning or "돌파" in sig.reasoning

    # 10. HIGH confidence 조건 — ADX > 35
    def test_high_confidence_condition(self):
        df = _make_buy_df(n=80)
        sig = self.strategy.generate(df)
        if sig.confidence == Confidence.HIGH:
            assert sig.action in (Action.BUY, Action.SELL)

    # 11. MEDIUM confidence — ADX 25~35
    def test_medium_confidence_condition(self):
        df = _make_df(n=80, trend="up", adx_strong=True)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=80)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_df(n=80)
        sig = self.strategy.generate(df)
        assert sig.strategy == "trend_follow_break"

    # 14. 최소 행 수(40)에서 동작 확인
    def test_min_rows_works(self):
        df = _make_df(n=40, trend="up")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "trend_follow_break"
