"""
ChandelierExitStrategy: ATR 기반 추세 추종 전략.

- atr14 = (high - low).rolling(14, min_periods=1).mean()  (True Range 간소화)
- highest_high = high.rolling(22, min_periods=1).max()
- lowest_low = low.rolling(22, min_periods=1).min()
- chandelier_long = highest_high - atr14 * 3.0
- chandelier_short = lowest_low + atr14 * 3.0
- BUY: close > chandelier_long AND close > close.shift(1)
- SELL: close < chandelier_short AND close < close.shift(1)
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ChandelierExitStrategy(BaseStrategy):
    name = "chandelier_exit"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족: {len(df)} < 25",
                invalidation="",
            )

        high = df["high"]
        low = df["low"]
        close = df["close"]

        atr14 = (high - low).rolling(14, min_periods=1).mean()
        highest_high = high.rolling(22, min_periods=1).max()
        lowest_low = low.rolling(22, min_periods=1).min()

        chandelier_long = highest_high - atr14 * 3.0
        chandelier_short = lowest_low + atr14 * 3.0

        idx = len(df) - 2
        row = df.iloc[idx]

        cl_val = chandelier_long.iloc[idx]
        cs_val = chandelier_short.iloc[idx]
        atr_val = atr14.iloc[idx]

        c = float(close.iloc[idx])
        c_prev = float(close.iloc[idx - 1])

        # NaN 체크
        if pd.isna(cl_val) or pd.isna(cs_val) or pd.isna(atr_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=c,
                reasoning="지표 NaN",
                invalidation="",
            )

        cl_val = float(cl_val)
        cs_val = float(cs_val)
        atr_val = float(atr_val)

        buy_cond = c > cl_val and c > c_prev
        sell_cond = c < cs_val and c < c_prev

        if buy_cond:
            conf = Confidence.HIGH if c > cl_val * 1.01 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"Chandelier Exit BUY: close({c:.4f}) > chandelier_long({cl_val:.4f}), "
                    f"close > prev_close({c_prev:.4f}). ATR={atr_val:.4f}"
                ),
                invalidation=f"close < chandelier_long({cl_val:.4f}) 시 무효.",
                bull_case="22봉 최고점 기반 동적 지지선 위 추세 추종.",
                bear_case="전환 실패 가능성 존재.",
            )

        if sell_cond:
            conf = Confidence.HIGH if c < cs_val * 0.99 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"Chandelier Exit SELL: close({c:.4f}) < chandelier_short({cs_val:.4f}), "
                    f"close < prev_close({c_prev:.4f}). ATR={atr_val:.4f}"
                ),
                invalidation=f"close > chandelier_short({cs_val:.4f}) 시 무효.",
                bull_case="반전 가능성 존재.",
                bear_case="22봉 최저점 기반 동적 저항선 하향 이탈 확인.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=c,
            reasoning=(
                f"Chandelier Exit HOLD: CL={cl_val:.4f}, CS={cs_val:.4f}, "
                f"close={c:.4f}, ATR={atr_val:.4f}"
            ),
            invalidation="",
        )
