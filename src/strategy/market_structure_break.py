"""
MarketStructureBreakStrategy: HH/HL vs LH/LL 구조 분석.
- swing high/low 탐지 후 시장 구조 변화 감지
- BUY: HH+HL (완전 bullish 구조)
- SELL: LH+LL (완전 bearish 구조)
- Confidence: HIGH if swing 2개씩 확보 + 추세 명확, else MEDIUM
"""

import pandas as pd
from typing import Optional, List, Tuple

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class MarketStructureBreakStrategy(BaseStrategy):
    name = "market_structure_break"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for market_structure_break")

        idx = len(df) - 2
        last = df.iloc[idx]
        close = float(last["close"])

        swing_highs: List[Tuple[int, float]] = []
        swing_lows: List[Tuple[int, float]] = []

        for i in range(1, idx):
            if i + 1 < len(df):
                h = float(df['high'].iloc[i])
                if h > float(df['high'].iloc[i - 1]) and h > float(df['high'].iloc[i + 1]):
                    swing_highs.append((i, h))
                l = float(df['low'].iloc[i])
                if l < float(df['low'].iloc[i - 1]) and l < float(df['low'].iloc[i + 1]):
                    swing_lows.append((i, l))

        has_enough = len(swing_highs) >= 2 and len(swing_lows) >= 2

        if not has_enough:
            return self._hold(df, "Insufficient swing points for market_structure_break")

        sh_last = swing_highs[-1][1]
        sh_prev = swing_highs[-2][1]
        sl_last = swing_lows[-1][1]
        sl_prev = swing_lows[-2][1]

        bullish = sh_last > sh_prev and sl_last > sl_prev
        bearish = sh_last < sh_prev and sl_last < sl_prev

        if bullish:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"HH+HL structure: SH {sh_prev:.4f}→{sh_last:.4f}, "
                    f"SL {sl_prev:.4f}→{sl_last:.4f}"
                ),
                invalidation=f"Break below swing low {sl_last:.4f}",
                bull_case=f"Higher High ({sh_last:.4f}) and Higher Low ({sl_last:.4f}) confirmed",
                bear_case=f"Watch if SH fails: prev={sh_prev:.4f}",
            )

        if bearish:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"LH+LL structure: SH {sh_prev:.4f}→{sh_last:.4f}, "
                    f"SL {sl_prev:.4f}→{sl_last:.4f}"
                ),
                invalidation=f"Break above swing high {sh_last:.4f}",
                bull_case=f"Watch if SL holds: prev={sl_prev:.4f}",
                bear_case=f"Lower High ({sh_last:.4f}) and Lower Low ({sl_last:.4f}) confirmed",
            )

        return self._hold(df, "Mixed structure: no clear HH+HL or LH+LL")

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        close = 0.0
        if df is not None and len(df) >= 2:
            try:
                close = float(df.iloc[-2]["close"])
            except Exception:
                close = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
