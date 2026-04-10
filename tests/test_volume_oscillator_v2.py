"""
VolumeOscillatorV2Strategy 단위 테스트 (mock DataFrame, API 호출 없음).
"""

import pandas as pd
import numpy as np
import pytest
from typing import Optional

from src.strategy.volume_oscillator_v2 import VolumeOscillatorV2Strategy
from src.strategy.base import Action, Confidence, Signal

_N = 40  # 최소 20행 초과


def _make_df(
    n: int = _N,
    base_close: float = 100.0,
    price_up: bool = True,
    high_vol_spike: bool = True,  # vol_osc > 0 AND > vol_osc_ma
) -> pd.DataFrame:
    """
    vol_osc > 0 AND vol_osc > vol_osc_ma を作るには:
    - 앞부분: slow volume (vol_osc ≈ 0)
    - 마지막 1~2개 candle만 매우 높은 volume (fast EWM 급등 → vol_osc 급등)
    - vol_osc_ma(5) < vol_osc_now 보장

    price_up=True → closes[-2] > closes[-3]
    price_up=False → closes[-2] < closes[-3]
    """
    # base volume for most candles
    base_vol = 1000.0
    spike_vol = 50000.0  # 매우 큰 spike → fast EWM >>> slow EWM

    volumes = [base_vol] * n
    closes = [base_close] * n
    highs = [base_close * 1.001] * n
    lows = [base_close * 0.999] * n
    opens = [base_close] * n

    if high_vol_spike:
        # Only the last completed candle (idx=-2) has a spike
        # This ensures vol_osc at idx is much higher than vol_osc_ma(5) of prev candles
        volumes[-2] = spike_vol
        volumes[-1] = spike_vol  # current candle (ignored)
    else:
        # flat volume → vol_osc ≈ 0
        pass

    # price direction at idx=-2
    prev_close = base_close
    if price_up:
        last_close = base_close + 1.0
    else:
        last_close = base_close - 1.0

    closes[-3] = prev_close
    closes[-2] = last_close
    closes[-1] = last_close
    opens[-2] = prev_close
    highs[-2] = max(last_close, base_close) * 1.001
    lows[-2] = min(last_close, base_close) * 0.999

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


class TestVolumeOscillatorV2Strategy:

    def setup_method(self):
        self.strategy = VolumeOscillatorV2Strategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "volume_oscillator_v2"

    # 2. 데이터 부족 (< 20행) → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "데이터 부족" in sig.reasoning

    # 3. 정확히 20행 → Signal 반환
    def test_exactly_min_rows(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. BUY: vol_osc > 0, > vol_osc_ma, price_up
    def test_buy_signal(self):
        df = _make_df(n=_N, base_close=100.0, price_up=True, high_vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "volume_oscillator_v2"
        assert sig.entry_price > 0

    # 5. SELL: vol_osc > 0, > vol_osc_ma, price_down
    def test_sell_signal(self):
        df = _make_df(n=_N, base_close=100.0, price_up=False, high_vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "volume_oscillator_v2"
        assert sig.entry_price > 0

    # 6. BUY confidence HIGH: vol_osc > 20
    def test_buy_high_confidence(self):
        # spike_vol=50000 vs base_vol=1000 → vol_osc >> 20
        df = _make_df(n=_N, base_close=100.0, price_up=True, high_vol_spike=True)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 7. SELL confidence HIGH: vol_osc > 20
    def test_sell_high_confidence(self):
        df = _make_df(n=_N, base_close=100.0, price_up=False, high_vol_spike=True)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_N)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 9. BUY 신호: invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _make_df(n=_N, price_up=True, high_vol_spike=True)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.invalidation != ""

    # 10. SELL 신호: invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _make_df(n=_N, price_up=False, high_vol_spike=True)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.invalidation != ""

    # 11. entry_price 양수
    def test_entry_price_positive(self):
        df = _make_df(n=_N)
        sig = self.strategy.generate(df)
        assert sig.entry_price >= 0

    # 12. 낮은 볼륨 (vol_osc ≈ 0) → HOLD
    def test_hold_flat_volume(self):
        df = _make_df(n=_N, high_vol_spike=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 13. 큰 데이터셋 안정성
    def test_large_dataset(self):
        df = _make_df(n=200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. None DataFrame → HOLD
    def test_none_dataframe(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 15. BUY에서 strategy 필드 일치
    def test_buy_strategy_field(self):
        df = _make_df(n=_N, price_up=True, high_vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.strategy == "volume_oscillator_v2"

    # 16. SELL에서 strategy 필드 일치
    def test_sell_strategy_field(self):
        df = _make_df(n=_N, price_up=False, high_vol_spike=True)
        sig = self.strategy.generate(df)
        assert sig.strategy == "volume_oscillator_v2"
