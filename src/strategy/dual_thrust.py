"""
DualThrustStrategy: 전일 범위 기반 당일 돌파 전략.

계산 (k1=0.5, k2=0.5, lookback=1):
  Range = max(prev_high - prev_close, prev_close - prev_low)
  Buy_Level = prev_close + k1 * Range
  Sell_Level = prev_close - k2 * Range

BUY: close > Buy_Level AND 볼륨 > 10봉 평균
SELL: close < Sell_Level AND 볼륨 > 10봉 평균

confidence: HIGH if (close - Buy_Level) / Range > 0.1 (10% 초과), MEDIUM otherwise
최소 10행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10
_K1 = 0.5
_K2 = 0.5
_BREAKOUT_CONF_THRESHOLD = 0.1


class DualThrustStrategy(BaseStrategy):
    name = "dual_thrust"

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
        prev = df.iloc[idx - 1]
        curr = df.iloc[idx]

        prev_high = float(prev["high"])
        prev_low = float(prev["low"])
        prev_close = float(prev["close"])
        curr_close = float(curr["close"])

        range_val = max(prev_high - prev_close, prev_close - prev_low)

        if range_val <= 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="Range가 0 이하, 신호 없음",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        buy_level = prev_close + _K1 * range_val
        sell_level = prev_close - _K2 * range_val

        avg_vol = float(df["volume"].iloc[idx - 10:idx].mean())
        vol_ok = float(curr["volume"]) > avg_vol

        # BUY
        if curr_close > buy_level and vol_ok:
            breakout_ratio = (curr_close - buy_level) / range_val
            conf = Confidence.HIGH if breakout_ratio > _BREAKOUT_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"상단 돌파: close {curr_close:.2f} > Buy_Level {buy_level:.2f}, "
                    f"Range {range_val:.2f}, 볼륨 확인"
                ),
                invalidation=f"close가 Buy_Level {buy_level:.2f} 아래로 하락 시",
                bull_case=f"Range 대비 {breakout_ratio:.1%} 초과 돌파",
                bear_case="볼륨 감소 시 False Breakout 가능",
            )

        # SELL
        if curr_close < sell_level and vol_ok:
            breakout_ratio = (sell_level - curr_close) / range_val
            conf = Confidence.HIGH if breakout_ratio > _BREAKOUT_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"하단 돌파: close {curr_close:.2f} < Sell_Level {sell_level:.2f}, "
                    f"Range {range_val:.2f}, 볼륨 확인"
                ),
                invalidation=f"close가 Sell_Level {sell_level:.2f} 위로 상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"Range 대비 {breakout_ratio:.1%} 하단 돌파",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"돌파 없음: close {curr_close:.2f}, "
                f"Buy_Level {buy_level:.2f}, Sell_Level {sell_level:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
