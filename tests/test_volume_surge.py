"""
VolumeSurgeStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_surge import VolumeSurgeStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 30,
    close: float = 110.0,
    open_: float = 99.0,
    volume: float = 1000.0,
    avg_volume: float = 300.0,
) -> pd.DataFrame:
    """
    신호 봉 = index -2. 앞 n-2개 봉의 volume = avg_volume.
    close 값은 모두 동일하게 설정해 고점/저점 경계 테스트용 별도 helper 사용.
    """
    volumes = [avg_volume] * n
    closes = [100.0] * n
    opens = [99.0] * n

    # 신호 봉
    volumes[-2] = volume
    closes[-2] = close
    opens[-2] = open_

    df = pd.DataFrame({"open": opens, "close": closes, "volume": volumes})
    return df


def _make_breakout_df(
    n: int = 30,
    signal_close: float = 110.0,
    signal_open: float = 99.0,
    signal_volume: float = 1000.0,
    avg_volume: float = 300.0,
    base_close: float = 100.0,
) -> pd.DataFrame:
    """고점 돌파 테스트용: base_close로 이전 봉들을 설정."""
    volumes = [avg_volume] * n
    closes = [base_close] * n
    opens = [base_close - 1.0] * n

    volumes[-2] = signal_volume
    closes[-2] = signal_close
    opens[-2] = signal_open

    df = pd.DataFrame({"open": opens, "close": closes, "volume": volumes})
    return df


class TestVolumeSurgeStrategy:

    def setup_method(self):
        self.strategy = VolumeSurgeStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volume_surge"

    # 2. BUY 신호: surge + 양봉 + 20봉 고점 돌파
    def test_buy_signal(self):
        df = _make_breakout_df(
            signal_close=110.0, signal_open=99.0,
            signal_volume=900.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.BUY
        assert sig.strategy == "volume_surge"
        assert sig.entry_price == 110.0

    # 3. BUY HIGH confidence: vol_ratio > 4.0
    def test_buy_high_confidence(self):
        df = _make_breakout_df(
            signal_close=110.0, signal_open=99.0,
            signal_volume=1300.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 4. BUY MEDIUM confidence: 2.5 < vol_ratio <= 4.0
    def test_buy_medium_confidence(self):
        df = _make_breakout_df(
            signal_close=110.0, signal_open=99.0,
            signal_volume=900.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 5. SELL 신호: surge + 음봉 + 20봉 저점 붕괴
    def test_sell_signal(self):
        # base_close=100, signal_close=80 (저점 붕괴), signal_open=99 (음봉)
        df = _make_breakout_df(
            signal_close=80.0, signal_open=99.0,
            signal_volume=900.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == 80.0

    # 6. SELL HIGH confidence
    def test_sell_high_confidence(self):
        df = _make_breakout_df(
            signal_close=80.0, signal_open=99.0,
            signal_volume=1300.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. HOLD: surge 없음 (vol_ratio < 2.5)
    def test_hold_no_surge(self):
        df = _make_breakout_df(
            signal_close=110.0, signal_open=99.0,
            signal_volume=600.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. HOLD: surge 있지만 고점 미돌파 (close <= high_20)
    def test_hold_bull_no_breakout(self):
        # signal_close=99 (이전 봉들 100과 같거나 낮음 — 고점 돌파 안됨)
        df = _make_breakout_df(
            signal_close=99.0, signal_open=95.0,
            signal_volume=900.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: surge 있지만 저점 미붕괴 (음봉인데 close >= low_20)
    def test_hold_bear_no_breakdown(self):
        # signal_close=101 > base_close=100, 음봉이지만 저점 붕괴 안됨
        df = _make_breakout_df(
            signal_close=101.0, signal_open=110.0,
            signal_volume=900.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. 데이터 부족 (< 25행)
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 11. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_breakout_df(
            signal_close=110.0, signal_open=99.0,
            signal_volume=900.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 12. HOLD 신호의 entry_price = _last(df)["close"]
    def test_hold_entry_price(self):
        df = _make_df(n=30, volume=100.0, avg_volume=300.0)  # no surge
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 13. vol_ratio 경계값: 정확히 2.5배는 HOLD
    def test_vol_ratio_boundary_hold(self):
        # vol_ratio = 2.5 정확히 → surge 조건 미충족 (> 2.5 필요)
        df = _make_breakout_df(
            signal_close=110.0, signal_open=99.0,
            signal_volume=750.0, avg_volume=300.0, base_close=100.0
        )
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
