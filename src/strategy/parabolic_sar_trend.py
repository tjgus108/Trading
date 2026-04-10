"""
ParabolicSARTrend 전략:
- Parabolic SAR 계산으로 추세 전환 감지
- AF 초기=0.02, 스텝=0.02, max=0.20
- BUY: 하락→상승 전환, SELL: 상승→하락 전환
- confidence: HIGH if |close - sar| / close > 0.02 else MEDIUM
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20


class ParabolicSARTrendStrategy(BaseStrategy):
    name = "parabolic_sar_trend"

    def _compute_sar(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        n = len(df)

        sar = [0.0] * n
        ep = float(high.iloc[0])
        af = 0.02
        bullish = True
        sar[0] = float(low.iloc[0])

        for i in range(1, n):
            if bullish:
                sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
                if float(low.iloc[i]) < sar[i]:
                    bullish = False
                    sar[i] = ep
                    ep = float(low.iloc[i])
                    af = 0.02
                else:
                    if float(high.iloc[i]) > ep:
                        ep = float(high.iloc[i])
                        af = min(af + 0.02, 0.20)
            else:
                sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
                if float(high.iloc[i]) > sar[i]:
                    bullish = True
                    sar[i] = ep
                    ep = float(high.iloc[i])
                    af = 0.02
                else:
                    if float(low.iloc[i]) < ep:
                        ep = float(low.iloc[i])
                        af = min(af + 0.02, 0.20)

        return pd.Series(sar, index=df.index)

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
        )

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < MIN_ROWS:
            rows = len(df) if df is not None else 0
            return self._hold(df if df is not None else pd.DataFrame(), f"Insufficient data: {rows} < {MIN_ROWS}")

        sar_series = self._compute_sar(df)

        idx = len(df) - 2
        close = df["close"]

        prev_bullish = float(close.iloc[idx - 1]) > float(sar_series.iloc[idx - 1])
        curr_bullish = float(close.iloc[idx]) > float(sar_series.iloc[idx])

        entry = float(close.iloc[idx])
        sar_val = float(sar_series.iloc[idx])

        dist_ratio = abs(entry - sar_val) / entry if entry != 0 else 0.0
        confidence = Confidence.HIGH if dist_ratio > 0.02 else Confidence.MEDIUM

        if not prev_bullish and curr_bullish:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SAR 하락→상승 전환 (SAR={sar_val:.4f}, close={entry:.4f})",
                invalidation=f"close가 SAR {sar_val:.4f} 아래로 하락 시 무효",
                bull_case="Parabolic SAR 추세 전환 (상승)",
                bear_case="추세 전환 실패 가능성",
            )

        if prev_bullish and not curr_bullish:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SAR 상승→하락 전환 (SAR={sar_val:.4f}, close={entry:.4f})",
                invalidation=f"close가 SAR {sar_val:.4f} 위로 상승 시 무효",
                bull_case="추세 전환 실패 가능성",
                bear_case="Parabolic SAR 추세 전환 (하락)",
            )

        direction = "상승" if curr_bullish else "하락"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"SAR {direction} 추세 지속 (전환 없음, SAR={sar_val:.4f})",
            invalidation="",
        )
