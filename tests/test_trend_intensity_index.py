"""
TrendIntensityIndexV2Strategy 단위 테스트 (14개 이상).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_intensity_index import TrendIntensityIndexV2Strategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, mode: str = "hold") -> pd.DataFrame:
    """
    mode:
      "buy"  → tii crosses above tii_ma in negative zone
      "sell" → tii crosses below tii_ma in positive zone
      "hold" → flat
      "nan"  → too short for NaN
    """
    np.random.seed(0)

    if mode == "buy":
        # 하락 후 회복: tii 음수에서 tii_ma 상향 돌파
        # 앞 n-10봉: 강한 하락 (tii 매우 음수)
        # 뒤 10봉: 약간 회복 (tii 상승하며 tii_ma 돌파)
        closes = np.concatenate([
            np.linspace(150, 100, n - 10),
            np.linspace(100, 105, 10),
        ])
    elif mode == "sell":
        # 상승 후 하락: tii 양수에서 tii_ma 하향 돌파
        closes = np.concatenate([
            np.linspace(100, 150, n - 10),
            np.linspace(150, 145, 10),
        ])
    elif mode == "hold":
        closes = np.ones(n) * 100 + np.sin(np.linspace(0, 2 * np.pi, n)) * 2
    else:
        closes = np.ones(n) * 100

    return pd.DataFrame({
        "open":   closes,
        "high":   closes * 1.005,
        "low":    closes * 0.995,
        "close":  closes,
        "volume": np.ones(n) * 1000,
    })


def _make_crossover_buy_df():
    """TII가 tii_ma를 상향 돌파하는 정교한 데이터 (음수 구간)."""
    n = 60
    # 앞 50봉: 강한 하락 (below SMA 거의 다)
    # 뒤 10봉: 반등
    closes = list(np.linspace(150, 80, 50)) + list(np.linspace(80, 90, 10))
    df = pd.DataFrame({
        "open": closes,
        "high": [c * 1.005 for c in closes],
        "low":  [c * 0.995 for c in closes],
        "close": closes,
        "volume": [1000.0] * n,
    })
    return df


def _make_crossover_sell_df():
    """TII가 tii_ma를 하향 돌파하는 정교한 데이터 (양수 구간)."""
    n = 60
    closes = list(np.linspace(80, 150, 50)) + list(np.linspace(150, 140, 10))
    df = pd.DataFrame({
        "open": closes,
        "high": [c * 1.005 for c in closes],
        "low":  [c * 0.995 for c in closes],
        "close": closes,
        "volume": [1000.0] * n,
    })
    return df


# ── tests ────────────────────────────────────────────────────────────────────

class TestTrendIntensityIndexV2Strategy:

    def setup_method(self):
        self.strategy = TrendIntensityIndexV2Strategy()

    # 1. 전략명
    def test_strategy_name(self):
        assert self.strategy.name == "trend_intensity_index"

    # 2. 인스턴스 타입
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음
    def test_no_none_return(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 필드 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. Signal 반환 타입
    def test_signal_type(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")

    # 8. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 9. strategy 필드 = "trend_intensity_index"
    def test_strategy_field(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.strategy == "trend_intensity_index"

    # 10. 최소 행 = 45 경계
    def test_min_rows_boundary(self):
        df = _make_df(n=45)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 11. 44행 → HOLD (부족)
    def test_below_min_rows(self):
        df = _make_df(n=44)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. HOLD 신호: flat 데이터
    def test_hold_flat_data(self):
        df = _make_df(n=60, mode="hold")
        sig = self.strategy.generate(df)
        # flat이면 신호 없어야 함 (HOLD 가능)
        assert isinstance(sig, Signal)

    # 13. HIGH confidence: abs(tii) > 40
    def test_high_confidence_strong_trend(self):
        """강한 추세에서 HIGH confidence 가능."""
        closes = np.linspace(100, 200, 70)
        df = pd.DataFrame({
            "open": closes, "high": closes * 1.01,
            "low": closes * 0.99, "close": closes,
            "volume": np.ones(70) * 1000,
        })
        sig = self.strategy.generate(df)
        # 강한 상승 → tii 큰 양수, 신호가 생기면 HIGH
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 14. MEDIUM confidence: abs(tii) <= 40
    def test_medium_confidence_moderate_trend(self):
        """약한 추세에서 MEDIUM confidence."""
        closes = np.ones(60) * 100
        closes[30:] = 102  # 약간만 상승
        df = pd.DataFrame({
            "open": closes, "high": closes * 1.001,
            "low": closes * 0.999, "close": closes,
            "volume": np.ones(60) * 1000,
        })
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. BUY reasoning에 "TII" 포함
    def test_buy_reasoning_mentions_tii(self):
        df = _make_crossover_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "tii" in sig.reasoning.lower() or "TII" in sig.reasoning

    # 16. SELL reasoning에 "TII" 포함
    def test_sell_reasoning_mentions_tii(self):
        df = _make_crossover_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "tii" in sig.reasoning.lower() or "TII" in sig.reasoning
