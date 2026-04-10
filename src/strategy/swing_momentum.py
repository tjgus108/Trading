"""
SwingMomentumStrategy: 스윙 포인트 기반 모멘텀.
확인된 스윙 고/저점 돌파 + 볼륨 필터.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SwingMomentumStrategy(BaseStrategy):
    name = "swing_momentum"

    _MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="Insufficient data",
                invalidation="",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # 2봉 전까지 확인된 스윙 고/저점
        recent_swing_high = high.rolling(5, min_periods=1).max().shift(2)
        recent_swing_low = low.rolling(5, min_periods=1).min().shift(2)
        swing_range = recent_swing_high - recent_swing_low

        vol_ma10 = volume.rolling(10, min_periods=1).mean()
        avg_range = (high - low).rolling(20, min_periods=1).mean()

        idx = len(df) - 2
        last = df.iloc[idx]

        c = close.iloc[idx]
        sh = recent_swing_high.iloc[idx]
        sl = recent_swing_low.iloc[idx]
        sr = swing_range.iloc[idx]
        vol = volume.iloc[idx]
        vma = vol_ma10.iloc[idx]
        avg_r = avg_range.iloc[idx]
        entry = last["close"]

        import math
        if any(math.isnan(v) for v in [c, sh, sl, sr, vol, vma, avg_r]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in indicators",
                invalidation="",
            )

        confidence = Confidence.HIGH if sr > avg_r * 1.5 else Confidence.MEDIUM

        bull_case = (
            f"close={c:.4f} swing_high={sh:.4f} swing_low={sl:.4f} "
            f"swing_range={sr:.4f} vol={vol:.1f} vol_ma10={vma:.1f}"
        )
        bear_case = bull_case

        # BUY: 스윙 고점 돌파 + 볼륨 확인
        if c > sh and vol > vma:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Swing breakout BUY: close={c:.4f} > swing_high={sh:.4f}, "
                    f"volume surge (vol={vol:.1f} > ma={vma:.1f})."
                ),
                invalidation=f"Close below swing_high ({sh:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 스윙 저점 이탈 + 볼륨 확인
        if c < sl and vol > vma:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Swing breakdown SELL: close={c:.4f} < swing_low={sl:.4f}, "
                    f"volume surge (vol={vol:.1f} > ma={vma:.1f})."
                ),
                invalidation=f"Close above swing_low ({sl:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No swing breakout. close={c:.4f} swing_high={sh:.4f} "
                f"swing_low={sl:.4f} vol={vol:.1f} vol_ma={vma:.1f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
