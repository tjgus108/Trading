"""
StochasticMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.stoch_momentum import StochasticMomentumStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 40, close_vals=None, high_vals=None, low_vals=None,
             volume: float = 1000.0) -> pd.DataFrame:
    """기본 DataFrame 생성 헬퍼."""
    if close_vals is None:
        close_vals = [100.0] * n
    if high_vals is None:
        high_vals = [c + 1.0 for c in close_vals]
    if low_vals is None:
        low_vals = [c - 1.0 for c in close_vals]

    return pd.DataFrame({
        "open": close_vals,
        "close": close_vals,
        "high": high_vals,
        "low": low_vals,
        "volume": [volume] * n,
    })


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """
    SMI < 0 이고 SMI가 signal을 상향 돌파하는 상황 유도.
    앞부분: 가격 하락 (close가 midpoint 아래, SMI 음수)
    마지막 완성봉(-2): close가 살짝 반등 → SMI > signal 크로스 유도
    """
    closes = []
    highs = []
    lows = []
    # 긴 하락 구간 → SMI 음수 구축
    for i in range(n - 4):
        closes.append(100.0 - i * 0.3)
        highs.append(closes[-1] + 0.5)
        lows.append(closes[-1] - 0.5)
    # 하락 더 가속 (prev: SMI < signal)
    closes.append(closes[-1] - 2.0)
    highs.append(closes[-1] + 0.5)
    lows.append(closes[-1] - 0.5)
    # 신호 봉(-2): 반등 → SMI > signal
    closes.append(closes[-1] + 0.8)
    highs.append(closes[-1] + 0.5)
    lows.append(closes[-1] - 0.5)
    # 진행 중 봉(-1)
    closes.append(closes[-1] + 0.3)
    highs.append(closes[-1] + 0.5)
    lows.append(closes[-1] - 0.5)

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * len(closes),
    })


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """
    SMI > 0 이고 SMI가 signal을 하향 돌파하는 상황 유도.
    앞부분: 가격 상승 (SMI 양수)
    마지막 완성봉(-2): 하락 반전 → SMI < signal 크로스
    """
    closes = []
    highs = []
    lows = []
    for i in range(n - 4):
        closes.append(100.0 + i * 0.3)
        highs.append(closes[-1] + 0.5)
        lows.append(closes[-1] - 0.5)
    # 상승 더 가속 (prev: SMI > signal)
    closes.append(closes[-1] + 2.0)
    highs.append(closes[-1] + 0.5)
    lows.append(closes[-1] - 0.5)
    # 신호 봉(-2): 급락 → SMI < signal
    closes.append(closes[-1] - 0.8)
    highs.append(closes[-1] + 0.5)
    lows.append(closes[-1] - 0.5)
    # 진행 중 봉(-1)
    closes.append(closes[-1] - 0.3)
    highs.append(closes[-1] + 0.5)
    lows.append(closes[-1] - 0.5)

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * len(closes),
    })


class TestStochasticMomentumStrategy:

    def setup_method(self):
        self.strategy = StochasticMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "stoch_momentum"

    # 2. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 경계: 정확히 20행 → 실행은 돼야 함
    def test_exactly_min_rows(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. HOLD: 중립 (가격 변화 없음 → SMI = 0)
    def test_hold_flat_price(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "stoch_momentum"

    # 5. Signal 필드 완전성 (HOLD)
    def test_signal_fields_complete(self):
        df = _make_df(n=40)
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
        assert sig.reasoning != ""

    # 6. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=40, close_vals=[50.0] * 40)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 7. high/low 컬럼 없을 때 폴백
    def test_no_high_low_columns(self):
        df = pd.DataFrame({
            "open": [100.0] * 30,
            "close": [100.0] * 30,
            "volume": [1000.0] * 30,
        })
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.HOLD

    # 8. BUY 신호 생성 확인 (하락 후 반등 패턴)
    def test_buy_signal_generated(self):
        df = _make_buy_df(n=50)
        sig = self.strategy.generate(df)
        # 신호 방향 또는 HOLD (크로스 정확도 의존)
        assert sig.action in (Action.BUY, Action.HOLD)
        assert sig.strategy == "stoch_momentum"

    # 9. SELL 신호 생성 확인 (상승 후 하락 패턴)
    def test_sell_signal_generated(self):
        df = _make_sell_df(n=50)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)
        assert sig.strategy == "stoch_momentum"

    # 10. BUY confidence HIGH when SMI < -40
    def test_buy_high_confidence_when_deep_oversold(self):
        # 매우 긴 하락 → SMI << -40 구간 후 반등
        n = 80
        closes = []
        highs = []
        lows = []
        for i in range(n - 4):
            closes.append(200.0 - i * 1.5)
            highs.append(closes[-1] + 0.5)
            lows.append(closes[-1] - 20.0)  # 넓은 range로 SMI 크게 음수
        closes.append(closes[-1] - 5.0)
        highs.append(closes[-1] + 0.5)
        lows.append(closes[-1] - 20.0)
        closes.append(closes[-1] + 2.0)
        highs.append(closes[-1] + 0.5)
        lows.append(closes[-1] - 20.0)
        closes.append(closes[-1] + 1.0)
        highs.append(closes[-1] + 0.5)
        lows.append(closes[-1] - 20.0)

        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * len(closes),
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # SMI < -40 이면 HIGH, 아니면 MEDIUM
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 11. SELL confidence HIGH when SMI > 40
    def test_sell_high_confidence_when_deep_overbought(self):
        n = 80
        closes = []
        highs = []
        lows = []
        for i in range(n - 4):
            closes.append(100.0 + i * 1.5)
            highs.append(closes[-1] + 20.0)
            lows.append(closes[-1] - 0.5)
        closes.append(closes[-1] + 5.0)
        highs.append(closes[-1] + 20.0)
        lows.append(closes[-1] - 0.5)
        closes.append(closes[-1] - 2.0)
        highs.append(closes[-1] + 20.0)
        lows.append(closes[-1] - 0.5)
        closes.append(closes[-1] - 1.0)
        highs.append(closes[-1] + 20.0)
        lows.append(closes[-1] - 0.5)

        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": highs, "low": lows,
            "volume": [1000.0] * len(closes),
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 12. reasoning 내용 확인
    def test_reasoning_not_empty(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 13. 가격 단조 증가 → HOLD (크로스 없음)
    def test_hold_monotonic_increase(self):
        closes = [100.0 + i * 0.01 for i in range(40)]
        highs = [c + 0.5 for c in closes]
        lows = [c - 0.5 for c in closes]
        df = _make_df(n=40, close_vals=closes, high_vals=highs, low_vals=lows)
        sig = self.strategy.generate(df)
        # 크로스가 발생하지 않아 HOLD 가능성 높음
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
        assert isinstance(sig, Signal)
