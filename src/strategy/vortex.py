"""
Vortex Indicator 기반 추세 전략.
- VI+ = VM+(14기간 합) / TR(14기간 합)
- VI- = VM-(14기간 합) / TR(14기간 합)
- BUY:  VI+ 크로스오버 VI- AND VI+ > 1.0
- SELL: VI- 크로스오버 VI+ AND VI- > 1.0
- confidence: HIGH if |VI+ - VI-| > 0.2, MEDIUM otherwise
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_PERIOD = 14


class VortexStrategy(BaseStrategy):
    name = "vortex"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for Vortex (need 20 rows)")

        idx = len(df) - 2

        high = df["high"]
        low = df["low"]
        close = df["close"]

        vm_plus = (high - low.shift(1)).abs()
        vm_minus = (low - high.shift(1)).abs()
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs()
        ], axis=1).max(axis=1)

        vi_plus = vm_plus.rolling(_PERIOD).sum() / tr.rolling(_PERIOD).sum()
        vi_minus = vm_minus.rolling(_PERIOD).sum() / tr.rolling(_PERIOD).sum()

        vp_now = float(vi_plus.iloc[idx])
        vp_prev = float(vi_plus.iloc[idx - 1])
        vm_now = float(vi_minus.iloc[idx])
        vm_prev = float(vi_minus.iloc[idx - 1])

        if any(v != v for v in (vp_now, vp_prev, vm_now, vm_prev)):  # NaN check
            return self._hold(df, "Vortex: NaN in indicator values")

        cross_up = vp_prev <= vm_prev and vp_now > vm_now
        cross_down = vm_prev <= vp_prev and vm_now > vp_now

        last = self._last(df)
        close_price = float(last["close"])
        separation = abs(vp_now - vm_now)
        confidence = Confidence.HIGH if separation > 0.2 else Confidence.MEDIUM
        context = f"VI+={vp_now:.4f} VI-={vm_now:.4f} sep={separation:.4f}"

        if cross_up and vp_now > 1.0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"Vortex BUY: VI+ 크로스오버 VI- (VI+={vp_now:.4f} > VI-={vm_now:.4f}, VI+>1.0)"
                ),
                invalidation="VI+ < VI- 또는 VI+ < 1.0",
                bull_case=context,
                bear_case=context,
            )

        if cross_down and vm_now > 1.0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"Vortex SELL: VI- 크로스오버 VI+ (VI-={vm_now:.4f} > VI+={vp_now:.4f}, VI->1.0)"
                ),
                invalidation="VI- < VI+ 또는 VI- < 1.0",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"Vortex HOLD: no crossover signal ({context})", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        try:
            close_price = float(self._last(df)["close"])
        except Exception:
            close_price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
