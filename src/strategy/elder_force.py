"""
ElderForceIndexStrategy: Elder's Force Index 기반 매매 전략.

로직:
  - Force Index = close.diff() * volume
  - FI_2  = Force Index.ewm(span=2).mean()   (단기, 진입 타이밍)
  - FI_13 = Force Index.ewm(span=13).mean()  (장기, 추세)
  - BUY:  FI_13 > 0 (상승 추세) AND FI_2 < 0 (단기 조정 → 매수 기회)
  - SELL: FI_13 < 0 (하락 추세) AND FI_2 > 0 (단기 반등 → 매도 기회)
  - confidence HIGH: |FI_13| > FI_13.rolling(20).std() * 1.5
  - 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ElderForceIndexStrategy(BaseStrategy):
    name = "elder_force"

    MIN_ROWS = 20

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 20행 필요",
                invalidation="",
            )

        last = self._last(df)
        idx = len(df) - 2

        close = df["close"]
        volume = df["volume"]

        force_index = close.diff() * volume
        fi_2 = force_index.ewm(span=2, adjust=False).mean()
        fi_13 = force_index.ewm(span=13, adjust=False).mean()

        fi2_val = float(fi_2.iloc[idx])
        fi13_val = float(fi_13.iloc[idx])

        # confidence 계산: |FI_13| > rolling std * 1.5
        lookback = min(20, idx)
        fi13_std = float(fi_13.iloc[idx - lookback: idx].std())
        if fi13_std > 0 and abs(fi13_val) > fi13_std * 1.5:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        entry = float(last["close"])

        bull_case = (
            f"FI_13={fi13_val:.2f} (>0 상승 추세), FI_2={fi2_val:.2f} (<0 단기 조정)"
        )
        bear_case = (
            f"FI_13={fi13_val:.2f} (<0 하락 추세), FI_2={fi2_val:.2f} (>0 단기 반등)"
        )

        if fi13_val > 0 and fi2_val < 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Elder Force BUY: FI_13={fi13_val:.2f}>0 (상승 추세) + "
                    f"FI_2={fi2_val:.2f}<0 (단기 조정 진입 기회)"
                ),
                invalidation=f"FI_13 < 0 (추세 전환)",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if fi13_val < 0 and fi2_val > 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Elder Force SELL: FI_13={fi13_val:.2f}<0 (하락 추세) + "
                    f"FI_2={fi2_val:.2f}>0 (단기 반등 매도 기회)"
                ),
                invalidation=f"FI_13 > 0 (추세 전환)",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Elder Force HOLD: FI_13={fi13_val:.2f} FI_2={fi2_val:.2f} — 조건 미충족"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
