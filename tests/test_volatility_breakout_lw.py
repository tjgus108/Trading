"""
VolatilityBreakoutLWStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest

from src.strategy.volatility_breakout import VolatilityBreakoutLWStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 15


def _alternating_closes(n: int, base: float = 100.0, amp: float = 1.0):
    """RSI를 중립(~50)으로 유지하기 위해 상승/하락 번갈아 반복."""
    result = []
    for i in range(n):
        result.append(base + amp if i % 2 == 0 else base - amp)
    return result


def _base_df(n: int = _MIN_ROWS + 5) -> dict:
    closes = _alternating_closes(n)
    return {
        "open": [100.0] * n,
        "close": closes[:],
        "high": [101.0] * n,
        "low": [99.0] * n,
        "volume": [1000.0] * n,
        "ema50": [100.0] * n,
        "atr14": [1.0] * n,
    }


def _make_buy_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    BUY 조건 충족:
    - prev(idx-1): high=102, low=98, close=100 → prev_range=4
    - buy_level = 100 + 0.5*4 = 102
    - curr(idx): close=103.2 > 102 ✓ (돌파폭=1.2 → MEDIUM)
    - volume: avg_10=500, curr=1000 → vol_ok ✓
    - RSI: alternating ±1 + 상승 1.2 → RSI ~50-55 < 65 ✓
    """
    d = _base_df(n)
    idx = n - 2

    # prev 봉
    d["high"][idx - 1] = 102.0
    d["low"][idx - 1] = 98.0
    d["close"][idx - 1] = 100.0
    d["open"][idx - 1] = 100.0

    # curr 봉: 돌파 (close=103.2 > buy_level=102)
    d["close"][idx] = 103.2
    d["high"][idx] = 104.0
    d["low"][idx] = 100.0
    d["open"][idx] = 100.0

    # volume: 이전 10봉 낮게, 현재 높게
    for i in range(idx - 10, idx):
        d["volume"][i] = 500.0
    d["volume"][idx] = 1000.0

    return pd.DataFrame(d)


def _make_buy_high_conf_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    HIGH confidence BUY:
    - prev_range=4, buy_level=100+2=102
    - 돌파폭 = close(105.1) - buy_level(102) = 3.1 > 4*0.75=3.0 → HIGH
    - close(105.1)는 prev_close(100)보다 5.1 상승 → RSI 상승 but <65 유지 (이전 봉 alternating)
    """
    d = _base_df(n)
    idx = n - 2

    d["high"][idx - 1] = 102.0
    d["low"][idx - 1] = 98.0
    d["close"][idx - 1] = 100.0
    d["open"][idx - 1] = 100.0

    d["close"][idx] = 105.1
    d["high"][idx] = 106.0
    d["low"][idx] = 100.0
    d["open"][idx] = 100.0

    for i in range(idx - 10, idx):
        d["volume"][i] = 500.0
    d["volume"][idx] = 1000.0

    return pd.DataFrame(d)


def _make_sell_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    SELL 조건 충족:
    - prev: high=102, low=98, close=100 → prev_range=4, sell_level=98
    - curr close=96.8 < 98 ✓ (돌파폭=1.2 → MEDIUM)
    - vol_ok ✓
    - RSI: alternating ±1 base + 하락 1.2 → RSI ~40~50 > 35 ✓
    """
    d = _base_df(n)
    idx = n - 2

    d["high"][idx - 1] = 102.0
    d["low"][idx - 1] = 98.0
    d["close"][idx - 1] = 100.0
    d["open"][idx - 1] = 100.0

    d["close"][idx] = 96.8
    d["high"][idx] = 100.0
    d["low"][idx] = 96.0
    d["open"][idx] = 100.0

    for i in range(idx - 10, idx):
        d["volume"][i] = 500.0
    d["volume"][idx] = 1000.0

    return pd.DataFrame(d)


def _make_sell_high_conf_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    HIGH confidence SELL:
    - prev_range=4, sell_level=98
    - close=94.9 → 돌파폭 = 98-94.9 = 3.1 > 4*0.75=3.0 → HIGH
    - RSI: alternating ±1 + 하락 ~5 → RSI > 35 유지 (기존 gain/loss 균형)
    """
    d = _base_df(n)
    idx = n - 2

    d["high"][idx - 1] = 102.0
    d["low"][idx - 1] = 98.0
    d["close"][idx - 1] = 100.0
    d["open"][idx - 1] = 100.0

    d["close"][idx] = 94.9
    d["high"][idx] = 100.0
    d["low"][idx] = 94.0
    d["open"][idx] = 100.0

    for i in range(idx - 10, idx):
        d["volume"][i] = 500.0
    d["volume"][idx] = 1000.0

    return pd.DataFrame(d)


class TestVolatilityBreakoutLWStrategy:

    def setup_method(self):
        self.strategy = VolatilityBreakoutLWStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volatility_breakout_lw"

    # 2. BUY 신호
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "volatility_breakout_lw"

    # 3. BUY MEDIUM confidence (돌파폭 < 전일 변동폭 * 0.75)
    def test_buy_medium_confidence(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 4. BUY HIGH confidence (돌파폭 > 전일 변동폭 * 0.75)
    def test_buy_high_confidence(self):
        df = _make_buy_high_conf_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. BUY entry_price = close
    def test_buy_entry_price(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == pytest.approx(103.2)

    # 6. SELL 신호
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "volatility_breakout_lw"

    # 7. SELL HIGH confidence
    def test_sell_high_confidence(self):
        df = _make_sell_high_conf_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. SELL entry_price = close
    def test_sell_entry_price(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == pytest.approx(96.8)

    # 9. HOLD: 돌파 없음
    def test_hold_no_breakout(self):
        n = _MIN_ROWS + 5
        d = _base_df(n)
        idx = n - 2
        # prev_range=4, buy_level=102, sell_level=98, close=100 (중간)
        d["high"][idx - 1] = 102.0
        d["low"][idx - 1] = 98.0
        d["close"][idx - 1] = 100.0
        d["close"][idx] = 100.0
        d["high"][idx] = 101.0
        d["low"][idx] = 99.0
        df = pd.DataFrame(d)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: 볼륨 미달
    def test_hold_volume_insufficient(self):
        df = _make_buy_df()
        idx = len(df) - 2
        df = df.copy()
        # avg_vol=500, 현재 볼륨 100 < 500
        df.loc[df.index[idx], "volume"] = 100.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: RSI >= 65 (BUY 조건 차단)
    def test_hold_rsi_too_high_for_buy(self):
        n = _MIN_ROWS + 30
        d = _base_df(n)
        idx = n - 2

        d["high"][idx - 1] = 110.0
        d["low"][idx - 1] = 90.0
        d["close"][idx - 1] = 100.0
        d["open"][idx - 1] = 100.0

        # 이전 14봉 이상을 연속 상승으로 세팅 → RSI 높게
        for i in range(idx - 16, idx):
            d["close"][i] = 80.0 + (i - (idx - 16)) * 2.0

        # curr: buy_level 돌파
        d["close"][idx] = 112.0
        d["high"][idx] = 113.0
        d["low"][idx] = 100.0

        for i in range(idx - 10, idx):
            d["volume"][i] = 500.0
        d["volume"][idx] = 1000.0

        df = pd.DataFrame(d)
        sig = self.strategy.generate(df)
        # RSI >= 65 이면 BUY 안 됨
        assert sig.action in (Action.HOLD, Action.SELL)

    # 12. 데이터 부족 (< 15행)
    def test_insufficient_data(self):
        n = 10
        d = _base_df(n)
        df = pd.DataFrame(d)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "volatility_breakout_lw"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 14. BUY reasoning에 핵심 정보 포함
    def test_buy_reasoning_content(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "BUY" in sig.reasoning or "buy_level" in sig.reasoning

    # 15. SELL reasoning에 핵심 정보 포함
    def test_sell_reasoning_content(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "SELL" in sig.reasoning or "sell_level" in sig.reasoning

    # 16. HOLD action confidence = LOW
    def test_hold_confidence_low(self):
        n = _MIN_ROWS + 5
        d = _base_df(n)
        idx = n - 2
        # prev_range=4, buy_level=102, sell_level=98, close=100 (중간 → HOLD)
        d["high"][idx - 1] = 102.0
        d["low"][idx - 1] = 98.0
        d["close"][idx - 1] = 100.0
        d["close"][idx] = 100.0
        d["high"][idx] = 101.0
        d["low"][idx] = 99.0
        df = pd.DataFrame(d)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
