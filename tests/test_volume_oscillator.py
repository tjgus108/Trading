"""
VolumeOscillatorStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_oscillator import VolumeOscillatorStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0, ema50: float = 98.0,
             vol_spike: bool = False, high_spike: bool = False) -> pd.DataFrame:
    """
    신호 봉 = index -2.
    vol_spike=True: VO > 5 트리거용 높은 볼륨.
    high_spike=True: VO > 20 트리거용 매우 높은 볼륨.
    """
    base_vol = 1000.0
    volumes = [base_vol] * n

    if high_spike:
        # ema5 >> ema20 이 되도록 앞 볼륨 낮게, 뒤 볼륨 매우 높게
        for i in range(n - 5, n - 1):
            volumes[i] = base_vol * 30
    elif vol_spike:
        for i in range(n - 5, n - 1):
            volumes[i] = base_vol * 8

    df = pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close * 1.01] * n,
        "low": [close * 0.99] * n,
        "volume": volumes,
        "ema50": [ema50] * n,
        "atr14": [1.0] * n,
    })
    return df


class TestVolumeOscillatorStrategy:

    def setup_method(self):
        self.strategy = VolumeOscillatorStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "volume_oscillator"

    # 2. 데이터 부족 (< 25행) → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. BUY 신호: VO > 5, close > ema50
    def test_buy_signal(self):
        df = _make_df(close=105.0, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "volume_oscillator"
        assert sig.entry_price == 105.0

    # 4. SELL 신호: VO > 5, close < ema50
    def test_sell_signal(self):
        df = _make_df(close=95.0, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "volume_oscillator"
        assert sig.entry_price == 95.0

    # 5. HOLD: VO <= 5 (볼륨 평범)
    def test_hold_normal_volume(self):
        df = _make_df(close=105.0, ema50=100.0, vol_spike=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. BUY HIGH confidence: VO > 20
    def test_buy_high_confidence(self):
        df = _make_df(close=105.0, ema50=100.0, high_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. SELL HIGH confidence: VO > 20
    def test_sell_high_confidence(self):
        df = _make_df(close=95.0, ema50=100.0, high_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. BUY confidence is HIGH or MEDIUM depending on VO magnitude
    def test_buy_confidence_set(self):
        df = _make_df(close=105.0, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(close=105.0, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")
        assert sig.reasoning != ""

    # 10. Signal 반환 타입 확인
    def test_returns_signal_type(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 11. close == ema50 (경계값): HOLD (ema50 동일이면 buy 조건 불충족)
    def test_hold_close_equals_ema50(self):
        df = _make_df(close=100.0, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. reasoning에 VO 값 포함 확인
    def test_reasoning_contains_vo(self):
        df = _make_df(close=105.0, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert "VO=" in sig.reasoning

    # 13. entry_price는 close 값
    def test_entry_price_is_close(self):
        df = _make_df(close=107.5, ema50=100.0, vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(107.5)

    # 14. n=25 최소 행 데이터 정상 작동
    def test_minimum_rows(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
