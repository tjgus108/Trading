"""
HigherHighMomentumStrategy:
- Higher High / Lower Low 구조 + 3봉 모멘텀(ROC3)
- BUY:  hh5 > hh5_prev AND ll5 > ll5_prev AND roc3 > 0
- SELL: ll5 < ll5_prev AND hh5 < hh5_prev AND roc3 < 0
- confidence: HIGH(거래량 > 10봉 평균 * 1.3), MEDIUM 그 외
- 최소 데이터: 25행
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class HigherHighMomentumStrategy(BaseStrategy):
    name = "higher_high_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # 마지막 완성 캔들 인덱스

        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]

        hh5 = high.rolling(5, min_periods=1).max()
        ll5 = low.rolling(5, min_periods=1).min()
        hh5_prev = hh5.shift(5)
        ll5_prev = ll5.shift(5)

        roc3 = close.pct_change(3)
        vol_ma10 = volume.rolling(10, min_periods=1).mean()

        # 완성 캔들 값
        hh5_val = hh5.iloc[idx]
        ll5_val = ll5.iloc[idx]
        hh5_prev_val = hh5_prev.iloc[idx]
        ll5_prev_val = ll5_prev.iloc[idx]
        roc3_val = roc3.iloc[idx]
        vol_val = volume.iloc[idx]
        vol_ma_val = vol_ma10.iloc[idx]
        close_val = float(close.iloc[idx])

        # NaN 체크
        if any(
            _isnan(v) for v in [hh5_val, ll5_val, hh5_prev_val, ll5_prev_val, roc3_val, vol_val, vol_ma_val]
        ):
            return self._hold(df, "NaN in indicators")

        higher_high = float(hh5_val) > float(hh5_prev_val)
        higher_low = float(ll5_val) > float(ll5_prev_val)
        lower_low = float(ll5_val) < float(ll5_prev_val)
        lower_high = float(hh5_val) < float(hh5_prev_val)
        roc3_pos = float(roc3_val) > 0
        roc3_neg = float(roc3_val) < 0

        high_conf = float(vol_val) > float(vol_ma_val) * 1.3
        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        context = (
            f"hh5={hh5_val:.4f} hh5_prev={hh5_prev_val:.4f} "
            f"ll5={ll5_val:.4f} ll5_prev={ll5_prev_val:.4f} "
            f"roc3={roc3_val:.4f} vol={vol_val:.1f} vol_ma={vol_ma_val:.1f}"
        )

        if higher_high and higher_low and roc3_pos:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Higher High/Low 구조 + 모멘텀 상승: "
                    f"hh5({hh5_val:.4f})>hh5_prev({hh5_prev_val:.4f}), "
                    f"ll5({ll5_val:.4f})>ll5_prev({ll5_prev_val:.4f}), "
                    f"roc3={roc3_val:.4f}>0"
                ),
                invalidation=f"hh5 drops below {hh5_prev_val:.4f} or roc3 turns negative",
                bull_case=context,
                bear_case=context,
            )

        if lower_low and lower_high and roc3_neg:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Lower Low/High 구조 + 모멘텀 하락: "
                    f"ll5({ll5_val:.4f})<ll5_prev({ll5_prev_val:.4f}), "
                    f"hh5({hh5_val:.4f})<hh5_prev({hh5_prev_val:.4f}), "
                    f"roc3={roc3_val:.4f}<0"
                ),
                invalidation=f"ll5 rises above {ll5_prev_val:.4f} or roc3 turns positive",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No structure signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2
        close_val = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )


def _isnan(v) -> bool:
    try:
        return math.isnan(float(v))
    except (TypeError, ValueError):
        return True
