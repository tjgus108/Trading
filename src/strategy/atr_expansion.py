"""
ATRExpansionStrategy: ATR 확장을 이용한 추세 가속 감지.

- ATR14 = EWM span=14 (TR의 지수이동평균)
- ATR_ratio = ATR14 / ATR14.rolling(20).mean()
- ATR_ratio > 1.5 → 변동성 확장 (추세 가속)
- BUY:  atr_expansion AND close > EMA20 AND close > close.shift(3)
- SELL: atr_expansion AND close < EMA20 AND close < close.shift(3)
- confidence: ATR_ratio > 2.0 → HIGH, else MEDIUM
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_ATR_EXPAND_THRESHOLD = 1.5
_ATR_HIGH_THRESHOLD = 2.0


class ATRExpansionStrategy(BaseStrategy):
    name = "atr_expansion"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        # True Range
        high = df["high"]
        low = df["low"]
        prev_close = df["close"].shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)

        # ATR14 via EWM
        atr14 = tr.ewm(span=14, adjust=False).mean()
        atr_ratio = atr14 / atr14.rolling(20).mean()

        close = float(df["close"].iloc[idx])
        ema20 = float(df["close"].ewm(span=20, adjust=False).mean().iloc[idx])
        atr_ratio_val = float(atr_ratio.iloc[idx])

        # close 3봉 전
        close_3ago = float(df["close"].iloc[idx - 3]) if idx >= 3 else close

        atr_expansion = atr_ratio_val > _ATR_EXPAND_THRESHOLD
        conf = Confidence.HIGH if atr_ratio_val > _ATR_HIGH_THRESHOLD else Confidence.MEDIUM

        context = (
            f"close={close:.2f}, ema20={ema20:.2f}, "
            f"atr_ratio={atr_ratio_val:.4f}, close_3ago={close_3ago:.2f}"
        )

        if not atr_expansion:
            return self._hold(
                df,
                f"No ATR expansion: atr_ratio={atr_ratio_val:.4f}<{_ATR_EXPAND_THRESHOLD}",
                context, context,
            )

        if close > ema20 and close > close_3ago:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ATR Expansion BUY: atr_ratio={atr_ratio_val:.4f}>{_ATR_EXPAND_THRESHOLD}, "
                    f"close({close:.2f})>ema20({ema20:.2f}), close>close_3ago({close_3ago:.2f})"
                ),
                invalidation=f"close<ema20({ema20:.2f}) or atr_ratio<{_ATR_EXPAND_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        if close < ema20 and close < close_3ago:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ATR Expansion SELL: atr_ratio={atr_ratio_val:.4f}>{_ATR_EXPAND_THRESHOLD}, "
                    f"close({close:.2f})<ema20({ema20:.2f}), close<close_3ago({close_3ago:.2f})"
                ),
                invalidation=f"close>ema20({ema20:.2f}) or atr_ratio<{_ATR_EXPAND_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"ATR expansion but no directional filter: close={close:.2f} ema20={ema20:.2f} close_3ago={close_3ago:.2f}",
            context, context,
        )

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
