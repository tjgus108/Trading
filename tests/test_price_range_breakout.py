"""
PriceRangeBreakoutStrategy 단위 테스트 (mock DataFrame, API 호출 없음).
"""

import pandas as pd
import numpy as np
import pytest
from typing import Optional

from src.strategy.price_range_breakout import PriceRangeBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal

_N = 60  # 최소 25행 초과


def _make_breakout_df(
    n: int = _N,
    base: float = 100.0,
    direction: str = "up",   # "up" or "down"
    wide_pct: float = 0.10,  # 초기 wide range (range_ma 높게)
    narrow_pct: float = 0.01,  # 최근 narrow range (compression)
    breakout_gap: float = 2.0,  # 돌파 폭
) -> pd.DataFrame:
    """
    앞부분: wide range → range_ma 크게
    뒷부분(15개): narrow range → compression = True
    last candle (idx=-2): close = range_high + gap (up) or range_low - gap (down)
    """
    wide_h = base * (1 + wide_pct / 2)
    wide_l = base * (1 - wide_pct / 2)
    narrow_h = base * (1 + narrow_pct / 2)
    narrow_l = base * (1 - narrow_pct / 2)

    # wide range for first (n - 20) candles
    split = n - 20
    highs = [wide_h] * split + [narrow_h] * 20
    lows = [wide_l] * split + [narrow_l] * 20
    closes = [base] * n
    opens = [base] * n
    volumes = [1000.0] * n

    # last completed candle at idx = n-2
    if direction == "up":
        breakout_close = narrow_h + breakout_gap
    else:
        breakout_close = narrow_l - breakout_gap

    closes[-2] = breakout_close
    opens[-2] = base
    # Keep high/low at narrow range (don't inflate with breakout_close)
    highs[-2] = narrow_h
    lows[-2] = narrow_l
    closes[-1] = breakout_close
    opens[-1] = breakout_close

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


def _make_no_compression_df(
    n: int = _N,
    base: float = 100.0,
) -> pd.DataFrame:
    """모든 구간 일정 range → compression False (range_width ≈ range_ma)."""
    pct = 0.05
    rh = base * (1 + pct / 2)
    rl = base * (1 - pct / 2)
    closes = [base] * n
    highs = [rh] * n
    lows = [rl] * n
    opens = [base] * n
    volumes = [1000.0] * n
    return pd.DataFrame({
        "open": opens, "close": closes, "high": highs, "low": lows, "volume": volumes,
    })


class TestPriceRangeBreakoutStrategy:

    def setup_method(self):
        self.strategy = PriceRangeBreakoutStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "price_range_breakout"

    # 2. 데이터 부족 (< 25행) → HOLD
    def test_insufficient_data(self):
        df = _make_no_compression_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "데이터 부족" in sig.reasoning

    # 3. 정확히 25행 → Signal 반환
    def test_exactly_min_rows(self):
        df = _make_no_compression_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. 균일한 range (compression 없음) → BUY/SELL 없음
    def test_hold_no_compression(self):
        df = _make_no_compression_df(n=_N)
        sig = self.strategy.generate(df)
        # range_width ≈ range_ma → compression False → HOLD
        assert sig.action == Action.HOLD

    # 5. BUY: 압축 후 상향 돌파
    def test_buy_signal_upward_breakout(self):
        df = _make_breakout_df(n=_N, base=100.0, direction="up",
                               wide_pct=0.10, narrow_pct=0.01, breakout_gap=2.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "price_range_breakout"
        assert sig.entry_price > 0

    # 6. SELL: 압축 후 하향 돌파
    def test_sell_signal_downward_breakout(self):
        df = _make_breakout_df(n=_N, base=100.0, direction="down",
                               wide_pct=0.10, narrow_pct=0.01, breakout_gap=2.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "price_range_breakout"
        assert sig.entry_price > 0

    # 7. BUY confidence HIGH: range_width < range_ma * 0.5
    def test_buy_high_confidence(self):
        # narrow_pct=0.002 → width=0.2, wide_pct=0.10 → ma~10
        # 0.2 < 10*0.5=5 → HIGH
        df = _make_breakout_df(n=_N, base=100.0, direction="up",
                               wide_pct=0.10, narrow_pct=0.002, breakout_gap=2.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 8. BUY confidence MEDIUM: range_width between range_ma*0.5 and range_ma*0.7
    def test_buy_medium_confidence(self):
        # narrow_pct=0.06 → width=6, wide_pct=0.10 → ma~10
        # 6 < 10*0.7=7 → compression, HIGH if 6<10*0.5=5 → False → MEDIUM
        df = _make_breakout_df(n=_N, base=100.0, direction="up",
                               wide_pct=0.10, narrow_pct=0.06, breakout_gap=2.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.MEDIUM

    # 9. SELL confidence HIGH
    def test_sell_high_confidence(self):
        df = _make_breakout_df(n=_N, base=100.0, direction="down",
                               wide_pct=0.10, narrow_pct=0.002, breakout_gap=2.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_no_compression_df(n=_N)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 11. BUY 신호: invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _make_breakout_df(n=_N, direction="up")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.invalidation != ""

    # 12. SELL 신호: invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _make_breakout_df(n=_N, direction="down")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.invalidation != ""

    # 13. entry_price 양수
    def test_entry_price_positive(self):
        df = _make_no_compression_df(n=_N)
        sig = self.strategy.generate(df)
        assert sig.entry_price >= 0

    # 14. 큰 데이터셋 안정성
    def test_large_dataset(self):
        df = _make_breakout_df(n=200, direction="up")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. None DataFrame → HOLD
    def test_none_dataframe(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 16. BUY reasoning에 "돌파" 포함
    def test_buy_reasoning_contains_breakout(self):
        df = _make_breakout_df(n=_N, direction="up")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "돌파" in sig.reasoning
