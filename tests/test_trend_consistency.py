"""
TrendConsistencyStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_consistency import TrendConsistencyStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_bullish_df(n: int = _MIN_ROWS + 2) -> pd.DataFrame:
    """완전한 상승 정렬: close > ema5 > ema10 > ema20, 마지막 봉 상승."""
    # 단조 증가 close → EMA들도 close < ema_fast 순서가 됨을 피하기 위해
    # 점진적으로 증가하여 ema5 > ema10 > ema20 유지
    closes = [100.0 + i * 2.0 for i in range(n)]
    # 마지막 완성 캔들(-2)이 이전(-3)보다 높도록
    closes[-2] = closes[-3] + 1.0
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_bearish_df(n: int = _MIN_ROWS + 2) -> pd.DataFrame:
    """완전한 하락 정렬: close < ema5 < ema10 < ema20, 마지막 봉 하락."""
    closes = [200.0 - i * 2.0 for i in range(n)]
    closes[-2] = closes[-3] - 1.0
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_flat_df(n: int = _MIN_ROWS + 2) -> pd.DataFrame:
    """횡보: close ≈ ema5 ≈ ema10 ≈ ema20."""
    closes = [100.0] * n
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


class TestTrendConsistencyStrategy:

    def setup_method(self):
        self.strategy = TrendConsistencyStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "trend_consistency"

    # 2. Signal 반환 타입 확인
    def test_returns_signal(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 3. BUY 신호: 완전 상승 정렬
    def test_buy_signal_full_bull(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 4. BUY 전략명 확인
    def test_buy_strategy_name(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "trend_consistency"

    # 5. BUY HIGH confidence (bull_count == 3)
    def test_buy_high_confidence(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 6. SELL 신호: 완전 하락 정렬
    def test_sell_signal_full_bear(self):
        df = _make_bearish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 7. SELL 전략명 확인
    def test_sell_strategy_name(self):
        df = _make_bearish_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "trend_consistency"

    # 8. SELL HIGH confidence (bear_count == 3)
    def test_sell_high_confidence(self):
        df = _make_bearish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 9. HOLD: 횡보 시
    def test_hold_flat(self):
        df = _make_flat_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. 데이터 부족 시 HOLD
    def test_insufficient_data_hold(self):
        df = _make_flat_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. 데이터 부족 시 LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_flat_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 12. entry_price == close 마지막 완성 캔들
    def test_entry_price_is_last_close(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 13. BUY 시 상승 확인 조건: prev_close >= close → HOLD
    def test_no_buy_if_price_not_rising(self):
        df = _make_bullish_df()
        # 마지막 완성 캔들(-2) close를 이전(-3)보다 낮게 설정
        closes = list(df["close"])
        closes[-2] = closes[-3] - 0.5
        df["close"] = closes
        sig = self.strategy.generate(df)
        # bull_count==3 이지만 close < prev_close → HOLD
        assert sig.action != Action.BUY

    # 14. SELL 시 하락 확인 조건: prev_close <= close → HOLD
    def test_no_sell_if_price_not_falling(self):
        df = _make_bearish_df()
        closes = list(df["close"])
        closes[-2] = closes[-3] + 0.5
        df["close"] = closes
        sig = self.strategy.generate(df)
        assert sig.action != Action.SELL

    # 15. reasoning 문자열 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 16. 정확히 MIN_ROWS 행에서 작동
    def test_exactly_min_rows(self):
        df = _make_bullish_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
