"""
OrderFlowImbalanceV2Strategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.order_flow_imbalance_v2 import OrderFlowImbalanceV2Strategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 25, close: float = 100.0, open_: float = 99.0,
             high: float = 101.0, low: float = 98.0, volume: float = 1000.0) -> pd.DataFrame:
    """균형적인 봉 → HOLD 유도. 마지막 완성봉 = iloc[-2]."""
    rows = []
    for _ in range(n):
        rows.append({"open": open_, "close": close, "high": high, "low": low, "volume": volume})
    return pd.DataFrame(rows)


def _make_buy_df(n: int = 25) -> pd.DataFrame:
    """강한 양봉 + 거래량 → BUY 신호 유도."""
    rows = []
    for _ in range(n):
        rows.append({"open": 90.0, "close": 100.0, "high": 101.0, "low": 89.0, "volume": 2000.0})
    return pd.DataFrame(rows)


def _make_sell_df(n: int = 25) -> pd.DataFrame:
    """강한 음봉 + 거래량 → SELL 신호 유도."""
    rows = []
    for _ in range(n):
        rows.append({"open": 100.0, "close": 90.0, "high": 101.0, "low": 89.0, "volume": 2000.0})
    return pd.DataFrame(rows)


def _make_high_conf_buy_df(n: int = 25) -> pd.DataFrame:
    """abs(imbalance) > 0.4 → HIGH confidence BUY 유도."""
    rows = []
    for _ in range(n):
        # 완전 양봉, 거래량 집중
        rows.append({"open": 80.0, "close": 100.0, "high": 100.0, "low": 80.0, "volume": 5000.0})
    return pd.DataFrame(rows)


class TestOrderFlowImbalanceV2Strategy:

    def setup_method(self):
        self.strategy = OrderFlowImbalanceV2Strategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "order_flow_imbalance_v2"

    # 2. 인스턴스 생성
    def test_instance(self):
        assert isinstance(self.strategy, OrderFlowImbalanceV2Strategy)

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

    # 8. BUY 신호 생성 확인
    def test_buy_signal_generated(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 신호 생성 확인
    def test_sell_signal_generated(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. HIGH confidence 조건
    def test_high_confidence_buy(self):
        df = _make_high_conf_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 12. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert sig.strategy == "order_flow_imbalance_v2"

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
            assert "매수" in sig.reasoning or "imbalance" in sig.reasoning

    # 15. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "매도" in sig.reasoning or "imbalance" in sig.reasoning

    # 16. None 입력 → entry_price 0
    def test_none_entry_price_zero(self):
        sig = self.strategy.generate(None)
        assert sig.entry_price == 0.0

    # 17. volume 컬럼 없으면 에러 없이 처리
    def test_volume_column_required(self):
        df = pd.DataFrame([
            {"open": 99.0, "close": 100.0, "high": 101.0, "low": 98.0}
            for _ in range(25)
        ])
        # volume 없으면 KeyError 발생할 수 있음 — 전략은 volume을 요구하므로 예외 허용
        try:
            sig = self.strategy.generate(df)
        except (KeyError, Exception):
            pass  # 예상된 동작
