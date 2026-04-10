"""
EMAFanStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import numpy as np
import pytest
from typing import Optional

from src.strategy.ema_fan import EMAFanStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 55


def _make_df(closes, volumes=None) -> pd.DataFrame:
    n = len(closes)
    if volumes is None:
        volumes = [1000.0] * n
    opens = [c * 0.999 for c in closes]
    highs = [c * 1.001 for c in closes]
    lows = [c * 0.999 for c in closes]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": closes,
        "atr14": [1.0] * n,
    })


def _make_bullish_fan_df(n: int = _MIN_ROWS + 5, expanding: bool = True) -> pd.DataFrame:
    """
    ema5 > ema10 > ema20 > ema50이 되도록 강한 상승 추세 설계.
    expanding=True: fan_spread > fan_spread_ma
    """
    # 강한 상승 추세: 선형 증가 후 가속
    base = 100.0
    if expanding:
        # 가속 상승으로 팬 확대
        closes = [base + i * 0.5 + (i / n) ** 2 * 30 for i in range(n)]
    else:
        # 완만한 상승 (팬 형성되지만 확대 없음) — 최근 봉을 flat으로
        closes = [base + i * 0.3 for i in range(n)]
        # 최근 10봉을 flat으로 만들어 fan_spread < fan_spread_ma
        for i in range(n - 12, n):
            closes[i] = closes[n - 13]
    return _make_df(closes)


def _make_bearish_fan_df(n: int = _MIN_ROWS + 5, expanding: bool = True) -> pd.DataFrame:
    """
    ema5 < ema10 < ema20 < ema50이 되도록 강한 하락 추세 설계.
    """
    base = 200.0
    if expanding:
        closes = [base - i * 0.5 - (i / n) ** 2 * 30 for i in range(n)]
    else:
        closes = [base - i * 0.3 for i in range(n)]
        for i in range(n - 12, n):
            closes[i] = closes[n - 13]
    return _make_df(closes)


class TestEMAFanStrategy:

    def setup_method(self):
        self.strategy = EMAFanStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "ema_fan"

    # 2. BUY 신호 (bullish fan + expanding)
    def test_buy_signal_bullish_fan(self):
        df = _make_bullish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 3. BUY strategy 이름 확인
    def test_buy_strategy_name(self):
        df = _make_bullish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.strategy == "ema_fan"

    # 4. SELL 신호 (bearish fan + expanding)
    def test_sell_signal_bearish_fan(self):
        df = _make_bearish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 5. SELL strategy 이름 확인
    def test_sell_strategy_name(self):
        df = _make_bearish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.strategy == "ema_fan"

    # 6. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        closes = [100.0 + i for i in range(40)]
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 7. HOLD: flat 시장 (EMA 정렬 없음)
    def test_hold_flat_market(self):
        closes = [100.0] * (_MIN_ROWS + 5)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. Signal 필드 완전성 (BUY)
    def test_buy_signal_fields_complete(self):
        df = _make_bullish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "ema_fan"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 9. Signal 필드 완전성 (SELL)
    def test_sell_signal_fields_complete(self):
        df = _make_bearish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert isinstance(sig.entry_price, float)

    # 10. BUY reasoning에 팬 정보 포함
    def test_buy_reasoning_contains_fan_info(self):
        df = _make_bullish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "BUY" in sig.reasoning

    # 11. SELL reasoning에 팬 정보 포함
    def test_sell_reasoning_contains_fan_info(self):
        df = _make_bearish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "SELL" in sig.reasoning

    # 12. entry_price는 마지막 완성 캔들의 close
    def test_entry_price_is_last_close(self):
        df = _make_bullish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[len(df) - 2])
        assert sig.entry_price == pytest.approx(expected_close)

    # 13. BUY confidence는 MEDIUM 또는 HIGH
    def test_buy_confidence_is_medium_or_high(self):
        df = _make_bullish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 14. SELL confidence는 MEDIUM 또는 HIGH
    def test_sell_confidence_is_medium_or_high(self):
        df = _make_bearish_fan_df(expanding=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 15. HOLD confidence는 LOW
    def test_hold_confidence_is_low(self):
        closes = [100.0] * (_MIN_ROWS + 5)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
