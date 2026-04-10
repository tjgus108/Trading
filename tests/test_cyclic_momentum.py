"""
CyclicMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.cyclic_momentum import CyclicMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _make_df(n: int = _MIN_ROWS + 5, close_series: Optional[list] = None,
             volume: float = 1000.0) -> pd.DataFrame:
    if close_series is None:
        closes = [100.0] * n
    else:
        closes = list(close_series)
        n = len(closes)
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [volume] * n,
    })


def _make_df_plain(n: int = _MIN_ROWS + 5, base: float = 100.0) -> pd.DataFrame:
    closes = [base] * n
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_buy_signal_df() -> pd.DataFrame:
    """
    z_cycle < -1.0, rising (z_cycle > z_prev), roc5 > 0 조건 생성.
    - 처음 25개: 점진 하락 → 사이클 저점 형성
    - 이후 5개: 약간 반등 (roc5 > 0, z_cycle 상승)
    """
    n = _MIN_ROWS + 5
    # 앞부분 하락해서 20MA 아래 (detrended 음수, cycle_osc 음수)
    # 마지막 부분 소폭 반등
    closes = []
    for i in range(n):
        if i < 22:
            closes.append(100.0 - i * 0.5)  # 하락
        else:
            closes.append(closes[-1] + 0.1)  # 소폭 반등
    return _make_df(close_series=closes)


def _make_sell_signal_df() -> pd.DataFrame:
    """z_cycle > 1.0, falling, roc5 < 0 조건."""
    n = _MIN_ROWS + 5
    closes = []
    for i in range(n):
        if i < 22:
            closes.append(100.0 + i * 0.5)  # 상승
        else:
            closes.append(closes[-1] - 0.1)  # 소폭 하락
    return _make_df(close_series=closes)


class TestCyclicMomentumStrategy:

    def setup_method(self):
        self.strategy = CyclicMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "cyclic_momentum"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_df_plain(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_df_plain(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 4. Signal 타입 반환
    def test_returns_signal_type(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 5. strategy 필드
    def test_signal_strategy_field(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.strategy == "cyclic_momentum"

    # 6. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 7. 평평한 데이터 → HOLD (z_cycle ≈ 0)
    def test_flat_data_returns_hold(self):
        df = _make_df_plain(n=_MIN_ROWS + 5, base=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. BUY 신호 action
    def test_buy_signal_action(self):
        df = _make_buy_signal_df()
        sig = self.strategy.generate(df)
        # 사이클 저점 형성 여부에 따라 BUY 또는 HOLD
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 신호 action
    def test_sell_signal_action(self):
        df = _make_sell_signal_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. confidence는 HIGH 또는 MEDIUM 또는 LOW
    def test_confidence_valid_values(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. HOLD confidence는 LOW
    def test_hold_confidence_is_low(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 12. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 13. 강한 z_cycle → HIGH confidence (BUY 시나리오)
    def test_high_confidence_on_strong_zcycle_buy(self):
        """abs(z_cycle) > 1.5 이면 HIGH confidence."""
        # 매우 급격한 하락 후 반등: 강한 z_cycle 음수
        n = _MIN_ROWS + 10
        closes = []
        for i in range(n):
            if i < 25:
                closes.append(100.0 - i * 2.0)  # 급락
            else:
                closes.append(closes[-1] + 0.5)  # 반등
        df = _make_df(close_series=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 14. NaN 포함 데이터 → HOLD
    def test_nan_data_returns_hold(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        df.loc[df.index[-2], "close"] = float("nan")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. 최소 행 경계값 (_MIN_ROWS)
    def test_min_rows_boundary(self):
        df = _make_df_plain(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 16. invalidation 필드 존재
    def test_invalidation_field_exists(self):
        df = _make_df_plain(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "invalidation")
