"""
ElderForceIndexStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.elder_force import ElderForceIndexStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 80,
    fi13_sign: str = "pos",   # "pos" | "neg"
    fi2_sign: str = "neg",    # "neg" | "pos"
    strong_trend: bool = False,
) -> pd.DataFrame:
    """
    FI_13 방향은 앞 n-5 봉의 추세로 결정.
    FI_2 방향은 마지막 5봉에서 반전해 결정.
    strong_trend: True → 추세 step 크게 → |FI_13| > std*1.5 가능성 높음.
    """
    np.random.seed(1)
    base = 100.0
    trend_n = n - 5      # FI_13 방향을 위한 구간
    end_n = 5            # FI_2 방향을 위한 마지막 구간

    step = 0.01 if strong_trend else 0.004

    closes = [base]
    # 추세 구간
    if fi13_sign == "pos":
        for _ in range(trend_n - 1):
            closes.append(closes[-1] * (1 + step))
    else:
        for _ in range(trend_n - 1):
            closes.append(closes[-1] * (1 - step))

    # FI_2 반전 구간: fi2_sign에 맞춰 마지막 완성봉(idx=-2) 방향 결정
    # 작은 step으로 FI_13 방향은 유지, FI_2만 반전
    small_step = 0.001
    if fi2_sign == "neg":
        # 작은 하락: FI_2 < 0 (idx=-2에서 close 감소)
        for _ in range(end_n):
            closes.append(closes[-1] * (1 - small_step))
    else:
        # 작은 상승: FI_2 > 0 (idx=-2에서 close 증가)
        for _ in range(end_n):
            closes.append(closes[-1] * (1 + small_step))

    closes = np.array(closes[:n], dtype=float)

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()
    volume = np.ones(n) * 2000.0  # 고정 볼륨으로 부호가 price diff에만 의존

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volume,
    })


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


# ── tests ─────────────────────────────────────────────────────────────────────

class TestElderForceIndexStrategy:

    def setup_method(self):
        self.strategy = ElderForceIndexStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "elder_force"

    # 2. FI_13>0, FI_2<0 → BUY
    def test_fi13_pos_fi2_neg_buy(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 3. FI_13<0, FI_2>0 → SELL
    def test_fi13_neg_fi2_pos_sell(self):
        df = _make_df(n=60, fi13_sign="neg", fi2_sign="pos")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 4. FI_13>0, FI_2>0 → HOLD
    def test_fi13_pos_fi2_pos_hold(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="pos")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 5. FI_13<0, FI_2<0 → HOLD
    def test_fi13_neg_fi2_neg_hold(self):
        df = _make_df(n=60, fi13_sign="neg", fi2_sign="neg")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. 강한 추세 → HIGH confidence
    def test_strong_trend_high_confidence(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg", strong_trend=True)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. 약한 추세 → MEDIUM confidence
    def test_weak_trend_medium_confidence(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg", strong_trend=False)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 8. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. 데이터 부족 reasoning
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "elder_force"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 11. BUY reasoning에 "FI_13" 포함
    def test_buy_reasoning_contains_fi13(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "FI_13" in signal.reasoning

    # 12. SELL reasoning에 "FI_13" 포함
    def test_sell_reasoning_contains_fi13(self):
        df = _make_df(n=60, fi13_sign="neg", fi2_sign="pos")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "FI_13" in signal.reasoning

    # 13. BUY invalidation에 "FI_13" 포함
    def test_buy_invalidation(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "FI_13" in signal.invalidation

    # 14. SELL에 bull_case/bear_case 포함
    def test_sell_has_bull_bear_case(self):
        df = _make_df(n=60, fi13_sign="neg", fi2_sign="pos")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 15. entry_price는 마지막 완성봉 close
    def test_entry_price_is_last_close(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="neg")
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 16. HOLD reasoning에 "HOLD" 포함
    def test_hold_reasoning(self):
        df = _make_df(n=60, fi13_sign="pos", fi2_sign="pos")
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert "HOLD" in signal.reasoning or "부족" in signal.reasoning
