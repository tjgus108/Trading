"""
RegimeFilterStrategy: 시장 레짐 감지 후 레짐 맞춤 신호.

레짐:
  TREND_UP:   ema20 > ema50 * 1.02
  TREND_DOWN: ema20 < ema50 * 0.98
  RANGING:    |ema20 - ema50| / ema50 < 0.02 AND not high_vol
  HIGH_VOL:   atr_ratio > atr_ratio_mean20 * 1.5

신호:
  BUY:  TREND_UP  AND close > rolling(5).max().shift(1)
  SELL: TREND_DOWN AND close < rolling(5).min().shift(1)
  HOLD: RANGING 또는 HIGH_VOL
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 60


class RegimeFilterStrategy(BaseStrategy):
    name = "regime_filter"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="Insufficient data for regime_filter",
                invalidation="",
            )

        idx = len(df) - 2
        close = df["close"]

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        # ATR14
        high = df["high"]
        low_ = df["low"]
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low_,
            (high - prev_close).abs(),
            (low_ - prev_close).abs(),
        ], axis=1).max(axis=1)
        atr14 = tr.rolling(14).mean()
        atr_ratio = atr14 / close.replace(0, float("nan"))

        atr_ratio_mean20 = atr_ratio.rolling(20).mean()

        e20 = float(ema20.iloc[idx])
        e50 = float(ema50.iloc[idx])
        ar = float(atr_ratio.iloc[idx]) if not pd.isna(atr_ratio.iloc[idx]) else 0.0
        ar_mean = float(atr_ratio_mean20.iloc[idx]) if not pd.isna(atr_ratio_mean20.iloc[idx]) else float("inf")

        close_now = float(close.iloc[idx])

        # regime flags
        high_vol = ar > ar_mean * 1.5 if ar_mean > 0 else False
        trend_up = e20 > e50 * 1.02
        trend_down = e20 < e50 * 0.98
        ema_diff_ratio = abs(e20 - e50) / max(e50, 1e-10)
        ranging = (ema_diff_ratio < 0.02) and not high_vol

        # rolling 5-bar max/min (shift 1 = previous bar's value)
        roll5_max = close.rolling(5).max().shift(1)
        roll5_min = close.rolling(5).min().shift(1)
        prev_max = float(roll5_max.iloc[idx]) if not pd.isna(roll5_max.iloc[idx]) else float("inf")
        prev_min = float(roll5_min.iloc[idx]) if not pd.isna(roll5_min.iloc[idx]) else 0.0

        # confidence
        conf = (
            Confidence.HIGH
            if trend_up and ar < ar_mean * 0.8
            else Confidence.MEDIUM
        )

        if trend_up and close_now > prev_max:
            regime_str = "TREND_UP"
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"레짐={regime_str}, ema20={e20:.4f} > ema50*1.02={e50*1.02:.4f}, "
                    f"close={close_now:.4f} > 5bar_max={prev_max:.4f}"
                ),
                invalidation="ema20 < ema50 또는 close < 5bar_max",
                bull_case=f"ema20/ema50 ratio={e20/max(e50,1e-10):.4f}, atr_ratio={ar:.5f}",
                bear_case=f"atr_ratio_mean={ar_mean:.5f}",
            )

        if trend_down and close_now < prev_min:
            regime_str = "TREND_DOWN"
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"레짐={regime_str}, ema20={e20:.4f} < ema50*0.98={e50*0.98:.4f}, "
                    f"close={close_now:.4f} < 5bar_min={prev_min:.4f}"
                ),
                invalidation="ema20 > ema50 또는 close > 5bar_min",
                bull_case=f"atr_ratio={ar:.5f}",
                bear_case=f"ema20/ema50 ratio={e20/max(e50,1e-10):.4f}",
            )

        if ranging:
            regime_label = "RANGING"
        elif high_vol:
            regime_label = "HIGH_VOL"
        elif trend_up:
            regime_label = "TREND_UP (no breakout)"
        elif trend_down:
            regime_label = "TREND_DOWN (no breakdown)"
        else:
            regime_label = "UNDEFINED"

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_now,
            reasoning=f"레짐={regime_label}, 진입 조건 미충족",
            invalidation="TREND_UP+돌파 또는 TREND_DOWN+붕괴 필요",
            bull_case=f"ema20={e20:.4f}, ema50={e50:.4f}",
            bear_case=f"atr_ratio={ar:.5f}",
        )
