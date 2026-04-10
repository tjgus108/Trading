"""
SwingPointStrategy: Swing High/Low를 이용한 구조적 매매.

로직:
  - swing_high = high.rolling(3).max().shift(1)
  - swing_low  = low.rolling(3).min().shift(1)
  - BUY:  close > prev_swing_high (이전 스윙 고점 돌파)
  - SELL: close < prev_swing_low  (이전 스윙 저점 이탈)
  - confidence HIGH: 돌파 크기 > ATR14 * 0.5
  - 최소 행: 10
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10


class SwingPointStrategy(BaseStrategy):
    name = "swing_point"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족: 최소 10행 필요",
                invalidation="",
            )

        idx = len(df) - 2  # 마지막 완성봉

        high = df["high"]
        low = df["low"]
        close = df["close"]

        swing_high = high.rolling(3).max().shift(1)
        swing_low = low.rolling(3).min().shift(1)

        prev_swing_high = float(swing_high.iloc[idx])
        prev_swing_low = float(swing_low.iloc[idx])
        entry = float(close.iloc[idx])

        # ATR14: 컬럼이 있으면 사용, 없으면 계산
        if "atr14" in df.columns:
            atr14 = float(df["atr14"].iloc[idx])
        else:
            tr = pd.concat([
                high - low,
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs(),
            ], axis=1).max(axis=1)
            atr14 = float(tr.rolling(14).mean().iloc[idx])

        atr14 = atr14 if atr14 > 0 else 1.0  # 0 방어

        context = (
            f"close={entry:.4f} swing_high={prev_swing_high:.4f} "
            f"swing_low={prev_swing_low:.4f} atr14={atr14:.4f}"
        )

        if entry > prev_swing_high:
            breakout_size = entry - prev_swing_high
            confidence = Confidence.HIGH if breakout_size > atr14 * 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"SwingPoint BUY: close({entry:.4f}) > swing_high({prev_swing_high:.4f}), "
                    f"돌파 크기={breakout_size:.4f}, ATR14={atr14:.4f}"
                ),
                invalidation=f"Close below swing_low({prev_swing_low:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if entry < prev_swing_low:
            breakout_size = prev_swing_low - entry
            confidence = Confidence.HIGH if breakout_size > atr14 * 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"SwingPoint SELL: close({entry:.4f}) < swing_low({prev_swing_low:.4f}), "
                    f"이탈 크기={breakout_size:.4f}, ATR14={atr14:.4f}"
                ),
                invalidation=f"Close above swing_high({prev_swing_high:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"SwingPoint HOLD: close={entry:.4f} in range "
                f"[{prev_swing_low:.4f}, {prev_swing_high:.4f}]"
            ),
            invalidation="",
            bull_case=context,
            bear_case=context,
        )
