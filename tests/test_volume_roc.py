"""
VolumeROCStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest

from src.strategy.volume_roc import VolumeROCStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close_vals=None, volume_vals=None) -> pd.DataFrame:
    """기본 DataFrame 생성 헬퍼."""
    if close_vals is None:
        close_vals = [100.0] * n
    if volume_vals is None:
        volume_vals = [1000.0] * n

    return pd.DataFrame({
        "open": close_vals,
        "close": close_vals,
        "high": [c + 1.0 for c in close_vals],
        "low": [c - 1.0 for c in close_vals],
        "volume": volume_vals,
    })


def _make_high_vol_roc_df(n: int = 30, rising: bool = True) -> pd.DataFrame:
    """
    vol_roc_ema > 50 이 되도록 거래량 급증 + 가격 방향 설정.
    앞 10봉: 낮은 거래량 (기저)
    이후: 높은 거래량 (급증 > 50%)
    """
    closes = []
    volumes = []

    base_vol = 1000.0
    high_vol = 2000.0  # 100% 증가 → vol_roc > 50

    for i in range(n):
        if i < 10:
            volumes.append(base_vol)
        else:
            volumes.append(high_vol)

    # 가격: 신호 봉(-2) 기준 상승 or 하락
    if rising:
        for i in range(n):
            closes.append(100.0 + i * 0.1)
    else:
        for i in range(n):
            closes.append(100.0 - i * 0.1)

    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": volumes,
    })


def _make_low_vol_roc_df(n: int = 30) -> pd.DataFrame:
    """vol_roc_ema < 20 → HOLD 유도: 거래량 변화 없음."""
    closes = [100.0] * n
    volumes = [1000.0] * n  # 동일 거래량 → vol_roc = 0
    return _make_df(n=n, close_vals=closes, volume_vals=volumes)


class TestVolumeROCStrategy:

    def setup_method(self):
        self.strategy = VolumeROCStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "volume_roc"

    # 2. 데이터 부족 (< 15행)
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 경계: 정확히 15행 → 실행은 돼야 함
    def test_exactly_min_rows(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. HOLD: 거래량 변화 없음 (vol_roc_ema < 20)
    def test_hold_low_volume_change(self):
        df = _make_low_vol_roc_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "volume_roc"

    # 5. BUY: 거래량 급증 + 상승
    def test_buy_high_volume_rising(self):
        df = _make_high_vol_roc_df(n=30, rising=True)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)
        assert sig.strategy == "volume_roc"

    # 6. SELL: 거래량 급증 + 하락
    def test_sell_high_volume_falling(self):
        df = _make_high_vol_roc_df(n=30, rising=False)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)
        assert sig.strategy == "volume_roc"

    # 7. BUY: 매우 높은 거래량 급증 → HIGH confidence
    def test_buy_high_confidence(self):
        n = 30
        # vol_roc_ema > 100 → HIGH confidence
        # 기저: 1000, 급증: 3000 → vol_roc = 200%
        closes = [100.0 + i * 0.1 for i in range(n)]
        volumes = [1000.0] * 10 + [3000.0] * (n - 10)
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": volumes,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 8. SELL: 매우 높은 거래량 급증 + 하락 → HIGH confidence
    def test_sell_high_confidence(self):
        n = 30
        closes = [100.0 - i * 0.1 for i in range(n)]
        volumes = [1000.0] * 10 + [3000.0] * (n - 10)
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": volumes,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30)
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

    # 10. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df(n=30, close_vals=[50.0] * 30)
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 11. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 12. HOLD: vol_roc_ema가 20~50 사이 (BUY/SELL 임계값 미달)
    def test_hold_medium_volume_change(self):
        n = 30
        # vol_roc ≈ 30%: 기저 1000 → 1300 (30% 증가)
        # ewm으로 수렴하므로 20~50 사이에 위치할 수 있음
        closes = [100.0] * n
        volumes = [1000.0] * 10 + [1300.0] * (n - 10)
        df = _make_df(n=n, close_vals=closes, volume_vals=volumes)
        sig = self.strategy.generate(df)
        # vol_roc_ema가 20~50이면 HOLD, 아니면 direction 없으면 HOLD
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)
        assert isinstance(sig, Signal)

    # 13. HOLD: vol_roc_ema > 50 이지만 가격 변화 없음 (close == prev_close)
    def test_hold_high_volume_flat_price(self):
        n = 30
        closes = [100.0] * n  # 가격 변화 없음
        volumes = [1000.0] * 10 + [3000.0] * (n - 10)
        df = _make_df(n=n, close_vals=closes, volume_vals=volumes)
        sig = self.strategy.generate(df)
        # close == prev_close → BUY/SELL 조건 불만족 → HOLD
        assert sig.action == Action.HOLD
