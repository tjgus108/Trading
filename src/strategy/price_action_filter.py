"""
PriceActionFilterStrategy:
- 추세 + 변곡 + 거래량 3중 필터
- BUY:  trend_up AND strong_bull AND vol_confirm
- SELL: NOT trend_up AND strong_bear AND vol_confirm
- HOLD: 필터 미통과
- confidence: HIGH if body_ratio > 0.8 AND vol_confirm else MEDIUM
- 최소 데이터: 55행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55


class PriceActionFilterStrategy(BaseStrategy):
    name = "price_action_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for PriceActionFilter (need 55 rows)")

        df = df.copy()
        close = df["close"].astype(float)
        open_ = df["open"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        # 1. 추세 필터: EMA50
        ema50 = close.ewm(span=50, adjust=False).mean()
        trend_up = close > ema50

        # 2. 변곡 필터: 강한 봉
        body = (close - open_).abs()
        total_range = high - low + 1e-10
        body_ratio = body / total_range

        strong_bull = (close > open_) & (body_ratio > 0.6)
        strong_bear = (close < open_) & (body_ratio > 0.6)

        # 3. 거래량 필터
        vol = df["volume"].astype(float)
        vol_confirm = vol > vol.rolling(10).mean()

        idx = len(df) - 2

        trend_up_val = bool(trend_up.iloc[idx]) if not np.isnan(trend_up.iloc[idx]) else False
        strong_bull_val = bool(strong_bull.iloc[idx])
        strong_bear_val = bool(strong_bear.iloc[idx])
        vol_confirm_val = bool(vol_confirm.iloc[idx]) if not np.isnan(vol_confirm.iloc[idx]) else False
        body_ratio_val = float(body_ratio.iloc[idx]) if not np.isnan(body_ratio.iloc[idx]) else 0.0

        last = self._last(df)
        close_val = float(last["close"])
        ema50_val = float(ema50.iloc[idx])

        context = (
            f"trend_up={trend_up_val} strong_bull={strong_bull_val} "
            f"strong_bear={strong_bear_val} vol_ok={vol_confirm_val} "
            f"body_ratio={body_ratio_val:.2f} ema50={ema50_val:.4f} close={close_val:.4f}"
        )

        # BUY
        if trend_up_val and strong_bull_val and vol_confirm_val:
            confidence = Confidence.HIGH if body_ratio_val > 0.8 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"PriceActionFilter 매수: {context}",
                invalidation="EMA50 하향 돌파 시",
                bull_case=context,
                bear_case=context,
            )

        # SELL
        if not trend_up_val and strong_bear_val and vol_confirm_val:
            confidence = Confidence.HIGH if body_ratio_val > 0.8 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"PriceActionFilter 매도: {context}",
                invalidation="EMA50 상향 돌파 시",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"PriceActionFilter no signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
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
