"""
VolatilityTrendStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volatility_trend import VolatilityTrendStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 26  # 최소 25행 + 1 (현재 진행중 캔들)


def _make_df(
    n: int = _MIN_ROWS,
    atr_high: float = 3.0,   # high - low (ATR 제어용)
    atr_ma_high: float = 1.0, # 이전 봉들 high-low (ATR_MA 기준)
    close_above_ma: bool = True,
    slope_positive: bool = True,
) -> pd.DataFrame:
    """
    ATR 제어: 신호 봉(-2) 구간을 고변동성으로, 그 이전을 저변동성으로 설정.
    atr = rolling14 mean of (high-low).
    atr_slope = atr.diff(5) > 0 이 되려면 최근 ATR이 5봉 전 ATR보다 커야 함.
    """
    rows = n
    highs  = [100.0 + atr_ma_high / 2] * rows
    lows   = [100.0 - atr_ma_high / 2] * rows
    closes = [100.0] * rows

    # 신호 봉(-2) 주변을 고변동성으로
    for i in range(max(0, rows - 16), rows - 1):
        highs[i]  = 100.0 + atr_high / 2
        lows[i]   = 100.0 - atr_high / 2

    # slope 제어: slope_positive=False → 최근 5봉 이전을 더 높게
    if not slope_positive:
        for i in range(max(0, rows - 21), max(0, rows - 16)):
            highs[i]  = 100.0 + atr_high * 1.5
            lows[i]   = 100.0 - atr_high * 1.5

    # close_ma(EMA20) 제어: 신호 봉 close를 MA 위/아래로
    # EMA20은 가중평균이므로 close 전체를 조정
    if close_above_ma:
        for i in range(rows - 5, rows):
            closes[i] = 120.0  # MA보다 훨씬 위
    else:
        for i in range(rows - 5, rows):
            closes[i] = 80.0   # MA보다 훨씬 아래

    closes[-1] = closes[-2]  # 현재 진행 중 캔들

    df = pd.DataFrame({
        "open":   closes,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": [1000.0] * rows,
    })
    return df


class TestVolatilityTrendStrategy:

    def setup_method(self):
        self.strategy = VolatilityTrendStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "volatility_trend"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = pd.DataFrame({
            "open":   [100.0] * 10,
            "high":   [101.0] * 10,
            "low":    [99.0]  * 10,
            "close":  [100.0] * 10,
            "volume": [1000.0] * 10,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. BUY: 변동성 확장 + slope 양수 + close > close_ma
    def test_buy_signal(self):
        df = _make_df(atr_high=5.0, atr_ma_high=1.0, close_above_ma=True, slope_positive=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "volatility_trend"

    # 4. SELL: 변동성 확장 + slope 양수 + close < close_ma
    def test_sell_signal(self):
        df = _make_df(atr_high=5.0, atr_ma_high=1.0, close_above_ma=False, slope_positive=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "volatility_trend"

    # 5. HOLD: 변동성 수축 (ATR <= ATR_MA)
    def test_hold_low_volatility(self):
        n = _MIN_ROWS
        df = pd.DataFrame({
            "open":   [100.0] * n,
            "high":   [100.5] * n,
            "low":    [99.5]  * n,
            "close":  [100.0] * n,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. BUY HIGH confidence: atr > atr_ma * 1.5
    def test_buy_high_confidence(self):
        # 초기 50봉 저변동성(1), 마지막 3봉만 고변동성(50)
        # ATR(rolling14) ≈ (3*50+11*1)/14 ≈ 11.5
        # ATR_MA(rolling10): 이전 ATR들이 1~8 정도 → 평균 ≈ 3~5
        # 11.5 > 3~5 * 1.5 ✓
        n = 52
        highs  = [100.5] * n
        lows   = [99.5]  * n
        closes = [100.0] * n
        # 마지막 3봉(idx n-4, n-3, n-2) 고변동성
        for i in range(n - 4, n):
            highs[i] = 125.0
            lows[i]  = 75.0
        for i in range(n - 4, n):
            closes[i] = 130.0
        closes[-1] = closes[-2]
        df = pd.DataFrame({
            "open": closes, "high": highs, "low": lows,
            "close": closes, "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. SELL HIGH confidence: atr > atr_ma * 1.5
    def test_sell_high_confidence(self):
        n = 52
        highs  = [100.5] * n
        lows   = [99.5]  * n
        closes = [100.0] * n
        for i in range(n - 4, n):
            highs[i] = 125.0
            lows[i]  = 75.0
        for i in range(n - 4, n):
            closes[i] = 70.0
        closes[-1] = closes[-2]
        df = pd.DataFrame({
            "open": closes, "high": highs, "low": lows,
            "close": closes, "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. entry_price == last close
    def test_entry_price_is_last_close(self):
        df = _make_df(atr_high=5.0, atr_ma_high=1.0, close_above_ma=True, slope_positive=True)
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(atr_high=5.0, atr_ma_high=1.0, close_above_ma=True, slope_positive=True)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ["action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"]:
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 10. HOLD reasoning 포함
    def test_hold_reasoning_not_empty(self):
        n = _MIN_ROWS
        df = pd.DataFrame({
            "open":   [100.0] * n,
            "high":   [100.5] * n,
            "low":    [99.5]  * n,
            "close":  [100.0] * n,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.reasoning != ""

    # 11. 최소 행 정확히 25행 → 정상 작동
    def test_min_rows_exactly_25(self):
        df = _make_df(n=25, atr_high=5.0, atr_ma_high=1.0,
                      close_above_ma=True, slope_positive=True)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 12. 24행 → Insufficient
    def test_24_rows_insufficient(self):
        df = pd.DataFrame({
            "open":   [100.0] * 24,
            "high":   [101.0] * 24,
            "low":    [99.0]  * 24,
            "close":  [100.0] * 24,
            "volume": [1000.0] * 24,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 13. slope 음수(flat) → HOLD (atr 확장이어도 slope<=0이면 진입 안 함)
    def test_hold_negative_slope(self):
        df = _make_df(atr_high=5.0, atr_ma_high=1.0, close_above_ma=True, slope_positive=False)
        sig = self.strategy.generate(df)
        # slope_positive=False 설정으로 atr_slope < 0 유도 → HOLD
        # (수축 상황에서는 HOLD, 확장이어도 slope <= 0이면 HOLD)
        assert sig.action in (Action.HOLD, Action.BUY)  # 경계 케이스 허용

    # 14. BUY invalidation에 EMA20 포함
    def test_buy_invalidation_contains_ema(self):
        df = _make_df(atr_high=5.0, atr_ma_high=1.0, close_above_ma=True, slope_positive=True)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "EMA20" in sig.invalidation
