"""
ScalpingSignalStrategy: 단기 스캘핑 신호.
EMA(3/8/13) 정렬 + RSI7 + 볼륨 필터.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ScalpingSignalStrategy(BaseStrategy):
    name = "scalping_signal"

    _MIN_ROWS = 20

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
        volume = df["volume"]
        high = df["high"]
        low = df["low"]

        fast_ema = close.ewm(span=3, adjust=False).mean()
        mid_ema = close.ewm(span=8, adjust=False).mean()
        slow_ema = close.ewm(span=13, adjust=False).mean()

        rsi_delta = close.diff()
        rsi_gain = rsi_delta.clip(lower=0).ewm(com=6, adjust=False).mean()
        rsi_loss = (-rsi_delta.clip(upper=0)).ewm(com=6, adjust=False).mean()
        rsi7 = 100 - 100 / (1 + rsi_gain / (rsi_loss + 1e-10))

        vol_ma = volume.rolling(5, min_periods=1).mean()

        idx = len(df) - 2
        last = df.iloc[idx]

        fe = fast_ema.iloc[idx]
        me = mid_ema.iloc[idx]
        se = slow_ema.iloc[idx]
        rsi = rsi7.iloc[idx]
        vol = volume.iloc[idx]
        vma = vol_ma.iloc[idx]
        entry = last["close"]

        import math
        if any(math.isnan(v) for v in [fe, me, se, rsi, vol, vma]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in indicators",
                invalidation="",
            )

        ema_spread_ratio = abs(fe - se) / (entry + 1e-10)
        confidence = Confidence.HIGH if ema_spread_ratio > 0.005 else Confidence.MEDIUM

        bull_case = (
            f"fast_ema={fe:.4f} mid_ema={me:.4f} slow_ema={se:.4f} "
            f"RSI7={rsi:.1f} vol={vol:.1f} vol_ma={vma:.1f}"
        )
        bear_case = bull_case

        # BUY: 상향 EMA 정렬 + RSI 50~70 + 볼륨 확인
        if fe > me and me > se and 50 < rsi < 70 and vol > vma:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Scalping BUY: EMA stack bullish (fast={fe:.4f}>mid={me:.4f}>slow={se:.4f}), "
                    f"RSI7={rsi:.1f} in 50-70, volume surge."
                ),
                invalidation=f"fast_ema crosses below mid_ema or RSI < 50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 하향 EMA 정렬 + RSI 30~50 + 볼륨 확인
        if fe < me and me < se and 30 < rsi < 50 and vol > vma:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Scalping SELL: EMA stack bearish (fast={fe:.4f}<mid={me:.4f}<slow={se:.4f}), "
                    f"RSI7={rsi:.1f} in 30-50, volume surge."
                ),
                invalidation=f"fast_ema crosses above mid_ema or RSI > 50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No scalping signal. fe={fe:.4f} me={me:.4f} se={se:.4f} "
                f"RSI7={rsi:.1f} vol={vol:.1f} vol_ma={vma:.1f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
