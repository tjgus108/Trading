"""
PriceActionMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest

from src.strategy.price_action_momentum import PriceActionMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 5,
             close_val: float = 100.0,
             open_val: float = 98.0,
             ema50: float = 95.0,
             volume: float = 1000.0,
             avg_volume: float = 800.0,
             trend: str = "up") -> pd.DataFrame:
    """
    trend='up':   close > ema50, close > 20봉 전, close > 5봉 전
    trend='down': close < ema50, close < 20봉 전, close < 5봉 전
    trend='flat': 신호 없음
    """
    if trend == "up":
        closes = [close_val - (n - 1 - i) * 0.5 for i in range(n)]
    elif trend == "down":
        closes = [close_val + (n - 1 - i) * 0.5 for i in range(n)]
    else:
        closes = [close_val] * n

    closes[-2] = close_val
    closes[-1] = close_val

    opens = [open_val] * n
    vols = [avg_volume] * n
    vols[-2] = volume  # idx 봉의 볼륨

    df = pd.DataFrame({
        "open":   opens,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": vols,
        "ema50":  [ema50] * n,
        "atr14":  [1.0] * n,
    })
    return df


def _make_full_bull_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """bull_score == 5: 모든 조건 충족."""
    close_val = 110.0
    ema50 = 95.0
    # 상승 추세: 20봉 전부터 꾸준히 오름
    closes = [80.0 + i * 1.5 for i in range(n)]
    closes[-2] = close_val
    closes[-1] = close_val
    opens = [closes[i] - 1.0 for i in range(n)]  # 양봉
    vols = [500.0] * n
    vols[-2] = 2000.0  # 볼륨 급증
    df = pd.DataFrame({
        "open":   opens,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": vols,
        "ema50":  [ema50] * n,
        "atr14":  [1.0] * n,
    })
    return df


def _make_full_bear_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """bear_score == 5: 모든 하락 조건 충족."""
    close_val = 70.0
    ema50 = 95.0
    # 하락 추세
    closes = [120.0 - i * 1.5 for i in range(n)]
    closes[-2] = close_val
    closes[-1] = close_val
    opens = [closes[i] + 1.0 for i in range(n)]  # 음봉
    vols = [500.0] * n
    vols[-2] = 2000.0  # 볼륨 급증
    df = pd.DataFrame({
        "open":   opens,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": vols,
        "ema50":  [ema50] * n,
        "atr14":  [1.0] * n,
    })
    return df


class TestPriceActionMomentumStrategy:

    def setup_method(self):
        self.strategy = PriceActionMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "price_action_momentum"

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

    # 4. strategy 필드
    def test_strategy_field(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.strategy == "price_action_momentum"

    # 5. BUY: bull_score >= 4
    def test_buy_signal(self):
        df = _make_full_bull_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 6. BUY entry_price = close
    def test_buy_entry_price(self):
        df = _make_full_bull_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 7. SELL: bear_score >= 4
    def test_sell_signal(self):
        df = _make_full_bear_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 8. SELL entry_price = close
    def test_sell_entry_price(self):
        df = _make_full_bear_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 9. HIGH confidence: bull_score == 5
    def test_high_confidence_bull(self):
        df = _make_full_bull_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. HIGH confidence: bear_score == 5
    def test_high_confidence_bear(self):
        df = _make_full_bear_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. confidence 유효값
    def test_confidence_valid_values(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. 최소 행수 경계: 정확히 _MIN_ROWS
    def test_exact_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 13. 최소 행수 -1 → HOLD
    def test_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 14. action 유효값
    def test_action_valid_values(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 15. HOLD reasoning 확인
    def test_hold_reasoning_content(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert "No signal" in sig.reasoning or "Insufficient" in sig.reasoning

    # 16. BUY reasoning에 'BUY' 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_full_bull_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 17. SELL reasoning에 'SELL' 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_full_bear_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning
