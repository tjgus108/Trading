"""
IchimokuStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.ichimoku import IchimokuStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26


def _make_buy_df(n: int = _MIN_ROWS + 1, close_dist: float = 0.02) -> pd.DataFrame:
    """
    BUY 조건: tenkan > kijun AND close > kijun
    전략:
      - 오래된 17봉(kijun 전용): high=100, low=50 → kijun_min=50 확보
      - 마지막 9봉(tenkan): high=110, low=108 → tenkan=(110+108)/2=109
      - kijun = (max_high_26 + min_low_26)/2 = (110+50)/2 = 80
      - tenkan(109) > kijun(80) ✓
      - close = kijun * (1 + close_dist) > kijun ✓
    """
    rows = n
    highs = [100.0] * rows
    lows = [50.0] * rows
    closes = [80.0] * rows

    # 마지막 9봉(-2 기준 포함): high=110, low=108
    start_tenkan = rows - 2 - (_TENKAN_PERIOD - 1)
    for i in range(start_tenkan, rows - 1):
        highs[i] = 110.0
        lows[i] = 108.0

    # kijun = (110 + 50) / 2 = 80
    # close > kijun
    kijun = (110.0 + 50.0) / 2
    close_val = kijun * (1.0 + close_dist)
    for i in range(rows):
        closes[i] = close_val
    # 신호 봉(-2) close 명시
    closes[-2] = close_val

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * rows,
        "ema50": [close_val] * rows,
        "atr14": [1.0] * rows,
    })


def _make_sell_df(n: int = _MIN_ROWS + 1, close_dist: float = 0.02) -> pd.DataFrame:
    """
    SELL 조건: tenkan < kijun AND close < kijun
    전략:
      - 오래된 17봉(kijun 전용): high=150, low=100 → kijun_max=150 확보
      - 마지막 9봉(tenkan): high=72, low=70 → tenkan=(72+70)/2=71
      - kijun = (150+70)/2 = 110
      - tenkan(71) < kijun(110) ✓
      - close = kijun * (1 - close_dist) < kijun ✓
    """
    rows = n
    highs = [150.0] * rows
    lows = [100.0] * rows
    closes = [110.0] * rows

    # 마지막 9봉: high=72, low=70
    start_tenkan = rows - 2 - (_TENKAN_PERIOD - 1)
    for i in range(start_tenkan, rows - 1):
        highs[i] = 72.0
        lows[i] = 70.0

    # kijun = (150 + 70) / 2 = 110
    kijun = (150.0 + 70.0) / 2
    close_val = kijun * (1.0 - close_dist)
    for i in range(rows):
        closes[i] = close_val
    closes[-2] = close_val

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * rows,
        "ema50": [close_val] * rows,
        "atr14": [1.0] * rows,
    })


class TestIchimokuStrategy:

    def setup_method(self):
        self.strategy = IchimokuStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "ichimoku"

    # 2. BUY 신호
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "ichimoku"

    # 3. BUY entry_price = close
    def test_buy_entry_price(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        # kijun=80, close=80*(1+0.02)=81.6
        assert sig.entry_price == pytest.approx(81.6)

    # 4. BUY HIGH confidence: close가 kijun에서 1% 이상 이격
    def test_buy_high_confidence(self):
        # close_dist=2% >= 1% → HIGH
        df = _make_buy_df(close_dist=0.02)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. BUY MEDIUM confidence: close가 kijun에서 1% 미만 이격
    def test_buy_medium_confidence(self):
        # close_dist=0.5% < 1% → MEDIUM
        df = _make_buy_df(close_dist=0.005)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 6. SELL 신호
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "ichimoku"

    # 7. SELL HIGH confidence: close가 kijun에서 1% 이상 아래
    def test_sell_high_confidence(self):
        # close_dist=2% → HIGH
        df = _make_sell_df(close_dist=0.02)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. SELL MEDIUM confidence: close가 kijun에서 1% 미만 아래
    def test_sell_medium_confidence(self):
        # close_dist=0.5% → MEDIUM
        df = _make_sell_df(close_dist=0.005)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 9. HOLD: tenkan > kijun but close < kijun
    def test_hold_tenkan_above_but_close_below(self):
        # BUY 세팅에서 close를 kijun 아래로
        rows = _MIN_ROWS + 1
        highs = [100.0] * rows
        lows = [50.0] * rows

        start_tenkan = rows - 2 - (_TENKAN_PERIOD - 1)
        for i in range(start_tenkan, rows - 1):
            highs[i] = 110.0
            lows[i] = 108.0

        # kijun = (110+50)/2 = 80, tenkan = (110+108)/2 = 109
        # close < kijun = 70
        closes = [70.0] * rows
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * rows,
            "ema50": [70.0] * rows,
            "atr14": [1.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: tenkan < kijun but close > kijun
    def test_hold_tenkan_below_but_close_above(self):
        # SELL 세팅에서 close를 kijun 위로
        rows = _MIN_ROWS + 1
        highs = [150.0] * rows
        lows = [100.0] * rows

        start_tenkan = rows - 2 - (_TENKAN_PERIOD - 1)
        for i in range(start_tenkan, rows - 1):
            highs[i] = 72.0
            lows[i] = 70.0

        # kijun = (150+70)/2 = 110, tenkan = (72+70)/2 = 71
        # close > kijun = 115
        closes = [115.0] * rows
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * rows,
            "ema50": [115.0] * rows,
            "atr14": [1.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. 데이터 부족 (< 30행)
    def test_insufficient_data(self):
        rows = 20
        df = pd.DataFrame({
            "open": [100.0] * rows,
            "close": [100.0] * rows,
            "high": [101.0] * rows,
            "low": [99.0] * rows,
            "volume": [1000.0] * rows,
            "ema50": [100.0] * rows,
            "atr14": [1.0] * rows,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "ichimoku"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 13. BUY reasoning에 신호 관련 정보 포함
    def test_buy_reasoning_contains_info(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "골든크로스" in sig.reasoning or "tenkan" in sig.reasoning.lower()

    # 14. SELL reasoning에 신호 관련 정보 포함
    def test_sell_reasoning_contains_info(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "데드크로스" in sig.reasoning or "tenkan" in sig.reasoning.lower()
