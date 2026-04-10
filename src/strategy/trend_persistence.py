"""
TrendPersistenceStrategy: 자기상관 기반 추세 지속성 점수 (Hurst-like).
- autocorr > 0 : 추세 지속 (추세 추종 진입)
- autocorr < 0 : 평균 회귀
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_LOOKBACK = 20


class TrendPersistenceStrategy(BaseStrategy):
    name = "trend_persistence"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS + 1:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for trend_persistence",
                invalidation="",
            )

        close = df["close"]

        close_ma = close.rolling(_LOOKBACK, min_periods=1).mean()
        deviations = close - close_ma

        autocorr = (
            deviations.rolling(_LOOKBACK, min_periods=2)
            .apply(
                lambda x: pd.Series(x).autocorr(lag=1) if len(x) >= 2 else 0.0,
                raw=False,
            )
            .fillna(0.0)
        )

        idx = len(df) - 2
        last = self._last(df)

        entry_price = float(last["close"])
        autocorr_val = float(autocorr.iloc[idx])
        close_ma_val = float(close_ma.iloc[idx])
        close_prev = float(close.iloc[idx - 1]) if idx >= 1 else entry_price

        if any(pd.isna(v) for v in [autocorr_val, close_ma_val, close_prev]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry_price,
                reasoning="NaN detected in indicators",
                invalidation="",
            )

        confidence = Confidence.HIGH if autocorr_val > 0.5 else Confidence.MEDIUM

        bull_case = (
            f"autocorr={autocorr_val:.3f} > 0.2, "
            f"close={entry_price:.2f} > ma={close_ma_val:.2f}, "
            f"close rising"
        )
        bear_case = (
            f"autocorr={autocorr_val:.3f} > 0.2, "
            f"close={entry_price:.2f} < ma={close_ma_val:.2f}, "
            f"close falling"
        )

        if autocorr_val > 0.2 and entry_price > close_ma_val and entry_price > close_prev:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Trend persistence: autocorr={autocorr_val:.3f} > 0.2, "
                    f"close above MA and rising."
                ),
                invalidation=f"Close below MA ({close_ma_val:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if autocorr_val > 0.2 and entry_price < close_ma_val and entry_price < close_prev:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Trend persistence: autocorr={autocorr_val:.3f} > 0.2, "
                    f"close below MA and falling."
                ),
                invalidation=f"Close above MA ({close_ma_val:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=confidence,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"No signal: autocorr={autocorr_val:.3f}, "
                f"close={entry_price:.2f}, ma={close_ma_val:.2f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
