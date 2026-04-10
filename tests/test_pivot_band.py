"""
PivotBandStrategy 단위 테스트 (14개 이상).

DataFrame 구조:
  - idx = len(df) - 2: 신호 봉 (curr)
  - idx - 1: 이전 봉 (prev) → Pivot 계산 및 prev_close
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.pivot_band import PivotBandStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _pivot_bands(prev_high, prev_low, prev_close):
    """band_upper, band_lower, r1, s1, r2, s2 계산."""
    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = 2 * pivot - prev_low
    s1 = 2 * pivot - prev_high
    r2 = pivot + (prev_high - prev_low)
    s2 = pivot - (prev_high - prev_low)
    band_upper = (r1 + r2) / 2
    band_lower = (s1 + s2) / 2
    return band_upper, band_lower, r1, s1, r2, s2


def _make_df(
    n: int = 20,
    pivot_high: float = 110.0,
    pivot_low: float = 90.0,
    pivot_close: float = 100.0,
    prev_close: float = 100.0,
    curr_close: float = 100.0,
) -> pd.DataFrame:
    """
    PivotBandStrategy:
      idx = len(df) - 2  → 신호 봉 (curr)
      prev = df.iloc[idx - 1]  → pivot OHLC 및 prev_close

    So:
      iloc[-3] is NOT used by strategy (idx-1 = len-3, that IS prev)
      Wait: idx = len-2, prev = iloc[idx-1] = iloc[len-3]

    Actually: idx = len(df)-2, prev = df.iloc[idx-1] = df.iloc[len-3]
    And curr = df.iloc[idx] = df.iloc[len-2]

    So iloc[-3] = prev (for pivot and prev_close)
    iloc[-2] = curr (signal)
    iloc[-1] = current candle (ignored)
    """
    closes = [100.0] * n
    highs  = [101.0] * n
    lows   = [99.0]  * n

    # prev 봉 (idx-1 = iloc[-3]): pivot 계산 + prev_close
    closes[-3] = prev_close
    highs[-3]  = pivot_high
    lows[-3]   = pivot_low

    # curr 봉 (idx = iloc[-2]): 신호
    closes[-2] = curr_close
    highs[-2]  = curr_close + 0.5
    lows[-2]   = curr_close - 0.5

    # 진행 중 봉 (iloc[-1])
    closes[-1] = curr_close
    highs[-1]  = curr_close + 1.0
    lows[-1]   = curr_close - 1.0

    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n=20):
    """BUY: prev_close < band_lower, curr_close >= band_lower.

    Strategy에서 prev = df.iloc[idx-1] 행으로 pivot과 prev_close를 함께 계산.
    따라서 prev_close IS pivot_close.

    두 봉(prev, signal)으로 크로스오버를 만들려면:
    - prev 봉: high/low/close를 선택해서 band_lower를 특정 값으로 만들고,
               close < band_lower가 되도록 설계

    실용적 접근: prev 봉의 close를 의도적으로 낮게 설정하면
    band_lower도 낮아진다. 대신 두 봉 사이 gap을 이용:
    - 이전 봉(iloc[-4])이 band_lower 아래, 현재 봉(iloc[-3])도 아래,
      신호 봉(iloc[-2])이 band_lower 이상.
    → 즉 df.iloc[idx-1]["close"]가 band_lower 아래이고,
       df.iloc[idx]["close"]가 band_lower 이상.

    하지만 pivot은 df.iloc[idx-1] 기준. 해결: band_lower가 close 아래에 오도록.
    pivot = (H + L + C)/3, band_lower = (s1+s2)/2 = (2P-H + P-(H-L))/2
          = (3P - H - (H-L))/2 = (3P - 2H + L)/2
    H=110, L=90, C=85 (close가 낮으면):
      P = (110+90+85)/3 = 95
      s1 = 2*95-110 = 80, s2 = 95-(20) = 75
      band_lower = (80+75)/2 = 77.5
    prev_close = 85 > band_lower = 77.5  → 조건 불만족

    다른 접근: prev 봉의 close를 band_lower보다 낮게 만들기
    band_lower = (s1+s2)/2, s1 = 2P - H, s2 = P - (H-L)
    H=110, L=90, C=?:
      P = (110+90+C)/3
      s1 = 2*(200+C)/3 - 110 = (400+2C-330)/3 = (70+2C)/3
      s2 = (200+C)/3 - 20 = (200+C-60)/3 = (140+C)/3
      band_lower = ((70+2C)+(140+C))/(3*2) = (210+3C)/6 = (70+C)/2
    For close < band_lower: C < (70+C)/2 → 2C < 70+C → C < 70
    So with C=60: band_lower = (70+60)/2 = 65 > 60 ✓
    """
    ph, pl, pc = 110.0, 90.0, 60.0  # close=60 < band_lower=65
    band_upper, band_lower, r1, s1, r2, s2 = _pivot_bands(ph, pl, pc)
    # prev_close = pc = 60 < band_lower = 65 → BUY 조건 1 충족
    # curr_close >= band_lower
    signal_curr_close = band_lower + 0.5
    return _make_df(n=n, pivot_high=ph, pivot_low=pl, pivot_close=pc,
                    prev_close=pc,
                    curr_close=signal_curr_close), band_lower, ph, pl, pc


def _make_sell_df(n=20):
    """SELL: prev_close > band_upper, curr_close <= band_upper.
    band_upper = (r1+r2)/2 = (2P-L + P+(H-L))/2 = (3P - L + H - L)/2 = (3P+H-2L)/2
    H=110, L=90, C=?:
      P = (110+90+C)/3
      r1 = 2*(200+C)/3 - 90 = (400+2C-270)/3 = (130+2C)/3
      r2 = (200+C)/3 + 20 = (200+C+60)/3 = (260+C)/3
      band_upper = ((130+2C)+(260+C))/(3*2) = (390+3C)/6 = (130+C)/2
    For close > band_upper: C > (130+C)/2 → 2C > 130+C → C > 130
    So with C=140: band_upper = (130+140)/2 = 135 < 140 ✓
    """
    ph, pl, pc = 110.0, 90.0, 140.0  # close=140 > band_upper=135
    band_upper, band_lower, r1, s1, r2, s2 = _pivot_bands(ph, pl, pc)
    signal_curr_close = band_upper - 0.5
    return _make_df(n=n, pivot_high=ph, pivot_low=pl, pivot_close=pc,
                    prev_close=pc,
                    curr_close=signal_curr_close), band_upper, ph, pl, pc


# ── tests ────────────────────────────────────────────────────────────────────

class TestPivotBandStrategy:

    def setup_method(self):
        self.strategy = PivotBandStrategy()

    # 1. 전략명
    def test_strategy_name(self):
        assert self.strategy.name == "pivot_band"

    # 2. 인스턴스 타입
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=3)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음 (항상 Signal 반환)
    def test_no_none_return(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 필드 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. BUY 신호 (하단 밴드 복귀)
    def test_buy_signal(self):
        df, band_lower, *_ = _make_buy_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 7. SELL 신호 (상단 밴드 이탈)
    def test_sell_signal(self):
        df, band_upper, *_ = _make_sell_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 8. Signal 필드 완전성
    def test_signal_fields(self):
        df, *_ = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")

    # 9. BUY reasoning에 "PivotBand" 또는 "band" 포함
    def test_buy_reasoning_mentions_band(self):
        df, *_ = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "band" in sig.reasoning.lower() or "pivot" in sig.reasoning.lower()

    # 10. SELL reasoning에 "PivotBand" 또는 "band" 포함
    def test_sell_reasoning_mentions_band(self):
        df, *_ = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "band" in sig.reasoning.lower() or "pivot" in sig.reasoning.lower()

    # 11. HIGH confidence via BUY (curr > r2): use _make_sell_df and check
    def test_high_or_medium_confidence_sell(self):
        # SELL scenario: signal
        df, band_upper, *_ = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. BUY confidence is HIGH or MEDIUM depending on position
    def test_buy_confidence_value(self):
        # Confidence HIGH if curr < s2 or curr > r2, else MEDIUM
        # _make_buy_df: pc=60, band_lower=65, curr=65.5
        # With H=110,L=90,C=60: s2 = (200+60)/3 - 20 = 66.67
        # curr=65.5 < s2=66.67 → HIGH
        df, *_ = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 13. entry_price > 0
    def test_entry_price_positive(self):
        df, *_ = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 14. strategy 필드 = "pivot_band"
    def test_strategy_field(self):
        df, *_ = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "pivot_band"

    # 15. 최소 행: 5행
    def test_min_rows_boundary(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        # 5행이면 통과 (HOLD or signal)
        assert isinstance(sig, Signal)

    # 16. HOLD: prev_close 이미 band_lower 위 (no crossover)
    def test_hold_when_no_crossover(self):
        # Use default _make_df: prev_close=100, curr_close=100
        # band_lower for H=101,L=99,C=100: pivot=100, s1=99, s2=98, band_lower=98.5
        # prev_close=100 > band_lower=98.5 → no BUY crossover
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
