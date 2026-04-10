"""
NightStarStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.night_star import NightStarStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 20) -> pd.DataFrame:
    """기본 OHLCV DataFrame (중립적 데이터)."""
    np.random.seed(0)
    closes = np.linspace(100.0, 100.0, n)
    opens = closes.copy()
    highs = closes * 1.02
    lows = closes * 0.98
    volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_morning_star(n: int = 20, high_vol: bool = False, doji_star: bool = False) -> pd.DataFrame:
    """
    Morning Star 패턴 삽입:
    idx-2(base): 강한 음봉
    idx-1(star): 도지/소형봉
    idx(confirm): 강한 양봉
    idx = len(df) - 2
    """
    df = _base_df(n)
    idx = len(df) - 2

    # base candle: 강한 음봉
    df.at[idx - 2, "open"] = 105.0
    df.at[idx - 2, "close"] = 98.0  # bearish, body=7, range=8 → ratio=0.875
    df.at[idx - 2, "high"] = 106.0
    df.at[idx - 2, "low"] = 97.0

    # star candle: 소형봉
    if doji_star:
        df.at[idx - 1, "open"] = 97.0
        df.at[idx - 1, "close"] = 97.0  # doji
        df.at[idx - 1, "high"] = 97.5
        df.at[idx - 1, "low"] = 96.5
    else:
        df.at[idx - 1, "open"] = 97.2
        df.at[idx - 1, "close"] = 97.4   # star_body=0.2, range=1.0 → ratio=0.2
        df.at[idx - 1, "high"] = 97.7
        df.at[idx - 1, "low"] = 96.7

    # confirm candle: 강한 양봉
    df.at[idx, "open"] = 97.5
    df.at[idx, "close"] = 103.0  # bullish, body=5.5, range=6 → ratio≈0.92
    df.at[idx, "high"] = 103.5
    df.at[idx, "low"] = 97.0

    if high_vol:
        # 마지막 confirm 봉 volume을 평균의 2배로
        df.at[idx, "volume"] = 5000.0
    else:
        df.at[idx, "volume"] = 500.0  # low volume

    return df


def _make_evening_star(n: int = 20, high_vol: bool = False, doji_star: bool = False) -> pd.DataFrame:
    """
    Evening Star 패턴 삽입:
    idx-2(base): 강한 양봉
    idx-1(star): 도지/소형봉
    idx(confirm): 강한 음봉
    """
    df = _base_df(n)
    idx = len(df) - 2

    # base candle: 강한 양봉
    df.at[idx - 2, "open"] = 95.0
    df.at[idx - 2, "close"] = 102.0  # bullish, body=7, range=8 → ratio=0.875
    df.at[idx - 2, "high"] = 103.0
    df.at[idx - 2, "low"] = 94.0

    # star candle
    if doji_star:
        df.at[idx - 1, "open"] = 102.0
        df.at[idx - 1, "close"] = 102.0  # doji
        df.at[idx - 1, "high"] = 102.5
        df.at[idx - 1, "low"] = 101.5
    else:
        df.at[idx - 1, "open"] = 101.8
        df.at[idx - 1, "close"] = 102.0   # star_body=0.2, range=1.0 → ratio=0.2
        df.at[idx - 1, "high"] = 102.3
        df.at[idx - 1, "low"] = 101.3

    # confirm candle: 강한 음봉
    df.at[idx, "open"] = 101.5
    df.at[idx, "close"] = 96.0  # bearish, body=5.5, range=6 → ratio≈0.92
    df.at[idx, "high"] = 102.0
    df.at[idx, "low"] = 95.5

    if high_vol:
        df.at[idx, "volume"] = 5000.0
    else:
        df.at[idx, "volume"] = 500.0

    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestNightStarStrategy:

    def setup_method(self):
        self.strategy = NightStarStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "night_star"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _base_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _base_df(n=5)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. Morning Star → BUY
    def test_morning_star_buy(self):
        df = _make_morning_star(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 5. Evening Star → SELL
    def test_evening_star_sell(self):
        df = _make_evening_star(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 6. Morning Star doji star → HIGH confidence
    def test_morning_star_doji_high_confidence(self):
        df = _make_morning_star(n=20, doji_star=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY
        assert signal.confidence == Confidence.HIGH

    # 7. Evening Star doji star → HIGH confidence
    def test_evening_star_doji_high_confidence(self):
        df = _make_evening_star(n=20, doji_star=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.HIGH

    # 8. Morning Star high volume → HIGH confidence
    def test_morning_star_high_volume_high_confidence(self):
        df = _make_morning_star(n=20, high_vol=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY
        assert signal.confidence == Confidence.HIGH

    # 9. Evening Star high volume → HIGH confidence
    def test_evening_star_high_volume_high_confidence(self):
        df = _make_evening_star(n=20, high_vol=True)
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.HIGH

    # 10. 중립 데이터 → HOLD
    def test_neutral_data_hold(self):
        df = _base_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_morning_star(n=20)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "night_star"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 12. BUY reasoning에 "Morning Star" 포함
    def test_buy_reasoning_contains_morning_star(self):
        df = _make_morning_star(n=20)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "Morning Star" in signal.reasoning

    # 13. SELL reasoning에 "Evening Star" 포함
    def test_sell_reasoning_contains_evening_star(self):
        df = _make_evening_star(n=20)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "Evening Star" in signal.reasoning

    # 14. BUY 신호 bull_case/bear_case 포함
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_morning_star(n=20)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 15. SELL 신호 bull_case/bear_case 포함
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_evening_star(n=20)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. base 강한 양봉인데 confirm도 양봉이면 Evening Star 미감지 → HOLD
    def test_evening_star_not_triggered_if_confirm_bullish(self):
        df = _make_evening_star(n=20)
        idx = len(df) - 2
        # confirm candle을 양봉으로 변경
        df.at[idx, "open"] = 96.0
        df.at[idx, "close"] = 101.5
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 17. HOLD confidence LOW
    def test_hold_confidence_low(self):
        df = _base_df(n=20)
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert signal.confidence == Confidence.LOW
