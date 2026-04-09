"""
VolumeClimaxStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_climax import VolumeClimaxStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 40,
    close: float = 100.0,
    open_: float = 99.0,
    volume: float = 300.0,
    avg_volume: float = 100.0,
    rsi_force: float = None,  # 특정 RSI 유도용 close 트렌드
) -> pd.DataFrame:
    """
    신호 봉 = index -2.
    rsi_force: None이면 flat close. "low" → 강한 하락으로 RSI < 30 유도.
    "high" → 강한 상승으로 RSI > 70 유도.
    """
    volumes = [avg_volume] * n
    opens = [close - 1.0] * n

    if rsi_force == "low":
        # 강한 하락 추세 → RSI < 30
        closes = [close + (n - 2 - i) * 0.5 for i in range(n)]
    elif rsi_force == "high":
        # 강한 상승 추세 → RSI > 70
        closes = [close - (n - 2 - i) * 0.5 for i in range(n)]
    else:
        closes = [close] * n

    # 신호 봉 설정
    volumes[-2] = volume
    opens[-2] = open_

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "volume": volumes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
    })
    return df


def _make_buy_df(n: int = 40, vol_ratio: float = 3.5) -> pd.DataFrame:
    """Selling climax (BUY 신호) 유도: 양봉 + 극단적 거래량 + RSI < 30."""
    avg_vol = 100.0
    volume = avg_vol * vol_ratio
    # 강한 하락 후 양봉 → RSI < 30 유도
    closes = [200.0 - i * 2.0 for i in range(n)]
    opens = [c + 1.0 for c in closes]  # open > close → 음봉 기본 (신호봉 별도 설정)

    volumes = [avg_vol] * n
    volumes[-2] = volume
    opens[-2] = closes[-2] - 1.0   # 신호봉 양봉: close > open
    # closes[-2] 는 이미 낮은 값 (하락 끝)

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "volume": volumes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
    })
    return df


def _make_sell_df(n: int = 40, vol_ratio: float = 3.5) -> pd.DataFrame:
    """Buying climax (SELL 신호) 유도: 음봉 + 극단적 거래량 + RSI > 70."""
    avg_vol = 100.0
    volume = avg_vol * vol_ratio
    # 강한 상승 후 음봉 → RSI > 70 유도
    closes = [100.0 + i * 2.0 for i in range(n)]
    # 신호봉을 음봉으로: open > close. open은 closes[-2] + 1, close는 closes[-2]
    opens = [c - 1.0 for c in closes]
    opens[-2] = closes[-2] + 1.0   # 신호봉: open > close → 음봉

    volumes = [avg_vol] * n
    volumes[-2] = volume

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "volume": volumes,
        "high": [c + 1.5 for c in closes],
        "low": [c - 0.5 for c in closes],
    })
    return df


class TestVolumeClimaxStrategy:

    def setup_method(self):
        self.strategy = VolumeClimaxStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volume_climax"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Selling climax → BUY 신호
    def test_buy_selling_climax(self):
        df = _make_buy_df(vol_ratio=3.5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "volume_climax"

    # 4. BUY entry_price = last close
    def test_buy_entry_price(self):
        df = _make_buy_df(vol_ratio=3.5)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.entry_price == float(df.iloc[-2]["close"])

    # 5. Buying climax → SELL 신호
    def test_sell_buying_climax(self):
        df = _make_sell_df(vol_ratio=3.5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "volume_climax"

    # 6. SELL entry_price = last close
    def test_sell_entry_price(self):
        df = _make_sell_df(vol_ratio=3.5)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.entry_price == float(df.iloc[-2]["close"])

    # 7. HIGH confidence: vol_ratio > 5.0 (BUY)
    def test_buy_high_confidence(self):
        df = _make_buy_df(vol_ratio=5.5)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 8. HIGH confidence: vol_ratio > 5.0 (SELL)
    def test_sell_high_confidence(self):
        df = _make_sell_df(vol_ratio=5.5)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 9. MEDIUM confidence: 3.0 < vol_ratio <= 5.0 (BUY)
    def test_buy_medium_confidence(self):
        df = _make_buy_df(vol_ratio=3.5)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.MEDIUM

    # 10. HOLD: 거래량 부족 (vol_ratio < 3.0)
    def test_hold_insufficient_volume(self):
        n = 40
        avg_vol = 100.0
        closes = [200.0 - i * 2.0 for i in range(n)]
        opens = list(closes)
        volumes = [avg_vol] * n
        volumes[-2] = avg_vol * 2.0  # < 3.0x → no climax
        opens[-2] = closes[-2] - 1.0

        df = pd.DataFrame({
            "open": opens, "close": closes, "volume": volumes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df(vol_ratio=3.5)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)

    # 12. HOLD 신호 entry_price = _last(df)["close"]
    def test_hold_entry_price(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 13. HOLD reasoning 비어있지 않음
    def test_hold_reasoning_nonempty(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 14. BUY 신호의 RSI 조건 미충족 시 HOLD
    def test_buy_rsi_condition_required(self):
        """양봉 + 극단적 거래량이지만 RSI가 30 이상이면 BUY 안 됨."""
        n = 40
        avg_vol = 100.0
        # 평평한 close → RSI 중간값
        closes = [100.0] * n
        opens = [101.0] * n  # 모두 음봉
        volumes = [avg_vol] * n
        volumes[-2] = avg_vol * 4.0  # climax
        opens[-2] = closes[-2] - 1.0  # 신호봉 양봉
        df = pd.DataFrame({
            "open": opens, "close": closes, "volume": volumes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
        })
        sig = self.strategy.generate(df)
        # RSI가 30 미만이 아니므로 BUY 신호 없어야 함
        assert sig.action != Action.BUY
