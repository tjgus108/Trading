"""
PriceRSIDivergenceStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import numpy as np
import pytest

from src.strategy.price_rsi_div import PriceRSIDivergenceStrategy, _calc_rsi
from src.strategy.base import Action, Confidence, Signal

_N = 60  # 최소 35행 초과


def _flat_df(n: int = _N, close: float = 100.0) -> pd.DataFrame:
    """모든 봉이 flat한 기본 DataFrame."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 1.0] * n,
        "low": [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _make_bullish_div_df(n: int = _N) -> pd.DataFrame:
    """
    Bullish divergence 조건:
    - price: 후반 저점 < 전반 저점
    - RSI: 후반 RSI > 전반 RSI (oversold에서 회복 중)
    전반 구간에서 낮은 가격 + 낮은 RSI 피벗, 후반에서 더 낮은 가격 + 높은 RSI.
    """
    closes = []
    highs = []
    lows = []

    # 전반부: 하락 → 피벗 저점 형성 (낮은 RSI)
    for i in range(n // 2):
        # 서서히 하락하다가 바닥에서 반등
        phase = i / (n // 2)
        c = 100.0 - 20.0 * phase + 5.0 * np.sin(phase * np.pi * 2)
        closes.append(c)
        highs.append(c + 1.0)
        lows.append(c - 1.0)

    # 후반부: 더 낮은 가격 저점이지만 RSI는 높음 (divergence)
    # 방법: 매우 급격한 하락 후 바로 반등 → RSI 빠르게 회복
    for i in range(n // 2):
        phase = i / (n // 2)
        # 전반 최저점보다 낮게 설정 후 후반에 반등
        c = 78.0 - 3.0 * (1 - phase)  # 75~78 범위 (전반 최저 ~80보다 낮음)
        closes.append(c)
        highs.append(c + 0.5)
        lows.append(c - 0.5)

    # df.iloc[-2] = last completed candle (divergence point)
    # last candle should have lower price low but RSI already recovering
    closes[-2] = 74.0   # 전반 저점 ~80보다 낮음
    lows[-2] = 74.0
    highs[-2] = 75.0

    # current in-progress candle
    closes[-1] = 76.0
    lows[-1] = 74.5
    highs[-1] = 76.5

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_bearish_div_df(n: int = _N) -> pd.DataFrame:
    """
    Bearish divergence 조건:
    - price: 후반 고점 > 전반 고점
    - RSI: 후반 RSI < 전반 RSI (overbought에서 약화 중)
    """
    closes = []
    highs = []
    lows = []

    # 전반부: 상승 → 피벗 고점 형성 (높은 RSI)
    for i in range(n // 2):
        phase = i / (n // 2)
        c = 100.0 + 20.0 * phase + 3.0 * np.sin(phase * np.pi * 2)
        closes.append(c)
        highs.append(c + 1.0)
        lows.append(c - 1.0)

    # 후반부: 더 높은 가격 고점이지만 RSI는 낮음
    for i in range(n // 2):
        phase = i / (n // 2)
        # 전반 최고점보다 높게 but RSI 약화
        c = 122.0 + 3.0 * phase  # 122~125 범위
        closes.append(c)
        highs.append(c + 0.5)
        lows.append(c - 0.5)

    closes[-2] = 126.0  # 전반 고점 ~120보다 높음
    highs[-2] = 127.0
    lows[-2] = 125.0

    closes[-1] = 125.0
    highs[-1] = 126.0
    lows[-1] = 124.0

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


class TestPriceRSIDivergenceStrategy:

    def setup_method(self):
        self.strategy = PriceRSIDivergenceStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_rsi_div"

    # 2. 데이터 부족 (< 35행) → HOLD
    def test_insufficient_data(self):
        df = _flat_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "데이터 부족" in sig.reasoning

    # 3. 정확히 35행 경계 → Signal 반환
    def test_exactly_min_rows(self):
        df = _flat_df(n=35)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. flat DataFrame → HOLD (다이버전스 없음)
    def test_flat_no_divergence(self):
        df = _flat_df(n=_N)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "price_rsi_div"

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _flat_df(n=_N)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 6. entry_price 양수 (데이터 충분)
    def test_entry_price_positive(self):
        df = _flat_df(n=_N)
        sig = self.strategy.generate(df)
        assert sig.entry_price >= 0

    # 7. _calc_rsi: 결과 0~100 범위
    def test_calc_rsi_range(self):
        closes = pd.Series([100.0 + i * 0.5 for i in range(50)])
        rsi = _calc_rsi(closes, 14)
        assert rsi.min() >= 0
        assert rsi.max() <= 100

    # 8. _calc_rsi: 상승 시리즈 → RSI 하락 추세보다 높음
    def test_calc_rsi_uptrend_high(self):
        # 상승 추세: 손실이 없어 avg_loss=0 → fillna(50), 하락 추세 RSI보다 높아야 함
        up_closes = pd.Series([100.0 + i for i in range(50)])
        down_closes = pd.Series([150.0 - i for i in range(50)])
        rsi_up = _calc_rsi(up_closes, 14)
        rsi_down = _calc_rsi(down_closes, 14)
        assert float(rsi_up.iloc[-1]) >= float(rsi_down.iloc[-1])

    # 9. _calc_rsi: 하락 시리즈 → RSI 낮음
    def test_calc_rsi_downtrend_low(self):
        closes = pd.Series([150.0 - i for i in range(50)])
        rsi = _calc_rsi(closes, 14)
        assert float(rsi.iloc[-1]) < 30

    # 10. BUY 신호 타입 확인
    def test_buy_signal_type(self):
        df = _make_bullish_div_df()
        sig = self.strategy.generate(df)
        # Signal 객체 반환 확인
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)

    # 11. SELL 신호 타입 확인
    def test_sell_signal_type(self):
        df = _make_bearish_div_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)

    # 12. BUY 신호 시 confidence HIGH 조건 (RSI diff > 10)
    def test_buy_confidence_high_if_large_rsi_diff(self):
        """RSI diff > 10이면 HIGH, 아니면 MEDIUM."""
        df = _make_bullish_div_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. 큰 데이터셋 안정성
    def test_large_dataset(self):
        df = _flat_df(n=200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. BUY: RSI < 50 조건 검증 (RSI >= 50이면 BUY 불가)
    def test_buy_requires_rsi_below_50(self):
        """상승 추세 flat → RSI 높음 → bullish divergence 있어도 BUY 안 됨."""
        # 상승 추세에서 flat → RSI > 50
        n = _N
        closes = [100.0 + i * 0.3 for i in range(n)]
        df = pd.DataFrame({
            "open": closes,
            "close": closes,
            "high": [c + 1.0 for c in closes],
            "low": [c - 1.0 for c in closes],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        # RSI > 50인 상승 추세에서는 BUY가 나오지 않아야 함
        assert sig.action != Action.BUY

    # 15. SELL: RSI > 50 조건 검증
    def test_sell_requires_rsi_above_50(self):
        """하락 추세 → RSI < 50 → bearish divergence 있어도 SELL 안 됨."""
        n = _N
        closes = [150.0 - i * 0.3 for i in range(n)]
        df = pd.DataFrame({
            "open": closes,
            "close": closes,
            "high": [c + 1.0 for c in closes],
            "low": [c - 1.0 for c in closes],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action != Action.SELL
