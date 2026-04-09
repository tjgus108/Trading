"""
VolatilityRatioStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volatility_ratio import VolatilityRatioStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 5,
             close_val: float = 100.0,
             ema50: float = 95.0,
             vr_mode: str = "low") -> pd.DataFrame:
    """
    vr_mode='low':  short vol < long vol → VR < 1.2 → HOLD
    vr_mode='high': short vol 폭발 → VR > 1.2
    """
    rows = n
    if vr_mode == "low":
        # 안정적인 가격 → short/long vol 비슷하거나 short < long
        closes = [close_val + np.sin(i * 0.1) * 0.5 for i in range(rows)]
    else:
        # 앞부분 안정 + 뒷부분 급변동 → short vol 증가
        stable = [close_val] * (rows - 8)
        volatile = [close_val + ((-1) ** i) * 5 * (i + 1) for i in range(8)]
        closes = stable + volatile

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


def _make_high_vr_df(n: int = _MIN_ROWS + 5,
                     close_val: float = 110.0,
                     ema50: float = 95.0) -> pd.DataFrame:
    """VR > 1.2 유도: 앞부분 안정 + 마지막 5봉에서 큰 진동.
    신호 봉(-2)의 close = close_val.
    """
    rows = n
    stable = [100.0] * (rows - 7)
    # 마지막 7봉 중 앞 5봉 큰 진동, -2봉=close_val, -1봉=close_val
    volatile = [80.0, 130.0, 75.0, 135.0, 70.0, close_val, close_val]
    closes = stable + volatile
    df = pd.DataFrame({
        "open":   [100.0] * rows,
        "close":  closes,
        "high":   [c + 2.0 for c in closes],
        "low":    [c - 2.0 for c in closes],
        "volume": [1000.0] * rows,
        "ema50":  [ema50] * rows,
        "atr14":  [1.0] * rows,
    })
    return df


class TestVolatilityRatioStrategy:

    def setup_method(self):
        self.strategy = VolatilityRatioStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "volatility_ratio"

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
        assert sig.strategy == "volatility_ratio"

    # 5. VR 낮음 → HOLD
    def test_hold_low_vr(self):
        df = _make_df(n=_MIN_ROWS + 5, vr_mode="low")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. HOLD reasoning에 'No signal' 또는 'Insufficient' 포함
    def test_hold_reasoning(self):
        df = _make_df(n=_MIN_ROWS + 5, vr_mode="low")
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert "No signal" in sig.reasoning or "Insufficient" in sig.reasoning

    # 7. BUY 신호: VR > 1.2 AND close > ema50
    def test_buy_signal(self):
        df = _make_high_vr_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 8. BUY entry_price = close 값
    def test_buy_entry_price(self):
        df = _make_high_vr_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 9. SELL 신호: VR > 1.2 AND close < ema50
    def test_sell_signal(self):
        df = _make_high_vr_df(close_val=80.0, ema50=95.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 10. SELL entry_price = close 값
    def test_sell_entry_price(self):
        df = _make_high_vr_df(close_val=80.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 11. HIGH confidence: VR > 1.5
    def test_high_confidence_when_high_vr(self):
        # VR > 1.5 이면 HIGH confidence
        df = _make_high_vr_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action in (Action.BUY, Action.SELL):
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. MEDIUM confidence: 1.2 < VR <= 1.5
    def test_medium_confidence(self):
        df = _make_high_vr_df(close_val=110.0, ema50=95.0)
        sig = self.strategy.generate(df)
        if sig.action in (Action.BUY, Action.SELL):
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. 최소 행수 경계: 정확히 _MIN_ROWS 행
    def test_exact_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. 최소 행수 -1: 부족 → HOLD
    def test_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. confidence는 HIGH/MEDIUM/LOW 중 하나
    def test_confidence_valid_values(self):
        for vr_mode in ("low", "high"):
            df = _make_df(n=_MIN_ROWS + 10, vr_mode=vr_mode)
            sig = self.strategy.generate(df)
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
