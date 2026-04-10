"""
VolatilityBreakoutStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import math

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.volatility_breakout import VolatilityBreakoutStrategy

_MIN_ROWS = 20


def _make_base_df(n: int = 30, close_val: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame."""
    return pd.DataFrame({
        "open": [close_val] * n,
        "close": [close_val] * n,
        "high": [close_val + 1.0] * n,
        "low": [close_val - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 45) -> pd.DataFrame:
    """
    BUY 조건: BB 확장(bb_width > bb_width_ma) + close > bb_upper
    - 처음 35개: flat at 100.0 → bb_width_ma 낮게 유지
    - 마지막 10개: 매우 급등 → BB 확장 + 상단 돌파
    idx=43(n-2): close가 bb_upper 초과 보장
    """
    closes = [100.0] * 35
    for i in range(n - 35):
        closes.append(100.0 + (i + 1) * 30.0)

    df = pd.DataFrame({
        "open": [c - 0.5 for c in closes],
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _make_sell_df(n: int = 45) -> pd.DataFrame:
    """
    SELL 조건: BB 확장 + close < bb_lower
    - 처음 35개: flat at 100.0
    - 마지막 10개: 매우 급락 → BB 확장 + 하단 이탈
    """
    closes = [100.0] * 35
    for i in range(n - 35):
        closes.append(100.0 - (i + 1) * 30.0)

    df = pd.DataFrame({
        "open": [c + 0.5 for c in closes],
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


class TestVolatilityBreakoutStrategy:

    def setup_method(self):
        self.strategy = VolatilityBreakoutStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volatility_breakout"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_base_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Signal 객체 반환
    def test_returns_signal(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)

    # 5. strategy 필드
    def test_strategy_field(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "volatility_breakout"

    # 6. action 유효값
    def test_action_valid_values(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence 유효값
    def test_confidence_valid_values(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. entry_price는 float (NaN 아님)
    def test_entry_price_is_float(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)
        assert not math.isnan(sig.entry_price)

    # 9. BUY 신호
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 10. BUY reasoning에 'BUY' 포함
    def test_buy_reasoning_contains_buy(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 11. SELL 신호
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 12. SELL reasoning에 'SELL' 포함
    def test_sell_reasoning_contains_sell(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 13. 최소 행수 경계: 정확히 _MIN_ROWS
    def test_exact_min_rows(self):
        df = _make_base_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. 최소 행수 -1 → HOLD
    def test_below_min_rows(self):
        df = _make_base_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 15. flat → HOLD (변동성 없음)
    def test_flat_data_holds(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        # 완전 flat이면 bb_std=0, bb_width=0, expanding=False
        assert sig.action == Action.HOLD

    # 16. BUY entry_price = 마지막 완성 캔들 close
    def test_buy_entry_price_equals_close(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 17. SELL entry_price = 마지막 완성 캔들 close
    def test_sell_entry_price_equals_close(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            idx = len(df) - 2
            assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))

    # 18. BUY confidence HIGH or MEDIUM
    def test_buy_confidence_high_or_medium(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 19. SELL confidence HIGH or MEDIUM
    def test_sell_confidence_high_or_medium(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 20. HOLD reasoning content
    def test_hold_reasoning_content(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        if sig.action == Action.HOLD:
            assert sig.reasoning != ""
