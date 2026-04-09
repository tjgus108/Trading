"""
RangeExpansionStrategy 단위 테스트.

DataFrame 구조:
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
  - 앞쪽 봉들: avg_tr_20 계산에 사용

TR = max(high-low, |high-prev_close|, |low-prev_close|)
avg_tr_20 = TR.rolling(20).mean()
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.range_expansion import RangeExpansionStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 30,
    base_tr: float = 1.0,
    signal_tr_multiplier: float = 1.0,
    signal_bull: bool = True,
) -> pd.DataFrame:
    """
    제어 가능한 DataFrame 생성.
    - 앞 n-2 봉: TR ≈ base_tr (avg_tr_20 기준 설정)
    - 인덱스 -2 (신호 봉): TR = base_tr * signal_tr_multiplier
    - signal_bull=True → close > open (양봉), False → close < open (음봉)
    """
    closes = [100.0 + i * 0.01 for i in range(n)]
    # base TR ≈ base_tr: high-low = base_tr
    highs = [c + base_tr / 2 for c in closes]
    lows  = [c - base_tr / 2 for c in closes]
    opens = [c for c in closes]

    df = pd.DataFrame({
        "open":   opens,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })

    # 신호 봉 (-2) 설정
    signal_idx = n - 2
    signal_close = 100.0
    signal_tr = base_tr * signal_tr_multiplier

    if signal_bull:
        signal_open = signal_close - 0.3
    else:
        signal_open = signal_close + 0.3

    # high-low = signal_tr
    signal_high = signal_close + signal_tr / 2
    signal_low  = signal_close - signal_tr / 2

    df.loc[signal_idx, "open"]  = signal_open
    df.loc[signal_idx, "close"] = signal_close
    df.loc[signal_idx, "high"]  = signal_high
    df.loc[signal_idx, "low"]   = signal_low

    # current 봉 (-1): 무시됨
    df.loc[n - 1, "open"]  = signal_close
    df.loc[n - 1, "close"] = signal_close
    df.loc[n - 1, "high"]  = signal_close + 0.5
    df.loc[n - 1, "low"]   = signal_close - 0.5

    return df


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestRangeExpansionStrategy:

    def setup_method(self):
        self.strategy = RangeExpansionStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "range_expansion"

    # 2. 데이터 부족 (24행) → HOLD
    def test_insufficient_data_24_rows(self):
        df = _make_df(n=24)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 데이터 부족 경계 - 25행 → 처리됨
    def test_exactly_25_rows_processes(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. BUY 신호: TR > avg*1.5 + 양봉
    def test_buy_signal_expanded_range_bull(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.8, signal_bull=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "range_expansion"

    # 5. BUY HIGH confidence: TR > avg*2.0
    def test_buy_high_confidence_tr_over_2x(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=2.2, signal_bull=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 6. BUY MEDIUM confidence: 1.5 < TR/avg < 2.0
    def test_buy_medium_confidence_tr_1_5_to_2x(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.7, signal_bull=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 7. SELL 신호: TR > avg*1.5 + 음봉
    def test_sell_signal_expanded_range_bear(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.8, signal_bull=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "range_expansion"

    # 8. SELL HIGH confidence: TR > avg*2.0
    def test_sell_high_confidence_tr_over_2x(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=2.2, signal_bull=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 9. SELL MEDIUM confidence: 1.5 < TR/avg < 2.0
    def test_sell_medium_confidence_tr_1_5_to_2x(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.7, signal_bull=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 10. TR < avg*1.5 → HOLD (양봉)
    def test_hold_tr_below_threshold_bull(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.2, signal_bull=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. TR < avg*1.5 → HOLD (음봉)
    def test_hold_tr_below_threshold_bear(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.2, signal_bull=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 13. BUY entry_price = signal_close
    def test_buy_entry_price_correct(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=2.0, signal_bull=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == pytest.approx(100.0, abs=0.01)

    # 14. SELL entry_price = signal_close
    def test_sell_entry_price_correct(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=2.0, signal_bull=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == pytest.approx(100.0, abs=0.01)

    # 15. BUY reasoning에 "양봉" 또는 "TR" 포함
    def test_buy_reasoning_mentions_tr_or_bull(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.8, signal_bull=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "TR" in sig.reasoning or "양봉" in sig.reasoning

    # 16. SELL reasoning에 "음봉" 또는 "TR" 포함
    def test_sell_reasoning_mentions_tr_or_bear(self):
        df = _make_df(n=30, base_tr=1.0, signal_tr_multiplier=1.8, signal_bull=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "TR" in sig.reasoning or "음봉" in sig.reasoning
