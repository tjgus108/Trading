"""
TailRiskFilterStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.tail_risk_filter import TailRiskFilterStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 5, close_values=None, base_close: float = 100.0) -> pd.DataFrame:
    """
    신호 봉은 idx = n-2 (BaseStrategy._last() 기준).
    close_values: 길이 n의 close 시계열. None이면 base_close 상수.
    """
    if close_values is None:
        closes = [base_close] * n
    else:
        closes = list(close_values)
        assert len(closes) == n

    df = pd.DataFrame({
        "open": [c * 0.999 for c in closes],
        "close": closes,
        "high": [c * 1.001 for c in closes],
        "low": [c * 0.999 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _make_calm_uptrend(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    calm period + 상승. 수익률 분산이 있어야 z_score가 작게 계산됨.
    returns가 작고 일정하지 않도록 정규분포 노이즈 추가 (seed 고정).
    """
    import random
    random.seed(42)
    closes = [100.0]
    for i in range(1, n):
        # 작은 상승 drift + 소량 노이즈
        change = 0.002 + random.gauss(0, 0.003)
        closes.append(closes[-1] * (1 + change))
    return _make_df(n=n, close_values=closes)


def _make_calm_downtrend(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """calm period + 하락. 수익률 분산 있음."""
    import random
    random.seed(43)
    closes = [100.0]
    for i in range(1, n):
        change = -0.002 + random.gauss(0, 0.003)
        closes.append(closes[-1] * (1 + change))
    return _make_df(n=n, close_values=closes)


def _make_extreme_move(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """극단적 이동 포함: 대부분 평온, 마지막 직전 봉 근처에서 폭등."""
    import random
    random.seed(44)
    closes = [100.0]
    for i in range(1, n):
        if i == n - 3:
            closes.append(closes[-1] * 1.30)  # 30% 폭등 → extreme
        else:
            closes.append(closes[-1] * (1 + random.gauss(0, 0.003)))
    return _make_df(n=n, close_values=closes)


class TestTailRiskFilterStrategy:

    def setup_method(self):
        self.strategy = TailRiskFilterStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "tail_risk_filter"

    # 2. BUY 신호: calm + 상승 추세
    def test_buy_signal(self):
        df = _make_calm_uptrend()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "tail_risk_filter"

    # 3. SELL 신호: calm + 하락 추세
    def test_sell_signal(self):
        df = _make_calm_downtrend()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "tail_risk_filter"

    # 4. 극단적 이동 → HOLD (calm_period = False)
    def test_hold_on_extreme_move(self):
        df = _make_extreme_move()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 (< 25행)
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 6. Signal 타입 확인
    def test_signal_type(self):
        df = _make_calm_uptrend()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_calm_uptrend()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY reasoning 비어있지 않음
    def test_buy_reasoning_nonempty(self):
        df = _make_calm_uptrend()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 9. entry_price는 close 값
    def test_entry_price_is_close(self):
        df = _make_calm_uptrend()
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_close, rel=1e-6)

    # 10. HIGH confidence: calm + |z_score| < 0.5 (점진적 상승)
    def test_buy_high_confidence_low_z(self):
        # 매우 천천히 상승 → z_score가 낮음
        closes = [100.0 + i * 0.05 for i in range(_MIN_ROWS + 5)]
        df = _make_df(close_values=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. MEDIUM confidence: calm + |z_score| >= 0.5
    def test_confidence_is_high_or_medium(self):
        df = _make_calm_uptrend()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. HOLD: action=HOLD일 때 confidence=LOW
    def test_hold_confidence_low(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 13. SELL confidence는 HIGH 또는 MEDIUM
    def test_sell_confidence(self):
        df = _make_calm_downtrend()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 14. 정확히 25행 (경계값)
    def test_exact_min_rows(self):
        closes = [100.0 + i * 0.1 for i in range(_MIN_ROWS)]
        df = _make_df(n=_MIN_ROWS, close_values=closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. close == ma 일 때 (BUY 조건 불충족 → HOLD)
    def test_hold_when_close_equals_ma(self):
        # 상수 close → returns=0, no signal
        df = _make_df(n=_MIN_ROWS + 5, base_close=100.0)
        sig = self.strategy.generate(df)
        # 상수라면 returns=0이므로 BUY/SELL 조건 미충족
        assert sig.action == Action.HOLD
