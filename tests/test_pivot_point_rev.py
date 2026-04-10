"""
PivotPointRevStrategy 단위 테스트 (mock DataFrame, API 호출 없음).

구조:
  - idx     = len(df) - 2 : 신호 봉 (curr_close)
  - idx - 1               : 이전봉 → Pivot 계산
  - idx + 1 (= -1)        : 진행 중 캔들 (무시)

Pivot 계산:
  pivot = (prev_high + prev_low + prev_close) / 3
  r1    = 2 * pivot - prev_low
  s1    = 2 * pivot - prev_high
  r2    = pivot + (prev_high - prev_low)
  s2    = pivot - (prev_high - prev_low)
"""

import pandas as pd
import pytest

from src.strategy.pivot_point_rev import PivotPointRevStrategy
from src.strategy.base import Action, Confidence, Signal


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _pivot_levels(prev_high, prev_low, prev_close):
    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = 2 * pivot - prev_low
    s1 = 2 * pivot - prev_high
    r2 = pivot + (prev_high - prev_low)
    s2 = pivot - (prev_high - prev_low)
    return pivot, r1, s1, r2, s2


def _make_df(
    n: int = 30,
    prev_high: float = 110.0,
    prev_low: float = 90.0,
    prev_close: float = 100.0,
    signal_close: float = 100.0,
) -> pd.DataFrame:
    """
    제어 가능한 DataFrame 생성.
      - [-3] (idx-1): prev 봉 → Pivot 계산에 사용
      - [-2] (idx):   signal 봉 → curr_close
      - [-1]:         진행 중 캔들
    """
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0]  * n
    opens  = [100.0] * n

    # prev 봉
    closes[-3] = prev_close
    highs[-3]  = prev_high
    lows[-3]   = prev_low
    opens[-3]  = prev_close

    # signal 봉
    closes[-2] = signal_close
    highs[-2]  = signal_close + 0.01
    lows[-2]   = signal_close - 0.01
    opens[-2]  = signal_close

    # current (진행 중)
    closes[-1] = signal_close
    highs[-1]  = signal_close + 0.5
    lows[-1]   = signal_close - 0.5
    opens[-1]  = signal_close

    return pd.DataFrame({
        "open":   opens,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestPivotPointRevStrategy:

    def setup_method(self):
        self.strategy = PivotPointRevStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "pivot_point_rev"

    # 2. 인스턴스 생성
    def test_instance_creation(self):
        s = PivotPointRevStrategy()
        assert s is not None

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert sig.reasoning != ""

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        # S1 근처: curr_close = s1 * 0.999 (s1 * 0.998 ~ s1 사이)
        signal_close = s1 * 0.999
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            lower = sig.reasoning.lower()
            assert "pivotrev" in lower or "s1" in lower or "s2" in lower

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        # R1 근처: curr_close = r1 * 1.001 (r1 ~ r1 * 1.002 사이)
        signal_close = r1 * 1.001
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            lower = sig.reasoning.lower()
            assert "pivotrev" in lower or "r1" in lower or "r2" in lower

    # 10. HIGH confidence 테스트 (S2 근처)
    def test_high_confidence_near_s2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, _, _, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        # S2 근처: s2 * 0.999 (s2 * 0.998 ~ s2 사이)
        signal_close = s2 * 0.999
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence 테스트 (S1 근처)
    def test_medium_confidence_near_s1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        # S1 근처이지만 S2 범위 밖
        signal_close = s1 * 0.999
        # S2 범위 아닌지 확인
        assert not (signal_close < s2 and signal_close > s2 * 0.998)
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = s1 * 0.999
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "pivot_point_rev"

    # 14. 최소 행 수(20)에서 동작
    def test_minimum_rows_works(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = s1 * 0.999
        df = _make_df(
            n=20, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. BUY near S1 signal
    def test_buy_near_s1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = s1 * 0.999
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 16. SELL near R1 signal
    def test_sell_near_r1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = r1 * 1.001
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 17. HOLD when price is far from all levels
    def test_hold_far_from_levels(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        pivot, _, _, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        # pivot 근처는 어떤 레벨과도 멀다
        signal_close = pivot
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 18. HIGH confidence near R2
    def test_high_confidence_near_r2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, _, r2, _ = _pivot_levels(prev_high, prev_low, prev_close)
        # R2 근처: r2 * 1.001 (r2 ~ r2 * 1.002 사이)
        signal_close = r2 * 1.001
        df = _make_df(
            n=30, prev_high=prev_high, prev_low=prev_low,
            prev_close=prev_close, signal_close=signal_close
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH
