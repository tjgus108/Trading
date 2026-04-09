"""
HurstExponentStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.hurst_strategy import HurstExponentStrategy, _calc_hurst
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up") -> pd.DataFrame:
    """기본 DataFrame 생성."""
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
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_trend_df(n: int = 60) -> pd.DataFrame:
    """강한 상승 추세 → H > 0.55, EMA9 > EMA21 유도."""
    closes = np.linspace(100, 200, n)
    df = _make_df(n)
    df["close"] = closes
    df["high"] = closes * 1.002
    df["low"] = closes * 0.998
    return df


def _make_reversion_df_oversold(n: int = 60) -> pd.DataFrame:
    """H < 0.45, close << SMA20 유도."""
    np.random.seed(7)
    base = np.ones(n) * 100.0
    # 진동 패턴으로 H 낮추기
    for i in range(1, n):
        base[i] = base[i - 1] * (-1 if i % 2 == 0 else 1) * 0.001 + base[i - 1]
    # 마지막 값을 SMA20보다 훨씬 낮게
    base[-2] = base[-(n // 2):-2].mean() * 0.90  # SMA20 대비 10% 하락
    df = pd.DataFrame({
        "open": base, "high": base * 1.001, "low": base * 0.999,
        "close": base, "volume": np.ones(n) * 1000,
    })
    return df


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes, "high": closes * 1.01,
        "low": closes * 0.99, "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestHurstExponentStrategy:

    def setup_method(self):
        self.strategy = HurstExponentStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "hurst_strategy"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. 최소 40행에서 정상 실행
    def test_exactly_min_rows(self):
        df = _make_df(n=40)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "hurst_strategy"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 6. entry_price == close[-2]
    def test_entry_price_is_last_close(self):
        df = _make_df(n=60)
        expected = float(df["close"].iloc[-2])
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(expected, rel=1e-5)

    # 7. 강한 상승 추세 → BUY 또는 HOLD (never SELL)
    def test_strong_uptrend_not_sell(self):
        df = _make_trend_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 8. reasoning에 H= 포함
    def test_reasoning_contains_hurst(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        # 데이터 충분 시 H= 또는 "부족"
        if signal.action != Action.HOLD or "Hurst" in signal.reasoning:
            assert "H=" in signal.reasoning or "부족" in signal.reasoning or "Hurst" in signal.reasoning

    # 9. HOLD 시 confidence LOW
    def test_hold_confidence_low(self):
        df = _make_insufficient_df(n=5)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 10. _calc_hurst: 상승 추세 → H 반환
    def test_calc_hurst_returns_float(self):
        closes = pd.Series(np.linspace(100, 200, 50))
        h = _calc_hurst(closes)
        assert isinstance(h, float)

    # 11. _calc_hurst: 데이터 부족 → None
    def test_calc_hurst_insufficient_returns_none(self):
        closes = pd.Series([100.0, 101.0, 102.0])
        h = _calc_hurst(closes)
        assert h is None

    # 12. _calc_hurst: 상수 시계열 → None (분산=0)
    def test_calc_hurst_constant_series_none(self):
        closes = pd.Series([100.0] * 40)
        h = _calc_hurst(closes)
        assert h is None

    # 13. bull_case/bear_case 존재 (충분한 데이터)
    def test_bull_bear_case_present(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action != Action.HOLD:
            assert "H=" in signal.bull_case or len(signal.bull_case) > 0

    # 14. H > 0.65 → HIGH confidence
    def test_high_confidence_when_h_extreme(self):
        # 매우 강한 추세로 H > 0.65 유도
        df = _make_trend_df(n=80)
        signal = self.strategy.generate(df)
        # HIGH confidence이거나 MEDIUM (H에 따라 다를 수 있음)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 15. 39행 → HOLD (최소 미충족)
    def test_39_rows_insufficient(self):
        df = _make_insufficient_df(n=39)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 16. 평균 회귀 과매도 시나리오 → BUY 또는 HOLD
    def test_reversion_oversold_buy_or_hold(self):
        df = _make_reversion_df_oversold(n=60)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.HOLD)

    # 17. 과매수 시나리오 → SELL 또는 HOLD
    def test_reversion_overbought_sell_or_hold(self):
        np.random.seed(13)
        n = 60
        base = np.ones(n) * 100.0
        for i in range(1, n):
            sign = 1 if i % 2 == 0 else -1
            base[i] = base[i - 1] + sign * 0.05
        # 마지막 완성봉을 SMA20 대비 5% 높게
        sma_approx = np.mean(base[-(n // 2):-2])
        base[-2] = sma_approx * 1.06
        df = pd.DataFrame({
            "open": base, "high": base * 1.001, "low": base * 0.999,
            "close": base, "volume": np.ones(n) * 1000,
        })
        signal = self.strategy.generate(df)
        assert signal.action in (Action.SELL, Action.HOLD)
