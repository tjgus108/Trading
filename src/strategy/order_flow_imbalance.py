"""
OrderFlowImbalanceStrategy:
- 봉 내부 구조로 매수/매도 압력 불균형 추정
- BUY: imbalance > imbalance_ma AND imbalance > 0.3
- SELL: imbalance < imbalance_ma AND imbalance < -0.3
- HOLD: 그 외
- confidence: HIGH if abs(imbalance) > 0.5 else MEDIUM
- 최소 데이터: 15행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_MA_PERIOD = 10
_BUY_THRESH = 0.3
_SELL_THRESH = -0.3
_HIGH_CONF_THRESH = 0.5


class OrderFlowImbalanceStrategy(BaseStrategy):
    name = "order_flow_imbalance"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            reason = "Insufficient data for order flow imbalance"
            if df is not None and len(df) >= 2:
                last = self._last(df)
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=float(last["close"]),
                    reasoning=reason,
                    invalidation="",
                )
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
            )

        close = df["close"].astype(float)
        open_ = df["open"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        body = (close - open_).abs()
        upper_wick = high - close.combine(open_, max)
        lower_wick = close.combine(open_, min) - low
        total_range = (high - low).clip(lower=0.0001)

        buy_pressure = (body * (close > open_).astype(float) + lower_wick) / total_range
        sell_pressure = (body * (close < open_).astype(float) + upper_wick) / total_range
        imbalance = buy_pressure - sell_pressure
        imbalance_ma = imbalance.rolling(_MA_PERIOD).mean()

        idx = len(df) - 2
        imb = float(imbalance.iloc[idx])
        imb_ma = imbalance_ma.iloc[idx]

        if pd.isna(imb) or pd.isna(imb_ma):
            return self._hold(df, "NaN in imbalance calculation")

        imb_ma_val = float(imb_ma)
        close_val = float(df["close"].iloc[idx])

        confidence = Confidence.HIGH if abs(imb) > _HIGH_CONF_THRESH else Confidence.MEDIUM

        if imb > imb_ma_val and imb > _BUY_THRESH:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"매수 압력 우세: imbalance={imb:.3f} > ma={imb_ma_val:.3f} AND imbalance > {_BUY_THRESH}",
                invalidation=f"Imbalance drops below {_BUY_THRESH}",
                bull_case=f"imbalance={imb:.3f} imb_ma={imb_ma_val:.3f}",
                bear_case=f"imbalance={imb:.3f}",
            )

        if imb < imb_ma_val and imb < _SELL_THRESH:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"매도 압력 우세: imbalance={imb:.3f} < ma={imb_ma_val:.3f} AND imbalance < {_SELL_THRESH}",
                invalidation=f"Imbalance rises above {_SELL_THRESH}",
                bull_case=f"imbalance={imb:.3f}",
                bear_case=f"imbalance={imb:.3f} imb_ma={imb_ma_val:.3f}",
            )

        return self._hold(df, f"중립: imbalance={imb:.3f} ma={imb_ma_val:.3f}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
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
