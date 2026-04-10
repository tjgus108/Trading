"""
CarryStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.carry_strategy import CarryStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df_flat(n: int = _MIN_ROWS + 5, close: float = 100.0) -> pd.DataFrame:
    """횡보 시세 — z_carry ≈ 0 → HOLD"""
    closes = [close] * n
    return pd.DataFrame({
        "open": closes, "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_df_spike_up(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    안정적 횡보 후 마지막 봉(-2)에서 급등 → z_carry > 1.5 → BUY
    """
    base = 100.0
    closes = [base] * n
    # 마지막 완성 봉(-2)를 크게 올림
    closes[-2] = base * 1.10  # +10%
    return pd.DataFrame({
        "open": closes, "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_df_spike_down(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    안정적 횡보 후 마지막 봉(-2)에서 급락 → z_carry < -1.5 → SELL
    """
    base = 100.0
    closes = [base] * n
    closes[-2] = base * 0.90  # -10%
    return pd.DataFrame({
        "open": closes, "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


class TestCarryStrategy:

    def setup_method(self):
        self.strategy = CarryStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "carry_strategy"

    # 2. BaseStrategy 상속
    def test_is_base_strategy(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strategy, BaseStrategy)

    # 3. 데이터 부족 시 HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_df_flat(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 4. 최소 행수 경계 (24행 → HOLD)
    def test_min_rows_boundary(self):
        df = _make_df_flat(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. 횡보 → HOLD
    def test_hold_flat_market(self):
        df = _make_df_flat(n=_MIN_ROWS + 10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. 급등 → BUY
    def test_buy_on_spike_up(self):
        df = _make_df_spike_up(n=_MIN_ROWS + 10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 7. 급락 → SELL
    def test_sell_on_spike_down(self):
        df = _make_df_spike_down(n=_MIN_ROWS + 10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 8. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df_spike_up(n=_MIN_ROWS + 10)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "carry_strategy"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""

    # 9. entry_price = 마지막 완성 캔들 close
    def test_entry_price_is_last_complete_candle(self):
        df = _make_df_spike_up(n=_MIN_ROWS + 10)
        sig = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected)

    # 10. BUY confidence HIGH (|z_carry| > 2.0)
    def test_buy_high_confidence(self):
        # 매우 큰 스파이크 → |z_carry| >> 2.0
        n = _MIN_ROWS + 20
        base = 100.0
        closes = [base] * n
        closes[-2] = base * 1.50  # +50%
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 11. SELL confidence HIGH (|z_carry| > 2.0)
    def test_sell_high_confidence(self):
        n = _MIN_ROWS + 20
        base = 100.0
        closes = [base] * n
        closes[-2] = base * 0.50  # -50%
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 12. 정확히 _MIN_ROWS 행 → 정상 처리
    def test_exactly_min_rows(self):
        df = _make_df_flat(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 13. 큰 데이터셋 정상 동작
    def test_large_dataset(self):
        df = _make_df_spike_up(n=200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. z_carry 임계값 경계 (자연 변동성 있는 데이터에서 작은 스파이크 → HOLD)
    def test_small_spike_returns_hold(self):
        # 자연 변동이 있는 데이터에서 평균 수준의 변동 → |z_carry| < 1.5 → HOLD
        n = _MIN_ROWS + 20
        rng = np.random.default_rng(42)
        # 표준편차 1% 수준의 정규 변동
        returns = rng.normal(0, 0.01, n)
        returns[-2] = 0.005  # 0.5% 수익률: 평균 대비 작은 양의 변동
        closes = [100.0]
        for r in returns[1:]:
            closes.append(closes[-1] * (1 + r))
        # 마지막 완성 봉(-2)의 수익률을 정확히 0.5%로 제어
        closes[-2] = closes[-3] * 1.005
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        # 작은 변동 → HOLD (z_carry < 1.5)
        assert sig.action == Action.HOLD
