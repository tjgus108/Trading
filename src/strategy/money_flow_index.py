"""
MoneyFlowIndexStrategy (MFI — crossover version):
- typical_price = (high + low + close) / 3
- raw_money_flow = typical_price * volume
- pos_mf = raw_mf.where(diff > 0, 0).rolling(14).sum()
- neg_mf = raw_mf.where(diff < 0, 0).rolling(14).sum()
- mfi = 100 - 100 / (1 + pos_mf / neg_mf)
- BUY:  mfi crosses above 20 (prev < 20, cur >= 20) — 과매도 탈출
- SELL: mfi crosses below 80 (prev > 80, cur <= 80) — 과매수 이탈
- confidence: HIGH if mfi < 10 (BUY) or mfi > 90 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 14
_MIN_ROWS = 20
_OVERSOLD = 20
_OVERBOUGHT = 80
_HIGH_BUY = 10
_HIGH_SELL = 90


class MoneyFlowIndexStrategy(BaseStrategy):
    name = "money_flow_index"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data: need {_MIN_ROWS} rows",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        tp = (df["high"] + df["low"] + df["close"]) / 3
        raw_mf = tp * df["volume"]
        diff = tp.diff()

        pos_mf = raw_mf.where(diff > 0, 0.0).rolling(_PERIOD).sum()
        neg_mf = raw_mf.where(diff < 0, 0.0).rolling(_PERIOD).sum()

        mfi = 100 - 100 / (1 + pos_mf / neg_mf.replace(0, 1e-10))

        mfi_now = float(mfi.iloc[idx])
        mfi_prev = float(mfi.iloc[idx - 1])

        if pd.isna(mfi_now) or pd.isna(mfi_prev):
            close = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="MFI NaN — Insufficient data",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = float(df["close"].iloc[idx])

        # BUY: crosses above 20
        if mfi_prev < _OVERSOLD and mfi_now >= _OVERSOLD:
            conf = Confidence.HIGH if mfi_now < _HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MFI crossover above {_OVERSOLD}: {mfi_prev:.2f} → {mfi_now:.2f} (과매도 탈출)",
                invalidation=f"MFI drops back below {_OVERSOLD}",
                bull_case=f"MFI={mfi_now:.2f}, 과매도 탈출 크로스오버",
                bear_case="추가 하락 가능성",
            )

        # SELL: crosses below 80
        if mfi_prev > _OVERBOUGHT and mfi_now <= _OVERBOUGHT:
            conf = Confidence.HIGH if mfi_now > _HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MFI crossover below {_OVERBOUGHT}: {mfi_prev:.2f} → {mfi_now:.2f} (과매수 이탈)",
                invalidation=f"MFI rises back above {_OVERBOUGHT}",
                bull_case="단기 반등 가능성",
                bear_case=f"MFI={mfi_now:.2f}, 과매수 이탈 크로스오버",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"MFI 중립: {mfi_now:.2f} (no crossover)",
            invalidation="",
            bull_case="",
            bear_case="",
        )
