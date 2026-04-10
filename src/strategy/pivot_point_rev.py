"""
PivotPointRevStrategy: 피벗 포인트와 지지/저항선에서의 반등 전략.

로직:
  - 이전봉(idx-1) 데이터로 피벗 계산:
      pivot = (high + low + close) / 3
      r1 = 2 * pivot - low
      s1 = 2 * pivot - high
      r2 = pivot + (high - low)
      s2 = pivot - (high - low)
  - BUY:  curr_close < s1 AND curr_close > s1 * 0.998  (S1 근처 반등)
          OR curr_close < s2 AND curr_close > s2 * 0.998  (S2 근처)
  - SELL: curr_close > r1 AND curr_close < r1 * 1.002  (R1 근처 반락)
          OR curr_close > r2 AND curr_close < r2 * 1.002
  - confidence: HIGH if S2/R2 레벨 근처 else MEDIUM
  - 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.rolling(period).mean()


class PivotPointRevStrategy(BaseStrategy):
    name = "pivot_point_rev"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for PivotPointRev (min 20 rows)")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]

        prev_high = float(prev["high"])
        prev_low = float(prev["low"])
        prev_close = float(prev["close"])
        curr_close = float(curr["close"])

        pivot = (prev_high + prev_low + prev_close) / 3
        r1 = 2 * pivot - prev_low
        s1 = 2 * pivot - prev_high
        r2 = pivot + (prev_high - prev_low)
        s2 = pivot - (prev_high - prev_low)

        atr_series = _atr(df)
        atr_val = float(atr_series.iloc[idx])
        if atr_val != atr_val:  # NaN check
            atr_val = 0.0

        context = (
            f"close={curr_close:.4f} pivot={pivot:.4f} "
            f"S1={s1:.4f} S2={s2:.4f} R1={r1:.4f} R2={r2:.4f} ATR={atr_val:.4f}"
        )

        # BUY: near S2 (higher priority / HIGH confidence)
        if curr_close < s2 and curr_close > s2 * 0.998:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"PivotRev: S2 지지 근처 반등 신호. {context}",
                invalidation=f"S2({s2:.4f}) 하향 이탈 시",
                bull_case=f"S2={s2:.4f} 지지 반등 → S1={s1:.4f} 목표",
                bear_case="S2 이탈 시 추가 하락",
            )

        # BUY: near S1 (MEDIUM confidence)
        if curr_close < s1 and curr_close > s1 * 0.998:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"PivotRev: S1 지지 근처 반등 신호. {context}",
                invalidation=f"S1({s1:.4f}) 하향 이탈 시",
                bull_case=f"S1={s1:.4f} 지지 반등 → pivot={pivot:.4f} 목표",
                bear_case=f"S2={s2:.4f} 테스트 가능성",
            )

        # SELL: near R2 (higher priority / HIGH confidence)
        if curr_close > r2 and curr_close < r2 * 1.002:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"PivotRev: R2 저항 근처 반락 신호. {context}",
                invalidation=f"R2({r2:.4f}) 상향 돌파 시",
                bull_case="R2 돌파 시 추가 상승",
                bear_case=f"R2={r2:.4f} 저항 반락 → R1={r1:.4f} 목표",
            )

        # SELL: near R1 (MEDIUM confidence)
        if curr_close > r1 and curr_close < r1 * 1.002:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"PivotRev: R1 저항 근처 반락 신호. {context}",
                invalidation=f"R1({r1:.4f}) 상향 돌파 시",
                bull_case=f"R2={r2:.4f} 테스트 가능성",
                bear_case=f"R1={r1:.4f} 저항 반락 → pivot={pivot:.4f} 목표",
            )

        return self._hold(df, f"PivotRev: 레벨 근처 없음. {context}")

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        price = 0.0
        if df is not None and len(df) >= 2:
            try:
                price = float(self._last(df)["close"])
            except Exception:
                price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
