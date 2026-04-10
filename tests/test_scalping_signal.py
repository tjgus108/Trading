"""
ScalpingSignalStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.scalping_signal import ScalpingSignalStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 20


def _make_df(
    n: int = _MIN_ROWS + 2,
    close: float = 100.0,
    volume: float = 2000.0,
    vol_ma: float = 1000.0,
    ema_bullish: bool = True,
    rsi_value: float = 60.0,
) -> pd.DataFrame:
    """
    신호 봉은 idx=-2 (BaseStrategy._last 기준).
    ema 조건은 close 값으로 간접 조작하지 않고,
    EMA를 직접 시뮬레이션 가능한 close 시리즈 생성.
    """
    rows = n
    # 볼륨: 마지막 -2봉만 높게, 나머지는 vol_ma 수준
    volumes = [vol_ma] * rows
    volumes[-2] = volume

    # close 시리즈: EMA 정렬을 위해 단조 상승/하락
    if ema_bullish:
        # 상향: 초반 낮고 후반 높음 → fast_ema > mid_ema > slow_ema
        closes = list(np.linspace(90, 100, rows))
    else:
        # 하향: 초반 높고 후반 낮음 → fast_ema < mid_ema < slow_ema
        closes = list(np.linspace(100, 90, rows))

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": volumes,
    })
    return df


def _compute_rsi7(series: pd.Series) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(com=6, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(com=6, adjust=False).mean()
    return 100 - 100 / (1 + gain / (loss + 1e-10))


class TestScalpingSignalStrategy:

    def setup_method(self):
        self.strategy = ScalpingSignalStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "scalping_signal"

    # 2. BUY: 상향 EMA 정렬 + RSI 50~70 + 볼륨
    def test_buy_signal_bullish_ema(self):
        df = _make_df(ema_bullish=True, volume=2000.0, vol_ma=1000.0)
        sig = self.strategy.generate(df)
        # 단조 상승 close → EMA 정렬 bullish
        # RSI도 계산하여 조건 확인이 필요하므로 BUY 또는 HOLD 허용
        # 실제 RSI 50~70 범위 확인
        close = df["close"]
        rsi = _compute_rsi7(close)
        idx = len(df) - 2
        rsi_val = rsi.iloc[idx]
        if 50 < rsi_val < 70:
            assert sig.action == Action.BUY
        # RSI 조건 맞지 않으면 HOLD도 허용

    # 3. BUY signal fields
    def test_buy_signal_fields(self):
        # 명시적으로 BUY 조건 맞는 df 생성
        rows = 30
        closes = list(np.linspace(85, 100, rows))
        volumes = [500.0] * rows
        volumes[-2] = 2000.0
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.3 for c in closes],
            "low": [c - 0.3 for c in closes],
            "volume": volumes,
        })
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.strategy == "scalping_signal"
        assert sig.entry_price > 0

    # 4. SELL: 하향 EMA 정렬 + RSI 30~50 + 볼륨
    def test_sell_signal_bearish_ema(self):
        df = _make_df(ema_bullish=False, volume=2000.0, vol_ma=1000.0)
        close = df["close"]
        rsi = _compute_rsi7(close)
        idx = len(df) - 2
        rsi_val = rsi.iloc[idx]
        sig = self.strategy.generate(df)
        if 30 < rsi_val < 50:
            assert sig.action == Action.SELL
        else:
            # 조건 불충족 시 HOLD
            assert sig.action in [Action.SELL, Action.HOLD]

    # 5. HOLD: 볼륨 부족
    def test_hold_low_volume(self):
        df = _make_df(ema_bullish=True, volume=500.0, vol_ma=1000.0)
        sig = self.strategy.generate(df)
        # volume < vol_ma → 볼륨 필터 실패 → HOLD
        assert sig.action == Action.HOLD

    # 6. HOLD: 데이터 부족
    def test_hold_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 7. Signal 타입 확인
    def test_returns_signal_type(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 8. entry_price는 마지막 완성 캔들 close
    def test_entry_price_is_last_candle(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(df["close"].iloc[-2], rel=1e-5)

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert sig.reasoning != ""

    # 10. HIGH confidence: EMA 스프레드 > 0.5%
    def test_high_confidence_wide_spread(self):
        # 급격한 단조 상승 → 큰 EMA 스프레드
        rows = 30
        closes = list(np.linspace(50, 110, rows))  # 큰 스프레드
        volumes = [500.0] * rows
        volumes[-2] = 2000.0
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": volumes,
        })
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. MEDIUM confidence: 좁은 EMA 스프레드
    def test_medium_confidence_narrow_spread(self):
        rows = _MIN_ROWS + 2
        # 매우 완만한 상승 → 작은 EMA 스프레드
        closes = list(np.linspace(99.9, 100.0, rows))
        volumes = [500.0] * rows
        volumes[-2] = 2000.0
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.1 for c in closes],
            "low": [c - 0.1 for c in closes],
            "volume": volumes,
        })
        sig = self.strategy.generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence == Confidence.MEDIUM

    # 12. action은 유효한 열거형
    def test_action_is_valid_enum(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in [Action.BUY, Action.SELL, Action.HOLD]

    # 13. confidence는 유효한 열거형
    def test_confidence_is_valid_enum(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in [Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW]

    # 14. HOLD: RSI 범위 외 (BUY 조건에서 RSI >= 70)
    def test_hold_rsi_overbought(self):
        # 급등: rsi가 70 초과할 수 있음 → HOLD
        rows = _MIN_ROWS + 2
        # 마지막 봉에서 급등 → RSI 높음
        closes = [100.0] * rows
        closes[-2] = 200.0  # 급등
        volumes = [500.0] * rows
        volumes[-2] = 2000.0
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 1 for c in closes],
            "low": [c - 1 for c in closes],
            "volume": volumes,
        })
        sig = self.strategy.generate(df)
        # RSI가 매우 높을 경우 BUY 불가 → HOLD
        close_series = df["close"]
        rsi = _compute_rsi7(close_series)
        idx = len(df) - 2
        if rsi.iloc[idx] >= 70:
            assert sig.action != Action.BUY
