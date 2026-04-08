"""
Momentum/Trend-Following 전략:
- BUY:  roc > 0.03 AND close > ema50
- SELL: roc < -0.03 AND close < ema50
- HOLD: 그 외
- confidence: HIGH(|roc|>0.06), MEDIUM(|roc|>0.03)
- 최소 데이터: 55행 (shift(20) + ema50 warmup)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_ROC_PERIOD = 20
_BUY_THRESHOLD = 0.03
_SELL_THRESHOLD = -0.03
_HIGH_CONF_THRESHOLD = 0.06


class MomentumStrategy(BaseStrategy):
    name = "momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        ema50 = float(last["ema50"])

        # 20봉 ROC
        prev_close = float(df["close"].iloc[-2 - _ROC_PERIOD])
        roc = (close - prev_close) / prev_close

        above_ema = close > ema50
        below_ema = close < ema50

        context = f"close={close:.2f} ema50={ema50:.2f} roc={roc:.4f}"

        if roc > _BUY_THRESHOLD and above_ema:
            confidence = Confidence.HIGH if roc > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Momentum 상승: roc={roc:.4f}>{_BUY_THRESHOLD}, close({close:.2f})>ema50({ema50:.2f})",
                invalidation=f"Close below EMA50 ({ema50:.2f}) or ROC < {_BUY_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        if roc < _SELL_THRESHOLD and below_ema:
            confidence = Confidence.HIGH if roc < -_HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Momentum 하락: roc={roc:.4f}<{_SELL_THRESHOLD}, close({close:.2f})<ema50({ema50:.2f})",
                invalidation=f"Close above EMA50 ({ema50:.2f}) or ROC > {_SELL_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: roc={roc:.4f} above_ema={above_ema}", context, context)

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
