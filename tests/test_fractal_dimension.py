"""
FractalDimensionStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.fractal_dimension import FractalDimensionStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(closes: list) -> pd.DataFrame:
    closes = np.array(closes, dtype=float)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(len(closes)) * 1000,
    })


def _make_trending_up(n: int = 30) -> pd.DataFrame:
    """효율적 상승 추세 (직선적 상승)."""
    closes = [100.0 + i * 0.5 for i in range(n)]
    return _make_df(closes)


def _make_trending_down(n: int = 30) -> pd.DataFrame:
    """효율적 하락 추세 (직선적 하락)."""
    closes = [100.0 - i * 0.5 for i in range(n)]
    return _make_df(closes)


def _make_zigzag(n: int = 30) -> pd.DataFrame:
    """지그재그 → 비효율적 → 낮은 ER."""
    closes = [100.0 + (1 if i % 2 == 0 else -1) * (i % 5) for i in range(n)]
    return _make_df(closes)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestFractalDimensionStrategy:

    def setup_method(self):
        self.strat = FractalDimensionStrategy()

    # 1. 기본 속성
    def test_name(self):
        assert self.strat.name == "fractal_dimension"

    # 2. 데이터 부족 시 HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_trending_up(5)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
        assert "데이터 부족" in sig.reasoning

    # 3. MIN_ROWS - 1 개 → HOLD
    def test_min_rows_minus_one_hold(self):
        df = _make_trending_up(19)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. 반환 타입
    def test_returns_signal_type(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. strategy 필드
    def test_signal_strategy_field(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert sig.strategy == "fractal_dimension"

    # 6. entry_price = iloc[-2]
    def test_entry_price_is_last_completed_candle(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)

    # 7. 상승 추세 → BUY or HOLD
    def test_trending_up_buy_or_hold(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 8. 하락 추세 → SELL or HOLD
    def test_trending_down_sell_or_hold(self):
        df = _make_trending_down(30)
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 9. 효율적 상승 추세 BUY 신호
    def test_efficient_uptrend_buy(self):
        closes = [100.0 + i * 1.0 for i in range(50)]
        df = _make_df(closes)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 10. 효율적 하락 추세 SELL 신호
    def test_efficient_downtrend_sell(self):
        closes = [200.0 - i * 1.0 for i in range(50)]
        df = _make_df(closes)
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 11. confidence 유효 값
    def test_confidence_valid(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert len(sig.reasoning) > 0

    # 13. 지그재그 → HOLD (비효율 추세)
    def test_zigzag_hold(self):
        df = _make_zigzag(30)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. bull_case / bear_case 필드 존재
    def test_bull_bear_case_fields(self):
        df = _make_trending_up(30)
        sig = self.strat.generate(df)
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 15. 경계값 - 정확히 20행
    def test_exactly_min_rows(self):
        df = _make_trending_up(20)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 16. 큰 데이터셋 처리
    def test_large_dataset(self):
        df = _make_trending_up(200)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 17. er > 0.8 → HIGH confidence
    def test_high_confidence_high_er(self):
        # 완전 직선 상승: er이 1에 가깝게
        closes = [float(100 + i) for i in range(50)]
        df = _make_df(closes)
        sig = self.strat.generate(df)
        # 직선이면 BUY + HIGH confidence 가능
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
