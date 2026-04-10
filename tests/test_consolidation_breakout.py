"""
ConsolidationBreakoutStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import numpy as np
import pytest

from src.strategy.consolidation_breakout import ConsolidationBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal

_N = 40  # 최소 15행 초과


def _make_df(
    n: int = _N,
    consol_range_pct: float = 0.01,  # consolidation 범위
    base: float = 100.0,
    last_close: float = None,
    last_volume: float = 1000.0,
    avg_volume: float = 500.0,
) -> pd.DataFrame:
    """
    consolidation window (3~10봉 이전)은 narrow range,
    last completed candle (df.iloc[-2])의 close를 조정 가능.
    """
    consol_high = base * (1 + consol_range_pct / 2)
    consol_low = base * (1 - consol_range_pct / 2)

    closes = [base] * n
    highs = [consol_high] * n
    lows = [consol_low] * n
    opens = [base] * n
    volumes = [avg_volume] * n

    # df.iloc[-2] = last completed candle
    if last_close is None:
        last_close = base
    closes[-2] = last_close
    opens[-2] = base
    highs[-2] = max(last_close, consol_high)
    lows[-2] = min(last_close, consol_low)
    volumes[-2] = last_volume

    # df.iloc[-1] = current in-progress candle (ignored by strategy)
    closes[-1] = last_close
    opens[-1] = last_close

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


class TestConsolidationBreakoutStrategy:

    def setup_method(self):
        self.strategy = ConsolidationBreakoutStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "consolidation_breakout"

    # 2. 데이터 부족 (< 15행) → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "데이터 부족" in sig.reasoning

    # 3. 정확히 15행 경계 처리 → Signal 반환
    def test_exactly_min_rows(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. HOLD: consolidation 있지만 돌파 없음
    def test_hold_no_breakout(self):
        # narrow range (1%), close = base (돌파 없음)
        df = _make_df(n=_N, consol_range_pct=0.01, last_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. HOLD: consolidation 없음 (range > 3%)
    def test_hold_no_consolidation(self):
        # wide range (5%) → not consolidation
        df = _make_df(n=_N, consol_range_pct=0.05, last_close=102.6)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. BUY: consolidation + close > consol_high * 1.001
    def test_buy_breakout_above(self):
        base = 100.0
        consol_range_pct = 0.01  # high=100.5, low=99.5
        consol_high = base * (1 + consol_range_pct / 2)  # 100.5
        last_close = consol_high * 1.002  # 100.5 * 1.002 > 100.5 * 1.001
        df = _make_df(n=_N, consol_range_pct=consol_range_pct, last_close=last_close)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "consolidation_breakout"
        assert sig.entry_price > 0

    # 7. BUY confidence HIGH: volume > avg * 2.0
    def test_buy_high_confidence_volume(self):
        base = 100.0
        consol_range_pct = 0.01
        consol_high = base * (1 + consol_range_pct / 2)
        last_close = consol_high * 1.002
        df = _make_df(
            n=_N,
            consol_range_pct=consol_range_pct,
            last_close=last_close,
            last_volume=2500.0,  # > avg(500) * 2.0 = 1000
            avg_volume=500.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 8. BUY confidence MEDIUM: volume <= avg * 2.0
    def test_buy_medium_confidence_volume(self):
        base = 100.0
        consol_range_pct = 0.01
        consol_high = base * (1 + consol_range_pct / 2)
        last_close = consol_high * 1.002
        df = _make_df(
            n=_N,
            consol_range_pct=consol_range_pct,
            last_close=last_close,
            last_volume=800.0,   # <= avg(500) * 2.0 = 1000
            avg_volume=500.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 9. SELL: consolidation + close < consol_low * 0.999
    def test_sell_breakout_below(self):
        base = 100.0
        consol_range_pct = 0.01  # low=99.5
        consol_low = base * (1 - consol_range_pct / 2)
        last_close = consol_low * 0.998  # 99.5 * 0.998 < 99.5 * 0.999
        df = _make_df(n=_N, consol_range_pct=consol_range_pct, last_close=last_close)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "consolidation_breakout"

    # 10. SELL confidence HIGH: volume > avg * 2.0
    def test_sell_high_confidence_volume(self):
        base = 100.0
        consol_range_pct = 0.01
        consol_low = base * (1 - consol_range_pct / 2)
        last_close = consol_low * 0.998
        df = _make_df(
            n=_N,
            consol_range_pct=consol_range_pct,
            last_close=last_close,
            last_volume=2000.0,
            avg_volume=500.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_N)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 12. BUY 신호 시 invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        base = 100.0
        consol_range_pct = 0.01
        consol_high = base * (1 + consol_range_pct / 2)
        last_close = consol_high * 1.002
        df = _make_df(n=_N, consol_range_pct=consol_range_pct, last_close=last_close)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.invalidation != ""

    # 13. SELL 신호 시 invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        base = 100.0
        consol_range_pct = 0.01
        consol_low = base * (1 - consol_range_pct / 2)
        last_close = consol_low * 0.998
        df = _make_df(n=_N, consol_range_pct=consol_range_pct, last_close=last_close)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.invalidation != ""

    # 14. entry_price 양수 (충분한 데이터)
    def test_entry_price_positive(self):
        df = _make_df(n=_N)
        sig = self.strategy.generate(df)
        assert sig.entry_price >= 0

    # 15. 큰 데이터셋 안정성
    def test_large_dataset(self):
        df = _make_df(n=200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
