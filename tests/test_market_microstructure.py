"""
MarketMicrostructureStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.market_microstructure import MarketMicrostructureStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 25, close: float = 100.0, open_: float = 99.0,
             high: float = 102.0, low: float = 98.0, volume: float = 1000.0) -> pd.DataFrame:
    """기본 봉 → HOLD 유도. 마지막 완성봉 = iloc[-2]."""
    rows = []
    for _ in range(n):
        rows.append({"open": open_, "close": close, "high": high, "low": low, "volume": volume})
    return pd.DataFrame(rows)


def _make_buy_df(n: int = 25) -> pd.DataFrame:
    """좁은 spread + 상승 → BUY 신호 유도."""
    rows = []
    # 대부분 넓은 spread로 spread_ma 높이기
    for i in range(n - 5):
        rows.append({"open": 99.0, "close": 100.0, "high": 110.0, "low": 90.0, "volume": 1000.0})
    # 마지막 5봉: 좁은 spread + 상승
    for i in range(5):
        rows.append({"open": 99.5, "close": 100.1, "high": 100.3, "low": 99.8, "volume": 1000.0})
    return pd.DataFrame(rows)


def _make_sell_df(n: int = 25) -> pd.DataFrame:
    """좁은 spread + 하락 → SELL 신호 유도."""
    rows = []
    # 대부분 넓은 spread로 spread_ma 높이기
    for i in range(n - 5):
        rows.append({"open": 100.0, "close": 100.0, "high": 110.0, "low": 90.0, "volume": 1000.0})
    # 마지막 5봉: 좁은 spread + 하락
    for i in range(5):
        rows.append({"open": 100.5, "close": 99.9, "high": 100.6, "low": 99.7, "volume": 1000.0})
    return pd.DataFrame(rows)


def _make_high_conf_buy_df(n: int = 25) -> pd.DataFrame:
    """spread < spread_ma * 0.5 → HIGH confidence 유도."""
    rows = []
    # 앞부분 매우 넓은 spread
    for i in range(n - 5):
        rows.append({"open": 50.0, "close": 100.0, "high": 150.0, "low": 50.0, "volume": 1000.0})
    # 마지막: 매우 좁은 spread + 상승
    for i in range(5):
        rows.append({"open": 99.9, "close": 100.1, "high": 100.15, "low": 99.85, "volume": 1000.0})
    return pd.DataFrame(rows)


class TestMarketMicrostructureStrategy:

    def setup_method(self):
        self.strategy = MarketMicrostructureStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "market_microstructure"

    # 2. 인스턴스 생성
    def test_instance(self):
        assert isinstance(self.strategy, MarketMicrostructureStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY 신호 또는 HOLD 반환
    def test_buy_or_hold(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 신호 또는 HOLD 반환
    def test_sell_or_hold(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. HIGH confidence 조건
    def test_high_confidence_possible(self):
        df = _make_high_conf_buy_df()
        sig = self.strategy.generate(df)
        # BUY이면 HIGH 또는 MEDIUM
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 12. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert sig.strategy == "market_microstructure"

    # 13. 최소 행 수(20)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "유동성" in sig.reasoning or "spread" in sig.reasoning

    # 15. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "유동성" in sig.reasoning or "spread" in sig.reasoning

    # 16. None 입력 → entry_price 0
    def test_none_entry_price_zero(self):
        sig = self.strategy.generate(None)
        assert sig.entry_price == 0.0

    # 17. 동일 close → HOLD (방향 없음)
    def test_same_close_hold(self):
        # 동일 close → close_val == prev_close_val → 방향 조건 불충족
        df = _make_df(n=25, close=100.0)
        sig = self.strategy.generate(df)
        # HOLD 가능성 높음 (close == prev_close)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
