"""
VolumeMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_momentum import VolumeMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(
    n: int = _MIN_ROWS + 5,
    price_mom: float = 0.0,
    vol_mom: float = 0.0,
    close_above_vol_ma: bool = True,
) -> pd.DataFrame:
    """
    price_mom: 5봉 가격 변화율 (close[-2] vs close[-7])
    vol_mom:   5봉 거래량 변화율 (vol[-2] vs vol[-7])
    close_above_vol_ma: close[-2]가 vol_ma(20) 위이면 True
    """
    base_close = 100.0
    # close[-2] 결정 (iloc[-2] = 마지막 완성 봉)
    # price_mom = (close[-2] - close[-7]) / close[-7]
    close_curr = base_close * (1 + price_mom)
    close_prev5 = base_close  # 5봉 전 close

    closes = [base_close] * n
    closes[-2] = close_curr
    closes[-7] = close_prev5  # -2 에서 5봉 전 = -7

    # vol_ma 제어: base_vol=1000, close_curr 기준 위/아래 설정
    base_vol = 1000.0
    vol_curr = base_vol * (1 + vol_mom)
    vol_prev5 = base_vol

    volumes = [base_vol] * n
    volumes[-2] = vol_curr
    volumes[-7] = vol_prev5  # 5봉 전 vol

    # vol_ma(20): iloc[-2] 기준 rolling(20) → iloc[-21:-1]의 평균
    # 현재 vol_curr가 rolling MA 위/아래가 되도록 vol_ma 값 제어
    # close > vol_ma 조건 → vol_ma를 close보다 낮게 혹은 높게
    # vol_ma는 volume의 rolling mean이 아닌 close와 비교됨
    # NOTE: 코드에서 close > vol_ma (close가 volume rolling mean보다 큰지 비교)
    # close는 가격, vol_ma는 거래량 평균 → 보통 가격이 훨씬 큼
    # 테스트에서 명시적으로 제어하기 위해 volume 값을 조정
    if close_above_vol_ma:
        # close_curr > vol_ma(20) 가 되도록: volume들을 close_curr보다 작게
        for i in range(n):
            volumes[i] = close_curr * 0.5  # vol_ma will be ~0.5*close_curr
        volumes[-2] = close_curr * 0.5 * (1 + vol_mom)
        volumes[-7] = close_curr * 0.5
    else:
        # close_curr < vol_ma(20) 가 되도록: volume들을 close_curr보다 크게
        for i in range(n):
            volumes[i] = close_curr * 2.0
        volumes[-2] = close_curr * 2.0 * (1 + vol_mom)
        volumes[-7] = close_curr * 2.0

    df = pd.DataFrame({
        "open": closes[:],
        "close": closes,
        "high": [c * 1.01 for c in closes],
        "low": [c * 0.99 for c in closes],
        "volume": volumes,
    })
    return df


class TestVolumeMomentumStrategy:

    def setup_method(self):
        self.strategy = VolumeMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volume_momentum"

    # 2. BUY: price_mom > 0.01, vol_mom > 0.3, close > vol_ma
    def test_buy_signal(self):
        df = _make_df(price_mom=0.02, vol_mom=0.5, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "volume_momentum"

    # 3. BUY HIGH confidence: vol_mom > 0.6 AND price_mom > 0.02
    def test_buy_high_confidence(self):
        df = _make_df(price_mom=0.03, vol_mom=0.7, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 4. BUY MEDIUM confidence: vol_mom in (0.3, 0.6]
    def test_buy_medium_confidence(self):
        df = _make_df(price_mom=0.015, vol_mom=0.4, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 5. SELL: price_mom < -0.01, vol_mom > 0.3, close < vol_ma
    def test_sell_signal(self):
        df = _make_df(price_mom=-0.02, vol_mom=0.5, close_above_vol_ma=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "volume_momentum"

    # 6. SELL HIGH confidence: vol_mom > 0.6 AND price_mom < -0.02
    def test_sell_high_confidence(self):
        df = _make_df(price_mom=-0.03, vol_mom=0.7, close_above_vol_ma=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. SELL MEDIUM confidence: vol_mom in (0.3, 0.6]
    def test_sell_medium_confidence(self):
        df = _make_df(price_mom=-0.015, vol_mom=0.4, close_above_vol_ma=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 8. HOLD: price_mom > 0.01 but close < vol_ma (wrong side)
    def test_hold_buy_price_but_below_vol_ma(self):
        df = _make_df(price_mom=0.02, vol_mom=0.5, close_above_vol_ma=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: price_mom < -0.01 but close > vol_ma (wrong side)
    def test_hold_sell_price_but_above_vol_ma(self):
        df = _make_df(price_mom=-0.02, vol_mom=0.5, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: vol_mom <= 0.3 (insufficient volume surge)
    def test_hold_low_vol_mom(self):
        df = _make_df(price_mom=0.02, vol_mom=0.1, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: price_mom in (-0.01, 0.01) (neutral)
    def test_hold_neutral_price_mom(self):
        df = _make_df(price_mom=0.005, vol_mom=0.5, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. 데이터 부족 (< 25행)
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(price_mom=0.02, vol_mom=0.5, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 14. entry_price는 현재 close
    def test_entry_price_is_close(self):
        df = _make_df(price_mom=0.02, vol_mom=0.5, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_close, rel=1e-3)

    # 15. HOLD reasoning not empty
    def test_hold_reasoning_not_empty(self):
        df = _make_df(price_mom=0.0, vol_mom=0.0, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.reasoning != ""

    # 16. BUY reasoning mentions price_mom and vol_mom
    def test_buy_reasoning_content(self):
        df = _make_df(price_mom=0.02, vol_mom=0.5, close_above_vol_ma=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "price_mom" in sig.reasoning
        assert "vol_mom" in sig.reasoning
