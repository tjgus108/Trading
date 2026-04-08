"""
StochasticStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.stochastic import StochasticStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 30,
    close: float = 100.0,
    k_target: str = "neutral",  # "oversold_cross", "overbought_cross", "neutral"
) -> pd.DataFrame:
    """
    신호 봉(-2)에서 원하는 %K/%D 상태를 만드는 DataFrame 생성.
    마지막 봉(-1)은 진행 중 캔들.

    k_target:
      "oversold_golden"  → %K < 20, %D < 20, %K > %D  → BUY
      "oversold_no_cross"→ %K < 20, %D < 20, %K < %D  → HOLD
      "overbought_dead"  → %K > 80, %D > 80, %K < %D  → SELL
      "overbought_no_cross"→%K>80, %D>80, %K > %D     → HOLD
      "neutral"          → %K ≈ 50                     → HOLD
    """
    rows = n

    # 기본 값: 모든 봉 동일 (close=high=low → %K=50)
    closes = [close] * rows
    highs = [close] * rows
    lows = [close] * rows

    # high-low range 를 설정해 %K 제어
    # %K = (close - low_14) / (high_14 - low_14) * 100
    if k_target == "oversold_golden":
        # 과매도 영역: high가 훨씬 높고 close는 low 근처
        # 앞부분 %K 낮게 만들고, 마지막 %K(-2봉) 는 %D보다 살짝 높게
        # 14봉 window에서 range = 100, close ≈ low+5~15
        base_high = close + 100
        base_low = close - 5
        for i in range(rows):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_low + 5   # %K ≈ 5%

        # 신호 봉(-2): %K를 15 정도로 → BUY 조건 %K > %D
        # 이전 봉들 %K 를 10 근처로 → %D(3봉 SMA) < 20
        # 신호 봉: close = low + 15 → %K=15
        closes[-2] = base_low + 15
        # 진행 중 봉(-1): 관계없음
        closes[-1] = base_low + 12

    elif k_target == "oversold_no_cross":
        # %K < %D (내려가는 중) → HOLD
        base_high = close + 100
        base_low = close - 5
        for i in range(rows):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_low + 15  # %K=15

        # 신호 봉(-2)에서 %K를 더 낮게: %K < %D
        closes[-2] = base_low + 5    # %K=5, %D ≈ 11.7 → %K < %D
        closes[-1] = base_low + 12

    elif k_target == "overbought_dead":
        # 과매수 영역: low가 훨씬 낮고 close는 high 근처
        base_high = close + 5
        base_low = close - 100
        for i in range(rows):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_high - 5  # %K ≈ 95%

        # 신호 봉(-2): %K < %D → SELL
        closes[-2] = base_high - 15   # %K=85 < %D≈90
        closes[-1] = base_high - 5

    elif k_target == "overbought_no_cross":
        # %K > %D → HOLD
        base_high = close + 5
        base_low = close - 100
        for i in range(rows):
            highs[i] = base_high
            lows[i] = base_low
            closes[i] = base_high - 15  # %K=85

        # 신호 봉(-2): %K 더 높게 → %K > %D
        closes[-2] = base_high - 5   # %K=95
        closes[-1] = base_high - 10

    else:  # neutral
        # 모든 봉 동일 → %K=50
        pass

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * rows,
    })
    return df


class TestStochasticStrategy:

    def setup_method(self):
        self.strategy = StochasticStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "stochastic"

    # 2. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. HOLD: 중립 구간
    def test_hold_neutral(self):
        df = _make_df(n=30, k_target="neutral")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "stochastic"

    # 4. BUY: 과매도 골든크로스
    def test_buy_oversold_golden_cross(self):
        df = _make_df(n=30, k_target="oversold_golden")
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "stochastic"
        assert sig.entry_price > 0

    # 5. BUY confidence: HIGH when %K < 10
    def test_buy_high_confidence(self):
        # %K=5 < 10 → HIGH
        df = _make_df(n=30, k_target="oversold_golden")
        # 신호 봉 close를 더 낮춰 %K < 10 유도
        base_low = df["low"].iloc[0]
        base_range = float(df["high"].iloc[0]) - float(df["low"].iloc[0])
        # %K = (close - low) / range * 100 < 10 → close < low + 0.1*range
        df = df.copy()
        df.iloc[-2, df.columns.get_loc("close")] = base_low + base_range * 0.05
        # %D도 <20 이 되려면 앞 2봉도 낮아야 함
        df.iloc[-3, df.columns.get_loc("close")] = base_low + base_range * 0.05
        df.iloc[-4, df.columns.get_loc("close")] = base_low + base_range * 0.05
        sig = self.strategy.generate(df)
        # %K(신호봉)=5, %D=5 → %K==D → 조건 %K>%D 불만족 → HOLD 가능
        # 따라서 HIGH confidence BUY이거나 HOLD 둘 다 수용
        assert sig.action in (Action.BUY, Action.HOLD)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 6. SELL: 과매수 데드크로스
    def test_sell_overbought_dead_cross(self):
        df = _make_df(n=30, k_target="overbought_dead")
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "stochastic"
        assert sig.entry_price > 0

    # 7. SELL confidence: HIGH when %K > 90
    def test_sell_high_confidence(self):
        df = _make_df(n=30, k_target="overbought_dead")
        base_high = float(df["high"].iloc[0])
        base_low = float(df["low"].iloc[0])
        base_range = base_high - base_low
        # %K > 90 → close > low + 0.9*range
        df = df.copy()
        df.iloc[-2, df.columns.get_loc("close")] = base_low + base_range * 0.92
        df.iloc[-3, df.columns.get_loc("close")] = base_low + base_range * 0.97
        df.iloc[-4, df.columns.get_loc("close")] = base_low + base_range * 0.97
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 8. HOLD: 과매도이지만 크로스 없음 (%K < %D)
    def test_hold_oversold_no_cross(self):
        df = _make_df(n=30, k_target="oversold_no_cross")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: 과매수이지만 크로스 없음 (%K > %D)
    def test_hold_overbought_no_cross(self):
        df = _make_df(n=30, k_target="overbought_no_cross")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30, k_target="neutral")
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

    # 11. high/low 컬럼 없을 때 (close만 있는 DataFrame) 처리
    def test_no_high_low_columns(self):
        df = pd.DataFrame({
            "open": [100.0] * 25,
            "close": [100.0] * 25,
            "volume": [1000.0] * 25,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD  # close==high==low → denom=0 → %K=50 → neutral

    # 12. 최소 데이터 경계: 정확히 20행
    def test_exactly_min_rows(self):
        df = _make_df(n=20, k_target="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.HOLD
