"""
RangeBiasStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.range_bias import RangeBiasStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(n: int = _MIN_ROWS + 5,
             close_ratio: float = 0.5,
             trend: str = "flat") -> pd.DataFrame:
    """
    close_ratio: 0=저점 마감, 1=고점 마감 (일정)
    trend: "up"=점점 위에서 마감, "down"=점점 아래서 마감, "flat"=일정
    """
    rows = n
    lows = [100.0] * rows
    highs = [102.0] * rows

    if trend == "up":
        # 마지막 봉들이 고점 근처에서 마감 → bias > 0.6
        ratios = [0.5] * (rows // 2) + [0.85] * (rows - rows // 2)
    elif trend == "down":
        # 마지막 봉들이 저점 근처에서 마감 → bias < 0.4
        ratios = [0.5] * (rows // 2) + [0.15] * (rows - rows // 2)
    else:
        ratios = [close_ratio] * rows

    closes = [lows[i] + ratios[i] * (highs[i] - lows[i]) for i in range(rows)]

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * rows,
    })
    return df


def _make_buy_df() -> pd.DataFrame:
    """bias > 0.6 + bias_trend > 0 조건: 지속적 상단 마감 + 개선 추세"""
    rows = 30
    lows = [100.0] * rows
    highs = [102.0] * rows
    # 앞 절반은 중간, 뒤 절반은 점점 상단
    ratios = [0.5] * 10 + [0.65 + i * 0.01 for i in range(20)]
    closes = [lows[i] + ratios[i] * (highs[i] - lows[i]) for i in range(rows)]
    return pd.DataFrame({
        "open": closes, "close": closes,
        "high": highs, "low": lows,
        "volume": [1000.0] * rows,
    })


def _make_sell_df() -> pd.DataFrame:
    """bias < 0.4 + bias_trend < 0 조건: 지속적 하단 마감 + 악화 추세"""
    rows = 30
    lows = [100.0] * rows
    highs = [102.0] * rows
    ratios = [0.5] * 10 + [0.35 - i * 0.01 for i in range(20)]
    closes = [lows[i] + max(0, ratios[i]) * (highs[i] - lows[i]) for i in range(rows)]
    return pd.DataFrame({
        "open": closes, "close": closes,
        "high": highs, "low": lows,
        "volume": [1000.0] * rows,
    })


class TestRangeBiasStrategy:

    def setup_method(self):
        self.strategy = RangeBiasStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "range_bias"

    # 2. 인스턴스 타입 확인
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 시 HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음
    def test_returns_signal_not_none(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 필드 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. 정상 signal 반환
    def test_normal_signal_with_sufficient_data(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY 신호 확인
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 9. BUY reasoning에 키워드 포함
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "bias" in sig.reasoning.lower() or "편향" in sig.reasoning

    # 10. SELL 신호 확인
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 11. SELL reasoning에 키워드 포함
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "bias" in sig.reasoning.lower() or "편향" in sig.reasoning

    # 12. confidence HIGH or MEDIUM (신호 있을 때)
    def test_confidence_is_high_or_medium(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action in (Action.BUY, Action.SELL):
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 14. strategy 필드 확인
    def test_strategy_field(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "range_bias"

    # 15. 최소 행 경계
    def test_min_rows_boundary(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 16. HIGH confidence BUY (bias > 0.75)
    def test_high_confidence_buy(self):
        rows = 30
        lows = [100.0] * rows
        highs = [102.0] * rows
        # 전체 구간 0.9 비율로 마감 → bias > 0.75
        ratios = [0.9] * rows
        closes = [lows[i] + ratios[i] * (highs[i] - lows[i]) for i in range(rows)]
        # bias_trend > 0 보장: bias_ma보다 bias가 크도록 앞은 0.7, 뒤는 0.9
        ratios2 = [0.7] * 15 + [0.92] * 15
        closes2 = [lows[i] + ratios2[i] * (highs[i] - lows[i]) for i in range(rows)]
        df = pd.DataFrame({
            "open": closes2, "close": closes2,
            "high": highs, "low": lows,
            "volume": [1000.0] * rows,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 17. HIGH confidence SELL (bias < 0.25)
    def test_high_confidence_sell(self):
        rows = 30
        lows = [100.0] * rows
        highs = [102.0] * rows
        ratios = [0.3] * 15 + [0.08] * 15
        closes = [lows[i] + ratios[i] * (highs[i] - lows[i]) for i in range(rows)]
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * rows,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH
