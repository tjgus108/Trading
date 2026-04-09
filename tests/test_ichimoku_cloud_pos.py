"""
IchimokuCloudPosStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.ichimoku_cloud_pos import IchimokuCloudPosStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 80
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26
_SENKOU_B_PERIOD = 52
_DISPLACEMENT = 26


def _make_df(n: int, highs, lows, closes, volumes=None) -> pd.DataFrame:
    if volumes is None:
        volumes = [1000.0] * n
    opens = closes[:]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": closes,
        "atr14": [1.0] * n,
    })


def _make_buy_df(n: int = _MIN_ROWS + 1, dist: float = 0.03) -> pd.DataFrame:
    """
    BUY 조건: close > cloud_top AND tenkan > kijun

    설계:
      - 전체: high=200, low=50 → senkou_b=(200+50)/2=125
      - senkou_idx = n-2-26 에서 tenkan/kijun 계산:
          senkou_a_tenkan = (200+50)/2=125, senkou_a_kijun=(200+50)/2=125
          senkou_a=125, senkou_b=125, cloud_top=125
      - 현재 tenkan (idx=n-2): 최근 9봉 high=180, low=178 → tenkan=179
      - 현재 kijun (idx=n-2): 최근 26봉 — 9봉은 high=180, 나머지 17봉 high=200, low=50
          kijun_high=200, kijun_low=50 → kijun=125
      - tenkan(179) > kijun(125) ✓
      - close = cloud_top * (1 + dist) > cloud_top ✓
    """
    rows = n
    highs = [200.0] * rows
    lows = [50.0] * rows

    # 현재 기준(idx=n-2) 마지막 9봉: high=180, low=178
    idx = rows - 2
    start_tenkan = idx - _TENKAN_PERIOD + 1
    for i in range(start_tenkan, idx + 1):
        highs[i] = 180.0
        lows[i] = 178.0

    # kijun = (200+178)/2 = 189? No: 나머지 17봉에 high=200 있으므로
    # kijun_high=200, kijun_low=178 → kijun=(200+178)/2=189
    # senkou_a=senkou_b=125, cloud_top=125
    # close > 125: use cloud_top=125 approach
    # Actually let's fix lows for non-tenkan part to keep kijun low=50
    for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
        lows[i] = 178.0  # tenkan봉 low

    # kijun_low = min of 26 봉: non-tenkan 봉 low=50, tenkan봉 low=178 → kijun_low=50
    # kijun_high = max of 26봉: non-tenkan봉 high=200, tenkan봉 high=180 → kijun_high=200
    # kijun = (200+50)/2 = 125
    # cloud_top = 125, close = 125*(1+dist)
    cloud_top = 125.0
    close_val = cloud_top * (1.0 + dist)
    closes = [close_val] * rows

    return _make_df(rows, highs, lows, closes)


def _make_sell_df(n: int = _MIN_ROWS + 1, dist: float = 0.03) -> pd.DataFrame:
    """
    SELL 조건: close < cloud_bottom AND tenkan < kijun

    설계:
      - 전체: high=200, low=50 → cloud_bottom=125
      - 현재 tenkan 봉: high=72, low=70 → tenkan=71
      - kijun = (200+70)/2 = 135? No:
          kijun 26봉 중 비-tenkan봉 high=200, low=50; tenkan봉 high=72, low=70
          kijun_high=200, kijun_low=50 → kijun=125
      - tenkan(71) < kijun(125) ✓
      - cloud_bottom=125, close = 125*(1-dist) < cloud_bottom ✓
    """
    rows = n
    highs = [200.0] * rows
    lows = [50.0] * rows

    idx = rows - 2
    start_tenkan = idx - _TENKAN_PERIOD + 1
    for i in range(start_tenkan, idx + 1):
        highs[i] = 72.0
        lows[i] = 70.0

    cloud_bottom = 125.0
    close_val = cloud_bottom * (1.0 - dist)
    closes = [close_val] * rows

    return _make_df(rows, highs, lows, closes)


class TestIchimokuCloudPosStrategy:

    def setup_method(self):
        self.strategy = IchimokuCloudPosStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "ichimoku_cloud_pos"

    # 2. BUY 신호
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "ichimoku_cloud_pos"

    # 3. BUY entry_price = close
    def test_buy_entry_price(self):
        df = _make_buy_df(dist=0.03)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == pytest.approx(125.0 * 1.03)

    # 4. BUY HIGH confidence (dist >= 2%)
    def test_buy_high_confidence(self):
        df = _make_buy_df(dist=0.03)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. BUY MEDIUM confidence (dist < 2%)
    def test_buy_medium_confidence(self):
        df = _make_buy_df(dist=0.01)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 6. SELL 신호
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "ichimoku_cloud_pos"

    # 7. SELL HIGH confidence (dist >= 2%)
    def test_sell_high_confidence(self):
        df = _make_sell_df(dist=0.03)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. SELL MEDIUM confidence (dist < 2%)
    def test_sell_medium_confidence(self):
        df = _make_sell_df(dist=0.01)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 9. HOLD: close > cloud_top but tenkan < kijun
    def test_hold_above_cloud_but_tenkan_below(self):
        rows = _MIN_ROWS + 1
        highs = [200.0] * rows
        lows = [50.0] * rows
        idx = rows - 2
        # tenkan봉: high=72, low=70 → tenkan=71 < kijun=125
        start_t = idx - _TENKAN_PERIOD + 1
        for i in range(start_t, idx + 1):
            highs[i] = 72.0
            lows[i] = 70.0
        # close > cloud_top=125
        closes = [130.0] * rows
        df = _make_df(rows, highs, lows, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: close < cloud_bottom but tenkan > kijun
    def test_hold_below_cloud_but_tenkan_above(self):
        rows = _MIN_ROWS + 1
        highs = [200.0] * rows
        lows = [50.0] * rows
        idx = rows - 2
        # tenkan봉: high=180, low=178 → tenkan=179 > kijun=125
        start_t = idx - _TENKAN_PERIOD + 1
        for i in range(start_t, idx + 1):
            highs[i] = 180.0
            lows[i] = 178.0
        # close < cloud_bottom=125
        closes = [100.0] * rows
        df = _make_df(rows, highs, lows, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: close 구름 안에 있을 때
    def test_hold_inside_cloud(self):
        rows = _MIN_ROWS + 1
        # senkou_a != senkou_b 구름 생성: high=200, low=50 → both=125 (flat cloud)
        # close = 125 (구름 경계) → 구름 위/아래 조건 불충족
        highs = [200.0] * rows
        lows = [50.0] * rows
        closes = [125.0] * rows
        df = _make_df(rows, highs, lows, closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. 데이터 부족 (< 80행)
    def test_insufficient_data(self):
        rows = 50
        df = _make_df(rows, [101.0] * rows, [99.0] * rows, [100.0] * rows)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "ichimoku_cloud_pos"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 14. BUY reasoning에 cloud_top 포함
    def test_buy_reasoning_contains_cloud_top(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "cloud_top" in sig.reasoning or "Cloud Position" in sig.reasoning

    # 15. SELL reasoning에 cloud_bottom 포함
    def test_sell_reasoning_contains_cloud_bottom(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "cloud_bottom" in sig.reasoning or "Cloud Position" in sig.reasoning
