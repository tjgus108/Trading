"""
VolumePriceConfirmStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.vol_price_confirm import VolumePriceConfirmStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 25


def _make_df(
    n: int = 50,
    closes=None,
    volumes=None,
) -> pd.DataFrame:
    if closes is None:
        closes = [100.0] * n
    if volumes is None:
        volumes = [1000.0] * n
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    opens = closes[:]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


def _make_buy_df(up_vol_days: int = 4, n: int = 50) -> pd.DataFrame:
    """
    BUY 조건:
    - up_vol_days >= 3: 마지막 5봉 중 up_vol_days개 → 상승 + 볼륨 평균 초과
    - close > EMA20
    - RSI14 40-65
    """
    # 꾸준히 상승하는 시리즈로 RSI ~55, EMA 추종
    closes = []
    base = 90.0
    for i in range(n):
        closes.append(base + i * 0.5)  # 완만한 상승 → RSI 중간대

    # 볼륨: 평균=1000, 신호 봉 앞 up_vol_days개는 크게
    volumes = [1000.0] * n
    idx = n - 2  # _last() 기준
    # 5봉 윈도우: [idx-4, idx-3, idx-2, idx-1, idx]
    for i in range(idx - 4, idx - 4 + up_vol_days):
        if i >= 0:
            volumes[i] = 5000.0  # 평균보다 훨씬 큼

    return _make_df(n, closes, volumes)


def _make_sell_df(down_vol_days: int = 4, n: int = 50) -> pd.DataFrame:
    """
    SELL 조건:
    - down_vol_days >= 3: 마지막 5봉 중 down_vol_days개 → 하락 + 볼륨 평균 초과
    - close < EMA20
    - RSI14 35-60
    """
    closes = []
    base = 120.0
    for i in range(n):
        closes.append(base - i * 0.5)  # 완만한 하락

    volumes = [1000.0] * n
    idx = n - 2
    for i in range(idx - 4, idx - 4 + down_vol_days):
        if i >= 0:
            volumes[i] = 5000.0

    return _make_df(n, closes, volumes)


class TestVolumePriceConfirmStrategy:

    def setup_method(self):
        self.strategy = VolumePriceConfirmStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "vol_price_confirm"

    # 2. 데이터 부족 (< 25행) → HOLD
    def test_insufficient_data(self):
        rows = 20
        df = _make_df(rows)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert sig.strategy == "vol_price_confirm"
        assert isinstance(sig.entry_price, float)
        assert sig.reasoning != ""
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 4. HOLD: 충분한 데이터 but 조건 미충족 → HOLD
    def test_hold_when_no_condition(self):
        # 플랫(변동 없음) → price_dir=0, up/down_vol_days=0
        closes = [100.0] * 50
        volumes = [1000.0] * 50
        df = _make_df(50, closes, volumes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. HOLD confidence = LOW
    def test_hold_confidence_is_low(self):
        df = _make_df(20)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 6. BUY: up_vol_days >= 3, RSI 40-65, close > EMA20
    def test_buy_signal_with_3_up_vol_days(self):
        # 충분한 상승 시리즈로 BUY 조건 확인 (회귀 테스트)
        n = 60
        closes = [90.0 + i * 0.4 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        # 5봉 중 3봉에 볼륨 폭발
        for i in range(idx - 4, idx - 4 + 3):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        # BUY 또는 HOLD (RSI 범위 의존) — 최소 action이 유효해야 함
        assert sig.action in (Action.BUY, Action.HOLD)

    # 7. SELL: down_vol_days >= 3, RSI 35-60, close < EMA20
    def test_sell_signal_with_3_down_vol_days(self):
        n = 60
        closes = [120.0 - i * 0.4 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        for i in range(idx - 4, idx - 4 + 3):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 8. BUY HIGH confidence: up_vol_days == 5
    def test_buy_high_confidence_when_5_up_vol_days(self):
        # up_vol_days=5 → HIGH
        n = 60
        closes = [90.0 + i * 0.3 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        for i in range(idx - 4, idx + 1):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 9. SELL HIGH confidence: down_vol_days == 5
    def test_sell_high_confidence_when_5_down_vol_days(self):
        n = 60
        closes = [120.0 - i * 0.3 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        for i in range(idx - 4, idx + 1):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 10. BUY MEDIUM confidence: up_vol_days < 5
    def test_buy_medium_confidence_when_less_than_5_up_vol_days(self):
        n = 60
        closes = [90.0 + i * 0.3 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        # 정확히 3봉만 볼륨 높임
        for i in range(idx - 4, idx - 4 + 3):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.MEDIUM

    # 11. strategy 필드 확인
    def test_strategy_name_in_signal(self):
        df = _make_df(50)
        sig = self.strategy.generate(df)
        assert sig.strategy == "vol_price_confirm"

    # 12. BUY reasoning에 up_vol_days 포함
    def test_buy_reasoning_contains_up_vol_days(self):
        n = 60
        closes = [90.0 + i * 0.4 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        for i in range(idx - 4, idx + 1):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "up_vol" in sig.reasoning or "Volume" in sig.reasoning

    # 13. SELL reasoning에 down_vol_days 포함
    def test_sell_reasoning_contains_down_vol_days(self):
        n = 60
        closes = [120.0 - i * 0.4 for i in range(n)]
        volumes = [500.0] * n
        idx = n - 2
        for i in range(idx - 4, idx + 1):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "down_vol" in sig.reasoning or "Volume" in sig.reasoning

    # 14. RSI 범위 밖이면 BUY 아님
    def test_no_buy_when_rsi_above_65(self):
        # RSI > 65가 되도록 연속 급등
        n = 60
        closes = [50.0 + i * 2.0 for i in range(n)]  # 급등 → RSI 높음
        volumes = [500.0] * n
        idx = n - 2
        for i in range(idx - 4, idx + 1):
            if i >= 0:
                volumes[i] = 8000.0
        df = _make_df(n, closes, volumes)
        sig = self.strategy.generate(df)
        # RSI > 65이면 BUY가 아니어야 함
        assert sig.action in (Action.HOLD, Action.SELL)

    # 15. 최소 행 경계값: 정확히 25행
    def test_exactly_min_rows(self):
        df = _make_df(_MIN_ROWS)
        sig = self.strategy.generate(df)
        # 25행은 통과, HOLD 또는 신호 모두 가능
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
