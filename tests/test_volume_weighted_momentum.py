"""
VolumeWeightedMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_weighted_momentum import VolumeWeightedMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(
    n: int = _MIN_ROWS + 5,
    price_trend: str = "flat",
    volume_mult: float = 1.0,
) -> pd.DataFrame:
    """
    price_trend: 'up' | 'down' | 'flat'
    """
    if price_trend == "up":
        closes = [100.0 + i * 1.5 for i in range(n)]
    elif price_trend == "down":
        closes = [200.0 - i * 1.5 for i in range(n)]
    else:
        closes = [100.0] * n

    volumes = [1000.0 * volume_mult] * n
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": volumes,
    })


def _make_strong_up_df(n: int = 50) -> pd.DataFrame:
    """강한 상승: vw_momentum > vw_mom_ma > 0 보장.
    초반 flat → 후반 가속 상승으로 window 끝부분에서 momentum이 MA를 항상 초과.
    """
    # 초반 30개 flat, 이후 가속 증가
    flat = [100.0] * 30
    # 가속 상승: 각 스텝 증분이 커져서 마지막에 returns 급등
    rising = []
    base = 100.0
    for i in range(n - 30):
        base += (i + 1) * 0.5
        rising.append(base)
    closes = flat + rising
    volumes = [1000.0] * len(closes)
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": volumes,
    })


def _make_strong_down_df(n: int = 50) -> pd.DataFrame:
    """강한 하락: vw_momentum < vw_mom_ma < 0 보장."""
    flat = [200.0] * 30
    falling = []
    base = 200.0
    for i in range(n - 30):
        base -= (i + 1) * 0.5
        falling.append(base)
    closes = flat + falling
    volumes = [1000.0] * len(closes)
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "volume": volumes,
    })


class TestVolumeWeightedMomentumStrategy:

    def setup_method(self):
        self.strategy = VolumeWeightedMomentumStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "volume_weighted_momentum"

    # 2. Signal 반환 타입 확인
    def test_returns_signal(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 3. BUY 신호: 강한 상승 추세
    def test_buy_signal_strong_up(self):
        df = _make_strong_up_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 4. BUY 전략명 확인
    def test_buy_strategy_name(self):
        df = _make_strong_up_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "volume_weighted_momentum"

    # 5. SELL 신호: 강한 하락 추세
    def test_sell_signal_strong_down(self):
        df = _make_strong_down_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 6. SELL 전략명 확인
    def test_sell_strategy_name(self):
        df = _make_strong_down_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "volume_weighted_momentum"

    # 7. HOLD: 횡보 시
    def test_hold_flat(self):
        df = _make_df(price_trend="flat")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. 데이터 부족 시 HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. 데이터 부족 시 LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 10. entry_price == close 마지막 완성 캔들
    def test_entry_price_is_last_close(self):
        df = _make_strong_up_df()
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 11. BUY confidence: HIGH or MEDIUM
    def test_buy_confidence_valid(self):
        df = _make_strong_up_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. SELL confidence: HIGH or MEDIUM
    def test_sell_confidence_valid(self):
        df = _make_strong_down_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_strong_up_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 14. 정확히 MIN_ROWS 행에서 작동
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. 높은 거래량 → 모멘텀 강화 (BUY 유지)
    def test_high_volume_buy(self):
        df = _make_strong_up_df()
        # 전체 거래량 10배
        df["volume"] = df["volume"] * 10
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 16. bull_case / bear_case 문자열 포함
    def test_bull_bear_case_strings(self):
        df = _make_strong_up_df()
        sig = self.strategy.generate(df)
        assert "vw_momentum" in sig.bull_case
        assert "vw_momentum" in sig.bear_case
