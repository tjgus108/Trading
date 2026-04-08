"""
PivotPointsStrategy 단위 테스트 (mock DataFrame, API 호출 없음).

DataFrame 구조:
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (= idx): 신호 봉 (last)
  - 인덱스 -3 (= idx-1): 이전 봉 (prev) → Pivot 계산에 사용

Pivot 계산 (prev 봉 기준):
  P  = (prev_high + prev_low + prev_close) / 3
  R1 = 2*P - prev_low
  S1 = 2*P - prev_high
  R2 = P + (prev_high - prev_low)
  S2 = P - (prev_high - prev_low)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.pivot_points import PivotPointsStrategy
from src.strategy.base import Action, Confidence, Signal


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 30,
    prev_high: float = 110.0,
    prev_low: float = 90.0,
    prev_close: float = 100.0,
    signal_close: float = 100.0,
    rsi_override: float = None,
) -> pd.DataFrame:
    """
    제어 가능한 Pivot 테스트용 DataFrame 생성.

    - 인덱스 [-3] (prev):  Pivot 계산에 사용 (prev_high/low/close)
    - 인덱스 [-2] (signal): 신호 봉 (signal_close)
    - 인덱스 [-1] (current): 진행 중

    rsi_override < 40  → RSI 낮게: signal_close 기준으로 전체 하락 시리즈
    rsi_override > 60  → RSI 높게: signal_close 기준으로 전체 상승 시리즈
    None               → 중립
    """
    base_close = 100.0
    closes = [base_close] * n
    highs  = [base_close + 1] * n
    lows   = [base_close - 1] * n

    if rsi_override is not None:
        if rsi_override < 40:
            # signal_close에서 끝나는 강한 하락 시리즈
            # 앞 n-2 봉 = signal_close + (n-2-i) * step (하락)
            step = 1.5
            for i in range(n - 2):
                v = signal_close + (n - 2 - i) * step
                closes[i] = v
                highs[i]  = v + 0.5
                lows[i]   = v - 0.5
        else:
            # signal_close에서 끝나는 강한 상승 시리즈
            step = 1.5
            for i in range(n - 2):
                v = signal_close - (n - 2 - i) * step
                closes[i] = v
                highs[i]  = v + 0.5
                lows[i]   = v - 0.5

    # prev 봉 (-3): Pivot 계산에 사용
    closes[-3] = prev_close
    highs[-3]  = prev_high
    lows[-3]   = prev_low

    # signal 봉 (-2): 신호 봉
    closes[-2] = signal_close
    highs[-2]  = signal_close + 0.5
    lows[-2]   = signal_close - 0.5

    # current 봉 (-1): 진행 중
    closes[-1] = signal_close
    highs[-1]  = signal_close + 1
    lows[-1]   = signal_close - 1

    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })


def _pivot_levels(prev_high, prev_low, prev_close):
    """Pivot S1/R1/S2/R2 계산 헬퍼."""
    p  = (prev_high + prev_low + prev_close) / 3
    r1 = 2 * p - prev_low
    s1 = 2 * p - prev_high
    r2 = p + (prev_high - prev_low)
    s2 = p - (prev_high - prev_low)
    return p, r1, s1, r2, s2


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestPivotPointsStrategy:

    def setup_method(self):
        self.strategy = PivotPointsStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "pivot_points"

    # 2. BUY 신호 (close < S1, RSI < 40)
    def test_buy_signal(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        # signal_close = S1 - 2 (확실히 이탈)
        signal_close = s1 - 2.0
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=25.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "pivot_points"
        assert sig.entry_price == pytest.approx(signal_close, abs=0.01)

    # 3. SELL 신호 (close > R1, RSI > 60)
    def test_sell_signal(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = r1 + 2.0
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=75.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "pivot_points"
        assert sig.entry_price == pytest.approx(signal_close, abs=0.01)

    # 4. BUY HIGH confidence (S2 근처: |close - S2| / S2 < 0.005)
    def test_buy_high_confidence_near_s2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        # S2 에 딱 붙이기
        signal_close = s2 * 1.001  # 0.1% 위 (0.5% 이내)
        # S2 < S1 이어야 BUY 조건(close < S1) 성립
        assert signal_close < s1, "S2가 S1보다 낮아야 함"
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=25.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. BUY MEDIUM confidence (S1 근처, S2 아님)
    def test_buy_medium_confidence_near_s1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, s2 = _pivot_levels(prev_high, prev_low, prev_close)
        # S1 바로 아래지만 S2와는 멀리
        signal_close = s1 - 1.0
        # S2와 거리 확인 (1% 이상)
        assert abs(signal_close - s2) / abs(s2) >= 0.005
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=25.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 6. SELL HIGH confidence (R2 근처)
    def test_sell_high_confidence_near_r2(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, r2, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = r2 * 1.001  # R2 0.1% 위
        assert signal_close > r1
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=75.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. SELL MEDIUM confidence (R1 근처, R2 아님)
    def test_sell_medium_confidence_near_r1(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, r2, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = r1 + 1.0
        assert abs(signal_close - r2) / abs(r2) >= 0.005
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=75.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 8. close < S1이지만 RSI > 40 → HOLD
    def test_hold_buy_condition_but_rsi_too_high(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = s1 - 2.0
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=75.0,  # RSI 높음 → BUY 조건 불충족
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=3)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 10. Signal 필드 완전성
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
        assert sig.reasoning != ""

    # 11. BUY reasoning에 "Pivot" 또는 "support" 포함 (대소문자 무관)
    def test_buy_reasoning_mentions_pivot_or_support(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, _, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = s1 - 2.0
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=25.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        lower = sig.reasoning.lower()
        assert "pivot" in lower or "support" in lower

    # 12. SELL reasoning에 "Pivot" 또는 "resistance" 포함
    def test_sell_reasoning_mentions_pivot_or_resistance(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = r1 + 2.0
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=75.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        lower = sig.reasoning.lower()
        assert "pivot" in lower or "resistance" in lower

    # 13. HOLD: close가 S1~R1 사이 (중립 구간)
    def test_hold_neutral_zone(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        p, r1, s1, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = p  # 피벗 중간 → HOLD
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=50.0,
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 14. HOLD: close > R1이지만 RSI < 60 → HOLD
    def test_hold_sell_condition_but_rsi_too_low(self):
        prev_high, prev_low, prev_close = 110.0, 90.0, 100.0
        _, r1, _, _, _ = _pivot_levels(prev_high, prev_low, prev_close)
        signal_close = r1 + 2.0
        df = _make_df(
            n=40,
            prev_high=prev_high, prev_low=prev_low, prev_close=prev_close,
            signal_close=signal_close,
            rsi_override=25.0,  # RSI 낮음 → SELL 조건 불충족
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
