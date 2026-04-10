"""
AdaptiveVolatilityStrategy: 변동성 레짐에 따라 신호 임계값을 동적으로 조정.
- 저변동성(low_vol): 작은 신호에도 진입 가능 → HIGH confidence
- 고변동성(high_vol): 큰 신호에만 진입 → MEDIUM confidence
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class AdaptiveVolatilityStrategy(BaseStrategy):
    name = "adaptive_volatility"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS + 1:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for adaptive_volatility",
                invalidation="",
            )

        high = df["high"]
        low = df["low"]
        close = df["close"]

        atr = (high - low).rolling(14, min_periods=1).mean()
        atr_pct = atr / (close + 1e-10)
        vol_regime = atr_pct.rolling(20, min_periods=1).mean()

        low_vol = atr_pct < vol_regime * 0.8
        # high_vol is computed but used only for confidence
        # high_vol = atr_pct > vol_regime * 1.2

        returns = close.pct_change().fillna(0)
        momentum = returns.rolling(10, min_periods=1).sum()

        threshold = vol_regime * 2.0
        ema20 = close.ewm(span=20, adjust=False).mean()

        idx = len(df) - 2
        last = self._last(df)

        entry_price = float(last["close"])

        mom_val = float(momentum.iloc[idx])
        thresh_val = float(threshold.iloc[idx])
        ema20_val = float(ema20.iloc[idx])
        low_vol_val = bool(low_vol.iloc[idx])
        atr_pct_val = float(atr_pct.iloc[idx])
        vol_regime_val = float(vol_regime.iloc[idx])

        if any(
            pd.isna(v) for v in [mom_val, thresh_val, ema20_val, atr_pct_val, vol_regime_val]
        ):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry_price,
                reasoning="NaN detected in indicators",
                invalidation="",
            )

        confidence = Confidence.HIGH if low_vol_val else Confidence.MEDIUM

        bull_case = (
            f"momentum={mom_val:.4f} > threshold={thresh_val:.4f}, "
            f"close={entry_price:.2f} > ema20={ema20_val:.2f}, "
            f"atr_pct={atr_pct_val:.4f}, vol_regime={vol_regime_val:.4f}"
        )
        bear_case = (
            f"momentum={mom_val:.4f} < -threshold={thresh_val:.4f}, "
            f"close={entry_price:.2f} < ema20={ema20_val:.2f}, "
            f"atr_pct={atr_pct_val:.4f}, vol_regime={vol_regime_val:.4f}"
        )

        if mom_val > thresh_val and entry_price > ema20_val:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"momentum={mom_val:.4f} > threshold={thresh_val:.4f} "
                    f"and close above EMA20. low_vol={low_vol_val}"
                ),
                invalidation=f"Close below EMA20 ({ema20_val:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if mom_val < -thresh_val and entry_price < ema20_val:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"momentum={mom_val:.4f} < -threshold={thresh_val:.4f} "
                    f"and close below EMA20. low_vol={low_vol_val}"
                ),
                invalidation=f"Close above EMA20 ({ema20_val:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=confidence,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"No signal: momentum={mom_val:.4f}, threshold={thresh_val:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
