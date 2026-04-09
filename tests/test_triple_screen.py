"""
TripleScreenStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

from typing import Optional

import pandas as pd
import pytest

from src.strategy.triple_screen import TripleScreenStrategy
from src.strategy.base import Action, Confidence, Signal

_N = 50  # 넉넉한 행 수


def _make_df_buy(stoch_k: float = 20.0, n: int = _N) -> pd.DataFrame:
    """
    BUY 조건 DataFrame:
      - Screen 1 (bullish tide): closes 꾸준히 상승 → ema26[-1] > ema26[-2]
      - Screen 2 (stoch_k < 30): high/low 범위로 정밀 제어, close는 트렌드 유지
      - Screen 3 (bull candle): open < close
    """
    # 상승 트렌드 closes
    closes = [100.0 + i * 1.0 for i in range(n)]
    opens = list(closes)

    # Stochastic 제어: 14봉 고정 high/low
    # %K = (close - low_14) / (high_14 - low_14) * 100
    # 신호 봉 close = closes[-2] ≈ 100 + (n-2)*1
    signal_close = closes[-2]  # 트렌드 유지

    # 14봉 low/high를 설정: signal_close가 stoch_k%에 위치하도록
    # low_14 = signal_close - stoch_k/100 * range_val
    # high_14 = low_14 + range_val
    range_val = 50.0
    low_14 = signal_close - stoch_k / 100.0 * range_val
    high_14 = low_14 + range_val

    highs = [high_14] * n
    lows = [low_14] * n

    # 양봉: open = signal_close - 1
    opens[-2] = signal_close - 1.0
    opens[-1] = closes[-1] - 1.0

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_df_sell(stoch_k: float = 80.0, n: int = _N) -> pd.DataFrame:
    """
    SELL 조건 DataFrame:
      - Screen 1 (bearish tide): closes 꾸준히 하락 → ema26[-1] < ema26[-2]
      - Screen 2 (stoch_k > 70): high/low 범위로 정밀 제어
      - Screen 3 (bear candle): open > close
    """
    closes = [100.0 + (n - i) * 1.0 for i in range(n)]
    opens = list(closes)

    signal_close = closes[-2]
    range_val = 50.0
    low_14 = signal_close - stoch_k / 100.0 * range_val
    high_14 = low_14 + range_val

    highs = [high_14] * n
    lows = [low_14] * n

    # 음봉: open = signal_close + 1
    opens[-2] = signal_close + 1.0
    opens[-1] = closes[-1] + 1.0

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_df_neutral(n: int = _N) -> pd.DataFrame:
    """중립 DataFrame: flat 가격, stoch_k ≈ 50."""
    closes = [100.0] * n
    range_val = 50.0
    return pd.DataFrame({
        "open": closes[:],
        "close": closes[:],
        "high": [100.0 + range_val / 2] * n,
        "low": [100.0 - range_val / 2] * n,
        "volume": [1000.0] * n,
    })


class TestTripleScreenStrategy:

    def setup_method(self):
        self.strategy = TripleScreenStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "triple_screen"

    # 2. 데이터 부족 (< 30행)
    def test_insufficient_data(self):
        df = _make_df_neutral(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 정확히 30행 경계 처리
    def test_exactly_min_rows(self):
        df = _make_df_neutral(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. HOLD: 중립 (flat 가격, stoch_k=50)
    def test_hold_neutral(self):
        df = _make_df_neutral(n=_N)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "triple_screen"

    # 5. BUY: 세 화면 모두 통과
    def test_buy_all_three_screens(self):
        df = _make_df_buy(stoch_k=20.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "triple_screen"
        assert sig.entry_price > 0

    # 6. BUY confidence HIGH: stoch_k < 20
    def test_buy_high_confidence_stoch_below_20(self):
        df = _make_df_buy(stoch_k=10.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. BUY confidence MEDIUM: 20 <= stoch_k < 30
    def test_buy_medium_confidence_stoch_20_30(self):
        df = _make_df_buy(stoch_k=25.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 8. SELL: 세 화면 모두 통과
    def test_sell_all_three_screens(self):
        df = _make_df_sell(stoch_k=80.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "triple_screen"
        assert sig.entry_price > 0

    # 9. SELL confidence HIGH: stoch_k > 80
    def test_sell_high_confidence_stoch_above_80(self):
        df = _make_df_sell(stoch_k=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 10. SELL confidence MEDIUM: 70 < stoch_k <= 80
    def test_sell_medium_confidence_stoch_70_80(self):
        df = _make_df_sell(stoch_k=75.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 11. HOLD: Screen1(bullish) + Screen2(stoch<30) + Screen3 실패(음봉)
    def test_hold_buy_missing_screen3_bearish_candle(self):
        df = _make_df_buy(stoch_k=20.0)
        df = df.copy()
        # 신호 봉을 음봉으로 변경
        df.iloc[-2, df.columns.get_loc("open")] = df.iloc[-2]["close"] + 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. HOLD: Screen1(bearish) + Screen2(stoch>70) + Screen3 실패(양봉)
    def test_hold_sell_missing_screen3_bull_candle(self):
        df = _make_df_sell(stoch_k=80.0)
        df = df.copy()
        # 신호 봉을 양봉으로 변경
        df.iloc[-2, df.columns.get_loc("open")] = df.iloc[-2]["close"] - 1.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df_neutral(n=_N)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 14. entry_price 양수
    def test_entry_price_positive(self):
        df = _make_df_neutral(n=_N)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 15. 큰 데이터셋 처리 (안정성)
    def test_large_dataset(self):
        df = _make_df_buy(stoch_k=20.0, n=200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
