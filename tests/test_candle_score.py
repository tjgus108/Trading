"""
CandleScoreStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.candle_score import CandleScoreStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 20) -> pd.DataFrame:
    np.random.seed(42)
    closes = np.linspace(100.0, 110.0, n)
    highs = closes * (1 + np.random.uniform(0.005, 0.015, n))
    lows = closes * (1 - np.random.uniform(0.005, 0.015, n))
    opens = closes * (1 + np.random.uniform(-0.003, 0.003, n))
    volumes = np.random.uniform(1000, 3000, n)
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_perfect_bull_df() -> pd.DataFrame:
    """bull_score == 5인 DataFrame: idx=-2 봉이 완벽한 강세 캔들."""
    n = 20
    volumes = np.ones(n) * 1000.0
    closes = np.ones(n) * 100.0
    opens = closes.copy()
    highs = closes + 5.0
    lows = closes - 5.0

    idx = n - 2  # 18

    # 양봉: close > open
    opens[idx] = 100.0
    closes[idx] = 109.5   # close near high (range = 10, high-close = 0.5 → 0.05 < 0.1)
    highs[idx] = 110.0
    lows[idx] = 100.0     # close-low = 9.5, range = 10, ratio = 0.95 > 0.9
    # body = 9.5, range = 10, ratio = 0.95 > 0.6
    # volume > prev
    volumes[idx] = 3000.0
    volumes[idx - 1] = 1000.0

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_perfect_bear_df() -> pd.DataFrame:
    """bear_score == 5인 DataFrame: idx=-2 봉이 완벽한 약세 캔들."""
    n = 20
    volumes = np.ones(n) * 1000.0
    closes = np.ones(n) * 100.0
    opens = closes.copy()
    highs = closes + 5.0
    lows = closes - 5.0

    idx = n - 2  # 18

    # 음봉: close < open
    opens[idx] = 109.5
    closes[idx] = 100.5   # close near low: (close-low)/(high-low) = 0.5/10 = 0.05 < 0.1
    highs[idx] = 110.0    # high-close = 9.5, range = 10, ratio = 0.95 > 0.9
    lows[idx] = 100.0
    # body = 9, range = 10, ratio = 0.9 > 0.6
    volumes[idx] = 3000.0
    volumes[idx - 1] = 1000.0

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestCandleScoreStrategy:

    def setup_method(self):
        self.strategy = CandleScoreStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "candle_score"

    # 2. 데이터 부족(15 미만) → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. Signal 반환 타입
    def test_returns_signal_type(self):
        df = _make_df(n=20)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 5. Perfect bull → BUY
    def test_perfect_bull_buy(self):
        df = _make_perfect_bull_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. Perfect bull → HIGH confidence (score == 5)
    def test_perfect_bull_high_confidence(self):
        df = _make_perfect_bull_df()
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.HIGH

    # 7. Perfect bear → SELL
    def test_perfect_bear_sell(self):
        df = _make_perfect_bear_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 8. Perfect bear → HIGH confidence (score == 5)
    def test_perfect_bear_high_confidence(self):
        df = _make_perfect_bear_df()
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.HIGH

    # 9. entry_price == close[idx=-2]
    def test_entry_price_equals_close(self):
        df = _make_perfect_bull_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 10. confidence 유효 값
    def test_confidence_valid_values(self):
        for fn in [lambda: _make_df(20), _make_perfect_bull_df, _make_perfect_bear_df]:
            signal = self.strategy.generate(fn())
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. action은 BUY/SELL/HOLD 중 하나
    def test_action_valid(self):
        df = _make_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_perfect_bull_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "candle_score"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 13. BUY reasoning에 bull score 포함
    def test_buy_reasoning_contains_score(self):
        df = _make_perfect_bull_df()
        signal = self.strategy.generate(df)
        assert "bull score" in signal.reasoning.lower() or "score" in signal.reasoning.lower()

    # 14. SELL reasoning에 bear score 포함
    def test_sell_reasoning_contains_score(self):
        df = _make_perfect_bear_df()
        signal = self.strategy.generate(df)
        assert "bear score" in signal.reasoning.lower() or "score" in signal.reasoning.lower()

    # 15. bull_score 직접 계산 검증 (score=5)
    def test_bull_score_max(self):
        # 완벽한 양봉 파라미터
        score = self.strategy._bull_score(
            o=100.0, h=110.0, lo=100.0, c=109.5,
            vol=3000.0, prev_vol=1000.0, rng=10.0,
        )
        assert score == 5

    # 16. bear_score 직접 계산 검증 (score=5)
    def test_bear_score_max(self):
        score = self.strategy._bear_score(
            o=109.5, h=110.0, lo=100.0, c=100.5,
            vol=3000.0, prev_vol=1000.0, rng=10.0,
        )
        assert score == 5

    # 17. 캔들 범위 0 → HOLD
    def test_zero_range_hold(self):
        n = 20
        closes = np.ones(n) * 100.0
        df = pd.DataFrame({
            "open": closes, "high": closes, "low": closes,
            "close": closes, "volume": np.ones(n) * 1000,
        })
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 18. score < 4 → HOLD
    def test_low_score_hold(self):
        n = 20
        np.random.seed(99)
        # 중립적인 도지 캔들 (open ≈ close, small body)
        closes = np.ones(n) * 100.0
        opens = closes.copy()
        highs = closes + 5.0
        lows = closes - 5.0
        # idx=-2: open == close (0점짜리 캔들)
        opens[n - 2] = 100.0
        closes[n - 2] = 100.0
        volumes = np.ones(n) * 1000.0
        df = pd.DataFrame({
            "open": opens, "high": highs, "low": lows,
            "close": closes, "volume": volumes,
        })
        signal = self.strategy.generate(df)
        # open==close → bull_score 0점(양봉 아님), bear_score 0점(음봉 아님) → HOLD
        assert signal.action == Action.HOLD
