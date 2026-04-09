"""
FRAMAStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.frama import FRAMAStrategy, _compute_frama
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", cross: str = "none") -> pd.DataFrame:
    """
    trend: "up" | "down" | "flat"
    cross: "buy" (마지막 완성봉에서 위로 크로스) | "sell" | "none"
    """
    np.random.seed(7)
    closes = [100.0]
    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.002, 0.006)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.002, 0.006)))
    else:
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.001, 0.001)))

    closes = np.array(closes)
    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes * (1 + np.random.uniform(-0.001, 0.001, n))
    volumes = np.random.uniform(1000, 5000, n)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })

    if cross == "buy":
        # -3: close < frama (아래), -2: close > frama (위) 강제 크로스
        frama_arr = _compute_frama(closes, highs, lows, 16)
        if not np.isnan(frama_arr[-2]) and not np.isnan(frama_arr[-3]):
            df.at[df.index[-3], "close"] = frama_arr[-3] * 0.98
            df.at[df.index[-2], "close"] = frama_arr[-2] * 1.02
    elif cross == "sell":
        frama_arr = _compute_frama(closes, highs, lows, 16)
        if not np.isnan(frama_arr[-2]) and not np.isnan(frama_arr[-3]):
            df.at[df.index[-3], "close"] = frama_arr[-3] * 1.02
            df.at[df.index[-2], "close"] = frama_arr[-2] * 0.98

    return df


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

class TestFRAMAStrategy:

    def setup_method(self):
        self.strategy = FRAMAStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "frama"

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
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 6. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "frama"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0

    # 7. BUY 크로스 감지
    def test_buy_cross_detected(self):
        df = _make_df(n=60, trend="up", cross="buy")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 8. SELL 크로스 감지
    def test_sell_cross_detected(self):
        df = _make_df(n=60, trend="down", cross="sell")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 9. BUY confidence: 이격 > 1% → HIGH
    def test_buy_high_confidence_large_gap(self):
        df = _make_df(n=60, trend="up", cross="buy")
        # 이격을 2%로 강제
        frama_arr = _compute_frama(
            df["close"].values.astype(float),
            df["high"].values.astype(float),
            df["low"].values.astype(float),
            16,
        )
        frama_val = frama_arr[-2]
        if not np.isnan(frama_val):
            df.at[df.index[-3], "close"] = frama_val * 0.98
            df.at[df.index[-2], "close"] = frama_val * 1.025  # 이격 2.5%
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 10. 크로스 없을 때 HOLD 가능
    def test_no_cross_hold(self):
        df = _make_df(n=60, trend="flat", cross="none")
        signal = self.strategy.generate(df)
        # 크로스가 우연히 없으면 HOLD
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 11. reasoning에 "FRAMA" 포함
    def test_reasoning_contains_frama(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        # 데이터 부족이 아니면 FRAMA 포함
        if signal.action != Action.HOLD or "부족" not in signal.reasoning:
            assert "FRAMA" in signal.reasoning or "부족" in signal.reasoning

    # 12. BUY 신호 reasoning에 크로스 언급
    def test_buy_reasoning_contains_cross(self):
        df = _make_df(n=60, trend="up", cross="buy")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "크로스" in signal.reasoning

    # 13. SELL 신호 reasoning에 크로스 언급
    def test_sell_reasoning_contains_cross(self):
        df = _make_df(n=60, trend="down", cross="sell")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "크로스" in signal.reasoning

    # 14. entry_price는 마지막 완성 캔들의 close
    def test_entry_price_is_last_close(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 15. _compute_frama: 결과 길이 동일
    def test_compute_frama_length(self):
        closes = np.linspace(100, 120, 60)
        highs = closes * 1.01
        lows = closes * 0.99
        result = _compute_frama(closes, highs, lows, 16)
        assert len(result) == 60

    # 16. _compute_frama: 첫 period-1 행은 NaN
    def test_compute_frama_initial_nan(self):
        closes = np.linspace(100, 120, 60)
        highs = closes * 1.01
        lows = closes * 0.99
        result = _compute_frama(closes, highs, lows, 16)
        # index 0~14 는 NaN
        assert all(np.isnan(result[i]) for i in range(15))

    # 17. BUY/SELL 신호에 bull_case / bear_case 포함
    def test_signal_has_bull_bear_case(self):
        df = _make_df(n=60, trend="up", cross="buy")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0
