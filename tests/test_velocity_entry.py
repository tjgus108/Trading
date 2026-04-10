"""
VelocityEntryStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.velocity_entry import VelocityEntryStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(n: int = _MIN_ROWS + 5, close_vals: list = None) -> pd.DataFrame:
    """
    마지막 봉(-2)가 신호 봉 (BaseStrategy._last() 기준).
    close_vals: 직접 지정 시 사용, 없으면 기본값으로 채움.
    """
    if close_vals is not None:
        closes = list(close_vals)
        rows = len(closes)
    else:
        rows = n
        closes = [100.0] * rows

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * rows,
    })
    return df


def _make_buy_df() -> pd.DataFrame:
    """
    BUY 조건: velocity[-2] > velocity_ma[-2] AND acceleration[-2] > 0
    앞부분: 완만한 상승 (velocity_ma baseline 형성)
    뒷부분: 가속도가 증가하는 상승 (velocity 계속 커짐)
    """
    # 앞 15봉: 일정한 0.5씩 상승 (velocity≈0.5 상수 → acceleration≈0)
    closes = [100.0 + i * 0.5 for i in range(15)]
    # 뒤 10봉: 가속도가 양수가 되도록 velocity 증가 (i^2 형태)
    base = closes[-1]
    for i in range(1, 11):
        closes.append(base + i * i * 0.3)
    return _make_df(close_vals=closes)


def _make_sell_df() -> pd.DataFrame:
    """
    SELL 조건: velocity[-2] < velocity_ma[-2] AND acceleration[-2] < 0
    앞부분: 완만한 하락 (velocity_ma baseline)
    뒷부분: 가속도가 음수로 증가 (점점 빠르게 하락)
    """
    closes = [100.0 - i * 0.5 for i in range(15)]
    base = closes[-1]
    for i in range(1, 11):
        closes.append(base - i * i * 0.3)
    return _make_df(close_vals=closes)


class TestVelocityEntryStrategy:

    def setup_method(self):
        self.strategy = VelocityEntryStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "velocity_entry"

    # 2. 인스턴스 타입 확인
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 시 HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. None 반환 없음 (항상 Signal 반환)
    def test_returns_signal_not_none(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig is not None

    # 5. reasoning 필드 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 6. 정상 signal 반환 (충분한 데이터)
    def test_normal_signal_with_sufficient_data(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY 신호 확인
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 9. BUY reasoning에 키워드 포함
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "velocity" in sig.reasoning.lower() or "속도" in sig.reasoning

    # 10. SELL 신호 확인
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 11. SELL reasoning에 키워드 포함
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "velocity" in sig.reasoning.lower() or "속도" in sig.reasoning

    # 12. confidence HIGH or MEDIUM (충분한 데이터)
    def test_confidence_is_high_or_medium(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action in (Action.BUY, Action.SELL):
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 14. strategy 필드 확인
    def test_strategy_field(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "velocity_entry"

    # 15. 최소 행 경계: 정확히 20행 이상 시 NaN 없으면 처리
    def test_min_rows_boundary(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 16. HOLD 신호 - 횡보장 (일정한 가격)
    def test_hold_signal_flat(self):
        closes = [100.0] * 25
        df = _make_df(close_vals=closes)
        sig = self.strategy.generate(df)
        # 속도=0, 가속=0 → HOLD 또는 NaN → HOLD
        assert sig.action == Action.HOLD
