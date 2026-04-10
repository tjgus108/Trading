"""
KijunBounceStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.kijun_bounce import KijunBounceStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26


def _base_df(n: int, highs, lows, closes, opens=None) -> pd.DataFrame:
    if opens is None:
        opens = closes[:]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = _MIN_ROWS + 5, kijun_rising: bool = True) -> pd.DataFrame:
    """
    BUY 조건:
    - tenkan > kijun: 마지막 9봉 high/low를 높게 설정
    - kijun 터치: close = kijun * 1.003 (0.3% 이격, ±0.5% 이내)
    - 양봉: close > open
    - kijun_rising/falling:
        current_kijun = max(high[idx-25..idx]), prev_kijun = max(high[idx-26..idx-1])
        idx 위치만 current에 고유, idx-26만 prev에 고유
    """
    rows = n
    idx = rows - 2  # _last() 기준 인덱스

    # 기본: high=100, low=60 (flat)
    highs = [100.0] * rows
    lows = [60.0] * rows

    # 마지막 9봉(tenkan 창): high=130, low=128 → tenkan=(130+128)/2=129
    for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
        highs[i] = 130.0
        lows[i] = 128.0

    # current_kijun 창: [idx-25..idx], high_max=130(from tenkan), low_min=60 → kijun=(130+60)/2=95
    # prev_kijun 창: [idx-26..idx-1], shares [idx-25..idx-1] with current
    # prev includes highs[idx-26]=100(or 200), current includes highs[idx]=130

    if kijun_rising:
        # highs[idx]=130 이미 설정됨 (current에만 있음)
        # prev 창에서 max는 highs[idx-26..idx-1] → highs[idx-1]=130(tenkan 포함)
        # prev_kijun_high = max(highs[idx-26..idx-1]) → idx-1 포함이므로 130
        # → prev_kijun = (130+128)/2 = 129 (tenkan 봉들도 prev에 포함됨)
        # prev_kijun == current_kijun → not rising
        # 해결: highs[idx]를 훨씬 높게 하고, prev 창에 해당 봉 제외
        # idx 위치만 current에 고유 → highs[idx]를 500으로 올리면 current_kijun_high=500, prev=130
        highs[idx] = 500.0
        # kijun = (500+60)/2 = 280, close = 280*1.003
        kijun = (500.0 + 60.0) / 2
    else:
        # kijun 하락: highs[idx-26]을 매우 높게 → prev_kijun_high=500 > current=130
        if idx - _KIJUN_PERIOD >= 0:
            highs[idx - _KIJUN_PERIOD] = 500.0
        # prev_kijun = (500+60)/2=280, current_kijun=(130+60)/2=95 → falling
        kijun = (130.0 + 60.0) / 2

    close_val = kijun * 1.003
    closes = [close_val] * rows
    opens = [close_val * 0.998] * rows

    return _base_df(rows, highs, lows, closes, opens)


def _make_sell_df(n: int = _MIN_ROWS + 5, kijun_falling: bool = True) -> pd.DataFrame:
    """
    SELL 조건:
    - tenkan < kijun: 마지막 9봉을 낮게 설정
    - kijun 터치: close = kijun * 0.997
    - 음봉: close < open
    - kijun_falling:
        current_kijun uses high[idx-25..idx], prev uses high[idx-26..idx-1]
        idx-26은 prev에만 고유, idx는 current에만 고유
    """
    rows = n
    idx = rows - 2

    highs = [120.0] * rows
    lows = [60.0] * rows

    # 마지막 9봉: high=62, low=60 → tenkan=(62+60)/2=61
    for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
        highs[i] = 62.0
        lows[i] = 60.0

    if kijun_falling:
        # prev_kijun > current_kijun: highs[idx-26]=500 (prev에만 고유)
        # prev_kijun_high=500, prev_kijun_low=60 → prev_kijun=280
        # current_kijun_high=120, current_kijun_low=60 → kijun=90
        # tenkan=61 < kijun=90 ✓
        if idx - _KIJUN_PERIOD >= 0:
            highs[idx - _KIJUN_PERIOD] = 500.0
        kijun = (120.0 + 60.0) / 2  # 90
    else:
        # kijun 상승: current > prev → highs[idx]=500 (current에만 고유)
        # current_kijun_high=500 → kijun=(500+60)/2=280
        # tenkan=(62+60)/2=61 < kijun=280 ✓
        highs[idx] = 500.0
        kijun = (500.0 + 60.0) / 2  # 280

    close_val = kijun * 0.997
    closes = [close_val] * rows
    opens = [close_val * 1.002] * rows

    return _base_df(rows, highs, lows, closes, opens)


class TestKijunBounceStrategy:

    def setup_method(self):
        self.strategy = KijunBounceStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "kijun_bounce"

    # 2. BUY 신호 생성
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "kijun_bounce"

    # 3. BUY entry_price = close
    def test_buy_entry_price(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        last_close = float(df.iloc[-2]["close"])
        assert sig.entry_price == pytest.approx(last_close)

    # 4. BUY HIGH confidence: kijun rising
    def test_buy_high_confidence_when_kijun_rising(self):
        df = _make_buy_df(kijun_rising=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. SELL 신호 생성
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "kijun_bounce"

    # 6. SELL entry_price = close
    def test_sell_entry_price(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        last_close = float(df.iloc[-2]["close"])
        assert sig.entry_price == pytest.approx(last_close)

    # 7. SELL HIGH confidence: kijun falling
    def test_sell_high_confidence_when_kijun_falling(self):
        df = _make_sell_df(kijun_falling=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. HOLD: kijun 터치하지 않음 (close가 kijun에서 멀리)
    def test_hold_when_not_touching_kijun(self):
        rows = _MIN_ROWS + 5
        highs = [120.0] * rows
        lows = [80.0] * rows
        idx = rows - 2
        for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
            highs[i] = 130.0
            lows[i] = 128.0
        kijun = (130.0 + 80.0) / 2  # 105
        close_val = kijun * 1.10  # 10% 위 → 터치 아님
        closes = [close_val] * rows
        opens = [close_val * 0.998] * rows
        df = _base_df(rows, highs, lows, closes, opens)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: kijun 터치 but 양봉이지만 cloud bearish (tenkan < kijun)
    def test_hold_when_buy_touch_but_cloud_bearish(self):
        rows = _MIN_ROWS + 5
        highs = [120.0] * rows
        lows = [80.0] * rows
        idx = rows - 2
        # tenkan < kijun: 마지막 9봉 낮게
        for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
            highs[i] = 82.0
            lows[i] = 80.0
        kijun = (120.0 + 80.0) / 2  # 100
        close_val = kijun * 1.003
        closes = [close_val] * rows
        opens = [close_val * 0.998] * rows  # 양봉
        df = _base_df(rows, highs, lows, closes, opens)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: kijun 터치 but 음봉이지만 cloud bullish (tenkan > kijun)
    def test_hold_when_sell_touch_but_cloud_bullish(self):
        rows = _MIN_ROWS + 5
        highs = [120.0] * rows
        lows = [80.0] * rows
        idx = rows - 2
        # tenkan > kijun: 마지막 9봉 높게
        for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
            highs[i] = 130.0
            lows[i] = 128.0
        kijun = (130.0 + 80.0) / 2  # 105
        close_val = kijun * 0.997
        closes = [close_val] * rows
        opens = [close_val * 1.002] * rows  # 음봉
        df = _base_df(rows, highs, lows, closes, opens)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. 데이터 부족 (< 30행)
    def test_insufficient_data(self):
        rows = 20
        df = _base_df(
            rows,
            [101.0] * rows,
            [99.0] * rows,
            [100.0] * rows,
        )
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
        assert sig.strategy == "kijun_bounce"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 13. BUY reasoning에 kijun 정보 포함
    def test_buy_reasoning_contains_kijun(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "kijun" in sig.reasoning.lower() or "Kijun" in sig.reasoning

    # 14. SELL reasoning에 kijun 정보 포함
    def test_sell_reasoning_contains_kijun(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "kijun" in sig.reasoning.lower() or "Kijun" in sig.reasoning

    # 15. HOLD action = HOLD, confidence = LOW
    def test_hold_confidence_is_low(self):
        rows = 20
        df = _base_df(rows, [101.0] * rows, [99.0] * rows, [100.0] * rows)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
