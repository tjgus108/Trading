"""
Chaikin Oscillator 전략.
- MFM = ((close-low)-(high-close)) / (high-low)  (0으로 나누면 0)
- MFV = MFM * volume
- ADL = MFV.cumsum()
- Chaikin Osc = ADL.ewm(span=3).mean() - ADL.ewm(span=10).mean()
- BUY: Osc crosses above 0 (prev < 0, now >= 0) AND close > EMA20
- SELL: Osc crosses below 0 (prev > 0, now <= 0) AND close < EMA20
- confidence: |Osc| > Osc.rolling(20).std() → HIGH
- 최소 행: 25
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25


class ChaikinOscillatorStrategy(BaseStrategy):
    name = "chaikin_osc"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
            )

        last = self._last(df)
        entry = float(last["close"])

        # Chaikin Oscillator 계산
        hl = df["high"] - df["low"]
        mfm = np.where(
            hl == 0,
            0.0,
            ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl,
        )
        mfv = pd.Series(mfm, index=df.index) * df["volume"]
        adl = mfv.cumsum()
        osc = adl.ewm(span=3, adjust=False).mean() - adl.ewm(span=10, adjust=False).mean()

        idx = len(df) - 2  # _last = iloc[-2]
        osc_now = float(osc.iloc[idx])
        osc_prev = float(osc.iloc[idx - 1])

        # EMA20: 컬럼 있으면 사용, 없으면 직접 계산
        if "ema20" in df.columns:
            ema20 = float(df["ema20"].iloc[idx])
        else:
            ema20 = float(df["close"].ewm(span=20, adjust=False).mean().iloc[idx])

        # 크로스 감지
        cross_up = osc_prev < 0 and osc_now >= 0
        cross_down = osc_prev > 0 and osc_now <= 0

        # confidence: |Osc| vs rolling std(20)
        osc_std = float(osc.rolling(20).std().iloc[idx])
        high_conf = abs(osc_now) > osc_std if not np.isnan(osc_std) and osc_std > 0 else False

        bull_case = (
            f"Osc={osc_now:.4f} crossed above 0 (prev={osc_prev:.4f}), "
            f"close={entry:.4f} > EMA20={ema20:.4f}"
        )
        bear_case = (
            f"Osc={osc_now:.4f} crossed below 0 (prev={osc_prev:.4f}), "
            f"close={entry:.4f} < EMA20={ema20:.4f}"
        )

        if cross_up and entry > ema20:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Chaikin Osc crossed above 0 ({osc_prev:.4f}→{osc_now:.4f}). "
                    f"close={entry:.4f} > EMA20={ema20:.4f}."
                ),
                invalidation=f"Osc drops back below 0 or close < EMA20 ({ema20:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down and entry < ema20:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Chaikin Osc crossed below 0 ({osc_prev:.4f}→{osc_now:.4f}). "
                    f"close={entry:.4f} < EMA20={ema20:.4f}."
                ),
                invalidation=f"Osc rises back above 0 or close > EMA20 ({ema20:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reasons = []
        if cross_up and entry <= ema20:
            reasons.append(f"Osc cross_up but close={entry:.4f} <= EMA20={ema20:.4f}")
        elif cross_down and entry >= ema20:
            reasons.append(f"Osc cross_down but close={entry:.4f} >= EMA20={ema20:.4f}")
        else:
            reasons.append(
                f"No Osc zero-cross. Osc={osc_now:.4f} prev={osc_prev:.4f}"
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="; ".join(reasons),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
