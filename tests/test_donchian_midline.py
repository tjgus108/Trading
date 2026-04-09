"""
DonchianMidlineStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

from typing import Optional

import pandas as pd
import pytest

from src.strategy.donchian_midline import DonchianMidlineStrategy
from src.strategy.base import Action, Confidence, Signal

_N = 60  # 최소 55행 초과


def _make_df(
    n: int = _N,
    close_last: float = 105.0,
    close_prev: float = 99.0,
    high_val: Optional[float] = None,
    low_val: Optional[float] = None,
) -> pd.DataFrame:
    """
    신호 봉(-2) 기준 DataFrame 생성.
    Donchian upper = high.rolling(20).max() ≈ high_val
    Donchian lower = low.rolling(20).min()  ≈ low_val
    midline ≈ (high_val + low_val) / 2
    """
    base = 100.0
    _high = high_val if high_val is not None else base + 10.0
    _low = low_val if low_val is not None else base - 10.0

    closes = [base] * n
    highs = [_high] * n
    lows = [_low] * n
    opens = [base] * n

    closes[-2] = close_last
    closes[-3] = close_prev
    closes[-1] = close_last
    opens[-2] = close_prev
    opens[-1] = close_last

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


class TestDonchianMidlineStrategy:

    def setup_method(self):
        self.strategy = DonchianMidlineStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "donchian_midline"

    # 2. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 정확히 55행 경계 처리
    def test_exactly_min_rows(self):
        df = _make_df(n=55)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. HOLD: 크로스 없음 (prev==last, 동일 가격)
    def test_hold_no_crossover(self):
        df = _make_df(n=_N, close_last=100.0, close_prev=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "donchian_midline"

    # 5. BUY: close가 midline을 상향 돌파 + close > ema50
    def test_buy_crosses_above_midline(self):
        # mid ≈ 100.0, prev_close=99.0 (<= mid), last_close=105.0 (> mid)
        # EMA50 ≈ 100 (초기 모두 100), close=105 > ema50 → BUY
        df = _make_df(n=_N, close_last=105.0, close_prev=99.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "donchian_midline"
        assert sig.entry_price > 0

    # 6. BUY confidence HIGH: close > upper * 0.98
    def test_buy_high_confidence_near_upper(self):
        # upper=110, upper*0.98=107.8, close=109.0 > 107.8 → HIGH
        df = _make_df(n=_N, close_last=109.0, close_prev=99.0,
                      high_val=110.0, low_val=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. BUY confidence MEDIUM: close not near upper
    def test_buy_medium_confidence(self):
        # upper=110, close=101 (> mid=100 but < 107.8) → MEDIUM
        df = _make_df(n=_N, close_last=101.0, close_prev=99.0,
                      high_val=110.0, low_val=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 8. SELL: close가 midline을 하향 돌파 + close < ema50
    def test_sell_crosses_below_midline(self):
        # mid=100, prev_close=101 (>= mid), last_close=94 (< mid)
        # EMA50: 초반 100.0 → ema50 ≈ 100, close=94 < ema50 → SELL
        n = _N
        base = 100.0
        closes = [base] * n
        highs = [base + 10.0] * n
        lows = [base - 10.0] * n
        opens = [base] * n

        closes[-3] = 101.0
        closes[-2] = 94.0
        closes[-1] = 94.0
        opens[-2] = 101.0

        df = pd.DataFrame({
            "open": opens, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "donchian_midline"

    # 9. SELL confidence HIGH: close < lower * 1.02
    def test_sell_high_confidence_near_lower(self):
        # lower=90, lower*1.02=91.8, close=90.5 < 91.8 → HIGH
        n = _N
        base = 100.0
        closes = [base] * n
        highs = [base + 10.0] * n
        lows = [base - 10.0] * n
        opens = [base] * n

        closes[-3] = 101.0
        closes[-2] = 90.5
        closes[-1] = 90.5
        opens[-2] = 101.0

        df = pd.DataFrame({
            "open": opens, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_N)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 11. entry_price는 양수
    def test_entry_price_positive(self):
        df = _make_df(n=_N)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 12. BUY 신호 시 invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _make_df(n=_N, close_last=105.0, close_prev=99.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.invalidation != ""

    # 13. SELL 신호 시 invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        n = _N
        base = 100.0
        closes = [base] * n
        highs = [base + 10.0] * n
        lows = [base - 10.0] * n
        opens = [base] * n
        closes[-3] = 101.0
        closes[-2] = 94.0
        closes[-1] = 94.0
        opens[-2] = 101.0
        df = pd.DataFrame({
            "open": opens, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.invalidation != ""

    # 14. 큰 데이터셋 처리 (안정성)
    def test_large_dataset(self):
        df = _make_df(n=200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
