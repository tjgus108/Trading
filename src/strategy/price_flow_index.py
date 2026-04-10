"""
PriceFlowIndexStrategy: 가격 흐름 지수 (Money Flow Index 간소화).
- pfi < 30 and rising → BUY (과매도 반등)
- pfi > 70 and falling → SELL (과매수 하락)
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class PriceFlowIndexStrategy(BaseStrategy):
    name = "price_flow_index"

    MIN_ROWS = 20

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        hold = Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=0.0,
            reasoning="No signal",
            invalidation="",
            bull_case="",
            bear_case="",
        )

        if df is None or len(df) < self.MIN_ROWS:
            hold.reasoning = "데이터 부족"
            return hold

        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]

        typical_price = (high + low + close) / 3
        raw_money_flow = typical_price * volume

        tp_up = (typical_price > typical_price.shift(1)).astype(float)
        tp_down = (typical_price < typical_price.shift(1)).astype(float)

        pos_flow = (raw_money_flow * tp_up).rolling(14, min_periods=1).sum()
        neg_flow = (raw_money_flow * tp_down).rolling(14, min_periods=1).sum()

        pfi = 100 * pos_flow / (pos_flow + neg_flow + 1e-10)
        pfi_ma = pfi.rolling(5, min_periods=1).mean()  # noqa: F841

        idx = len(df) - 2
        last = self._last(df)

        pfi_val = float(pfi.iloc[idx])
        pfi_prev = float(pfi.iloc[idx - 1]) if idx >= 1 else float("nan")

        if pd.isna(pfi_val) or pd.isna(pfi_prev):
            hold.reasoning = "NaN 값 감지"
            return hold

        entry = float(last["close"])
        hold.entry_price = entry

        bull_case = f"pfi={pfi_val:.2f}, pfi_prev={pfi_prev:.2f}"
        bear_case = f"pfi={pfi_val:.2f}, pfi_prev={pfi_prev:.2f}"

        # BUY: 과매도 반등
        if pfi_val < 30 and pfi_val > pfi_prev:
            confidence = Confidence.HIGH if pfi_val < 20 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"과매도 반등: pfi={pfi_val:.2f} < 30, "
                    f"pfi({pfi_val:.2f}) > pfi_prev({pfi_prev:.2f})"
                ),
                invalidation="pfi < pfi_prev 또는 pfi > 30",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 과매수 하락
        if pfi_val > 70 and pfi_val < pfi_prev:
            confidence = Confidence.HIGH if pfi_val > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"과매수 하락: pfi={pfi_val:.2f} > 70, "
                    f"pfi({pfi_val:.2f}) < pfi_prev({pfi_prev:.2f})"
                ),
                invalidation="pfi > pfi_prev 또는 pfi < 70",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        hold.reasoning = f"신호 없음: pfi={pfi_val:.2f}, pfi_prev={pfi_prev:.2f}"
        hold.bull_case = bull_case
        hold.bear_case = bear_case
        return hold
