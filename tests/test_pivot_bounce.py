"""
PivotBounceStrategy 단위 테스트.

DataFrame 구조 (n=35 기본):
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
  - prev_high = high.iloc[-26:-20].max()
  - prev_low  = low.iloc[-26:-20].min()
  - prev_close = close.iloc[-21]  (iloc[-21]은 iloc[-26:-20] 범위 내)
"""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.pivot_bounce import PivotBounceStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, base: float = 100.0) -> pd.DataFrame:
    """균일한 기본 DataFrame."""
    data = {
        "open":   [base] * n,
        "close":  [base] * n,
        "high":   [base + 1.0] * n,
        "low":    [base - 1.0] * n,
        "volume": [1000.0] * n,
    }
    return pd.DataFrame(data)


def _pivots_from_df(df: pd.DataFrame):
    """전략이 실제로 사용하는 prev_high/low/close 로 피봇 계산."""
    prev_high = float(df["high"].iloc[-26:-20].max())
    prev_low = float(df["low"].iloc[-26:-20].min())
    prev_close = float(df["close"].iloc[-21])
    p = (prev_high + prev_low + prev_close) / 3.0
    r1 = 2.0 * p - prev_low
    r2 = p + (prev_high - prev_low)
    s1 = 2.0 * p - prev_high
    s2 = p - (prev_high - prev_low)
    return p, r1, r2, s1, s2, prev_close


def _setup_pivot_range(df: pd.DataFrame, prev_high: float, prev_low: float) -> pd.DataFrame:
    """iloc[-26:-20] 구간에 prev_high/low 설정. iloc[-21].close는 변경 안 함."""
    df = df.copy()
    df.iloc[-26:-20, df.columns.get_loc("high")] = prev_high
    df.iloc[-26:-20, df.columns.get_loc("low")] = prev_low
    return df


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestPivotBounceStrategy:

    def setup_method(self):
        self.strat = PivotBounceStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "pivot_bounce"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_df(n=25)  # < 30 but >= 26 so iloc[-26] accessible
        # 25행짜리: iloc[-26] = -1 이므로 전략 내 _MIN_ROWS 체크 먼저 걸림
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 경계값: 29행 → HOLD
    def test_29_rows_returns_hold(self):
        df = _make_df(n=29)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. 경계값: 30행 → 처리됨
    def test_30_rows_processes(self):
        df = _make_df(n=30)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. S1 근방 + close > prev_close → BUY (MEDIUM)
    def test_buy_near_s1_medium_confidence(self):
        # S1 > prev_close 조건: prev_close < 2*prev_low - prev_high
        # prev_high=105, prev_low=95: pc < 2*95-105 = 85 → pc=70 사용
        # p = (105+95+70)/3 = 90, s1 = 2*90-105 = 75
        # close_val = 75*1.001 = 75.075 > 70 ✓, near_s1=True, near_s2=False → MEDIUM
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        df.iloc[-21, df.columns.get_loc("close")] = 70.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = s1 * 1.001
        assert close_val > prev_close, f"close_val={close_val} must be > prev_close={prev_close}"
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM
        assert sig.strategy == "pivot_bounce"

    # 6. S2 근방 + close > prev_close → BUY (HIGH)
    def test_buy_near_s2_high_confidence(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        # prev_close (iloc[-21]) 낮게 설정 → s2보다 낮아야 close > prev_close
        # s2 = P - (prev_high - prev_low) = 100 - 10 = 90 (default prev_close=100)
        # close_val ≈ 90 → prev_close는 더 낮아야 함
        # prev_close를 85로 설정 → s2 재계산
        df.iloc[-21, df.columns.get_loc("close")] = 85.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        # s2 = (105+95+85)/3 - 10 = 95 - 10 = 85
        close_val = s2 * 1.001  # ≈ 85.085 > 85 ✓
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. S1 근방이지만 close < prev_close → HOLD (반등 없음)
    def test_no_buy_when_close_below_prev_close(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        # prev_close를 110으로 높게
        df.iloc[-21, df.columns.get_loc("close")] = 110.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        # close ≈ s1, but close < prev_close(110) → HOLD
        close_val = s1 * 1.001
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 8. R1 근방 + close < prev_close → SELL (MEDIUM)
    def test_sell_near_r1_medium_confidence(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        # prev_close를 높게 → close < prev_close ✓
        df.iloc[-21, df.columns.get_loc("close")] = 120.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = r1 * 0.999  # r1 -0.1%
        # close < prev_close(120)이어야 함
        assert close_val < prev_close, f"close_val={close_val} must be < prev_close={prev_close}"
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 9. R2 근방 + close < prev_close → SELL (HIGH)
    def test_sell_near_r2_high_confidence(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        df.iloc[-21, df.columns.get_loc("close")] = 130.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = r2 * 0.999
        assert close_val < prev_close, f"close_val={close_val} must be < prev_close={prev_close}"
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 10. R1 근방이지만 close > prev_close → HOLD (반전 없음)
    def test_no_sell_when_close_above_prev_close(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        # prev_close 낮게
        df.iloc[-21, df.columns.get_loc("close")] = 80.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = r1 * 0.999
        # close > prev_close(80) → HOLD (반전 조건 미충족)
        assert close_val > prev_close
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 11. 피봇 레벨에서 멀리 있을 때 → HOLD
    def test_hold_when_far_from_all_levels(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        # close를 P 근방(pivot point 자체)으로 → S/R 레벨 아님
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        df.iloc[-2, df.columns.get_loc("close")] = p  # 정확히 P에 위치
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 13. BUY reasoning에 지지 레벨 언급
    def test_buy_reasoning_mentions_support_level(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        df.iloc[-21, df.columns.get_loc("close")] = 85.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = s2 * 1.001
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY
        assert "S1" in sig.reasoning or "S2" in sig.reasoning

    # 14. SELL reasoning에 저항 레벨 언급
    def test_sell_reasoning_mentions_resistance_level(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        df.iloc[-21, df.columns.get_loc("close")] = 130.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = r2 * 0.999
        assert close_val < prev_close
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL
        assert "R1" in sig.reasoning or "R2" in sig.reasoning

    # 15. entry_price는 마지막 완성봉의 close와 일치
    def test_entry_price_equals_last_close(self):
        df = _make_df(n=35, base=100.0)
        df = _setup_pivot_range(df, prev_high=105.0, prev_low=95.0)
        df.iloc[-21, df.columns.get_loc("close")] = 85.0
        p, r1, r2, s1, s2, prev_close = _pivots_from_df(df)
        close_val = s2 * 1.001
        df.iloc[-2, df.columns.get_loc("close")] = close_val
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == pytest.approx(close_val, abs=1e-6)
