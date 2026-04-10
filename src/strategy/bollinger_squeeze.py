"""
BollingerSqueezeStrategy:
- BB 폭 수축(squeeze) 후 모멘텀 방향 돌파 시 신호 생성
- BUY: squeeze AND momentum > 0 AND close > bb_mid
- SELL: squeeze AND momentum < 0 AND close < bb_mid
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class BollingerSqueezeStrategy(BaseStrategy):
    name = "bollinger_squeeze"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        idx = len(df) - 2

        bb_mid = close.rolling(20, min_periods=1).mean()
        bb_std = close.rolling(20, min_periods=1).std()
        bb_upper = bb_mid + bb_std * 2
        bb_lower = bb_mid - bb_std * 2
        bb_width = (bb_upper - bb_lower) / (bb_mid + 1e-10)
        width_ma = bb_width.rolling(20, min_periods=1).mean()

        squeeze = bb_width < width_ma * 0.75
        momentum = close - close.shift(5)

        last_squeeze = squeeze.iloc[idx]
        last_momentum = momentum.iloc[idx]
        last_close = close.iloc[idx]
        last_mid = bb_mid.iloc[idx]
        last_width = bb_width.iloc[idx]
        last_width_ma = width_ma.iloc[idx]

        import math
        if any(
            v is None or (isinstance(v, float) and math.isnan(v))
            for v in [last_momentum, last_close, last_mid, last_width, last_width_ma]
        ):
            return self._hold(df, "NaN in indicators")

        if last_squeeze and last_momentum > 0 and last_close > last_mid:
            conf = Confidence.HIGH if last_width < last_width_ma * 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=(
                    f"BB squeeze active, upward momentum ({last_momentum:.4f}), "
                    f"close ({last_close:.4f}) > mid ({last_mid:.4f})"
                ),
                invalidation=f"Close below BB mid ({last_mid:.4f})",
                bull_case=f"BB width={last_width:.6f} width_ma={last_width_ma:.6f}",
                bear_case="",
            )

        if last_squeeze and last_momentum < 0 and last_close < last_mid:
            conf = Confidence.HIGH if last_width < last_width_ma * 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=(
                    f"BB squeeze active, downward momentum ({last_momentum:.4f}), "
                    f"close ({last_close:.4f}) < mid ({last_mid:.4f})"
                ),
                invalidation=f"Close above BB mid ({last_mid:.4f})",
                bull_case="",
                bear_case=f"BB width={last_width:.6f} width_ma={last_width_ma:.6f}",
            )

        return self._hold(
            df,
            f"No squeeze signal (squeeze={last_squeeze}, momentum={last_momentum:.4f})",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
