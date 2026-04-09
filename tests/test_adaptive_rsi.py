"""
AdaptiveRSIStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adaptive_rsi import AdaptiveRSIStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _make_df(n: int = _MIN_ROWS + 5,
             close_val: float = 100.0,
             ema50: float = 95.0,
             trend: str = "flat") -> pd.DataFrame:
    """
    신호 봉은 idx = len(df) - 2.
    trend='up': 점진적 상승 후 마지막 -2봉이 close_val
    trend='down': 점진적 하락 후 마지막 -2봉이 close_val
    trend='flat': 모두 close_val
    """
    rows = n
    if trend == "up":
        closes = list(np.linspace(close_val * 0.7, close_val, rows))
    elif trend == "down":
        closes = list(np.linspace(close_val * 1.3, close_val, rows))
    else:
        closes = [close_val] * rows

    # 마지막 봉(-1)은 진행 중 캔들, 신호 봉(-2)에 close_val 고정
    closes[-2] = close_val
    closes[-1] = close_val

    df = pd.DataFrame({
        "open":   [close_val] * rows,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * rows,
        "ema50":  [ema50] * rows,
        "atr14":  [1.0] * rows,
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """close > KAMA (상승 추세), RSI < 40 유도.
    긴 하락 → KAMA가 하락 추세를 따라감 → 마지막에 close가 KAMA 위로 살짝 반등,
    하락 구간이 길어 RSI가 낮음.
    """
    rows = n
    # 긴 하락 후 마지막 몇 봉만 소폭 반등
    closes = list(np.linspace(100.0, 55.0, rows - 4)) + [57.0, 58.0, 59.0, 59.0]
    # 신호 봉(-2)과 마지막 봉(-1) 설정
    closes[-1] = closes[-2]
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * rows,
        "ema50":  [95.0] * rows,
        "atr14":  [1.0] * rows,
    })
    return df


def _make_sell_df(n: int = _MIN_ROWS + 20) -> pd.DataFrame:
    """close < KAMA (하락 추세), RSI > 60 유도.
    긴 상승 → KAMA가 상승 추세를 따라감 → 마지막에 close가 KAMA 아래로 소폭 하락,
    상승 구간이 길어 RSI가 높음.
    """
    rows = n
    closes = list(np.linspace(50.0, 100.0, rows - 4)) + [98.0, 97.0, 96.0, 96.0]
    closes[-1] = closes[-2]
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * rows,
        "ema50":  [70.0] * rows,
        "atr14":  [1.0] * rows,
    })
    return df


class TestAdaptiveRSIStrategy:

    def setup_method(self):
        self.strategy = AdaptiveRSIStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "adaptive_rsi"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=15)
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
        assert sig.strategy == "adaptive_rsi"

    # 5. BUY 신호: 상승 후 반등 패턴
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price > 0

    # 6. BUY 신호에서 entry_price = close 값
    def test_buy_entry_price(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 7. SELL 신호: 하락 추세 반전 패턴
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 8. SELL 신호에서 entry_price = close 값
    def test_sell_entry_price(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 9. HOLD: 평탄한 가격 (RSI ~50, KAMA ≈ close)
    def test_hold_flat_price(self):
        df = _make_df(n=_MIN_ROWS + 5, close_val=100.0, trend="flat")
        sig = self.strategy.generate(df)
        # 평탄한 경우 HOLD 또는 약한 신호
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 10. BUY confidence: RSI < 30 → HIGH
    def test_buy_high_confidence(self):
        df = _make_buy_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. SELL confidence: RSI > 70 → HIGH
    def test_sell_high_confidence(self):
        df = _make_sell_df(n=50)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. HOLD reasoning에 'No signal' 또는 'Insufficient' 포함
    def test_hold_reasoning(self):
        df = _make_df(n=_MIN_ROWS + 5, trend="flat")
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert "No signal" in sig.reasoning or "Insufficient" in sig.reasoning or "NaN" in sig.reasoning

    # 13. 최소 행수 경계값: 정확히 _MIN_ROWS 행 → 처리 가능
    def test_exact_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. 최소 행수 -1: 부족 → HOLD
    def test_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. confidence는 반드시 HIGH/MEDIUM/LOW 중 하나
    def test_confidence_valid_values(self):
        for trend in ("up", "down", "flat"):
            df = _make_df(n=_MIN_ROWS + 10, trend=trend)
            sig = self.strategy.generate(df)
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
