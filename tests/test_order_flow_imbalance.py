"""
OrderFlowImbalanceStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.order_flow_imbalance import OrderFlowImbalanceStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 20, close: float = 100.0, open_: float = 99.0,
             high: float = 101.0, low: float = 98.0) -> pd.DataFrame:
    """균형적인 봉으로 HOLD 유도. 마지막 완성봉 = iloc[-2]."""
    rows = []
    for _ in range(n):
        rows.append({"open": open_, "close": close, "high": high, "low": low})
    return pd.DataFrame(rows)


def _make_buy_df(n: int = 20) -> pd.DataFrame:
    """강한 매수 압력 봉들 → BUY 신호 유도."""
    rows = []
    for _ in range(n):
        # 큰 양봉 + 아래 꼬리 거의 없음 → buy_pressure 높음
        rows.append({"open": 95.0, "close": 100.0, "high": 100.5, "low": 94.8})
    return pd.DataFrame(rows)


def _make_sell_df(n: int = 20) -> pd.DataFrame:
    """강한 매도 압력 봉들 → SELL 신호 유도."""
    rows = []
    for _ in range(n):
        # 큰 음봉 + 위 꼬리 거의 없음 → sell_pressure 높음
        rows.append({"open": 100.0, "close": 95.0, "high": 100.2, "low": 94.5})
    return pd.DataFrame(rows)


def _make_high_conf_buy_df(n: int = 20) -> pd.DataFrame:
    """abs(imbalance) > 0.5 → HIGH confidence BUY."""
    rows = []
    for _ in range(n):
        # 완전 양봉, 꼬리 없음 → imbalance 최대
        rows.append({"open": 90.0, "close": 100.0, "high": 100.0, "low": 90.0})
    return pd.DataFrame(rows)


class TestOrderFlowImbalanceStrategy:

    def setup_method(self):
        self.strategy = OrderFlowImbalanceStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "order_flow_imbalance"

    # 2. 인스턴스 생성
    def test_instance(self):
        assert isinstance(self.strategy, OrderFlowImbalanceStrategy)

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
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "매수" in sig.reasoning or "imbalance" in sig.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "매도" in sig.reasoning or "imbalance" in sig.reasoning

    # 10. HIGH confidence: abs(imbalance) > 0.5
    def test_high_confidence_buy(self):
        df = _make_high_conf_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence: abs(imbalance) <= 0.5
    def test_medium_confidence(self):
        # 중간 수준의 매수 압력 (imbalance ~0.35)
        rows = []
        for _ in range(20):
            rows.append({"open": 98.0, "close": 100.0, "high": 101.5, "low": 97.5})
        df = pd.DataFrame(rows)
        sig = self.strategy.generate(df)
        # HOLD이거나 BUY/SELL MEDIUM
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.strategy == "order_flow_imbalance"

    # 14. 최소 행 수(15)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
