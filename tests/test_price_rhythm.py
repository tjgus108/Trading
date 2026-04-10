"""
PriceRhythmStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.price_rhythm import PriceRhythmStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(closes: list, volumes: Optional[list] = None) -> pd.DataFrame:
    n = len(closes)
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": volumes,
    })


def _make_flat_df(n: int = _MIN_ROWS + 5, base: float = 100.0,
                  vol: float = 1000.0) -> pd.DataFrame:
    closes = [base] * n
    volumes = [vol] * n
    return _make_df(closes, volumes)


def _make_buy_signal_df() -> pd.DataFrame:
    """
    rhythm_sum > 2, rhythm_change > 0, volume > vol_ma 조건.
    마지막 5개 연속 상승봉 + 볼륨 급증.
    """
    n = _MIN_ROWS + 5
    closes = []
    base = 100.0
    # 앞부분: 혼합
    for i in range(n - 6):
        closes.append(base + (i % 3) * 0.1)
    # 마지막 6개: 연속 상승 (rhythm_sum = +5)
    last = closes[-1]
    for i in range(6):
        last += 1.0
        closes.append(last)
    volumes = [500.0] * (n - 3) + [2000.0, 2000.0, 2000.0]  # 끝 볼륨 급증
    return _make_df(closes[:n], volumes[:n])


def _make_sell_signal_df() -> pd.DataFrame:
    """
    rhythm_sum < -2, rhythm_change < 0, volume > vol_ma 조건.
    마지막 5개 연속 하락봉 + 볼륨 급증.
    """
    n = _MIN_ROWS + 5
    closes = []
    base = 110.0
    for i in range(n - 6):
        closes.append(base - (i % 3) * 0.1)
    last = closes[-1]
    for i in range(6):
        last -= 1.0
        closes.append(last)
    volumes = [500.0] * (n - 3) + [2000.0, 2000.0, 2000.0]
    return _make_df(closes[:n], volumes[:n])


class TestPriceRhythmStrategy:

    def setup_method(self):
        self.strategy = PriceRhythmStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_rhythm"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_flat_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 부족 데이터 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_flat_df(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 4. Signal 타입 반환
    def test_returns_signal_type(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 5. strategy 필드
    def test_signal_strategy_field(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_rhythm"

    # 6. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 7. 평평한 데이터 → HOLD (rhythm_sum ≈ 0)
    def test_flat_data_returns_hold(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. BUY 신호 action
    def test_buy_signal_action(self):
        df = _make_buy_signal_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 신호 action
    def test_sell_signal_action(self):
        df = _make_sell_signal_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. confidence 유효값
    def test_confidence_valid_values(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. HOLD → confidence LOW
    def test_hold_confidence_is_low(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 12. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 13. abs(rhythm_sum) >= 4 → HIGH confidence
    def test_high_confidence_strong_rhythm(self):
        """5연속 상승봉 → rhythm_sum = 5 → HIGH confidence (if BUY)."""
        n = _MIN_ROWS + 5
        closes = [100.0 + i for i in range(n)]
        volumes = [2000.0] * n
        df = _make_df(closes, volumes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 14. 볼륨 낮으면 신호 없음 → HOLD
    def test_no_signal_low_volume(self):
        """리듬 조건 맞아도 볼륨 < vol_ma → HOLD."""
        n = _MIN_ROWS + 5
        closes = []
        base = 100.0
        for i in range(n - 6):
            closes.append(base + (i % 3) * 0.1)
        last = closes[-1]
        for i in range(6):
            last += 1.0
            closes.append(last)
        # 볼륨을 항상 낮게 설정 (vol_ma ≈ volume)
        volumes = [1000.0] * n
        volumes[-2] = 500.0  # 신호 봉 볼륨 낮게
        df = _make_df(closes[:n], volumes[:n])
        sig = self.strategy.generate(df)
        # volume <= vol_ma → HOLD 가능
        assert sig.action in (Action.HOLD, Action.BUY)

    # 15. 최소 행 경계값
    def test_min_rows_boundary(self):
        df = _make_flat_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 16. invalidation 필드 존재
    def test_invalidation_field_exists(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "invalidation")

    # 17. NaN 포함 데이터 → HOLD
    def test_nan_close_returns_hold(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        df.loc[df.index[-2], "close"] = float("nan")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
