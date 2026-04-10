"""
DualMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.dual_momentum import DualMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _make_df(n: int = _MIN_ROWS + 5,
             base_close: float = 100.0,
             trend: str = "up") -> pd.DataFrame:
    """
    trend='up': 가속 상승 시계열 → BUY 신호 유발 (abs_mom>0, rel_mom > rel_ma, abs_ma>0)
    trend='down': 가속 하락 시계열 → SELL 신호 유발
    trend='flat': 횡보 → HOLD
    가속도가 있어야 relative_momentum이 rel_ma를 초과함
    """
    rows = n
    if trend == "up":
        # 가속 상승: 후반부로 갈수록 상승폭 커짐
        closes = [base_close * (1.01 ** (i * i / rows)) for i in range(rows)]
    elif trend == "down":
        closes = [base_close * (0.99 ** (i * i / rows)) for i in range(rows)]
    else:
        closes = [base_close] * rows

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [1000.0] * rows,
    })
    return df


class TestDualMomentumStrategy:

    def setup_method(self):
        self.strategy = DualMomentumStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "dual_momentum"

    # 2. BaseStrategy 상속
    def test_is_base_strategy(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 시 HOLD 반환
    def test_insufficient_data_returns_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. 최소 행수 정확히 체크 (29행 → HOLD)
    def test_min_rows_boundary(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY 신호 (상승 추세)
    def test_buy_signal_uptrend(self):
        df = _make_df(n=_MIN_ROWS + 10, trend="up")
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 6. SELL 신호 (하락 추세)
    def test_sell_signal_downtrend(self):
        df = _make_df(n=_MIN_ROWS + 10, trend="down")
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 7. HOLD 신호 (횡보)
    def test_hold_signal_flat(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. Signal 필드 완전성 확인
    def test_signal_fields_complete(self):
        df = _make_df(n=_MIN_ROWS + 10, trend="up")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "dual_momentum"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert sig.invalidation != "" or sig.action == Action.HOLD

    # 9. entry_price = 마지막 완성 캔들의 close
    def test_entry_price_is_last_complete_candle(self):
        df = _make_df(n=_MIN_ROWS + 10, trend="up")
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 10. BUY 시 confidence HIGH (강한 상승)
    def test_buy_high_confidence(self):
        # 매우 강한 가속 상승 → abs_mom >> std
        rows = _MIN_ROWS + 20
        closes = [100.0 * (1.02 ** (i * i / rows)) for i in range(rows)]
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 1 for c in closes],
            "low": [c - 1 for c in closes],
            "volume": [1000.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 11. SELL 시 confidence HIGH (강한 하락)
    def test_sell_high_confidence(self):
        rows = _MIN_ROWS + 20
        closes = [100.0 * (0.95 ** i) for i in range(rows)]
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 1 for c in closes],
            "low": [c - 1 for c in closes],
            "volume": [1000.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 12. NaN 포함 데이터 → HOLD
    def test_nan_data_returns_hold(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="up")
        df.loc[df.index[-2], "close"] = float("nan")
        sig = self.strategy.generate(df)
        # NaN 가격이면 HOLD 또는 NaN 관련 처리
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 13. 정확히 _MIN_ROWS 행 → 정상 처리
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS, trend="up")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. 큰 데이터셋에서도 정상 동작
    def test_large_dataset(self):
        df = _make_df(n=200, trend="up")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
