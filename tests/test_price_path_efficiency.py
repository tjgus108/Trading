"""
PricePathEfficiencyStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_path_efficiency import PricePathEfficiencyStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20
_LOOKBACK = 8


def _make_df(n: int = _MIN_ROWS + 5, close_values=None, base_close: float = 100.0) -> pd.DataFrame:
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


def _make_efficient_uptrend(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """
    대부분 지그재그(저효율) → 마지막 LOOKBACK+6 봉만 직선 상승(고효율).
    efficiency_ma(5)가 아직 수렴하지 않은 시점에 idx 위치 → eff > eff_ma.
    """
    transition = _LOOKBACK + 4   # 지그재그에서 직선으로 바뀌는 위치 (끝에서)
    closes = []
    base = 100.0
    for i in range(n):
        if i < n - transition:
            closes.append(base + (i % 2) * 2.0)
        else:
            step = i - (n - transition)
            closes.append(base + step * 3.0)
    return _make_df(n=n, close_values=closes)


def _make_efficient_downtrend(n: int = _MIN_ROWS + 10) -> pd.DataFrame:
    """대부분 지그재그 → 마지막 구간 직선 하락. trend_up=False."""
    transition = _LOOKBACK + 4
    closes = []
    base = 100.0
    for i in range(n):
        if i < n - transition:
            closes.append(base + (i % 2) * 2.0)
        else:
            step = i - (n - transition)
            closes.append(base - step * 3.0)
    return _make_df(n=n, close_values=closes)


def _make_choppy(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    지그재그 → total_path 크고 net_change 작음 → efficiency < 0.5
    """
    closes = []
    for i in range(n):
        if i % 2 == 0:
            closes.append(100.0)
        else:
            closes.append(102.0)
    return _make_df(n=n, close_values=closes)


class TestPricePathEfficiencyStrategy:

    def setup_method(self):
        self.strategy = PricePathEfficiencyStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "price_path_efficiency"

    # 2. BUY 신호: 효율적 상승 추세
    def test_buy_signal(self):
        df = _make_efficient_uptrend()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "price_path_efficiency"

    # 3. SELL 신호: 효율적 하락 추세
    def test_sell_signal(self):
        df = _make_efficient_downtrend()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "price_path_efficiency"

    # 4. 지그재그 (efficiency < 0.5) → HOLD
    def test_hold_on_choppy(self):
        df = _make_choppy()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 6. Signal 타입 확인
    def test_signal_type(self):
        df = _make_efficient_uptrend()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_efficient_uptrend()
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
        df = _make_efficient_uptrend()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 9. entry_price는 신호 봉 close
    def test_entry_price_is_close(self):
        df = _make_efficient_uptrend()
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_close, rel=1e-6)

    # 10. HIGH confidence: efficiency > 0.75
    def test_buy_high_confidence(self):
        # 직선 상승 → efficiency ≈ 1.0 > 0.75
        df = _make_efficient_uptrend()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence: 0.5 < efficiency <= 0.75
    def test_sell_high_confidence_on_efficient_downtrend(self):
        df = _make_efficient_downtrend()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. HOLD confidence=LOW
    def test_hold_confidence_low(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 13. 정확히 20행 (경계값)
    def test_exact_min_rows(self):
        closes = [100.0 + i * 1.0 for i in range(_MIN_ROWS)]
        df = _make_df(n=_MIN_ROWS, close_values=closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. 상수 close → efficiency ≈ 0 → HOLD
    def test_hold_on_constant_close(self):
        df = _make_df(n=_MIN_ROWS + 5, base_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. BUY일 때 bull_case 비어있지 않음
    def test_buy_bull_case_nonempty(self):
        df = _make_efficient_uptrend()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.bull_case != ""
