"""
SmartMoneyFlowStrategy: Smart Money Flow — 봉 시작/종료 방향 + 거래량 가중.
- BUY: smf > smf_signal AND smf < 0
- SELL: smf < smf_signal AND smf > 0
- HOLD: 그 외
- confidence: HIGH if abs(smf) > smf.rolling(20).std() else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class SmartMoneyFlowStrategy(BaseStrategy):
    name = "smart_money_flow"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for SmartMoneyFlow")

        close = df["close"]

        otc_return = (close - df["open"]) / (df["open"] + 1e-10)
        weighted_flow = otc_return * df["volume"]

        smf = weighted_flow.rolling(10).sum()
        smf_signal = smf.ewm(span=5, adjust=False).mean()
        smf_std = smf.rolling(20).std()

        idx = len(df) - 2
        last = df.iloc[idx]

        smf_val = smf.iloc[idx]
        smf_signal_val = smf_signal.iloc[idx]
        smf_std_val = smf_std.iloc[idx]
        close_val = float(last["close"])

        if pd.isna(smf_val) or pd.isna(smf_signal_val):
            return self._hold(df, "NaN in indicators")

        std_valid = not pd.isna(smf_std_val) and smf_std_val > 0

        smf_std_str = f"{smf_std_val:.2f}" if std_valid else "NaN"
        info = (
            f"smf={smf_val:.2f} smf_signal={smf_signal_val:.2f} "
            f"smf_std={smf_std_str} close={close_val:.2f}"
        )

        if smf_val > smf_signal_val and smf_val < 0:
            confidence = (
                Confidence.HIGH
                if std_valid and abs(smf_val) > smf_std_val
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Smart money inflow starting (smf negative, rising): {info}",
                invalidation="smf crosses above zero or falls below signal",
                bull_case=info,
                bear_case=info,
            )

        if smf_val < smf_signal_val and smf_val > 0:
            confidence = (
                Confidence.HIGH
                if std_valid and abs(smf_val) > smf_std_val
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Smart money outflow starting (smf positive, falling): {info}",
                invalidation="smf crosses below zero or rises above signal",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"No signal: {info}", info, info)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
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
