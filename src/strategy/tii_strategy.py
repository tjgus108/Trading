"""
Trend Intensity Index (TII) Strategy.
TII 측정: 30봉 중 SMA30 위에 있는 봉의 비율 (0~100).
BUY:  TII > 80 AND close > SMA30  → 강한 상승추세
SELL: TII < 20 AND close < SMA30  → 강한 하락추세
HOLD: 그 외
Confidence HIGH: TII > 90 or TII < 10
최소 행: 35
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 35


class TrendIntensityIndexStrategy(BaseStrategy):
    name = "tii_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close: float = float(df["close"].iloc[-1])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"데이터 부족: {len(df)}행 (최소 {MIN_ROWS}행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]
        sma30 = close.rolling(30).mean()

        # count_above: 각 봉에서 직전 30봉 중 close > sma30인 개수
        above = (close > sma30).astype(float)
        count_above = above.rolling(30).sum()
        tii = count_above / 30 * 100

        last = self._last(df)
        last_idx = df.index[-2]

        tii_val: float = float(tii.loc[last_idx])
        sma_val: float = float(sma30.loc[last_idx])
        entry: float = float(last["close"])

        if pd.isna(tii_val) or pd.isna(sma_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="TII 계산 불가 (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        bull_case = f"TII={tii_val:.1f} > 80, close={entry:.4f} > SMA30={sma_val:.4f}"
        bear_case = f"TII={tii_val:.1f} < 20, close={entry:.4f} < SMA30={sma_val:.4f}"

        if tii_val > 80 and entry > sma_val:
            confidence = Confidence.HIGH if tii_val > 90 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Strong uptrend: TII={tii_val:.1f} > 80, close above SMA30={sma_val:.4f}",
                invalidation=f"Close below SMA30 ({sma_val:.4f}) or TII < 80",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if tii_val < 20 and entry < sma_val:
            confidence = Confidence.HIGH if tii_val < 10 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Strong downtrend: TII={tii_val:.1f} < 20, close below SMA30={sma_val:.4f}",
                invalidation=f"Close above SMA30 ({sma_val:.4f}) or TII > 20",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Unclear trend: TII={tii_val:.1f} (20 <= TII <= 80)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
