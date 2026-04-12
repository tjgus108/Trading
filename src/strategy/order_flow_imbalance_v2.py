"""
OrderFlowImbalanceV2Strategy Enhanced:
- 신호 품질 강화를 통한 Profit Factor 개선
- BUY_THRESH: 0.2 → 0.25 (더 강한 양봉 필요)
- SELL_THRESH: -0.2 → -0.25 (더 강한 음봉 필요)
- 거래량 필터: volume > volume_sma20 (강한 주문흐름 확인)
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_BUY_THRESH = 0.25    # 강화: 0.2 → 0.25
_SELL_THRESH = -0.25  # 강화: -0.2 → -0.25
_HIGH_CONF_THRESH = 0.4


class OrderFlowImbalanceV2Strategy(BaseStrategy):
    name = "order_flow_imbalance_v2"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            reason = "Insufficient data for order flow imbalance v2"
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
        volume = df["volume"].astype(float)

        buy_vol = volume * (close > open_).astype(float)
        sell_vol = volume * (close <= open_).astype(float)
        delta = buy_vol - sell_vol
        cum_delta = delta.rolling(10, min_periods=1).sum()
        total_vol = volume.rolling(10, min_periods=1).sum()
        imbalance = cum_delta / (total_vol + 1e-10)
        imbalance_ma = imbalance.rolling(5, min_periods=1).mean()
        ewm_close = close.ewm(span=10).mean()
        
        # 거래량 필터
        volume_sma20 = volume.rolling(20, min_periods=1).mean()

        idx = len(df) - 2
        imb = float(imbalance.iloc[idx])
        imb_ma = imbalance_ma.iloc[idx]
        close_val = float(close.iloc[idx])
        ewm_val = float(ewm_close.iloc[idx])
        vol_val = float(volume.iloc[idx])
        vol_sma = float(volume_sma20.iloc[idx])

        if pd.isna(imb) or pd.isna(imb_ma) or pd.isna(ewm_val) or pd.isna(vol_sma):
            return self._hold(df, "NaN in imbalance v2 calculation")

        imb_ma_val = float(imb_ma)
        confidence = Confidence.HIGH if abs(imb) > _HIGH_CONF_THRESH else Confidence.MEDIUM
        
        # 거래량 필터 확인
        vol_strong = vol_val > vol_sma

        if imb > _BUY_THRESH and imb > imb_ma_val and close_val > ewm_val and vol_strong:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"매수 압력 우세(v2): imbalance={imb:.3f} > {_BUY_THRESH} AND > ma={imb_ma_val:.3f} AND close > EWM AND vol_strong",
                invalidation=f"Imbalance drops below {_BUY_THRESH} or close < EWM or vol weakens",
                bull_case=f"imbalance={imb:.3f} imb_ma={imb_ma_val:.3f} ewm={ewm_val:.3f} vol={vol_val:.0f}vs{vol_sma:.0f}",
                bear_case=f"imbalance={imb:.3f}",
            )

        if imb < _SELL_THRESH and imb < imb_ma_val and close_val < ewm_val and vol_strong:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"매도 압력 우세(v2): imbalance={imb:.3f} < {_SELL_THRESH} AND < ma={imb_ma_val:.3f} AND close < EWM AND vol_strong",
                invalidation=f"Imbalance rises above {_SELL_THRESH} or close > EWM or vol weakens",
                bull_case=f"imbalance={imb:.3f}",
                bear_case=f"imbalance={imb:.3f} imb_ma={imb_ma_val:.3f} ewm={ewm_val:.3f} vol={vol_val:.0f}vs{vol_sma:.0f}",
            )

        return self._hold(df, f"중립(v2): imbalance={imb:.3f} ma={imb_ma_val:.3f}")

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
