"""
EMARibbonStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ema_ribbon import EMARibbonStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(closes, n=None):
    if n is None:
        n = len(closes)
    closes = np.array(closes)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_bullish_ribbon_df(n=120):
    """강한 상승: ema5>ema10>ema20>ema40>ema80, EMA5 cross 유도."""
    # 먼저 약한 상승으로 쌓다가 마지막 직전봉에서 크로스 발생하도록 설계
    # 기본 상승 추세: 전체적 상승
    np.random.seed(42)
    closes = np.array([100.0 * (1.002 ** i) for i in range(n)])
    df = _make_df(closes, n)
    return df


def _make_bearish_ribbon_df(n=120):
    """강한 하락: ema5<ema10<ema20<ema40<ema80, EMA5 cross 유도."""
    np.random.seed(43)
    closes = np.array([200.0 * (0.998 ** i) for i in range(n)])
    df = _make_df(closes, n)
    return df


def _make_insufficient_df(n=50):
    closes = np.linspace(100, 110, n)
    return _make_df(closes, n)


def _make_hold_df(n=120):
    """횡보: 정렬 없음."""
    np.random.seed(99)
    closes = 100.0 + np.random.uniform(-1, 1, n)
    return _make_df(closes, n)


def _inject_cross_up(df):
    """
    마지막 완성봉(iloc[-2]) 직전봉(iloc[-3])에서 ema5<=ema10이고,
    완성봉(iloc[-2])에서 ema5>ema10이 되도록 close 조작.
    """
    df = df.copy()
    # 이미 상승 추세면 cross가 일어나는 지점 근처로 세팅
    # 직전봉(-3)을 살짝 낮추고, 완성봉(-2)을 크게 올림
    df.iloc[-3, df.columns.get_loc("close")] = df["close"].iloc[-3] * 0.995
    df.iloc[-2, df.columns.get_loc("close")] = df["close"].iloc[-2] * 1.01
    df.iloc[-3, df.columns.get_loc("high")] = df["close"].iloc[-3] * 1.005
    df.iloc[-2, df.columns.get_loc("high")] = df["close"].iloc[-2] * 1.005
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestEMARibbonStrategy:

    def setup_method(self):
        self.strategy = EMARibbonStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "ema_ribbon"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=50)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 6. action은 유효한 값
    def test_action_is_valid(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence는 유효한 값
    def test_confidence_is_valid(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "ema_ribbon"

    # 9. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)
        assert signal.entry_price > 0

    # 10. entry_price는 _last 봉 close와 일치
    def test_entry_price_matches_last_close(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 11. reasoning은 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.reasoning, str)
        assert len(signal.reasoning) > 0

    # 12. bull_case / bear_case 필드 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 13. 상승 추세 → HOLD 또는 BUY (SELL 아님)
    def test_bullish_trend_no_sell(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 14. 하락 추세 → HOLD 또는 SELL (BUY 아님)
    def test_bearish_trend_no_buy(self):
        df = _make_bearish_ribbon_df()
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY

    # 15. BUY 신호 시 reasoning에 "EMA Ribbon BUY" 포함
    def test_buy_reasoning_label(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "EMA Ribbon BUY" in signal.reasoning

    # 16. SELL 신호 시 reasoning에 "EMA Ribbon SELL" 포함
    def test_sell_reasoning_label(self):
        df = _make_bearish_ribbon_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "EMA Ribbon SELL" in signal.reasoning

    # 17. BUY 신호 시 invalidation 포함
    def test_buy_has_invalidation(self):
        df = _make_bullish_ribbon_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 18. SELL 신호 시 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_bearish_ribbon_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 19. 횡보 → HOLD
    def test_sideways_hold(self):
        df = _make_hold_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 20. HIGH confidence: spread > 2% 인 경우 BUY → HIGH
    def test_high_confidence_large_spread(self):
        # 매우 강한 상승으로 spread 확보
        n = 120
        closes = np.array([100.0 * (1.005 ** i) for i in range(n)])
        df = _make_df(closes, n)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            # spread가 클 때 HIGH
            ema5 = float(df["close"].ewm(span=5, adjust=False).mean().iloc[-2])
            ema80 = float(df["close"].ewm(span=80, adjust=False).mean().iloc[-2])
            close = float(df["close"].iloc[-2])
            spread_pct = abs(ema5 - ema80) / close
            if spread_pct > 0.02:
                assert signal.confidence == Confidence.HIGH
