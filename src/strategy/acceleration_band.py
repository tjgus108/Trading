"""
AccelerationBandStrategy: Headley Acceleration Bands 돌파 전략.
개선: 추세 필터 + 변동성 확인 + 신호 강화
- upper = sma20 * (1 + 4 * sma20((high-low)/(high+low)))
- lower = sma20 * (1 - 4 * sma20((high-low)/(high+low)))
- BUY:  close crosses above upper + trend_up + vol_ok → HIGH
- SELL: close crosses below lower + trend_down + vol_ok → HIGH
- confidence: HIGH if (crossover + strong trend)
- 최소 행: 25
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20
_HIGH_CONF_MARGIN = 1.005


class AccelerationBandStrategy(BaseStrategy):
    name = "acceleration_band"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        sma = df["close"].rolling(_PERIOD).mean()
        hl_ratio = (df["high"] - df["low"]) / (df["high"] + df["low"]).replace(0, 1e-10)
        hl_sma = hl_ratio.rolling(_PERIOD).mean()

        upper = sma * (1 + 4 * hl_sma)
        lower = sma * (1 - 4 * hl_sma)

        idx = len(df) - 2
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])
        upper_now = float(upper.iloc[idx])
        upper_prev = float(upper.iloc[idx - 1])
        lower_now = float(lower.iloc[idx])
        lower_prev = float(lower.iloc[idx - 1])

        # 추세 필터: 14기간 최고가/최저가
        trend_lookback = min(14, len(df) - 1)
        high_14 = float(df["high"].iloc[-trend_lookback - 1:-1].max())
        low_14 = float(df["low"].iloc[-trend_lookback - 1:-1].min())
        trend_up = close_now >= high_14 * 0.98
        trend_down = close_now <= low_14 * 1.02

        # 변동성 필터: 최근 10개 캔들의 평균 변동성
        vol_lookback = min(10, len(df) - 1)
        recent_range = (df["high"].iloc[-vol_lookback - 1:-1].max() - 
                       df["low"].iloc[-vol_lookback - 1:-1].min())
        current_range = df["high"].iloc[idx] - df["low"].iloc[idx]
        vol_ok = current_range > recent_range * 0.7  # 현재 범위가 평균의 70% 이상

        # 밴드 폭 강도
        band_width = (upper_now - lower_now) / close_now if close_now > 0 else 0
        strong_band = band_width > 0.02  # 밴드 폭이 2% 이상 (강한 신호)

        context = (
            f"close={close_now:.2f} upper={upper_now:.2f} lower={lower_now:.2f} "
            f"trend_up={trend_up} trend_down={trend_down} vol_ok={vol_ok} band_width={band_width:.4f}"
        )

        # BUY: close crosses above upper + trend_up + vol_ok
        if close_prev <= upper_prev and close_now > upper_now and trend_up and vol_ok:
            # HIGH confidence if 강한 돌파 + 강한 밴드
            confidence = (
                Confidence.HIGH 
                if (close_now > upper_now * _HIGH_CONF_MARGIN and strong_band)
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Upper band breakout (trend+vol): close={close_now:.2f} > upper={upper_now:.2f}, "
                    f"trend_up={trend_up}, vol_ok={vol_ok}, band_width={band_width:.4f}"
                ),
                invalidation=f"close <= upper={upper_now:.2f}",
                bull_case=context,
                bear_case=context,
            )

        # SELL: close crosses below lower + trend_down + vol_ok
        if close_prev >= lower_prev and close_now < lower_now and trend_down and vol_ok:
            # HIGH confidence if 강한 돌파 + 강한 밴드
            confidence = (
                Confidence.HIGH 
                if (close_now < lower_now / _HIGH_CONF_MARGIN and strong_band)
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Lower band breakout (trend+vol): close={close_now:.2f} < lower={lower_now:.2f}, "
                    f"trend_down={trend_down}, vol_ok={vol_ok}, band_width={band_width:.4f}"
                ),
                invalidation=f"close >= lower={lower_now:.2f}",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_now,
            reasoning=(
                f"No crossover or filters failed: "
                f"crossover={close_prev <= upper_prev and close_now > upper_now or close_prev >= lower_prev and close_now < lower_now}, "
                f"trend_up={trend_up}, trend_down={trend_down}, vol_ok={vol_ok}"
            ),
            invalidation="",
            bull_case=context,
            bear_case=context,
        )
