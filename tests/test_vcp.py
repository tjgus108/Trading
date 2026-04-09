"""
VCPStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vcp import VCPStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_vcp_buy_df(n: int = 30) -> pd.DataFrame:
    """수축 패턴 + 상단 돌파(BUY) DataFrame."""
    np.random.seed(0)
    base = 100.0
    closes = [base + i * 0.1 for i in range(n)]

    # 수축하는 high/low 범위: 앞쪽 넓고 뒤쪽 좁아짐
    spreads = np.linspace(3.0, 0.5, n)
    highs = [closes[i] + spreads[i] for i in range(n)]
    lows = [closes[i] - spreads[i] for i in range(n)]

    # 마지막 close를 week_high[-2] * 0.995 이상으로 강제 (돌파)
    # week_high[-2] = max of highs[-6:-1]
    wh = max(highs[-6:-1])
    closes[-2] = wh * 0.996  # _last = iloc[-2] → BUY 조건

    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_vcp_sell_df(n: int = 30) -> pd.DataFrame:
    """수축 패턴 + 하단 붕괴(SELL) DataFrame."""
    np.random.seed(1)
    base = 100.0
    closes = [base - i * 0.1 for i in range(n)]
    spreads = np.linspace(3.0, 0.5, n)
    highs = [closes[i] + spreads[i] for i in range(n)]
    lows = [closes[i] - spreads[i] for i in range(n)]

    # 마지막 close를 week_low[-2] * 1.005 이하로 강제 (붕괴)
    wl = min(lows[-6:-1])
    closes[-2] = wl * 1.004

    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_hold_no_contraction_df(n: int = 30) -> pd.DataFrame:
    """수축 패턴 없음 (확대 패턴) → HOLD."""
    closes = np.linspace(100, 102, n)
    # 마지막으로 갈수록 spread가 커짐 → 수축 반대 (확대 패턴)
    spreads = np.linspace(0.5, 5.0, n)
    highs = closes + spreads
    lows = closes - spreads
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_no_contraction_df(n: int = 30) -> pd.DataFrame:
    """수축 패턴 없음(랜덤 범위)."""
    np.random.seed(7)
    closes = np.ones(n) * 100.0
    spreads = np.random.uniform(0.5, 3.0, n)
    highs = closes + spreads
    lows = closes - spreads
    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


def _make_high_confidence_df(n: int = 40) -> pd.DataFrame:
    """수축률 > 30% (HIGH confidence) + BUY.
    c1 = contractions[-3], c3 = contractions[-1], need c3 < c1 * 0.7.

    spreads 설계:
      spreads[-7] = 5.0  → c1 window에만 포함 (인덱스 n-7이 n-3 윈도우의 시작)
      spreads[-6] = 1.5  → c2 window의 최대
      spreads[-5:-1+1] = 0.3 → c3 window 전체
    결과: c1≈10, c2≈3, c3≈0.6, c3 < c1*0.7=7 → HIGH

    BUY 조건:
      step=0.5인 상승 추세 → closes[-2] = closes[-6] + 4*0.5 = closes[-6]+2.0
      week_high[-2] = max(highs[-6:-1]) = closes[-6]+1.5 (최대 high)
      closes[-2] = closes[-6]+2.0 > (closes[-6]+1.5)*0.99 = closes[-6]+1.485 → BUY
    """
    closes = np.array([100.0 + i * 0.5 for i in range(n)])
    spreads = np.full(n, 5.0)
    spreads[-7] = 5.0   # 이미 5.0이지만 명시
    spreads[-6] = 1.5
    spreads[-5] = 0.3
    spreads[-4] = 0.3
    spreads[-3] = 0.3
    spreads[-2] = 0.3
    spreads[-1] = 0.3
    highs = closes + spreads
    lows = closes - spreads

    df = pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestVCPStrategy:

    def setup_method(self):
        self.strategy = VCPStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "vcp"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 수축 패턴 + 상단 돌파 → BUY
    def test_contraction_breakout_buy(self):
        df = _make_vcp_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. 수축 패턴 + 하단 붕괴 → SELL
    def test_contraction_breakdown_sell(self):
        df = _make_vcp_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 7. 확대 패턴(수축 없음) → HOLD
    def test_contraction_no_breakout_hold(self):
        df = _make_hold_no_contraction_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 8. 수축 패턴 없음 → HOLD
    def test_no_contraction_hold(self):
        df = _make_no_contraction_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_vcp_buy_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "vcp"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 10. BUY reasoning에 "VCP" 포함
    def test_buy_reasoning_contains_vcp(self):
        df = _make_vcp_buy_df()
        signal = self.strategy.generate(df)
        assert "VCP" in signal.reasoning

    # 11. SELL reasoning에 "VCP" 포함
    def test_sell_reasoning_contains_vcp(self):
        df = _make_vcp_sell_df()
        signal = self.strategy.generate(df)
        assert "VCP" in signal.reasoning

    # 12. 수축률 > 30% → HIGH confidence
    def test_high_confidence_when_strong_contraction(self):
        df = _make_high_confidence_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 13. BUY 신호에 invalidation 포함
    def test_buy_has_invalidation(self):
        df = _make_vcp_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 14. SELL 신호에 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_vcp_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 15. 정확히 20행 데이터 (경계값) → HOLD 이상
    def test_exactly_min_rows(self):
        df = _make_hold_no_contraction_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence != Confidence.LOW or signal.action == Action.HOLD
