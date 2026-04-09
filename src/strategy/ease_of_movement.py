"""
Ease of Movement (EOM) 전략:
- 볼륨 대비 가격 변화의 용이성 측정
- BUY: EOM > 0 AND EOM 상승 중 AND close > ema50
- SELL: EOM < 0 AND EOM 하락 중 AND close < ema50
- confidence: HIGH if |EOM| > 1.0, MEDIUM otherwise
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_HIGH_CONF_EOM = 1.0


class EaseOfMovementStrategy(BaseStrategy):
    name = "ease_of_movement"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        mid_move = ((df["high"] + df["low"]) / 2) - ((df["high"].shift(1) + df["low"].shift(1)) / 2)
        box_ratio = (df["volume"] / 1e6) / (df["high"] - df["low"] + 1e-10)
        emv = mid_move / box_ratio.replace(0, 1e-10)
        eom = emv.ewm(span=14, adjust=False).mean()

        eom_now = float(eom.iloc[idx])
        eom_prev = float(eom.iloc[idx - 1])
        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        eom_rising = eom_now > eom_prev
        eom_falling = eom_now < eom_prev
        above_ema = close > ema50
        below_ema = close < ema50

        confidence = Confidence.HIGH if abs(eom_now) > _HIGH_CONF_EOM else Confidence.MEDIUM

        bull_case = (
            f"EOM={eom_now:.4f} (rising={eom_rising}), "
            f"close={close:.4f} > ema50={ema50:.4f}"
        )
        bear_case = (
            f"EOM={eom_now:.4f} (falling={eom_falling}), "
            f"close={close:.4f} < ema50={ema50:.4f}"
        )

        if eom_now > 0 and eom_rising and above_ema:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EOM 양수 상승 + close>ema50: "
                    f"EOM={eom_now:.4f}↑(prev={eom_prev:.4f}), "
                    f"close={close:.4f} ema50={ema50:.4f}"
                ),
                invalidation=f"EOM 음수 전환 또는 close < ema50({ema50:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if eom_now < 0 and eom_falling and below_ema:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EOM 음수 하락 + close<ema50: "
                    f"EOM={eom_now:.4f}↓(prev={eom_prev:.4f}), "
                    f"close={close:.4f} ema50={ema50:.4f}"
                ),
                invalidation=f"EOM 양수 전환 또는 close > ema50({ema50:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"No signal: EOM={eom_now:.4f} prev={eom_prev:.4f} close={close:.4f} ema50={ema50:.4f}",
            bull_case,
            bear_case,
        )

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
