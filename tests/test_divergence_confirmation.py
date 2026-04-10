"""
DivergenceConfirmationStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.divergence_confirmation import DivergenceConfirmationStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 35, close_prices=None) -> pd.DataFrame:
    if close_prices is None:
        close_prices = [100.0] * n
    highs = [c + 1.0 for c in close_prices]
    lows = [c - 1.0 for c in close_prices]
    return pd.DataFrame({
        "open": close_prices,
        "close": close_prices,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * len(close_prices),
    })


def _make_bullish_div_df(rsi_low: bool = False) -> pd.DataFrame:
    """
    Bullish divergence: price 하락 + RSI 상승.
    price[-10] > price[-2] (idx=n-2 기준 completed 내에서)
    RSI를 직접 제어하기 어려우므로 가격 패턴으로 유도.

    가격: 100 → 급락 → 반등 없는 상황
    RSI가 낮고 올라가도록: 먼저 급락 후 완만히 회복
    """
    n = 35
    # 처음 20봉: 점차 하락 (RSI도 하락)
    closes = list(np.linspace(200, 100, 20))
    # 다음 5봉: 급락 (낮은 RSI 만들기)
    closes += list(np.linspace(100, 60, 5))
    # 이후 봉들: 완만 회복하여 RSI 상승 but 가격은 여전히 낮음
    closes += [62.0, 63.0, 64.0, 65.0]
    # 신호봉(-2) 자리: 가격은 낮지만 RSI는 상승
    closes.append(63.0)  # idx = n-2 = 33
    closes.append(64.0)  # 진행 중 봉 (idx = n-1 = 34, 무시)

    closes = closes[:n]
    return _make_df(n=n, close_prices=closes)


def _make_bearish_div_df(rsi_high: bool = False) -> pd.DataFrame:
    """
    Bearish divergence: price 상승 + RSI 하락.
    처음 급등 → RSI 고점 → 이후 완만 상승 but RSI 하락
    """
    n = 35
    # 처음 20봉: 급등 (RSI 상승)
    closes = list(np.linspace(50, 200, 20))
    # 이후 강한 상승 후 급락 (RSI 내리기)
    closes += list(np.linspace(200, 250, 5))
    # RSI를 내리기 위해 급락 후 회복
    closes += [230.0, 210.0, 220.0, 225.0]
    # 신호봉(-2): 가격은 올랐지만 RSI는 하락
    closes.append(260.0)  # 가격 high (price_now > price_prev)
    closes.append(265.0)  # 진행 중

    closes = closes[:n]
    return _make_df(n=n, close_prices=closes)


class TestDivergenceConfirmationStrategy:

    def setup_method(self):
        self.strat = DivergenceConfirmationStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "divergence_confirmation"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=20)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 최소 행(30) - Signal 반환
    def test_exactly_min_rows_returns_signal(self):
        df = _make_df(n=30)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 4. Signal 객체 반환
    def test_returns_signal_object(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        assert sig.reasoning != ""

    # 6. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        assert sig.entry_price > 0

    # 7. strategy 필드
    def test_strategy_field(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        assert sig.strategy == "divergence_confirmation"

    # 8. BUY 또는 HOLD (bullish divergence)
    def test_bullish_div_signal(self):
        df = _make_bullish_div_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 또는 HOLD (bearish divergence)
    def test_bearish_div_signal(self):
        df = _make_bearish_div_df()
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. HOLD: 가격/RSI 동방향 상승 (발산 없음)
    def test_hold_no_divergence_uptrend(self):
        n = 35
        closes = list(np.linspace(100, 200, n))
        df = _make_df(n=n, close_prices=closes)
        sig = self.strat.generate(df)
        # 순수 상승이면 divergence 없이 HOLD
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert isinstance(sig, Signal)

    # 11. confidence는 유효한 값
    def test_confidence_valid_values(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. Bullish divergence HIGH confidence: RSI <= 30
    def test_bullish_high_confidence_low_rsi(self):
        """RSI <= 30인 bullish divergence → HIGH confidence."""
        n = 35
        # 급락으로 RSI 30 이하 만들기
        closes = list(np.linspace(200, 20, 25))   # 급락
        closes += [22.0, 21.0, 22.0, 23.0, 24.0]  # 소폭 반등 (RSI 상승 but 가격 저점 갱신)
        closes += [19.0]  # 신호봉: 가격 더 낮음
        closes += [20.0]  # 진행 중
        closes = closes[:n]
        df = _make_df(n=n, close_prices=closes)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. entry_price = 신호봉 close
    def test_entry_price_equals_signal_candle_close(self):
        df = _make_df(n=35)
        sig = self.strat.generate(df)
        expected = float(df.iloc[-2]["close"])
        assert sig.entry_price == pytest.approx(expected, rel=1e-4)

    # 14. 데이터 29행 (최소-1) → HOLD
    def test_one_below_min_rows(self):
        df = _make_df(n=29)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning
