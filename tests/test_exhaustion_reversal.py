"""
ExhaustionReversalStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.exhaustion_reversal import ExhaustionReversalStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(n: int = _MIN_ROWS + 5,
             close_vals: "list[float] | None" = None,
             volume_vals: "list[float] | None" = None,
             body_ratio_small: bool = False) -> pd.DataFrame:
    """기본 DataFrame 생성."""
    if close_vals is None:
        close_vals = [100.0] * n
    else:
        while len(close_vals) < n:
            close_vals = [close_vals[0]] + close_vals
        close_vals = close_vals[-n:]

    if volume_vals is None:
        volume_vals = [1000.0] * n

    closes = pd.Series(close_vals, dtype=float)
    highs = closes + 2.0
    lows = closes - 2.0

    if body_ratio_small:
        # 꼬리 길게, 몸통 작게 (body_ratio < 0.3)
        opens = closes + 0.1   # body = 0.1, hl_range = 4.0 → ratio = 0.025
    else:
        opens = closes         # body = 0, ratio = 0 (< 0.3 이지만 이건 중립)

    return pd.DataFrame({
        "open": opens.values,
        "high": highs.values,
        "low": lows.values,
        "close": closes.values,
        "volume": volume_vals,
    })


def _make_buy_df(high_confidence: bool = False) -> pd.DataFrame:
    """
    BUY 조건 충족:
    - close < close.rolling(20).min().shift(1) → 새 저점
    - body_ratio < 0.3 → 꼬리 긴 캔들
    - volume_spike: volume > vol_ma20 * 2.0
    """
    n = _MIN_ROWS + 10
    # 초반 n-1 봉: 100 근처 평탄 (20-window min ≈ 100)
    close_vals = [100.0] * n
    # 마지막 완성봉(idx=-2): 새 저점 (< 100)
    close_vals[-2] = 85.0
    # 현재 진행 봉(-1): 임의
    close_vals[-1] = 85.0

    # vol_ma20 at idx=-2 포함하여 계산됨: (19*1000 + spike)/20
    # 조건: spike > vol_ma * 2.0
    # 풀면: spike > (19000 + spike)/10 → 9*spike > 19000 → spike > 2111
    # HIGH: spike > vol_ma * 3.0 → spike > (19000+spike)/20*3 → 17*spike > 57000 → spike > 3353
    spike_vol = 4000.0 if high_confidence else 2500.0
    volume_vals = [1000.0] * n
    volume_vals[-2] = spike_vol

    df = _make_df(n=n, close_vals=close_vals, volume_vals=volume_vals, body_ratio_small=True)
    return df


def _make_sell_df(high_confidence: bool = False) -> pd.DataFrame:
    """
    SELL 조건 충족:
    - close > close.rolling(20).max().shift(1) → 새 고점
    - body_ratio < 0.3
    - volume_spike
    """
    n = _MIN_ROWS + 10
    close_vals = [100.0] * n
    # 마지막 완성봉(idx=-2): 새 고점 (> 100)
    close_vals[-2] = 115.0
    close_vals[-1] = 115.0

    spike_vol = 4000.0 if high_confidence else 2500.0
    volume_vals = [1000.0] * n
    volume_vals[-2] = spike_vol

    df = _make_df(n=n, close_vals=close_vals, volume_vals=volume_vals, body_ratio_small=True)
    return df


class TestExhaustionReversalStrategy:

    def setup_method(self):
        self.strategy = ExhaustionReversalStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "exhaustion_reversal"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 최소 행 수 크래시 없음
    def test_min_rows_no_crash(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. 평탄한 가격 + 정상 볼륨 → HOLD (volume_spike 없음)
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
        assert sig.strategy == "exhaustion_reversal"

    # 7. BUY HIGH confidence (volume > vol_ma * 3.0)
    def test_buy_high_confidence(self):
        df = _make_buy_df(high_confidence=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 8. SELL 신호 반환
    def test_sell_signal(self):
        df = _make_sell_df(high_confidence=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 9. SELL strategy 필드
    def test_sell_strategy_field(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "exhaustion_reversal"

    # 10. SELL HIGH confidence
    def test_sell_high_confidence(self):
        df = _make_sell_df(high_confidence=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 11. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 12. entry_price == close.iloc[-2]
    def test_entry_price_is_last_complete_candle(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 13. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 14. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=_MIN_ROWS + 5)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 15. volume_spike 없으면 HOLD (새 저점이어도)
    def test_no_volume_spike_hold(self):
        n = _MIN_ROWS + 10
        close_vals = [100.0] * n
        close_vals[-2] = 85.0
        close_vals[-1] = 85.0
        # 볼륨 낮게 (spike 없음)
        volume_vals = [1000.0] * n
        df = _make_df(n=n, close_vals=close_vals, volume_vals=volume_vals, body_ratio_small=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
