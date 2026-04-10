"""
SRFlipStrategy: 지지/저항 전환(Flip) 전략.

- BUY: 이전 저항(swing high)을 현재 종가가 0.1% 이상 돌파 → 저항이 지지로 전환
- SELL: 이전 지지(swing low)를 현재 종가가 0.1% 이상 하향 이탈 → 지지가 저항으로 전환
- confidence: HIGH if |curr_close - level| / level < 0.005 (레벨 근처), else MEDIUM
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class SRFlipStrategy(BaseStrategy):
    name = "sr_flip"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < 15:
            return self._hold(df, "Insufficient data for SR flip detection (need 15+ rows)")

        idx = len(df) - 2
        curr_close = float(self._last(df)['close'])

        # 이전 swing high 탐색 (저항)
        prev_resistance: Optional[float] = None
        for i in range(idx - 5, max(0, idx - 20), -1):
            if i + 2 < len(df) and i >= 2:
                if (float(df['high'].iloc[i]) > float(df['high'].iloc[i - 1]) and
                        float(df['high'].iloc[i]) > float(df['high'].iloc[i - 2]) and
                        float(df['high'].iloc[i]) > float(df['high'].iloc[i + 1]) and
                        float(df['high'].iloc[i]) > float(df['high'].iloc[i + 2])):
                    prev_resistance = float(df['high'].iloc[i])
                    break

        # 이전 swing low 탐색 (지지)
        prev_support: Optional[float] = None
        for i in range(idx - 5, max(0, idx - 20), -1):
            if i + 2 < len(df) and i >= 2:
                if (float(df['low'].iloc[i]) < float(df['low'].iloc[i - 1]) and
                        float(df['low'].iloc[i]) < float(df['low'].iloc[i - 2]) and
                        float(df['low'].iloc[i]) < float(df['low'].iloc[i + 1]) and
                        float(df['low'].iloc[i]) < float(df['low'].iloc[i + 2])):
                    prev_support = float(df['low'].iloc[i])
                    break

        entry = curr_close

        # BUY: 이전 저항 돌파 (저항 → 지지 전환)
        if prev_resistance is not None and curr_close > prev_resistance * 1.001:
            level = prev_resistance
            proximity = abs(curr_close - level) / level if level > 0 else 1.0
            conf = Confidence.HIGH if proximity < 0.005 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"SR Flip BUY: resistance {level:.2f} flipped to support. "
                    f"curr_close={curr_close:.2f} > {level * 1.001:.2f} (resistance * 1.001). "
                    f"proximity={proximity:.4f}."
                ),
                invalidation=f"Close back below previous resistance ({level:.2f})",
                bull_case=f"Resistance {level:.2f} now acting as support. Price above flip zone.",
                bear_case=f"Failed flip: price may revert below {level:.2f}.",
            )

        # SELL: 이전 지지 이탈 (지지 → 저항 전환)
        if prev_support is not None and curr_close < prev_support * 0.999:
            level = prev_support
            proximity = abs(curr_close - level) / level if level > 0 else 1.0
            conf = Confidence.HIGH if proximity < 0.005 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"SR Flip SELL: support {level:.2f} flipped to resistance. "
                    f"curr_close={curr_close:.2f} < {level * 0.999:.2f} (support * 0.999). "
                    f"proximity={proximity:.4f}."
                ),
                invalidation=f"Close back above previous support ({level:.2f})",
                bull_case=f"Recovery above {level:.2f} would invalidate breakdown.",
                bear_case=f"Support {level:.2f} now acting as resistance. Price below flip zone.",
            )

        resistance_str = f"{prev_resistance:.2f}" if prev_resistance is not None else "N/A"
        support_str = f"{prev_support:.2f}" if prev_support is not None else "N/A"
        return self._hold(
            df,
            f"No SR flip. resistance={resistance_str}, support={support_str}, close={curr_close:.2f}"
        )

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is None or len(df) < 2:
            entry = 0.0
        else:
            entry = float(df['close'].iloc[-2])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
