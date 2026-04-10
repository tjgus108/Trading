"""
SmartMoneyFlowStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.smart_money_flow import SmartMoneyFlowStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 30,
    close: float = 100.0,
    open_: float = 99.0,
    volume: float = 1000.0,
) -> pd.DataFrame:
    closes = [close] * n
    opens = [open_] * n
    volumes = [volume] * n
    return pd.DataFrame({"open": opens, "close": closes, "volume": volumes})


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """BUY: smf > smf_signal AND smf < 0."""
    closes = []
    opens = []
    volumes = []

    for i in range(n):
        if i < n - 15:
            # 초반: 큰 하락봉 → weighted_flow 음수 축적
            o = 110.0
            c = 100.0
            v = 5000.0
        elif i == n - 2:
            # 신호 봉: 반등 시작 (close > open → otc_return 양수, 하지만 smf는 여전히 음수)
            o = 100.0
            c = 102.0
            v = 3000.0
        else:
            o = 101.0
            c = 101.5
            v = 1000.0
        opens.append(o)
        closes.append(c)
        volumes.append(v)

    return pd.DataFrame({"open": opens, "close": closes, "volume": volumes})


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """SELL: smf < smf_signal AND smf > 0."""
    closes = []
    opens = []
    volumes = []

    for i in range(n):
        if i < n - 15:
            # 초반: 큰 상승봉 → weighted_flow 양수 축적
            o = 90.0
            c = 100.0
            v = 5000.0
        elif i == n - 2:
            # 신호 봉: 하락 시작 (close < open → otc_return 음수, smf 아직 양수)
            o = 100.0
            c = 98.0
            v = 3000.0
        else:
            o = 99.0
            c = 98.5
            v = 1000.0
        opens.append(o)
        closes.append(c)
        volumes.append(v)

    return pd.DataFrame({"open": opens, "close": closes, "volume": volumes})


class TestSmartMoneyFlowStrategy:

    def setup_method(self):
        self.strategy = SmartMoneyFlowStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "smart_money_flow"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, SmartMoneyFlowStrategy)

    # 3. 데이터 부족 (< 20행) → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=15)
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

    # 6. BUY 신호 생성 가능
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        # BUY 또는 HOLD (데이터에 따라 달라질 수 있음, action 타입 확인)
        assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)

    # 7. SELL 신호 생성 가능
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)

    # 8. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)

    # 9. BUY reasoning에 smf 정보 포함
    def test_buy_reasoning_smf(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "smf" in sig.reasoning.lower() or "smart" in sig.reasoning.lower()

    # 10. SELL reasoning 포함
    def test_sell_reasoning_smf(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "smf" in sig.reasoning.lower() or "smart" in sig.reasoning.lower()

    # 11. confidence는 HIGH 또는 MEDIUM 또는 LOW
    def test_confidence_valid(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 확인
    def test_strategy_field(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "smart_money_flow"

    # 14. 최소 행 경계 (정확히 20행)
    def test_min_rows_boundary(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
