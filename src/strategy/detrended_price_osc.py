"""
DetrendedPriceOscStrategy: DPO 기반 순수 사이클 측정 전략.
- period = 20, shift_amount = 11
- sma20 = close.rolling(20).mean()
- dpo = close.shift(11) - sma20
- dpo_ma = dpo.rolling(5).mean()
- BUY: dpo crosses above 0 AND dpo > dpo_ma
- SELL: dpo crosses below 0 AND dpo < dpo_ma
- confidence: HIGH if abs(dpo) > dpo.rolling(20).std() else MEDIUM
- 최소 35행 필요
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_SHIFT = _PERIOD // 2 + 1  # 11
_DPO_MA_PERIOD = 5
_CONF_STD_PERIOD = 20
_MIN_ROWS = 35


class DetrendedPriceOscStrategy(BaseStrategy):
    name = "detrended_price_osc"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (min 35 rows required)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]
        sma20 = close.rolling(_PERIOD).mean()
        dpo = close.shift(_SHIFT) - sma20
        dpo_ma = dpo.rolling(_DPO_MA_PERIOD).mean()
        dpo_std = dpo.rolling(_CONF_STD_PERIOD).std()

        idx = len(df) - 2
        dpo_now = float(dpo.iloc[idx])
        dpo_prev = float(dpo.iloc[idx - 1])
        dpo_ma_val = float(dpo_ma.iloc[idx])
        dpo_std_raw = dpo_std.iloc[idx]
        entry = float(close.iloc[idx])

        # NaN 체크
        if math.isnan(dpo_now) or math.isnan(dpo_prev) or math.isnan(dpo_ma_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="Insufficient data (NaN in DPO calculation)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        dpo_std_val = float(dpo_std_raw) if (dpo_std_raw is not None and not math.isnan(float(dpo_std_raw))) else 0.0

        # HIGH confidence: abs(dpo) > rolling std
        conf = Confidence.HIGH if dpo_std_val > 0 and abs(dpo_now) > dpo_std_val else Confidence.MEDIUM

        # BUY: dpo crosses above 0 AND dpo > dpo_ma (사이클 상승)
        if dpo_prev < 0 and dpo_now >= 0 and dpo_now > dpo_ma_val:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"DPO crosses above 0: {dpo_prev:.4f} → {dpo_now:.4f}, dpo_ma={dpo_ma_val:.4f}",
                invalidation="DPO re-crosses below 0",
                bull_case=f"DPO={dpo_now:.4f} 사이클 상승",
                bear_case="단기 반등에 그칠 수 있음",
            )

        # SELL: dpo crosses below 0 AND dpo < dpo_ma
        if dpo_prev > 0 and dpo_now < 0 and dpo_now < dpo_ma_val:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"DPO crosses below 0: {dpo_prev:.4f} → {dpo_now:.4f}, dpo_ma={dpo_ma_val:.4f}",
                invalidation="DPO re-crosses above 0",
                bull_case="단기 반등 가능성 있음",
                bear_case=f"DPO={dpo_now:.4f} 사이클 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"DPO neutral: {dpo_now:.4f}, dpo_ma={dpo_ma_val:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
