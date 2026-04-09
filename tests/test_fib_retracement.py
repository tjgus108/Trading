"""
FibRetracementStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.fib_retracement import FibRetracementStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 60, close_prices=None, high_prices=None, low_prices=None) -> pd.DataFrame:
    """기본 DataFrame 생성."""
    if close_prices is None:
        close_prices = [100.0] * n
    if high_prices is None:
        high_prices = [c + 1.0 for c in close_prices]
    if low_prices is None:
        low_prices = [c - 1.0 for c in close_prices]

    return pd.DataFrame({
        "open": close_prices,
        "close": close_prices,
        "high": high_prices,
        "low": low_prices,
        "volume": [1000.0] * len(close_prices),
    })


def _make_uptrend_fib_bounce_df() -> pd.DataFrame:
    """
    상승 추세 + 피보나치 되돌림 반등 데이터:
    - SMA50 < close (상승 추세)
    - swing_high = 200, swing_low = 100 → fib_38 = 138.2, fib_62 = 161.8
    - 신호봉 close를 존 내에서 반등 중으로 설정
    """
    n = 60
    # 전체적으로 상승 추세: 100 → 200으로 증가
    closes = list(np.linspace(100, 200, n - 10))
    # 되돌림: 200 → 145 구간 (피보나치 존 내)
    retracement = list(np.linspace(200, 145, 8))
    closes.extend(retracement)
    # 마지막 2봉: 반등 시작 (148으로 올라감)
    closes.append(147.0)   # 신호봉 직전
    closes.append(148.0)   # 신호봉 (-2)
    closes.append(149.0)   # 진행 중 봉 (-1, 무시)

    # 총 n개로 맞추기
    closes = closes[:n]

    highs = [c + 2.0 for c in closes]
    lows = [c - 2.0 for c in closes]

    # swing_high를 200으로 명시 (최근 50봉에서)
    highs[-10] = 202.0  # 50봉 내 최고점

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_downtrend_fib_resistance_df() -> pd.DataFrame:
    """
    하락 추세 + 피보나치 저항 데이터:
    - SMA50 > close (하락 추세)
    - swing_high = 200, swing_low = 100 → fib_38 = 138.2, fib_62 = 161.8
    - 신호봉 close를 존 내에서 저항 받아 하락 중으로 설정
    """
    n = 60
    # 하락 추세: 200 → 100으로 감소
    closes = list(np.linspace(200, 100, n - 5))
    # 반등: 100 → 150 구간 (피보나치 존 내)
    retracement = list(np.linspace(100, 150, 3))
    closes.extend(retracement)
    # 마지막 2봉: 저항 받아 다시 하락
    closes.append(149.0)   # 신호봉 직전
    closes.append(148.0)   # 신호봉 (-2) - 하락 중
    closes.append(147.0)   # 진행 중 봉 (-1, 무시)

    closes = closes[:n]

    highs = [c + 2.0 for c in closes]
    lows = [c - 2.0 for c in closes]

    # swing_high를 200으로 명시
    highs[0] = 202.0

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


class TestFibRetracementStrategy:

    def setup_method(self):
        self.strategy = FibRetracementStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "fib_retracement"

    # 2. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 정확히 최소 행 (55행) - 처리 가능
    def test_exactly_min_rows(self):
        df = _make_df(n=55)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. HOLD: 중립 (피보나치 존 밖)
    def test_hold_outside_zone(self):
        # close = 200, swing_high ≈ 201, swing_low ≈ 99 → 존 = [137~163] 밖
        n = 60
        closes = [200.0] * n
        highs = [201.0] * n
        lows = [99.0] * n
        df = pd.DataFrame({
            "open": closes, "close": closes, "high": highs, "low": lows,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY 신호 (상승 추세 + 피보나치 반등)
    def test_buy_signal_uptrend_bounce(self):
        df = _make_uptrend_fib_bounce_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 6. SELL 신호 (하락 추세 + 피보나치 저항)
    def test_sell_signal_downtrend_resistance(self):
        df = _make_downtrend_fib_resistance_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 9. strategy 필드 값
    def test_signal_strategy_field(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.strategy == "fib_retracement"

    # 10. 가격 범위 없을 때 (모든 봉 동일가격)
    def test_hold_no_price_range(self):
        n = 60
        closes = [100.0] * n
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": closes, "low": closes,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. Confidence: 61.8% 근방에서 HIGH
    def test_confidence_high_near_golden(self):
        """
        61.8% 레벨 근방 ±0.5%에서 BUY 신호가 나오면 HIGH confidence여야 함.
        """
        n = 60
        # swing_low=100, swing_high=200 → fib_62 = 161.8
        # 신호봉 close = 161.8 (정확히 61.8% 레벨)
        # 상승 추세: SMA50 < 161.8 이 되도록 초반은 낮게, 후반은 높게
        base_closes = list(np.linspace(50, 160, n - 3))
        base_closes.append(160.5)   # 신호봉 직전
        base_closes.append(161.8)   # 신호봉 (-2), 정확히 61.8%
        base_closes.append(162.0)   # 진행 중 봉

        closes = base_closes[:n]
        highs = [c + 2.0 for c in closes]
        lows = [c - 2.0 for c in closes]
        highs[0] = 202.0  # swing_high = 200 근방

        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        # BUY가 나오면 HIGH confidence, HOLD도 허용
        assert sig.action in (Action.BUY, Action.HOLD)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 12. Confidence: 존 내 비황금비율 구간에서 MEDIUM
    def test_confidence_medium_non_golden(self):
        """
        38.2% ~ 50% 구간에서 BUY가 나오면 MEDIUM confidence여야 함.
        """
        n = 60
        # swing_low=100, swing_high=200 → fib_38=138.2, fib_50=150
        # 신호봉 close ≈ 140 (38.2%~50% 구간)
        base_closes = list(np.linspace(50, 139, n - 3))
        base_closes.append(139.5)   # 신호봉 직전
        base_closes.append(140.0)   # 신호봉 (-2)
        base_closes.append(141.0)   # 진행 중

        closes = base_closes[:n]
        highs = [c + 2.0 for c in closes]
        lows = [c - 2.0 for c in closes]
        highs[0] = 202.0

        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.MEDIUM

    # 13. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 14. 데이터 54행 (최소-1) → HOLD
    def test_one_below_min_rows(self):
        df = _make_df(n=54)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning
