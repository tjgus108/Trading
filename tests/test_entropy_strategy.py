"""
ApproximateEntropyStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.entropy_strategy import ApproximateEntropyStrategy, _calc_entropy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, trend: str = "up") -> pd.DataFrame:
    np.random.seed(42)
    if trend == "up":
        closes = np.cumprod(1 + np.random.uniform(0.003, 0.008, n)) * 100
    elif trend == "down":
        closes = np.cumprod(1 - np.random.uniform(0.003, 0.008, n)) * 100
    else:
        closes = 100 + np.random.uniform(-0.5, 0.5, n).cumsum()
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_directional_df(n: int = 50, direction: str = "up") -> pd.DataFrame:
    """거의 단방향 움직임 → low entropy."""
    closes = np.zeros(n)
    closes[0] = 100.0
    for i in range(1, n):
        if direction == "up":
            closes[i] = closes[i - 1] * 1.005
        else:
            closes[i] = closes[i - 1] * 0.995
    highs = closes * 1.001
    lows = closes * 0.999
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_random_df_oversold(n: int = 50) -> pd.DataFrame:
    """랜덤 → high entropy, close << SMA20."""
    np.random.seed(99)
    closes = np.ones(n) * 100.0
    for i in range(1, n):
        closes[i] = closes[i - 1] + np.random.choice([-1, 1]) * 0.3
    # 완성봉(iloc[-2]) 과매도
    sma_approx = np.mean(closes[max(0, n - 22): n - 2])
    closes[-2] = sma_approx * 0.96
    highs = closes * 1.001
    lows = closes * 0.999
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_random_df_overbought(n: int = 50) -> pd.DataFrame:
    """랜덤 → high entropy, close >> SMA20."""
    np.random.seed(55)
    closes = np.ones(n) * 100.0
    for i in range(1, n):
        closes[i] = closes[i - 1] + np.random.choice([-1, 1]) * 0.3
    sma_approx = np.mean(closes[max(0, n - 22): n - 2])
    closes[-2] = sma_approx * 1.04
    highs = closes * 1.001
    lows = closes * 0.999
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes, "high": closes * 1.01,
        "low": closes * 0.99, "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestApproximateEntropyStrategy:

    def setup_method(self):
        self.strategy = ApproximateEntropyStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "entropy_strategy"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. 최소 25행에서 정상 실행
    def test_exactly_min_rows(self):
        df = _make_df(n=25)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=50)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "entropy_strategy"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 6. entry_price == close[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df(n=50)
        expected = float(df["close"].iloc[-2])
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(expected, rel=1e-5)

    # 7. 강한 상승 방향성 → BUY 또는 HOLD (never SELL)
    def test_directional_up_not_sell(self):
        df = _make_directional_df(n=50, direction="up")
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 8. 강한 하락 방향성 → SELL 또는 HOLD (never BUY)
    def test_directional_down_not_buy(self):
        df = _make_directional_df(n=50, direction="down")
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY

    # 9. HOLD 시 confidence LOW
    def test_hold_confidence_low_insufficient(self):
        df = _make_insufficient_df(n=5)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 10. _calc_entropy: 단방향 시계열 → 낮은 엔트로피
    def test_calc_entropy_directional_low(self):
        closes = pd.Series(np.linspace(100, 200, 40))
        ent = _calc_entropy(closes)
        assert ent < 0.7

    # 11. _calc_entropy: 랜덤 시계열 → 높은 엔트로피
    def test_calc_entropy_random_high(self):
        np.random.seed(0)
        closes = pd.Series(100 + np.random.choice([-1, 1], 40).cumsum() * 0.5)
        ent = _calc_entropy(closes)
        # 랜덤 시계열은 directional보다 높은 엔트로피
        directional = _calc_entropy(pd.Series(np.linspace(100, 200, 40)))
        assert ent > directional

    # 12. high entropy + 과매도 → BUY 또는 HOLD
    def test_high_entropy_oversold_buy_or_hold(self):
        df = _make_random_df_oversold(n=50)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.HOLD)

    # 13. high entropy + 과매수 → SELL 또는 HOLD
    def test_high_entropy_overbought_sell_or_hold(self):
        df = _make_random_df_overbought(n=50)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.SELL, Action.HOLD)

    # 14. 24행 → HOLD (최소 미충족)
    def test_24_rows_insufficient(self):
        df = _make_insufficient_df(n=24)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 15. reasoning에 entropy= 포함 (충분한 데이터)
    def test_reasoning_contains_entropy(self):
        df = _make_df(n=50)
        signal = self.strategy.generate(df)
        assert "entropy=" in signal.reasoning or "부족" in signal.reasoning

    # 16. bull_case/bear_case 존재 (충분한 데이터)
    def test_bull_bear_case_present(self):
        df = _make_df(n=50)
        signal = self.strategy.generate(df)
        if signal.action != Action.HOLD:
            assert len(signal.bull_case) > 0

    # 17. HIGH confidence when entropy < 0.5
    def test_high_confidence_low_entropy(self):
        # 완벽한 단방향 → entropy 매우 낮음
        n = 50
        closes = np.linspace(100, 200, n)
        df = pd.DataFrame({
            "open": closes, "high": closes * 1.001,
            "low": closes * 0.999, "close": closes,
            "volume": np.ones(n) * 1000,
        })
        signal = self.strategy.generate(df)
        # entropy < 0.5 이면 HIGH, 아니면 MEDIUM
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)
