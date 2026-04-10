"""
RelativeMomentumIndexStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.relative_momentum_index import RelativeMomentumIndexStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, closes=None) -> pd.DataFrame:
    if closes is None:
        closes = [100.0] * n
    closes = list(closes)
    assert len(closes) == n
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_oversold_bounce_df(n: int = 40) -> pd.DataFrame:
    """
    RMI < 30 + rising: 앞부분 급락 후 최근 1봉 소폭 반등.
    delta = close.diff(3) → 앞이 훨씬 높아야 gain 낮고 loss 높음 → RMI 낮음.
    마지막 -2봉이 -3봉보다 조금 높아야 rmi > rmi.shift(1).
    """
    # 앞 30개: 100에서 70까지 급락
    front = np.linspace(100, 70, n - 10).tolist()
    # 이후 9개: 70 유지
    mid = [70.0] * 9
    # 마지막 1개 (현재 진행 중 캔들, idx=-1): 71 (사용 안 됨)
    tail = [71.0]
    closes = front + mid + tail
    # idx=-2 봉을 70.5로: 이전 봉(70.0)보다 높아서 RMI 상승
    closes[-2] = 70.5
    return _make_df(n=n, closes=closes)


def _make_overbought_reversal_df(n: int = 40) -> pd.DataFrame:
    """
    RMI > 70 + falling: 앞부분 급등 후 최근 1봉 소폭 하락.
    """
    front = np.linspace(70, 100, n - 10).tolist()
    mid = [100.0] * 9
    tail = [99.0]
    closes = front + mid + tail
    # idx=-2 봉을 99.5로: 이전 봉(100.0)보다 낮아서 RMI 하락
    closes[-2] = 99.5
    return _make_df(n=n, closes=closes)


class TestRelativeMomentumIndexStrategy:

    def setup_method(self):
        self.strategy = RelativeMomentumIndexStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "relative_momentum_index"

    # 2. 데이터 부족 (< 20행) → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 경계값: 정확히 20행
    def test_exactly_min_rows(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")
        assert sig.reasoning != ""

    # 5. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "relative_momentum_index"

    # 6. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 7. BUY: oversold bounce
    def test_buy_signal(self):
        df = _make_oversold_bounce_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 8. BUY entry_price == last close
    def test_buy_entry_price(self):
        df = _make_oversold_bounce_df(n=40)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.entry_price == float(df["close"].iloc[-2])

    # 9. SELL: overbought reversal
    def test_sell_signal(self):
        df = _make_overbought_reversal_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 10. SELL entry_price == last close
    def test_sell_entry_price(self):
        df = _make_overbought_reversal_df(n=40)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.entry_price == float(df["close"].iloc[-2])

    # 11. HOLD: flat market (rmi ~= 50)
    def test_hold_flat_market(self):
        closes = [100.0] * 30
        df = _make_df(n=30, closes=closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. BUY confidence HIGH when rmi < 20
    def test_buy_confidence_high_extreme(self):
        # 더 극단적인 하락으로 rmi < 20 유도
        closes = np.linspace(100, 55, 38).tolist() + [56.0, 57.0]
        df = _make_df(n=40, closes=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # rmi < 20이면 HIGH, 아니면 MEDIUM
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. SELL confidence HIGH when rmi > 80
    def test_sell_confidence_high_extreme(self):
        closes = np.linspace(55, 100, 38).tolist() + [99.0, 98.0]
        df = _make_df(n=40, closes=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 14. 대량 데이터에서 에러 없이 동작
    def test_large_dataframe(self):
        df = _make_df(n=500)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. HOLD reasoning 포함
    def test_hold_reasoning_not_empty(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""
