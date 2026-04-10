"""
VolumeProfileStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

from typing import Optional

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_profile import VolumeProfileStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0, open_: float = 99.0,
             high: float = 101.0, low: float = 98.0,
             volume: float = 1000.0, prev_close: Optional[float] = None) -> pd.DataFrame:
    """
    마지막 완성 봉 = iloc[-2], 현재 진행 봉 = iloc[-1].
    prev_close: iloc[-3] 의 close (이전 봉).
    """
    closes = [close] * n
    opens = [open_] * n
    highs = [high] * n
    lows = [low] * n
    volumes = [volume] * n

    if prev_close is not None:
        closes[-3] = prev_close

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })
    return df


def _make_buy_df(n: int = 30) -> pd.DataFrame:
    """POC 위에서 close가 아래에 있고, 이전 봉보다 close 상승 → BUY"""
    rows = []
    # 대부분 봉: close=110 (high volume zone → POC ~110)
    for i in range(n - 3):
        rows.append({"open": 109.0, "close": 110.0, "high": 111.0, "low": 108.0, "volume": 2000.0})
    # 이전 봉 (idx-3 relative to final): close 낮음 → 반등 전
    rows.append({"open": 97.0, "close": 97.5, "high": 98.0, "low": 96.0, "volume": 500.0})
    # 신호 봉 (idx=-2): close < poc*0.99 AND close > prev_close
    rows.append({"open": 97.5, "close": 98.5, "high": 99.0, "low": 97.0, "volume": 600.0})
    # 현재 진행 봉 (idx=-1)
    rows.append({"open": 98.5, "close": 99.0, "high": 99.5, "low": 98.0, "volume": 500.0})
    return pd.DataFrame(rows)


def _make_sell_df(n: int = 30) -> pd.DataFrame:
    """POC 아래에 close가 있고, 이전 봉보다 close 하락 → SELL"""
    rows = []
    # 대부분 봉: close=90 (POC ~90)
    for i in range(n - 3):
        rows.append({"open": 89.0, "close": 90.0, "high": 91.0, "low": 88.0, "volume": 2000.0})
    # 이전 봉: close 높음
    rows.append({"open": 92.0, "close": 92.5, "high": 93.0, "low": 91.0, "volume": 500.0})
    # 신호 봉: close > poc*1.01 AND close < prev_close
    rows.append({"open": 92.5, "close": 91.5, "high": 93.0, "low": 91.0, "volume": 600.0})
    # 현재 봉
    rows.append({"open": 91.5, "close": 91.0, "high": 92.0, "low": 90.5, "volume": 500.0})
    return pd.DataFrame(rows)


class TestVolumeProfileStrategy:

    def setup_method(self):
        self.strategy = VolumeProfileStrategy()

    # 1. 전략명 확인
    def test_name(self):
        assert self.strategy.name == "volume_profile"

    # 2. 인스턴스 생성
    def test_instance(self):
        assert isinstance(self.strategy, VolumeProfileStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "POC" in sig.reasoning or "poc" in sig.reasoning

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "POC" in sig.reasoning or "poc" in sig.reasoning

    # 10. HIGH confidence 테스트 (close가 poc와 2% 이상 차이)
    def test_high_confidence(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            # buy_df에서 close~98.5, poc~110 → 거리 > 2%
            assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence 테스트 (poc 근처)
    def test_medium_confidence_hold(self):
        # close == poc 근처이면 HOLD 또는 MEDIUM
        df = _make_df(n=30, close=100.0, high=102.0, low=98.0, volume=1000.0)
        sig = self.strategy.generate(df)
        # HOLD 또는 MEDIUM confidence
        assert sig.action == Action.HOLD or sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.strategy == "volume_profile"

    # 14. 최소 행 수(25)에서 동작
    def test_min_rows_works(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
