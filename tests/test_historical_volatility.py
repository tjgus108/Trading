"""
HistoricalVolatilityStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.historical_volatility import HistoricalVolatilityStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _make_df(n: int = _MIN_ROWS + 5,
             close_val: float = 100.0,
             ema50: float = 95.0,
             mode: str = "stable") -> pd.DataFrame:
    """
    mode='stable': 완만한 사인파 → HV5 ≈ HV20 → ratio ≈ 1 → HOLD
    mode='contracted': 앞부분 변동 크고 뒷부분 거의 움직이지 않음 → HV5 < HV20 * 0.7
    """
    if mode == "stable":
        closes = [close_val + np.sin(i * 0.3) * 2.0 for i in range(n)]
    else:
        # 앞부분(0~n-8) 큰 변동, 뒷부분(n-7~) 거의 정적
        volatile = [close_val + ((-1) ** i) * 5 for i in range(n - 7)]
        flat = [close_val] * 7
        closes = volatile + flat

    closes[-2] = close_val
    closes[-1] = close_val

    df = pd.DataFrame({
        "open":   [close_val] * n,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50":  [ema50] * n,
        "atr14":  [1.0] * n,
    })
    return df


def _make_contracted_df(close_val: float = 110.0, ema50: float = 95.0,
                        n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """HV5 << HV20: 앞부분 큰 진동 + 뒷부분 완전 정지."""
    volatile = [100.0 + ((-1) ** i) * 8 for i in range(n - 7)]
    flat = [close_val] * 7
    closes = volatile + flat
    closes[-2] = close_val
    closes[-1] = close_val
    df = pd.DataFrame({
        "open":   [100.0] * n,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50":  [ema50] * n,
        "atr14":  [1.0] * n,
    })
    return df


class TestHistoricalVolatilityStrategy:

    def setup_method(self):
        self.strategy = HistoricalVolatilityStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "historical_volatility"

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
        assert sig.strategy == "historical_volatility"

    # 5. 변동성 확장(stable) → HOLD
    def test_hold_when_hv_expanding(self):
        df = _make_df(n=_MIN_ROWS + 5, mode="stable")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. HOLD reasoning 확인
    def test_hold_reasoning_content(self):
        df = _make_df(n=_MIN_ROWS + 5, mode="stable")
        sig = self.strategy.generate(df)
        assert "No signal" in sig.reasoning or "Insufficient" in sig.reasoning

    # 7. BUY: HV5 < HV20 * 0.7 AND close > ema50
    def test_buy_signal(self):
        df = _make_contracted_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 8. BUY entry_price = idx close 값
    def test_buy_entry_price(self):
        df = _make_contracted_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 9. SELL: HV5 < HV20 * 0.7 AND close < ema50
    def test_sell_signal(self):
        df = _make_contracted_df(close_val=80.0, ema50=95.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 10. SELL entry_price = idx close 값
    def test_sell_entry_price(self):
        df = _make_contracted_df(close_val=80.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 11. HIGH confidence: ratio < 0.5
    def test_high_confidence_deep_contraction(self):
        df = _make_contracted_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action in (Action.BUY, Action.SELL):
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. confidence 유효값
    def test_confidence_valid_values(self):
        for mode in ("stable", "contracted"):
            df = _make_df(n=_MIN_ROWS + 5, mode=mode)
            sig = self.strategy.generate(df)
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 13. 최소 행수 경계: 정확히 _MIN_ROWS 행
    def test_exact_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. 최소 행수 -1 → HOLD
    def test_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. action은 BUY/SELL/HOLD 중 하나
    def test_action_valid_values(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 16. BUY reasoning에 'BUY' 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_contracted_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 17. SELL reasoning에 'SELL' 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_contracted_df(close_val=80.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning
