"""
ADXRegimeStrategy: ADX 기반 시장 레짐 필터 전략.

트렌딩 시장 (ADX > 25):
  BUY:  +DI14 > -DI14
  SELL: -DI14 > +DI14

횡보 시장 (ADX < 20): HOLD

confidence: HIGH if ADX > 35, MEDIUM if ADX > 25
최소 데이터: 30행

adx_trend.py와 달리 EWM 방식으로 DM/ATR 계산하며 EMA50 조건 없음.
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_ADX_TRENDING = 25.0
_ADX_SIDEWAYS = 20.0
_ADX_HIGH = 35.0
_EWM_SPAN = 14


class ADXRegimeStrategy(BaseStrategy):
    name = "adx_regime"

    def __init__(
        self,
        adx_trending: float = _ADX_TRENDING,
        adx_sideways: float = _ADX_SIDEWAYS,
        adx_high: float = _ADX_HIGH,
    ):
        self.adx_trending = adx_trending
        self.adx_sideways = adx_sideways
        self.adx_high = adx_high

    def _compute(self, df: pd.DataFrame):
        """EWM 방식으로 ATR14, +DI14, -DI14, ADX 계산. Tuple 반환."""
        high = df["high"]
        low = df["low"]
        close = df["close"]

        prev_high = high.shift(1)
        prev_low = low.shift(1)
        prev_close = close.shift(1)

        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        up_move = high - prev_high
        down_move = prev_low - low

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        plus_dm_s = pd.Series(plus_dm, index=df.index, dtype=float)
        minus_dm_s = pd.Series(minus_dm, index=df.index, dtype=float)

        atr14 = tr.ewm(span=_EWM_SPAN, adjust=False).mean()
        plus_dm14 = plus_dm_s.ewm(span=_EWM_SPAN, adjust=False).mean()
        minus_dm14 = minus_dm_s.ewm(span=_EWM_SPAN, adjust=False).mean()

        with np.errstate(divide="ignore", invalid="ignore"):
            plus_di = (plus_dm14 / atr14.replace(0, float("nan"))) * 100
            minus_di = (minus_dm14 / atr14.replace(0, float("nan"))) * 100

        plus_di = plus_di.fillna(0.0)
        minus_di = minus_di.fillna(0.0)

        di_sum = plus_di + minus_di
        dx = ((plus_di - minus_di).abs() / di_sum.replace(0, float("nan"))) * 100
        dx = dx.fillna(0.0)

        adx = dx.ewm(span=_EWM_SPAN, adjust=False).mean()

        return adx, plus_di, minus_di

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="ADX Regime 계산에 필요한 데이터 부족 (최소 30행).",
                invalidation="",
            )

        adx_s, plus_di_s, minus_di_s = self._compute(df)

        adx_val = float(adx_s.iloc[-2])
        plus_di_val = float(plus_di_s.iloc[-2])
        minus_di_val = float(minus_di_s.iloc[-2])
        close_val = float(df["close"].iloc[-2])

        context = (
            f"ADX={adx_val:.1f} +DI={plus_di_val:.1f} -DI={minus_di_val:.1f} "
            f"close={close_val:.4f}"
        )

        if adx_val < self.adx_sideways:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"ADX < {self.adx_sideways} (횡보 시장, 신호 없음). {context}",
                invalidation=f"ADX >= {self.adx_trending} 진입 시 재평가.",
            )

        if adx_val < self.adx_trending:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"ADX {adx_val:.1f} 전환 구간 (횡보↔추세). {context}",
                invalidation=f"ADX >= {self.adx_trending} 또는 < {self.adx_sideways} 이동 시 재평가.",
            )

        confidence = Confidence.HIGH if adx_val > self.adx_high else Confidence.MEDIUM

        if plus_di_val > minus_di_val:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"트렌딩 시장 상승 추세 (+DI > -DI). {context}",
                invalidation="-DI > +DI 전환 또는 ADX < 20 하락 시 무효.",
                bull_case=f"ADX={adx_val:.1f} 강한 추세, +DI 우위.",
                bear_case="-DI/+DI 역전 시 추세 반전 위험.",
            )

        if minus_di_val > plus_di_val:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"트렌딩 시장 하락 추세 (-DI > +DI). {context}",
                invalidation="+DI > -DI 전환 또는 ADX < 20 하락 시 무효.",
                bull_case="+DI/-DI 역전 시 추세 반전 가능.",
                bear_case=f"ADX={adx_val:.1f} 강한 추세, -DI 우위.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"ADX 추세 시장이나 +DI/-DI 동일. {context}",
            invalidation="+DI 또는 -DI 우위 확립 시 신호 발생.",
        )
