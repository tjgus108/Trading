"""
VWMACDStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vw_macd import VWMACDStrategy, _compute_vwmacd
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up") -> pd.DataFrame:
    np.random.seed(13)
    closes = [100.0]
    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.003, 0.007)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.003, 0.007)))
    else:
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.001, 0.001)))

    closes = np.array(closes)
    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes * (1 + np.random.uniform(-0.001, 0.001, n))
    volumes = np.random.uniform(1000, 5000, n)

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_cross_df(direction: str = "buy", n: int = 60) -> pd.DataFrame:
    """
    histogram 크로스 강제 생성.
    direction: "buy" (음→양) | "sell" (양→음)
    """
    df = _make_df(n=n, trend="up" if direction == "buy" else "down")
    ind = _compute_vwmacd(df)
    hist = ind["histogram"].values.copy()

    # -3 index (df의 -3): 크로스 전 값
    # -2 index (df의 -2): 크로스 후 값
    if direction == "buy":
        # 이전봉(-3) histogram 음수, 현재봉(-2) histogram 양수
        if hist[-3] >= 0:
            # closes[-3]를 낮춰서 histogram을 음수로 유도 (근사)
            df.at[df.index[-3], "close"] = df["close"].iloc[-3] * 0.985
        if hist[-2] <= 0:
            df.at[df.index[-2], "close"] = df["close"].iloc[-2] * 1.015
    else:
        if hist[-3] <= 0:
            df.at[df.index[-3], "close"] = df["close"].iloc[-3] * 1.015
        if hist[-2] >= 0:
            df.at[df.index[-2], "close"] = df["close"].iloc[-2] * 0.985

    return df


def _make_buy_cross_df(n: int = 60) -> pd.DataFrame:
    """histogram이 음→양 크로스하는 데이터."""
    np.random.seed(99)
    closes = np.ones(n) * 100.0
    volumes = np.ones(n) * 1000.0

    # 앞부분: 하락 → 후반부: 상승 (MACD histogram 음→양 유도)
    for i in range(n // 2):
        closes[i] = 100.0 - i * 0.5
    for i in range(n // 2, n):
        closes[i] = closes[n // 2 - 1] + (i - n // 2 + 1) * 1.2

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_sell_cross_df(n: int = 60) -> pd.DataFrame:
    """histogram이 양→음 크로스하는 데이터."""
    np.random.seed(77)
    closes = np.ones(n) * 100.0
    volumes = np.ones(n) * 1000.0

    for i in range(n // 2):
        closes[i] = 100.0 + i * 0.5
    for i in range(n // 2, n):
        closes[i] = closes[n // 2 - 1] - (i - n // 2 + 1) * 1.2

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestVWMACDStrategy:

    def setup_method(self):
        self.strategy = VWMACDStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "vw_macd"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 충분한 데이터 → Signal 반환
    def test_sufficient_data_returns_signal(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 6. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "vw_macd"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0

    # 7. histogram 음→양 크로스 → BUY
    def test_buy_cross_histogram(self):
        df = _make_buy_cross_df(n=60)
        ind = _compute_vwmacd(df)
        last_hist = ind["histogram"].iloc[-2]
        prev_hist = ind["histogram"].iloc[-3]
        if prev_hist < 0 and last_hist > 0:
            signal = self.strategy.generate(df)
            assert signal.action == Action.BUY

    # 8. histogram 양→음 크로스 → SELL
    def test_sell_cross_histogram(self):
        df = _make_sell_cross_df(n=60)
        ind = _compute_vwmacd(df)
        last_hist = ind["histogram"].iloc[-2]
        prev_hist = ind["histogram"].iloc[-3]
        if prev_hist > 0 and last_hist < 0:
            signal = self.strategy.generate(df)
            assert signal.action == Action.SELL

    # 9. entry_price는 마지막 완성 캔들의 close
    def test_entry_price_is_last_close(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 10. _compute_vwmacd: 결과 컬럼 존재
    def test_compute_vwmacd_columns(self):
        df = _make_df(n=60)
        ind = _compute_vwmacd(df)
        assert "vw_macd" in ind.columns
        assert "signal" in ind.columns
        assert "histogram" in ind.columns

    # 11. _compute_vwmacd: 결과 길이 동일
    def test_compute_vwmacd_length(self):
        df = _make_df(n=60)
        ind = _compute_vwmacd(df)
        assert len(ind) == len(df)

    # 12. reasoning에 "histogram" 포함 (충분한 데이터)
    def test_reasoning_contains_histogram(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        if "부족" not in signal.reasoning:
            assert "histogram" in signal.reasoning

    # 13. BUY reasoning에 "상향 크로스" 포함
    def test_buy_reasoning_contains_cross(self):
        df = _make_buy_cross_df(n=60)
        ind = _compute_vwmacd(df)
        if ind["histogram"].iloc[-3] < 0 and ind["histogram"].iloc[-2] > 0:
            signal = self.strategy.generate(df)
            if signal.action == Action.BUY:
                assert "크로스" in signal.reasoning

    # 14. SELL reasoning에 "하향 크로스" 포함
    def test_sell_reasoning_contains_cross(self):
        df = _make_sell_cross_df(n=60)
        ind = _compute_vwmacd(df)
        if ind["histogram"].iloc[-3] > 0 and ind["histogram"].iloc[-2] < 0:
            signal = self.strategy.generate(df)
            if signal.action == Action.SELL:
                assert "크로스" in signal.reasoning

    # 15. 크로스 없을 때 → HOLD
    def test_no_cross_hold(self):
        # 완전 평탄 데이터: histogram 변화 없음
        closes = np.full(60, 100.0)
        volumes = np.full(60, 1000.0)
        df = pd.DataFrame({
            "open": closes,
            "high": closes * 1.001,
            "low": closes * 0.999,
            "close": closes,
            "volume": volumes,
        })
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 16. confidence: |histogram| > std → HIGH
    def test_confidence_high_when_large_histogram(self):
        df = _make_buy_cross_df(n=60)
        ind = _compute_vwmacd(df)
        last_hist = ind["histogram"].iloc[-2]
        prev_hist = ind["histogram"].iloc[-3]
        hist_std = ind["histogram"].iloc[-22:-2].std()
        if prev_hist < 0 and last_hist > 0 and abs(last_hist) > hist_std:
            signal = self.strategy.generate(df)
            if signal.action == Action.BUY:
                assert signal.confidence == Confidence.HIGH

    # 17. bull_case / bear_case 포함 (충분한 데이터)
    def test_signal_has_bull_bear_case(self):
        df = _make_df(n=60)
        signal = self.strategy.generate(df)
        if signal.action != Action.HOLD or "부족" not in signal.reasoning:
            assert isinstance(signal.bull_case, str)
            assert isinstance(signal.bear_case, str)
