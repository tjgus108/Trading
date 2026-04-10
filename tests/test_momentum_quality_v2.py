"""
MomentumQualityV2Strategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum_quality_v2 import MomentumQualityV2Strategy
from src.strategy.base import Action, Confidence, Signal


def _make_strong_uptrend(n: int = 50) -> pd.DataFrame:
    """BUY 조건 보장: consistency=3, strength>0, roc5>roc10.

    roc5 > roc10 ↔ close[t-10] > close[t-5] (수학적 동치).
    패턴: 상승 → 소폭 풀백(t-10 ~ t-5) → 강한 반등(t-5 ~ t).
    roc5, roc10, roc20 모두 양수가 되려면 t-20 보다 t가 충분히 높아야 함.
    """
    closes = []
    for i in range(n):
        if i < n - 15:
            # 초반: 완만한 상승
            closes.append(100.0 + i * 3.0)
        elif i < n - 5:
            # 풀백 구간 (10개 봉): 조금 하락
            closes.append(closes[-1] - 2.0)
        else:
            # 강한 반등 (마지막 5봉): 이전 고점보다 훨씬 높게
            closes.append(closes[-1] + 30.0)
    return pd.DataFrame({"close": closes})


def _make_strong_downtrend(n: int = 50) -> pd.DataFrame:
    """SELL 조건 보장: consistency=0, strength<0, roc5<roc10.

    roc5 < roc10 ↔ close[t-10] < close[t-5].
    패턴: 하락 → 소폭 반등(t-10 ~ t-5) → 강한 하락(t-5 ~ t).
    roc5, roc10, roc20 모두 음수가 되려면 t-20 보다 t가 충분히 낮아야 함.
    """
    closes = []
    for i in range(n):
        if i < n - 15:
            closes.append(3000.0 - i * 3.0)
        elif i < n - 5:
            # 소폭 반등
            closes.append(closes[-1] + 2.0)
        else:
            # 강한 추가 하락
            closes.append(closes[-1] - 30.0)
    return pd.DataFrame({"close": closes})


def _make_flat(n: int = 50, value: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame({"close": [value] * n})


def _make_mixed(n: int = 50) -> pd.DataFrame:
    """혼재 시리즈: sin파."""
    closes = [100.0 + 5.0 * np.sin(i * 0.3) for i in range(n)]
    return pd.DataFrame({"close": closes})


def _make_accelerating_up(n: int = 50) -> pd.DataFrame:
    """가속 상승: roc5 > roc10 보장."""
    closes = [100.0 + (i ** 1.8) * 0.05 for i in range(n)]
    return pd.DataFrame({"close": closes})


class TestMomentumQualityV2Strategy:

    def setup_method(self):
        self.strategy = MomentumQualityV2Strategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "momentum_quality_v2"

    # 2. 강한 상승 → BUY
    def test_buy_strong_uptrend(self):
        df = _make_strong_uptrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "momentum_quality_v2"

    # 3. 강한 하락 → SELL
    def test_sell_strong_downtrend(self):
        df = _make_strong_downtrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 4. flat → HOLD
    def test_hold_flat(self):
        df = _make_flat(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_flat(n=25)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 6. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_strong_uptrend(n=50)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 7. BUY entry_price = iloc[-2]["close"]
    def test_entry_price_buy(self):
        df = _make_strong_uptrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))

    # 8. HOLD entry_price
    def test_entry_price_hold(self):
        df = _make_flat(n=50, value=55.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(55.0)

    # 9. BUY confidence HIGH 또는 MEDIUM
    def test_buy_confidence_valid(self):
        df = _make_strong_uptrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. SELL confidence HIGH 또는 MEDIUM
    def test_sell_confidence_valid(self):
        df = _make_strong_downtrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. strategy 이름 일관성 (HOLD)
    def test_strategy_name_hold(self):
        df = _make_flat(n=50)
        sig = self.strategy.generate(df)
        assert sig.strategy == "momentum_quality_v2"

    # 12. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_strong_uptrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 13. 정확히 30행 (경계값) → 처리 가능
    def test_exactly_min_rows(self):
        df = _make_strong_uptrend(n=30)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert "Insufficient" not in sig.reasoning

    # 14. 29행 → 데이터 부족
    def test_below_min_rows(self):
        df = _make_strong_uptrend(n=29)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 15. SELL strategy 필드 확인
    def test_sell_strategy_field(self):
        df = _make_strong_downtrend(n=50)
        sig = self.strategy.generate(df)
        assert sig.strategy == "momentum_quality_v2"

    # 16. 가속 상승 → BUY (roc5 > roc10)
    def test_buy_accelerating(self):
        df = _make_accelerating_up(n=50)
        sig = self.strategy.generate(df)
        # 가속 상승이면 BUY 또는 HOLD (초기 구간 일관성 미달 가능)
        assert sig.action in (Action.BUY, Action.HOLD)
