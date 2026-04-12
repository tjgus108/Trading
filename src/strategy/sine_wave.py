"""
SineWaveStrategy: Ehlers Sine Wave Indicator 기반 전략.
사인파 피팅으로 사이클 위상을 감지하여 sine/lead 크로스오버 시 신호 생성.
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class SineWaveStrategy(BaseStrategy):
    name = "sine_wave"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data: need {_MIN_ROWS} rows, got {len(df)}")

        period = 20
        close_arr = df["close"].values.astype(float)
        n = len(close_arr)

        # HP filter (highpass)
        hp = np.zeros(n)
        alpha1 = (1 - np.sin(2 * np.pi / 48)) / np.cos(2 * np.pi / 48)
        for i in range(2, n):
            hp[i] = (1 + alpha1) / 2 * (close_arr[i] - close_arr[i - 1]) + alpha1 * hp[i - 1]

        sma20 = pd.Series(close_arr).rolling(period).mean().values
        std20 = pd.Series(close_arr).rolling(period).std().values
        zscore = np.zeros(n)
        mask = (~np.isnan(std20)) & (std20 > 0)
        zscore[mask] = (close_arr[mask] - sma20[mask]) / std20[mask]

        phase = np.arcsin(np.clip(zscore, -1, 1))
        lead_phase = phase + np.pi / 4

        sine_wave = pd.Series(np.sin(phase), index=df.index)
        lead_wave = pd.Series(np.sin(lead_phase), index=df.index)

        idx = len(df) - 2

        if pd.isna(sine_wave.iloc[idx]) or pd.isna(lead_wave.iloc[idx]) or \
           pd.isna(sine_wave.iloc[idx - 1]) or pd.isna(lead_wave.iloc[idx - 1]):
            return self._hold(df, "NaN in Sine Wave values")

        sine_cur = float(sine_wave.iloc[idx])
        lead_cur = float(lead_wave.iloc[idx])
        sine_prev = float(sine_wave.iloc[idx - 1])
        lead_prev = float(lead_wave.iloc[idx - 1])

        entry = float(df["close"].iloc[-2])

        cross_up = sine_prev < lead_prev and sine_cur > lead_cur
        cross_down = sine_prev > lead_prev and sine_cur < lead_cur

        confidence = Confidence.HIGH if abs(sine_cur) > 0.7 else Confidence.MEDIUM

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Sine Wave crossed above Lead Wave. "
                    f"sine={sine_cur:.4f} crossed above lead={lead_cur:.4f} "
                    f"(prev sine={sine_prev:.4f}, lead={lead_prev:.4f})."
                ),
                invalidation="sine_wave crosses below lead_wave again",
                bull_case=f"sine={sine_cur:.4f} rising above lead",
                bear_case=f"sine={sine_cur:.4f} may reverse downward",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Sine Wave crossed below Lead Wave. "
                    f"sine={sine_cur:.4f} crossed below lead={lead_cur:.4f} "
                    f"(prev sine={sine_prev:.4f}, lead={lead_prev:.4f})."
                ),
                invalidation="sine_wave crosses above lead_wave again",
                bull_case=f"sine={sine_cur:.4f} may reverse upward",
                bear_case=f"sine={sine_cur:.4f} falling below lead",
            )

        return self._hold(df, f"No Sine Wave crossover. sine={sine_cur:.4f}, lead={lead_cur:.4f}")

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
