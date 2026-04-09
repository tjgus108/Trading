"""
PivotReversalStrategy 단위 테스트.

DataFrame 구조 (n=30 기본):
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
  - 앞쪽 봉들: Pivot 탐지에 사용

Pivot High/Low 판별 조건:
  - 앞뒤 2봉보다 high(또는 low)가 높(낮)아야 함
"""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.pivot_reversal import PivotReversalStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _flat_df(n: int = 30, close: float = 100.0) -> pd.DataFrame:
    """모든 봉이 동일한 기본 DataFrame."""
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _insert_pivot_low(df: pd.DataFrame, idx: int, low_val: float) -> pd.DataFrame:
    """idx 위치에 Pivot Low를 삽입 (앞뒤 2봉보다 low가 낮게)."""
    df = df.copy()
    # 앞뒤 2봉의 low를 pivot_low + 2 로 설정
    for offset in [-2, -1, 1, 2]:
        target = idx + offset
        if 0 <= target < len(df):
            df.loc[target, "low"] = low_val + 2.0
            df.loc[target, "high"] = low_val + 3.0
    df.loc[idx, "low"] = low_val
    df.loc[idx, "high"] = low_val + 1.0
    df.loc[idx, "close"] = low_val + 0.5
    df.loc[idx, "open"] = low_val + 0.5
    return df


def _insert_pivot_high(df: pd.DataFrame, idx: int, high_val: float) -> pd.DataFrame:
    """idx 위치에 Pivot High를 삽입 (앞뒤 2봉보다 high가 높게)."""
    df = df.copy()
    for offset in [-2, -1, 1, 2]:
        target = idx + offset
        if 0 <= target < len(df):
            df.loc[target, "high"] = high_val - 2.0
            df.loc[target, "low"] = high_val - 3.0
    df.loc[idx, "high"] = high_val
    df.loc[idx, "low"] = high_val - 1.0
    df.loc[idx, "close"] = high_val - 0.5
    df.loc[idx, "open"] = high_val - 0.5
    return df


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestPivotReversalStrategy:

    def setup_method(self):
        self.strategy = PivotReversalStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "pivot_reversal"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _flat_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 최소 데이터(15행) 경계 - 14행 → HOLD
    def test_exactly_14_rows_returns_hold(self):
        df = _flat_df(n=14)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. 최소 데이터(15행) 경계 - 15행 → 처리됨
    def test_exactly_15_rows_processes(self):
        df = _flat_df(n=15)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 5. Pivot Low 반등 → BUY 신호
    def test_buy_signal_on_pivot_low_bounce(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2  # _last(df) = iloc[-2]
        # Pivot Low를 last_idx - 3 위치에 삽입 (앞뒤 2봉 필요, 충분한 거리)
        pivot_idx = last_idx - 3
        pivot_low = 90.0
        df = _insert_pivot_low(df, pivot_idx, pivot_low)
        # 신호 봉: close > pivot_low * 1.005
        signal_close = pivot_low * 1.01  # 1% 반등
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close - 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "pivot_reversal"
        assert sig.entry_price == pytest.approx(signal_close, abs=0.01)

    # 6. BUY HIGH confidence (반등폭 > 1%)
    def test_buy_high_confidence_bounce_over_1pct(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_low = 90.0
        df = _insert_pivot_low(df, pivot_idx, pivot_low)
        signal_close = pivot_low * 1.015  # 1.5% 반등 → HIGH
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close - 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. BUY MEDIUM confidence (반등폭 0.5~1%)
    def test_buy_medium_confidence_small_bounce(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_low = 90.0
        df = _insert_pivot_low(df, pivot_idx, pivot_low)
        # close > pivot_low * 1.005 이지만 bounce_ratio < 1%
        signal_close = pivot_low * 1.007  # 0.7% 반등 → MEDIUM
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close - 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 8. Pivot High 반락 → SELL 신호
    def test_sell_signal_on_pivot_high_drop(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_high = 110.0
        df = _insert_pivot_high(df, pivot_idx, pivot_high)
        signal_close = pivot_high * 0.989  # 1.1% 반락
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close + 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "pivot_reversal"
        assert sig.entry_price == pytest.approx(signal_close, abs=0.01)

    # 9. SELL HIGH confidence (반락폭 > 1%)
    def test_sell_high_confidence_drop_over_1pct(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_high = 110.0
        df = _insert_pivot_high(df, pivot_idx, pivot_high)
        signal_close = pivot_high * 0.985  # 1.5% 반락 → HIGH
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close + 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 10. SELL MEDIUM confidence (반락폭 0.5~1%)
    def test_sell_medium_confidence_small_drop(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_high = 110.0
        df = _insert_pivot_high(df, pivot_idx, pivot_high)
        signal_close = pivot_high * 0.993  # 0.7% 반락 → MEDIUM
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close + 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 11. Pivot Low 있지만 반등 0.3% 미만 → HOLD
    def test_hold_when_bounce_insufficient(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_low = 90.0
        df = _insert_pivot_low(df, pivot_idx, pivot_low)
        signal_close = pivot_low * 1.002  # 0.2% 반등 → close < pivot_low*1.005 → HOLD
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close - 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. Pivot High 있지만 반락 0.3% 미만 → HOLD
    def test_hold_when_drop_insufficient(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_high = 110.0
        df = _insert_pivot_high(df, pivot_idx, pivot_high)
        signal_close = pivot_high * 0.998  # 0.2% 반락 → close > pivot_high*0.995 → HOLD
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close + 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 13. Signal 필드 완전성 확인
    def test_signal_fields_complete(self):
        df = _flat_df(n=30)
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

    # 14. BUY reasoning에 "Pivot Low" 포함
    def test_buy_reasoning_mentions_pivot_low(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_low = 90.0
        df = _insert_pivot_low(df, pivot_idx, pivot_low)
        signal_close = pivot_low * 1.01
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close - 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "Pivot Low" in sig.reasoning

    # 15. SELL reasoning에 "Pivot High" 포함
    def test_sell_reasoning_mentions_pivot_high(self):
        n = 30
        df = _flat_df(n=n, close=100.0)
        last_idx = n - 2
        pivot_idx = last_idx - 3
        pivot_high = 110.0
        df = _insert_pivot_high(df, pivot_idx, pivot_high)
        signal_close = pivot_high * 0.989
        df.loc[last_idx, "close"] = signal_close
        df.loc[last_idx, "open"] = signal_close + 0.1
        df.loc[last_idx, "high"] = signal_close + 1.0
        df.loc[last_idx, "low"] = signal_close - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "Pivot High" in sig.reasoning

    # 16. Pivot 없을 때 HOLD
    def test_hold_no_pivot(self):
        df = _flat_df(n=30, close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
