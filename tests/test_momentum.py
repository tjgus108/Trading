"""
MomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum import MomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 55
_ROC_PERIOD = 20


def _make_df(n: int = _MIN_ROWS + 1,
             close: float = 100.0,
             ema50: float = 95.0,
             prev_close: float = 90.0) -> pd.DataFrame:
    """
    마지막 봉(-2)가 신호 봉 (BaseStrategy._last() 기준).
    roc = (close - prev_close) / prev_close
    prev_close 는 index -2 - 20 = -(22) 위치에 배치.
    """
    rows = n
    closes = [prev_close] * rows
    # index -2 - ROC_PERIOD = -(ROC_PERIOD + 2) 위치에 prev_close 설정
    # 나머지 봉들은 close 값으로 채우되, 마지막 -2 봉은 close
    for i in range(rows):
        closes[i] = prev_close
    # 신호 봉(-2)의 close
    closes[-2] = close
    # prev_close 위치(-2 - 20 = -(22))는 이미 prev_close 값

    df = pd.DataFrame({
        "open": [close] * rows,
        "close": closes,
        "high": [close + 1] * rows,
        "low": [close - 1] * rows,
        "volume": [1000.0] * rows,
        "ema50": [ema50] * rows,
        "atr14": [1.0] * rows,
    })
    return df


class TestMomentumStrategy:

    def setup_method(self):
        self.strategy = MomentumStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "momentum"

    # 2. BUY 신호: roc > 0.03, close > ema50
    def test_buy_signal(self):
        # prev=90, close=95 → roc = 5/90 ≈ 0.0556 > 0.03, ema50=90 < close
        df = _make_df(close=95.0, ema50=90.0, prev_close=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "momentum"
        assert sig.entry_price == 95.0

    # 3. BUY HIGH confidence: |roc| > 0.06
    def test_buy_high_confidence(self):
        # prev=90, close=97 → roc ≈ 0.0778 > 0.06
        df = _make_df(close=97.0, ema50=90.0, prev_close=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 4. BUY MEDIUM confidence: 0.03 < |roc| <= 0.06
    def test_buy_medium_confidence(self):
        # prev=90, close=95 → roc ≈ 0.0556, ema50=90
        df = _make_df(close=95.0, ema50=90.0, prev_close=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 5. SELL 신호: roc < -0.03, close < ema50
    def test_sell_signal(self):
        # prev=100, close=95 → roc = -0.05 < -0.03, ema50=100 > close
        df = _make_df(close=95.0, ema50=100.0, prev_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == 95.0

    # 6. SELL HIGH confidence: roc < -0.06
    def test_sell_high_confidence(self):
        # prev=100, close=93 → roc = -0.07 < -0.06
        df = _make_df(close=93.0, ema50=100.0, prev_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. HOLD: roc > 0.03 but close < ema50 (momentum up, price below ema)
    def test_hold_buy_roc_below_ema(self):
        # prev=90, close=95 → roc > 0.03 but ema50=100 > close
        df = _make_df(close=95.0, ema50=100.0, prev_close=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. HOLD: roc < -0.03 but close > ema50 (momentum down, price above ema)
    def test_hold_sell_roc_above_ema(self):
        # prev=100, close=95 → roc = -0.05 but ema50=90 < close
        df = _make_df(close=95.0, ema50=90.0, prev_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: |roc| <= 0.03 (모멘텀 약함)
    def test_hold_weak_momentum(self):
        # prev=100, close=101 → roc = 0.01 < 0.03
        df = _make_df(close=101.0, ema50=90.0, prev_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 11. Signal 필드 완전성 확인
    def test_signal_fields_complete(self):
        df = _make_df(close=95.0, ema50=90.0, prev_close=90.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")
        assert sig.reasoning != ""
