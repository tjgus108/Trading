"""
HighLowChannelStrategy:
- High-Low 채널 중앙 반등/반락 (ATR 조정 포함)
- BUY:  position < 0.25 AND close > close.shift(1) (채널 하단 25% + 상향)
- SELL: position > 0.75 AND close < close.shift(1) (채널 상단 25% + 하향)
- confidence: HIGH if position < 0.1 (BUY) or position > 0.9 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20


def _calc_atr14(df: pd.DataFrame) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(14).mean()


class HighLowChannelStrategy(BaseStrategy):
    name = "high_low_channel"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning=f"Insufficient data: {len(df)} < {MIN_ROWS}",
                invalidation="",
            )

        idx = len(df) - 2
        last = self._last(df)  # df.iloc[-2]

        high = df["high"]
        low = df["low"]
        close = df["close"]

        highest_n = high.rolling(14).max()
        lowest_n = low.rolling(14).min()
        channel_width = highest_n - lowest_n
        # avoid div by zero
        safe_width = channel_width.replace(0, 0.0001)
        position_series = (close - lowest_n) / safe_width
        atr14 = _calc_atr14(df)

        pos_val = position_series.iloc[idx]
        atr_val = atr14.iloc[idx]
        close_val = float(close.iloc[idx])
        prev_close_val = float(close.iloc[idx - 1]) if idx >= 1 else close_val
        highest_val = float(highest_n.iloc[idx])
        lowest_val = float(lowest_n.iloc[idx])

        # NaN 체크
        if pd.isna(pos_val) or pd.isna(atr_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="NaN in indicators",
                invalidation="",
            )

        entry_price = float(last["close"])
        price_up = close_val > prev_close_val
        price_down = close_val < prev_close_val

        # BUY: 채널 하단 25% + 상향
        if pos_val < 0.25 and price_up:
            conf = Confidence.HIGH if pos_val < 0.1 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"채널 하단 반등: position={pos_val:.3f} < 0.25, "
                    f"close={close_val:.4f} > prev={prev_close_val:.4f}, "
                    f"channel=[{lowest_val:.4f}, {highest_val:.4f}]"
                ),
                invalidation=f"Close below channel low {lowest_val:.4f}",
                bull_case=f"Channel bounce, ATR={atr_val:.4f}",
                bear_case="",
            )

        # SELL: 채널 상단 25% + 하향
        if pos_val > 0.75 and price_down:
            conf = Confidence.HIGH if pos_val > 0.9 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"채널 상단 반락: position={pos_val:.3f} > 0.75, "
                    f"close={close_val:.4f} < prev={prev_close_val:.4f}, "
                    f"channel=[{lowest_val:.4f}, {highest_val:.4f}]"
                ),
                invalidation=f"Close above channel high {highest_val:.4f}",
                bull_case="",
                bear_case=f"Channel rejection, ATR={atr_val:.4f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"채널 중간 구간: position={pos_val:.3f} "
                f"(0.25 ~ 0.75), channel=[{lowest_val:.4f}, {highest_val:.4f}]"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
