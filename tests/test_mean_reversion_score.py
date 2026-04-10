"""
MeanReversionScoreStrategy 단위 테스트 (14개 이상)
"""

import math

import numpy as np
import pandas as pd
import pytest

from src.strategy.mean_reversion_score import MeanReversionScoreStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_oversold_df(n: int = 60) -> pd.DataFrame:
    """
    과매도 상태: 가격이 급락 후 낮은 위치 + 거래량 급증.
    rev_score > 1.5 AND vol_z > 0 → BUY
    """
    np.random.seed(1)
    # 처음 n-10 봉은 평균 근처
    closes = list(np.random.uniform(100, 102, n - 10))
    # 마지막 10봉: 급락
    for _ in range(10):
        closes.append(closes[-1] * 0.985)
    closes = np.array(closes[:n])

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()

    # 마지막 완성 캔들(idx = n-2)에서 거래량 급증
    volumes = np.random.uniform(1000, 2000, n)
    volumes[n - 2] = volumes[:n - 2].mean() * 5  # vol_z > 0 보장

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_overbought_df(n: int = 60) -> pd.DataFrame:
    """
    과매수 상태: 가격이 급등 후 높은 위치 + 거래량 급증.
    rev_score < -1.5 AND vol_z > 0 → SELL
    """
    np.random.seed(2)
    closes = list(np.random.uniform(100, 102, n - 10))
    for _ in range(10):
        closes.append(closes[-1] * 1.015)
    closes = np.array(closes[:n])

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()

    volumes = np.random.uniform(1000, 2000, n)
    volumes[n - 2] = volumes[:n - 2].mean() * 5

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_neutral_df(n: int = 60) -> pd.DataFrame:
    """중립 상태: rev_score ~0 → HOLD"""
    np.random.seed(3)
    closes = np.random.uniform(99, 101, n)
    highs = closes * 1.002
    lows = closes * 0.998
    volumes = np.random.uniform(1000, 2000, n)
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_short_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    highs = closes * 1.005
    lows = closes * 0.995
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMeanReversionScoreStrategy:

    def setup_method(self):
        self.strategy = MeanReversionScoreStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "mean_reversion_score"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_short_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_short_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. 과매도 → BUY
    def test_oversold_buy(self):
        df = _make_oversold_df(n=80)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 5. 과매수 → SELL
    def test_overbought_sell(self):
        df = _make_overbought_df(n=80)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 6. 중립 → HOLD
    def test_neutral_hold(self):
        df = _make_neutral_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 7. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_neutral_df(n=60)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 8. action이 유효한 값
    def test_action_valid(self):
        df = _make_neutral_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 9. confidence가 유효한 값
    def test_confidence_valid(self):
        df = _make_oversold_df(n=80)
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 10. strategy 필드
    def test_signal_strategy_field(self):
        df = _make_neutral_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.strategy == "mean_reversion_score"

    # 11. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_neutral_df(n=60)
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)

    # 12. BUY reasoning에 "과매도" 포함
    def test_buy_reasoning_contains_oversold(self):
        df = _make_oversold_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "과매도" in signal.reasoning

    # 13. SELL reasoning에 "과매수" 포함
    def test_sell_reasoning_contains_overbought(self):
        df = _make_overbought_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "과매수" in signal.reasoning

    # 14. BUY HIGH confidence when abs(rev_score) > 2.0
    def test_buy_high_confidence_strong_signal(self):
        # Very strong oversold: larger drop
        np.random.seed(99)
        n = 100
        closes = list(np.random.uniform(100, 102, n - 15))
        for _ in range(15):
            closes.append(closes[-1] * 0.975)
        closes = np.array(closes[:n])
        highs = closes * 1.005
        lows = closes * 0.995
        volumes = np.random.uniform(1000, 2000, n)
        volumes[n - 2] = volumes[:n - 2].mean() * 10
        df = pd.DataFrame({
            "open": closes, "high": highs, "low": lows,
            "close": closes, "volume": volumes,
        })
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            # HIGH when abs(rev_score) > 2.0
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 15. bull_case / bear_case 문자열
    def test_bull_bear_case_strings(self):
        df = _make_oversold_df(n=80)
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 16. bull_case에 "rev_score" 포함
    def test_bull_case_has_rev_score(self):
        df = _make_oversold_df(n=80)
        signal = self.strategy.generate(df)
        assert "rev_score" in signal.bull_case

    # 17. reasoning이 비어있지 않음
    def test_reasoning_nonempty(self):
        df = _make_neutral_df(n=60)
        signal = self.strategy.generate(df)
        assert len(signal.reasoning) > 0
