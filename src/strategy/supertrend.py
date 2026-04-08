"""
SuperTrend 전략: ATR 기반 동적 지지/저항선으로 추세 전환 감지.
추세 방향 전환 시 BUY/SELL HIGH, 지속 시 HOLD.
개선:
  - 볼륨 필터: 20봉 평균 이상일 때만 신호 (volume 컬럼이 있을 때 활성화)
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SuperTrendStrategy(BaseStrategy):
    name = "supertrend"

    def __init__(self, period: int = 10, multiplier: float = 2.5):
        self.period = period
        self.multiplier = multiplier

    def _compute_supertrend(self, df: pd.DataFrame) -> pd.Series:
        """SuperTrend 방향 계산. True=buy 추세, False=sell 추세."""
        hl2 = (df["high"] + df["low"]) / 2
        atr = df["atr14"]

        basic_upper = hl2 + self.multiplier * atr
        basic_lower = hl2 - self.multiplier * atr

        upper = basic_upper.copy()
        lower = basic_lower.copy()
        trend = pd.Series(True, index=df.index)  # True = buy(bullish)

        for i in range(1, len(df)):
            prev_upper = upper.iloc[i - 1]
            prev_lower = lower.iloc[i - 1]
            close_prev = df["close"].iloc[i - 1]

            # upper band: only tighten (decrease) if previous close was above prev upper
            cur_upper = basic_upper.iloc[i]
            if cur_upper < prev_upper or close_prev > prev_upper:
                upper.iloc[i] = cur_upper
            else:
                upper.iloc[i] = prev_upper

            # lower band: only tighten (increase) if previous close was below prev lower
            cur_lower = basic_lower.iloc[i]
            if cur_lower > prev_lower or close_prev < prev_lower:
                lower.iloc[i] = cur_lower
            else:
                lower.iloc[i] = prev_lower

            close = df["close"].iloc[i]
            prev_trend = trend.iloc[i - 1]

            if prev_trend:  # was buy
                trend.iloc[i] = close >= lower.iloc[i]
            else:  # was sell
                trend.iloc[i] = close > upper.iloc[i]

        return trend

    def generate(self, df: pd.DataFrame) -> Signal:
        min_required = max(self.period + 1, 3)
        if len(df) < min_required or "atr14" not in df.columns:
            last_close = df["close"].iloc[-1] if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning="데이터 부족 또는 atr14 컬럼 없음.",
                invalidation="",
            )

        trend = self._compute_supertrend(df)

        prev_trend = trend.iloc[-3]   # 직전 완성 캔들 전
        last_trend = trend.iloc[-2]   # 직전 완성 캔들 (_last 기준)
        entry = float(df["close"].iloc[-2])

        turned_buy = (not prev_trend) and last_trend
        turned_sell = prev_trend and (not last_trend)

        # 볼륨 필터: volume 컬럼이 있을 때 20봉 평균 이상이어야 신호 발생
        vol_ok = True
        vol_info = ""
        if "volume" in df.columns:
            vol_lookback = min(20, len(df) - 1)
            avg_vol = df["volume"].iloc[-vol_lookback - 1 : -1].mean()
            cur_vol = float(df["volume"].iloc[-2])
            vol_ok = cur_vol >= avg_vol
            vol_info = f" Vol={cur_vol:.1f} AvgVol={avg_vol:.1f}"

        if turned_buy and vol_ok:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SuperTrend sell→buy 추세 전환.{vol_info}",
                invalidation="SuperTrend 재하락 전환 시 무효.",
                bull_case="ATR 기반 하단 지지선 돌파 확인.",
                bear_case="추세 전환 실패 가능성 존재.",
            )

        if turned_sell and vol_ok:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SuperTrend buy→sell 추세 전환.{vol_info}",
                invalidation="SuperTrend 재상승 전환 시 무효.",
                bull_case="추세 전환 실패 가능성 존재.",
                bear_case="ATR 기반 상단 저항선 하향 돌파 확인.",
            )

        direction = "buy" if last_trend else "sell"
        hold_reason = f"SuperTrend {direction} 추세 지속 중."
        if (turned_buy or turned_sell) and not vol_ok:
            hold_reason = f"SuperTrend 추세 전환 감지됐으나 볼륨 미달.{vol_info}"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning=hold_reason,
            invalidation="",
        )
