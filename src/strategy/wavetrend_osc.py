"""
WaveTrendOscStrategy: WaveTrend Oscillator (LazyBear) 기반 전략.
과매도 구간에서 wt1이 wt2를 상향 돌파 시 BUY,
과매수 구간에서 하향 돌파 시 SELL.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


class WaveTrendOscStrategy(BaseStrategy):
    name = "wavetrend_osc"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data: need {_MIN_ROWS} rows, got {len(df)}")

        hlc3 = (df["high"] + df["low"] + df["close"]) / 3

        ema1 = hlc3.ewm(span=10, adjust=False).mean()
        d = (hlc3 - ema1).abs().ewm(span=10, adjust=False).mean()
        ci = (hlc3 - ema1) / (0.015 * d.replace(0, 0.0001))
        wt1 = ci.ewm(span=21, adjust=False).mean()
        wt2 = wt1.rolling(4).mean()

        idx = len(df) - 2
        last = df.iloc[-2]

        # NaN check
        if pd.isna(wt1.iloc[idx]) or pd.isna(wt2.iloc[idx]) or pd.isna(wt1.iloc[idx - 1]) or pd.isna(wt2.iloc[idx - 1]):
            return self._hold(df, "NaN in WaveTrend values")

        wt1_cur = float(wt1.iloc[idx])
        wt2_cur = float(wt2.iloc[idx])
        wt1_prev = float(wt1.iloc[idx - 1])
        wt2_prev = float(wt2.iloc[idx - 1])

        entry = float(last["close"])

        cross_up = wt1_prev < wt2_prev and wt1_cur > wt2_cur
        cross_down = wt1_prev > wt2_prev and wt1_cur < wt2_cur

        if cross_up and wt1_cur < -60:
            confidence = Confidence.HIGH if wt1_cur < -80 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"WaveTrend cross up in oversold zone. "
                    f"wt1={wt1_cur:.2f} crossed above wt2={wt2_cur:.2f} (prev wt1={wt1_prev:.2f}, wt2={wt2_prev:.2f}). "
                    f"wt1 < -60 (oversold)."
                ),
                invalidation=f"wt1 crosses below wt2 again",
                bull_case=f"wt1={wt1_cur:.2f} < -60, strong oversold reversal",
                bear_case=f"wt1={wt1_cur:.2f} may continue lower",
            )

        if cross_down and wt1_cur > 60:
            confidence = Confidence.HIGH if wt1_cur > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"WaveTrend cross down in overbought zone. "
                    f"wt1={wt1_cur:.2f} crossed below wt2={wt2_cur:.2f} (prev wt1={wt1_prev:.2f}, wt2={wt2_prev:.2f}). "
                    f"wt1 > 60 (overbought)."
                ),
                invalidation=f"wt1 crosses above wt2 again",
                bull_case=f"wt1={wt1_cur:.2f} may bounce higher",
                bear_case=f"wt1={wt1_cur:.2f} > 60, strong overbought reversal",
            )

        return self._hold(df, f"No WaveTrend crossover signal. wt1={wt1_cur:.2f}, wt2={wt2_cur:.2f}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
