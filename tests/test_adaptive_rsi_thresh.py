"""
AdaptiveRSIThresholdStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_rsi_thresh import AdaptiveRSIThresholdStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(closes, highs=None, lows=None) -> pd.DataFrame:
    n = len(closes)
    if highs is None:
        highs = [c + 1.0 for c in closes]
    if lows is None:
        lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })


def _make_flat_df(n: int = _MIN_ROWS + 5, val: float = 100.0) -> pd.DataFrame:
    return _make_df([val] * n)


def _make_oversold_trending_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """Trending market (ADX > 25) + RSI < 40 + RSI rising → BUY."""
    # 강한 상승 추세 후 잠깐 하락(RSI 낮아짐), 신호 봉에서 RSI 반등
    closes = list(np.linspace(50.0, 100.0, n - 6))
    # 급락 구간 추가 → RSI 낮아짐
    closes += [95.0, 88.0, 82.0, 76.0, 75.0, 76.5]
    closes[-1] = closes[-2]
    highs = [c + 2.0 for c in closes]
    lows = [c - 2.0 for c in closes]
    return _make_df(closes, highs, lows)


def _make_overbought_trending_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """Trending market (ADX > 25) + RSI > 60 + RSI falling → SELL."""
    closes = list(np.linspace(100.0, 50.0, n - 6))
    # 급등 구간 추가 → RSI 높아짐
    closes += [55.0, 62.0, 68.0, 74.0, 75.0, 73.5]
    closes[-1] = closes[-2]
    highs = [c + 2.0 for c in closes]
    lows = [c - 2.0 for c in closes]
    return _make_df(closes, highs, lows)


def _make_range_buy_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """Range market (ADX <= 25) + RSI < 30 + RSI rising → BUY."""
    # 사이드웨이 + 급락으로 RSI 매우 낮게
    closes = []
    for i in range(n - 6):
        closes.append(100.0 + 1.0 * np.sin(i * 0.3))
    closes += [98.0, 90.0, 82.0, 75.0, 74.0, 75.5]
    closes[-1] = closes[-2]
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    return _make_df(closes, highs, lows)


class TestAdaptiveRSIThresholdStrategy:

    def setup_method(self):
        self.strategy = AdaptiveRSIThresholdStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "adaptive_rsi_thresh"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_flat_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 4. strategy 필드 값
    def test_strategy_field(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.strategy == "adaptive_rsi_thresh"

    # 5. 최소 행수 경계값
    def test_exact_min_rows(self):
        df = _make_flat_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. 최소 행수 미만 → HOLD
    def test_below_min_rows(self):
        df = _make_flat_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 7. confidence 유효값
    def test_confidence_valid_values(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 9. entry_price = close at idx -2
    def test_entry_price_equals_close(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 10. 평탄한 가격 → HOLD (RSI ~50)
    def test_flat_price_hold(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        # RSI ~50이므로 임계값 초과 안 함 → HOLD
        assert sig.action == Action.HOLD

    # 11. HOLD reasoning 내용 확인
    def test_hold_reasoning_content(self):
        df = _make_flat_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert any(kw in sig.reasoning for kw in ("No signal", "Insufficient", "NaN"))

    # 12. trending BUY 신호 (not SELL)
    def test_trending_buy_not_sell(self):
        df = _make_oversold_trending_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 13. trending SELL 신호 (not BUY)
    def test_trending_sell_not_buy(self):
        df = _make_overbought_trending_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 14. BUY reasoning에 'BUY' 포함
    def test_buy_reasoning_content(self):
        df = _make_oversold_trending_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 15. SELL reasoning에 'SELL' 포함
    def test_sell_reasoning_content(self):
        df = _make_overbought_trending_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 16. Range market buy 신호
    def test_range_buy_signal(self):
        df = _make_range_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 17. action은 BUY/SELL/HOLD 중 하나
    def test_action_valid_values(self):
        for n in [_MIN_ROWS, _MIN_ROWS + 10, _MIN_ROWS + 30]:
            df = _make_flat_df(n=n)
            sig = self.strategy.generate(df)
            assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
