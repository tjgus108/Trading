"""
DynamicPivotChannelStrategy:
- 동적 피봇 채널 (가격 액션 기반)
- Upper pivot line: 최근 rolling max of high (7봉)
- Lower pivot line: 최근 rolling min of low (7봉)
- BUY: close < lower_pivot_line (하단 이탈 후 지지)
- SELL: close > upper_pivot_line (상단 이탈 후 저항)
- confidence: 채널 폭 < ATR14 * 2 → HIGH
- 최소 20행 필요
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_PIVOT_WINDOW = 7
_ATR_PERIOD = 14


def _calc_atr(df: pd.DataFrame, period: int = _ATR_PERIOD) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


class DynamicPivotChannelStrategy(BaseStrategy):
    name = "dynamic_pivot_channel"

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

        atr = _calc_atr(df)

        # 마지막 완성봉 기준 (idx = len-2)
        idx = len(df) - 2

        # Upper/lower pivot: rolling max/min of recent 7 bars up to idx
        upper_line = float(df["high"].iloc[max(0, idx - _PIVOT_WINDOW + 1): idx + 1].max())
        lower_line = float(df["low"].iloc[max(0, idx - _PIVOT_WINDOW + 1): idx + 1].min())

        close_now = float(df["close"].iloc[idx])
        atr_val = float(atr.iloc[idx])

        channel_width = upper_line - lower_line
        narrow_channel = (atr_val > 0) and (channel_width < atr_val * 2)

        entry = close_now

        # BUY: close below lower pivot (breakout below support → mean reversion / support hold)
        if close_now < lower_line:
            conf = Confidence.HIGH if narrow_channel else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"하단 피봇 채널 이탈: close={close_now:.2f} < lower={lower_line:.2f}, "
                    f"channel_width={channel_width:.2f}, ATR={atr_val:.2f}"
                ),
                invalidation=f"채널 하단 {lower_line:.2f} 회복 실패 시",
                bull_case=f"하단 지지 반등 기대, narrow={narrow_channel}",
                bear_case="채널 하단 이탈 지속 가능성",
            )

        # SELL: close above upper pivot (breakout above resistance → mean reversion / resistance)
        if close_now > upper_line:
            conf = Confidence.HIGH if narrow_channel else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"상단 피봇 채널 이탈: close={close_now:.2f} > upper={upper_line:.2f}, "
                    f"channel_width={channel_width:.2f}, ATR={atr_val:.2f}"
                ),
                invalidation=f"채널 상단 {upper_line:.2f} 상향 돌파 지속 시",
                bull_case="채널 상단 돌파 지속 가능성",
                bear_case=f"상단 저항 반락 기대, narrow={narrow_channel}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"채널 내부: close={close_now:.2f}, "
                f"lower={lower_line:.2f}, upper={upper_line:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
