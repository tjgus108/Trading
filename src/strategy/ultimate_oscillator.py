"""
Ultimate Oscillator 전략:
- BUY: UO < 30 (과매도) AND UO 상승 중
- SELL: UO > 70 (과매수) AND UO 하락 중
- Confidence: HIGH if UO < 20 (BUY) or UO > 80 (SELL), MEDIUM otherwise
- 최소 35행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_UPPER = 70
_LOWER = 30
_HIGH_CONF_BUY = 20
_HIGH_CONF_SELL = 80


class UltimateOscillatorStrategy(BaseStrategy):
    name = "ultimate_oscillator"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        prev_close = df["close"].shift(1)
        low_or_prev = pd.concat([df["low"], prev_close], axis=1).min(axis=1)
        high_or_prev = pd.concat([df["high"], prev_close], axis=1).max(axis=1)
        bp = df["close"] - low_or_prev
        tr = high_or_prev - low_or_prev

        avg7 = bp.rolling(7).sum() / tr.rolling(7).sum().replace(0, 1e-10)
        avg14 = bp.rolling(14).sum() / tr.rolling(14).sum().replace(0, 1e-10)
        avg28 = bp.rolling(28).sum() / tr.rolling(28).sum().replace(0, 1e-10)
        uo = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7

        uo_now = float(uo.iloc[idx])
        uo_prev = float(uo.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        # BUY: 과매도 AND 상승 중
        if uo_now < _LOWER and uo_now > uo_prev:
            conf = Confidence.HIGH if uo_now < _HIGH_CONF_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"UO 과매도 반등: UO {uo_prev:.1f} → {uo_now:.1f} (임계값 {_LOWER})",
                invalidation=f"UO 재하락 시 ({_LOWER} 이하, 하강 중)",
                bull_case=f"UO {uo_now:.1f}, 과매도 구간 내 상승 전환",
                bear_case="단순 반등일 수 있음",
            )

        # SELL: 과매수 AND 하락 중
        if uo_now > _UPPER and uo_now < uo_prev:
            conf = Confidence.HIGH if uo_now > _HIGH_CONF_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"UO 과매수 하락: UO {uo_prev:.1f} → {uo_now:.1f} (임계값 {_UPPER})",
                invalidation=f"UO 재상승 시 ({_UPPER} 이상, 상승 중)",
                bull_case="단순 조정일 수 있음",
                bear_case=f"UO {uo_now:.1f}, 과매수 구간 내 하락 전환",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"UO 중립: {uo_now:.1f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
