"""
Detrended Price Oscillator Cross 전략:
- DPO = close.shift(period/2 + 1) - SMA(close, period)  [period=20]
- Signal = EWM(DPO, span=9)
- BUY:  DPO crosses above Signal (DPO > Signal AND 이전봉 DPO <= Signal)
- SELL: DPO crosses below Signal
- confidence: HIGH if |DPO - Signal| > std(DPO, 20), MEDIUM 그 외
- 최소 데이터: 35행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_DPO_PERIOD = 20
_SIGNAL_SPAN = 9
_STD_WINDOW = 20


class DPOCrossStrategy(BaseStrategy):
    name = "dpo_cross"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
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

        close = df["close"]
        shift_n = _DPO_PERIOD // 2 + 1  # 11 for period=20
        sma = close.rolling(_DPO_PERIOD).mean()
        dpo = close.shift(shift_n) - sma
        signal = dpo.ewm(span=_SIGNAL_SPAN, adjust=False).mean()
        dpo_std = dpo.rolling(_STD_WINDOW).std()

        # _last(df) = df.iloc[-2]
        last_idx = len(df) - 2

        dpo_now = dpo.iloc[last_idx]
        dpo_prev = dpo.iloc[last_idx - 1]
        sig_now = signal.iloc[last_idx]
        sig_prev = signal.iloc[last_idx - 1]
        std_now = dpo_std.iloc[last_idx]
        close_now = close.iloc[last_idx]

        if pd.isna(dpo_now) or pd.isna(sig_now) or pd.isna(std_now):
            last = self._last(df)
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="지표 계산 불충분",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        diff = dpo_now - sig_now
        bull_case = f"DPO {dpo_now:.4f} > Signal {sig_now:.4f} (diff={diff:.4f})"
        bear_case = f"DPO {dpo_now:.4f} < Signal {sig_now:.4f} (diff={diff:.4f})"

        cross_up = (dpo_now > sig_now) and (dpo_prev <= sig_prev)
        cross_down = (dpo_now < sig_now) and (dpo_prev >= sig_prev)

        if cross_up:
            conf = Confidence.HIGH if abs(diff) > std_now else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=float(close_now),
                reasoning=f"DPO Cross UP: DPO {dpo_now:.4f} crossed above Signal {sig_now:.4f}",
                invalidation="DPO crosses back below Signal",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down:
            conf = Confidence.HIGH if abs(diff) > std_now else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=float(close_now),
                reasoning=f"DPO Cross DOWN: DPO {dpo_now:.4f} crossed below Signal {sig_now:.4f}",
                invalidation="DPO crosses back above Signal",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=f"DPO 크로스 없음: DPO {dpo_now:.4f}, Signal {sig_now:.4f}",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
