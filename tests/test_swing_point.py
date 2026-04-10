"""
SwingPointStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest

from src.strategy.swing_point import SwingPointStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 10


def _make_df(n: int = _MIN_ROWS + 5,
             close_vals: "list[float] | None" = None,
             high_vals: "list[float] | None" = None,
             low_vals: "list[float] | None" = None,
             atr14: float = 2.0) -> pd.DataFrame:
    """
    _last(df) = df.iloc[-2] 기준.
    swing_high = high.rolling(3).max().shift(1)  → idx-1 기준 최근 3봉 최고가
    swing_low  = low.rolling(3).min().shift(1)   → idx-1 기준 최근 3봉 최저가
    """
    if close_vals is None:
        close_vals = [100.0] * n
    while len(close_vals) < n:
        close_vals = [close_vals[0]] + close_vals
    close_vals = close_vals[-n:]

    closes = pd.Series(close_vals, dtype=float)

    if high_vals is None:
        high_vals_s = closes + 1.0
    else:
        while len(high_vals) < n:
            high_vals = [high_vals[0]] + high_vals
        high_vals_s = pd.Series(high_vals[-n:], dtype=float)

    if low_vals is None:
        low_vals_s = closes - 1.0
    else:
        while len(low_vals) < n:
            low_vals = [low_vals[0]] + low_vals
        low_vals_s = pd.Series(low_vals[-n:], dtype=float)

    return pd.DataFrame({
        "open": closes.values,
        "high": high_vals_s.values,
        "low": low_vals_s.values,
        "close": closes.values,
        "volume": [1000.0] * n,
        "atr14": [atr14] * n,
    })


def _make_buy_df(large_breakout: bool = False) -> pd.DataFrame:
    """
    close[-2] > swing_high 조건 충족.
    swing_high = high.rolling(3).max().shift(1): idx=-2 기준으로 인덱스 -3~-1의 최고가.
    close[-2]를 swing_high보다 크게 설정.
    """
    n = _MIN_ROWS + 5
    # high: 대부분 101, low: 대부분 99 → swing_high ≈ 101
    # close[-2]: 110 → 돌파
    close_vals = [100.0] * (n - 1) + [110.0]
    high_vals = [101.0] * n
    low_vals = [99.0] * n
    # close[-2] = 110, high[-2] = 101 → close > swing_high(≈101) ✓
    # atr14: large_breakout이면 작게 설정해서 돌파가 크게 보이도록
    atr14 = 2.0 if large_breakout else 20.0
    df = _make_df(n=n, close_vals=close_vals, high_vals=high_vals, low_vals=low_vals, atr14=atr14)
    # close[-2]를 명시적으로 110으로
    df.loc[df.index[-2], "close"] = 110.0
    return df


def _make_sell_df(large_breakout: bool = False) -> pd.DataFrame:
    """
    close[-2] < swing_low 조건 충족.
    """
    n = _MIN_ROWS + 5
    close_vals = [100.0] * (n - 1) + [90.0]
    high_vals = [101.0] * n
    low_vals = [99.0] * n
    atr14 = 2.0 if large_breakout else 20.0
    df = _make_df(n=n, close_vals=close_vals, high_vals=high_vals, low_vals=low_vals, atr14=atr14)
    df.loc[df.index[-2], "close"] = 88.0
    return df


class TestSwingPointStrategy:

    def setup_method(self):
        self.strategy = SwingPointStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "swing_point"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 최소 행 수 → 정상 동작
    def test_min_rows_no_crash(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. close가 범위 내 → HOLD
    def test_within_range_hold(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY 신호
    def test_buy_signal(self):
        df = _make_buy_df(large_breakout=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "swing_point"

    # 6. BUY HIGH confidence (돌파 크기 > ATR14 * 0.5)
    def test_buy_high_confidence(self):
        # atr14=2, close=110, swing_high≈101 → 돌파크기≈9 > 2*0.5=1 → HIGH
        df = _make_buy_df(large_breakout=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. BUY MEDIUM confidence (돌파 크기 < ATR14 * 0.5)
    def test_buy_medium_confidence(self):
        # atr14=20, close=110, swing_high≈101 → 돌파크기≈9 < 20*0.5=10 → MEDIUM
        df = _make_buy_df(large_breakout=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 8. SELL 신호
    def test_sell_signal(self):
        df = _make_sell_df(large_breakout=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "swing_point"

    # 9. SELL HIGH confidence
    def test_sell_high_confidence(self):
        df = _make_sell_df(large_breakout=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 10. SELL MEDIUM confidence (이탈 크기 < ATR14 * 0.5)
    def test_sell_medium_confidence(self):
        # swing_low ≈ 99, close[-2]=98.5, 이탈크기=0.5, atr14=20 → 0.5 < 10 → MEDIUM
        n = _MIN_ROWS + 5
        close_vals = [100.0] * (n - 1) + [98.5]
        high_vals = [101.0] * n
        low_vals = [99.0] * n
        df = _make_df(n=n, close_vals=close_vals, high_vals=high_vals, low_vals=low_vals, atr14=20.0)
        df.loc[df.index[-2], "close"] = 98.5
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

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
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 13. atr14 컬럼 없어도 계산 동작
    def test_works_without_atr14_column(self):
        n = _MIN_ROWS + 5
        df = _make_df(n=n)
        df = df.drop(columns=["atr14"])
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. HOLD reasoning 포함 확인
    def test_hold_reasoning_contains_hold_or_info(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert "HOLD" in sig.reasoning or "부족" in sig.reasoning
