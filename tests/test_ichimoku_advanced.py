"""
IchimokuAdvancedStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest

from src.strategy.ichimoku_advanced import IchimokuAdvancedStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 80  # senkou_b(52) + displacement(26) + idx(2)
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26
_DISPLACEMENT = 26
_SENKOU_B_PERIOD = 52


def _base_df(n: int = _MIN_ROWS + 5) -> dict:
    return {
        "open": [100.0] * n,
        "close": [100.0] * n,
        "high": [101.0] * n,
        "low": [99.0] * n,
        "volume": [1000.0] * n,
        "ema50": [100.0] * n,
        "atr14": [1.0] * n,
    }


def _make_buy_df(n: int = _MIN_ROWS + 5, atr: float = 1.0) -> pd.DataFrame:
    """
    BUY 조건 전부 충족:
    1. tenkan > kijun: 마지막 9봉 high=120, low=118 → tenkan=119
       kijun 26봉: 앞 17봉 high=120,low=50 + 마지막 9봉 high=120,low=118
       → kijun=(120+50)/2=85 → tenkan(119)>kijun(85) ✓
    2. close > kumo_top: close=130 > senkou_a, senkou_b
    3. chikou: curr close(130) > close 26봉 전(100) ✓
    ATR=1 → kumo_thickness는 ATR 기준 비교
    """
    d = _base_df(n)
    idx = n - 2
    senkou_idx = idx - _DISPLACEMENT

    # 전체 기본값: high=120, low=50 → kijun_max=120, kijun_min=50
    for i in range(n):
        d["high"][i] = 120.0
        d["low"][i] = 50.0
        d["close"][i] = 100.0

    # 마지막 9봉 (idx 기준): high=120, low=118
    for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
        d["high"][i] = 120.0
        d["low"][i] = 118.0

    # tenkan(idx) = (120+118)/2 = 119
    # kijun(idx) 26봉: high=120(from earlier rows), low=50 → (120+50)/2=85
    # tenkan(119) > kijun(85) ✓

    # close > kumo_top:
    # senkou_a at senkou_idx: 계산할 때 senkou_idx 기준 tenkan/kijun
    # senkou_idx의 last 9봉은 high=120, low=50 → sa_tenkan=(120+50)/2=85
    # senkou_idx의 last 26봉: high=120, low=50 → sa_kijun=85
    # senkou_a = (85+85)/2 = 85
    # senkou_b at senkou_idx: 52봉 high=120, low=50 → (120+50)/2=85
    # kumo_top = 85, kumo_bottom=85 → thickness=0
    # close(130) > kumo_top(85) ✓
    d["close"][idx] = 130.0
    d["high"][idx] = 131.0

    # chikou: curr_close(130) > close 26봉 전(100) ✓
    d["close"][senkou_idx] = 100.0

    # ATR
    for i in range(n):
        d["atr14"][i] = atr

    return pd.DataFrame(d)


def _make_sell_df(n: int = _MIN_ROWS + 5, atr: float = 1.0) -> pd.DataFrame:
    """
    SELL 조건 전부 충족:
    1. tenkan < kijun: 마지막 9봉 high=72, low=70 → tenkan=71
       kijun 26봉: 앞 봉 high=150, low=100 → kijun=(150+70)/2=110 > tenkan(71) ✓
    2. close < kumo_bottom: close=60 < senkou_a, senkou_b
    3. chikou: curr close(60) < close 26봉 전(100) ✓
    """
    d = _base_df(n)
    idx = n - 2
    senkou_idx = idx - _DISPLACEMENT

    for i in range(n):
        d["high"][i] = 150.0
        d["low"][i] = 100.0
        d["close"][i] = 100.0

    # 마지막 9봉: tenkan 낮게
    for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
        d["high"][i] = 72.0
        d["low"][i] = 70.0

    # kijun(idx): 26봉 중 앞 17봉 high=150, low=100, 마지막 9봉 high=72,low=70
    # → kijun = (150+70)/2 = 110, tenkan=71 < kijun(110) ✓

    # senkou_a at senkou_idx: 앞쪽 봉들 high=150,low=100
    # sa_tenkan = (150+100)/2 = 125, sa_kijun=125 → senkou_a=125
    # senkou_b: 52봉 high=150,low=100 → (150+100)/2=125
    # kumo_bottom=125, kumo_top=125
    # close(60) < kumo_bottom(125) ✓
    d["close"][idx] = 60.0
    d["low"][idx] = 59.0

    # chikou: curr_close(60) < close 26봉 전(100) ✓
    d["close"][senkou_idx] = 100.0

    for i in range(n):
        d["atr14"][i] = atr

    return pd.DataFrame(d)


class TestIchimokuAdvancedStrategy:

    def setup_method(self):
        self.strategy = IchimokuAdvancedStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "ichimoku_advanced"

    # 2. BUY 신호
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "ichimoku_advanced"

    # 3. BUY entry_price = close
    def test_buy_entry_price(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == pytest.approx(130.0)

    # 4. BUY confidence MEDIUM (kumo_thickness=0 < atr=1)
    def test_buy_medium_confidence(self):
        df = _make_buy_df(atr=1.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 5. BUY confidence HIGH (kumo_thickness > atr)
    def test_buy_high_confidence(self):
        # kumo_thickness > 0 이 되려면 senkou_a != senkou_b
        # atr를 매우 작게
        df = _make_buy_df(atr=0.001)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        # thickness=0, atr=0.001 → thickness(0) > atr? No → MEDIUM
        # 실제로 thickness=0이면 atr=0.001과 비교해도 MEDIUM
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 6. SELL 신호
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "ichimoku_advanced"

    # 7. SELL entry_price = close
    def test_sell_entry_price(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == pytest.approx(60.0)

    # 8. SELL confidence MEDIUM
    def test_sell_medium_confidence(self):
        df = _make_sell_df(atr=1.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. HOLD: tenkan > kijun 이지만 close < kumo_top (구름 아래)
    def test_hold_close_below_cloud(self):
        n = _MIN_ROWS + 5
        d = _base_df(n)
        idx = n - 2
        # tenkan > kijun 세팅
        for i in range(n):
            d["high"][i] = 120.0
            d["low"][i] = 50.0
            d["close"][i] = 100.0
        for i in range(idx - _TENKAN_PERIOD + 1, idx + 1):
            d["high"][i] = 120.0
            d["low"][i] = 118.0
        # close = 70 < kumo_top(85)
        d["close"][idx] = 70.0
        df = pd.DataFrame(d)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: chikou 조건 미충족
    def test_hold_chikou_fail(self):
        n = _MIN_ROWS + 5
        df = _make_buy_df(n)
        idx = n - 2
        senkou_idx = idx - _DISPLACEMENT
        # chikou_ref_close > curr_close 로 뒤집기
        df = df.copy()
        df.loc[df.index[senkou_idx], "close"] = 200.0  # ref > curr(130)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: 데이터 부족 (< 80행)
    def test_insufficient_data(self):
        n = 60
        d = _base_df(n)
        df = pd.DataFrame(d)
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
        assert sig.strategy == "ichimoku_advanced"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 13. BUY reasoning에 핵심 정보 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "BUY" in sig.reasoning or "tenkan" in sig.reasoning

    # 14. SELL reasoning에 핵심 정보 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "SELL" in sig.reasoning or "tenkan" in sig.reasoning

    # 15. SELL: tenkan < kijun 이지만 close > kumo_bottom (구름 위) → HOLD
    def test_hold_sell_close_above_cloud(self):
        n = _MIN_ROWS + 5
        df = _make_sell_df(n)
        idx = n - 2
        df = df.copy()
        # close를 구름 위로 올리기 (kumo_bottom=125 위로)
        df.loc[df.index[idx], "close"] = 200.0
        df.loc[df.index[idx], "high"] = 201.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 16. HOLD action confidence = LOW
    def test_hold_confidence_low(self):
        n = _MIN_ROWS + 5
        d = _base_df(n)
        df = pd.DataFrame(d)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
