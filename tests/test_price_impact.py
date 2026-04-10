"""
PriceImpactStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_impact import PriceImpactStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close_vals=None, volume: float = 100.0) -> pd.DataFrame:
    """기본 DataFrame 생성."""
    if close_vals is None:
        closes = [100.0 + i * 0.1 for i in range(n)]
    else:
        closes = list(close_vals)
    opens = [c - 0.5 for c in closes]
    volumes = [volume] * n
    return pd.DataFrame({"open": opens, "close": closes, "volume": volumes})


def _make_buy_df(n: int = 30) -> pd.DataFrame:
    """BUY 신호 유도: 신호 봉에 큰 가격 변화 + 상승 방향."""
    closes = [100.0] * n
    volumes = [10000.0] * n

    # 신호 봉 이전: 완만한 상승 (dir_ma > 0 유도)
    for i in range(n - 15, n - 2):
        closes[i] = 100.0 + (i - (n - 15)) * 0.5

    # 신호 봉: 큰 상승 + 작은 거래량 (impact 극대화)
    closes[-2] = closes[-3] + 50.0  # 큰 가격 변화
    volumes[-2] = 1.0               # 매우 작은 거래량 → impact 폭발

    opens = [c - 0.3 for c in closes]
    return pd.DataFrame({"open": opens, "close": closes, "volume": volumes})


def _make_sell_df(n: int = 30) -> pd.DataFrame:
    """SELL 신호 유도: 큰 가격 변화 + 하락 방향."""
    closes = [100.0] * n
    volumes = [10000.0] * n

    # 신호 봉 이전: 완만한 하락 (dir_ma < 0 유도)
    for i in range(n - 15, n - 2):
        closes[i] = 100.0 - (i - (n - 15)) * 0.5

    # 신호 봉: 큰 하락 + 작은 거래량
    closes[-2] = closes[-3] - 50.0
    volumes[-2] = 1.0

    opens = [c + 0.3 for c in closes]
    return pd.DataFrame({"open": opens, "close": closes, "volume": volumes})


class TestPriceImpactStrategy:

    def setup_method(self):
        self.strategy = PriceImpactStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "price_impact"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, PriceImpactStrategy)

    # 3. 데이터 부족 (< 25행) → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음 — Signal 반환
    def test_returns_signal(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig is not None
        assert isinstance(sig, Signal)

    # 5. reasoning 필드 비어있지 않음
    def test_reasoning_nonempty(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. BUY 신호 생성
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 7. SELL 신호 생성
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 8. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)

    # 9. BUY reasoning에 방향/충격 정보 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "impact" in sig.reasoning.lower() or "direction" in sig.reasoning.lower()

    # 10. SELL reasoning 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "impact" in sig.reasoning.lower() or "direction" in sig.reasoning.lower()

    # 11. HIGH confidence 가능
    def test_high_confidence_possible(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 확인
    def test_strategy_field(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_impact"

    # 14. 최소 행 경계 (정확히 25행)
    def test_min_rows_boundary(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
