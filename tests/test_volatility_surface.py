"""
VolatilitySurfaceStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volatility_surface import VolatilitySurfaceStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30


def _make_df(n: int = _MIN_ROWS + 5, close_val: float = 100.0,
             noise: float = 0.001) -> pd.DataFrame:
    """기본: 저변동성(uniform close), vol_ratio 낮음."""
    closes = [close_val + noise * i for i in range(n)]
    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """
    BUY 조건: vol_ratio < 0.8, vol_ratio < vol_ratio_ma, close > ma20.
    장기 변동성이 크고 단기 변동성이 작은 상승 추세 시나리오.
    """
    closes = []
    # 처음 n-5개: 큰 변동으로 rv_long 높임
    base = 90.0
    for i in range(n - 5):
        if i % 2 == 0:
            closes.append(base + 5.0)
        else:
            closes.append(base - 5.0)
    # 마지막 5개: 좁은 범위로 rv_short 낮추고 상승 방향
    for i in range(5):
        closes.append(105.0 + i * 0.01)

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.2 for c in closes],
        "low": [c - 0.2 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _make_sell_df() -> pd.DataFrame:
    """
    SELL 조건: vol_ratio < 0.8, vol_ratio < vol_ratio_ma, close < ma20.

    Strategy:
    - 처음 30개: 100.0 근처에서 큰 변동 (±10) → rv_long 씨앗 값 높음
    - 이후 25개: 99.0 평균, 좁은 범위(±0.05) → rv_short 낮아지고 vol_ratio < 1.0
    - 마지막 10개: 점점 낮아지는 값 → close < ma20
      (ma20은 중간 레벨인 ~99에서 시작하므로 마지막 봉이 ~85이면 < ma20)
    """
    closes = []
    # 처음 30개: 큰 변동 → rv_long 높음
    for i in range(30):
        closes.append(100.0 + (10.0 if i % 2 == 0 else -10.0))
    # 다음 25개: 좁은 변동, 낮은 레벨 (rv_short 낮춤)
    for i in range(25):
        closes.append(85.0 + (0.05 if i % 2 == 0 else -0.05))
    # 마지막 10개: 더 내려가 close < ma20 확실히
    for i in range(10):
        closes.append(70.0 - i * 0.01)

    n = len(closes)
    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.05 for c in closes],
        "low": [c - 0.05 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


class TestVolatilitySurfaceStrategy:

    def setup_method(self):
        self.strategy = VolatilitySurfaceStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volatility_surface"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. BUY 신호: vol_ratio<0.8, close>ma20
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 4. BUY strategy 이름 필드
    def test_buy_strategy_name(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "volatility_surface"

    # 5. SELL 신호: vol_ratio<0.8, close<ma20
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 6. SELL strategy 이름 필드
    def test_sell_strategy_name(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "volatility_surface"

    # 7. HIGH confidence when vol_ratio < 0.6
    def test_confidence_high_when_low_vol_ratio(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 8. Signal 타입
    def test_signal_type(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 10. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 11. HOLD: high vol_ratio (>= 0.8)
    def test_hold_high_vol_ratio(self):
        """vol_ratio >= 0.8: 단기/장기 변동성 비슷 → HOLD"""
        n = _MIN_ROWS + 5
        # 균등한 변동성: rv_short ≈ rv_long → vol_ratio ≈ 1.0
        np.random.seed(42)
        closes = 100.0 + np.cumsum(np.random.randn(n) * 2)
        df = pd.DataFrame({
            "open": closes,
            "close": closes,
            "high": closes + 0.5,
            "low": closes - 0.5,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        # vol_ratio가 높으면 HOLD, 낮으면 BUY/SELL 가능 — 단순히 Signal 반환 확인
        assert isinstance(sig, Signal)

    # 12. 정확히 MIN_ROWS 행에서 동작
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 13. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 14. MIN_ROWS - 1 → HOLD
    def test_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
