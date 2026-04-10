"""
MomentumAccelerationStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum_accel import MomentumAccelerationStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(n: int = _MIN_ROWS + 5,
             close_vals: "list[float] | None" = None,
             ema20: "float | None" = None,
             atr14: float = 2.0) -> pd.DataFrame:
    """
    close_vals를 직접 지정하거나, 지정하지 않으면 평탄한 시리즈를 사용.
    _last(df) = df.iloc[-2] 기준.
    """
    if close_vals is None:
        close_vals = [100.0] * n
    else:
        # n 맞추기
        while len(close_vals) < n:
            close_vals = [close_vals[0]] + close_vals
        close_vals = close_vals[-n:]

    closes = pd.Series(close_vals, dtype=float)
    highs = closes + 1.0
    lows = closes - 1.0

    data: dict = {
        "open": closes.values,
        "high": highs.values,
        "low": lows.values,
        "close": closes.values,
        "volume": [1000.0] * n,
        "atr14": [atr14] * n,
    }
    if ema20 is not None:
        data["ema20"] = [ema20] * n

    return pd.DataFrame(data)


def _make_buy_df(accel_ema_strong: bool = False) -> pd.DataFrame:
    """
    accel_ema > 0.5, mom5 > 0, close > ema20 조건을 충족하는 DataFrame.
    _last(df) = df.iloc[-2] 기준.

    패턴: 5봉 flat + 5봉 급등을 반복.
    최종 완성봉(idx=-2)이 급등 구간 끝에 위치하도록 구성.

    수학: flat[0..4]=base, rise[5..9]=base+step
      mom5(i=9) = step/base * 100
      mom10(i=9) = step/base * 100  (i-10=i-10은 동일한 base)
      accel = mom5 - mom10/2 = step/base*100/2 > 0 ✓
    """
    # 패턴을 반복해 ewm이 수렴하도록 충분한 행 확보
    # 마지막 완성봉이 급등구간 마지막(index 9 of cycle) 이 되도록 설계
    if accel_ema_strong:
        step = 10.0   # accel ≈ 5 > 1.5 → HIGH
    else:
        step = 3.0    # accel ≈ 1.5 → MEDIUM
    base = 100.0
    closes = []
    # 5 사이클 반복
    for _ in range(5):
        for _ in range(5):
            closes.append(base)
        for _ in range(5):
            closes.append(base + step)
        base += step
    # idx = len-2 → closes[-2] = base+step (급등 구간 마지막 근처)
    # 마지막 봉(closes[-1]) 추가: 진행 중인 봉이므로 의미 없음
    closes.append(closes[-1])
    n = len(closes)
    return _make_df(n=n, close_vals=closes, ema20=80.0)


def _make_sell_df(accel_ema_strong: bool = False) -> pd.DataFrame:
    """
    accel_ema < -0.5, mom5 < 0, close < ema20 조건을 충족하는 DataFrame.
    패턴: 5봉 flat + 5봉 급락 반복.
    accel = -step/(2*base)*100 → step 크게 해야 < -0.5 충족.
    """
    if accel_ema_strong:
        step = 20.0   # accel ≈ -20/(2*200)*100 = -5 < -1.5 → HIGH
    else:
        step = 6.0    # accel ≈ -6/(2*270)*100 = -1.1 < -0.5 → MEDIUM
    base = 300.0
    closes = []
    for _ in range(5):
        for _ in range(5):
            closes.append(base)
        for _ in range(5):
            closes.append(base - step)
        base -= step
    closes.append(closes[-1])
    n = len(closes)
    return _make_df(n=n, close_vals=closes, ema20=400.0)


class TestMomentumAccelerationStrategy:

    def setup_method(self):
        self.strategy = MomentumAccelerationStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "momentum_accel"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 데이터 정확히 최소 행 수 → 정상 동작
    def test_min_rows_no_crash(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. 평탄한 가격 → HOLD (mom5=0)
    def test_flat_price_hold(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY 신호 기본
    def test_buy_signal(self):
        df = _make_buy_df(accel_ema_strong=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "momentum_accel"

    # 6. BUY HIGH confidence (accel_ema > 1.5)
    def test_buy_high_confidence(self):
        df = _make_buy_df(accel_ema_strong=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. SELL 신호 기본
    def test_sell_signal(self):
        df = _make_sell_df(accel_ema_strong=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "momentum_accel"

    # 8. SELL HIGH confidence (accel_ema < -1.5)
    def test_sell_high_confidence(self):
        df = _make_sell_df(accel_ema_strong=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 9. mom5 > 0 but close < ema20 → HOLD
    def test_hold_buy_below_ema20(self):
        n = _MIN_ROWS + 10
        closes = [90.0] * 10 + [95.0] * (n - 10)
        df = _make_df(n=n, close_vals=closes, ema20=200.0)  # ema20 매우 높음
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. mom5 < 0 but close > ema20 → HOLD
    def test_hold_sell_above_ema20(self):
        n = _MIN_ROWS + 10
        closes = [110.0] * 10 + [105.0] * (n - 10)
        df = _make_df(n=n, close_vals=closes, ema20=50.0)  # ema20 매우 낮음
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 12. entry_price == close.iloc[-2]
    def test_entry_price_is_last_complete_candle(self):
        n = _MIN_ROWS + 10
        closes = [90.0] * 10 + [95.0] * (n - 10)
        df = _make_df(n=n, close_vals=closes, ema20=80.0)
        sig = self.strategy.generate(df)
        expected_entry = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_entry)

    # 13. ema20 컬럼 없어도 계산 동작
    def test_works_without_ema20_column(self):
        n = _MIN_ROWS + 10
        closes = [90.0] * 10 + [95.0] * (n - 10)
        df = _make_df(n=n, close_vals=closes, ema20=None)  # ema20 컬럼 없음
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. HOLD reasoning 포함 확인
    def test_hold_reasoning_contains_hold(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert "HOLD" in sig.reasoning or "부족" in sig.reasoning
