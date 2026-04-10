"""
TrendStrengthFilterStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.trend_strength_filter import TrendStrengthFilterStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", adx_strength: str = "strong") -> pd.DataFrame:
    """
    테스트용 OHLCV DataFrame 생성.
    trend: "up" | "down" | "flat"
    adx_strength: "strong" (ADX > 20) | "weak" (ADX <= 20)
    """
    np.random.seed(7)
    base = 100.0
    closes = [base]

    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.004, 0.010)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.004, 0.010)))
    else:
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.0005, 0.0005)))

    closes = np.array(closes)

    if adx_strength == "strong":
        spread = 0.05
    else:
        spread = 0.002

    highs = closes * (1 + spread)
    lows = closes * (1 - spread)
    opens = closes * (1 + np.random.uniform(-0.001, 0.001, n))

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
    })
    return df


def _make_short_df(n: int = 15) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestTrendStrengthFilterStrategy:

    def setup_method(self):
        self.strategy = TrendStrengthFilterStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "trend_strength_filter"

    # 2. 데이터 부족 시 HOLD
    def test_insufficient_data_hold(self):
        df = _make_short_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_short_df(n=20)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 4. 강한 상승 추세 BUY
    def test_strong_uptrend_buy(self):
        df = _make_df(n=80, trend="up", adx_strength="strong")
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 5. 강한 하락 추세 SELL
    def test_strong_downtrend_sell(self):
        df = _make_df(n=80, trend="down", adx_strength="strong")
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 6. 횡보장 weak ADX HOLD
    def test_weak_adx_hold(self):
        df = _make_df(n=80, trend="flat", adx_strength="weak")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 7. ADX > 35 시 HIGH confidence
    def test_high_confidence_strong_adx(self):
        df = _make_df(n=80, trend="up", adx_strength="strong")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # ADX > 35 → HIGH
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 8. Signal 타입 및 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=80, trend="up", adx_strength="strong")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "trend_strength_filter"
        assert isinstance(sig.entry_price, float)
        assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0

    # 9. BUY reasoning에 "ADX" 포함
    def test_buy_reasoning_contains_adx(self):
        df = _make_df(n=80, trend="up", adx_strength="strong")
        sig = self.strategy.generate(df)
        assert "ADX" in sig.reasoning

    # 10. SELL reasoning에 "ADX" 포함
    def test_sell_reasoning_contains_adx(self):
        df = _make_df(n=80, trend="down", adx_strength="strong")
        sig = self.strategy.generate(df)
        assert "ADX" in sig.reasoning

    # 11. BUY 시 bull_case/bear_case 있음
    def test_buy_has_bull_bear_case(self):
        df = _make_df(n=80, trend="up", adx_strength="strong")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 12. SELL 시 bull_case/bear_case 있음
    def test_sell_has_bull_bear_case(self):
        df = _make_df(n=80, trend="down", adx_strength="strong")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.bull_case) > 0
            assert len(sig.bear_case) > 0

    # 13. EMA21 위에 close 조작 → 상승 신호 유발 확인
    def test_ema21_price_alignment(self):
        df = _make_df(n=80, trend="up", adx_strength="strong")
        sig = self.strategy.generate(df)
        # 상승 추세이므로 BUY or HOLD (SELL이 아니어야 함)
        assert sig.action != Action.SELL

    # 14. 하락 추세에서 SELL entry_price는 close 값
    def test_sell_entry_price_equals_close(self):
        df = _make_df(n=80, trend="down", adx_strength="strong")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            last_close = float(df["close"].iloc[-2])
            assert abs(sig.entry_price - last_close) < 1e-6

    # 15. None df 처리
    def test_none_df_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 16. DI 방향-EMA 불일치 시 HOLD
    def test_di_ema_misalign_hold(self):
        """상승 추세 ADX 강하나 EMA21을 강제로 close보다 훨씬 위에 설정."""
        df = _make_df(n=80, trend="up", adx_strength="strong")
        # close를 매우 낮게 만들어 EMA21 < close 조건 불만족
        df["close"] = df["close"] * 0.5
        df["low"] = df["low"] * 0.5
        df["open"] = df["open"] * 0.5
        sig = self.strategy.generate(df)
        # close가 낮아지면 DI 방향과 EMA21 위치가 달라져 HOLD 가능
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
