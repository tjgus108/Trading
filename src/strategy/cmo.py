"""
CMO (Chande Momentum Oscillator) 전략:
- BUY: CMO < -50 (과매도) AND CMO 상승 중
- SELL: CMO > 50 (과매수) AND CMO 하락 중
- Confidence: HIGH if CMO < -70 (BUY) or CMO > 70 (SELL), MEDIUM otherwise
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 14
_MIN_ROWS = 20
_UPPER = 50
_LOWER = -50
_HIGH_CONF_BUY = -70
_HIGH_CONF_SELL = 70


class CMOStrategy(BaseStrategy):
    name = "cmo"

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

        delta = df["close"].diff()
        su = delta.clip(lower=0).rolling(_PERIOD).sum()
        sd = (-delta.clip(upper=0)).rolling(_PERIOD).sum()
        cmo = 100 * (su - sd) / (su + sd).replace(0, 1e-10)

        cmo_now = float(cmo.iloc[idx])
        cmo_prev = float(cmo.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        # BUY: 과매도 AND 상승 중
        if cmo_now < _LOWER and cmo_now > cmo_prev:
            conf = Confidence.HIGH if cmo_now < _HIGH_CONF_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"CMO 과매도 반등: CMO {cmo_prev:.1f} → {cmo_now:.1f} (임계값 {_LOWER})",
                invalidation=f"CMO 재하락 시 ({_LOWER} 이하, 하강 중)",
                bull_case=f"CMO {cmo_now:.1f}, 과매도 구간 내 상승 전환",
                bear_case="단순 반등일 수 있음",
            )

        # SELL: 과매수 AND 하락 중
        if cmo_now > _UPPER and cmo_now < cmo_prev:
            conf = Confidence.HIGH if cmo_now > _HIGH_CONF_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"CMO 과매수 하락: CMO {cmo_prev:.1f} → {cmo_now:.1f} (임계값 {_UPPER})",
                invalidation=f"CMO 재상승 시 ({_UPPER} 이상, 상승 중)",
                bull_case="단순 조정일 수 있음",
                bear_case=f"CMO {cmo_now:.1f}, 과매수 구간 내 하락 전환",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"CMO 중립: {cmo_now:.1f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
