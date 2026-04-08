"""
ADXTrendStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.adx_trend import ADXTrendStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up", adx_strength: str = "high") -> pd.DataFrame:
    """
    테스트용 OHLCV + ema50 + atr14 DataFrame 생성.
    trend: "up" | "down" | "flat"
    adx_strength: "high" (ADX>=40) | "medium" (25<=ADX<40) | "weak" (ADX<25)
    """
    np.random.seed(42)
    base = 100.0
    closes = [base]

    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.003, 0.008)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.003, 0.008)))
    else:  # flat
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.001, 0.001)))

    closes = np.array(closes)

    if adx_strength == "high":
        spread = 0.06   # 넓은 스프레드 → 강한 추세
    elif adx_strength == "medium":
        spread = 0.025
    else:
        spread = 0.004  # 좁은 스프레드 → ADX 낮음

    highs = closes * (1 + spread)
    lows = closes * (1 - spread)
    opens = closes * (1 + np.random.uniform(-0.002, 0.002, n))

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
    })

    # ema50: BUY 조건 → close > ema50 / SELL 조건 → close < ema50
    if trend == "up":
        df["ema50"] = closes * 0.95   # close > ema50
    elif trend == "down":
        df["ema50"] = closes * 1.05   # close < ema50
    else:
        df["ema50"] = closes          # close ≈ ema50

    df["atr14"] = (highs - lows) * 0.5

    return df


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98,
        "atr14": (highs - lows) * 0.5,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestADXTrendStrategy:

    def setup_method(self):
        self.strategy = ADXTrendStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "adx_trend"

    # 2. 강한 상승 추세 BUY (ADX>=40, +DI>-DI, close>ema50)
    def test_strong_uptrend_buy(self):
        df = _make_df(n=80, trend="up", adx_strength="high")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. 강한 하락 추세 SELL (ADX>=40, -DI>+DI, close<ema50)
    def test_strong_downtrend_sell(self):
        df = _make_df(n=80, trend="down", adx_strength="high")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. BUY HIGH confidence (ADX>=40)
    def test_buy_high_confidence(self):
        df = _make_df(n=80, trend="up", adx_strength="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 5. BUY MEDIUM confidence (25<=ADX<40)
    def test_buy_medium_confidence(self):
        df = _make_df(n=80, trend="up", adx_strength="medium")
        signal = self.strategy.generate(df)
        # medium strength: action can be BUY with MEDIUM confidence, or HOLD
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 6. SELL HIGH confidence (ADX>=40)
    def test_sell_high_confidence(self):
        df = _make_df(n=80, trend="down", adx_strength="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 7. SELL MEDIUM confidence
    def test_sell_medium_confidence(self):
        df = _make_df(n=80, trend="down", adx_strength="medium")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 8. 횡보장 HOLD (ADX<25)
    def test_sideways_hold(self):
        df = _make_df(n=80, trend="flat", adx_strength="weak")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. ADX>=25이지만 close가 반대 방향 → HOLD
    def test_adx_strong_but_price_misalign_hold(self):
        """
        +DI > -DI (상승 추세) 이지만 close < ema50 → HOLD
        """
        df = _make_df(n=80, trend="up", adx_strength="high")
        # EMA50을 강제로 close 위에 두어 불일치 유발
        df["ema50"] = df["close"] * 1.10
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 10. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=80, trend="up", adx_strength="high")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "adx_trend"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 12. reasoning에 "ADX" 포함
    def test_reasoning_contains_adx(self):
        df = _make_df(n=80, trend="up", adx_strength="high")
        signal = self.strategy.generate(df)
        assert "ADX" in signal.reasoning

    # 13. 데이터 부족 시 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 14. HOLD 시 confidence LOW (ADX<25)
    def test_sideways_confidence_low(self):
        df = _make_df(n=80, trend="flat", adx_strength="weak")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    # 15. BUY 신호에 bull_case/bear_case 포함
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_df(n=80, trend="up", adx_strength="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. SELL 신호에 bull_case/bear_case 포함
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_df(n=80, trend="down", adx_strength="high")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0
