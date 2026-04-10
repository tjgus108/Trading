"""
RangeTradingStrategy: 횡보 구간 범위 내 반전 매매.
- range_high = close.rolling(20, min_periods=1).max()
- range_low  = close.rolling(20, min_periods=1).min()
- mid        = (range_high + range_low) / 2
- range_width = range_high - range_low
- rsi 직접 계산 (period=14)
- BUY:  close < range_low + range_width * 0.2 AND rsi < 40
- SELL: close > range_high - range_width * 0.2 AND rsi > 60
- confidence: HIGH if rsi < 30 (BUY) or rsi > 70 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ROLL = 20
_RSI_PERIOD = 14
_BUY_RSI = 40
_SELL_RSI = 60
_HIGH_BUY_RSI = 30
_HIGH_SELL_RSI = 70
_ZONE_FRAC = 0.2


class RangeTradingStrategy(BaseStrategy):
    name = "range_trading"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        # 진행 중 캔들 제외
        idx = len(df) - 2
        close_s = df["close"].iloc[: idx + 1]

        range_high = close_s.rolling(_ROLL, min_periods=1).max()
        range_low = close_s.rolling(_ROLL, min_periods=1).min()
        range_width = range_high - range_low

        rh = float(range_high.iloc[-1])
        rl = float(range_low.iloc[-1])
        rw = float(range_width.iloc[-1])

        # RSI 계산
        delta = close_s.diff()
        gain = delta.clip(lower=0).rolling(_RSI_PERIOD, min_periods=1).mean()
        loss = (-delta.clip(upper=0)).rolling(_RSI_PERIOD, min_periods=1).mean()
        rsi_val = float((100 - 100 / (1 + gain / (loss + 1e-10))).iloc[-1])

        close = float(close_s.iloc[-1])

        # NaN guard
        if pd.isna(rh) or pd.isna(rl) or pd.isna(rsi_val):
            return self._hold(df, "NaN in indicators")

        buy_zone = rl + rw * _ZONE_FRAC
        sell_zone = rh - rw * _ZONE_FRAC
        context = (
            f"close={close:.4f} range_low={rl:.4f} range_high={rh:.4f} "
            f"buy_zone={buy_zone:.4f} sell_zone={sell_zone:.4f} rsi={rsi_val:.1f}"
        )

        if close < buy_zone and rsi_val < _BUY_RSI:
            confidence = Confidence.HIGH if rsi_val < _HIGH_BUY_RSI else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"횡보 하단 반전: close({close:.4f})<buy_zone({buy_zone:.4f}), "
                    f"rsi={rsi_val:.1f}<{_BUY_RSI}"
                ),
                invalidation=f"Close below range_low ({rl:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if close > sell_zone and rsi_val > _SELL_RSI:
            confidence = Confidence.HIGH if rsi_val > _HIGH_SELL_RSI else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"횡보 상단 반전: close({close:.4f})>sell_zone({sell_zone:.4f}), "
                    f"rsi={rsi_val:.1f}>{_SELL_RSI}"
                ),
                invalidation=f"Close above range_high ({rh:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
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
