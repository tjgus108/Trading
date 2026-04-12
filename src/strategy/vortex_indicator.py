"""
Vortex Indicator 전략 (vortex_indicator):
- VI+ = VM+(14기간 합) / TR(14기간 합)
- VI- = VM-(14기간 합) / TR(14기간 합)
- BUY:  vi_plus 크로스오버 vi_minus (이전 vi_plus < vi_minus, 현재 vi_plus > vi_minus)
- SELL: vi_plus 크로스 하방 vi_minus
- confidence: HIGH if |vi_plus - vi_minus| > 0.1 else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_PERIOD = 14


class VortexIndicatorStrategy(BaseStrategy):
    name = "vortex_indicator"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for VortexIndicator (need 20 rows)")

        idx = len(df) - 2

        high = df["high"]
        low = df["low"]
        close = df["close"]

        tr = pd.concat([
            (high - low),
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs()
        ], axis=1).max(axis=1)

        vm_plus = (high - low.shift(1)).abs()
        vm_minus = (low - high.shift(1)).abs()

        tr14 = tr.rolling(_PERIOD).sum()
        vm_plus14 = vm_plus.rolling(_PERIOD).sum()
        vm_minus14 = vm_minus.rolling(_PERIOD).sum()

        vi_plus = vm_plus14 / tr14
        vi_minus = vm_minus14 / tr14

        vp_now = float(vi_plus.iloc[idx])
        vp_prev = float(vi_plus.iloc[idx - 1])
        vm_now = float(vi_minus.iloc[idx])
        vm_prev = float(vi_minus.iloc[idx - 1])

        # NaN check
        if any(v != v for v in (vp_now, vp_prev, vm_now, vm_prev)):
            return self._hold(df, "VortexIndicator: NaN in indicator values")

        last = self._last(df)
        close_price = float(last["close"])
        separation = abs(vp_now - vm_now)
        confidence = Confidence.HIGH if separation > 0.1 else Confidence.MEDIUM

        cross_up = vp_prev < vm_prev and vp_now > vm_now
        cross_down = vp_prev > vm_prev and vp_now < vm_now

        context = f"VI+={vp_now:.4f} VI-={vm_now:.4f} sep={separation:.4f}"

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"VortexIndicator BUY: VI+ crossed above VI- "
                    f"(prev VI+={vp_prev:.4f}<VI-={vm_prev:.4f}, "
                    f"now VI+={vp_now:.4f}>VI-={vm_now:.4f})"
                ),
                invalidation="VI+ < VI-로 재역전 시",
                bull_case=context,
                bear_case=context,
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"VortexIndicator SELL: VI+ crossed below VI- "
                    f"(prev VI+={vp_prev:.4f}>VI-={vm_prev:.4f}, "
                    f"now VI+={vp_now:.4f}<VI-={vm_now:.4f})"
                ),
                invalidation="VI+ > VI-로 재역전 시",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"VortexIndicator HOLD: no crossover ({context})", context, context)

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
