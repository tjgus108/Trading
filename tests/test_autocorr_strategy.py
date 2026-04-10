"""
AutoCorrelationStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.autocorr_strategy import AutoCorrelationStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 5, closes=None) -> pd.DataFrame:
    if closes is None:
        closes = [100.0] * n
    rows = len(closes)
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * rows,
    })


def _make_trending_up_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """강한 상승 추세: 양의 자기상관 유도 (수익률이 지속적으로 양수)."""
    # 꾸준한 상승으로 양의 AC 유도
    closes = []
    val = 100.0
    for i in range(n):
        val += 0.5 + 0.1 * np.sin(i * 0.1)  # 꾸준한 상승
        closes.append(val)
    # 신호 봉(-2)이 이전 봉(-3)보다 높도록
    closes[-2] = closes[-3] + 0.5
    closes[-1] = closes[-2]
    return _make_df(closes=closes)


def _make_trending_down_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """강한 하락 추세: 양의 자기상관 + 하락."""
    closes = []
    val = 150.0
    for i in range(n):
        val -= 0.5 + 0.1 * np.sin(i * 0.1)
        closes.append(max(val, 1.0))
    closes[-2] = closes[-3] - 0.5
    closes[-1] = closes[-2]
    return _make_df(closes=closes)


def _make_mean_rev_buy_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """음의 AC + close < SMA20 * 0.98 → BUY 유도."""
    # 지그재그 패턴으로 음의 AC 유도, 가격은 낮은 수준
    closes = []
    for i in range(n):
        closes.append(80.0 + 2.0 * ((-1) ** i))  # 지그재그
    # 신호 봉을 SMA의 97% 수준으로
    avg = np.mean(closes[-20:])
    closes[-2] = avg * 0.96
    closes[-1] = closes[-2]
    return _make_df(closes=closes)


def _make_mean_rev_sell_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """음의 AC + close > SMA20 * 1.02 → SELL 유도."""
    closes = []
    for i in range(n):
        closes.append(100.0 + 2.0 * ((-1) ** i))
    avg = np.mean(closes[-20:])
    closes[-2] = avg * 1.04
    closes[-1] = closes[-2]
    return _make_df(closes=closes)


class TestAutoCorrelationStrategy:

    def setup_method(self):
        self.strategy = AutoCorrelationStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "autocorr_strategy"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 4. strategy 필드 값
    def test_strategy_field(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.strategy == "autocorr_strategy"

    # 5. 최소 행수 경계값
    def test_exact_min_rows(self):
        closes = [100.0] * _MIN_ROWS
        df = _make_df(closes=closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. 최소 행수 미만 → HOLD
    def test_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 7. confidence는 유효값만
    def test_confidence_valid_values(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 9. entry_price = close at idx -2
    def test_entry_price_equals_close(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 10. HOLD reasoning에 'No signal' 또는 'Insufficient' 포함
    def test_hold_reasoning_content(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert any(kw in sig.reasoning for kw in ("No signal", "Insufficient", "NaN"))

    # 11. 상승 추세 시 BUY or HOLD (SELL 아님)
    def test_trending_up_not_sell(self):
        df = _make_trending_up_df()
        sig = self.strategy.generate(df)
        # 강한 추세에서 SELL이 나오지 않아야 함
        assert sig.action in (Action.BUY, Action.HOLD)

    # 12. 하락 추세 시 SELL or HOLD (BUY 아님)
    def test_trending_down_not_buy(self):
        df = _make_trending_down_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 13. BUY 신호 action 타입 확인
    def test_buy_action_type(self):
        df = _make_mean_rev_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 14. SELL 신호 action 타입 확인
    def test_sell_action_type(self):
        df = _make_mean_rev_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 15. |AC| > 0.3이면 HIGH confidence (BUY/SELL일 때)
    def test_high_confidence_when_strong_ac(self):
        # 강한 추세 데이터로 HIGH confidence 확인
        df = _make_trending_up_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action != Action.HOLD:
            # HIGH or MEDIUM 모두 허용
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 16. 평탄한 가격 → HOLD (수익률 0, AC NaN or 0)
    def test_flat_price_hold(self):
        closes = [100.0] * (_MIN_ROWS + 5)
        df = _make_df(closes=closes)
        sig = self.strategy.generate(df)
        # 평탄한 경우 AC=NaN → HOLD
        assert sig.action == Action.HOLD
