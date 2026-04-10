"""
IntradayMomentumStrategy: 봉 내 위치 + 거래량 흐름 기반 단기 모멘텀.
- BUY:  momentum_score > score_ma AND position > 0.7 AND volume > vol_ma
- SELL: momentum_score < score_ma AND position < 0.3 AND volume > vol_ma
- confidence: HIGH if position > 0.85 (BUY) or < 0.15 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class IntradayMomentumStrategy(BaseStrategy):
    name = "intraday_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        position = (close - low) / (high - low + 1e-10)
        pos_ma = position.rolling(10, min_periods=1).mean()
        vol_ma = volume.rolling(10, min_periods=1).mean()
        momentum_score = (position - pos_ma) * (volume / (vol_ma + 1e-10))
        score_ma = momentum_score.rolling(5, min_periods=1).mean()

        idx = len(df) - 2
        last = df.iloc[idx]

        pos_val = float(position.iloc[idx])
        vol_val = float(volume.iloc[idx])
        vol_ma_val = float(vol_ma.iloc[idx])
        ms_val = float(momentum_score.iloc[idx])
        sma_val = float(score_ma.iloc[idx])

        if any(np.isnan(v) for v in [pos_val, vol_val, vol_ma_val, ms_val, sma_val]):
            return self._hold(df, "NaN in indicators")

        close_val = float(last["close"])
        context = (
            f"position={pos_val:.3f} momentum_score={ms_val:.4f} "
            f"score_ma={sma_val:.4f} volume={vol_val:.0f} vol_ma={vol_ma_val:.0f}"
        )

        if ms_val > sma_val and pos_val > 0.7 and vol_val > vol_ma_val:
            confidence = Confidence.HIGH if pos_val > 0.85 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Intraday momentum 상승: position={pos_val:.3f}>0.7, ms={ms_val:.4f}>sma={sma_val:.4f}, vol>{vol_ma_val:.0f}",
                invalidation=f"position < 0.7 or momentum_score < score_ma",
                bull_case=context,
                bear_case=context,
            )

        if ms_val < sma_val and pos_val < 0.3 and vol_val > vol_ma_val:
            confidence = Confidence.HIGH if pos_val < 0.15 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Intraday momentum 하락: position={pos_val:.3f}<0.3, ms={ms_val:.4f}<sma={sma_val:.4f}, vol>{vol_ma_val:.0f}",
                invalidation=f"position > 0.3 or momentum_score > score_ma",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: position={pos_val:.3f} ms={ms_val:.4f}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
