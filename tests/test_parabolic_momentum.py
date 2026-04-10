"""
ParabolicMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.parabolic_momentum import ParabolicMomentumStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(n: int = _MIN_ROWS + 5,
             close_vals: "list[float] | None" = None) -> pd.DataFrame:
    """기본 DataFrame 생성. _last(df) = df.iloc[-2] 기준."""
    if close_vals is None:
        close_vals = [100.0] * n
    else:
        while len(close_vals) < n:
            close_vals = [close_vals[0]] + close_vals
        close_vals = close_vals[-n:]

    closes = pd.Series(close_vals, dtype=float)
    highs = closes + 1.0
    lows = closes - 1.0

    return pd.DataFrame({
        "open": closes.values,
        "high": highs.values,
        "low": lows.values,
        "close": closes.values,
        "volume": [1000.0] * n,
    })


def _make_buy_df(high_confidence: bool = False) -> pd.DataFrame:
    """
    accel > accel_ma AND accel > 0 AND accel > accel_std * 0.5 조건 충족.

    전략:
    - 초반 30봉: 일정 속도 상승 → returns 일정, accel ≈ 0, accel_ma ≈ 0
    - 마지막 완성봉(-2): 갑자기 수익률이 큰 폭으로 증가 → accel 양수 급등
    - accel_std: 초반 변동이 작아야 std가 작아 accel > std*0.5 충족 가능
    """
    n = 50
    closes = []
    val = 100.0
    # 초반 47봉: 일정한 작은 상승 (+0.1씩) → returns 일정, accel = 0
    for i in range(47):
        closes.append(val)
        val += 0.1
    # 봉 48 (idx=-2): 큰 점프
    jump = 10.0 if not high_confidence else 30.0
    closes.append(val + jump)
    # 봉 49 (idx=-1, 진행 중): 임의
    closes.append(val + jump)
    n = len(closes)
    return _make_df(n=n, close_vals=closes)


def _make_sell_df(high_confidence: bool = False) -> pd.DataFrame:
    """
    accel < accel_ma AND accel < 0 AND accel < -accel_std * 0.5 조건 충족.

    전략: 초반 일정 하락 → 마지막 완성봉에 급락.
    """
    n = 50
    closes = []
    val = 200.0
    for i in range(47):
        closes.append(val)
        val -= 0.1
    drop = 10.0 if not high_confidence else 30.0
    closes.append(val - drop)
    closes.append(val - drop)
    n = len(closes)
    return _make_df(n=n, close_vals=closes)


class TestParabolicMomentumStrategy:

    def setup_method(self):
        self.strategy = ParabolicMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "parabolic_momentum"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 데이터 정확히 최소 행 수 → 정상 동작 (크래시 없음)
    def test_min_rows_no_crash(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. 평탄한 가격 → HOLD (accel = 0)
    def test_flat_price_hold(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY 신호 반환
    def test_buy_signal(self):
        df = _make_buy_df(high_confidence=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 6. BUY strategy 필드
    def test_buy_strategy_field(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.strategy == "parabolic_momentum"

    # 7. SELL 신호 반환
    def test_sell_signal(self):
        df = _make_sell_df(high_confidence=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 8. SELL strategy 필드
    def test_sell_strategy_field(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.strategy == "parabolic_momentum"

    # 9. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 10. entry_price == close.iloc[-2]
    def test_entry_price_is_last_complete_candle(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 12. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 13. HOLD reasoning 확인
    def test_hold_reasoning_contains_hold(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert "HOLD" in sig.reasoning or "부족" in sig.reasoning

    # 14. 부족 데이터 entry_price = 0 (빈 df)
    def test_empty_df_entry_price_zero(self):
        df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.entry_price == 0.0
