"""
PriceChannelFilterStrategy: 도나치안 채널 기반 가격 채널 필터 전략.
- upper_ch = high.rolling(20).max()
- lower_ch = low.rolling(20).min()
- position_in_channel = (close - lower_ch) / (channel_width + 1e-10)
- BUY:  position_in_channel > 0.8 AND close > close.shift(1) (상단 20% 돌파)
- SELL: position_in_channel < 0.2 AND close < close.shift(1) (하단 20% 이탈)
- confidence: HIGH if > 0.95 or < 0.05, else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_CHANNEL_PERIOD = 20
_BUY_THRESHOLD = 0.8
_SELL_THRESHOLD = 0.2
_HIGH_CONF_HIGH = 0.95
_HIGH_CONF_LOW = 0.05


def _calc_channel_position(df: pd.DataFrame) -> "tuple[float, float, float]":
    """마지막 완성 캔들(-2) 기준 채널 내 위치 반환."""
    window = df.iloc[:-1]  # 진행 중 캔들 제외
    high = window["high"]
    low = window["low"]
    close = window["close"]

    upper_ch = high.rolling(_CHANNEL_PERIOD, min_periods=1).max()
    lower_ch = low.rolling(_CHANNEL_PERIOD, min_periods=1).min()
    channel_width = upper_ch - lower_ch
    position_in_channel = (close - lower_ch) / (channel_width + 1e-10)

    pos = float(position_in_channel.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) >= 2 else float(close.iloc[-1])
    curr_close = float(close.iloc[-1])
    return pos, curr_close, prev_close


class PriceChannelFilterStrategy(BaseStrategy):
    name = "price_channel_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        if "high" not in df.columns:
            df = df.copy()
            df["high"] = df["close"]
        if "low" not in df.columns:
            df = df.copy()
            df["low"] = df["close"]

        pos, curr_close, prev_close = _calc_channel_position(df)
        last = self._last(df)
        close = float(last["close"])

        import math
        if math.isnan(pos):
            return self._hold(df, "NaN in channel position")

        context = f"position={pos:.3f} close={close:.4f}"

        # BUY: 상단 20% 돌파 + 상승 중
        if pos > _BUY_THRESHOLD and curr_close > prev_close:
            confidence = Confidence.HIGH if pos > _HIGH_CONF_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"채널 상단 돌파 ({context})",
                invalidation=f"채널 내 위치 {pos:.3f} → 0.5 이하 하락 시",
                bull_case="상단 돌파 후 추세 지속 가능",
                bear_case="채널 내부로 되돌림 시 손실",
            )

        # SELL: 하단 20% 이탈 + 하락 중
        if pos < _SELL_THRESHOLD and curr_close < prev_close:
            confidence = Confidence.HIGH if pos < _HIGH_CONF_LOW else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"채널 하단 이탈 ({context})",
                invalidation=f"채널 내 위치 {pos:.3f} → 0.5 이상 반등 시",
                bull_case="채널 내부 반등 시 손실",
                bear_case="하단 이탈 후 추세 하락 가능",
            )

        return self._hold(df, context)

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        close = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="N/A",
        )
