"""
AccelerationBandStrategy: Headley Acceleration Bands 돌파 전략.

개선 사항 (Cycle 122):
- RSI 필터 추가: BUY시 RSI<70, SELL시 RSI>30 (과매수/과매도 회피)
- 밴드 폭 필터 강화: strong_band 임계값 상향 (0.015→0.025)
- 추세 필터 개선: 더 명확한 고점/저점 기준
- 목표: PF 1.511 → 1.7+, 손실 거래 감소

원리:
- upper = sma20 * (1 + 4 * sma20((high-low)/(high+low)))
- lower = sma20 * (1 - 4 * sma20((high-low)/(high+low)))
- BUY:  close crosses above upper + RSI<70 + trend/vol
- SELL: close crosses below lower + RSI>30 + trend/vol
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

        # 신호는 -2에서 발생, 현재는 -1
        idx = len(df) - 2
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])
        upper_now = float(upper.iloc[idx])
        upper_prev = float(upper.iloc[idx - 1])
        lower_now = float(lower.iloc[idx])
        lower_prev = float(lower.iloc[idx - 1])

        # ✅ NEW: RSI 필터
        rsi_val = 50.0
        if "rsi14" in df.columns:
            rsi_raw = float(df["rsi14"].iloc[idx])
            if rsi_raw == rsi_raw:  # NaN check
                rsi_val = rsi_raw

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
        vol_ok = current_range > recent_range * 0.5

        # ✅ 밴드 폭 강도 (기준 강화: 0.015 → 0.025)
        band_width = (upper_now - lower_now) / close_now if close_now > 0 else 0
        strong_band = band_width > 0.025  # 강한 신호: 2.5% 이상

        context = (
            f"close={close_now:.2f} upper={upper_now:.2f} lower={lower_now:.2f} "
            f"rsi={rsi_val:.1f} trend_up={trend_up} trend_down={trend_down} vol_ok={vol_ok} band_width={band_width:.4f}"
        )

        # BUY: close crosses above upper + RSI<70 + (trend_up OR vol_ok)
        if close_prev <= upper_prev and close_now > upper_now and rsi_val < 70 and (trend_up or vol_ok):
            # HIGH confidence if 강한 돌파 + 강한 밴드 + 추세
            confidence = (
                Confidence.HIGH 
                if (close_now > upper_now * _HIGH_CONF_MARGIN and strong_band and trend_up)
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Upper band breakout (RSI<70, trend OR vol): close={close_now:.2f} > upper={upper_now:.2f}, "
                    f"RSI={rsi_val:.1f}, trend_up={trend_up}, vol_ok={vol_ok}, band_width={band_width:.4f}"
                ),
                invalidation=f"close <= upper={upper_now:.2f} or RSI>=70",
                bull_case=context,
                bear_case=context,
            )

        # SELL: close crosses below lower + RSI>30 + (trend_down OR vol_ok)
        if close_prev >= lower_prev and close_now < lower_now and rsi_val > 30 and (trend_down or vol_ok):
            # HIGH confidence if 강한 돌파 + 강한 밴드 + 추세
            confidence = (
                Confidence.HIGH 
                if (close_now < lower_now / _HIGH_CONF_MARGIN and strong_band and trend_down)
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Lower band breakout (RSI>30, trend OR vol): close={close_now:.2f} < lower={lower_now:.2f}, "
                    f"RSI={rsi_val:.1f}, trend_down={trend_down}, vol_ok={vol_ok}, band_width={band_width:.4f}"
                ),
                invalidation=f"close >= lower={lower_now:.2f} or RSI<=30",
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
                f"rsi_ok={rsi_val < 70 or rsi_val > 30}, trend_or_vol={(trend_up or trend_down or vol_ok)}"
            ),
            invalidation="",
            bull_case=context,
            bear_case=context,
        )
