"""
MFI (Money Flow Index) 전략:
- 볼륨 가중 RSI (과매수/과매도 신호)
- BUY: MFI < 20 (과매도) AND MFI 상승 중
- SELL: MFI > 80 (과매수) AND MFI 하락 중
- Confidence: HIGH if MFI < 10 (BUY) or MFI > 90 (SELL), MEDIUM otherwise
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 14
_MIN_ROWS = 20
_OVERSOLD = 20
_OVERBOUGHT = 80
_HIGH_BUY = 10
_HIGH_SELL = 90


class MFIStrategy(BaseStrategy):
    name = "mfi"

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

        tp = (df["high"] + df["low"] + df["close"]) / 3
        raw_mf = tp * df["volume"]
        tp_change = tp.diff()

        pos_mf = raw_mf.where(tp_change > 0, 0.0)
        neg_mf = raw_mf.where(tp_change < 0, 0.0)

        pos_sum = pos_mf.rolling(_PERIOD).sum()
        neg_sum = neg_mf.rolling(_PERIOD).sum()

        mfr = pos_sum / neg_sum.replace(0, 1e-10)
        mfi = 100 - (100 / (1 + mfr))

        mfi_now = float(mfi.iloc[idx])
        mfi_prev = float(mfi.iloc[idx - 1])
        close = float(df["close"].iloc[idx])

        rising = mfi_now > mfi_prev
        falling = mfi_now < mfi_prev

        if mfi_now < _OVERSOLD and rising:
            conf = Confidence.HIGH if mfi_now < _HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MFI 과매도 반등: MFI={mfi_now:.2f} < {_OVERSOLD}, 상승 중 ({mfi_prev:.2f} → {mfi_now:.2f})",
                invalidation=f"MFI > {_OVERSOLD} 또는 MFI 하락 전환",
                bull_case=f"MFI={mfi_now:.2f}, 강한 과매도 반등 신호",
                bear_case="추가 하락 가능성",
            )

        if mfi_now > _OVERBOUGHT and falling:
            conf = Confidence.HIGH if mfi_now > _HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MFI 과매수 하락: MFI={mfi_now:.2f} > {_OVERBOUGHT}, 하락 중 ({mfi_prev:.2f} → {mfi_now:.2f})",
                invalidation=f"MFI < {_OVERBOUGHT} 또는 MFI 상승 전환",
                bull_case="단기 반등 가능성",
                bear_case=f"MFI={mfi_now:.2f}, 강한 과매수 하락 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"MFI 중립: MFI={mfi_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
