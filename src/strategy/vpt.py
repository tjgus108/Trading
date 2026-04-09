"""
VPT (Volume Price Trend) 전략:
- VPT = cumsum(volume * (close - prev_close) / prev_close)
- VPT_EMA = EMA(VPT, 14)
- BUY: VPT 상향 크로스 (이전 VPT <= VPT_EMA, 현재 VPT > VPT_EMA)
- SELL: VPT 하락 크로스 (이전 VPT >= VPT_EMA, 현재 VPT < VPT_EMA)
- confidence: HIGH if 크로스 후 2봉 이상 유지, MEDIUM if 방금 크로스
- 최소 25행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EMA_SPAN = 14


class VPTStrategy(BaseStrategy):
    name = "vpt"

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

        price_change = df["close"].pct_change()
        vpt = (df["volume"] * price_change).cumsum()
        vpt_ema = vpt.ewm(span=_EMA_SPAN, adjust=False).mean()

        vpt_now = float(vpt.iloc[idx])
        vpt_prev = float(vpt.iloc[idx - 1])
        vpt_prev2 = float(vpt.iloc[idx - 2])
        ema_now = float(vpt_ema.iloc[idx])
        ema_prev = float(vpt_ema.iloc[idx - 1])
        ema_prev2 = float(vpt_ema.iloc[idx - 2])

        cross_up = vpt_prev <= ema_prev and vpt_now > ema_now
        cross_down = vpt_prev >= ema_prev and vpt_now < ema_now

        close = float(df["close"].iloc[idx])

        bull_case = (
            f"VPT 상향 크로스: VPT={vpt_now:.2f} > VPT_EMA={ema_now:.2f}. "
            f"볼륨 가중 가격 상승 추세."
        )
        bear_case = (
            f"VPT 하향 크로스: VPT={vpt_now:.2f} < VPT_EMA={ema_now:.2f}. "
            f"볼륨 가중 가격 하락 추세."
        )

        if cross_up:
            # HIGH: 2봉 이상 유지 (idx-2에서 이미 vpt > ema)
            conf = Confidence.HIGH if vpt_prev2 > ema_prev2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VPT 상향 크로스: VPT={vpt_now:.2f} > VPT_EMA={ema_now:.2f} "
                    f"(prev VPT={vpt_prev:.2f} <= EMA={ema_prev:.2f})"
                ),
                invalidation="VPT < VPT_EMA",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down:
            # HIGH: 2봉 이상 유지 (idx-2에서 이미 vpt < ema)
            conf = Confidence.HIGH if vpt_prev2 < ema_prev2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VPT 하향 크로스: VPT={vpt_now:.2f} < VPT_EMA={ema_now:.2f} "
                    f"(prev VPT={vpt_prev:.2f} >= EMA={ema_prev:.2f})"
                ),
                invalidation="VPT > VPT_EMA",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"VPT 크로스 없음: VPT={vpt_now:.2f}, VPT_EMA={ema_now:.2f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
