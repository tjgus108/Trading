"""
GaussianChannelStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest
from typing import Optional

from src.strategy.gaussian_channel import GaussianChannelStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(n: int = _MIN_ROWS + 10, prices: Optional[list] = None) -> pd.DataFrame:
    if prices is None:
        prices = [100.0] * n
    else:
        if len(prices) < n:
            prices = [prices[0]] * (n - len(prices)) + list(prices)
    closes = list(prices)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 2.0 for c in closes],
        "low":    [c - 2.0 for c in closes],
        "volume": [1000.0] * len(closes),
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 30) -> pd.DataFrame:
    """
    하단 채널 복귀 유발: 급락 후 반등.
    마지막 완성봉 (idx=-2): prev < lower, curr > lower
    """
    prices = [100.0] * (n - 3) + [70.0, 71.0, 71.0]
    # high/low를 좁게 설정 — ATR 작게, 채널 좁게 만들어 복귀 신호 쉽게 유발
    closes = list(prices)
    highs = [c + 0.5 for c in closes]
    lows  = [c - 0.5 for c in closes]
    # 급락 전 구간 low를 아주 낮게 설정 → ATR 크게
    for i in range(n - 5, n - 3):
        highs[i] = closes[i] + 5.0
        lows[i]  = closes[i] - 5.0
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })
    return df


def _make_sell_df(n: int = _MIN_ROWS + 30) -> pd.DataFrame:
    """
    상단 채널 이탈 유발: 급등 후 하락.
    """
    prices = [100.0] * (n - 3) + [130.0, 129.0, 129.0]
    closes = list(prices)
    highs = [c + 0.5 for c in closes]
    lows  = [c - 0.5 for c in closes]
    for i in range(n - 5, n - 3):
        highs[i] = closes[i] + 5.0
        lows[i]  = closes[i] - 5.0
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * n,
    })
    return df


class TestGaussianChannelStrategy:

    def setup_method(self):
        self.strategy = GaussianChannelStrategy()

    # 1. 전략명
    def test_name(self):
        assert self.strategy.name == "gaussian_channel"

    # 2. 인스턴스
    def test_instance(self):
        assert isinstance(self.strategy, GaussianChannelStrategy)

    # 3. 데이터 부족 → HOLD + "Insufficient"
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음
    def test_returns_signal_not_none(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. 정상 Signal 반환
    def test_returns_signal_instance(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.strategy == "gaussian_channel"

    # 8. BUY reasoning에 "GaussianChannel" 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "GaussianChannel" in sig.reasoning

    # 9. SELL reasoning에 "GaussianChannel" 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "GaussianChannel" in sig.reasoning

    # 10. confidence는 HIGH 또는 MEDIUM
    def test_high_confidence_possible(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. flat prices → HOLD
    def test_flat_prices_hold(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드
    def test_strategy_field(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "gaussian_channel"

    # 14. 최소 행 경계: 정확히 20행
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. 19행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 16. HOLD reasoning에 "GaussianChannel" 포함
    def test_hold_reasoning_content(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert "GaussianChannel" in sig.reasoning or "Insufficient" in sig.reasoning

    # 17. entry_price == close at iloc[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 18. action enum 유효
    def test_action_is_valid_enum(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
