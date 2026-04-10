"""
LiquidityScoreStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.liquidity_score import LiquidityScoreStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """
    BUY 조건:
    - liquidity_score > liq_ma: 볼륨 급증 + 스프레드 좁음 → liq_score 높음
    - close > close_ma: 상승 추세
    - vol_score > 1.2: 최근 거래량 > 평균 1.2배
    """
    np.random.seed(10)
    closes = np.linspace(100, 120, n)
    # 좁은 spread (스프레드 작음 → liq_score 높음)
    highs = closes * 1.001
    lows = closes * 0.999
    # 마지막 구간 볼륨 급증
    volumes = np.ones(n) * 1000.0
    volumes[-5:] = 3000.0  # vol_score > 1.2 확보
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """
    SELL 조건:
    - liquidity_score > liq_ma
    - close < close_ma: 하락 추세
    - vol_score > 1.2
    """
    np.random.seed(20)
    closes = np.linspace(120, 100, n)
    highs = closes * 1.001
    lows = closes * 0.999
    volumes = np.ones(n) * 1000.0
    volumes[-5:] = 3000.0
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_low_vol_df(n: int = 40) -> pd.DataFrame:
    """vol_score <= 1.2 → HOLD"""
    np.random.seed(30)
    closes = np.linspace(100, 120, n)
    highs = closes * 1.001
    lows = closes * 0.999
    volumes = np.ones(n) * 1000.0  # 균일 볼륨 → vol_score ≈ 1.0
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_high_conf_df(n: int = 40) -> pd.DataFrame:
    """HIGH confidence: vol_score > 2.0, liquidity_score > liq_ma * 1.5"""
    np.random.seed(40)
    closes = np.linspace(100, 130, n)
    # 매우 좁은 스프레드
    highs = closes * 1.0005
    lows = closes * 0.9995
    volumes = np.ones(n) * 500.0
    volumes[-10:] = 5000.0  # vol_score >> 2.0
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestLiquidityScoreStrategy:

    def setup_method(self):
        self.strategy = LiquidityScoreStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "liquidity_score"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → LOW confidence
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 6. action 유효값
    def test_action_valid_value(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence 유효값
    def test_confidence_valid_value(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 = "liquidity_score"
    def test_signal_strategy_field(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.strategy == "liquidity_score"

    # 9. entry_price = float
    def test_entry_price_is_float(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)

    # 10. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0

    # 11. 상승 추세 + 볼륨 급증 → BUY
    def test_buy_signal_on_uptrend_vol_surge(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 12. 하락 추세 + 볼륨 급증 → SELL
    def test_sell_signal_on_downtrend_vol_surge(self):
        df = _make_sell_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 13. 낮은 볼륨 → HOLD
    def test_low_volume_hold(self):
        df = _make_low_vol_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 14. HIGH confidence 조건
    def test_high_confidence_on_strong_signal(self):
        df = _make_high_conf_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action in (Action.BUY, Action.SELL):
            assert signal.confidence == Confidence.HIGH

    # 15. BUY reasoning에 "BUY" 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_buy_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "BUY" in signal.reasoning

    # 16. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_sell_df(n=40)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "SELL" in signal.reasoning
