"""
Klinger Oscillator 전략 - 볼륨/가격 추세 포착.
- TP = (high + low + close) / 3
- Trend: TP(i) > TP(i-1) → +1, else -1
- DM = high - low
- CM = 이전 CM + DM (Trend 동일), else DM + 이전 DM
- VF = Volume * |2 * DM/CM - 1| * Trend * 100
- KVO = EMA(VF, 34) - EMA(VF, 55)
- Signal = EMA(KVO, 13)
- BUY: KVO 상향 크로스 (이전 KVO <= 이전 Signal, 현재 KVO > Signal)
- SELL: KVO 하향 크로스 (이전 KVO >= 이전 Signal, 현재 KVO < Signal)
- 최소 70행 필요
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 70


def _compute_kvo(df: pd.DataFrame):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    trend = np.where(tp.diff() > 0, 1, -1)

    dm = (df["high"] - df["low"]).values
    cm_arr = np.zeros(len(df))
    for i in range(1, len(df)):
        if trend[i] == trend[i - 1]:
            cm_arr[i] = cm_arr[i - 1] + dm[i]
        else:
            cm_arr[i] = dm[i - 1] + dm[i]

    cm = pd.Series(cm_arr, index=df.index)
    cm_safe = cm.replace(0, 1e-10)

    vf = df["volume"] * (2 * pd.Series(dm, index=df.index) / cm_safe - 1).abs() * pd.Series(trend, index=df.index) * 100

    kvo = vf.ewm(span=34, adjust=False).mean() - vf.ewm(span=55, adjust=False).mean()
    signal = kvo.ewm(span=13, adjust=False).mean()
    return kvo, signal


class KlingerStrategy(BaseStrategy):
    name = "klinger"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 70행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        kvo, signal = _compute_kvo(df)

        last = self._last(df)
        idx = len(df) - 2

        kvo_now = float(kvo.iloc[idx])
        kvo_prev = float(kvo.iloc[idx - 1])
        sig_now = float(signal.iloc[idx])
        sig_prev = float(signal.iloc[idx - 1])
        entry = float(last["close"])

        cross_up = kvo_prev <= sig_prev and kvo_now > sig_now
        cross_down = kvo_prev >= sig_prev and kvo_now < sig_now

        if cross_up:
            conf = Confidence.HIGH if kvo_now > 0 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"KVO 상향 크로스: KVO={kvo_now:.2f} > Signal={sig_now:.2f} "
                    f"(Klinger Oscillator 매수 신호)"
                ),
                invalidation="KVO가 Signal 아래로 하향 돌파 시",
                bull_case=f"KVO={kvo_now:.2f}, Signal={sig_now:.2f}, 상향 크로스",
                bear_case="볼륨 추세 반전 가능성",
            )

        if cross_down:
            conf = Confidence.HIGH if kvo_now < 0 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"KVO 하향 크로스: KVO={kvo_now:.2f} < Signal={sig_now:.2f} "
                    f"(Klinger Oscillator 매도 신호)"
                ),
                invalidation="KVO가 Signal 위로 상향 돌파 시",
                bull_case="단기 반등 가능성",
                bear_case=f"KVO={kvo_now:.2f}, Signal={sig_now:.2f}, 하향 크로스",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Klinger 중립: KVO={kvo_now:.2f}, Signal={sig_now:.2f} (크로스 없음)"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
