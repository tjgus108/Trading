"""
TrendFollowBreakStrategy: ADX 추세 강도 필터 + 가격 돌파 결합 전략.

- ADX(14) 계산: TR/+DM/-DM → rolling(14).mean() 방식
- highest = high.rolling(20).max().shift(1)
- lowest  = low.rolling(20).min().shift(1)
- BUY:  ADX > 25 AND close > highest (상단 돌파)
- SELL: ADX > 25 AND close < lowest  (하단 돌파)
- HOLD: ADX <= 25 (추세 약함)
- confidence: HIGH if ADX > 35 else MEDIUM
- 최소 40행 필요
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_ADX_PERIOD = 14
_BREAK_PERIOD = 20
_ADX_THRESHOLD = 25.0
_ADX_HIGH = 35.0


class TrendFollowBreakStrategy(BaseStrategy):
    """ADX 추세 필터 + 돌파 신호 전략."""

    name = "trend_follow_break"

    def __init__(
        self,
        adx_period: int = _ADX_PERIOD,
        break_period: int = _BREAK_PERIOD,
        adx_threshold: float = _ADX_THRESHOLD,
        adx_high: float = _ADX_HIGH,
    ):
        self.adx_period = adx_period
        self.break_period = break_period
        self.adx_threshold = adx_threshold
        self.adx_high = adx_high

    def _compute_adx(self, df: pd.DataFrame) -> pd.Series:
        """rolling mean 방식 ADX 계산. pandas Series로 반환."""
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)

        prev_close = close.shift(1)
        prev_high = high.shift(1)
        prev_low = low.shift(1)

        # True Range
        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        # +DM / -DM
        up_move = high - prev_high
        down_move = prev_low - low

        plus_dm = pd.Series(
            np.where((up_move > 0) & (up_move > down_move), up_move, 0.0),
            index=df.index,
        )
        minus_dm = pd.Series(
            np.where((down_move > 0) & (down_move > up_move), down_move, 0.0),
            index=df.index,
        )

        p = self.adx_period
        atr_smooth = tr.rolling(p).mean()
        plus_dm_smooth = plus_dm.rolling(p).mean()
        minus_dm_smooth = minus_dm.rolling(p).mean()

        plus_di = 100.0 * plus_dm_smooth / atr_smooth.replace(0, np.nan)
        minus_di = 100.0 * minus_dm_smooth / atr_smooth.replace(0, np.nan)

        di_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = 100.0 * (plus_di - minus_di).abs() / di_sum
        adx = dx.rolling(p).mean()

        return adx.fillna(0.0)

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            n = len(df) if df is not None else 0
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Insufficient data: {n}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 데이터 확보 후 재평가",
            )

        idx = len(df) - 2  # 마지막 완성봉

        adx_series = self._compute_adx(df)
        adx_val = float(adx_series.iloc[idx])

        highest = df["high"].rolling(self.break_period).max().shift(1)
        lowest = df["low"].rolling(self.break_period).min().shift(1)

        close = float(df["close"].iloc[idx])
        highest_val = float(highest.iloc[idx])
        lowest_val = float(lowest.iloc[idx])
        entry = close

        reasoning_base = (
            f"ADX={adx_val:.1f}, close={close:.4f}, "
            f"highest={highest_val:.4f}, lowest={lowest_val:.4f}"
        )

        if adx_val <= self.adx_threshold:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ADX={adx_val:.1f} <= {self.adx_threshold} — 추세 약함. {reasoning_base}",
                invalidation=f"ADX > {self.adx_threshold} 초과 시 재평가",
            )

        if pd.isna(highest_val) or pd.isna(lowest_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"돌파 기준값 NaN. {reasoning_base}",
                invalidation="충분한 롤링 데이터 확보 후 재평가",
            )

        confidence = Confidence.HIGH if adx_val > self.adx_high else Confidence.MEDIUM

        # BUY: 상단 돌파
        if close > highest_val:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"추세 돌파 BUY: ADX={adx_val:.1f} > {self.adx_threshold}, close > highest. {reasoning_base}",
                invalidation=f"close < highest({highest_val:.4f}) 또는 ADX <= {self.adx_threshold} 시 무효",
                bull_case="강한 추세 + 상단 돌파 — 상승 지속 기대",
                bear_case="가짜 돌파 시 되돌림 위험",
            )

        # SELL: 하단 돌파
        if close < lowest_val:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"추세 돌파 SELL: ADX={adx_val:.1f} > {self.adx_threshold}, close < lowest. {reasoning_base}",
                invalidation=f"close > lowest({lowest_val:.4f}) 또는 ADX <= {self.adx_threshold} 시 무효",
                bull_case="하락 추세 반전 시 반등 가능",
                bear_case="강한 하락 추세 + 하단 돌파 — 추가 하락 기대",
            )

        # ADX > 25이나 돌파 없음
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"ADX > {self.adx_threshold}이나 돌파 없음 (HOLD). {reasoning_base}",
            invalidation="close > highest 또는 close < lowest 돌파 시 신호 발생",
        )
