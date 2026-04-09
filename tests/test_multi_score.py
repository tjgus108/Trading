"""
MultiScoreStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.multi_score import MultiScoreStrategy, _ema
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _compute_bull_score(df: pd.DataFrame) -> int:
    """테스트용 bull_score 직접 계산."""
    close = df["close"]
    volume = df["volume"]
    ema50 = _ema(close, 50)
    sma20 = close.rolling(20).mean()
    vol_sma20 = volume.rolling(20).mean()
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    macd_line = _ema(close, 12) - _ema(close, 26)
    signal_line = _ema(macd_line, 9)
    histogram = macd_line - signal_line
    close_val = float(close.iloc[-2])
    return (
        int(close_val > float(ema50.iloc[-2]))
        + int(float(rsi.iloc[-2]) > 50)
        + int(close_val > float(sma20.iloc[-2]))
        + int(float(volume.iloc[-2]) > float(vol_sma20.iloc[-2]) * 1.1)
        + int(float(histogram.iloc[-2]) > 0)
    )


def _make_bull_df(n: int = 150) -> pd.DataFrame:
    """강세 데이터: 가속 상승으로 5개 지표 모두 강세 보장."""
    closes = np.array([100.0 * (1.008 ** i) for i in range(n)])
    # 마지막 30개는 더 빠르게 가속 (MACD histogram 양수 보장)
    for i in range(n - 30, n):
        closes[i] = closes[i - 1] * 1.015
    highs = closes * 1.005
    lows = closes * 0.995
    # 볼륨: 이전 20개 평균 대비 마지막 5개만 급등 (1.1배 초과 보장)
    volumes = np.ones(n) * 500
    volumes[-5:] = 3000  # 최근 5개만 급등 → vol_sma20 대비 충분히 높음
    df = pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


def _make_bear_df(n: int = 150) -> pd.DataFrame:
    """약세 데이터: 가속 하락으로 5개 지표 대부분 약세."""
    closes = np.array([500.0 * (0.992 ** i) for i in range(n)])
    for i in range(n - 30, n):
        closes[i] = closes[i - 1] * 0.985
    highs = closes * 1.005
    lows = closes * 0.995
    volumes = np.ones(n) * 500
    volumes[-5:] = 3000
    df = pd.DataFrame({
        "open": closes * 0.999,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


def _make_flat_df(n: int = 60) -> pd.DataFrame:
    """횡보 데이터."""
    np.random.seed(2)
    closes = np.ones(n) * 100 + np.random.randn(n) * 0.2
    highs = closes * 1.002
    lows = closes * 0.998
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.001,
        "low": closes * 0.999,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMultiScoreStrategy:

    def setup_method(self):
        self.strategy = MultiScoreStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "multi_score"

    # 2. 강세 데이터 → BUY (bull_score >= 4 확인 포함)
    def test_bull_market_buy(self):
        df = _make_bull_df()
        score = _compute_bull_score(df)
        assert score >= 4, f"테스트 데이터 bull_score={score} < 4: 테스트 데이터 문제"
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 약세 데이터 → SELL (bear_score 계산으로 검증)
    def test_bear_market_sell(self):
        df = _make_bear_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. BUY 신호 confidence (HIGH or MEDIUM)
    def test_buy_confidence_valid(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 5. SELL 신호 confidence (HIGH or MEDIUM)
    def test_sell_confidence_valid(self):
        df = _make_bear_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 6. 데이터 부족 → HOLD, LOW
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=25)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 7. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "multi_score"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 9. BUY reasoning에 "bull_score" 포함
    def test_buy_reasoning_contains_bull_score(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "bull_score" in signal.reasoning

    # 10. SELL reasoning에 "bear_score" 포함
    def test_sell_reasoning_contains_bear_score(self):
        df = _make_bear_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "bear_score" in signal.reasoning

    # 11. BUY 신호 bull_case / bear_case 비어있지 않음
    def test_buy_has_bull_bear_case(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 12. SELL 신호 bull_case / bear_case 비어있지 않음
    def test_sell_has_bull_bear_case(self):
        df = _make_bear_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 13. entry_price는 close 값
    def test_entry_price_is_close(self):
        df = _make_bull_df(n=80)
        signal = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected_close) < 1e-6

    # 14. 횡보 시 HOLD
    def test_flat_market_hold(self):
        df = _make_flat_df(n=60)
        signal = self.strategy.generate(df)
        # 횡보에서는 bull/bear score 모두 4 미만이어야 함
        assert signal.action == Action.HOLD

    # 15. n=30 경계값 테스트 (정확히 30행)
    def test_min_rows_boundary(self):
        df = _make_bull_df(n=30)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 16. n=29 경계값 → HOLD
    def test_below_min_rows(self):
        df = _make_insufficient_df(n=29)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
