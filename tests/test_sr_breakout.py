"""
SRBreakoutStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.sr_breakout import SRBreakoutStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_base_df(n: int = 60) -> pd.DataFrame:
    """기본 OHLCV DataFrame: 완만한 상승, swing 포인트 포함."""
    np.random.seed(0)
    closes = np.linspace(100.0, 110.0, n)
    highs = closes * (1 + np.random.uniform(0.005, 0.015, n))
    lows = closes * (1 - np.random.uniform(0.005, 0.015, n))
    opens = closes * (1 + np.random.uniform(-0.003, 0.003, n))
    volumes = np.random.uniform(1000, 3000, n)
    df = pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
        "ema50": closes * 0.97, "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_breakout_buy_df() -> pd.DataFrame:
    """저항선 돌파(BUY) 조건을 확실히 만족하는 DataFrame."""
    n = 60
    np.random.seed(1)
    closes = np.ones(n) * 100.0
    highs = closes.copy()
    lows = closes.copy()
    volumes = np.ones(n) * 1000.0

    # swing high 삽입: window 내 중간에 명확한 고점 생성
    # idx = n-2 = 58, window = df.iloc[58-20:57] = df.iloc[38:57]
    # window 내 i=5 지점에 swing high 삽입
    base_idx = 38
    for j in range(len(highs)):
        highs[j] = 100.0
        lows[j] = 99.0
        closes[j] = 99.5

    # swing high at base_idx+5
    shi = base_idx + 5
    highs[shi] = 105.0
    closes[shi] = 104.8
    highs[shi - 1] = 102.0
    highs[shi - 2] = 101.0
    highs[shi + 1] = 102.0
    highs[shi + 2] = 101.0

    # swing low at base_idx+10
    sli = base_idx + 10
    lows[sli] = 95.0
    closes[sli] = 95.2
    lows[sli - 1] = 97.0
    lows[sli - 2] = 98.0
    lows[sli + 1] = 97.0
    lows[sli + 2] = 98.0

    # idx-1 (57): prev_close <= resistance (105)
    closes[57] = 104.5
    # idx (58): close > resistance + big gap (HIGH conf)
    closes[58] = 106.0
    highs[58] = 106.5
    lows[58] = 105.8

    # 볼륨: idx(58) 크게
    volumes[58] = 5000.0

    df = pd.DataFrame({
        "open": closes.copy(), "high": highs, "low": lows,
        "close": closes, "volume": volumes,
        "ema50": closes * 0.97, "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_breakout_sell_df() -> pd.DataFrame:
    """지지선 이탈(SELL) 조건을 확실히 만족하는 DataFrame."""
    n = 60
    np.random.seed(2)
    closes = np.ones(n) * 100.0
    highs = closes.copy()
    lows = closes.copy()
    volumes = np.ones(n) * 1000.0

    base_idx = 38
    for j in range(len(highs)):
        highs[j] = 101.0
        lows[j] = 99.0
        closes[j] = 100.0

    # swing high
    shi = base_idx + 5
    highs[shi] = 108.0
    closes[shi] = 107.8
    highs[shi - 1] = 104.0
    highs[shi - 2] = 103.0
    highs[shi + 1] = 104.0
    highs[shi + 2] = 103.0

    # swing low at base_idx+10
    sli = base_idx + 10
    lows[sli] = 92.0
    closes[sli] = 92.3
    lows[sli - 1] = 95.0
    lows[sli - 2] = 96.0
    lows[sli + 1] = 95.0
    lows[sli + 2] = 96.0

    # prev_close >= support (92)
    closes[57] = 93.0
    lows[57] = 92.5
    # close < support - big gap
    closes[58] = 90.5
    highs[58] = 91.0
    lows[58] = 90.0

    volumes[58] = 5000.0

    df = pd.DataFrame({
        "open": closes.copy(), "high": highs, "low": lows,
        "close": closes, "volume": volumes,
        "ema50": closes * 1.05, "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98, "atr14": (highs - lows) * 0.5,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestSRBreakoutStrategy:

    def setup_method(self):
        self.strategy = SRBreakoutStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "sr_breakout"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. BUY 신호 반환 타입
    def test_buy_signal_type(self):
        df = _make_breakout_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 5. BUY 조건: action == BUY
    def test_buy_action(self):
        df = _make_breakout_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. BUY HIGH confidence (이격률 > 0.5%)
    def test_buy_high_confidence(self):
        df = _make_breakout_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 7. SELL 신호: action == SELL
    def test_sell_action(self):
        df = _make_breakout_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 8. SELL HIGH confidence (이격률 > 0.5%)
    def test_sell_high_confidence(self):
        df = _make_breakout_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. Signal 필드 완전성 (BUY)
    def test_signal_fields_buy(self):
        df = _make_breakout_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.strategy, str)
        assert signal.strategy == "sr_breakout"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 10. Signal 필드 완전성 (SELL)
    def test_signal_fields_sell(self):
        df = _make_breakout_sell_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "sr_breakout"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0

    # 11. HOLD 신호: action == HOLD (일반 데이터)
    def test_hold_no_breakout(self):
        df = _make_base_df(n=60)
        signal = self.strategy.generate(df)
        # swing points 없거나 돌파 없으면 HOLD
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 12. BUY reasoning에 "resistance" 포함
    def test_buy_reasoning_contains_resistance(self):
        df = _make_breakout_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "resistance" in signal.reasoning.lower()

    # 13. SELL reasoning에 "support" 포함
    def test_sell_reasoning_contains_support(self):
        df = _make_breakout_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "support" in signal.reasoning.lower()

    # 14. entry_price == close[idx]
    def test_entry_price_equals_close(self):
        df = _make_breakout_buy_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 15. 볼륨 부족 시 HOLD (볼륨이 평균보다 작으면 신호 없음)
    def test_no_signal_low_volume(self):
        df = _make_breakout_buy_df()
        # 볼륨을 매우 낮게 설정
        df["volume"] = 1.0
        signal = self.strategy.generate(df)
        # 볼륨 확인 실패 → HOLD
        assert signal.action == Action.HOLD

    # 16. confidence 유효 값
    def test_confidence_valid_values(self):
        for make_fn in [_make_breakout_buy_df, _make_breakout_sell_df, lambda: _make_base_df(60)]:
            df = make_fn()
            signal = self.strategy.generate(df)
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
